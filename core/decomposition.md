## Spec Decomposition

Spec Decomposition provides multi-spec intelligence: automatic scope assessment, split detection, an initiative data model for tracking related specs, cross-spec dependencies with enforcement, cycle detection, dependency gates, scope hammering for blocker resolution, and the walking skeleton principle. All behavior is always-on — no configuration flag to enable or disable.

### 1. Scope Assessment Gate (Phase 1.5)

After Phase 1 step 9 (context summary), before Phase 2, run the Scope Assessment Gate. This gate is always-on and runs unconditionally for every spec.

**Complexity signals** — check the user's feature request for the following indicators:

| Signal | Detection Method |
| --- | --- |
| Independent deliverables | 2+ distinct functional units that could ship separately |
| Distinct code domains | >2 separate code areas (e.g., API + UI + database) |
| Language signals | Phrases like "and also", "plus", "additionally", "as well as" joining unrelated capabilities |
| Estimated task count | >8-10 tasks estimated from the request scope |
| Independent criteria clusters | Acceptance criteria that group into separable clusters with no cross-references |

**Assessment procedure:**

1. Evaluate the feature request against all 5 complexity signals.
2. If 2 or more signals are present, decomposition is recommended.
3. If fewer than 2 signals are present, proceed as a single spec — no decomposition needed.

**When decomposition is recommended:**

1. Build a decomposition proposal with the following fields for each proposed spec:

| Field | Description |
| --- | --- |
| Name | Descriptive spec identifier (kebab-case) |
| Description | 1-2 sentence summary of scope |
| Estimated tasks | Rough count (S: 1-3, M: 4-6, L: 7-10) |
| Execution order | Which wave this spec belongs to (wave 1 = no dependencies, wave 2 = depends on wave 1, etc.) |
| Dependency rationale | Why this spec depends on or is independent of others |

1. If `canAskInteractive` is true: ASK_USER("This feature request has multiple independent components. I recommend splitting into {N} specs:\n\n{proposal table}\n\nApprove decomposition? (yes/no/modify)")
   - If approved: proceed to initiative creation (step 3).
   - If declined: proceed as a single spec — continue to Phase 2.
   - If modified: adjust the proposal per user feedback and re-present.

2. If `canAskInteractive` is false: NOTIFY_USER("Scope assessment detected {N} independent components. Proceeding as a single spec in non-interactive mode. Consider splitting manually:\n\n{proposal table}") and continue to Phase 2 as a single spec.

**When decomposition is approved (interactive mode):**

1. Create the initiative:
   - Generate an initiative ID from the feature name (kebab-case, matching pattern `^[a-zA-Z0-9._-]+$`).
   - Compute execution waves from the proposed dependency rationale (see section 7: Initiative Order Derivation).
   - Identify the walking skeleton (see section 9: Walking Skeleton Principle).
   - RUN_COMMAND(`mkdir -p <specsDir>/initiatives`)
   - RUN_COMMAND(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) to capture the current timestamp.
   - WRITE_FILE(`<specsDir>/initiatives/<initiative-id>.json`) with the initiative data model (see section 3).
   - NOTIFY_USER("Created initiative '{initiative-id}' with {N} specs in {W} execution waves.")

2. Continue with the first spec (wave 1, walking skeleton) — proceed to Phase 2. The current spec's `partOf` field in spec.json will be set to the initiative ID during Phase 2 step 3.

### 2. Split Detection (Phase 2 Safety Net)

After Phase 2 step 1 (requirements drafting), if Phase 1.5 did NOT recommend decomposition, run a second-pass split detection as a safety net.

**Procedure:**

1. Review the drafted requirements for criteria clustering:
   - Group acceptance criteria by functional area.
   - If criteria cluster into 2+ independent groups (groups with no cross-references between them), decomposition may have been missed.

2. If independent clusters are detected:
   - Follow the same proposal format as Phase 1.5 (step 4).
   - Follow the same interactive/non-interactive decision flow as Phase 1.5 (steps 5-6).
   - If approved: create the initiative (Phase 1.5 step 7) and continue with the current spec as the first spec in the initiative.

3. If no independent clusters are detected, continue with Phase 2 as normal.

This check fires only when Phase 1.5 did not trigger (either because signals were below threshold or because the user declined). It does not run if decomposition was already approved.

### 3. Initiative Data Model

An initiative groups related specs created through decomposition (or manually) into a tracked unit with execution ordering.

**Location:** `<specsDir>/initiatives/<initiative-id>.json`

**Fields:**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | Yes | Initiative identifier, pattern `^[a-zA-Z0-9._-]+$` |
| `title` | string | Yes | Human-readable title (maxLength 200) |
| `description` | string | No | Detailed description (maxLength 2000) |
| `created` | string | Yes | ISO 8601 timestamp of creation |
| `updated` | string | Yes | ISO 8601 timestamp of last modification |
| `author` | string | Yes | Author name (maxLength 100) |
| `specs` | string[] | Yes | Array of spec IDs belonging to this initiative (maxItems 50) |
| `order` | string[][] | Yes | Execution waves — array of arrays where each inner array is a wave of spec IDs that can execute in parallel (maxItems 20 waves, inner maxItems 50) |
| `skeleton` | string | No | Spec ID of the walking skeleton (first wave-1 spec) |
| `status` | string | Yes | `active` or `completed` — derived from member spec statuses |

