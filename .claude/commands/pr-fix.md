Fetch inline review comments from a GitHub PR, group by issue type, apply fixes, and push — all in an isolated git worktree. Supports `watch` submode for PR babysitting and `all` submode to fix every open PR with review comments.

## Instructions

Follow these steps precisely. Do NOT add a Co-Authored-By line to commits.

### Argument Parsing

Parse `$ARGUMENTS` for one of three modes:

- **Fix mode** (default): `$ARGUMENTS` is a PR number (e.g., `3`) or empty.
- **Watch mode**: `$ARGUMENTS` starts with `watch` followed by a PR number (e.g., `watch 3`).
- **All mode**: `$ARGUMENTS` starts with `all`, optionally followed by `--dry-run` and/or a number limit (e.g., `all`, `all --dry-run`, `all 3`, `all --dry-run 3`).

If watch mode is detected, skip to the **Watch Mode** section below.
If all mode is detected, skip to the **All Mode** section below.

For fix mode, extract the PR number from `$ARGUMENTS`. If empty, try auto-detection: `gh pr view --json number -q .number 2>/dev/null`. If auto-detection fails, ask the user "Which PR number should I fix?" and wait for their response.

---

## Fix Mode

### Step 1: Pre-flight checks

1. **GitHub CLI available**: Run `gh --version`. If unavailable, tell the user "GitHub CLI (gh) is required. Install with: brew install gh" and stop.
2. **PR exists and is open**: Run `gh pr view <PR_NUMBER> --json number,state,headRefName,baseRefName,title`. If the PR does not exist or is not open, report the error and stop. Save `headRefName` as `PR_BRANCH` and `title` as `PR_TITLE`.
3. **Extract owner/repo**: Run `gh repo view --json owner,name -q '.owner.login + "/" + .name'`. Save as `OWNER_REPO`.
4. **Clean stale worktrees**: Run `git worktree list`. For any entries with paths containing `.claude/worktrees/pr-fix-`, remove them with `git worktree remove --force <path>`. This handles leftovers from interrupted prior runs.

### Step 2: Create worktree

1. Fetch the latest remote state: `git fetch origin <PR_BRANCH>`.
2. Create an isolated worktree attached to a local branch tracking the PR head:
   ```
   git worktree add -b <PR_BRANCH> .claude/worktrees/pr-fix-<PR_NUMBER> origin/<PR_BRANCH>
   ```
   If the local branch already exists, use `git worktree add .claude/worktrees/pr-fix-<PR_NUMBER> <PR_BRANCH>` instead.
3. If worktree creation fails (e.g., branch already checked out), report the error and stop.

Save `.claude/worktrees/pr-fix-<PR_NUMBER>` as `WORKTREE_DIR`.

### Step 3: Fetch review comments

Fetch all inline review comments:
```
gh api repos/{OWNER_REPO}/pulls/<PR_NUMBER>/comments --paginate
```

For each comment, extract: `id`, `path`, `line`, `original_line`, `body`, `diff_hunk`.

If no comments are found, report "No review comments on PR #<PR_NUMBER>" and skip to Step 9.

### Step 4: Group and deduplicate comments

Group comments that describe the **same underlying issue**:
- Comments with identical `body` text (ignoring trailing whitespace and code suggestion blocks) are grouped together
- Comments describing the same fix pattern across different files (detected by similar body structure) should also be grouped

For each unique issue group, create a summary:
- **Issue title**: A concise description of the problem
- **Affected files**: List of `path:line` locations
- **Comment body**: The shared comment text (first 200 chars)
- **Comment IDs**: All comment IDs in this group

Display the grouped summary:
```
Found <N> review comments grouped into <M> unique issues:

Issue 1/M: <issue title>
  Files: <path1>:<line>, <path2>:<line>, ...
  Comment: <truncated body>

Issue 2/M: <issue title>
  ...
```

### Step 5: Fix each issue group

For each unique issue group (maximum 10 groups — if more, warn and stop):

1. **Present**: Show the full comment body and all affected file paths with their diff hunks.
2. **Read**: Read each affected file from the worktree path (`<WORKTREE_DIR>/<path>`) to understand the current code.
3. **Fix**: Apply the code change that addresses the review comment. If the comment includes a code suggestion block, use it as a starting point but verify correctness. All file edits must target files inside `WORKTREE_DIR`.
4. **Report**: Tell the user what was changed in each file.

After all groups are processed, proceed to Step 6.

### Step 6: Regenerate and validate

Check the list of modified files (relative to the worktree).

