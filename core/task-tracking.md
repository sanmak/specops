## Task State Machine

### States

Every task in `tasks.md` has exactly one status:

| Status | Meaning |
|--------|---------|
| Pending | Not started |
| In Progress | Currently being worked on |
| Completed | Finished and verified |
| Blocked | Cannot proceed — requires resolution |

### Valid Transitions

```
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

### Acceptance Criteria Verification

Checkboxes in `tasks.md` are completion gates, not decoration. When transitioning a task to `Completed`:

1. Review every item under **Acceptance Criteria:** — check off each satisfied criterion: `- [ ]` → `- [x]`
2. Review every item under **Tests Required:** — check off each passing test: `- [ ]` → `- [x]`
3. If any acceptance criterion is NOT satisfied, do NOT mark the task `Completed` — keep it `In Progress` or set it to `Blocked` with the unmet criterion as the blocker

A task with unchecked acceptance criteria and a `Completed` status is a protocol breach — it signals verified work that was never actually verified.

### Deferred Criteria

Sometimes an acceptance criterion is intentionally excluded from the current scope (deferred to a future spec). To avoid blocking completion:

1. Move the deferred criterion from the main **Acceptance Criteria** list to a **Deferred Criteria** subsection beneath it
2. Annotate each deferred item with a reason: `- criterion text *(deferred — reason)*`
3. Deferred items are NOT checked during completion gate verification — only items in the main **Acceptance Criteria** list are gates

A task or spec with all main acceptance criteria checked and some items in **Deferred Criteria** is valid for completion. Deferred items should be tracked for follow-up (e.g., as future spec candidates in the Scope Boundary section).

### Conformance Rules

- **File-chat consistency**: reported status in chat must match what is persisted in `tasks.md`
- **Checkbox-status consistency**: a `Completed` task must have all acceptance criteria and test items checked off
- **Deferred-item tracking**: deferred acceptance criteria must be moved to a Deferred Criteria subsection, not left unchecked in the main list
- **Dependency enforcement**: if Task B depends on Task A, and Task A is `Blocked`, Task B cannot be set to `In Progress`
- **Progress summary accuracy**: the Progress Tracking counts at the bottom of `tasks.md` must reflect actual statuses
