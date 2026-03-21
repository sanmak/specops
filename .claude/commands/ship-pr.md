Commit all changes to a new branch, push, and open a PR for review. The original branch stays clean.

## Instructions

This command performs a commit → branch → push → PR workflow. Follow these steps precisely. Do NOT add a Co-Authored-By line to the commit.

---

## Step 0: Record the original branch

Run `git rev-parse --abbrev-ref HEAD` and save the result as `ORIGINAL_BRANCH`.

Set `TARGET_BRANCH` = `ORIGINAL_BRANCH`.

(The PR will always target the branch the user was on when they ran this command.)

---

## Part 1: Commit

### Step 1: Check for changes

Run `git status` to see the current state. If there are no modified, new, or deleted files (working tree is clean AND no staged changes), inform the user "Nothing to ship" and STOP.

### Step 2: Identify sensitive files

Before staging, check if any of these patterns appear in the untracked or modified files:

- `.env`, `.env.*`
- `credentials.json`, `secrets.json`, `*.pem`, `*.key`
- Any file with "secret", "credential", or "token" in its name
- `id_rsa`, `id_ed25519`, or any SSH private key files

If any are found, list them with a WARNING and do NOT stage them. Proceed with staging all other files.

### Step 3: Auto-stage files

Run `git add -A` to stage all changes (this respects `.gitignore` automatically).

Then un-stage any sensitive files identified in Step 2 using `git reset HEAD <file>` for each one.

### Step 4: Check for source/generated file consistency

Examine the staged files list with `git diff --cached --name-only`.

**If any files under `core/`, `generator/templates/`, `generator/generate.py`, or `platforms/*/platform.json` are staged:**

- Run `python3 generator/generate.py --all` to regenerate platform outputs
- Stage the regenerated files: `git add platforms/ skills/ .claude-plugin/`

