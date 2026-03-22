# Production Learnings — Design

## Architecture Overview

New `core/learnings.md` module (~180-220 lines) following the three-layer architecture pattern. The module defines the learning lifecycle, storage format, capture mechanisms, retrieval filtering, and safety rules using abstract operations. The generator wires it into all 4 platform outputs.

## Storage Format

Learnings are stored in `<specsDir>/memory/learnings.json` alongside the existing memory files (`context.md`, `decisions.json`, `patterns.json`).

```json
{
  "version": 1,
  "learnings": [
    {
      "id": "L-<specId>-<N>",
      "specId": "batch-processing",
      "category": "performance|scaling|security|reliability|ux|design|other",
      "severity": "critical|high|medium|low",
      "description": "Concurrent writes above 500 connections degrade P99",
      "resolution": "Added connection pooling with max 200 concurrent writes",
      "preventionRule": "Spec design.md must include concurrency limits for write-heavy operations",
      "affectedFiles": ["src/batch/writer.ts", "src/db/pool.ts"],
      "reconsiderWhen": ["PostgreSQL upgraded past v15", "Write throughput exceeds 10k/sec"],
      "supersedes": null,
      "supersededBy": null,
      "discoveredAt": "2026-03-10T14:22:00Z",
      "resolvedAt": "2026-03-14T09:15:00Z"
    }
  ]
}
```

## Architecture Decisions

### AD-1: Immutable records with supersession chain

A learning is never edited. When context changes, create a new learning with `supersedes: "L-old-id"` and update the old learning's `supersededBy` field. Rationale: follows the ADR pattern (Netflix) — records can't go stale because they're point-in-time snapshots. The supersession chain itself is the institutional memory.

### AD-2: "Reconsider When" triggers over calendar-based review

Each learning carries optional `reconsiderWhen` conditions — evaluable statements the agent checks during Phase 1 loading. Categories:
- **File existence**: `"src/old-auth/ directory removed"` → agent checks FILE_EXISTS
- **Version checks**: `"PostgreSQL upgraded past v15"` → agent checks dependency files
- **Threshold checks**: `"Team grows beyond 8 engineers"` → not auto-evaluable, presented as-is

If any condition evaluates to true, the learning is flagged as "potentially invalidated" rather than presented as fact. This is trigger-based review (system property) instead of calendar-based review (cultural norm).

### AD-3: Five-layer retrieval filtering

Phase 1 loading uses a filtering pipeline to prevent noise:
1. **Proximity** — Only learnings whose `affectedFiles` overlap with files the current spec will touch
2. **Recurrence** — Weight learnings appearing in 2+ specs higher
3. **Severity** — Critical/high always surface; medium/low only if directly relevant
4. **Decay/validity** — Evaluate `reconsiderWhen` triggers, flag invalidated learnings
5. **Category matching** — During design phase surface design learnings, during implementation surface implementation learnings

Cap: max `maxSurfaced` learnings (default 3, configurable, max 10).

### AD-4: Three capture mechanisms

1. **Explicit**: `/specops learn <spec-name>` — developer describes what they discovered (5-second capture)
2. **Agent-proposed**: During bugfix workflow, agent detects learning opportunity from the fix context and proposes capture (developer approves/rejects, zero writing)
3. **Reconciliation-based**: `/specops reconcile --learnings` scans recent git history for hotfix patterns linked to specs and proposes learnings

### AD-5: Executable knowledge suggestion

When a learning describes a testable condition (performance threshold, constraint violation), the agent suggests: "This learning is testable. Want me to propose a fitness function?" The agent does NOT auto-create tests — it proposes, the developer decides. Rationale: fitness functions (ThoughtWorks pattern) convert prose into executable checks that can't go stale silently.

### AD-6: Pattern detection extension

Extends the existing `patterns.json` with a `learningPatterns` array. Cross-spec learning categories appearing in 2+ specs are detected as recurring patterns and stored for Phase 1 surfacing in future specs.

## Integration Points

| Phase | Location | Change |
|-------|----------|--------|
| Phase 1 step 4 | `core/workflow.md` | Load learnings.json after memory, filter by 5-layer pipeline, surface max 3 |
| Phase 4 step 3 | `core/workflow.md` | After memory update, prompt for learning capture if implementation revealed surprises |
| Bugfix workflow | `core/workflow.md` | Agent-proposed learning extraction during bugfix specs |
| Dispatcher | `core/dispatcher.md` | New `learn` mode route (step ~7.5) |
| Reconciliation | `core/reconciliation.md` | `--learnings` flag extension for git history scanning |
| Memory | `core/memory.md` | Reference learnings pattern detection |

## Config Schema

New `learnings` object under `implementation` in `.specops.json`:

```json
"learnings": {
  "enabled": true,
  "maxSurfaced": 3,
  "severityThreshold": "medium",
  "capturePrompt": "auto"
}
```

- `enabled` (boolean, default true): Toggle learnings system
- `maxSurfaced` (integer, default 3, min 1, max 10): Max learnings shown during Phase 1
- `severityThreshold` (enum: "all"/"medium"/"high"/"critical", default "medium"): Minimum severity to surface
- `capturePrompt` (enum: "auto"/"manual"/"off", default "auto"): When to prompt — auto = Phase 4 + bugfix, manual = only /specops learn, off = disabled

## Files Affected

**New:**
- `core/learnings.md` — Core module (~180-220 lines)

**Modified:**
- `core/workflow.md` — Phase 1 step 4 (loading), Phase 4 step 3 (capture), bugfix workflow
- `core/dispatcher.md` — New `learn` mode route
- `core/reconciliation.md` — `--learnings` extension
- `core/memory.md` — Reference learnings pattern detection
- `core/mode-manifest.json` — Add `learnings` to spec, from-plan, audit, learn modes
- `spec-schema.json` — Optional `productionLearnings` array
- `schema.json` — `learnings` config object under `implementation`
- `generator/generate.py` — `build_common_context()` addition
- `generator/templates/*.j2` — `{{ learnings }}` placeholder (all 4 templates)
- `generator/validate.py` — `LEARNINGS_MARKERS` constant and check
- `tests/test_platform_consistency.py` — `learnings` entry in REQUIRED_MARKERS
- `CLAUDE.md` — New module and config documentation
- `docs/REFERENCE.md` — `/specops learn` command
- `docs/STRUCTURE.md` — `learnings.json` file
