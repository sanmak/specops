# Implementation Tasks: Workflow Enforcement Gates

## Task Breakdown

### Task 1: Edit core/workflow.md — Phase 1 Pre-flight Gate
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None

**Description:**
Restructure Phase 1 step 5 to use enforcement gate pattern with protocol breach language, content-level steering check, and STOP consequence.

**Implementation Steps:**
1. Replace step 5 heading with "Pre-flight check (enforcement gate)"
2. Add "protocol breach" to the opening sentence
3. Split enforcement checks into separate bullets (steering dir, steering content, memory dir)
4. Add LIST_DIR content check for at least one .md file
5. Add STOP consequence bullet after corrective actions
6. Keep .gitignore check as visually separated sub-section

**Acceptance Criteria:**
- [x] "protocol breach" appears in Phase 1 step 5
- [x] LIST_DIR content check added for steering directory
- [x] STOP consequence added
- [x] .gitignore check visually separated below enforcement bullets

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Regenerated outputs pass validation

---

### Task 2: Edit core/workflow.md — Phase 4 Memory Write Enforcement
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None

**Description:**
Add "(mandatory)" to Phase 4 step 3 heading and add "protocol breach" language with forward reference to completion gate.

**Implementation Steps:**
1. Change step 3 heading from "Update memory" to "Update memory (mandatory)"
2. Append enforcement sentence after existing text

**Acceptance Criteria:**
- [x] Step 3 heading includes "(mandatory)"
- [x] "protocol breach" appears in step 3
- [x] Forward reference to step 5 verification included

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Regenerated outputs pass validation

---

### Task 3: Edit core/workflow.md — Phase 3 Implementation Gates Restructure
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None

**Description:**
Break Phase 3 step 1 from a single paragraph into a structured sub-list with named gates (Review gate, Task tracking gate) and a separate status update bullet.

**Implementation Steps:**
1. Replace the single paragraph with "Implementation gates" heading
2. Create Review gate sub-bullet (existing review gate text, condensed)
3. Create Task tracking gate sub-bullet with cross-reference to config-handling.md and protocol breach language
4. Create "After both gates pass" sub-bullet for status update logic

**Acceptance Criteria:**
- [x] Phase 3 step 1 uses sub-list structure
- [x] Review gate and Task tracking gate are separate named bullets
- [x] "protocol breach" appears in task tracking gate bullet
- [x] Status update logic is in its own bullet after gates

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Regenerated outputs pass validation

---

### Task 4: Edit core/config-handling.md — Task Tracking Gate Rewrite
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** None
**Blocker:** None

**Description:**
Remove "advisory, not blocking" language and replace with protocol breach enforcement. Add specific partial/total failure scenarios and enforcement principle anchor.

**Implementation Steps:**
1. Add "protocol breach" to the gate introduction paragraph
2. Rewrite steps 4-5 with specific scenarios (partial success, total failure)
3. Add step 6 as enforcement principle: "The gate enforces attempted creation, not 100% success"
4. Remove old step 5 ("Do NOT block implementation — the gate is advisory, not blocking")

**Acceptance Criteria:**
- [x] "advisory, not blocking" removed
- [x] "protocol breach" added to gate introduction
- [x] Partial and total failure scenarios specified separately
- [x] "attempted creation" enforcement principle documented

**Files to Modify:**
- `core/config-handling.md`

**Tests Required:**
- [x] Regenerated outputs pass validation

---

### Task 5: Update validation markers
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 4
**Priority:** High
**IssueID:** None
**Blocker:** None

**Description:**
Add "attempted creation" marker to both generator/validate.py and tests/test_platform_consistency.py to verify the new enforcement language propagates to all platform outputs.

**Implementation Steps:**
1. Add `"attempted creation"` to `EXTERNAL_TRACKING_MARKERS` in validate.py
2. Add `"attempted creation"` to `REQUIRED_MARKERS["external_tracking"]` in test_platform_consistency.py

**Acceptance Criteria:**
- [x] Marker present in generator/validate.py EXTERNAL_TRACKING_MARKERS
- [x] Marker present in tests/test_platform_consistency.py REQUIRED_MARKERS

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] python3 generator/validate.py passes
- [x] python3 tests/test_platform_consistency.py passes

---

### Task 6: Regenerate platform outputs and run all tests
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5
**Priority:** High
**IssueID:** None
**Blocker:** None

**Description:**
Regenerate all platform outputs from updated core files, run full validation and test suite, spot-check enforcement language in generated outputs.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Spot-check: grep "protocol breach" in SKILL.md (>= 5 occurrences)
5. Spot-check: grep "advisory, not blocking" returns nothing
6. Spot-check: grep "attempted creation" is present

**Acceptance Criteria:**
- [x] All platform outputs regenerated without errors
- [x] Validation passes (all markers present)
- [x] All tests pass
- [x] "protocol breach" count >= 5 in platforms/claude/SKILL.md
- [x] "advisory, not blocking" absent from all generated outputs
- [x] "attempted creation" present in all generated outputs

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/` manifests (generated)

**Tests Required:**
- [x] Full test suite passes

---

## Implementation Order
1. Tasks 1-4 (parallel — independent core file edits)
2. Task 5 (depends on Task 4 — marker text must exist in config-handling.md)
3. Task 6 (depends on all — regeneration and validation)

## Progress Tracking
- Total Tasks: 6
- Completed: 6
- In Progress: 0
- Blocked: 0
- Pending: 0