**If any of these checksummed files are staged** (`skills/specops/SKILL.md`, `schema.json`, `platforms/claude/SKILL.md`, `platforms/claude/platform.json`, `platforms/cursor/specops.mdc`, `platforms/cursor/platform.json`, `platforms/codex/SKILL.md`, `platforms/codex/platform.json`, `platforms/copilot/specops.instructions.md`, `platforms/copilot/platform.json`, `core/workflow.md`, `core/safety.md`, `hooks/pre-commit`, `hooks/pre-push`, `scripts/install-hooks.sh`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`):

- Regenerate checksums: run `shasum -a 256 skills/specops/SKILL.md schema.json platforms/claude/SKILL.md platforms/claude/platform.json platforms/cursor/specops.mdc platforms/cursor/platform.json platforms/codex/SKILL.md platforms/codex/platform.json platforms/copilot/specops.instructions.md platforms/copilot/platform.json core/workflow.md core/safety.md hooks/pre-commit hooks/pre-push scripts/install-hooks.sh .claude-plugin/plugin.json .claude-plugin/marketplace.json > CHECKSUMS.sha256`
- Stage it: `git add CHECKSUMS.sha256`

### Step 5: Review changes

Run `git diff --cached --stat` for a summary and `git diff --cached` for the full diff. Analyze the changes to understand their purpose and scope. Save this analysis — you will use it for the PR body.

**Tip**: Run `/pre-pr` before `/ship-pr` to catch issues that review bots (CodeRabbit, Copilot, Greptile) would flag in PR review.

### Step 5.5: Documentation staleness check

After reviewing the diff, quickly check if the staged changes might affect documentation. Get the staged file list from the `git diff --cached --name-only` output you already have.

Flag potential staleness if ANY of these patterns match staged files:

- `core/` or `generator/` files → `CLAUDE.md`, `README.md`, `docs/STRUCTURE.md` may need updates
- `schema.json` → `docs/REFERENCE.md`, example configs may need updates
- `.claude/commands/` files → `CLAUDE.md` commands table may need updates
- `platforms/*/platform.json` → `README.md` platforms table may need updates
- `scripts/*.sh` → `CLAUDE.md` key commands may need updates
- `hooks/*` → `CLAUDE.md` security-sensitive files list may need updates
- `.github/workflows/` → `CLAUDE.md` CI notes, `CONTRIBUTING.md` may need updates

If ANY of the above patterns match AND the commit does NOT already include the affected docs, display this advisory:

> **Tip**: This commit touches files that may affect documentation. Run `/docs-sync` after the PR is merged to check for stale docs.

Do NOT block the commit. This is informational only. Proceed to Step 6 regardless.

If none of the patterns match, or if the commit already includes the affected doc files, skip this step silently.

### Step 6: Generate commit message

Based on the actual diff, generate a conventional commit message:

**Prefix** (choose exactly one):

- `feat:` -- new feature or capability
- `fix:` -- bug fix
- `chore:` -- version bumps, CI, dependencies, config changes
- `docs:` -- documentation only changes
- `test:` -- test additions or fixes
- `refactor:` -- code restructuring with no behavior change

**Message**: Concise 1-2 sentence summary focused on WHY, not WHAT. Do NOT include a Co-Authored-By line.

Save the generated commit message — you will use it for branch naming and PR title.

### Step 7: Commit

Run the commit using a heredoc for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
<your generated message>
EOF
)"
```

Do NOT use `--no-verify`. If the pre-commit hook fails:

1. Read the error output
2. Fix the issue (regenerate files, fix JSON, etc.)
3. Re-stage changes with `git add`
4. Retry the commit
5. If it fails again, report errors to the user and STOP

---

## Security Review Reminder

After committing, check if any of the following security-sensitive files are in the commit (use `git diff HEAD~1 --name-only`):

`core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `schema.json`, `spec-schema.json`, `platforms/claude/SKILL.md`, `setup.sh`, `scripts/remote-install.sh`, `generator/generate.py`, `hooks/pre-commit`, `hooks/pre-push`

If any match, display this advisory (do NOT block):

> **Tip**: This commit includes security-sensitive files. Consider reviewing carefully before merging the PR.

---

## Part 2: Branch & Move

### Step 8: Generate branch name

From the commit message generated in Step 6, create a branch name:

1. Extract the prefix (e.g., `feat`, `fix`, `chore`, `docs`, `test`, `refactor`)
2. Take the message after the colon, lowercase it
3. Replace spaces and special characters with hyphens
4. Remove trailing hyphens
5. Truncate to 50 characters max
6. Result format: `<prefix>/<slugified-message>` (e.g., `feat/add-dark-mode-toggle`)

Check if the branch already exists with `git branch --list <branch-name>`. If it does, append `-2` (or `-3`, etc.) until you find an unused name.

### Step 9: Move commit to the new branch

Run these commands in order:

1. `git branch <new-branch>` — creates the new branch at HEAD (includes the commit)
2. `git checkout <ORIGINAL_BRANCH>` — switch back to the original branch (still has the commit)
3. `git reset --hard HEAD~1` — remove the commit from the original branch
4. `git checkout <new-branch>` — switch to the new branch (which has the commit)

The original branch is now clean (back to where it was before the commit), and the new branch has the commit.

---

## Part 3: Push & PR

### Step 10: Run pre-push validation

Run these checks before pushing:

1. `python3 generator/validate.py` -- platform validation
2. `shasum -a 256 -c CHECKSUMS.sha256` -- checksum verification
3. `python3 generator/generate.py --all && git diff --exit-code platforms/ skills/ .claude-plugin/` -- generated files freshness
4. `python3 tests/check_schema_sync.py` -- schema structure
5. `bash scripts/run-tests.sh` -- full test suite
6. `npx markdownlint-cli2 "core/**/*.md" "docs/**/*.md" ".claude/commands/**/*.md" "README.md" "CLAUDE.md" "QUICKSTART.md" "CONTRIBUTING.md" "CHANGELOG.md"` -- markdown lint (skip if npx not available)

If any check fails, report the failure. Do NOT push. Switch back to the original branch with `git checkout <ORIGINAL_BRANCH>` and STOP.

### Step 11: Push the new branch

Run `git push -u origin <new-branch>`.

Do NOT use `--no-verify`.

### Step 12: Create PR

Using the diff analysis from Step 5 and the commit message from Step 6, create a PR:

```bash
gh pr create --base <TARGET_BRANCH> --title "<commit message>" --body "$(cat <<'EOF'
## Summary

<2-4 bullet points explaining what changed and why, derived from the diff analysis>

## Changes

<list of files modified with a brief description of each change>

## Test Plan

<bulleted checklist of how to verify these changes>
EOF
)"
```

Save the PR URL from the output.

### Step 13: Return to original branch

Run `git checkout <ORIGINAL_BRANCH>` to switch back to the user's original branch.

### Step 14: Confirm

Report the result:

- PR URL (clickable)
- New branch name
- Target branch
- Commit hash and message
- Reminder: "Your `<ORIGINAL_BRANCH>` branch is unchanged."
