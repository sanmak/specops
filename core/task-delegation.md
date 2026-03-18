## Task Delegation

Task delegation executes each Phase 3 task in a fresh context to prevent context window exhaustion. The main session acts as a lightweight orchestrator — it reads tasks.md, constructs a focused handoff bundle for each task, and delegates execution to a fresh context. Each delegate implements a single task with only the information it needs.

### Delegation Decision

At the start of Phase 3, after the implementation gate (step 1), determine whether to use delegation:

1. Read `config.implementation.taskDelegation` (default: `"auto"`)
2. If `"never"`: skip delegation, use standard sequential execution (Phase 3 step 2 as-is)
3. If `"always"`: activate delegation regardless of task count
4. If `"auto"`: READ_FILE `tasks.md`, count tasks with `**Status:** Pending`. If 4 or more, activate delegation. Otherwise, use standard sequential execution.
5. Check platform capability `canDelegateTask`:
   - `canDelegateTask = true` → **Strategy A** (Sub-Agent Delegation)
   - `canDelegateTask = false` and `canAskInteractive = true` → **Strategy B** (Session Checkpoint)
   - `canDelegateTask = false` and `canAskInteractive = false` → **Strategy C** (Enhanced Sequential)

### Handoff Bundle

The orchestrator constructs a focused context document for each delegated task. The bundle contains only what the delegate needs — no accumulated conversation history.

1. **Task details**: Full task content from tasks.md — Description, Implementation Steps, Acceptance Criteria, Files to Modify, Tests Required
2. **Design context**: The relevant section from design.md matched by component name or task reference. If no clear match, include the Architecture Overview section.
3. **Prior task summaries**: One-line summary per previously completed task, extracted from implementation.md Session Log entries
4. **Conventions**: Team conventions from `.specops.json` (if any)
5. **File paths only**: The delegate reads file contents itself. Do not include file contents in the bundle — this keeps it small.
6. **Execution protocols**: (a) Write Ordering — update tasks.md status to `In Progress` BEFORE starting work, and to `Completed` or `Blocked` BEFORE reporting. (b) Single Active Task — only one task may be In Progress at a time. (c) Acceptance Criteria — all checkboxes under `Acceptance Criteria:` and `Tests Required:` must be verified before marking Completed. (d) Implementation Journal — if you make a non-trivial design decision or deviate from design.md, append to implementation.md Decision Log or Deviations table. (e) File scope — modify only the files listed in "Files to Modify" for this task.

### Strategy A: Sub-Agent Delegation

When `canDelegateTask = true`:

**Orchestrator loop:**

1. READ_FILE `tasks.md` — identify the next task with `**Status:** Pending`
2. EDIT_FILE `tasks.md` — set that task to `**Status:** In Progress` (Write Ordering Protocol)
3. Construct the Handoff Bundle (see above)
4. Spawn a fresh agent with the handoff bundle as its prompt
5. When the agent returns:
   a. READ_FILE `tasks.md` — verify the task status is `Completed` or `Blocked`
   b. READ_FILE `implementation.md` — check for new Decision Log or Deviation entries
   c. If `Blocked`: read the `**Blocker:**` line and apply the following decision tree:
      - If the blocker is a missing dependency from another task: skip to the next task with no dependencies on the blocked task
      - Otherwise (implementation failure, environment issue, or ambiguous blocker): NOTIFY_USER with the blocker details and pause delegation for manual intervention
   d. If status is still `In Progress` (delegate did not update): EDIT_FILE `tasks.md` — set to `**Status:** Blocked` with `**Blocker:** Delegate did not complete task — manual review needed`
6. NOTIFY_USER with a brief task completion summary: task name, final status, key changes
7. Repeat from step 1 for the next Pending task
8. When no Pending tasks remain: proceed to Phase 4

**Delegate responsibilities:**

The delegate receives the handoff bundle and executes the single assigned task:

- READ_FILE each file listed in "Files to Modify" to understand current state
- Implement the changes described in Implementation Steps
- Run tests relevant to the task (matching "Tests Required") before marking Completed. If `config.implementation.testing` is `"auto"`, run the tests. If `"skip"`, skip testing. If `"manual"`, note that tests should be run.
- If tests fail: keep the task `In Progress` and attempt to fix. If unfixable, set to `Blocked` with the failure as the blocker reason.
- Check off Acceptance Criteria checkboxes in tasks.md as they are satisfied: `- [ ]` → `- [x]`
- Check off Tests Required checkboxes: `- [ ]` → `- [x]`
- EDIT_FILE `tasks.md` — set `**Status:** Completed` (all criteria met) or `**Status:** Blocked` (with `**Blocker:**` reason)
- If a non-trivial design decision was made: EDIT_FILE `implementation.md` — append a row to the Decision Log table
- If implementation deviates from design.md: EDIT_FILE `implementation.md` — append a row to the Deviations table
- EDIT_FILE `implementation.md` — append a brief Session Log entry: task name, files modified, key outcome
- Return a brief summary of what was implemented

**Delegate constraints:**

- Must NOT modify spec artifacts outside the assigned task scope (no changes to requirements.md, design.md, or other tasks in tasks.md)
  - Exception: When implementation diverges from design.md (pivot), record the deviation in implementation.md Deviations table. Do NOT update design.md — the orchestrator flags deviations for user review after delegation completes.
- Must NOT skip Acceptance Criteria verification
- Must follow the Write Ordering Protocol (update tasks.md status before reporting)
- Inherits all safety rules (convention sanitization, path containment, no secrets in specs)

### Strategy B: Session Checkpoint

When `canDelegateTask = false` and `canAskInteractive = true`:

After completing each task using standard sequential execution:

1. EDIT_FILE `implementation.md` — append a Session Log entry:
   ```
   ### Session N — Task M completed (YYYY-MM-DD)
   Task: [task name]
   Key decisions: [any decisions made, or "none"]
   Files modified: [list of files]
   Next task: Task [N+1] — [title]
   ```
2. ASK_USER: "Task [N] completed. To keep context fresh, start a new conversation and invoke SpecOps — it will automatically detect the in-progress spec and resume from Task [N+1]."
3. If the user chooses to continue in the same session: proceed with standard sequential execution for the next task.

Phase 1 context recovery handles the resume seamlessly — the next session reads implementation.md Session Log and tasks.md statuses to pick up exactly where the previous session ended.

### Strategy C: Enhanced Sequential

When `canDelegateTask = false` and `canAskInteractive = false`:

Execute tasks sequentially (standard Phase 3 behavior) with enhanced checkpointing:

1. After each task completion, EDIT_FILE `implementation.md` — append a detailed Session Log entry with: task name, key decisions, files modified, and a one-line summary of the outcome
2. Note in the output that later tasks may be affected by context window limits if the spec has many tasks
3. If context limitations are detected (degraded outputs, repeated errors), note the affected tasks in implementation.md for the user to review

### Delegation Safety

- Delegates inherit ALL safety rules from the Safety module (convention sanitization, template safety, path containment)
- Delegates must NOT modify files outside the spec's scope
- The orchestrator verifies task status in tasks.md after each delegation — this is the conformance gate
- If a delegate introduces a regression caught by a later task's sub-agent, the later task sets itself to `Blocked` referencing the prior task. The orchestrator surfaces this to the user.
- The Single Active Task rule still applies during delegation — the orchestrator sets one task to In Progress before delegating it

### Platform Adaptation

| Capability | Strategy | Behavior |
|-----------|----------|----------|
| `canDelegateTask = true` | A (Sub-Agent) | Fresh agent per task, orchestrator verifies |
| `canDelegateTask = false`, `canAskInteractive = true` | B (Session Checkpoint) | Prompt user for fresh session after each task |
| `canDelegateTask = false`, `canAskInteractive = false` | C (Enhanced Sequential) | Standard execution with detailed checkpointing |
