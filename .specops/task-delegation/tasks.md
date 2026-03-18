# Implementation Tasks: Task Delegation for Phase 3

## Task Breakdown

### Task 1: Add canDelegateTask capability flag
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**Blocker:** None
**Domain:** backend

**Description:**
Add the `canDelegateTask` capability flag to the tool abstraction layer and all 4 platform.json files.

**Implementation Steps:**
1. Add `canDelegateTask` row to the capability flags table in `core/tool-abstraction.md`
2. Add capability-based behavior adaptation entry for `canDelegateTask = false`
3. Add `"canDelegateTask": true` to `platforms/claude/platform.json` capabilities
4. Add `"canDelegateTask": false` to `platforms/cursor/platform.json` capabilities
5. Add `"canDelegateTask": false` to `platforms/codex/platform.json` capabilities
6. Add `"canDelegateTask": false` to `platforms/copilot/platform.json` capabilities

**Acceptance Criteria:**
- [x] `canDelegateTask` appears in core/tool-abstraction.md capability flags table
- [x] Behavior adaptation for `canDelegateTask = false` documented
- [x] All 4 platform.json files include the new capability

**Files to Modify:**
- `core/tool-abstraction.md`
- `platforms/claude/platform.json`
- `platforms/cursor/platform.json`
- `platforms/codex/platform.json`
- `platforms/copilot/platform.json`

**Tests Required:**
- [ ] Platform consistency test passes (all platforms have same capability keys)

---

### Task 2: Add taskDelegation config option to schema
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**Blocker:** None
**Domain:** backend

**Description:**
Add `taskDelegation` property under `implementation` in schema.json and update the full example config.

**Implementation Steps:**
1. Add `taskDelegation` property to `implementation.properties` in `schema.json`
2. Add `"taskDelegation": "auto"` to `examples/.specops.full.json`

**Acceptance Criteria:**
- [x] schema.json includes taskDelegation with enum ["auto", "always", "never"], default "auto", maxLength 10
- [x] examples/.specops.full.json includes the new field
- [x] Schema validation test passes

**Files to Modify:**
- `schema.json`
- `examples/.specops.full.json`

**Tests Required:**
- [ ] `python3 tests/check_schema_sync.py` passes
- [ ] `python3 tests/test_schema_validation.py` passes

---

### Task 3: Create core/task-delegation.md
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** Task 1
**Priority:** High
**Blocker:** None
**Domain:** backend

**Description:**
Create the core task delegation module with delegation decision logic, handoff bundle format, three strategies, and safety rules. Must use abstract operations only (platform-agnostic).

**Implementation Steps:**
1. Create `core/task-delegation.md` with the complete module content
2. Include: Delegation Decision, Handoff Bundle, Strategy A (Sub-Agent), Strategy B (Session Checkpoint), Strategy C (Enhanced Sequential), Delegation Safety sections
3. Ensure all file operations use abstract ops (READ_FILE, EDIT_FILE, etc.)
4. Include per-task testing in delegate responsibilities

**Acceptance Criteria:**
- [x] Module uses only abstract operations (no platform-specific tool names)
- [x] All three strategies documented with complete protocols
- [x] Handoff bundle format specified
- [x] Delegation safety rules included
- [x] Per-task testing defined in delegate responsibilities

**Files to Modify:**
- `core/task-delegation.md` (new file)

**Tests Required:**
- [ ] File exists and is well-formed markdown

---

### Task 4: Modify Phase 3 in workflow.md
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** High
**Blocker:** None
**Domain:** backend

**Description:**
Update Phase 3 step 2 to include the delegation decision check before sequential execution.

**Implementation Steps:**
1. Replace step 2 in Phase 3 of `core/workflow.md` with delegation-aware version

**Acceptance Criteria:**
- [x] Phase 3 step 2 references the Task Delegation module
- [x] Delegation is checked before falling back to sequential execution
- [x] Other Phase 3 steps remain unchanged

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [ ] Workflow markers still present in generated outputs

---

