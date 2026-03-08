# Implementation Tasks: Bugfix Regression Risk Analysis

## Task Breakdown

### Task 1: Add Regression Risk Analysis section to bugfix template
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Insert the Regression Risk Analysis section into `core/templates/bugfix.md` between Reproduction Steps and Proposed Fix. Add five subsections (Blast Radius, Behavior Inventory, Test Coverage Assessment, Risk Tier, Scope Escalation Check) with severity-scaling guidance in HTML comments. Update the Unchanged Behavior section comment to reference the analysis. Update the Testing Plan Unchanged Behavior comment to reference Must-Test items. Remove the HTML comment at bottom of Testing Plan (replaced by Scope Escalation Check). Add two new acceptance criteria checkboxes.

**Implementation Steps:**
1. Insert Regression Risk Analysis section after line 26 (end of Reproduction Steps)
2. Add severity-scaling HTML comment at top of section
3. Add five subsections with placeholder content and HTML guidance comments
4. Update Unchanged Behavior section HTML comment to reference analysis
5. Update Testing Plan Unchanged Behavior comment to reference Risk Tier
6. Remove HTML comment at bottom of Testing Plan about Feature Spec creation
7. Add two new acceptance criteria checkboxes

**Acceptance Criteria:**
- [x] Regression Risk Analysis section exists between Reproduction Steps and Proposed Fix
- [x] Five subsections present: Blast Radius, Behavior Inventory, Test Coverage Assessment, Risk Tier, Scope Escalation Check
- [x] Severity scaling documented in HTML comment
- [x] Unchanged Behavior comment references the analysis
- [x] Old Feature Spec HTML comment removed from Testing Plan
- [x] Two new acceptance criteria checkboxes added

**Files to Modify:**
- `core/templates/bugfix.md`

**Tests Required:**
- [x] Template renders correctly with all sections
- [x] Existing template markers still present (Bug Fix: [Title])

---

### Task 2: Enhance Phase 2 bugfix workflow guidance
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Replace the single-paragraph bugfix guidance in `core/workflow.md` (line 53) with a severity-tiered discovery procedure. The procedure must use abstract operations (LIST_DIR, READ_FILE, RUN_COMMAND) and provide concrete steps for Critical/High, Medium, and Low severity bugs. Include instruction to complete analysis BEFORE writing Proposed Fix.

**Implementation Steps:**
1. Locate the existing bugfix guidance paragraph in Phase 2 (line 53)
2. Replace with structured severity-tiered procedure
3. Use abstract operations throughout
4. Include explicit instruction ordering (analysis before fix)

**Acceptance Criteria:**
- [x] Phase 2 contains severity-tiered bugfix guidance (Critical/High, Medium, Low)
- [x] Abstract operations used (LIST_DIR, READ_FILE, RUN_COMMAND)
- [x] Guidance explicitly states analysis before Proposed Fix
- [x] Scope escalation criteria included

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] No platform-specific tool names in workflow.md
- [x] Abstract operations match those in core/tool-abstraction.md

---

### Task 3: Add regression validation markers
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**Domain:** generator
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add REGRESSION_MARKERS list to `generator/validate.py`. Add check call in `validate_platform()`. Add markers to the cross-platform consistency loop.

**Implementation Steps:**
1. Define REGRESSION_MARKERS list after TASK_TRACKING_MARKERS
2. Add `check_markers_present` call in `validate_platform()`
3. Add REGRESSION_MARKERS to the cross-platform consistency loop

**Acceptance Criteria:**
- [x] REGRESSION_MARKERS list defined with section headings
- [x] validate_platform() checks regression markers
- [x] Cross-platform consistency loop includes regression markers

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [x] validate.py runs without errors
- [x] All platform outputs pass regression marker check after regeneration

---

### Task 4: Regenerate platform outputs and validate
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3
**Priority:** High
**Domain:** devops
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Regenerate all platform outputs, run the validator, and run the full test suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`

**Acceptance Criteria:**
- [x] All platform outputs regenerated
- [x] Validator passes (including new regression markers)
- [x] All tests pass

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/` manifests (generated)

**Tests Required:**
- [x] python3 generator/validate.py passes
- [x] bash scripts/run-tests.sh passes

---

## Implementation Order
1. Task 1, Task 2 (parallel — independent core file changes)
2. Task 3 (depends on Task 1 — markers must match template content)
3. Task 4 (depends on all above — regenerate and validate)

## Progress Tracking
- Total Tasks: 4
- Completed: 4
- In Progress: 0
- Blocked: 0
- Pending: 0
