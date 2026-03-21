# Implementation Tasks: PR Review Noise Reduction

## Task Breakdown

### Task 1: Create .coderabbit.yml
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Create `.coderabbit.yml` at the repo root with path_filters to exclude all generated files from inline review, and path_instructions to provide architectural context for `core/*.md` and `generator/templates/*.j2`.

**Implementation Steps:**
1. Create `.coderabbit.yml` with reviews.path_filters excluding: `platforms/claude/SKILL.md`, `platforms/cursor/specops.mdc`, `platforms/codex/SKILL.md`, `platforms/copilot/specops.instructions.md`, `skills/specops/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `CHECKSUMS.sha256`
2. Add path_instructions for `core/*.md` explaining abstract tool operations
3. Add path_instructions for `generator/templates/*.j2` explaining Jinja2 syntax
4. Add path_instructions for `generator/validate.py` about marker sync requirement

**Acceptance Criteria:**
- [x] `.coderabbit.yml` exists at repo root
- [x] All 8 generated file paths excluded via path_filters
- [x] 3 path_instructions sections present with accurate context

**Files to Modify:**
- `.coderabbit.yml` (new)

**Tests Required:**
- [x] YAML syntax valid (python3 -c "import yaml; yaml.safe_load(open('.coderabbit.yml'))")

---

### Task 2: Add markdownlint config and CI job
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Create `.markdownlint.json` config file and add a `markdownlint` job to `.github/workflows/ci.yml` that lints source markdown files only.

**Implementation Steps:**
1. Create `.markdownlint.json` with MD040 and MD058 enabled, MD013/MD033/MD041 disabled
2. Add `markdownlint` job to `ci.yml` using `npx markdownlint-cli2` on source markdown files
3. Ensure generated files are NOT in the lint scope

**Acceptance Criteria:**
- [x] `.markdownlint.json` exists with correct rule configuration
- [x] CI job runs `npx markdownlint-cli2` on `core/**/*.md`, `docs/**/*.md`, `.claude/commands/**/*.md`, `README.md`, `CLAUDE.md`, `QUICKSTART.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- [x] Generated platform files are NOT linted

**Files to Modify:**
- `.markdownlint.json` (new)
- `.github/workflows/ci.yml`

**Tests Required:**
- [x] JSON syntax valid for `.markdownlint.json`
- [x] CI YAML syntax valid

---

### Task 3: Fix FILE_EXISTS tool mapping gap
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Add `FILE_EXISTS` to all 4 platform.json toolMapping entries and to validate.py's ABSTRACT_OPERATIONS list. Regenerate all platform outputs and verify no raw `FILE_EXISTS(` remains.

**Implementation Steps:**
1. Read all 4 `platforms/*/platform.json` files to understand existing toolMapping format
2. Add `"FILE_EXISTS"` mapping to each platform's toolMapping
3. Add `"FILE_EXISTS("` to ABSTRACT_OPERATIONS list in `generator/validate.py`
4. Run `python3 generator/generate.py --all` to regenerate
5. Run `python3 generator/validate.py` to verify no raw operations remain

**Acceptance Criteria:**
- [x] All 4 platform.json files contain FILE_EXISTS in toolMapping
- [x] validate.py ABSTRACT_OPERATIONS includes "FILE_EXISTS("
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes with no FILE_EXISTS violations
- [x] `bash scripts/run-tests.sh` passes

**Files to Modify:**
- `platforms/claude/platform.json`
- `platforms/cursor/platform.json`
- `platforms/codex/platform.json`
- `platforms/copilot/platform.json`
- `generator/validate.py`
- `platforms/claude/SKILL.md` (regenerated)
- `platforms/cursor/specops.mdc` (regenerated)
- `platforms/codex/SKILL.md` (regenerated)
- `platforms/copilot/specops.instructions.md` (regenerated)
- `skills/specops/SKILL.md` (regenerated)

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes

---

### Task 4: Add source-level abstract op validation
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3
**Priority:** High
**IssueID:** None
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Add `validate_source_syntax()` function to `generator/validate.py` that checks `core/*.md` files for malformed abstract operation usage and verifies all platform.json files have complete toolMapping coverage.

**Implementation Steps:**
1. Read `core/tool-abstraction.md` to extract the canonical list of abstract operations
2. Add `validate_source_syntax()` that:
   a. For each `core/*.md` (excluding `tool-abstraction.md`): scan for abstract op names followed by `(` and verify they have arguments
   b. For each `platforms/*/platform.json`: verify every abstract op has a toolMapping entry
3. Wire the function into the main validation flow
4. Run validation to verify it passes on current source

