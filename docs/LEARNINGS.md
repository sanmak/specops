# Production Learnings

Specs end at "completed." Production reveals what specs missed.

SpecOps captures these discoveries as structured, immutable records linked to originating specs. When future work touches the same code, relevant learnings surface automatically during Phase 1 context loading. The agent factors them into its design before writing a single line.

## How It Works

A learning is a point-in-time record: what was discovered, how it was resolved, and what future specs should do differently. Learnings follow the ADR (Architecture Decision Record) pattern. They are superseded, never edited.

```json
{
  "id": "L-batch-processing-1",
  "specId": "batch-processing",
  "category": "performance",
  "severity": "high",
  "description": "Concurrent writes above 500 connections degrade P99",
  "preventionRule": "Design docs must include concurrency limits for write-heavy ops",
  "affectedFiles": ["src/batch/writer.ts"],
  "reconsiderWhen": ["PostgreSQL upgraded past v15"]
}
```

## Three Capture Mechanisms

**1. Explicit capture** at the moment of discovery:

```text
/specops learn batch-processing
```

Interactive prompts collect the category, severity, affected files, prevention rule, and reconsider conditions. Zero free-form writing required.

**2. Agent-proposed capture** during bugfix workflows:

After fixing a bug linked to a prior spec, the agent summarizes the fix and proposes it as a learning. You approve or reject. No writing.

**3. Passive extraction** from git history:

```text
/specops reconcile --learnings
```

Scans recent commits for hotfix patterns, cross-references affected files against completed specs, and proposes learnings for each match.

## Retrieval Filtering

Not all learnings are relevant to every spec. A five-layer filtering pipeline ensures only applicable learnings surface:

| Layer | Filter | Purpose |
| --- | --- | --- |
| 1 | Proximity | Keeps learnings whose affected files overlap with the current spec |
| 2 | Recurrence | Weights learnings from categories appearing across multiple specs |
| 3 | Severity | Applies configurable threshold (default: medium and above) |
| 4 | Decay/Validity | Evaluates "reconsider when" conditions, excludes superseded learnings |
| 5 | Category matching | Prefers design/scaling learnings during spec, performance/reliability during implementation |

The top N learnings (configurable, default 3) are surfaced, ordered by severity, recurrence, then recency.

## Supersession

Learnings are immutable. When a learning becomes outdated:

1. Create a new learning with `supersedes` set to the old learning's ID
2. The old learning's `supersededBy` field is updated (the only allowed modification)
3. The old learning remains for historical reference but is excluded from retrieval

## Configuration

In `.specops.json` under `implementation.learnings`:

```json
{
  "implementation": {
    "learnings": {
      "capturePrompt": "auto",
      "maxSurfaced": 3,
      "severityThreshold": "medium"
    }
  }
}
```

| Setting | Default | Description |
| --- | --- | --- |
| `capturePrompt` | `"auto"` | `auto`: agent proposes learnings during bugfixes. `manual`: explicit capture only. `off`: disabled. |
| `maxSurfaced` | `3` | Maximum learnings shown during Phase 1 (1-10) |
| `severityThreshold` | `"medium"` | Minimum severity to surface. Critical/high always pass. |

## Storage

Learnings live in `<specsDir>/memory/learnings.json` alongside existing memory files. One file, no additional directories.
