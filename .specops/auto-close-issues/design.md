# Design: Auto-Close GitHub Issues on Task Completion

## Architecture Overview

This feature strengthens the existing External Tracker Sync section in `core/task-tracking.md` and adds a Phase 4 sweep to `core/workflow.md`. No new modules are created. The change follows the pattern established by the workflow-enforcement-gates spec: converting advisory cross-references into deterministic imperative steps with enforcement language.

The existing `core/config-handling.md` Status Sync section already specifies the close commands per platform. The problem is that `core/task-tracking.md` references the config-handling module but does not embed the close step as a mandatory part of the completion flow. Agents skip non-mandatory steps (per L-workflow-enforcement-gates-1 learning).

## Technical Decisions

### Decision 1: Inline Close Step vs Cross-Reference

**Context:** The close command is already documented in config-handling.md under Status Sync. Should task-tracking.md duplicate the commands or cross-reference?

**Options Considered:**

1. Cross-reference to config-handling.md Status Sync -- DRY but agents skip cross-references (proven by the friction point)
2. Inline the close commands directly in task-tracking.md -- Duplication but deterministic execution

**Decision:** Option 2 -- Inline the close commands
**Rationale:** L-workflow-enforcement-gates-1 learning: "agents skip non-mandatory steps." Cross-references are inherently non-mandatory. The task-tracking.md module is the single place where task completion is defined, so the close step must live there. The config-handling.md Status Sync section remains as the authoritative reference, and task-tracking.md adds an imperative step that agents cannot skip.

### Decision 2: Phase 4 Sweep Location

**Context:** Where should the Phase 4 sweep for missed closures live?

**Options Considered:**

1. In `core/task-tracking.md` as a new section
2. In `core/workflow.md` as a new Phase 4 step

**Decision:** Option 2 -- In `core/workflow.md` as Phase 4 step 5.5
**Rationale:** The sweep happens once per spec completion, not per task. It belongs in the Phase 4 completion sequence. Using sub-step notation (5.5) avoids renumbering existing steps (per ast-based-repo-map decision pattern).

### Decision 3: New Validator Markers

**Context:** Should we add new validator markers for the auto-close behavior?

**Decision:** No new markers needed. The auto-close behavior is an enhancement to the existing External Tracker Sync section in task-tracking.md, which is already covered by TASK_TRACKING_MARKERS. The content will appear inside sections already validated by existing markers. If the existing markers do not cover the new content, we will add markers, but the initial approach is to work within existing validated sections.

## Component Design

### Component 1: Task Completion Auto-Close (core/task-tracking.md)

**Responsibility:** Close the external issue when a task transitions to Completed
**Location:** New step 4.5 in the "External Tracker Sync" section, or integrated into the existing completion flow description
**Interface:** Uses existing abstract operations (RUN_COMMAND, NOTIFY_USER, READ_FILE)
**Dependencies:** `canExecuteCode` capability flag, `config.team.taskTracking`, task IssueID

The step is:
1. After updating tasks.md status to Completed (Write Ordering Protocol step 1)
2. Before performing the work completion report (step 3)
3. Check: `config.team.taskTracking` is not `"none"` AND IssueID is valid AND `canExecuteCode` is true
4. Execute platform-specific close command via RUN_COMMAND
5. If command fails: NOTIFY_USER with error, continue (non-blocking)
6. If `canExecuteCode` is false: NOTIFY_USER with suggested manual close command

### Component 2: Phase 4 Issue Sweep (core/workflow.md)

**Responsibility:** Catch any issues that were not closed during Phase 3 (agent context loss, delegation gaps, skipped steps)
**Location:** New step 5.5 in Phase 4, between "Completion gate" (step 5) and "Set spec.json status" (step 6)
**Interface:** Uses READ_FILE, RUN_COMMAND, NOTIFY_USER

The step is:
1. If `config.team.taskTracking` is not `"none"` AND `canExecuteCode` is true:
2. READ_FILE `tasks.md` -- find all tasks with status Completed and a valid IssueID
3. For each such task, check if the issue is still open (GitHub: `gh issue view <number> --json state`)
4. If open, close it via RUN_COMMAND
5. Report results: "Closed N missed issues: #X, #Y, #Z" or "All issues already closed"
6. Failures are non-blocking -- NOTIFY_USER and continue

## Sequence Diagrams

### Flow 1: Task Completion with Auto-Close

```text
Agent -> tasks.md: Set status to Completed (Write Ordering)
Agent -> tasks.md: Read IssueID for this task
Agent -> Config: Check taskTracking != "none"
Agent -> Platform: Check canExecuteCode == true
Agent -> External Tracker: RUN_COMMAND(close issue)
External Tracker -> Agent: Success/Failure
Agent -> User: NOTIFY_USER if failure (non-blocking)
Agent -> tasks.md: Check acceptance criteria
Agent -> Chat: Report completion
```

### Flow 2: Phase 4 Sweep

```text
Agent -> tasks.md: READ_FILE (find all Completed tasks with IssueIDs)
Agent -> External Tracker: For each, check if still open
Agent -> External Tracker: Close any still-open issues
Agent -> User: Report sweep results
Agent -> spec.json: Set status to completed
```

## Data Model Changes

No data model changes. Uses existing `**IssueID:**` field in tasks.md and existing `config.team.taskTracking` configuration.

## Security Considerations

- The close command uses the existing `gh` CLI which inherits the user's authenticated session
- No new authentication mechanisms needed
- IssueID validation (not `None`, not `FAILED`-prefixed) prevents command injection via malformed IssueIDs

## Performance Considerations

- Auto-close adds one CLI command per task completion -- negligible
- Phase 4 sweep adds N status checks + up to N close commands (one per completed task) -- acceptable since this runs once per spec

## Testing Strategy

- Existing test suite validates generated platform outputs contain the right content
- Validator checks ensure abstract operations are substituted correctly
- Manual verification: run the auto-close spec itself with taskTracking enabled to verify issues get closed (dogfood)

## Rollout Plan

1. Modify `core/task-tracking.md` -- add auto-close step
2. Modify `core/workflow.md` -- add Phase 4 sweep step
3. Regenerate all platform outputs
4. Run validator and tests
5. Verify with dogfood (this spec's own issues should auto-close)

## Risks & Mitigations

- **Risk 1:** Agents still skip the auto-close step despite imperative language -- **Mitigation:** Use "protocol breach" enforcement language consistent with other gates; Phase 4 sweep catches misses
- **Risk 2:** gh CLI not authenticated in some environments -- **Mitigation:** Graceful degradation: warn and continue, never block task completion

## Dependencies & Blockers

### Spec Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| --              | --      | --        | --      |

### Cross-Spec Blockers

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| ------- | ------------- | --------------- | ----------------- | ------ |
| --       | --             | --               | --                 | --      |

## Future Enhancements

- Auto-reopen issues if a task is moved back from Completed (currently Completed is terminal, so this is moot)
- Batch close commands to reduce API calls during Phase 4 sweep
- Comment on the issue with a link to the completed task before closing