**Schema:** Validated against `initiative-schema.json` (draft-07, `additionalProperties: false` at all object levels).

**Status derivation:**

- `active`: At least one member spec has `status` other than `completed`.
- `completed`: All member specs have `status == "completed"`.

Status is recomputed whenever a member spec's status changes (Phase 4 step 6.3).

### 4. Cross-Spec Dependencies

Cross-spec dependencies declare explicit relationships between specs, enabling enforcement of execution ordering and blocker tracking.

**Declaration format in spec.json:**

The `specDependencies` array (optional, maxItems 50) contains dependency entries:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `specId` | string | Yes | ID of the dependency spec (maxLength 100, pattern `^[a-zA-Z0-9._-]+$`) |
| `reason` | string | Yes | Why this spec depends on the other (maxLength 500) |
| `required` | boolean | No | If `true`, this is a hard dependency — Phase 3 is blocked until the dependency is completed. If `false` or omitted, this is an advisory dependency — a warning is shown but Phase 3 proceeds. |
| `contractRef` | string | No | Path to an interface contract or shared artifact (maxLength 200) |

**Population:** During Phase 2 step 3, when writing spec.json:

- If the spec belongs to an initiative (`partOf` is set), populate `specDependencies` based on the initiative's execution wave ordering — specs in wave N depend on specs in wave N-1.
- The `relatedSpecs` array (optional, maxItems 20) lists informational references to specs that are related but not dependencies (see section 10: Cross-Linking).
- Run cycle detection (section 5) before writing spec.json. If a cycle is detected, do not write and STOP with the cycle chain.

### 5. Cycle Detection

Cycle detection prevents circular dependencies across specs. It uses depth-first search (DFS) with three-color marking (white/gray/black).

**Algorithm:**

1. READ_FILE(`<specsDir>/index.json`) to enumerate all specs. For each spec, if FILE_EXISTS(`<specsDir>/<spec-id>/spec.json`), READ_FILE it to get its `specDependencies` array.

2. Build an adjacency list: for each spec with `specDependencies`, create edges from the spec to each `specId` in its dependencies.

3. Initialize all nodes as white (unvisited).

4. For each white node, run DFS:
   - Mark node gray (in progress).
   - For each neighbor (dependency):
     - If gray: cycle detected — record the cycle chain from the current node back through the gray nodes.
     - If white: recurse.
   - Mark node black (completed).

5. If any cycle is detected:
   - NOTIFY_USER("Circular dependency detected: {cycle chain, e.g., spec-a → spec-b → spec-c → spec-a}. Resolve by removing or making one dependency advisory (required: false).")
   - STOP — do not proceed. Circular dependencies are a protocol breach.

6. If no cycles: continue.

**When cycle detection runs:**

- Phase 2 step 3: Before writing `specDependencies` to spec.json.
- Phase 3 step 1: As part of the dependency gate (section 7).
- Reconciliation: Check 6 (Dependency Health).

### 6. Initiative Order Derivation

Execution waves are derived from the dependency graph via topological sort.

**Algorithm:**

1. Build the dependency graph from all specs in the initiative:
   - For each spec in `initiative.specs`, read its `specDependencies` from spec.json.
   - Only consider dependencies where the `specId` is also in `initiative.specs` (ignore external dependencies for wave ordering).

2. Topological sort with wave assignment:
   - Wave 1: All specs with no intra-initiative dependencies.
   - Wave N: All specs whose intra-initiative dependencies are all in waves 1 through N-1.

3. Run cycle detection (section 5) on the intra-initiative graph. If a cycle is detected, STOP.

4. Write the computed waves to `initiative.order` as an array of arrays.

5. Update `initiative.updated` timestamp: RUN_COMMAND(`date -u +"%Y-%m-%dT%H:%M:%SZ"`).

6. WRITE_FILE(`<specsDir>/initiatives/<initiative-id>.json`) with the updated order.

**Recomputation trigger:** Whenever `specDependencies` change for any spec in the initiative (Phase 2 step 3 writes, reconciliation updates, manual edits).

### 7. Phase 3 Dependency Gate

At Phase 3 step 1, before any implementation work begins, run the dependency gate. This gate is mandatory — skipping it is a protocol breach.

**Procedure:**

1. READ_FILE(`<specsDir>/<spec-name>/spec.json`) to get `specDependencies`.

2. If `specDependencies` is absent or empty, the gate passes — proceed to implementation.

3. For each entry in `specDependencies`:
   a. READ_FILE(`<specsDir>/<entry.specId>/spec.json`) to get the dependency's status.
   b. If the dependency spec.json does not exist: NOTIFY_USER("Warning: Dependency '{entry.specId}' not found. Treating as unmet.") and treat as unmet.

4. **Required dependencies** (`required: true`):
   - If any required dependency has `status` other than `completed`: STOP.
   - NOTIFY_USER("Phase 3 BLOCKED: Required dependency '{entry.specId}' has status '{status}'. Cannot proceed until it is completed.")
   - Present scope hammering options (section 8).

