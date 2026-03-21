Fetch inline review comments from a GitHub PR, group by issue type, apply fixes, and push — all in an isolated git worktree. Supports `watch` submode for PR babysitting and `all` submode to fix every open PR with review comments.

## Instructions

Follow these steps precisely. Do NOT add a Co-Authored-By line to commits.

### Argument Parsing

**Compact-state recovery pre-check**: After detecting mode and PR target below, check for a matching compact state file. For fix mode, check `.claude/.pr-fix-compact-state-<PR_NUMBER>.json`. For all mode, check `.claude/.pr-fix-compact-state-all.json`. If the file exists and its saved `mode` and `pr_number` (or `pr_list`) match the current invocation, restore all state variables from the file and skip any already-completed steps. The compact state file is deleted at the end of a successful run (see Step 9 / Step A6).

Parse `$ARGUMENTS` for one of three modes:

**Global flag — `--minor`**: If `--minor` is present anywhere in `$ARGUMENTS`, set `INCLUDE_MINOR = true` and strip it before further parsing. Default: `INCLUDE_MINOR = false`. When false, CodeRabbit comments with `_🟡 Minor_` severity are filtered out in Step 4a. When true, all severities are processed.

Parse the remaining `$ARGUMENTS` for one of three modes:

- **Fix mode** (default): `$ARGUMENTS` is a PR number (e.g., `3`) or empty.
- **Watch mode**: `$ARGUMENTS` starts with `watch` followed by a PR number (e.g., `watch 3`).
- **All mode**: `$ARGUMENTS` starts with `all`, optionally followed by `--dry-run` and/or a number limit (e.g., `all`, `all --dry-run`, `all 3`, `all --dry-run 3`).

All modes support `--minor` (e.g., `/pr-fix 3 --minor`, `/pr-fix watch 3 --minor`, `/pr-fix all --minor --dry-run 3`).

If watch mode is detected, skip to the **Watch Mode** section below.
If all mode is detected, skip to the **All Mode** section below.

For fix mode, extract the PR number from `$ARGUMENTS`. If empty, try auto-detection: `gh pr view --json number -q .number 2>/dev/null`. If auto-detection fails, ask the user "Which PR number should I fix?" and wait for their response.

---

## Fix Mode

### Step 1: Pre-flight checks

1. **GitHub CLI available**: Run `gh --version`. If unavailable, tell the user "GitHub CLI (gh) is required. Install with: brew install gh" and stop.
2. **PR exists and is open**: Run `gh pr view <PR_NUMBER> --json number,state,headRefName,baseRefName,title`. If the PR does not exist or is not open, report the error and stop. Save `headRefName` as `PR_BRANCH` and `title` as `PR_TITLE`.
3. **Extract owner/repo**: Run `gh repo view --json owner,name -q '.owner.login + "/" + .name'`. Save as `OWNER_REPO`.
4. **Clean stale worktree for this PR**: Run `git worktree list`. If an entry exists with path `.claude/worktrees/pr-fix-<PR_NUMBER>`, remove it with `git worktree remove --force <path>`. Only remove the worktree matching the current PR number — do NOT remove other `pr-fix-*` worktrees, as they may belong to concurrent runs.

### Step 2: Create worktree

1. Fetch the latest remote state: `git fetch origin <PR_BRANCH>`.
2. Create an isolated worktree attached to a local branch tracking the PR head:

   ```bash
   git worktree add -b <PR_BRANCH> .claude/worktrees/pr-fix-<PR_NUMBER> origin/<PR_BRANCH>
   ```

   If the local branch already exists, use `git worktree add .claude/worktrees/pr-fix-<PR_NUMBER> <PR_BRANCH>` instead.
3. If worktree creation fails (e.g., branch already checked out), report the error and stop.

Save `.claude/worktrees/pr-fix-<PR_NUMBER>` as `WORKTREE_DIR`.

### Step 3: Fetch review comments

Fetch all inline review comments:

```bash
gh api repos/{OWNER_REPO}/pulls/<PR_NUMBER>/comments --paginate
```

For each comment, extract: `id`, `path`, `line`, `original_line`, `body`, `diff_hunk`.

