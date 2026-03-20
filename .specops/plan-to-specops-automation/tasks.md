# Implementation Tasks: Plan Mode → SpecOps Workflow Automation

## Task Breakdown

### Task 1: Add planFileDirectory to platform config
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #70
**Blocker:** None

**Description:**
Add `planFileDirectory` field to Claude's `platform.json` to enable from-plan auto-discovery.

**Implementation Steps:**
1. Add `"planFileDirectory": "~/.claude/plans"` after the `capabilities` block

**Acceptance Criteria:**
- [x] `planFileDirectory` field present in `platforms/claude/platform.json`
- [x] Other platform configs unchanged

**Files to Modify:**
- `platforms/claude/platform.json`

**Tests Required:**
- [x] JSON is valid after edit

---

### Task 2: Enhance core/from-plan.md with file path input and auto-discovery
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #71
**Blocker:** None

**Description:**
Add new detection patterns and restructure step 1 to support 4 input branches: inline content, file path, auto-discovery, and interactive paste.

**Implementation Steps:**
1. Add new detection patterns to the Detection section: "implement the plan", "implement my plan", "go ahead with the plan", "proceed with plan"
2. Restructure Workflow step 1 into 4 branches:
   - Branch A (existing): inline content
   - Branch B (new): file path validation + READ_FILE
   - Branch C (new): platform `planFileDirectory` auto-discovery
   - Branch D (existing): ASK_USER fallback
3. Add path validation rules (no `../`, must be `.md`, FILE_EXISTS check)
4. Add auto-discovery logic using LIST_DIR + RUN_COMMAND for recency sorting

**Acceptance Criteria:**
- [x] Detection section includes new trigger patterns
- [x] Step 1 has 4 input branches in priority order
- [x] Path validation rejects `../` and non-`.md` files
- [x] Auto-discovery uses platform `planFileDirectory` config
- [x] Non-interactive platforms get NOTIFY_USER fallback
- [x] All abstract operations used (no platform-specific tool names)

**Files to Modify:**
- `core/from-plan.md`

**Tests Required:**
- [x] Validator passes (from-plan markers present in generated output)

---

### Task 3: Add post-plan-acceptance gate to core/workflow.md
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #72
**Blocker:** None

**Description:**
Add step 10.5 to Getting Started in `core/workflow.md` that detects post-plan acceptance and enforces routing through From Plan Mode.

**Implementation Steps:**
1. Add step 10.5 between step 10 (from-plan check) and step 11 (interview check)
2. Define three-condition AND gate: acceptance phrase + plan context + .specops.json
3. Add protocol breach language for ad-hoc implementation

**Acceptance Criteria:**
- [x] Step 10.5 present in Getting Started section
- [x] Three-condition AND gate defined
- [x] Protocol breach language included
- [x] Abstract operations used (FILE_EXISTS for .specops.json check)

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Validator passes (workflow markers present)

---

### Task 4: Add SpecOps handoff to resume-plan.md
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #73
**Blocker:** None

**Description:**
Add Step 8 to `.claude/commands/resume-plan.md` that checks for SpecOps config and invokes from-plan after plan presentation.

**Implementation Steps:**
1. Add Step 8 after Step 7 (Present the plan)
2. Check FILE_EXISTS `.specops.json`
3. If exists: notify user and invoke `/specops from-plan` with PLAN_CONTENT
4. If not: report "No SpecOps configuration found" and proceed

**Acceptance Criteria:**
- [x] Step 8 present in resume-plan.md
- [x] SpecOps detection via .specops.json check
- [x] Graceful fallback when SpecOps not configured
- [x] Plan content passed to from-plan invocation

**Files to Modify:**
- `.claude/commands/resume-plan.md`

**Tests Required:**
- [x] Command file is valid markdown

---

### Task 5: Check and update generator/validate.py markers
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 2, Task 3
**Priority:** Medium
**IssueID:** #74
**Blocker:** None

**Description:**
Verify that `FROM_PLAN_MARKERS` in `generator/validate.py` covers the new plan-file-aware content. Add new markers if needed.

**Implementation Steps:**
1. Read current FROM_PLAN_MARKERS in validate.py
2. Determine if new markers are needed for plan file path or auto-discovery content
3. Add markers if the new from-plan content introduces new validation-worthy strings

**Acceptance Criteria:**
- [x] FROM_PLAN_MARKERS reviewed for coverage
- [x] New markers added if needed (added "auto-discovery" and "planFileDirectory")
- [x] validate.py still runs successfully

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes

---

### Task 6: Regenerate all platform outputs
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3
**Priority:** High
**IssueID:** #75
**Blocker:** None

**Description:**
Run the generator to propagate core changes to all 4 platform outputs.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Verify no errors in output

**Acceptance Criteria:**
- [x] Generator completes without errors
- [x] All 4 platform outputs regenerated

**Files to Modify:**
- `platforms/claude/SKILL.md`
- `platforms/cursor/specops.mdc`
- `platforms/codex/SKILL.md`
- `platforms/copilot/specops.instructions.md`
- `skills/specops/SKILL.md`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

**Tests Required:**
- [x] Generator exits with code 0

---

### Task 7: Run validation
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 5, Task 6
**Priority:** High
**IssueID:** #76
**Blocker:** None

**Description:**
Run the validator to ensure all generated outputs contain required markers.

**Implementation Steps:**
1. Run `python3 generator/validate.py`
2. Fix any validation failures

**Acceptance Criteria:**
- [x] `python3 generator/validate.py` passes with no errors

**Files to Modify:**
- None (validation only; may need fixes if validation fails)

**Tests Required:**
- [x] Validator exits with code 0

---

### Task 8: Run full test suite
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 6, Task 7
**Priority:** High
**IssueID:** #77
**Blocker:** None

**Description:**
Run the complete test suite to verify nothing is broken.

**Implementation Steps:**
1. Run `bash scripts/run-tests.sh`
2. Fix any test failures

**Acceptance Criteria:**
- [x] All tests pass

**Files to Modify:**
- None (test run only; may need fixes if tests fail)

**Tests Required:**
- [x] `bash scripts/run-tests.sh` exits with code 0

## Implementation Order
1. Task 1 (platform config — foundation)
2. Task 2, Task 3, Task 4 (parallel — core module, workflow gate, command bridge)
3. Task 5 (validate.py markers — depends on Task 2, 3)
4. Task 6 (regenerate — depends on Task 1, 2, 3)
5. Task 7 (validation — depends on Task 5, 6)
6. Task 8 (full tests — depends on Task 6, 7)

## Progress Tracking
- Total Tasks: 8
- Completed: 8
- In Progress: 0
- Blocked: 0
- Pending: 0
