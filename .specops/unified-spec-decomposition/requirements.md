# Feature: Unified Spec Decomposition + Cross-Spec Dependencies + Initiative Orchestration + Phase Dispatch

## Overview

SpecOps currently treats specs as isolated, flat units. When a user brings a large request, SpecOps creates one monolithic spec with no intelligence to decompose work into multiple right-sized specs, no way to track relationships between specs, and no enforcement of execution ordering. This feature adds multi-spec intelligence: scope assessment, split detection, an initiative data model, cross-spec dependencies with enforcement, autonomous initiative orchestration, and single-spec phase dispatch for fresh-context execution.

Key design decisions from the plan:
- **Always-on, no config flag** — Scope assessment, dependency enforcement, and blocker tracking are core workflow behavior, not optional features.
- **Two modules, distinct concerns** — `core/decomposition.md` (scope assessment, split detection, initiative data model) and `core/initiative-orchestration.md` (autonomous execution of multi-spec initiatives).
- **Any-to-any dependencies** — `specDependencies` works regardless of initiative membership.
- **Structured blockers** — Resolution types (scope_cut, interface_defined, completed, escalated, deferred) enable automated tracking.
- **Propose-only decomposition** — Agent recommends splitting, user decides. Specs created one-at-a-time via normal workflow.
- **Fresh context everywhere** — Initiative orchestrator dispatches each spec as a fresh sub-agent. Phase dispatch ensures Phase 3 and Phase 4 get fresh contexts.
- **File-based state, no in-memory accumulation** — Orchestrator reads all state from disk. Can restart at any point.

## User Stories

### Story 1: Automatic Scope Assessment

**As a** developer using SpecOps
**I want** the system to automatically assess whether my feature request should be split into multiple specs
**So that** large monolithic specs are prevented before they start

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven and State-Driven patterns -->
- WHEN a user begins Phase 1 and complexity signals are detected (>2 independent deliverables, >2 distinct code domains, estimated >8-10 tasks, independent acceptance criteria clusters) THE SYSTEM SHALL propose decomposition with spec names, descriptions, task estimates, execution order, and dependency rationale
- WHEN the system is in interactive mode THE SYSTEM SHALL ASK_USER for decomposition approval before proceeding
- WHEN the system is in non-interactive mode THE SYSTEM SHALL NOTIFY_USER and proceed as a single spec
- WHEN the user approves decomposition THE SYSTEM SHALL create an `initiative.json` file, populate the first spec's `specDependencies`, and proceed to Phase 2

**Progress Checklist:**

- [ ] Phase 1.5 Scope Assessment Gate triggers on complexity signals
- [ ] Interactive mode prompts user for approval
- [ ] Non-interactive mode notifies and proceeds
- [ ] Approved decomposition creates initiative.json and populates specDependencies

### Story 2: Split Detection Safety Net

**As a** developer
**I want** a second-pass split detection after requirements drafting in Phase 2
**So that** decomposition opportunities missed in Phase 1.5 are caught

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven -->
- WHEN Phase 2 requirements are drafted AND Phase 1.5 did not trigger THE SYSTEM SHALL check if criteria cluster into independent groups and propose splitting
- WHEN splitting is proposed THE SYSTEM SHALL follow the same approval/decision flow as Phase 1.5

**Progress Checklist:**

- [ ] Phase 2 split detection fires only when Phase 1.5 did not trigger
- [ ] Same proposal/decision flow as Phase 1.5

### Story 3: Initiative Data Model

**As a** developer managing multi-spec features
**I want** an initiative data model that tracks related specs and their execution order
**So that** I can see the big picture and track progress across specs

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven and Ubiquitous -->
- WHEN an initiative is created THE SYSTEM SHALL store it at `<specsDir>/initiatives/<id>.json` with fields: id, title, description, created, updated, author, specs[], order[][] (execution waves from DAG), skeleton (walking skeleton spec ID), status (active|completed, derived)
- THE SYSTEM SHALL validate initiative.json against `initiative-schema.json`
- WHEN specDependencies change THE SYSTEM SHALL recompute execution waves via topological sort

**Progress Checklist:**

- [ ] initiative.json created at correct location with all fields
- [ ] initiative-schema.json validates initiative structure
- [ ] Execution waves recomputed on dependency changes

### Story 4: Cross-Spec Dependencies

