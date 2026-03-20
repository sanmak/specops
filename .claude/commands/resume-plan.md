Resume a previously created plan — discovers plan files, syncs with latest main, and presents the plan ready for implementation.

## Instructions

Follow these steps precisely.

### Argument Parsing

Parse `$ARGUMENTS`:
- If non-empty, treat as a plan file identifier: a full filename (e.g., `serene-hugging-orbit.md`), a name without extension (e.g., `serene-hugging-orbit`), or a full path.
- If empty, proceed to plan discovery in Step 1.

### Step 1: Discover and select plan file

**If `$ARGUMENTS` is empty:**

1. List all `.md` files in `~/.claude/plans/` sorted by modification time (newest first): `ls -t ~/.claude/plans/*.md 2>/dev/null`
2. If no files are found, report "No plan files found in `~/.claude/plans/`. Create a plan using Claude Code's plan mode first." and stop.
3. For each plan file (limit to the 15 most recent), extract:
   - The filename (without path)
   - The modification date: `stat -f '%Sm' -t '%Y-%m-%d %H:%M' <file>` (macOS) or `stat -c '%y' <file>` (Linux)
   - The first `#` heading from the file content, or "Untitled plan" if none
4. Display the list as a numbered table:

```
Available plans (most recent first):

 #  Plan file                          Last modified       Title
 1  serene-hugging-orbit.md            2025-03-18 23:14    Plan: Resolve PR #56 Conflicts
 2  majestic-knitting-haven.md         2025-03-17 14:22    Plan: Update README
 ...
```

5. Ask the user: "Which plan would you like to resume? Enter a number or filename." Wait for their response. Save the selection as `PLAN_PATH`.

**If `$ARGUMENTS` is non-empty:**

1. If `$ARGUMENTS` is a full path:
   - Reject if it is outside `~/.claude/plans/` unless the user explicitly confirms.
   - Require `.md` extension.
   - If valid and the file exists, save as `PLAN_PATH`; otherwise report an error and stop.
2. If `$ARGUMENTS` is a filename (with or without `.md`), look for it in `~/.claude/plans/`. Append `.md` if not already present. If found, save as `PLAN_PATH`.
3. If the file is not found, report "Plan file not found: `$ARGUMENTS`. Run `/resume-plan` without arguments to list available plans." and stop.

### Step 2: Read and validate the plan

1. Read the full content of `PLAN_PATH`. Save as `PLAN_CONTENT`.
2. If the file is empty, report "Plan file is empty: `PLAN_PATH`. Nothing to resume." and stop.
3. Extract the first line matching `# ...` (H1 heading) as `PLAN_TITLE`. If no H1 heading exists, use the filename as `PLAN_TITLE`.
4. If the file contains no markdown headings at all (no lines starting with `#`), warn: "This file does not appear to be a structured plan (no headings found). Proceeding anyway."

### Step 3: Check git state

1. Check for detached HEAD: run `git symbolic-ref -q HEAD`. If this fails (exit code non-zero), report: "You are in a detached HEAD state. Please checkout a branch before resuming a plan (`git checkout main` or `git checkout -b <branch-name>`)." and stop.

2. Run `git status` to check the working tree. If there are uncommitted changes (modified, staged, or untracked files — excluding untracked files under `.claude/`), warn the user:

   "There are uncommitted changes in the working tree. These should be committed or stashed before resuming a plan to avoid conflicts."

   Suggest: "Commit with `/commit`, stash with `git stash`, or continue at your own risk."

   Ask: "Continue with uncommitted changes? (yes/no)". If the user says no, stop.

3. Save the current branch name: `git rev-parse --abbrev-ref HEAD` as `CURRENT_BRANCH`.

### Step 4: Determine main branch

1. Detect the main branch name: `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`
2. If that fails, check if `origin/main` exists: `git rev-parse --verify origin/main 2>/dev/null`. If it does, use `main`.
3. If that also fails, check `origin/master`: `git rev-parse --verify origin/master 2>/dev/null`. If it does, use `master`.
4. Save as `MAIN_BRANCH`. If none of the above succeeded, report "Cannot determine the main branch. Please specify it manually." and stop.

### Step 5: Sync with latest code

1. Fetch latest from remote: `git fetch origin`

2. **If `CURRENT_BRANCH` equals `MAIN_BRANCH`:**
   - Pull latest: `git pull origin <MAIN_BRANCH>`
   - If the pull fails, report the error and stop.

3. **If `CURRENT_BRANCH` does not equal `MAIN_BRANCH`:**
   - If the working tree has uncommitted changes (detected in Step 3), stash them first: `git stash --include-untracked`. Save a flag `DID_STASH=true`.
   - Merge latest main into the current branch: `git merge origin/<MAIN_BRANCH> --no-edit`
   - If the merge fails with conflicts:
     - Report: "Merge conflicts detected while syncing with `<MAIN_BRANCH>`. Resolve conflicts first (consider `/resolve-conflicts`) or start from a clean branch."
     - Run `git merge --abort` to restore the working tree.
     - If `DID_STASH`, run `git stash pop` to restore the user's changes.
     - Stop.
   - If the merge succeeds:
     - If `DID_STASH`, run `git stash pop`. If stash pop fails with conflicts, report: "Merge succeeded but your stashed changes conflict with the merged code. Run `git stash show` to review and `git stash drop` after resolving." and stop.
     - Report: "Merged latest `origin/<MAIN_BRANCH>` into `<CURRENT_BRANCH>`."

### Step 6: Validate plan file references

Scan `PLAN_CONTENT` for file paths — look for paths in backtick-quoted strings, markdown links, and "Files to Modify" tables that reference project files.

For each referenced file path, check if the file exists in the current working tree.

If any referenced files are missing, display a warning:

```
Warning: The following files referenced in the plan may no longer exist:
  - path/to/deleted-file.md
  - path/to/moved-file.py

These may have been renamed or removed since the plan was created.
The plan may need adjustment for these files.
```

Do NOT stop. This is informational only.

### Step 7: Present the plan

Display the full plan with context:

```
========================================
  Plan: <PLAN_TITLE>
  Branch: <CURRENT_BRANCH>
  Synced with: <MAIN_BRANCH> (latest)
========================================

<PLAN_CONTENT>
```

Report: "Plan loaded and codebase synced."

### Step 8: SpecOps handoff

After presenting the plan, check if the project uses SpecOps:

1. Check if `.specops.json` exists in the project root.

2. **If `.specops.json` exists:**
   - Report: "SpecOps detected — converting plan to structured spec before implementation."
   - Invoke `/specops from-plan` with `PLAN_CONTENT` as the plan input. This routes through the full SpecOps lifecycle: spec creation (From Plan Mode) → implementation (Phase 3) → completion (Phase 4).
   - Do NOT proceed with direct implementation. The SpecOps workflow handles implementation after spec conversion.

3. **If `.specops.json` does NOT exist:**
   - Report: "No SpecOps configuration found. Ready for direct implementation from the plan above."
