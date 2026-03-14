Review code changes against SpecOps project-specific patterns. Catches recurring failure modes from real PRs — tool abstraction violations, generated file drift, cross-platform gaps, variable inconsistencies, and more. Complements `full-review-gate` (generic quality) and `pr-fix` (applying bot comments).

## Instructions

Follow these steps precisely.

### Argument Parsing

Parse `$ARGUMENTS`:
- A number (e.g., `11`) → **PR mode**: review that PR's diff
- `staged` → **Staged mode**: review only staged changes (`git diff --cached`)
- `current` or empty → **Current mode**: review all uncommitted changes (`git diff HEAD`)

### Step 1: Collect the diff

**PR mode**:
1. Verify `gh --version` is available. If not, report error and stop.
2. Fetch the PR diff: `gh pr diff <PR_NUMBER>`
3. Get changed file paths: `gh pr view <PR_NUMBER> --json files -q '[.files[].path]'`
4. Save as `DIFF_CONTENT` and `CHANGED_FILES`.
5. Set `REVIEW_TARGET = "PR #<PR_NUMBER>"`

**Staged mode**:
1. `git diff --cached` → `DIFF_CONTENT`
2. `git diff --cached --name-only` → `CHANGED_FILES`
3. Set `REVIEW_TARGET = "staged changes"`

**Current mode**:
1. `git diff HEAD` → `DIFF_CONTENT`
2. `git diff HEAD --name-only` → `CHANGED_FILES`
3. Set `REVIEW_TARGET = "current changes"`

If `DIFF_CONTENT` is empty, report "No changes found for `REVIEW_TARGET`" and stop.

---

### Step 2: Run review passes

Run all four passes. Collect findings as a list with: `[check_id]`, severity (P0/P1/P2/P3), file path, line (if known), description, and suggested fix.

---

#### Pass 1 — P0 Blockers

These indicate a broken build or a push that will definitely fail. Flag every instance.

**[1a] Raw abstract operations in generated outputs**

Read each generated platform file that appears in `CHANGED_FILES` OR read them fresh if Pass 1 is scanning for latent issues:
- `platforms/claude/SKILL.md`
- `platforms/cursor/specops.mdc`
- `platforms/codex/SKILL.md`
- `platforms/copilot/specops.instructions.md`
- `skills/specops/SKILL.md`

Search each for un-substituted abstract operations: `READ_FILE(`, `WRITE_FILE(`, `EDIT_FILE(`, `LIST_DIR(`, `FILE_EXISTS(`, `RUN_COMMAND(`, `ASK_USER(`, `NOTIFY_USER(`, `UPDATE_PROGRESS(`

> **P0** for any match. The generator failed to substitute the platform-specific language.
> Fix: `python3 generator/generate.py --platform <name>` then `python3 generator/validate.py`

**[1b] Detached HEAD risk in worktree creation**

Search `DIFF_CONTENT` (and any `.md` files in `CHANGED_FILES`) for `git worktree add` patterns.

Flag any instance matching: `git worktree add <path> origin/<branch>` WITHOUT a preceding `-b <local-branch>` flag. This creates a worktree in detached HEAD state — `git push` will fail.

> **P0** for any match.
> Fix: Change to `git worktree add -b <local-branch> <path> origin/<branch>`

**[1c] Malformed tool-abstraction calls in source files**

For any `core/*.md` or `generator/templates/*.j2` files in `CHANGED_FILES`, scan for:
- `WRITE_FILE` not followed by `(` on the same or next line
- `READ_FILE` not followed by `(`
- `EDIT_FILE` not followed by `(`

> **P0** for each instance in source files.
> Fix: Add the required `(path, content)` or `(path)` arguments.

---

#### Pass 2 — P1 Must Fix

These must be resolved before the PR merges.

**[2a] Generated file modified directly**

Check `CHANGED_FILES` for any of:
- `platforms/claude/SKILL.md`
- `platforms/cursor/specops.mdc`
- `platforms/codex/SKILL.md`
- `platforms/copilot/specops.instructions.md`
- `skills/specops/SKILL.md`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

If found, check whether `core/` or `generator/templates/` files are ALSO in `CHANGED_FILES`. If the generated file changed BUT no source file changed → the generated file was edited directly, which creates drift on next regeneration.

> **P1** if generated file changed without corresponding source change.
> Fix: Revert the generated file edit, apply the change to the appropriate `core/*.md` or `generator/templates/*.j2` source, and run `python3 generator/generate.py --all`.