If no comments are found, report "No review comments on PR #<PR_NUMBER>" and skip to Step 9.

### Compact Checkpoint FC1

After fetching raw comment payloads, estimate context window usage. If the conversation is ≥60% full:

1. Write `.claude/.pr-fix-compact-state-<PR_NUMBER>.json`:

   ```json
   {
     "mode": "fix",
     "pr_number": <PR_NUMBER>,
     "pr_branch": "<PR_BRANCH>",
     "pr_title": "<PR_TITLE>",
     "owner_repo": "<OWNER_REPO>",
     "worktree_dir": "<WORKTREE_DIR>",
     "raw_comments": <full comments array from Step 3>
   }
   ```

2. Run `/compact` with the hint: `"Compacting mid-execution of /pr-fix fix mode. PR #<PR_NUMBER> (<PR_TITLE>), worktree at <WORKTREE_DIR>. State saved to .claude/.pr-fix-compact-state-<PR_NUMBER>.json. Resuming at Step 4 (group and fix comments)."`
3. After compaction, read `.claude/.pr-fix-compact-state-<PR_NUMBER>.json` to restore `PR_NUMBER`, `PR_BRANCH`, `PR_TITLE`, `OWNER_REPO`, `WORKTREE_DIR`, and the raw comments array, then continue to Step 4.

If context usage is below 60%, skip this checkpoint and proceed directly to Step 4.

### Step 4: Group, deduplicate, triage, and prioritize comments

#### 4a: Filter non-actionable and minor-severity comments

Before grouping, discard the following — they are never fix requests:

- **CodeRabbit Walkthrough/Summary**: Any comment where `user.login == "coderabbitai[bot]"` AND it is a PR-level issue comment (not an inline review comment on a file). These are AI-generated PR summaries.
- Any comment whose body starts with "## Walkthrough", "## Summary", "## Changes", or similar section headings with no inline file reference.

**Severity filter** (applies only when `INCLUDE_MINOR` is false, which is the default):

- For comments from `coderabbitai[bot]`: parse the comment body for severity markers using the pattern `_(🔴 Critical|🟠 Major|🟡 Minor)_`. If the severity is `🟡 Minor`, discard the comment. If no severity marker is found, keep the comment (treat as potentially important).
- Comments from `copilot[bot]`, `greptile-apps[bot]`, `greptileai[bot]`, and all other reviewers: keep all comments regardless — these bots do not emit severity markers, so filtering is not possible.
- Track the count of discarded minor comments as `MINOR_FILTERED_COUNT` for display in Step 4e.

When `INCLUDE_MINOR` is true, skip this severity filter entirely — all comments pass through.

#### 4b: Group comments

Group remaining comments that describe the **same underlying issue**:

- Comments with identical `body` text (ignoring trailing whitespace and code suggestion blocks) are grouped together
- Comments describing the same fix pattern across different files (detected by similar body structure) should also be grouped

For each unique issue group, extract: **Issue title**, **Affected files** (`path:line`), **Comment body** (first 200 chars), **Comment IDs**, **Reviewer login**.

#### 4c: Classify each group into a tier

Assign each issue group a tier:

**Tier 1 — Auto-fix** (apply in Step 5 without asking):

