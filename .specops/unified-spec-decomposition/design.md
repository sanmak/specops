# Design: Unified Spec Decomposition + Cross-Spec Dependencies + Initiative Orchestration + Phase Dispatch

## Architecture Overview

This feature introduces multi-spec intelligence to SpecOps through two new core modules and targeted extensions to existing modules. The architecture follows SpecOps's three-tier pattern: platform-agnostic core modules using abstract operations, fed through the generator pipeline to produce platform-specific outputs.

Two new core modules with distinct concerns:
- **`core/decomposition.md`** — Scope assessment, split detection, initiative data model, cross-spec dependencies, cycle detection, dependency gates, scope hammering, walking skeleton. Does NOT contain the initiative execution loop.
- **`core/initiative-orchestration.md`** — Autonomous execution of multi-spec initiatives. Lightweight orchestrator that dispatches specs through the normal dispatcher, never reimplements workflow logic.

This separation means the orchestrator works with manually-created initiatives too, not just algorithmically-decomposed ones.

## Technical Decisions

### Decision 1: Always-on scope assessment (no config flag)

**Context:** Whether decomposition should be opt-in via configuration or always active.
**Options Considered:**

1. Config-gated (`config.decomposition.enabled`) — Pros: explicit opt-in. Cons: dead feature if not discovered, config flags without deterministic workflow instructions are dead features (per feedback).
2. Always-on — Pros: universally applied, no discovery problem. Cons: small overhead on every spec.

**Decision:** Always-on
**Rationale:** Config flags without deterministic workflow instructions are dead features (established feedback pattern). Scope assessment runs unconditionally as part of the standard Phase 1→4 flow. The overhead is negligible (file-based complexity signal check).

### Decision 2: Two separate modules

**Context:** Whether decomposition and initiative orchestration should live in one module or two.
**Options Considered:**

1. Single module — Pros: simpler. Cons: orchestrator coupled to decomposition, can't orchestrate manually-created initiatives.
2. Two modules — Pros: separation of concerns, orchestrator works independently. Cons: two files to maintain.

**Decision:** Two modules (`core/decomposition.md` + `core/initiative-orchestration.md`)
**Rationale:** The orchestrator should work with any initiative, not just those created by algorithmic decomposition. A user might manually create an initiative from existing specs.

### Decision 3: Propose-only decomposition

**Context:** Whether the agent should automatically split or propose and wait for user approval.
**Options Considered:**

1. Auto-split — Pros: frictionless. Cons: removes user control, may create unwanted specs.
2. Propose-only — Pros: user retains control, interactive approval flow. Cons: extra step.

**Decision:** Propose-only
**Rationale:** Decomposition decisions have significant downstream effects (multiple specs, initiative tracking). User approval is essential. In non-interactive mode, the system notifies and proceeds as a single spec.

### Decision 4: File-based state for orchestrator

**Context:** How the initiative orchestrator tracks state across spec executions.
**Options Considered:**

1. In-memory state — Pros: fast. Cons: lost on crash, can't resume.
2. File-based state — Pros: resumable, inspectable, no in-memory accumulation. Cons: disk I/O.

**Decision:** File-based state
**Rationale:** The orchestrator must be able to restart at any point and resume. All state comes from disk: initiative.json, spec.json, memory/, implementation.md.

### Decision 5: Phase dispatch (fresh context per phase)

**Context:** Whether Phase 3 and Phase 4 should execute in the same context as Phases 1-2 or get fresh contexts.
**Options Considered:**

1. Same context — Pros: simple. Cons: context window fills up, stale context degrades quality.
2. Fresh context per phase — Pros: maximum context window per phase. Cons: handoff overhead.

**Decision:** Fresh context per phase
**Rationale:** Context window reliability feedback (established feedback pattern) shows skill is too large for reliable single-context execution. Phases 1+2 stay together (tightly coupled), Phase 3 and Phase 4 each get fresh sub-agents. Platform-adapted: full sub-agent on Claude, checkpoint+prompt on Cursor/Copilot, sequential on Codex.

### Decision 6: Lower task delegation threshold

**Context:** Current auto-activation threshold of 6 is too conservative; most non-trivial specs don't trigger delegation.
**Options Considered:**

1. Keep threshold at 6 — Pros: conservative. Cons: under-utilized.
2. Lower to 4 — Pros: activates for most non-trivial specs (4 small tasks or 2 medium). Cons: more sub-agent dispatches.

