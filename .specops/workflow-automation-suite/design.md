# Design: Workflow Automation Suite

## Architecture Overview

Four new `core/*.md` modules plug into the existing three-layer architecture (core → generator → platforms). Each module hooks into `core/workflow.md` at specific phase boundaries using sub-step notation (established pattern from 4 prior specs). No new abstract operations are needed — all features use existing `READ_FILE`, `WRITE_FILE`, `EDIT_FILE`, `FILE_EXISTS`, `RUN_COMMAND`, `ASK_USER`, `NOTIFY_USER`, `UPDATE_PROGRESS`.

## Technical Decisions

### Decision 1: Run Logging Complements Metrics (No Overlap)
**Context:** `core/metrics.md` already captures outcome data (7 numeric fields in spec.json). Run logging must avoid duplication.
**Decision:** Run logging captures process data (timestamped execution trace). Metrics captures outcome data (aggregate numbers). They share no fields. The run log stores entries chronologically; metrics stores a single summary object.
**Rationale:** Clear separation means neither feature needs to know about the other. Metrics doesn't read from the run log; run logging doesn't write to spec.json.

### Decision 2: Plan Validation in Phase 2 (Preventive, Not Post-hoc)
**Context:** Task delegation quality gates already check file existence after implementation (post-hoc). Where should plan validation run?
**Decision:** Phase 2 step 5.7 — after coherence verification (5.5) and vocabulary verification (5.6), before external issue creation (step 6).
**Rationale:** Catching bad references before Phase 3 saves wasted implementation effort. Post-hoc checks (delegation quality gates) remain as a second safety net. The repo map (loaded in Phase 1 step 3.5) is the primary lookup to avoid redundant FILE_EXISTS calls.

### Decision 3: Phase-Boundary Checkpoints (Not Per-Task)
**Context:** `autoCommit` already handles per-task commits (Phase 3 step 7). How should checkpointing differ?
**Decision:** Exactly 3 commits per spec run at phase boundaries. autoCommit and gitCheckpointing are non-conflicting — both can be enabled simultaneously.
**Rationale:** Phase-boundary commits capture semantic milestones (spec ready, code done, spec complete). Per-task commits capture implementation progress. Different granularities serve different rollback needs.