**As a** developer working on interdependent specs
**I want** explicit dependency declarations between specs with enforcement
**So that** implementation order is enforced and dependency violations are prevented

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven, State-Driven, Unwanted -->
- WHEN a spec is created with `specDependencies` containing `required: true` entries THE SYSTEM SHALL block Phase 3 until all required dependencies have status=completed
- WHEN a spec has `required: false` dependency entries THE SYSTEM SHALL NOTIFY_USER with a warning and continue
- WHEN a cycle is detected in specDependencies (via DFS with white/gray/black coloring) THE SYSTEM SHALL NOTIFY_USER with the cycle chain and refuse to write or proceed
- IF a spec attempts to enter Phase 3 with unmet required dependencies THEN THE SYSTEM SHALL STOP with a protocol breach

**Progress Checklist:**

- [ ] specDependencies array in spec.json with specId, reason, required, contractRef fields
- [ ] Phase 3 dependency gate blocks on unmet required deps
- [ ] Advisory warnings for non-required deps
- [ ] Cycle detection prevents circular dependencies
- [ ] Protocol breach on Phase 3 with unmet deps

### Story 5: Scope Hammering on Blockers

**As a** developer whose spec hits a dependency blocker
**I want** structured resolution options instead of indefinite waiting
**So that** work continues to progress even when dependencies are incomplete

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven -->
- WHEN a spec encounters a dependency blocker THE SYSTEM SHALL present scope hammering options: cut scope, define interface contract + proceed with stub, wait, or escalate
- WHEN a resolution is chosen THE SYSTEM SHALL record it in the Cross-Spec Blockers table with a resolution type (scope_cut, interface_defined, completed, escalated, deferred)

**Progress Checklist:**

- [ ] Scope hammering options presented on blocker
- [ ] Resolution recorded with structured type

### Story 6: Walking Skeleton Principle

**As a** developer starting a multi-spec initiative
**I want** the first spec to establish an end-to-end integration path
**So that** subsequent specs can build on a proven architectural foundation

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven -->
- WHEN an initiative is created THE SYSTEM SHALL flag the first spec in wave 1 as the walking skeleton in initiative.json
- THE SYSTEM SHALL ensure the skeleton establishes the end-to-end integration path across all architectural layers

**Progress Checklist:**

- [ ] First wave-1 spec flagged as skeleton in initiative.json
- [ ] Skeleton covers end-to-end integration path

### Story 7: Initiative Orchestration

**As a** developer running a multi-spec initiative
**I want** autonomous orchestration that dispatches specs through the normal workflow with fresh contexts
**So that** each spec gets full context window and initiative progress is tracked automatically

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven, State-Driven -->
- WHEN the initiative mode is invoked THE SYSTEM SHALL read initiative.json, compute execution waves, identify the current wave, and select the next pending spec with all dependencies completed
- WHEN dispatching a spec THE SYSTEM SHALL build an Initiative Handoff Bundle (initiative context, spec identity, dependency context from completed deps, scope constraints) and dispatch through the normal dispatcher protocol as a fresh sub-agent
- WHEN a sub-agent completes THE SYSTEM SHALL verify completion via spec.json, update initiative.json, log to initiative-log.md, and check wave completion
- WHEN a sub-agent is blocked THE SYSTEM SHALL apply the Scope Hammering Protocol
- WHILE all specs in the initiative are completed THE SYSTEM SHALL mark the initiative as completed

**Progress Checklist:**

- [ ] Orchestrator reads state from disk (file-based, no in-memory accumulation)
- [ ] Handoff bundles contain initiative context, spec identity, dependency context, scope constraints
- [ ] Dispatch through normal dispatcher as fresh sub-agent
- [ ] Completion verification and initiative.json update
- [ ] initiative-log.md chronological execution log
- [ ] Scope Hammering Protocol on blockers

### Story 8: Single-Spec Phase Dispatch

**As a** developer working on a spec
**I want** Phase 3 and Phase 4 to execute in fresh contexts
**So that** each phase gets maximum context window instead of accumulating stale context

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven -->
- WHEN Phase 2 completes THE SYSTEM SHALL checkpoint to implementation.md and dispatch Phase 3 as a fresh sub-agent with a Phase 3 handoff bundle (spec name, artifact paths, Phase 1 Context Summary, Phase 2 Completion Summary, config)
- WHEN Phase 3 completes THE SYSTEM SHALL dispatch Phase 4 as a fresh sub-agent with a Phase 4 handoff bundle (spec name, artifact paths, implementation.md content, config)
- WHEN phase dispatch is available (canDelegateTask = true) THE SYSTEM SHALL use full sub-agent dispatch; otherwise THE SYSTEM SHALL checkpoint and prompt the user for a new session

