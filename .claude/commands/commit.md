Auto-stage, review, and commit all changes with a conventional commit message.

## Instructions

Follow these steps precisely. Do NOT add a Co-Authored-By line to the commit.

### Step 1: Check for changes

Run `git status` to see the current state of the working tree. If there are no modified, new, or deleted files (working tree is clean), inform the user "Nothing to commit -- working tree clean" and stop.

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

Run `git diff --cached --stat` to get a summary of what will be committed. Also run `git diff --cached` to read the full diff. Analyze the changes to understand their purpose and scope.

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

Based on the actual diff content, generate a conventional commit message following these rules:

**Prefix** (choose exactly one):

- `feat:` -- new feature or capability
- `fix:` -- bug fix
- `chore:` -- version bumps, CI, dependencies, config changes
- `docs:` -- documentation only changes
- `test:` -- test additions or fixes
- `refactor:` -- code restructuring with no behavior change

**Message body**: A concise 1-2 sentence summary focused on WHY the change was made, not WHAT files changed. Look at the actual code diff to understand intent.

**Examples of good messages**:

- `feat: add Gemini platform adapter`
- `fix: validator false-positive on abstraction section headers`
- `chore: bump version to 1.2.0`
- `docs: clarify specsDir path constraints in REFERENCE.md`

Do NOT include:

- A Co-Authored-By line
- File lists in the message
- Generic messages like "update files" or "make changes"

### Step 7: Commit

Run the commit using a heredoc for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
<your generated message>
EOF
)"
```

Do NOT use `--no-verify` -- let the pre-commit hook run. If the hook fails:

1. Read the error output carefully
2. Fix the issue (regenerate files, fix JSON, run shellcheck, etc.)
3. Re-stage any new changes with `git add`
4. Try the commit again with the same message
5. If the hook fails a second time, report the errors to the user and stop

### Step 8: Confirm

Run `git log --oneline -1` to show the committed result. Report success to the user with the commit hash and message.
