# Token Usage & Proxy Metrics

SpecOps automatically captures proxy productivity metrics when a spec completes. These metrics provide data points for measuring ROI without requiring platform-specific token counting APIs.

## Why Proxy Metrics?

AI coding assistants (Claude Code, Cursor, Codex, Copilot) do not expose token-counting APIs to custom instructions. SpecOps captures deterministic output measurements instead — artifact sizes, code changes, task counts, and duration — that correlate with token usage and productivity.

## Metrics Reference

Each completed spec stores a `metrics` object in `spec.json`:

| Metric | Type | Calculation |
| -------- | ------ | ------------- |
| `specArtifactTokensEstimate` | integer | Total characters across all spec artifacts (requirements.md, design.md, tasks.md, implementation.md) divided by 4 |
| `filesChanged` | integer | Files changed during implementation (from `git diff --stat`) |
| `linesAdded` | integer | Lines added during implementation |
| `linesRemoved` | integer | Lines removed during implementation |
| `tasksCompleted` | integer | Count of tasks with `**Status:** Completed` in tasks.md |
| `acceptanceCriteriaVerified` | integer | Count of checked `- [x]` checkboxes across spec artifacts |
| `specDurationMinutes` | integer | Wall-clock minutes from spec creation to completion |

## Benchmark Data

Based on SpecOps dogfooding (13 completed specs building SpecOps itself):

| Spec Type | Typical Tasks | Artifact Size (chars) | Token Estimate | Files Changed |
| ----------- | -------------- | ---------------------- | ---------------- | --------------- |
| Small feature | 3-4 | 3,000-5,000 | 750-1,250 | 4-8 |
| Medium feature | 5-6 | 6,000-10,000 | 1,500-2,500 | 8-15 |
| Large feature | 7-8 | 10,000-16,000 | 2,500-4,000 | 12-20 |
| Bugfix | 2-4 | 4,000-8,000 | 1,000-2,000 | 3-8 |
| Refactor | 3-5 | 5,000-9,000 | 1,250-2,250 | 6-12 |

These are spec artifact sizes only. Actual platform token usage includes the SpecOps instruction set (~50K tokens), codebase context, and conversation history — typically 5-20x the spec artifact size.

## ROI Analysis Framework

### Cost per Spec

To estimate the total token cost of a spec-driven workflow:

1. **Spec generation (Phase 2)**: ~2-5x the `specArtifactTokensEstimate` (the agent reads context, generates, and iterates)
2. **Implementation (Phase 3)**: Varies by code complexity. Use `linesAdded + linesRemoved` as a proxy — each line of code change typically requires 50-200 tokens of agent reasoning
3. **Review & completion (Phase 4)**: ~1-2x the `specArtifactTokensEstimate` (re-reading artifacts, verifying criteria)

### Productivity Ratio

Compare specs with and without SpecOps:

- **Lines of code per task**: `(linesAdded + linesRemoved) / tasksCompleted`
- **Acceptance criteria hit rate**: `acceptanceCriteriaVerified / total_criteria` (indicates spec quality)
- **Rework indicator**: If `specDurationMinutes` is disproportionately high relative to task count, it may indicate underspecified requirements

### Cross-Spec Trends

Track metrics across completed specs to identify:

- **Spec size inflation**: Growing `specArtifactTokensEstimate` over time may indicate over-specification
- **Code change density**: Ratio of `linesAdded` to `tasksCompleted` trending up may indicate tasks are too coarse
- **Duration patterns**: Consistent `specDurationMinutes` across similar spec types indicates a stable workflow

## Decomposition and Initiative Overhead

- **Phase 1.5 (Scope Assessment)**: Adds approximately 50-100 tokens of output per spec creation. The assessment evaluates complexity signals and produces a brief pass/fail result. When decomposition is triggered, the proposal format adds another 100-200 tokens.
- **Initiative management**: Negligible overhead. Reading and writing `initiative.json` and `initiative-log.md` involves small structured data files (typically under 1KB).
- **Cross-spec dependency checks**: The Phase 3 dependency gate reads `spec.json` files for referenced specs. With typical initiative sizes (2-5 specs), this adds fewer than 50 tokens per gate check.

## Limitations

- **Token estimates are approximate**: Characters/4 is a rough proxy. Actual tokenization varies by model and encoding.
- **Duration includes idle time**: `specDurationMinutes` measures wall-clock time, not active time. Sessions paused overnight inflate this number.
- **Git diff scope**: Code change metrics reflect all repository changes during the spec timeframe, which may include unrelated work on shared branches.
- **No input token tracking**: These metrics measure output/productivity, not input token consumption. The actual API cost depends on conversation length, context window usage, and model pricing.

## Example spec.json with Metrics

```json
{
  "id": "proxy-metrics",
  "type": "feature",
  "status": "completed",
  "version": 1,
  "created": "2026-03-20T19:50:01Z",
  "updated": "2026-03-20T21:30:00Z",
  "author": { "name": "sanmak" },
  "metrics": {
    "specArtifactTokensEstimate": 3200,
    "filesChanged": 14,
    "linesAdded": 280,
    "linesRemoved": 10,
    "tasksCompleted": 8,
    "acceptanceCriteriaVerified": 24,
    "specDurationMinutes": 100
  }
}
```
