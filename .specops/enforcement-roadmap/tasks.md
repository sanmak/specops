# Implementation Tasks: Enforcement Roadmap

## Task Breakdown

### Task 1: Checkbox Staleness Linter (A1)
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #61
**Blocker:** None

**Description:**
Create `scripts/lint-spec-artifacts.py` that scans `<specsDir>/*/tasks.md` for completed tasks with unchecked `- [ ]` items, excluding items under `**Deferred Criteria**` subsections. The linter should accept an optional specsDir argument (default `.specops`), scan all spec directories, and report errors with spec name, task name, and unchecked item.

**Implementation Steps:**
1. Create `scripts/lint-spec-artifacts.py` with argparse for optional specsDir
2. Implement task parsing: extract task blocks, identify status, find Acceptance Criteria and Deferred Criteria sections
3. For completed tasks: check for unchecked `- [ ]` items outside Deferred Criteria
4. Report errors with spec name, task number, and unchecked item text
5. Exit code 0 if no errors, 1 if any errors found
6. Add the linter to `scripts/run-tests.sh` (conditional on specsDir existence)

**Acceptance Criteria:**
- [x] Linter detects unchecked items in completed tasks
- [x] Linter skips items under Deferred Criteria subsections
- [x] Linter runs against all 9 existing dogfood specs with zero errors
- [x] Linter integrated into `scripts/run-tests.sh`
- [x] Exit code reflects pass/fail status

**Files to Modify:**
- `scripts/lint-spec-artifacts.py` (new)
- `scripts/run-tests.sh`

**Tests Required:**
- [x] Run linter against existing dogfood specs — zero errors
- [x] Manual test: create a task with unchecked items and verify detection

---

### Task 2: Phase 1 Context Summary Gate (A2)
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #62
**Blocker:** None

**Description:**
Add a mandatory Phase 1 Context Summary section to the implementation.md template. Add a gate in `core/workflow.md` requiring this section to be written before Phase 2 starts. The Context Summary records: config status, context recovery, steering files loaded, repo map status, memory loaded, detected vertical, and affected files.

**Implementation Steps:**
1. Add `## Phase 1 Context Summary` template to `core/templates/implementation.md` with placeholder fields
2. In `core/workflow.md` Phase 1, after the pre-flight check (step 5), add instruction to write the Context Summary to implementation.md
3. In `core/workflow.md` Phase 2, add a gate: "Phase 2 cannot start until the Phase 1 Context Summary has been written to implementation.md — proceeding without it is a protocol breach"
4. Ensure all Phase 1 steps use imperative language (verify no remaining "Tip:" or "consider" in Phase 1)

**Acceptance Criteria:**
- [x] `core/templates/implementation.md` contains `## Phase 1 Context Summary` section
- [x] `core/workflow.md` Phase 1 includes Context Summary write instruction
- [x] `core/workflow.md` Phase 2 includes Context Summary gate with protocol breach language
- [x] No "Tip:" language remains in Phase 1 steps

**Files to Modify:**
- `core/templates/implementation.md`
- `core/workflow.md`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes

---

### Task 3: Phase 4 Docs Check Gate (A3)
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1 (linter), Task 2 (gate pattern)
**Priority:** High
**IssueID:** #63
**Blocker:** None

**Description:**
Add a mandatory `## Documentation Review` section requirement to Phase 4 in `core/workflow.md`. The agent must write this section to implementation.md listing each doc checked and its status. Extend `scripts/lint-spec-artifacts.py` to verify the section exists for completed specs.

**Implementation Steps:**
1. In `core/workflow.md` Phase 4, strengthen the documentation check step: agent MUST write `## Documentation Review` to implementation.md
2. Add protocol breach language: if docs flagged stale and not updated, cannot set status to completed without explicit user confirmation
3. Extend `scripts/lint-spec-artifacts.py`: for completed specs, verify `## Documentation Review` section exists in implementation.md
4. Add `## Documentation Review` template section to `core/templates/implementation.md`

**Acceptance Criteria:**
- [x] `core/workflow.md` Phase 4 requires Documentation Review section with enforcement language
- [x] `core/templates/implementation.md` contains `## Documentation Review` section
- [x] Linter checks for Documentation Review section in completed specs
- [x] Existing dogfood specs are not broken (they were completed before this gate — linter should handle gracefully or skip legacy specs)

**Files to Modify:**
- `core/workflow.md`
- `core/templates/implementation.md`
- `scripts/lint-spec-artifacts.py`

**Tests Required:**
- [x] Linter runs against dogfood specs without false positives
- [x] `python3 generator/validate.py` passes

---

### Task 4: Config-to-Workflow Binding (A4)
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #64
**Blocker:** None

**Description:**
Add "Workflow Impact" annotations in `core/config-handling.md` for each config value that should affect agent behavior. Add explicit conditionals in `core/workflow.md` Phase 3 for `taskTracking` config. Audit all config flags for missing workflow references.

**Implementation Steps:**
1. In `core/config-handling.md`, add a `### Workflow Impact` subsection after each behavioral config value documenting which workflow step(s) it affects
2. In `core/workflow.md` Phase 3, add explicit conditionals: "If config.team.taskTracking is not 'none', RUN_COMMAND to create issue before setting task to In Progress"
3. Audit config values: `autoCommit`, `createPR`, `testing`, `linting`, `formatting`, `taskTracking`, `specReview`, `taskDelegation` — verify each has a corresponding workflow reference
4. Document any config values that lack workflow references as findings

**Acceptance Criteria:**
- [x] Each behavioral config value in config-handling.md has a Workflow Impact annotation
- [x] Phase 3 workflow has explicit conditionals for taskTracking
- [x] Audit results documented (which config values now have workflow references, which are informational-only)