**Decision:** Lower to 4, make configurable via `config.implementation.delegationThreshold`
**Rationale:** Score 4 covers most non-trivial specs without being overly aggressive. Configurable threshold lets teams adjust.

## Component Design

### Component 1: Scope Assessment Gate (Phase 1.5)

**Responsibility:** Detect when a feature request should be decomposed into multiple specs
**Interface:** Runs after Phase 1 step 9, before Phase 2. Checks complexity signals: independent deliverables, distinct domains (>2 code areas), language signals ("and also", "plus"), estimated >8-10 tasks, independent acceptance criteria clusters.
**Dependencies:** `core/workflow.md` (insertion point), `ASK_USER`/`NOTIFY_USER` abstract ops

### Component 2: Split Detection (Phase 2 Safety Net)

**Responsibility:** Second-pass decomposition check after requirements drafting
**Interface:** Runs in Phase 2 after step 1, fires only if Phase 1.5 did not trigger
**Dependencies:** `core/workflow.md`, Phase 1.5 outcome

### Component 3: Initiative Data Model

**Responsibility:** Schema and lifecycle for multi-spec initiatives
**Interface:** `<specsDir>/initiatives/<id>.json` — JSON file with id, title, description, created, updated, author, specs[], order[][] (execution waves), skeleton, status
**Dependencies:** `initiative-schema.json`, `index-schema.json` (partOf field)

### Component 4: Cross-Spec Dependencies

**Responsibility:** Declare and enforce dependencies between specs
**Interface:** `specDependencies` array in spec.json with entries: {specId, reason, required, contractRef?}
**Dependencies:** `spec-schema.json`, Phase 3 dependency gate

### Component 5: Cycle Detection

**Responsibility:** Prevent circular dependencies across specs
**Interface:** DFS with white/gray/black coloring across all specs' specDependencies. Runs at spec creation and Phase 3 gate.
**Dependencies:** `index.json` (to enumerate all specs), spec.json files

### Component 6: Phase 3 Dependency Gate

**Responsibility:** Block Phase 3 when required dependencies are incomplete
**Interface:** For each required entry: READ_FILE dependency's spec.json, verify status=completed. Not completed → STOP. For advisory entries: warn and continue.
**Dependencies:** `core/dispatcher.md` (check 8), `core/workflow.md` (Phase 3 step 1)

### Component 7: Initiative Orchestrator

**Responsibility:** Autonomous execution of multi-spec initiatives
**Interface:** New `initiative` mode, registered in mode-manifest.json with modules: ["initiative-orchestration", "config-handling", "safety", "memory"]
**Dependencies:** `core/dispatcher.md` (mode routing), initiative.json, spec.json files

### Component 8: Phase Dispatch

**Responsibility:** Execute Phase 3 and Phase 4 in fresh sub-agent contexts
**Interface:** Phase dispatch gates after Phase 2 step 6.7 and Phase 3 step 8
**Dependencies:** `core/workflow.md`, platform capability flag `canDelegateTask`

## Data Model Changes

### New Schema: initiative-schema.json

```text
initiative.json:
  - id: string (required, pattern ^[a-zA-Z0-9._-]+$)
  - title: string (required, maxLength 200)
  - description: string (optional, maxLength 2000)
  - created: string (required, ISO 8601)
  - updated: string (required, ISO 8601)
  - author: string (required, maxLength 100)
  - specs: array of string (required, maxItems 50)
  - order: array of array of string (required, maxItems 20, inner maxItems 50)
  - skeleton: string (optional, maxLength 100)
  - status: enum active|completed (required)
```

### Modified Schema: spec-schema.json

```text
spec.json:
  + partOf: string (optional, maxLength 100, pattern ^[a-zA-Z0-9._-]+$)
  + relatedSpecs: array of string (optional, maxItems 20)
  + specDependencies: array of object (optional, maxItems 50)
    - specId: string (required)
    - reason: string (required, maxLength 500)
    - required: boolean (optional)
    - contractRef: string (optional, maxLength 200)
```

### Modified Schema: index-schema.json

```text
index entry:
  + partOf: string (optional, maxLength 100)
```

## Sequence Diagrams

### Flow 1: Scope Assessment and Decomposition

```text
User -> Dispatcher: Large feature request
Dispatcher -> Workflow: Phase 1 (Understand)
Workflow -> Decomposition: Phase 1.5 Scope Assessment
Decomposition -> User: Propose decomposition (names, order, rationale)
User -> Decomposition: Approve / Decline
Decomposition -> FileSystem: Create initiative.json
Decomposition -> Workflow: Continue with first spec → Phase 2
```

