# Implementation Tasks: Project-Type-Aware Workflow

## Task Breakdown

### Task 1: Migration Vertical
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — issues not created during implementation
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Add the `migration` vertical to SpecOps following the established vertical pattern.

**Implementation Steps:**
1. Add `### migration` section to `core/verticals.md` after `### builder` with domain vocabulary, requirements.md/design.md/tasks.md adaptations
2. Add migration vocabulary verification entry to the verification table in `core/verticals.md`
3. Add migration keywords to `core/workflow.md` step 7 vertical detection list
4. Add `"migration"` to the vertical enum in `schema.json`
5. Add `"### migration"` to `VERTICAL_MARKERS` in `generator/validate.py`
6. Add `"### migration"` to verticals markers in `tests/test_platform_consistency.py`

**Acceptance Criteria:**
- [x] `### migration` section present in core/verticals.md with domain vocabulary, req/design/task adaptations
- [x] Migration vocabulary verification entry in the table
- [x] Migration keywords in workflow.md step 7
- [x] "migration" in schema.json vertical enum
- [x] "### migration" in validate.py VERTICAL_MARKERS
- [x] "### migration" in test_platform_consistency.py verticals markers

**Files to Modify:**
- `core/verticals.md`
- `core/workflow.md`
- `schema.json`
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/check_schema_sync.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 2: Auto-Init Suggestion
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — issues not created during implementation
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Add auto-init suggestion to Phase 1 step 1 in `core/workflow.md` when `.specops.json` is missing.

**Implementation Steps:**
1. Modify step 1 in `core/workflow.md` to add a conditional: if `.specops.json` does not exist, ASK_USER offering init or defaults
2. Document both paths: init redirect and continue with defaults

**Acceptance Criteria:**
- [x] Step 1 includes conditional check for missing `.specops.json`
- [x] ASK_USER prompt offers init or defaults
- [x] Init redirect path documented
- [x] Defaults continuation path documented

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] `python3 generator/validate.py` passes (existing WORKFLOW_MARKERS still present)

---

### Task 3: Project Type Detection in Init
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — issues not created during implementation
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Add Step 1.5 to `core/init.md` that auto-detects project type (greenfield/brownfield) and presents to user with migration override.

**Implementation Steps:**
1. Insert Step 1.5 after Step 1 in `core/init.md`
2. Document repo scanning logic (LIST_DIR, FILE_EXISTS checks, file counting)
3. Document classification rules (≤ 5 = greenfield, > 5 = brownfield, migration = user override)
4. Document ASK_USER with 3 options (Greenfield, Brownfield, Migration)
5. Document template pre-selection for each type
6. Add non-interactive platform fallback (detect and proceed without asking)

**Acceptance Criteria:**
- [x] Step 1.5 present in init.md between Step 1 and Step 2
- [x] Repo scanning logic documented with exclusion list
- [x] Classification rules clear (greenfield vs brownfield threshold)
- [x] User confirmation with 3 options (Greenfield, Brownfield, Migration)
- [x] Template pre-selection for each project type
- [x] Non-interactive platform fallback

**Files to Modify:**
- `core/init.md`

**Tests Required:**
- [x] `python3 generator/validate.py` passes

---

### Task 4: Brownfield Assisted Steering Population
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3
**Priority:** High
**IssueID:** FAILED — issues not created during implementation
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Add Step 4.7 to `core/init.md` that auto-populates steering files from existing project documentation when the project type is brownfield.

**Implementation Steps:**
1. Insert Step 4.7 after Step 4.6 in `core/init.md`
2. Document product.md population from README.md (overview, features, description sections)
3. Document tech.md population from dependency manifests (package.json, pyproject.toml, etc.)
4. Document structure.md population from top-level directory listing
5. Document placeholder detection (bracket-enclosed placeholders)
6. Document notification to user about pre-populated files

**Acceptance Criteria:**
- [x] Step 4.7 present in init.md after Step 4.6
- [x] product.md population from README.md documented
- [x] tech.md population from dependency manifests documented (priority order)
- [x] structure.md population from directory listing documented
- [x] Placeholder detection logic documented
- [x] User notification after population

**Files to Modify:**
- `core/init.md`

**Tests Required:**
- [x] `python3 generator/validate.py` passes

---

### Task 5: Greenfield Adaptive Phase 1
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — issues not created during implementation
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Add step 7.5 to `core/workflow.md` for greenfield detection, with alternative steps 8g/9g replacing hollow codebase exploration. Update `core/templates/implementation.md` with project state line.

**Implementation Steps:**
1. Insert step 7.5 in `core/workflow.md` after step 7 (vertical detection)
2. Document greenfield detection logic (LIST_DIR, file count ≤ 5)
3. Document step 8g (propose initial project structure)
4. Document step 9g (auto-populate steering files from conversation context)
5. Add conditional labels to steps 8-9: "(Brownfield/migration only)"
6. Add `- Project state: [greenfield / brownfield / migration]` to `core/templates/implementation.md`

**Acceptance Criteria:**
- [x] Step 7.5 present in workflow.md between step 7 and step 8
- [x] Greenfield detection heuristic documented (≤ 5 source files)
- [x] Steps 8g and 9g fully documented
- [x] Steps 8-9 labeled as brownfield/migration only
- [x] Project state line added to implementation.md template

**Files to Modify:**
- `core/workflow.md`
- `core/templates/implementation.md`

**Tests Required:**
- [x] `python3 generator/validate.py` passes

---

### Task 6: Regenerate and Validate
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5
**Priority:** High
**IssueID:** FAILED — issues not created during implementation
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Regenerate all platform outputs and run full validation suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Verify `### migration` appears in all 4 platform outputs
5. Verify greenfield and assisted steering text appears in generated outputs
6. Verify auto-init suggestion text appears in generated outputs

**Acceptance Criteria:**
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` reports 0 errors
- [x] `bash scripts/run-tests.sh` reports all tests pass (7/7 pass, lint fail is checkbox staleness — fixed)
- [x] `### migration` present in all 4 platform output files
- [x] Greenfield detection text in generated outputs
- [x] Assisted steering text in generated outputs

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/` (generated)

**Tests Required:**
- [x] `python3 generator/validate.py` — 0 errors
- [x] `bash scripts/run-tests.sh` — all tests pass
- [x] `python3 tests/check_schema_sync.py` — schema well-formed

---

## Implementation Order
1. Task 1 (migration vertical — validates pipeline)
2. Task 2 (auto-init suggestion — independent)
3. Task 3 (project type detection — independent)
4. Task 4 (brownfield assisted steering — depends on Task 3)
5. Task 5 (greenfield adaptive Phase 1 — independent)
6. Task 6 (regenerate and validate — depends on all)

## Progress Tracking
- Total Tasks: 6
- Completed: 6
- In Progress: 0
- Blocked: 0
- Pending: 0