### Decision 4: Pipeline Config as Single Integer (Simplicity Principle)
**Context:** slop-janitor uses multiple knobs (cycles, improvements, review passes). Should SpecOps match that?
**Decision:** Single config value `pipelineMaxCycles` (integer, 1-10, default 3). No nested pipeline config object.
**Rationale:** `stopOnGreen` behavior is always on (the loop's entire purpose). `autoFixLint` defers to existing `linting.fixOnSave`. Review passes are handled by existing Phase 4 acceptance verification. One knob is sufficient.

### Decision 5: Zero-Progress Detection
**Context:** A pipeline could loop forever if the same criteria remain unmet across cycles.
**Decision:** Track unmet criteria set per cycle. If identical to the previous cycle's unmet set, stop early.
**Rationale:** Prevents infinite loops without requiring the user to set a low max cycle count. Complements the hard cap (maxCycles ≤ 10).

## Product Module Design

### Module 1: Run Logging (`core/run-logging.md`)
**Responsibility:** Capture per-step execution trace during the SpecOps workflow.
**Storage:** `<specsDir>/runs/<spec-name>-<YYYYMMDD-HHMMSS>.log.md`
**Interface:** Append-only EDIT_FILE operations at instrumented workflow points.

**Format:** Markdown with YAML frontmatter:
```yaml
---
specId: "<spec-name>"
startedAt: "ISO 8601"
completedAt: "ISO 8601 or null"
finalStatus: "completed | implementing | blocked | error"
phases: [1, 2, 3, 4]
---
```

**Log entry types (5):**
1. Phase transition: `## Phase N: <name>` with timestamp
2. Step execution: `### [HH:MM:SS] Step N: <description>` with Action/Result
3. Decision: `### [HH:MM:SS] Decision: <topic>` with choice and rationale
4. File operation: sub-bullets under steps (`- Read: <path>`, `- Write: <path>`)
5. Error/blocker: `### [HH:MM:SS] ERROR: <description>` with detail and recovery

**Naming edge case:** At Phase 1, spec name is unknown for new specs. Use `_pending-<timestamp>` then rename when spec name is determined in Phase 2.

**Delegation interaction:** Only the orchestrator writes to the run log. Delegates do NOT write — avoids contention.

### Module 2: Plan Validation (`core/plan-validation.md`)
**Responsibility:** Validate that file paths and code references in spec artifacts exist in the codebase before implementation.
**Trigger:** Phase 2 step 5.7, gated by `config.implementation.validateReferences`.

**Reference extraction:**
- `tasks.md`: file paths from `**Files to Modify:**` sections
- `design.md`: file paths from sections containing "Files" in heading + backtick-enclosed references

**Resolution strategy:**
1. Repo map first (loaded in Phase 1 step 3.5 as a steering file)
2. FILE_EXISTS fallback for paths not in the map
3. Prefix normalization (strip leading `./`)

**New-file heuristic:** Skip validation for paths whose task says "create", "add new file", or "scaffold".

**Outcomes:** Recorded in `implementation.md` Phase 1 Context Summary.

### Module 3: Git Checkpointing (`core/git-checkpointing.md`)
**Responsibility:** Commit at 3 phase boundaries during spec execution.
**Trigger:** `config.implementation.gitCheckpointing` (boolean) + platform `canAccessGit`.

**Checkpoint points:**
| Point | Trigger | Commit message | What's committed |
|-------|---------|---------------|-----------------|
| After Phase 2 step 6 | Spec artifacts created | `specops(checkpoint): spec-created -- <name>` | `<specsDir>/<spec-name>/` only |
| After Phase 3 tasks | All tasks done | `specops(checkpoint): implemented -- <name>` | `git add -A` |
| After Phase 4 step 6 | Status set to completed | `specops(checkpoint): completed -- <name>` | `git add -A` |

**Safety rules:**
- Dirty tree at start → disable for entire run (never mix user changes)
- Git failure → NOTIFY_USER and continue (non-blocking)
- Never force push, never amend
- Respect pre-commit/pre-push hooks

**autoCommit interaction:** Non-conflicting. autoCommit = per-task (Phase 3 step 7). Checkpointing = per-phase. If both on, autoCommit handles tasks; Phase 3 checkpoint may be empty (nothing new to commit) — skipped silently.

### Module 4: Pipeline Mode (`core/pipeline.md`)
**Responsibility:** Automate Phase 3 → Phase 4 acceptance cycling for existing specs.
**Trigger:** `/specops pipeline <spec-name>` (new subcommand detected in Getting Started step 11.7).

**Pipeline flow:**
```
prerequisites → [cycle: Phase 3 → acceptance check → pass? → finalize] | [fail → reset tasks → next cycle] | [max cycles → stop]
```

**Prerequisites:** Spec exists, status is draft/approved/self-approved/implementing, all spec files present.

**Integration points:**
- Run logging: writes `## Cycle N` sections per cycle
- Git checkpointing: "implemented" per cycle, "completed" once at end
- Task delegation: delegates within each cycle (existing protocol)
- Plan validation: runs once in Phase 2 (before pipeline), not per cycle
- Metrics: captured once at final completion

## System Flow

```
User invokes /specops pipeline <name>
  → Getting Started step 11.7: detect pipeline mode
  → Pipeline prerequisites check
  → Cycle loop:
      → Phase 3 (existing logic, with delegation if configured)
      → Git checkpoint: implemented (if enabled)
      → Phase 4 step 1: acceptance criteria check
      → All pass? → finalize (steps 2-8) → DONE
      → Unmet + cycles remain? → reset tasks → next cycle
      → Max cycles? → STOP with summary
```

## Integration Points

All 4 modules integrate through the same established pattern:
1. New `core/*.md` module using abstract operations
2. Entry in `build_common_context()` in `generator/generate.py` (~line 335)
3. `{{ variable }}` inclusion in all 4 `.j2` templates
4. Marker constants in `generator/validate.py` (BOTH `validate_platform()` AND cross-platform loop)
5. Marker category in `tests/test_platform_consistency.py`
6. Config option in `schema.json` under `implementation`

## Data Architecture

### New Config Options (`schema.json` under `implementation`)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `runLogging` | enum `["on","off"]` | `"on"` | Enable per-run execution logging |
| `validateReferences` | enum `["off","warn","strict"]` | `"off"` | Pre-implementation reference validation |
| `gitCheckpointing` | boolean | `false` | Phase-boundary git commits |
| `pipelineMaxCycles` | integer (1-10) | `3` | Max pipeline mode iterations |

### Run Log Files

Stored in `<specsDir>/runs/`, one file per workflow invocation. Markdown with YAML frontmatter. Append-only during execution. Not included in git checkpoint commits.

## Testing Strategy
- Schema validation: new config options pass validation
- Schema constraints: invalid values rejected (pipelineMaxCycles > 10, invalid enum)
- Platform consistency: 4 new marker categories present in all platforms
- Build tests: generator produces valid outputs with new modules
- Validator: all new markers present, no raw abstract ops

## Ship Plan
1. Implement run logging + git checkpointing (no cross-dependencies)
2. Implement plan validation (uses repo map, no feature deps)
3. Implement pipeline mode (orchestrates all three)
4. Regenerate all platform outputs, validate, test

## Risks & Mitigations
- **Risk:** workflow.md grows too large with 4 new hook points → **Mitigation:** Each hook is 1-2 lines referencing the module (established pattern from memory/steering/delegation)
- **Risk:** Pipeline mode re-entering Phase 3 with partial state → **Mitigation:** Pipeline resets unfinished tasks to Pending before each cycle, reusing existing task state machine
- **Risk:** Run log naming collision for concurrent runs → **Mitigation:** Timestamp includes seconds (HHMMSS) making collisions extremely unlikely for same-spec concurrent runs
