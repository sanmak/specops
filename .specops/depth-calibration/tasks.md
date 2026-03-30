# Tasks: Depth Calibration System

## Task 1: Add depth assessment to Phase 1 in core/workflow.md

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #238
**Dependencies:** None

**Description:** Add step 9.7 "Depth assessment" to Phase 1 in `core/workflow.md`. The step computes the depth flag from three signals (task count, domain breadth, new dependency presence) and records it in the implementation.md Phase 1 Context Summary. Also add user override detection to step 6 (request analysis).

**Implementation Steps:**
1. Add step 9.7 between existing steps 9.5 and Phase 2, implementing the depth assessment algorithm from design.md
2. Add user override detection keywords to step 6 analysis
3. Use abstract operations only (no platform-specific tool names)
4. Record depth flag as `- Depth: <flag> [computed | user override]` in Context Summary template

**Acceptance Criteria:**
- [x] Step 9.7 exists in Phase 1 with the depth assessment algorithm
- [x] User override detection is integrated into step 6
- [x] All instructions use abstract operations

**Files to Modify:**
- `core/workflow.md`

## Task 2: Add conditional step behavior to core/workflow.md

**Status:** Completed
**Priority:** High
**Effort:** Large
**IssueID:** #239
**Dependencies:** Task 1

**Description:** Modify five workflow steps to check the depth flag and adjust behavior: repo map refresh (step 3.5), scope assessment (step 9.5), spec evaluation (step 6.85), implementation evaluation (Phase 4A), and dependency introduction gate (step 5.8).

**Implementation Steps:**
1. Modify step 3.5 (repo map): add "If depth is `lightweight`, skip refresh and use existing map if available."
2. Modify step 9.5 (scope assessment): add "If depth is `lightweight`, this gate passes trivially (skip complexity signal evaluation)."
3. Modify step 6.85 (spec evaluation): add "If depth is `lightweight`, skip spec evaluation. If depth is `standard`, limit to 1 iteration. If depth is `deep`, run up to maxIterations."
4. Modify Phase 4A (implementation evaluation): add "If depth is `lightweight`, skip full evaluation and proceed directly to Phase 4C acceptance criteria verification."
5. Modify step 5.8 (dependency gate): add "If depth is `lightweight` and no new dependencies detected in design.md, skip gate."

**Acceptance Criteria:**
- [x] Repo map step conditionally skips on lightweight
- [x] Scope assessment conditionally passes on lightweight
- [x] Spec evaluation conditionally skips/limits by depth
- [x] Implementation evaluation conditionally compresses on lightweight
- [x] Dependency gate conditionally skips on lightweight when no new deps
- [x] Standard depth behavior is unchanged from current workflow

**Files to Modify:**
- `core/workflow.md`

## Task 3: Add depth flag to dispatcher Shared Context Block

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #240
**Dependencies:** Task 1

**Description:** Update `core/dispatcher.md` to include the depth flag in the Shared Context Block passed to dispatched modes. The dispatcher does not compute the depth -- it passes through the value set during Phase 1 in the spec mode.

**Implementation Steps:**
1. Find the Shared Context Block section in `core/dispatcher.md`
2. Add depth flag to the context data passed to dispatched modes
3. Document that depth is computed by the spec mode during Phase 1

**Acceptance Criteria:**
- [x] Depth flag appears in the Shared Context Block
- [x] Dispatcher documentation notes depth is computed by spec mode

**Files to Modify:**
- `core/dispatcher.md`

## Task 4: Add depth field to spec-schema.json

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #241
**Dependencies:** None

**Description:** Add the `depth` field to `spec-schema.json` as a string enum property. This records the per-spec depth flag for traceability and audit.

**Implementation Steps:**
1. Read `spec-schema.json` to understand existing structure
2. Add `depth` property with type string, enum ["lightweight", "standard", "deep"]
3. Ensure additionalProperties: false compatibility

**Acceptance Criteria:**
- [x] `depth` field exists in spec-schema.json
- [x] Field is a string enum with three valid values
- [x] Schema validates correctly

**Files to Modify:**
- `spec-schema.json`

## Task 5: Add depth documentation to config-handling module

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #242
**Dependencies:** Task 1

**Description:** Update `core/config-handling.md` to document the depth field in the spec.json structure section, and add the depth flag to the Context Summary template in `core/templates/implementation.md`.

**Implementation Steps:**
1. Add `depth` to the spec.json field documentation in config-handling.md
2. Add `- Depth:` line to the Phase 1 Context Summary template in `core/templates/implementation.md`

**Acceptance Criteria:**
- [x] Depth field documented in spec.json structure
- [x] Context Summary template includes depth line

**Files to Modify:**
- `core/config-handling.md`
- `core/templates/implementation.md`

## Task 6: Add depth validation markers and regenerate

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #243
**Dependencies:** Tasks 1-5

**Description:** Add DEPTH_MARKERS to `generator/validate.py` for validation of generated outputs. Add markers to both the per-platform validation function and the cross-platform consistency loop (Gap 31 enforcement). Import in `tests/test_platform_consistency.py`. Regenerate all platform outputs and verify.

**Implementation Steps:**
1. Define DEPTH_MARKERS constant in validate.py with key heading/phrase markers
2. Add marker check to `validate_platform()` function
3. Add marker to cross-platform consistency check loop
4. Import and check in `tests/test_platform_consistency.py`
5. Run `python3 generator/generate.py --all` to regenerate
6. Run `python3 generator/validate.py` to verify
7. Run `bash scripts/run-tests.sh` to run full test suite

**Acceptance Criteria:**
- [x] DEPTH_MARKERS constant defined in validate.py
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