**Acceptance Criteria:**
- [x] `validate_source_syntax()` function exists in validate.py
- [x] Function detects bare abstract ops without proper call syntax in core/*.md
- [x] Function detects missing toolMapping entries in platform.json
- [x] Current source passes validation (no false positives on existing code)

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes on current source
- [x] `bash scripts/run-tests.sh` passes

---

### Task 5: Wire lint-specs.sh into pre-commit hook
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Add Check 6 to `hooks/pre-commit` that runs `scripts/lint-specs.sh` when `.specops/` files are staged.

**Implementation Steps:**
1. Add Check 6 after existing Check 5 (PII detection)
2. Filter staged files for `.specops/` paths
3. If any match and `scripts/lint-specs.sh` exists, run it
4. If it fails, increment ERRORS and show lint output
5. Run shellcheck on the modified hook

**Acceptance Criteria:**
- [x] Check 6 exists in hooks/pre-commit
- [x] Check only runs when `.specops/` files are staged
- [x] Check only runs when `scripts/lint-specs.sh` exists
- [x] `shellcheck hooks/pre-commit` passes

**Files to Modify:**
- `hooks/pre-commit`

**Tests Required:**
- [x] `shellcheck hooks/pre-commit` passes

---

### Task 6: Add step reference validation
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** Medium
**IssueID:** None
**Blocker:** None
**Domain:** backend
**Ship Blocking:** No

**Description:**
Add `validate_step_references()` function to `generator/validate.py` that detects dangling step references (e.g., "Step 5" when only 4 steps exist) in generated platform outputs.

**Implementation Steps:**
1. Add function that for each generated output:
   a. Finds all step references matching patterns like "Step N", "step N", "Step N.N"
   b. Counts actual step definitions (lines matching `### Step N` or similar)
   c. Reports any reference to a non-existent step
2. Wire into main validation flow
3. Verify it passes on current generated outputs

**Acceptance Criteria:**
- [x] `validate_step_references()` function exists in validate.py
- [x] Function detects references to non-existent steps
- [x] Current generated outputs pass validation

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes

---

### Task 7: Strengthen validation markers
**Status:** Pending
**Estimated Effort:** M
**Dependencies:** None
**Priority:** Medium
**IssueID:** None
**Blocker:** None
**Domain:** backend
**Ship Blocking:** No

**Description:**
Audit `*_MARKERS` lists in `generator/validate.py` for generic single-word markers. Replace with more specific multi-word or heading-prefixed strings. Keep `tests/test_platform_consistency.py` in sync.

**Implementation Steps:**
1. Read validate.py and identify all `*_MARKERS` constants
2. For each list, identify markers that are single-word or could match incidentally
3. Replace generic markers with more specific strings
4. Apply identical changes to `tests/test_platform_consistency.py`
5. Run validation and tests to confirm markers still match generated outputs

**Acceptance Criteria:**
- [ ] No single-word markers remain in `*_MARKERS` lists (unless they are inherently unique)
- [ ] `validate.py` and `test_platform_consistency.py` marker lists are identical
- [ ] `python3 generator/validate.py` passes
- [ ] `bash scripts/run-tests.sh` passes

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [ ] `python3 generator/validate.py` passes
- [ ] `python3 tests/test_platform_consistency.py` passes

---

### Task 8: Create /pre-pr command
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7
**Priority:** High
**IssueID:** None
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Create `.claude/commands/pre-pr.md` that chains `/core-review current`, automated validation, and `/docs-sync` into a single pre-PR quality gate with a summary dashboard.

**Implementation Steps:**
1. Create `.claude/commands/pre-pr.md` with 5-step workflow:
   - Step 1: Run `/core-review current`, auto-fix P0/P1
   - Step 2: Run validation battery (validate.py, lint-specs.sh, checksums, tests)
   - Step 3: Run `/docs-sync` if source files changed
   - Step 4: Display summary dashboard with pass/fail for each check
   - Step 5: Security advisory if sensitive files in diff
2. Define dashboard format with clear pass/fail indicators
3. Define verdict logic: all pass → "Ready for /ship-pr", any fail → "Fix issues first"

**Acceptance Criteria:**
- [x] `.claude/commands/pre-pr.md` exists
- [x] Command chains /core-review, validate.py, lint-specs.sh, checksums, tests, /docs-sync
- [x] Dashboard shows pass/fail for each check
- [x] Security advisory appears for security-sensitive files
- [x] Verdict clearly states readiness or blocking issues

**Files to Modify:**
- `.claude/commands/pre-pr.md` (new)

**Tests Required:**
- [x] Command file exists and is valid markdown

---

### Task 9: Update /ship-pr with /pre-pr tip
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 8
**Priority:** Low
**IssueID:** None
**Blocker:** None
**Domain:** devops
**Ship Blocking:** No

**Description:**
Add an informational tip to `.claude/commands/ship-pr.md` after Step 5 suggesting `/pre-pr` before shipping.

**Implementation Steps:**
1. Read `.claude/commands/ship-pr.md`
2. Add a tip after Step 5 (Review changes): "**Tip**: Run `/pre-pr` before `/ship-pr` to catch issues that bots would flag in review."
3. Ensure it does not block the workflow

**Acceptance Criteria:**
- [x] Tip text present in ship-pr.md after Step 5
- [x] Tip is informational only (does not block flow)

**Files to Modify:**
- `.claude/commands/ship-pr.md`

**Tests Required:**
- [x] File is valid markdown

---

## Implementation Order
1. Task 1 (bot config — independent)
2. Task 2 (markdownlint — independent)
3. Task 3 (FILE_EXISTS fix — foundation for Task 4)
4. Task 5 (pre-commit lint-specs — independent)
5. Task 4 (source syntax validation — depends on Task 3)
6. Task 6 (step reference validation — independent)
7. Task 7 (strengthen markers — independent)
8. Task 8 (/pre-pr command — depends on Tasks 3-7)
9. Task 9 (/ship-pr tip — depends on Task 8)

## Progress Tracking
- Total Tasks: 9
- Completed: 8
- In Progress: 0
- Blocked: 0
- Pending: 1 (Task 7 — deferred)