5. **Advisory dependencies** (`required: false` or `required` omitted):
   - If an advisory dependency is not completed: NOTIFY_USER("Advisory: Dependency '{entry.specId}' is not yet completed (status: {status}). Proceeding with implementation, but be aware of potential integration issues.")
   - Continue — advisory dependencies do not block.

6. Run cycle detection (section 5) as a safety net — even if cycles were checked at write time, re-verify before implementation.

7. If all required dependencies are completed (or no required dependencies exist), the gate passes — proceed to implementation.

### 8. Scope Hammering

When a spec encounters a dependency blocker (Phase 3 dependency gate fails), present structured resolution options instead of indefinite waiting.

**Options:**

| Option | Resolution Type | Description |
| --- | --- | --- |
| Cut scope | `scope_cut` | Remove the blocked functionality from this spec. Update requirements and tasks to exclude the dependent feature. |
| Define interface contract | `interface_defined` | Define the expected interface or contract for the dependency, create a stub implementation, and proceed. Record the contract path in `contractRef`. |
| Wait | `deferred` | Defer this spec until the dependency completes. Do not proceed to Phase 3. |
| Escalate | `escalated` | Flag the blocker for human decision. Record the escalation in the blockers table. |

**Procedure:**

1. If `canAskInteractive` is true: ASK_USER("Dependency '{entry.specId}' is blocking Phase 3. Options:\n1. Cut scope — remove dependent functionality\n2. Define interface — create contract + stub, proceed\n3. Wait — defer until dependency completes\n4. Escalate — flag for human decision\n\nChoose an option:")

2. If `canAskInteractive` is false: NOTIFY_USER("Dependency '{entry.specId}' is blocking Phase 3. Deferring until dependency completes.") and use `deferred` as the resolution type.

3. Record the resolution in the Cross-Spec Blockers table in the spec's `tasks.md` (and `requirements.md` / `design.md` if present):

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| --- | --- | --- | --- | --- |
| {description} | {specId} | {scope_cut/interface_defined/deferred/escalated} | {detail} | {open/resolved} |

1. If `scope_cut`: Update requirements.md and tasks.md to remove the blocked functionality. Proceed to Phase 3 with reduced scope.
2. If `interface_defined`: WRITE_FILE the interface contract, update `contractRef` in the specDependency entry, proceed to Phase 3 with stub implementation.
3. If `deferred`: Do not proceed to Phase 3. The spec remains in its current status until the dependency completes.
4. If `escalated`: Do not proceed to Phase 3. NOTIFY_USER("Blocker escalated. Awaiting human decision.")

### 9. Walking Skeleton Principle

When an initiative is created, the first spec in wave 1 is designated as the walking skeleton.

**Purpose:** The walking skeleton establishes an end-to-end integration path across all architectural layers touched by the initiative. Subsequent specs build on this proven foundation.

**Designation:**

1. From the initiative's execution waves (section 6), identify wave 1 specs.
2. If wave 1 has a single spec, it is the skeleton.
3. If wave 1 has multiple specs, select the one that touches the most architectural layers (based on the decomposition proposal's domain analysis).
4. Record the skeleton spec ID in `initiative.skeleton`.

**Skeleton spec guidance:**

- The skeleton spec should prioritize breadth over depth — it establishes the integration path, not full feature implementation.
- During Phase 2 of the skeleton spec, include a requirement that the implementation proves the end-to-end path works (e.g., data flows from input to output through all layers).
- NOTIFY_USER("Spec '{skeleton-id}' is the walking skeleton for initiative '{initiative-id}'. It should establish the end-to-end integration path.")

### 10. Cross-Linking

The `relatedSpecs` array in spec.json provides informational cross-references between specs.

**Format:** Array of spec ID strings (maxItems 20, each maxLength 100, pattern `^[a-zA-Z0-9._-]+$`).

**Population:** During Phase 2 step 3, populate `relatedSpecs` with:

- Other specs in the same initiative (if `partOf` is set).
- Specs that modify overlapping files (detected from memory patterns if available).
- Specs explicitly mentioned in the feature request.

**Usage:** `relatedSpecs` is informational only — it does not affect execution ordering or gates. It appears in spec view output (core/view.md) and audit reports (core/reconciliation.md) to help developers understand the broader context.

### Platform Adaptation

| Capability | Impact |
| --- | --- |
| `canAskInteractive: true` | Full interactive decomposition approval, scope hammering options presented as choices |
| `canAskInteractive: false` | Decomposition notified but not applied (proceed as single spec). Scope hammering defaults to `deferred`. |
| `canExecuteCode: true` (all platforms) | Shell commands available for `mkdir -p`, `date`, cycle detection graph traversal via file reads |
| `canTrackProgress: false` | Report decomposition and dependency status in response text |
| `canDelegateTask: true` | Initiative orchestrator can dispatch specs as fresh sub-agents (see core/initiative-orchestration.md) |
| `canDelegateTask: false` | Initiative specs executed sequentially or via checkpoint+prompt |
