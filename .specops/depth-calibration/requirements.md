# Depth Calibration System

## Overview

SpecOps runs the same full ceremony for a 2-task typo fix as for a 20-task cross-domain initiative. This wastes context budget, developer time, and causes small-spec abandonment. The depth calibration system adds complexity assessment to Phase 1 that sets a `lightweight` / `standard` / `deep` flag. Workflow steps conditionally skip, compress, or expand based on this flag.

## Product Requirements

### FR-1: Complexity Assessment in Phase 1

<!-- EARS: Event-Driven -->
WHEN Phase 1 completes step 9.5 (Scope Assessment), THE SYSTEM SHALL assess complexity using three signals: estimated task count, file domain breadth (number of distinct directories modified), and presence of new dependencies. THE SYSTEM SHALL compute a depth flag from these signals.

**Acceptance Criteria:**
- [x] Task count <= 2 AND single directory domain AND no new dependencies = `lightweight`
- [x] Task count 3-8 AND multiple directories but within a single code domain = `standard`
- [x] Task count > 8 OR cross-domain (e.g., core + generator + tests) OR new external dependencies = `deep`
- [x] Depth flag is recorded in `implementation.md` Phase 1 Context Summary
- [x] Depth flag is persisted to `spec.json` as `depth` field

### FR-2: Conditional Step Behavior

<!-- EARS: State-Driven -->
WHILE the depth flag is `lightweight`, THE SYSTEM SHALL skip repo map refresh (use existing if available), skip scope assessment iteration, skip spec evaluation, limit implementation evaluation to acceptance criteria verification only, and skip the dependency introduction gate when no new dependencies are detected.

<!-- EARS: State-Driven -->
WHILE the depth flag is `standard`, THE SYSTEM SHALL use the repo map if it exists without forcing a refresh, run scope assessment normally, run spec evaluation for 1 iteration maximum, run full 4-dimension implementation evaluation, and run the dependency introduction gate normally.

<!-- EARS: State-Driven -->
WHILE the depth flag is `deep`, THE SYSTEM SHALL force a repo map refresh, run scope assessment with initiative decomposition check, run spec evaluation up to maxIterations, run full implementation evaluation with per-task granularity if task count > 5, and run the dependency introduction gate with extended analysis.

**Acceptance Criteria:**
- [x] Lightweight specs skip repo map refresh (step 3.5 uses existing map if available)
- [x] Lightweight specs skip scope assessment (step 9.5 passes trivially)
- [x] Lightweight specs skip spec evaluation (step 6.85 passes trivially)
- [x] Lightweight specs limit Phase 4A to acceptance criteria check only
- [x] Standard specs behave identically to current workflow (backward compatible)
- [x] Deep specs force repo map refresh
- [x] Deep specs run full evaluation iterations

### FR-3: Depth Override

<!-- EARS: Optional Feature -->
WHERE the user provides an explicit depth flag in their request (e.g., "lightweight", "quick", "deep dive", "thorough"), THE SYSTEM SHALL use the user-specified depth instead of the computed depth and record the override in `implementation.md`.

**Acceptance Criteria:**
- [x] "quick" or "lightweight" in user request forces `lightweight` depth
- [x] "thorough" or "deep" or "deep dive" in user request forces `deep` depth
- [x] Override is recorded as `- Depth: <flag> (user override)` in Context Summary

### FR-4: Dispatcher Integration

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL include the depth flag in the dispatcher's Shared Context Block so that the dispatched spec mode receives the depth context.

**Acceptance Criteria:**
- [x] `core/dispatcher.md` passes the depth flag to the dispatched mode
- [x] Depth flag is available at Phase 3 and Phase 4 entry points

## Non-Functional Requirements

- **NFR-1**: The complexity assessment adds no user-visible latency -- it uses data already collected during Phase 1 (task count estimate from request analysis, affected files from step 9).
- **NFR-2**: Standard depth must be bit-for-bit backward compatible with the current workflow behavior. No existing spec behavior changes.
- **NFR-3**: The depth flag must use abstract operations only in `core/workflow.md` (no platform-specific tool names).

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
