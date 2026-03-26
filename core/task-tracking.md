## Task State Machine

### States

Every task in `tasks.md` has exactly one status:

| Status | Meaning |
| --- | --- |
| Pending | Not started |
| In Progress | Currently being worked on |
| Completed | Finished and verified |
| Blocked | Cannot proceed — requires resolution |

### Valid Transitions

```text
Pending ──────► In Progress
In Progress ──► Completed
In Progress ──► Blocked
Blocked ──────► In Progress
```

**Prohibited transitions** (protocol breach if attempted):

- Pending → Completed (must pass through In Progress)
- Pending → Blocked (must start work to discover blockers)
- Completed → any state (completed is terminal)
- Blocked → Completed (must unblock first)
- Blocked → Pending (cannot regress)

### Pre-Task Anchoring

Before setting a task to `In Progress`, anchor the task's expected scope in `implementation.md`:

1. READ_FILE the task's **Acceptance Criteria** and **Tests Required** sections from `tasks.md`
2. READ_FILE the relevant requirements from `requirements.md`/`bugfix.md`/`refactor.md` and the matching design section from `design.md`
3. EDIT_FILE `implementation.md` — append a brief Task Scope note to the Session Log: `Task N scope: [1-2 sentence summary of expected changes and acceptance criteria]`

This anchored scope is used by the Pivot Check (below) to detect drift between planned and actual changes. Without the anchor, pivot detection has nothing to compare against.

### Write Ordering Protocol

When changing task status, follow this strict sequence:

1. EDIT_FILE `tasks.md` to update the task's `**Status:**` line
2. Then perform the work (implement, test, etc.)
3. Then report progress in chat

This means:

- Before starting a task: write `In Progress` to `tasks.md` first
- Before reporting completion: write `Completed` to `tasks.md` first
- Before reporting a blocker: write `Blocked` to `tasks.md` first

Violation of write ordering is a protocol breach. Chat status must never lead persisted file status.

### Single Active Task

Only **one** task may be `In Progress` at any time. Before setting a new task to `In Progress`:

1. READ_FILE `tasks.md`
2. Verify no other task has `**Status:** In Progress`
3. If one does, complete it or set it to `Blocked` first

### Delegation Compatibility

When tasks are executed via delegation (see the Task Delegation module):

- The **Single Active Task** rule still applies — the orchestrator sets one task to In Progress before delegating it
- The **Write Ordering Protocol** is the delegate's responsibility — the delegate updates tasks.md before and after work
- The orchestrator **verifies** task status in tasks.md after each delegation returns (conformance gate)
- If a delegate returns without setting Completed or Blocked, the orchestrator sets the task to Blocked with reason "Delegate did not complete task"

### Blocker Handling

When a task is blocked:

1. EDIT_FILE `tasks.md` — set `**Status:** Blocked` on the task
2. Add a `**Blocker:**` line with: the error or dependency, and what is needed to unblock
3. EDIT_FILE `implementation.md` — add an entry to the "Blockers Encountered" section

When unblocking:

1. Update or clear the `**Blocker:**` line
2. Set status back to `In Progress` (following write ordering)

### Implementation Journal Updates

After completing each code-modifying task (not documentation-only or config-only tasks), check whether any of these conditions apply:

1. **Decision made**: A non-trivial choice was made during implementation (library selection, algorithm choice, approach when multiple options existed). EDIT_FILE `implementation.md` — append a row to the "Decision Log" table with: sequential number, the decision, rationale, task number, and current date.

2. **Deviation from design**: The implementation differs from what `design.md` specified. EDIT_FILE `implementation.md` — append a row to the "Deviations from Design" table with: what was planned, what was actually done, the reason, and task number.

3. **Blocker encountered**: Already handled by Blocker Handling above.

If none of these conditions apply (the task was implemented exactly as designed with no notable choices), skip the journal update for that task. Do not add trivial entries.

When resuming implementation in a new session, READ_FILE `implementation.md` before starting work to recover context from previous sessions. The Session Log section records session boundaries — append a brief entry noting which task you are resuming from.

### Pivot Check

Before marking a task `Completed`, compare the actual output against the anchored Task Scope note in `implementation.md` (written during Pre-Task Anchoring) and the planned approach in `design.md` and `requirements.md`. If the implementation diverged from the anchored scope (different approach, different data format, different API, scope change), update the affected spec artifact **before** closing the task. Spec artifacts that still describe the old approach after a pivot are a recurring drift class — Phase 4 checkbox verification cannot catch it because the outdated spec text has no checkboxes to fail.

### Acceptance Criteria Verification