**[2b] Cross-platform marker gap**

If `generator/validate.py` or `tests/test_platform_consistency.py` appears in `CHANGED_FILES`:
1. Read `generator/validate.py` — extract all marker strings from the `*_MARKERS` dicts (e.g., `SAFETY_MARKERS`, `STEERING_MARKERS`, etc.)
2. Read `tests/test_platform_consistency.py` — extract all marker strings from its marker lists
3. Compare: any marker present in validate.py but absent from test_platform_consistency.py, or vice versa

> **P1** for each gap.
> Fix: Add the missing marker to whichever file is missing it.

**[2c] Variable inconsistency across modes in the same file**

For any `.md` command file in `CHANGED_FILES` (`.claude/commands/*.md`):

Look for the pattern: a variable is assigned in one mode/section (e.g., `OWNER_REPO=...`) but the same concept is referenced using a different form (e.g., `{owner}/{repo}` or `$owner/$repo`) in another mode/section of the same file.

Specifically check: when a new variable is introduced in Fix/All mode, verify Watch mode uses the same variable.

> **P1** for each inconsistency found.
> Fix: Update all occurrences in the file to use the same variable name.

**[2d] Missing entry in COMMANDS.md quick-lookup table**

If `docs/COMMANDS.md` is NOT in `CHANGED_FILES` but any of these changed:
- A platform skill file (adding a new subcommand or mode)
- `core/workflow.md` (adding a new phase or workflow step)
- `.claude/commands/*.md` (adding a new command)

Read `docs/COMMANDS.md` and check whether the new feature has an entry in the quick-lookup table.

> **P1** if the new feature is absent from COMMANDS.md.
> Fix: Add the missing row to the lookup table.

**[2e] Missing checksum regeneration**

Security-sensitive files that require checksum regeneration: `core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `hooks/pre-commit`, `hooks/pre-push`, `scripts/install-hooks.sh`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `schema.json`, `platforms/claude/SKILL.md`, `platforms/claude/platform.json`, `platforms/cursor/specops.mdc`, `platforms/cursor/platform.json`, `platforms/codex/SKILL.md`, `platforms/codex/platform.json`, `platforms/copilot/specops.instructions.md`, `platforms/copilot/platform.json`, `skills/specops/SKILL.md`.

If any of these appear in `CHANGED_FILES` but `CHECKSUMS.sha256` does NOT appear in `CHANGED_FILES`:

> **P1**: Security-sensitive files changed but `CHECKSUMS.sha256` was not regenerated.
> Fix: Run `bash scripts/bump-version.sh <current-version> --checksums` or manually regenerate checksums.

**[2f] spec.json missing required lifecycle fields**

If any `spec.json` file appears in `CHANGED_FILES`, read it and check for these required fields: `id`, `version`, `status`, `author`, `createdAt`, `updatedAt`, `specopsCreatedWith`, `specopsUpdatedWith`, `requiredApprovals`.

> **P1** for each missing field.
> Fix: Add the missing field with the appropriate value.

**[2g] index.json not updated after spec creation**

If any `spec.json` file appears in `CHANGED_FILES` (new file) but `.specops/index.json` does NOT appear in `CHANGED_FILES`:

> **P1**: Spec created or modified but `.specops/index.json` was not updated.
> Fix: Update `.specops/index.json` to include/reflect the spec entry.

**[2h] Interactive prompts in non-interactive platform outputs**

If `platforms/codex/SKILL.md` or `platforms/copilot/specops.instructions.md` appears in `CHANGED_FILES`:

Read the file and check for `ASK_USER` appearing in sections marked as first-run, initial setup, or non-interactive paths. These platforms cannot interactively prompt users.

Also check: any sentence starting with "Ask the user" or "Prompt the user" in a context that would be the first invocation (before any spec exists).

> **P1** for each interactive prompt in a non-interactive code path.
> Fix: Replace with a note-and-assume pattern ("If no config found, assume defaults and note the assumption").

---

#### Pass 3 — P2 Advisory

Flag for careful review before merge.

**[3a] Security-sensitive file changed**

Check `CHANGED_FILES` for: `core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `generator/generate.py`, `hooks/pre-commit`, `hooks/pre-push`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`.

> **P2** for each match.
> Note: "Security-sensitive file — verify no behavior regressions and no unintended agent instruction changes."

**[3b] Spec/implementation alignment spot check**

If both `.specops/*/requirements.md` (or `design.md`) AND implementation files are in `CHANGED_FILES`:
1. Read the requirements/design file
2. Read the changed implementation files
3. Check: do the key acceptance criteria in the spec reflect what was actually implemented? Look for obvious mismatches (spec says "schema-configured" but impl uses "convention-based", spec says "required approval" but impl skips it, etc.)

> **P2** for each significant mismatch found.
> Note: "Spec says X but implementation does Y — confirm this divergence is intentional."

**[3c] Step reference off-by-one in instruction files**

For any `.md` instruction files in `CHANGED_FILES`, scan for patterns like "see Step N", "in Step N", "skip to Step N", "proceed to Step N".

For each reference found, count the actual steps in the document and verify the referenced step number exists.

> **P2** for dangling or incorrect references.
> Fix: Correct the step number.

---

#### Pass 4 — P3 Quality Notes

**[4a] EARS notation in acceptance criteria**

For any `.specops/*/requirements.md` files in `CHANGED_FILES`, scan acceptance criteria lines (lines under "### Acceptance Criteria" or similar).

Check each criterion: does it use EARS patterns? Expected patterns: starts with WHEN, IF, THE SYSTEM SHALL, WHILE, WHERE. Non-EARS criterion examples: "The system should...", "It must...", "Users can...".

> **P3** for each AC item that doesn't use EARS form.
> Note: "Consider rephrasing to EARS notation (WHEN/IF/THE SYSTEM SHALL)."

**[4b] Empty spec sections**

For any `.specops/` files in `CHANGED_FILES`, check for section headers (lines starting with `##` or `###`) that are immediately followed by another header or end of file, with no content.