- Contains a code suggestion block (` ```suggestion ` fenced block) — highest confidence
- Format/string fix: missing `###` heading prefix on a marker, spacing in checkboxes, off-by-one step references in prose
- Missing entry in an additive list or table (COMMANDS.md, validator marker list, test marker list)
- Variable name inconsistency (e.g., `{owner}/{repo}` should be `OWNER_REPO`)
- Broken tool-abstraction syntax (`WRITE_FILE` or `READ_FILE` missing required arguments)
- From `coderabbitai[bot]` inline (file-level) comment with a clear, localized fix

**Tier 2 — Show & confirm** (display full comment, wait for user approval before fixing):

- Affected file is in the security-sensitive list: `core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `generator/generate.py`, `hooks/pre-commit`, `hooks/pre-push`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- From `copilot[bot]` — catches logic errors/edge cases; show before applying
- From `greptile-apps[bot]` or `greptileai[bot]` (unless it contains a code suggestion block, which promotes to Tier 1) — these catch real architectural issues; show before applying
- Comment body describes a behavior change (not just a cosmetic fix)
- Multiple conflicting fixes suggested for the same location

**Tier 3 — Skip** (report to user but do not fix):

- Comment describes a design/architecture mismatch ("spec says X but impl does Y")
- Comment is ambiguous about what the correct fix is
- Affected file is a generated output: `platforms/claude/SKILL.md`, `platforms/cursor/specops.mdc`, `platforms/codex/SKILL.md`, `platforms/copilot/specops.instructions.md`, `skills/specops/SKILL.md` — these must be fixed at their source (see Step 5 generated-file rule)

#### 4d: Assign priority

Within each tier, assign a priority tag for ordering:

- **P0**: Broken syntax, undefined/inconsistent variables, detached HEAD issues, missing required schema fields — fix these first
- **P1**: Missing entries in validators/tests/docs, format inconsistencies — fix in normal order
- **P2**: Security-sensitive file changes (Tier 2) — fix after Tier 1 with approval
- **P3**: Skip with explanation (Tier 3) — listed last

#### 4e: Display triage summary

```text
Found <N> review comments grouped into <M> unique issues:
Severity filter: <MINOR_FILTERED_COUNT> minor comments excluded (use --minor to include)

Triage: <T1> auto-fix, <T2> need approval, <T3> skipped

✅ AUTO-FIX:
  Issue 1/M [P0]: <issue title>
    Reviewer: coderabbitai[bot] | Files: <path1>:<line>
    Comment: <truncated body>

  Issue 2/M [P1]: <issue title>
    Reviewer: coderabbitai[bot] | Files: <path2>:<line>
    Comment: <truncated body>

⚠️  NEEDS APPROVAL:
  Issue 3/M [P2]: <issue title>
    Reviewer: copilot[bot] | Files: core/workflow.md:<line>
    Comment: <truncated body>

  Issue 4/M [P2]: <issue title>
    Reviewer: greptile-apps[bot] | Files: <path>:<line>
    Comment: <truncated body>

⊘ SKIPPED:
  Issue 5/M: <issue title> — CodeRabbit Walkthrough (not a fix request)
```

When `INCLUDE_MINOR` is true, replace the severity filter line with: `Severity filter: off (--minor flag active, all severities included)`. When `MINOR_FILTERED_COUNT` is 0, display: `Severity filter: active (no minor comments found)`.

### Step 5: Fix each issue group

Process groups in priority order (P0 → P1 → P2). Maximum 10 groups total — if more, warn and stop.

**Tier 3 groups are not processed here** — they were already reported as skipped in Step 4.

#### For each Tier 1 (auto-fix) group

1. **Present**: Show the full comment body and all affected file paths with their diff hunks.
2. **Generated-file re-routing**: If the affected file is a generated output (`platforms/claude/SKILL.md`, `platforms/cursor/specops.mdc`, `platforms/codex/SKILL.md`, `platforms/copilot/specops.instructions.md`, `skills/specops/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`): do NOT edit the generated file. Instead, identify the source file in `core/` or `generator/templates/` that produces the relevant section. Apply the fix to the source file. Report: "Fixing in source file `<core/file.md>` — regeneration in Step 6 will propagate to generated outputs." Skip to the next group if no clear source file can be identified.
3. **Read**: Read each affected file from the worktree path (`<WORKTREE_DIR>/<path>`) to understand the current code.
4. **Fix**: Apply the code change. If a code suggestion block is present, use it as the basis but verify correctness. All edits must target files inside `WORKTREE_DIR`.
5. **Report**: Tell the user what was changed in each file.

#### For each Tier 2 (needs approval) group

1. **Present**: Show the full comment body, affected file paths with diff hunks, and explain why it requires approval (e.g., "This touches `core/workflow.md`, a security-sensitive file").
2. **Ask**: "Apply this fix? (yes/no/skip)"
3. If approved: apply fix as above (including generated-file re-routing check).
4. If declined or skipped: record as `SKIPPED: user declined` and continue.

After all groups are processed, proceed to Step 6.

### Step 6: Regenerate and validate

Check the list of modified files (relative to the worktree).

**If any files under `core/`, `generator/templates/`, `generator/generate.py`, or `platforms/*/platform.json` were modified:**

- Run `python3 generator/generate.py --all` from `WORKTREE_DIR`
- Stage regenerated files

**If any checksummed files were modified** (`skills/specops/SKILL.md`, `schema.json`, `platforms/claude/SKILL.md`, `platforms/claude/platform.json`, `platforms/cursor/specops.mdc`, `platforms/cursor/platform.json`, `platforms/codex/SKILL.md`, `platforms/codex/platform.json`, `platforms/copilot/specops.instructions.md`, `platforms/copilot/platform.json`, `core/workflow.md`, `core/safety.md`, `hooks/pre-commit`, `hooks/pre-push`, `scripts/install-hooks.sh`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`):

- Regenerate checksums from `WORKTREE_DIR`:

  ```bash
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

   ```bash
   git -C <WORKTREE_DIR> commit -m "$(cat <<'EOF'
   fix: <generated message>
   EOF
   )"
   ```

5. Do NOT use `--no-verify`. If pre-commit hook fails, fix and retry (up to 2 times).
6. Push: `git -C <WORKTREE_DIR> push`. Do NOT use `--no-verify`.

### Step 8: Reply to PR comments

For each issue group that was fixed, reply to ONE comment in the group (the first one) using:

```bash
gh api repos/{OWNER_REPO}/pulls/comments/<comment_id>/replies -f body="Fixed in <short-sha>."
```

This avoids spamming every duplicate comment with a reply.

### Step 9: Cleanup worktree

Remove the worktree:

```bash
git worktree remove <WORKTREE_DIR> --force
```

If the `.claude/worktrees/` directory is empty after cleanup, remove it: `rmdir .claude/worktrees/ 2>/dev/null`.

Delete the compact state file if it exists: `rm -f .claude/.pr-fix-compact-state-<PR_NUMBER>.json`.

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
2. Validate PR exists and is open: `gh pr view <PR_NUMBER> --json number,state,headRefName,title`. Save `headRefName` as `PR_BRANCH`.
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

```bash
gh run list --branch <PR_BRANCH> --json databaseId,status,conclusion,name --limit 10
```

Categorize each workflow run:

- **Passing**: `conclusion == "success"`
- **Failing**: `conclusion == "failure"`
- **In progress**: `status == "in_progress" || status == "queued"`

### Step W4: Check for new review comments

Fetch inline review comments:

```bash
gh api repos/{OWNER_REPO}/pulls/<PR_NUMBER>/comments --paginate
```

Compare the count against `lastCommentCount` from state. If new comments exist:

1. Extract only comments with `id > lastCommentId`
2. Apply severity filter: if `INCLUDE_MINOR` is false (default), discard CodeRabbit comments with `_🟡 Minor_` severity marker. Track filtered count for the status dashboard (Step W6).
3. Group and deduplicate remaining new comments (same logic as Fix Mode Step 4, including Greptile promotion to Tier 2)
4. For comments with code suggestion blocks: auto-fix if the fix is clear and isolated (single file, unambiguous change)
5. For ambiguous comments: summarize and notify the user — do NOT auto-fix

### Step W5: Check PR conversations

Fetch PR issue comments (general discussion, not inline reviews):

```bash
gh api repos/{OWNER_REPO}/issues/<PR_NUMBER>/comments
```

Compare count against `lastIssueCommentCount`. If new messages:

1. Summarize each new message
2. If a reviewer asks a question, draft a reply for the user's approval before posting

### Step W6: Report status dashboard

Display a concise summary:

```text
PR #<N> Status (checked at HH:MM)
├─ CI: ✓ All checks passing / ✗ <name> failed / ⏳ <name> in progress
├─ Review comments: <N> new since last check (<M> auto-fixed, <K> need attention, <J> minor filtered)
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
- **No compaction in Watch mode** — it is intentionally lightweight and completes in a single short turn. Compaction checkpoints apply only to Fix mode and All mode.

---

## Compaction Protocol

Long-running executions (Fix mode with many issue groups, All mode with multiple PRs) can accumulate significant context from API payloads, file reads, and validation output. Compaction checkpoints prevent hitting context limits mid-execution.

### When to compact

At each designated checkpoint (FC1, AC1, AC2), estimate context window usage. If the conversation is **≥60% full**, trigger the compaction sequence. If below 60%, skip the checkpoint and continue.

### How to compact

1. **Save state**: Write a mode-specific compact state file with all critical runtime variables. For fix mode, use `.claude/.pr-fix-compact-state-<PR_NUMBER>.json`. For all mode, use `.claude/.pr-fix-compact-state-all.json`. This ensures concurrent fix-mode runs for different PRs do not clobber each other's state.
2. **Compact**: Run `/compact` with a descriptive hint summarizing the current state (mode, PR number, title, worktree path, what step resumes next). This gives the compaction algorithm enough context to produce a useful summary.
3. **Restore**: Immediately after compaction, read the mode-specific compact state file and restore all saved variables into the current session context.
4. **Continue**: Proceed from the step immediately after the checkpoint — do not re-execute any already-completed steps.

### State file lifecycle

- **Path**: `.claude/.pr-fix-compact-state-<PR_NUMBER>.json` (fix mode) or `.claude/.pr-fix-compact-state-all.json` (all mode)
- **Created**: Written at each compact checkpoint when usage is ≥60%
- **Updated**: Overwritten at each subsequent checkpoint with latest progress
- **Deleted**: Removed at successful run completion (Step 9 for Fix mode, Step A7 for All mode)
- **Recovery**: If the file exists at command start and matches the current invocation, restore state and resume (see Argument Parsing pre-check)

---

## All Mode

All mode discovers every open PR with review comments and fixes them all, each in its own isolated git worktree.

### Argument Parsing (All Mode)

Parse everything after `all` in `$ARGUMENTS` (after global `--minor` flag has been stripped):

- `--dry-run` or `dry-run`: Preview mode — discover and display what would be fixed without applying changes.
- `--minor`: Include minor-severity comments (see global flag description in Argument Parsing above).
- A number (e.g., `3`): Override the maximum PR limit (default is 5).
- All flags can be combined: `all --dry-run --minor 3` or `all 3 --dry-run --minor`.

### Step A1: Pre-flight checks

1. **GitHub CLI available**: Run `gh --version`. If unavailable, tell the user "GitHub CLI (gh) is required. Install with: brew install gh" and stop.
2. **Extract owner/repo**: Run `gh repo view --json owner,name -q '.owner.login + "/" + .name'`. Save as `OWNER_REPO`.
3. **Clean stale worktrees for discovered PRs**: Run `git worktree list`. For each PR in `PR_LIST`, if an entry exists with path `.claude/worktrees/pr-fix-<NUMBER>`, remove it with `git worktree remove --force <path>`. Only remove worktrees matching PRs in the current `PR_LIST` — do NOT remove other `pr-fix-*` worktrees, as they may belong to concurrent runs.

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

   ```bash
   gh api repos/{OWNER_REPO}/pulls/<NUMBER>/comments --paginate
   ```

2. For each comment, extract: `id`, `path`, `line`, `original_line`, `body`, `diff_hunk`.
3. If no comments are found for this PR, remove it from `PR_LIST` and continue.
4. Apply the **full Fix Mode Step 4 pipeline**:
   - **4a**: Filter non-actionable comments (CodeRabbit Walkthrough/Summary PR-level comments, comments starting with "## Walkthrough"/"## Summary"/"## Changes", and minor-severity CodeRabbit comments when `INCLUDE_MINOR` is false).
   - **4b**: Group remaining comments that describe the same underlying issue (same body structure across files, identical body text).
   - **4c**: Classify each group into Tier 1 (auto-fix), Tier 2 (needs approval), or Tier 3 (skip) using the exact criteria from Fix Mode Step 4c.
   - **4d**: Assign priority tags (P0–P3) using the exact criteria from Fix Mode Step 4d.
5. Store the tier and priority on each issue group (used by Step A5b).
6. For each unique issue group, create a summary with issue title, tier, priority, affected files, comment body, and comment IDs.

### Step A4: Display discovery dashboard

Display the full summary:

```text
PR Fix-All Discovery
=====================

Found <N> open PRs with review comments:

PR #<N1>: <title>
  Branch: <headRefName> → <baseRefName>
  Comments: <M> comments in <K> issue groups
  Triage: <T1> auto-fix, <T2> need approval, <T3> skipped
  Issues:
    ✅ 1. <issue title> [P0] (<file count> files) — auto-fix
    ⚠️  2. <issue title> [P2] (<file>) — needs approval
    ⚠️  3. <issue title> [P2] (<file>) — needs approval (Greptile architectural issue)

PR #<N2>: <title>
  Branch: <headRefName> → <baseRefName>
  Comments: <M> comments in <K> issue groups
  Triage: <T1> auto-fix, <T2> need approval, <T3> skipped
  Issues:
    ✅ 1. <issue title> [P1] (<file count> files) — auto-fix

Total: <X> PRs, <Y> issue groups, <Z> comments
Triage totals: <T1> auto-fix, <T2> need approval, <T3> skipped
```

If `--dry-run` is active, display this dashboard and stop with message: "Dry run complete. Run `/pr-fix all` without --dry-run to apply fixes."

### Compact Checkpoint AC1

After displaying the discovery dashboard, estimate context window usage. If the conversation is ≥60% full:

1. Write `.claude/.pr-fix-compact-state-all.json`:

   ```json
   {
     "mode": "all",
     "owner_repo": "<OWNER_REPO>",
     "pr_list": <full PR_LIST array>,
     "current_pr_index": 0,
     "results": []
   }
   ```

2. Run `/compact` with the hint: `"Compacting mid-execution of /pr-fix all mode. Discovered <N> PRs: [PR numbers and titles]. State saved to .claude/.pr-fix-compact-state-all.json. Resuming at Step A5 (process each PR)."`
3. After compaction, read `.claude/.pr-fix-compact-state-all.json` to restore `OWNER_REPO`, `PR_LIST`, and `results`, then continue to Step A5.

If context usage is below 60%, skip this checkpoint and proceed directly to Step A5.

### Step A5: Process each PR in a worktree

For each PR in `PR_LIST` (sequentially, one at a time):

#### Step A5a: Create worktree

1. Fetch the latest remote state: `git fetch origin <headRefName>`.
2. Create an isolated worktree attached to a local branch tracking the PR head:

   ```bash
   git worktree add -b <headRefName> .claude/worktrees/pr-fix-<NUMBER> origin/<headRefName>
   ```

   If the local branch already exists, use `git worktree add .claude/worktrees/pr-fix-<NUMBER> <headRefName>` instead.
3. If worktree creation fails, log the error, record this PR as `SKIPPED: <reason>`, and continue to the next PR.

Save `.claude/worktrees/pr-fix-<NUMBER>` as `WORKTREE_DIR`.

#### Step A5b: Fix each issue group

Process groups in priority order (P0 → P1 → P2). Maximum 10 groups — if more, warn and skip remaining.

**Tier 3 groups are not processed here** — they were already reported as skipped in Step A4.

##### For each Tier 1 (auto-fix) group in All Mode

1. **Present**: Show the full comment body and all affected file paths with their diff hunks.
2. **Generated-file re-routing**: If the affected file is a generated output (`platforms/claude/SKILL.md`, `platforms/cursor/specops.mdc`, `platforms/codex/SKILL.md`, `platforms/copilot/specops.instructions.md`, `skills/specops/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`): do NOT edit the generated file. Instead, identify the source file in `core/` or `generator/templates/` that produces the relevant section. Apply the fix to the source file. Report: "Fixing in source file `<core/file.md>` — regeneration in Step A5c will propagate to generated outputs." Skip to the next group if no clear source file can be identified.
3. **Read**: Read each affected file from `<WORKTREE_DIR>/<path>` to understand the current code.
4. **Fix**: Apply the code change. If a code suggestion block is present, use it as the basis but verify correctness. All edits must target files inside `WORKTREE_DIR`.
5. **Report**: Tell the user what was changed in each file.

##### For each Tier 2 (needs approval) group in All Mode

1. **Present**: Show the full comment body, affected file paths with diff hunks, and explain why it requires approval (e.g., "This touches `core/workflow.md`, a security-sensitive file").
2. **Ask**: "Apply this fix? (yes/no/skip)"
3. If approved: apply fix as above (including generated-file re-routing check).
4. If declined or skipped: record as `SKIPPED: user declined` and continue.

#### Step A5c: Regenerate and validate

Same logic as Fix Mode Step 6, but run from `WORKTREE_DIR`.

If any validation fails after 2 retries, record this PR as `FAILED: validation error — <details>` and continue to the next PR (do not push broken code).

#### Step A5d: Commit and push

1. Stage all modified files: `git -C <WORKTREE_DIR> add -A`
2. Un-stage sensitive files (`.env*`, `credentials.json`, `*.pem`, `*.key`, SSH keys) if any.
3. Generate a commit message with `fix:` prefix summarizing the review fixes for this PR.
4. Commit using heredoc:

   ```bash
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

```bash
gh api repos/{OWNER_REPO}/pulls/comments/<comment_id>/replies -f body="Fixed in <short-sha>."
```

#### Step A5f: Record result

Save the result for this PR:

- **Status**: `FIXED`, `SKIPPED`, or `FAILED`
- **Commit SHA** (if fixed)
- **Files modified** (list)
- **Issues auto-fixed** (Tier 1 applied count)
- **Issues approved** (Tier 2 user-approved count)
- **Issues skipped by user** (Tier 2 user-declined count)
- **Issues skipped (tier 3)** (Tier 3 not-actionable count)
- **Error message** (if skipped or failed)

#### Compact Checkpoint AC2 (between PR iterations)

After recording the result for this PR and before beginning the next PR, estimate context window usage. If the conversation is ≥60% full AND there are more PRs remaining:

1. Update `.claude/.pr-fix-compact-state-all.json`:

   ```json
   {
     "mode": "all",
     "owner_repo": "<OWNER_REPO>",
     "pr_list": <full PR_LIST array>,
     "current_pr_index": <index of the NEXT PR to process>,
     "results": <array of all results recorded so far>
   }
   ```

2. Run `/compact` with the hint: `"Compacting mid-execution of /pr-fix all mode. Completed PR #<N> (<title>). <K> of <total> PRs processed so far. State saved to .claude/.pr-fix-compact-state-all.json. Resuming with next PR."`
3. After compaction, read `.claude/.pr-fix-compact-state-all.json` to restore `OWNER_REPO`, `PR_LIST`, `current_pr_index`, and `results`, then continue with the next PR at index `current_pr_index`.

If context usage is below 60% or no more PRs remain, skip this checkpoint and continue the loop normally.

### Step A6: Cleanup worktrees

For each worktree created during this run:

```bash
git worktree remove .claude/worktrees/pr-fix-<NUMBER> --force
```

If the `.claude/worktrees/` directory is empty after cleanup, remove it: `rmdir .claude/worktrees/ 2>/dev/null`.

Delete the compact state file if it exists: `rm -f .claude/.pr-fix-compact-state-all.json`.

### Step A7: Summary dashboard

Display the consolidated results:

```text
PR Fix-All Summary
===================

Processed: <N> PRs

✓ FIXED:
  PR #<N1>: <title>
    Commit: <sha> — fix: <message>
    Auto-fixed: <K1> | Approved: <K2> | Skipped (user): <K3> | Skipped (tier 3): <K4>
    Files modified: <file list>

  PR #<N2>: <title>
    Commit: <sha> — fix: <message>
    Auto-fixed: <K1> | Approved: <K2> | Skipped (user): <K3> | Skipped (tier 3): <K4>
    Files modified: <file list>

⊘ SKIPPED:
  PR #<N3>: <title> — <reason>

✗ FAILED:
  PR #<N4>: <title> — <reason>

Totals: <X> fixed, <Y> skipped, <Z> failed
```

If any PRs were fixed, suggest: "Run `/pr-fix all --dry-run` to check for remaining review comments."

If any PRs were skipped or failed, suggest: "Use `/pr-fix <NUMBER>` to handle individual PRs that couldn't be processed."