**If any files under `core/`, `generator/templates/`, `generator/generate.py`, or `platforms/*/platform.json` were modified:**
- Run `python3 generator/generate.py --all` from `WORKTREE_DIR`
- Stage regenerated files

**If any checksummed files were modified** (`skills/specops/SKILL.md`, `schema.json`, `platforms/claude/SKILL.md`, `platforms/claude/platform.json`, `platforms/cursor/specops.mdc`, `platforms/cursor/platform.json`, `platforms/codex/SKILL.md`, `platforms/codex/platform.json`, `platforms/copilot/specops.instructions.md`, `platforms/copilot/platform.json`, `core/workflow.md`, `core/safety.md`, `hooks/pre-commit`, `hooks/pre-push`, `scripts/install-hooks.sh`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`):
- Regenerate checksums from `WORKTREE_DIR`:
  ```
  cd <WORKTREE_DIR> && shasum -a 256 skills/specops/SKILL.md schema.json platforms/claude/SKILL.md platforms/claude/platform.json platforms/cursor/specops.mdc platforms/cursor/platform.json platforms/codex/SKILL.md platforms/codex/platform.json platforms/copilot/specops.instructions.md platforms/copilot/platform.json core/workflow.md core/safety.md hooks/pre-commit hooks/pre-push scripts/install-hooks.sh .claude-plugin/plugin.json .claude-plugin/marketplace.json > CHECKSUMS.sha256
  ```

Run validation from `WORKTREE_DIR`:
1. `python3 generator/validate.py`
2. `shasum -a 256 -c CHECKSUMS.sha256`
3. `bash scripts/run-tests.sh`

If any validation fails, attempt to fix (up to 2 retries). If still failing, stop and report.

### Step 7: Commit and push

1. Stage all modified files: `git -C <WORKTREE_DIR> add -A`
2. Un-stage sensitive files (`.env*`, `credentials.json`, `*.pem`, `*.key`, SSH keys) if any.
3. Generate a commit message with `fix:` prefix summarizing the review fixes.
4. Commit using heredoc:
   ```
   git -C <WORKTREE_DIR> commit -m "$(cat <<'EOF'
   fix: <generated message>
   EOF
   )"
   ```
5. Do NOT use `--no-verify`. If pre-commit hook fails, fix and retry (up to 2 times).
6. Push: `git -C <WORKTREE_DIR> push`. Do NOT use `--no-verify`.

### Step 8: Reply to PR comments

For each issue group that was fixed, reply to ONE comment in the group (the first one) using:

```
gh api repos/{OWNER_REPO}/pulls/comments/<comment_id>/replies -f body="Fixed in <short-sha>."
```

This avoids spamming every duplicate comment with a reply.

### Step 9: Cleanup worktree

Remove the worktree:
```
git worktree remove <WORKTREE_DIR> --force
```

If the `.claude/worktrees/` directory is empty after cleanup, remove it: `rmdir .claude/worktrees/ 2>/dev/null`.

### Step 10: Confirm

Report the result:
- Number of issues fixed (grouped count)
- Files modified
- Commit hash and message
- PR URL
- Suggest: "Run `/loop 15m /pr-fix watch <PR_NUMBER>` to babysit this PR."

---

## Watch Mode

Watch mode is designed for use with `/loop` to babysit a PR. It checks CI status, new review comments, and PR conversations on each invocation.

### Step W1: Pre-flight

1. Extract PR number from `$ARGUMENTS` (after `watch`).
2. Validate PR exists and is open: `gh pr view <PR_NUMBER> --json number,state,headRefName,title`.
3. Extract owner/repo: `gh repo view --json owner,name -q '.owner.login + "/" + .name'`. Save as `OWNER_REPO`.

### Step W2: Load state

Check if `.claude/.pr-fix-state-<PR_NUMBER>.json` exists. If yes, read it. If not, initialize with empty state:
```json
{
  "lastCommentCount": 0,
  "lastCommentId": 0,
  "lastIssueCommentCount": 0,
  "lastCheckedAt": ""
}
```

### Step W3: Check CI status

Run:
```
gh run list --branch <PR_BRANCH> --json databaseId,status,conclusion,name --limit 10
```

Categorize each workflow run:
- **Passing**: `conclusion == "success"`
- **Failing**: `conclusion == "failure"`
- **In progress**: `status == "in_progress" || status == "queued"`

### Step W4: Check for new review comments

Fetch inline review comments:
```
gh api repos/{OWNER_REPO}/pulls/<PR_NUMBER>/comments --paginate
```

Compare the count against `lastCommentCount` from state. If new comments exist:
1. Extract only comments with `id > lastCommentId`
2. Group and deduplicate new comments (same logic as Fix Mode Step 4)
3. For comments with code suggestion blocks: auto-fix if the fix is clear and isolated (single file, unambiguous change)
4. For ambiguous comments: summarize and notify the user — do NOT auto-fix

### Step W5: Check PR conversations

Fetch PR issue comments (general discussion, not inline reviews):
```
gh api repos/{OWNER_REPO}/issues/<PR_NUMBER>/comments
```

Compare count against `lastIssueCommentCount`. If new messages:
1. Summarize each new message
2. If a reviewer asks a question, draft a reply for the user's approval before posting

### Step W6: Report status dashboard

Display a concise summary:

```
PR #<N> Status (checked at HH:MM)
├─ CI: ✓ All checks passing / ✗ <name> failed / ⏳ <name> in progress
├─ Review comments: <N> new since last check (<M> auto-fixed, <K> need attention)
└─ Conversations: <N> new messages
```

If any fixes were auto-applied in Step W4:
- Stage, commit with `fix: auto-fix PR review comment (<brief description>)`, and push
- Reply to the fixed comment with the commit SHA

### Step W7: Save state

Write updated state to `.claude/.pr-fix-state-<PR_NUMBER>.json`:
```json
{
  "lastCommentCount": <current total>,
  "lastCommentId": <highest comment id>,
  "lastIssueCommentCount": <current total>,
  "lastCheckedAt": "<ISO 8601 timestamp>"
}
```

### Watch Mode Notes

- Watch mode is designed to be lightweight — it should complete quickly (under 30 seconds) so it doesn't block the `/loop` scheduler.
- Auto-fixes are conservative: only apply when the fix is unambiguous (code suggestion blocks targeting a single clear change).
- Never auto-fix changes to security-sensitive files (`core/safety.md`, `core/workflow.md`, `generator/generate.py`, etc.) — always notify the user.
- The state file is gitignored (`.claude/` is typically in `.gitignore`).

---

## All Mode

All mode discovers every open PR with review comments and fixes them all, each in its own isolated git worktree.

### Argument Parsing (All Mode)

Parse everything after `all` in `$ARGUMENTS`:

- `--dry-run` or `dry-run`: Preview mode — discover and display what would be fixed without applying changes.
- A number (e.g., `3`): Override the maximum PR limit (default is 5).
- Both can be combined: `all --dry-run 3` or `all 3 --dry-run`.

### Step A1: Pre-flight checks

1. **GitHub CLI available**: Run `gh --version`. If unavailable, tell the user "GitHub CLI (gh) is required. Install with: brew install gh" and stop.
2. **Extract owner/repo**: Run `gh repo view --json owner,name -q '.owner.login + "/" + .name'`. Save as `OWNER_REPO`.
3. **Clean stale worktrees**: Run `git worktree list`. For any entries with paths containing `.claude/worktrees/pr-fix-`, remove them with `git worktree remove --force <path>`.

### Step A2: Discover PRs with review comments

1. Run `gh pr list --search "review:changes_requested" --state open --json number,headRefName,baseRefName,title --limit 10`.
2. If no results, try a broader search: run `gh pr list --state open --json number,headRefName,baseRefName,title --limit 20`. For each PR, check inline comment count: `gh api repos/{OWNER_REPO}/pulls/<NUMBER>/comments --jq 'length'`. Keep only PRs with comment count > 0.
3. Deduplicate results by PR number.
4. Cap the list at MAX_PRS (default 5, or the user-provided override).
5. If zero PRs have review comments, report "No open PRs with review comments found." and stop.

Save the list as `PR_LIST` with each entry containing: `number`, `headRefName`, `baseRefName`, `title`.

### Step A3: Fetch and group comments per PR

For each PR in `PR_LIST`:

1. Fetch all inline review comments:
   ```
   gh api repos/{OWNER_REPO}/pulls/<NUMBER>/comments --paginate
   ```
2. For each comment, extract: `id`, `path`, `line`, `original_line`, `body`, `diff_hunk`.
3. If no comments are found for this PR, remove it from `PR_LIST` and continue.
4. Group comments that describe the **same underlying issue** (same logic as Fix Mode Step 4).
5. For each unique issue group, create a summary with issue title, affected files, comment body, and comment IDs.

### Step A4: Display discovery dashboard

Display the full summary:

```
PR Fix-All Discovery
=====================

