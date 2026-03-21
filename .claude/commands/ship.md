Commit all changes and push to remote in one operation (combines /commit and /push).

## Instructions

This command performs a full commit-then-push workflow. Follow these steps precisely. Do NOT add a Co-Authored-By line to the commit.

---

## Part 1: Commit

### Step 1: Check for changes

Run `git status` to see the current state. If there are no modified, new, or deleted files (working tree is clean), skip to Part 2 (there may still be unpushed commits to push).

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

Run `git diff --cached --stat` for a summary and `git diff --cached` for the full diff. Analyze the changes to understand their purpose and scope.

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

> **Tip**: This commit touches files that may affect documentation. Run `/docs-sync` after committing to check for stale docs.

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
5. If it fails again, report errors to the user and STOP -- do NOT proceed to Part 2

---

## Security Review Reminder

After committing, check if any of the following security-sensitive files are in the commit (use `git diff HEAD~1 --name-only`):

`core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `schema.json`, `spec-schema.json`, `platforms/claude/SKILL.md`, `setup.sh`, `scripts/remote-install.sh`, `generator/generate.py`, `hooks/pre-commit`, `hooks/pre-push`

If any match, display this advisory (do NOT block the push):

> **Tip**: This commit includes security-sensitive files. Consider running `/security-review` before pushing.

If none of the committed files match this list, skip this step silently.

---

## Part 2: Push

### Step 8: Check if there is anything to push

Run `git log @{upstream}..HEAD --oneline 2>/dev/null` to see unpushed commits.

If no upstream is set, we will push with `-u`. If there are no unpushed commits and upstream exists, inform the user "Already up to date with remote" and stop.

### Step 9: Run pre-push validation

Run these checks before pushing:

1. `python3 generator/validate.py` -- platform validation
2. `shasum -a 256 -c CHECKSUMS.sha256` -- checksum verification
3. `python3 generator/generate.py --all && git diff --exit-code platforms/ skills/ .claude-plugin/` -- generated files freshness
4. `python3 tests/check_schema_sync.py` -- schema structure
5. `bash scripts/run-tests.sh` -- full test suite

If any check fails, report the failure and stop. Do NOT push.

### Step 10: Push

Determine the current branch: `git rev-parse --abbrev-ref HEAD`

Push with `git push` (or `git push -u origin <branch>` if no upstream).

Do NOT use `--no-verify`.

### Step 11: Confirm

Run `git log --oneline -1` and report the full result: commit hash, message, branch, and remote status.
