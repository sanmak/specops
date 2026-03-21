Push the current branch to remote after validating all pre-push checks pass.

## Instructions

Follow these steps precisely.

### Step 1: Check current state

Run `git status` to confirm the working tree. If there are uncommitted changes (modified or untracked files), warn the user: "There are uncommitted changes. Run /commit first or commit manually before pushing." and stop.

### Step 2: Check if there is anything to push

Run `git log @{upstream}..HEAD --oneline 2>/dev/null` to see unpushed commits.

If the command fails (no upstream set), note that we will push with `-u` to set upstream tracking.

If there are no unpushed commits and upstream exists, inform the user "Already up to date with remote -- nothing to push" and stop.

### Step 3: Run pre-push validation

Before pushing, proactively run the same checks the pre-push hook will run, so we can fix issues before they block the push:

1. `python3 generator/validate.py` -- platform validation
2. `shasum -a 256 -c CHECKSUMS.sha256` -- checksum verification
3. `python3 generator/generate.py --all && git diff --exit-code platforms/ skills/ .claude-plugin/` -- generated files freshness
4. `python3 tests/check_schema_sync.py` -- schema structure
5. `bash scripts/run-tests.sh` -- full test suite
6. `npx markdownlint-cli2 "core/**/*.md" "docs/**/*.md" ".claude/commands/**/*.md" "README.md" "CLAUDE.md" "QUICKSTART.md" "CONTRIBUTING.md" "CHANGELOG.md"` -- markdown lint (skip if npx not available)

If any check fails:

- Report which check failed and the error output
- If the failure is fixable (stale generated files, stale checksums), explain what the user needs to do
- Do NOT push. Stop and let the user fix the issue.

### Step 4: Push

Determine the current branch: `git rev-parse --abbrev-ref HEAD`

If the branch has an upstream, run:

```bash
git push
```

If the branch does not have an upstream, run:

```bash
git push -u origin <branch-name>
```

Do NOT use `--no-verify` -- let the pre-push hook run normally.

If the push fails, report the error to the user.

### Step 5: Confirm

Run `git log --oneline -1` and report success, including the branch name and remote.