### Flow 2: Initiative Orchestration

```text
User -> Dispatcher: "initiative <id>"
Dispatcher -> Orchestrator: Route to initiative mode
Orchestrator -> FileSystem: Read initiative.json
Orchestrator -> Orchestrator: Compute waves, find next spec
Orchestrator -> Orchestrator: Build Handoff Bundle
Orchestrator -> Dispatcher: Dispatch spec (fresh sub-agent)
SubAgent -> Workflow: Full Phase 1-4 lifecycle
SubAgent -> FileSystem: Update spec.json (completed)
Orchestrator -> FileSystem: Update initiative.json, log to initiative-log.md
Orchestrator -> Orchestrator: Repeat until all specs done
```

### Flow 3: Phase Dispatch (Single Spec)

```text
Workflow -> Phase2: Execute Phase 2
Phase2 -> FileSystem: Write Phase 2 Completion Summary to implementation.md
Phase2 -> Dispatcher: Signal fresh Phase 3 sub-agent
Dispatcher -> SubAgent: Phase 3 Handoff Bundle (spec name, artifact paths, summaries)
SubAgent -> Phase3: Execute Phase 3 (Implementation)
Phase3 -> FileSystem: Write Phase 3 Completion Summary
Phase3 -> Dispatcher: Signal fresh Phase 4 sub-agent
Dispatcher -> SubAgent: Phase 4 Handoff Bundle (spec name, artifact paths, implementation.md)
SubAgent -> Phase4: Execute Phase 4 (Completion)
```

### Flow 4: Dependency Gate (Phase 3)

```text
Workflow -> DependencyGate: Phase 3 entry
DependencyGate -> FileSystem: Read spec.json specDependencies
DependencyGate -> FileSystem: Read each dependency's spec.json
DependencyGate -> CycleDetection: DFS with coloring
CycleDetection -> DependencyGate: No cycles (or STOP if cycle found)
DependencyGate -> DependencyGate: Check required deps completed
DependencyGate -> Workflow: PASS (all met) or STOP (unmet required dep)
```

## Security Considerations

- Path construction: Initiative IDs use same pattern as spec IDs (`^[a-zA-Z0-9._-]+$`), preventing path traversal
- All initiative paths constructed under `<specsDir>/initiatives/`
- READ_FILE on user-supplied paths: validate relative path, containment under repo root, absence of `../` traversal sequences
- initiative.json reviewed for well-formedness before execution

## Testing Strategy

- Unit tests: `tests/test_spec_schema.py` — partOf, relatedSpecs, specDependencies validation
- Unit tests: `tests/test_initiative_schema.py` (new) — initiative schema well-formedness, valid/invalid initiatives
- Integration tests: `tests/test_platform_consistency.py` — DECOMPOSITION_MARKERS present across platforms
- Validation: `generator/validate.py` — DECOMPOSITION_MARKERS and INITIATIVE_MARKERS in both validate_platform() and cross-platform loop

## Risks & Mitigations

- **Risk 1:** Scope assessment produces false positives (proposes splitting for simple features) → **Mitigation:** Propose-only design — user always decides. Complexity signals require multiple indicators, not just one.
- **Risk 2:** Cycle detection performance on large dependency graphs → **Mitigation:** DFS with coloring is O(V+E), negligible for realistic spec counts (<50 specs).
- **Risk 3:** Phase dispatch handoff bundles miss critical context → **Mitigation:** Bundles include file paths (not full content), sub-agent reads on demand. Phase summaries capture key decisions.
- **Risk 4:** Initiative orchestrator loses track of state on crash → **Mitigation:** All state is file-based. Orchestrator reads from disk on every iteration. Can resume from any point.

## Future Enhancements

- Dependency graph visualization (CLI or web)
- Cross-repository initiative tracking
- Parallel spec execution within a wave (when platform supports multiple sub-agents)
- Initiative templates for common decomposition patterns
- Automatic dependency inference from file overlap analysis

## Platform Adaptation

| Platform | canDelegateTask | Phase Dispatch | Initiative Orchestration |
|----------|-----------------|---------------|------------------------|
| Claude | true | Full sub-agent dispatch per phase | Full sub-agent dispatch per spec |
| Cursor | false | Checkpoint + prompt user for new session | Checkpoint + prompt |
| Codex | false | Enhanced sequential with phase summaries | Enhanced sequential |
| Copilot | false | Checkpoint + prompt | Checkpoint + prompt |