**Files to Modify:**
- `core/config-handling.md`
- `core/workflow.md`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes

---

### Task 5: Cross-Section Coherence Check (A5)
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #65
**Blocker:** None

**Description:**
Add a "Coherence Verification" step at the end of Phase 2 (after all spec files are generated). The agent reads the requirements/bugfix/refactor file, extracts numeric constraints from NFRs, cross-checks against functional requirements, and records the result in implementation.md. Add COHERENCE_MARKERS to `generator/validate.py`.

**Implementation Steps:**
1. In `core/workflow.md` Phase 2, add a Coherence Verification step after spec file generation and before external issue creation
2. Define the coherence check procedure: read the spec file, extract numeric constraints from NFRs, cross-check against functional requirements for contradictions
3. Require the result to be recorded in implementation.md (in the Phase 1 Context Summary or a new `## Coherence Check` subsection)
4. Add COHERENCE_MARKERS to `generator/validate.py` — markers like "Coherence Verification", "cross-check"
5. Add COHERENCE_MARKERS to the cross-platform consistency loop in validate.py

**Acceptance Criteria:**
- [x] `core/workflow.md` Phase 2 contains Coherence Verification step
- [x] Coherence result recorded in implementation.md
- [x] COHERENCE_MARKERS defined in `generator/validate.py`
- [x] COHERENCE_MARKERS in cross-platform consistency check loop
- [x] `python3 generator/validate.py` passes with new markers

**Files to Modify:**
- `core/workflow.md`
- `generator/validate.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 6: Pre-Task Anchoring (B1)
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** Medium
**IssueID:** #66
**Blocker:** None

**Description:**
Before setting a task to In Progress, the agent must READ acceptance criteria and relevant requirements, then write a "Task Scope" note to implementation.md. After completing the task, the existing pivot check is strengthened to compare actual changes against the anchored Task Scope.

**Implementation Steps:**
1. In `core/task-tracking.md`, add a pre-task anchoring step before the In Progress transition: READ acceptance criteria + relevant requirements, WRITE_FILE a Task Scope note to implementation.md
2. Strengthen the existing Pivot Check section: reference the anchored Task Scope for comparison, not just the design.md
3. Use abstract operations (READ_FILE, WRITE_FILE) per tool-abstraction.md

**Acceptance Criteria:**
- [x] `core/task-tracking.md` contains pre-task anchoring step
- [x] Pivot Check references anchored Task Scope
- [x] Uses abstract operations only

**Files to Modify:**
- `core/task-tracking.md`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes

---

### Task 7: Vertical Vocabulary Verification (B2)
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** Medium
**IssueID:** #67
**Blocker:** None

**Description:**
After generating spec files in Phase 2, add a vocabulary verification step that scans for prohibited default terms and replaces with vertical-specific terms. The result is recorded in the Context Summary.

**Implementation Steps:**
1. In `core/verticals.md`, add a "Vocabulary Verification" subsection describing the post-generation scan
2. Define prohibited terms per vertical (the inverse of the vocabulary mapping — e.g., for infrastructure, "User Stories" is prohibited when the correct term is "Infrastructure Requirements")
3. In `core/workflow.md` Phase 2, after spec generation and Coherence Verification, add the vocabulary verification step
4. Record result in implementation.md

**Acceptance Criteria:**
- [x] `core/verticals.md` contains Vocabulary Verification subsection
- [x] Prohibited terms defined for each vertical
- [x] `core/workflow.md` Phase 2 references vocabulary verification
- [x] Result recorded in implementation.md

**Files to Modify:**
- `core/verticals.md`
- `core/workflow.md`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes

---

### Task 8: Version Extraction Linter (B3)
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1 (extends lint-spec-artifacts.py)
**Priority:** Medium
**IssueID:** #68
**Blocker:** None

**Description:**
Extend `scripts/lint-spec-artifacts.py` to verify that `specopsCreatedWith` and `specopsUpdatedWith` fields in spec.json match a valid semver pattern (e.g., `1.3.0`), are absent, or are `"unknown"` (acceptable for legacy specs). Invalid patterns (empty string, non-semver text) should be reported as warnings.

**Implementation Steps:**
1. In `scripts/lint-spec-artifacts.py`, add a version validation check for each spec's spec.json
2. Parse `specopsCreatedWith` and `specopsUpdatedWith` fields
3. Validate against semver regex: `^\d+\.\d+\.\d+$`
4. Accept absent fields or `"unknown"` (legacy compatibility)
5. Report warnings for invalid patterns

**Acceptance Criteria:**
- [x] Linter validates version fields in spec.json
- [x] Valid semver, absent, and "unknown" are accepted
- [x] Invalid patterns reported as warnings
- [x] Existing dogfood specs pass validation

**Files to Modify:**
- `scripts/lint-spec-artifacts.py`

**Tests Required:**
- [x] Run linter against existing dogfood specs — zero version errors

---

## Implementation Order
1. Task 1 (A1 — Checkbox Linter) — foundation, independent
2. Task 2 (A2 — Phase 1 Context Summary) — independent
3. Task 4 (A4 — Config-to-Workflow) — independent
4. Task 5 (A5 — Coherence Check) — independent
5. Task 3 (A3 — Phase 4 Docs Gate) — depends on Task 1 and Task 2 patterns
6. Task 6 (B1 — Pre-Task Anchoring) — independent
7. Task 7 (B2 — Vertical Verification) — independent
8. Task 8 (B3 — Version Linter) — extends Task 1

Regenerate all platform outputs after completing all tasks.

## Progress Tracking
- Total Tasks: 8
- Completed: 8
- In Progress: 0
- Blocked: 0
- Pending: 0
