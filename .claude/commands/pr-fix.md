Fetch inline review comments from a GitHub PR, group by issue type, apply fixes, and push. Supports a `watch` submode for PR babysitting with `/loop`.

## Instructions

Follow these steps precisely. Do NOT add a Co-Authored-By line to commits.

### Argument Parsing

Parse `$ARGUMENTS` for one of two modes:

- **Fix mode** (default): `$ARGUMENTS` is a PR number (e.g., `3`) or empty.
- **Watch mode**: `$ARGUMENTS` starts with `watch` followed by a PR number (e.g., `watch 3`).

If watch mode is detected, skip to the **Watch Mode** section below.

For fix mode, extract the PR number from `$ARGUMENTS`. If empty, try auto-detection: `gh pr view --json number -q .number 2>/dev/null`. If auto-detection fails, ask the user "Which PR number should I fix?" and wait for their response.

---

## Fix Mode

### Step 1: Pre-flight checks

1. **GitHub CLI available**: Run `gh --version`. If unavailable, tell the user "GitHub CLI (gh) is required. Install with: brew install gh" and stop.
2. **PR exists and is open**: Run `gh pr view <PR_NUMBER> --json number,state,headRefName,baseRefName,title`. If the PR does not exist or is not open, report the error and stop. Save `headRefName` as `PR_BRANCH` and `title` as `PR_TITLE`.
3. **Working tree is clean**: Run `git status`. If there are uncommitted changes, tell the user "Working tree is not clean. Commit or stash changes first." and stop.

### Step 2: Switch to the PR branch

1. Run `git rev-parse --abbrev-ref HEAD` and save as `ORIGINAL_BRANCH`.
2. If `ORIGINAL_BRANCH` != `PR_BRANCH`, run `git checkout <PR_BRANCH>`. If the branch does not exist locally, run `git checkout -t origin/<PR_BRANCH>`.
3. Run `git pull --ff-only` to ensure the branch is up to date.

### Step 3: Fetch review comments

Extract owner and repo: `gh repo view --json owner,name -q '.owner.login + "/" + .name'`.

Fetch all inline review comments:
```
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments --paginate
```

For each comment, extract: `id`, `path`, `line`, `original_line`, `body`, `diff_hunk`.

If no comments are found, report "No review comments on PR #<PR_NUMBER>" and skip to Step 8.

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
2. **Read**: Read each affected file to understand the current code.
3. **Fix**: Apply the code change that addresses the review comment. If the comment includes a code suggestion block, use it as a starting point but verify correctness.
4. **Report**: Tell the user what was changed in each file.

After all groups are processed, proceed to Step 6.

### Step 6: Regenerate and validate

Check the list of modified files.

**If any files under `core/`, `generator/templates/`, `generator/generate.py`, or `platforms/*/platform.json` were modified:**
- Run `python3 generator/generate.py --all`
- Stage regenerated files

**If any checksummed files were modified** (`skills/specops/SKILL.md`, `schema.json`, `platforms/claude/SKILL.md`, `platforms/claude/platform.json`, `platforms/cursor/specops.mdc`, `platforms/cursor/platform.json`, `platforms/codex/SKILL.md`, `platforms/codex/platform.json`, `platforms/copilot/specops.instructions.md`, `platforms/copilot/platform.json`, `core/workflow.md`, `core/safety.md`, `hooks/pre-commit`, `hooks/pre-push`, `scripts/install-hooks.sh`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`):
- Regenerate checksums:
  ```
  shasum -a 256 skills/specops/SKILL.md schema.json platforms/claude/SKILL.md platforms/claude/platform.json platforms/cursor/specops.mdc platforms/cursor/platform.json platforms/codex/SKILL.md platforms/codex/platform.json platforms/copilot/specops.instructions.md platforms/copilot/platform.json core/workflow.md core/safety.md hooks/pre-commit hooks/pre-push scripts/install-hooks.sh .claude-plugin/plugin.json .claude-plugin/marketplace.json > CHECKSUMS.sha256
  ```

Run validation:
1. `python3 generator/validate.py`
2. `shasum -a 256 -c CHECKSUMS.sha256`
3. `bash scripts/run-tests.sh`

If any validation fails, attempt to fix (up to 2 retries). If still failing, stop and report.

### Step 7: Commit and push

1. Stage all modified files: `git add -A`
2. Un-stage sensitive files (`.env*`, `credentials.json`, `*.pem`, `*.key`, SSH keys) if any.
3. Generate a commit message with `fix:` prefix summarizing the review fixes.
4. Commit using heredoc:
   ```
   git commit -m "$(cat <<'EOF'
   fix: <generated message>
   EOF
   )"
   ```
5. Do NOT use `--no-verify`. If pre-commit hook fails, fix and retry (up to 2 times).
6. Push: `git push`. Do NOT use `--no-verify`.

### Step 8: Reply to PR comments

For each issue group that was fixed, reply to ONE comment in the group (the first one) using:

```
gh api repos/{owner}/{repo}/pulls/comments/<comment_id>/replies -f body="Fixed in <short-sha>."
```

This avoids spamming every duplicate comment with a reply.

### Step 9: Return to original branch

If `ORIGINAL_BRANCH` != `PR_BRANCH`, run `git checkout <ORIGINAL_BRANCH>`.

### Step 10: Confirm

Report the result:
- Number of issues fixed (grouped count)
- Files modified
- Commit hash and message
- PR URL
- Branch returned to
- Suggest: "Run `/loop 15m /pr-fix watch <PR_NUMBER>` to babysit this PR."

---

## Watch Mode

Watch mode is designed for use with `/loop` to babysit a PR. It checks CI status, new review comments, and PR conversations on each invocation.

### Step W1: Pre-flight

1. Extract PR number from `$ARGUMENTS` (after `watch`).
2. Validate PR exists and is open: `gh pr view <PR_NUMBER> --json number,state,headRefName,title`.
3. Extract owner/repo: `gh repo view --json owner,name -q '.owner.login + "/" + .name'`.

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
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments --paginate
```

Compare the count against `lastCommentCount` from state. If new comments exist:
1. Extract only comments with `id > lastCommentId`
2. Group and deduplicate new comments (same logic as Fix Mode Step 4)
3. For comments with code suggestion blocks: auto-fix if the fix is clear and isolated (single file, unambiguous change)
4. For ambiguous comments: summarize and notify the user — do NOT auto-fix

### Step W5: Check PR conversations

Fetch PR issue comments (general discussion, not inline reviews):
```
gh api repos/{owner}/{repo}/issues/<PR_NUMBER>/comments
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
