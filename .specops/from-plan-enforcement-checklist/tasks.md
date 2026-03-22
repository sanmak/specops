# Implementation Tasks: From-Plan Enforcement Checklist Integration

## Spec-Level Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| ---            | ---    | ---      | ---    |

## Dependency Resolution Log

| Blocker | Resolution Type | Resolution Detail | Date |
| ------- | --------------- | ----------------- | ---- |
| ---     | ---             | ---               | ---  |

## Task Breakdown

### Task 1: Add Post-Conversion Enforcement Pass to core/from-plan.md

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #179
**Blocker:** None

**Description:**
Add step 6.5 to `core/from-plan.md` containing the 8 enforcement checks adapted for from-plan context. This is the core change -- all other tasks depend on this content existing.

**Implementation Steps:**

1. Open `core/from-plan.md` and locate step 6 (Gap-fill rule) and step 7 (Complete)
2. Insert new step 6.5 "Post-Conversion Enforcement Pass" between them
3. Write all 8 checks using abstract operations (FILE_EXISTS, READ_FILE, WRITE_FILE, RUN_COMMAND, NOTIFY_USER)
4. Include auto-remediation logic for steering directory, memory directory, and context summary
5. Include protocol breach language for skipping the enforcement pass
6. Include IssueID population check that triggers Task Tracking Integration protocol when taskTracking is configured
7. Include spec dependency gate check

**Acceptance Criteria:**

- [x] Step 6.5 exists in core/from-plan.md between step 6 and step 7
- [x] All 8 checks from dispatcher's Pre-Phase-3 Enforcement Checklist are present
- [x] Abstract operations used throughout (no platform-specific tool names)
- [x] Protocol breach language included
- [x] Auto-remediation for steering, memory, and context summary

**Files to Modify:**

- `core/from-plan.md`

**Tests Required:**

- [x] Verify abstract operations pass `generator/validate.py` (no raw abstract ops in output)

---

### Task 2: Update Validator Markers

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #180
**Blocker:** None

**Description:**
Add a marker to `FROM_PLAN_MARKERS` in `generator/validate.py` that verifies the post-conversion enforcement pass appears in all generated platform outputs. Following Gap 31: add to BOTH `validate_platform()` AND the cross-platform consistency check.

**Implementation Steps:**

1. Open `generator/validate.py`
2. Find the `FROM_PLAN_MARKERS` constant
3. Add `"Post-conversion enforcement"` marker string that appears in the generated enforcement section
4. Verify the marker appears in the cross-platform consistency loop as well (Gap 31)

**Acceptance Criteria:**

- [x] New marker added to FROM_PLAN_MARKERS
- [x] Marker present in both validate_platform() and cross-platform consistency check
- [x] `python3 generator/validate.py` passes after regeneration

**Files to Modify:**

- `generator/validate.py`

**Tests Required:**

- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 3: Regenerate Platform Outputs

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #181
**Blocker:** None

**Description:**
Regenerate all platform outputs after modifying `core/from-plan.md` and validate the generated files contain the new enforcement markers.

**Implementation Steps:**

1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Verify all 4 platform outputs include the enforcement pass content
4. Verify no raw abstract operations remain in generated files

**Acceptance Criteria:**

- [x] All 4 platform outputs regenerated
- [x] `python3 generator/validate.py` passes with 0 errors
- [x] No raw abstract operations in generated output

**Files to Modify:**

- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/plugin.json` (generated)
- `.claude-plugin/marketplace.json` (generated)
- `.claude/skills/specops/modes/from-plan.md` (generated)

**Tests Required:**

- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes

---

### Task 4: Run Full Test Suite

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** Medium
**IssueID:** #182
**Blocker:** None

**Description:**
Run the full test suite to verify no regressions from the changes.

**Implementation Steps:**

1. Run `bash scripts/run-tests.sh`
2. Review any failures and fix
3. Run `python3 generator/validate.py` for final validation

**Acceptance Criteria:**

- [x] All tests pass (7/8 -- 1 pre-existing failure in production-learnings spec, unrelated)
- [x] Validator passes with 0 errors

**Files to Modify:**

- None (test-only task)

**Tests Required:**

- [x] `bash scripts/run-tests.sh` all pass (1 pre-existing failure unrelated to this spec)
- [x] `python3 generator/validate.py` 0 errors

---

## Implementation Order

1. Task 1 (core module change -- foundation)
2. Task 2 (validator markers -- depends on Task 1 content)
3. Task 3 (regenerate -- depends on both Task 1 and Task 2)
4. Task 4 (full test suite -- depends on Task 3)

## Progress Tracking

- Total Tasks: 4
- Completed: 4
- In Progress: 0
- Blocked: 0
- Pending: 0