> **P3** for each empty section.
> Note: "Section `<heading>` appears empty — intentional or placeholder?"

**[4c] Malformed checkboxes**

For any `.md` files in `CHANGED_FILES`, scan for checkbox patterns. Valid: `- [ ] `, `- [x] `. Invalid: `- []`, `-[ ]`, `- [~]` (non-standard), missing space after `]`.

> **P3** for each malformed checkbox.
> Fix: Correct the spacing.

---

### Step 3: Display findings

Display all collected findings:

```
Core Review — <REVIEW_TARGET>
==========================================

<if no findings>
  ✓ All checks passed. No issues found.
  Ready to merge.

<if findings exist>
P0 BLOCKERS (fix immediately — do not merge):
  ✗ [<id>] <description>
      File: <path>:<line>
      Detail: <detail>
      Fix: <fix command or instruction>

P1 MUST FIX (resolve before merge):
  ✗ [<id>] <description>
      File: <path>
      Detail: <detail>
      Fix: <fix instruction>

P2 ADVISORY (review carefully):
  ⚠ [<id>] <description>
      File: <path>
      Note: <note>

P3 QUALITY (track and improve):
  ○ [<id>] <description>
      File: <path>
      Note: <note>

Summary: <X> P0 blockers, <Y> P1 issues, <Z> P2 advisories, <W> P3 notes
→ <"Not ready to merge." if P0 or P1 exist, else "Ready to merge (with advisory notes)." if P2+ exist, else "Ready to merge.">
```

---

### Step 4: Auto-fix offer

If P0 or P1 findings exist, ask:
```
Auto-fix mechanical P0/P1 issues? (yes / no / select)
  Mechanical fixes available: [list each auto-fixable finding by ID]
  Requires manual fix: [list each finding that needs human judgment]
```

- **`yes`**: Apply all mechanical fixes:
  - Re-run `python3 generator/generate.py --all` for [1a], [1c], [2a]
  - Run `python3 generator/validate.py` to confirm
  - Fix variable inconsistencies [2c] by updating the file
  - Add missing COMMANDS.md entries [2d]
  - Regenerate checksums for [2e]: `bash scripts/bump-version.sh <current-version> --checksums`
  - Add missing spec.json fields [2f]
  - Update index.json [2g]
  - Fix malformed checkboxes [4c]
  - After all mechanical fixes: re-run this review to confirm issues are resolved
- **`no`**: Report only — user handles manually
- **`select`**: Step through each fixable finding and ask "Fix this? (yes/no)"

Security-sensitive file issues [3a] and spec alignment issues [3b] are NEVER auto-fixed — always require human judgment.

For [1b] (detached HEAD in markdown files): display the exact line with the problematic pattern and the corrected version; ask for confirmation before editing.
