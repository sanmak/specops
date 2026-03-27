# Implementation Tasks: Auto-Close GitHub Issues on Task Completion

## Spec-Level Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| --              | --      | --        | --      |

## Dependency Resolution Log

| Blocker | Resolution Type | Resolution Detail | Date |
| ------- | --------------- | ----------------- | ---- |
| --       | --               | --                 | --    |

## Task Breakdown

### Task 1: Add auto-close step to core/task-tracking.md

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #200
**Blocker:** None

**Description:**
Add a deterministic auto-close step to the External Tracker Sync section in `core/task-tracking.md`. When a task transitions to Completed, the agent must close the corresponding external issue. This step must be imperative (not advisory) and use abstract operations.

**Implementation Steps:**

1. Read `core/task-tracking.md` to understand the existing External Tracker Sync section
2. Add a new subsection or expand the existing Completion close paragraph with step-by-step imperative instructions
3. Include platform-specific close commands for GitHub, Jira, and Linear using RUN_COMMAND
4. Add `canExecuteCode` guard and NOTIFY_USER fallback for non-code-executing platforms
5. Add graceful failure handling with NOTIFY_USER (non-blocking)
6. Use "protocol breach" language for skipping auto-close when taskTracking is configured

**Acceptance Criteria:**

- [x] Auto-close step exists in core/task-tracking.md with imperative language
- [x] Uses RUN_COMMAND abstract operation for close commands
- [x] Includes all three platforms: GitHub (`gh issue close`), Jira (`jira issue move "Done"`), Linear (`linear issue update --status "Done"`)
- [x] canExecuteCode guard prevents execution on non-code platforms
- [x] Failure handling is non-blocking (NOTIFY_USER, continue)

**Files to Modify:**

- `core/task-tracking.md`

**Tests Required:**

- [x] Generated platform outputs contain auto-close instructions after regeneration

---

### Task 2: Add Phase 4 sweep to core/workflow.md

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #201
**Blocker:** None

**Description:**
Add a Phase 4 step 5.5 that sweeps all completed tasks for missed issue closures. This catches cases where the Phase 3 auto-close was skipped due to agent context loss, delegation gaps, or platform limitations.

**Implementation Steps:**

1. Read `core/workflow.md` to find the exact location between step 5 (Completion gate) and step 6 (Set spec.json status)
2. Add step 5.5 "Issue closure sweep" with conditions: taskTracking configured, canExecuteCode true
3. Include logic to check each completed task's IssueID against the external tracker
4. Close any still-open issues
5. Report results via NOTIFY_USER
6. Ensure failures are non-blocking

**Acceptance Criteria:**

- [x] Step 5.5 exists in core/workflow.md Phase 4 section
- [x] Checks issue status before attempting close (avoids redundant close attempts)
- [x] Reports results to user
- [x] Non-blocking on failures

**Files to Modify:**

- `core/workflow.md`

**Tests Required:**

- [x] Generated platform outputs contain Phase 4 sweep instructions after regeneration

---

### Task 3: Regenerate all platform outputs

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #202
**Blocker:** None

**Description:**
Run the generator to regenerate all 5 platform outputs after modifying core modules. Verify the generated outputs contain the new auto-close and sweep content.

**Implementation Steps:**

1. Run `python3 generator/generate.py --all`
2. Verify generated files contain the new auto-close content
3. Run `python3 generator/validate.py` to ensure all checks pass
4. Run `bash scripts/run-tests.sh` to ensure all tests pass
5. If any validation fails, fix the source files and regenerate

**Acceptance Criteria:**

- [x] All 5 platform outputs regenerated successfully
- [x] Validator reports 0 errors
- [x] All tests pass
- [x] Generated outputs contain auto-close instructions (spot check claude and cursor)

**Files to Modify:**

- `platforms/claude/SKILL.md`
- `platforms/claude/modes/spec.md`
- `platforms/cursor/specops.mdc`
- `platforms/codex/SKILL.md`
- `platforms/copilot/specops.instructions.md`
- `platforms/antigravity/specops.md`

**Tests Required:**

- [x] `python3 generator/validate.py` passes with 0 errors
- [x] `bash scripts/run-tests.sh` passes all tests

---

### Task 4: Update checksums

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** Medium
**IssueID:** #203
**Blocker:** None

**Description:**
Regenerate CHECKSUMS.sha256 to reflect the modified core files and regenerated platform outputs. The pre-commit hook enforces checksum freshness.

**Implementation Steps:**

1. Check which files in CHECKSUMS.sha256 were modified
2. Regenerate checksums: `shasum -a 256` for all checksummed files
3. Update CHECKSUMS.sha256

**Acceptance Criteria:**

- [x] CHECKSUMS.sha256 reflects current file hashes
- [x] `shasum -a 256 -c CHECKSUMS.sha256` passes

**Files to Modify:**

- `CHECKSUMS.sha256`

**Tests Required:**

- [x] Checksum verification passes

---

## Implementation Order

1. Task 1 (core/task-tracking.md -- add auto-close step)
2. Task 2 (core/workflow.md -- add Phase 4 sweep) -- parallel with Task 1
3. Task 3 (regenerate all platform outputs -- depends on Tasks 1, 2)
4. Task 4 (update checksums -- depends on Task 3)

## Progress Tracking

- Total Tasks: 4
- Completed: 4
- In Progress: 0
- Blocked: 0
- Pending: 0