**Progress Checklist:**

- [ ] Phase 2 → Phase 3 dispatch with handoff bundle
- [ ] Phase 3 → Phase 4 dispatch with handoff bundle
- [ ] Platform adaptation (sub-agent, checkpoint+prompt, sequential)

### Story 9: Task Delegation Threshold Adjustment

**As a** developer
**I want** task delegation to activate more aggressively at a lower threshold
**So that** more specs benefit from fresh-context task execution

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven, Optional -->
- THE SYSTEM SHALL lower the auto-activation threshold from score 6 to score 4
- WHERE `config.implementation.delegationThreshold` is set THE SYSTEM SHALL use the configured value instead of the default

**Progress Checklist:**

- [ ] Default threshold lowered from 6 to 4
- [ ] Configurable via delegationThreshold

### Story 10: Template Dependencies & Blockers Sections

**As a** developer working on specs with dependencies
**I want** all spec templates to include Dependencies & Blockers sections
**So that** dependency tracking and blocker resolution are visible in spec artifacts

**Acceptance Criteria (EARS):**
<!-- EARS: Ubiquitous -->
- THE SYSTEM SHALL include a "Dependencies & Blockers" section in all five templates (feature-requirements.md, design.md, bugfix.md, refactor.md, tasks.md) with Spec Dependencies table and Cross-Spec Blockers table
- THE SYSTEM SHALL use structured resolution types: scope_cut, interface_defined, completed, escalated, deferred

**Progress Checklist:**

- [ ] Dependencies & Blockers section in feature-requirements.md
- [ ] Dependencies & Blockers section in design.md
- [ ] Dependencies & Blockers section in bugfix.md
- [ ] Dependencies & Blockers section in refactor.md
- [ ] Spec-Level Dependencies and Dependency Resolution Log in tasks.md

## Non-Functional Requirements

- Performance: Scope assessment and cycle detection must complete within normal Phase 1 execution time (no external API calls, pure file-based logic)
- Security: Initiative IDs use same `^[a-zA-Z0-9._-]+$` pattern as spec IDs (prevents path traversal). All paths constructed under `<specsDir>/initiatives/`
- Backward Compatibility: All new spec.json fields (partOf, relatedSpecs, specDependencies) are optional. Existing specs validate against updated schemas without changes.

## Constraints & Assumptions

- Scope assessment and split detection are always-on — no config flag to disable
- Decomposition is propose-only — agent recommends, user decides
- Specs within an initiative are created one-at-a-time via normal workflow
- `core/decomposition.md` and `core/initiative-orchestration.md` are separate modules with distinct concerns
- Phase dispatch (fresh context per phase) only works on platforms with `canDelegateTask = true`
- Orchestrator state is entirely file-based — can restart at any point

## Dependencies & Blockers

### Spec Dependencies

| Dependent Spec | Reason | Required | Status |
|---|---|---|---|
| None | This is a foundational feature with no spec-level dependencies | — | — |

### Cross-Spec Blockers

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
|---|---|---|---|---|
| None | — | — | — | — |

## Success Metrics

- `python3 generator/generate.py --all` regenerates successfully
- `python3 generator/validate.py` passes all checks including DECOMPOSITION_MARKERS and INITIATIVE_MARKERS
- `bash scripts/run-tests.sh` passes including new initiative schema tests
- `python3 tests/check_schema_sync.py` schemas well-formed
- Generated outputs contain: "Scope Assessment", "specDependencies", "Dependency Gate", "initiative", "Cycle Detection", "Walking Skeleton", "Initiative Orchestration", "Phase Dispatch" in all 4 platforms
- Existing `.specops/` specs validate against updated schemas (backward compatibility)
- Pre-commit hook passes: JSON syntax, ShellCheck, stale files, checksums, markdown lint

## Out of Scope

- Runtime dependency graph visualization (UI/CLI tool)
- Automatic decomposition without user approval
- Cross-repository initiative tracking
- Initiative-level rollback or undo
- Real-time collaboration on initiatives

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