### Task 5: Add delegation compatibility to task-tracking.md
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** Medium
**Blocker:** None
**Domain:** backend

**Description:**
Add a Delegation Compatibility section to task-tracking.md explaining how the task state machine rules apply during delegated execution.

**Implementation Steps:**
1. Add "Delegation Compatibility" section after "Single Active Task" in `core/task-tracking.md`

**Acceptance Criteria:**
- [x] Section explains orchestrator vs delegate responsibilities
- [x] Write Ordering Protocol responsibility assigned to delegate
- [x] Orchestrator conformance gate documented

**Files to Modify:**
- `core/task-tracking.md`

**Tests Required:**
- [ ] Task tracking markers still present in generated outputs

---

### Task 6: Wire into generator pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3
**Priority:** High
**Blocker:** None
**Domain:** backend

**Description:**
Add task_delegation to the generator build context and include it in all 4 platform Jinja2 templates.

**Implementation Steps:**
1. Add `"task_delegation": core["task-delegation"]` to `build_common_context()` in `generator/generate.py`
2. Add `{{ task_delegation }}` after `{{ task_tracking }}` in `generator/templates/claude.j2`
3. Add `{{ task_delegation }}` after `{{ task_tracking }}` in `generator/templates/cursor.j2`
4. Add `{{ task_delegation }}` after `{{ task_tracking }}` in `generator/templates/codex.j2`
5. Add `{{ task_delegation }}` after `{{ task_tracking }}` in `generator/templates/copilot.j2`

**Acceptance Criteria:**
- [x] `build_common_context()` includes `task_delegation` key
- [x] All 4 .j2 templates include `{{ task_delegation }}`
- [x] `python3 generator/generate.py --all` succeeds

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

**Tests Required:**
- [ ] Generator runs without errors
- [ ] Generated outputs contain delegation content

---

### Task 7: Add validation markers
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 6
**Priority:** High
**Blocker:** None
**Domain:** backend

**Description:**
Add DELEGATION_MARKERS to validate.py — both the per-platform check and the cross-platform consistency check.

**Implementation Steps:**
1. Add `DELEGATION_MARKERS` constant to `generator/validate.py`
2. Add `check_markers_present` call in `validate_platform()` for delegation markers
3. Add `DELEGATION_MARKERS` to the cross-platform consistency check loop in `main()`

**Acceptance Criteria:**
- [x] DELEGATION_MARKERS constant defined with markers matching core/task-delegation.md headings
- [x] Per-platform validation includes delegation markers
- [x] Cross-platform consistency check includes delegation markers
- [x] `python3 generator/validate.py` passes

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [ ] Validator passes for all 4 platforms
- [ ] `python3 tests/test_platform_consistency.py` passes

---

### Task 8: Regenerate, validate, and test
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 7
**Priority:** High
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Regenerate all platform outputs, run validation, and run all tests to confirm everything works end-to-end.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Verify generated Claude SKILL.md contains Strategy A with Agent tool reference
5. Verify generated Cursor .mdc contains Strategy B with session checkpoint

**Acceptance Criteria:**
- [x] All 4 platform outputs regenerated successfully
- [x] Validator passes with 0 errors
- [x] All tests pass
- [x] Generated outputs contain platform-appropriate delegation instructions

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/plugin.json` (generated)
- `.claude-plugin/marketplace.json` (generated)

**Tests Required:**
- [ ] `python3 generator/validate.py` — 0 errors
- [ ] `bash scripts/run-tests.sh` — all pass

## Implementation Order
1. Task 1, Task 2 (independent foundations)
2. Task 3 (core module — depends on Task 1 for capability flag reference)
3. Task 4, Task 5 (workflow integration — depend on Task 3)
4. Task 6 (generator pipeline — depends on Task 3)
5. Task 7 (validation — depends on Task 6)
6. Task 8 (end-to-end verification — depends on all)

## Progress Tracking
- Total Tasks: 8
- Completed: 8
- In Progress: 0
- Blocked: 0
- Pending: 0