Found <N> open PRs with review comments:

PR #<N1>: <title>
  Branch: <headRefName> → <baseRefName>
  Comments: <M> comments in <K> issue groups
  Issues:
    1. <issue title> (<file count> files)
    2. <issue title> (<file count> files)

PR #<N2>: <title>
  Branch: <headRefName> → <baseRefName>
  Comments: <M> comments in <K> issue groups
  Issues:
    1. <issue title> (<file count> files)

Total: <X> PRs, <Y> issue groups, <Z> comments
```

If `--dry-run` is active, display this dashboard and stop with message: "Dry run complete. Run `/pr-fix all` without --dry-run to apply fixes."

### Step A5: Process each PR in a worktree

For each PR in `PR_LIST` (sequentially, one at a time):

#### Step A5a: Create worktree

1. Fetch the latest remote state: `git fetch origin <headRefName>`.
2. Create an isolated worktree attached to a local branch tracking the PR head:
   ```
   git worktree add -b <headRefName> .claude/worktrees/pr-fix-<NUMBER> origin/<headRefName>
   ```
   If the local branch already exists, use `git worktree add .claude/worktrees/pr-fix-<NUMBER> <headRefName>` instead.
3. If worktree creation fails, log the error, record this PR as `SKIPPED: <reason>`, and continue to the next PR.

Save `.claude/worktrees/pr-fix-<NUMBER>` as `WORKTREE_DIR`.

#### Step A5b: Fix each issue group

For each unique issue group for this PR (maximum 10 groups — if more, warn and skip remaining):

1. **Present**: Show the full comment body and all affected file paths with their diff hunks.
2. **Read**: Read each affected file from `<WORKTREE_DIR>/<path>` to understand the current code.
3. **Fix**: Apply the code change that addresses the review comment. All file edits must target files inside `WORKTREE_DIR`.
4. **Report**: Tell the user what was changed in each file.

#### Step A5c: Regenerate and validate

Same logic as Fix Mode Step 6, but run from `WORKTREE_DIR`.

If any validation fails after 2 retries, record this PR as `FAILED: validation error — <details>` and continue to the next PR (do not push broken code).

#### Step A5d: Commit and push

1. Stage all modified files: `git -C <WORKTREE_DIR> add -A`
2. Un-stage sensitive files (`.env*`, `credentials.json`, `*.pem`, `*.key`, SSH keys) if any.
3. Generate a commit message with `fix:` prefix summarizing the review fixes for this PR.
4. Commit using heredoc:
   ```
   git -C <WORKTREE_DIR> commit -m "$(cat <<'EOF'
   fix: <generated message>
   EOF
   )"
   ```
5. Do NOT use `--no-verify`. If pre-commit hook fails, fix and retry (up to 2 times). If still failing, record this PR as `FAILED: pre-commit hook — <details>` and continue.
6. Push: `git -C <WORKTREE_DIR> push`. Do NOT use `--no-verify`.

Save the short commit SHA for this PR.

#### Step A5e: Reply to PR comments

For each issue group that was fixed, reply to ONE comment in the group (the first one) using:

```
gh api repos/{OWNER_REPO}/pulls/comments/<comment_id>/replies -f body="Fixed in <short-sha>."
```

#### Step A5f: Record result

Save the result for this PR:
- **Status**: `FIXED`, `SKIPPED`, or `FAILED`
- **Commit SHA** (if fixed)
- **Files modified** (list)
- **Issues fixed** (count)
- **Error message** (if skipped or failed)

### Step A6: Cleanup worktrees

For each worktree created during this run:
```
git worktree remove .claude/worktrees/pr-fix-<NUMBER> --force
```

If the `.claude/worktrees/` directory is empty after cleanup, remove it: `rmdir .claude/worktrees/ 2>/dev/null`.

### Step A7: Summary dashboard

Display the consolidated results:

```
PR Fix-All Summary
===================

Processed: <N> PRs

✓ FIXED:
  PR #<N1>: <title>
    Commit: <sha> — fix: <message>
    Issues fixed: <K>
    Files modified: <file list>

  PR #<N2>: <title>
    Commit: <sha> — fix: <message>
    Issues fixed: <K>
    Files modified: <file list>

⊘ SKIPPED:
  PR #<N3>: <title> — <reason>

✗ FAILED:
  PR #<N4>: <title> — <reason>

Totals: <X> fixed, <Y> skipped, <Z> failed
```

If any PRs were fixed, suggest: "Run `/pr-fix all --dry-run` to check for remaining review comments."

If any PRs were skipped or failed, suggest: "Use `/pr-fix <NUMBER>` to handle individual PRs that couldn't be processed."