Checkboxes in `tasks.md` are completion gates, not decoration. When transitioning a task to `Completed`:

1. **Pivot check**: Did this task's output differ from the plan? If yes, update the relevant spec artifact (design.md, requirements.md) before proceeding.
2. Review every item under **Acceptance Criteria:** — check off each satisfied criterion: `- [ ]` → `- [x]`
3. Review every item under **Tests Required:** — check off each passing test: `- [ ]` → `- [x]`
4. If any acceptance criterion is NOT satisfied, do NOT mark the task `Completed` — keep it `In Progress` or set it to `Blocked` with the unmet criterion as the blocker

A task with unchecked acceptance criteria and a `Completed` status is a protocol breach — it signals verified work that was never actually verified.

### Deferred Criteria

Sometimes an acceptance criterion is intentionally excluded from the current scope (deferred to a future spec). To avoid blocking completion:

1. Move the deferred criterion from the main **Acceptance Criteria** list to a **Deferred Criteria** subsection beneath it
2. Annotate each deferred item with a reason: `- criterion text *(deferred — reason)*`
3. Deferred items are NOT checked during completion gate verification — only items in the main **Acceptance Criteria** list are gates

A task or spec with all main acceptance criteria checked and some items in **Deferred Criteria** is valid for completion. Deferred items should be tracked for follow-up (e.g., as future spec candidates in the Scope Boundary section).

### External Tracker Sync

When `config.team.taskTracking` is not `"none"` and the task has a populated `**IssueID:**` (neither `None` nor prefixed with `FAILED`):

On **every status transition** (Pending → In Progress, In Progress → Completed, In Progress → Blocked, Blocked → In Progress), after updating `tasks.md` (Write Ordering Protocol), sync the status to the external tracker following the Status Sync protocol in the Configuration Handling module.

**Sync failures are non-blocking**: If the command to update the external tracker fails, NOTIFY_USER with the error and continue. The `tasks.md` state machine is always the source of truth.

**Completion close (mandatory)**: When transitioning a task to `Completed`, close the corresponding external issue. Skipping this step when `config.team.taskTracking` is not `"none"` and the task has a valid IssueID is a protocol breach. Execute the following steps immediately after the `tasks.md` status update (Write Ordering Protocol step 1) and before the completion report (step 3):

1. Verify preconditions: `config.team.taskTracking` is not `"none"` AND the task's `**IssueID:**` is neither `None` nor prefixed with `FAILED`. If preconditions are not met, skip to step 5.
2. If `canExecuteCode` is true, first normalize the IssueID according to the Status Sync protocol. For GitHub, derive `<number>` by stripping any leading `#` from the stored IssueID; for other platforms, use the stored IssueID as required by their respective CLIs. Then execute the platform-specific close command:
   - GitHub: RUN_COMMAND(`gh issue close <number> --reason completed`)
   - Jira: RUN_COMMAND(`jira issue move <IssueID> "Done"`)
   - Linear: RUN_COMMAND(`linear issue update <IssueID> --status "Done"`)
3. If the close command fails: NOTIFY_USER("Warning: Could not close external issue <IssueID> — <error>. The issue remains open. Continue with task completion.") and continue. Do NOT block the task from being marked complete in `tasks.md`.
4. If `canExecuteCode` is false: NOTIFY_USER("Task completed. Please close external issue <IssueID> manually: `<platform-specific close command>`") and continue.
5. Proceed with Acceptance Criteria Verification and completion report.

Issue creation uses the Issue Body Composition template from the Configuration Handling module — freeform issue bodies are a protocol breach.

### Conformance Rules

- **Spec-level dependency gate first**: When a spec has `specDependencies` in its spec.json, the spec-level dependency gate (see `core/decomposition.md` section 7) must pass before any task-level dependencies are evaluated. The ordering is: (1) verify all required spec-level dependencies are completed, (2) then evaluate task-level dependencies within the spec. A task cannot be set to `In Progress` if the spec-level dependency gate has not passed, regardless of whether the task's own `**Dependencies:**` field shows `None`.
- **File-chat consistency**: reported status in chat must match what is persisted in `tasks.md`
- **Checkbox-status consistency**: a `Completed` task must have all acceptance criteria and test items checked off
- **Deferred-item tracking**: deferred acceptance criteria must be moved to a Deferred Criteria subsection, not left unchecked in the main list
- **Dependency enforcement**: if Task B depends on Task A, and Task A is `Blocked`, Task B cannot be set to `In Progress`
- **Progress summary accuracy**: the Progress Tracking counts at the bottom of `tasks.md` must reflect actual statuses
