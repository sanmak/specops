# Design: Task Delegation for Phase 3

## Architecture Overview
Task delegation adds an orchestrator/worker pattern to Phase 3. The main session (orchestrator) stays lightweight — it reads tasks.md, constructs a focused handoff bundle for each task, and delegates execution to a fresh context. The worker (delegate) implements a single task with only the information it needs, then returns control. Three platform-adaptive strategies share the same core protocol but differ in how "fresh context" is achieved.

## Technical Decisions

### Decision 1: No New Abstract Tool Operation
**Context:** Should delegation be modeled as a new abstract operation (DELEGATE_TASK) in core/tool-abstraction.md?
**Options Considered:**
1. Add DELEGATE_TASK to tool-abstraction.md — would need mapping in all platform.json files
2. Handle delegation purely through workflow instructions and capability flags

**Decision:** Option 2 — workflow instructions + capability flag
**Rationale:** Delegation is a workflow strategy, not a tool operation. It varies fundamentally by platform (sub-agents vs session checkpoints vs sequential). Adding it to tool-abstraction would create a false equivalence. Follows simplicity principle: don't create abstractions used for different purposes on each platform.

### Decision 2: New Capability Flag
**Context:** How does the generator know which strategy to render?
**Decision:** Add `canDelegateTask` boolean to platform.json capabilities. Only Claude Code gets `true` (has Agent tool). All others get `false`.

### Decision 3: Configuration via .specops.json
**Context:** When should delegation activate?
**Decision:** Add `implementation.taskDelegation` with values `"auto"` (default), `"always"`, `"never"`. Auto activates when 4+ pending tasks and platform supports it.

### Decision 4: Sequential Only
**Context:** Should we support parallel task execution?
**Decision:** Sequential only. Parallel introduces merge conflicts in shared files and concurrent implementation.md updates. Deferred to future spec.

## Component Design

### Component 1: core/task-delegation.md
**Responsibility:** Platform-agnostic delegation protocol — decision logic, handoff bundle format, three strategies, safety rules
**Dependencies:** core/task-tracking.md (task state machine), core/workflow.md (Phase 3 integration)

### Component 2: Capability Flag (canDelegateTask)
**Responsibility:** Platform-level declaration of sub-agent spawning support
**Interface:** Boolean in platform.json `capabilities` object
**Dependencies:** core/tool-abstraction.md (capability flags table)

### Component 3: Config Option (taskDelegation)
**Responsibility:** User-facing toggle for delegation behavior
**Interface:** String enum in schema.json under `implementation`
**Dependencies:** schema.json, examples/.specops.full.json

### Component 4: Generator + Validator Pipeline
**Responsibility:** Include task-delegation module in generated outputs, validate markers across all platforms
**Dependencies:** generator/generate.py, generator/templates/*.j2, generator/validate.py

## Sequence: Orchestrator Loop (Strategy A)

```
Orchestrator                  tasks.md        Sub-Agent
    |                            |                |
    |-- READ tasks.md ---------->|                |
    |<-- next Pending task ------|                |
    |-- EDIT set In Progress --->|                |
    |                            |                |
    |-- construct handoff bundle |                |
    |-- spawn fresh agent ------>|                |
    |                            |<-- READ files  |
    |                            |<-- implement   |
    |                            |<-- EDIT status |
    |                            |-- Completed -->|
    |<-- agent returns ----------|                |
    |                            |                |
    |-- READ tasks.md ---------->|                |
    |<-- verify Completed -------|                |
    |-- NOTIFY user              |                |
    |-- repeat for next task     |                |
```

## Handoff Bundle Format

The orchestrator constructs a focused prompt for each delegated task:

1. **Task details** — full content from tasks.md (Description, Implementation Steps, Acceptance Criteria, Files to Modify, Tests Required)
2. **Design context** — relevant section from design.md matched by component name or task reference
3. **Prior task summaries** — one-line summary per completed task from implementation.md Session Log
4. **Conventions** — team conventions from .specops.json
5. **File paths only** — delegate reads file contents itself (keeps bundle small)

## Delegation Safety
- Delegates inherit ALL safety rules from the Safety module
- Delegates must NOT modify spec artifacts outside their assigned task scope
- The orchestrator verifies task status in tasks.md after each delegation (conformance gate)
- If a delegate returns without Completed or Blocked: orchestrator sets Blocked with reason

## Testing Strategy
- Per-task testing: delegates run tests before marking Completed (when implementation.testing is "auto")
- Orchestrator does NOT run full integration suite between tasks
- If a later delegate discovers a prior task broke something: sets itself to Blocked referencing the prior task

## Risks & Mitigations
- **Risk 1:** Sub-agent prompt too large → **Mitigation:** Bundle includes file paths only (not contents), design context matched by component
- **Risk 2:** Sub-agent fails silently → **Mitigation:** Orchestrator verifies tasks.md status after each return
- **Risk 3:** Cursor/Copilot UX friction (manual session restart) → **Mitigation:** Phase 1 context recovery handles seamless resume
