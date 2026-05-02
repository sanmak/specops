# Tasks: Environment Pre-flight Checks

## Task 1: Add environment pre-flight step to Phase 3 in core/workflow.md

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #249
**Dependencies:** None

**Description:** Add step 1.5 "Environment pre-flight" to Phase 3 in `core/workflow.md`. This step runs after all existing implementation gates but before the status update to `implementing`. It includes three checks: test command detection, dependency installation verification, and git branch state check.

**Implementation Steps:**
1. Read `core/workflow.md` to locate Phase 3 step 1 (Implementation gates)
2. Insert step 1.5 after the existing gates (dependency, review, task tracking, dependency introduction) but before the "After all gates pass" status update
3. Implement test command detection algorithm (5 project types)
4. Implement dependency installation check (directory existence)
5. Implement git branch state check (conflict detection)
6. Add pre-flight summary display
7. Use abstract operations only

**Acceptance Criteria:**
- [x] Step 1.5 exists in Phase 3 between gates and status update
- [x] Test command detection covers package.json, pyproject.toml, Makefile, Cargo.toml, go.mod
- [x] Dependency directory check matches project type
- [x] Git conflict detection blocks implementation (STOP)
- [x] Non-conflict dirty state warns but continues
- [x] Pre-flight summary displayed
- [x] All instructions use abstract operations

**Files to Modify:**
- `core/workflow.md`

## Task 2: Add pre-flight validation markers and regenerate

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #250
**Dependencies:** Task 1

**Description:** Add PREFLIGHT_MARKERS to `generator/validate.py` for validation of generated outputs. Add markers to both the per-platform validation function and the cross-platform consistency loop (Gap 31 enforcement). Import in `tests/test_platform_consistency.py`. Regenerate all platform outputs and verify.

**Implementation Steps:**
1. Define PREFLIGHT_MARKERS constant in validate.py with key heading/phrase markers
2. Add marker check to `validate_platform()` function
3. Add marker to cross-platform consistency check loop
4. Import and check in `tests/test_platform_consistency.py`
5. Run `python3 generator/generate.py --all` to regenerate
6. Run `python3 generator/validate.py` to verify
7. Run `bash scripts/run-tests.sh` to run full test suite

**Acceptance Criteria:**
- [x] PREFLIGHT_MARKERS constant defined in validate.py
- [x] Markers checked in validate_platform()
- [x] Markers checked in cross-platform consistency loop
- [x] test_platform_consistency.py imports and verifies markers
- [x] All platform outputs regenerated
- [x] Validator passes all checks
- [x] All tests pass

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`
- All generated platform outputs (via generate.py)
