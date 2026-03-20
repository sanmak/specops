## Proxy Metrics

Proxy metrics measure spec output and implementation productivity without requiring platform token APIs. Metrics are captured deterministically at Phase 4 (completion) and stored in `spec.json` as an optional `metrics` object. They provide data points for ROI analysis: how much was specified, how much code changed, how many tasks completed, and how long the workflow took.

### Metrics Capture Procedure

During Phase 4, after finalizing `implementation.md` (step 2) and before the memory update (step 3), capture proxy metrics. This step is mandatory when the spec status transitions to `completed`.

1. **Collect spec artifact sizes:**
   - READ_FILE(`<specsDir>/<spec-name>/requirements.md`) (or `bugfix.md` / `refactor.md` depending on spec type in `spec.json`)
   - READ_FILE(`<specsDir>/<spec-name>/design.md`)
   - READ_FILE(`<specsDir>/<spec-name>/tasks.md`)
   - READ_FILE(`<specsDir>/<spec-name>/implementation.md`)
   - For each file that exists, count the total characters. If a file does not exist, treat its character count as 0.
   - Calculate `specArtifactTokensEstimate` = total characters across all artifacts / 4 (integer division, round down)

2. **Collect git diff stats:**
   - READ_FILE(`<specsDir>/<spec-name>/spec.json`) to get the `created` timestamp
   - RUN_COMMAND(`git log --oneline --after="<created>" -- . | wc -l`) to check for commits in the spec timeframe
   - RUN_COMMAND(`git diff --stat HEAD~$(git log --oneline --after="<created>" -- . | wc -l) 2>/dev/null || echo "0 files changed"`) to get the diff summary
   - Parse the summary line for `filesChanged`, `linesAdded`, `linesRemoved`
   - If the git command fails or returns no output, set all three values to 0 and NOTIFY_USER("Could not compute git diff stats — metrics will show 0 for code changes.")

3. **Count completed tasks:**
   - From the `tasks.md` content already loaded in step 1, count occurrences of `**Status:** Completed` (case-sensitive match)
   - Store as `tasksCompleted`

4. **Count verified acceptance criteria:**
   - From the requirements/bugfix/refactor artifact already loaded in step 1, count occurrences of `- [x]` (checked checkboxes)
   - From the `tasks.md` content, also count `- [x]` under **Acceptance Criteria:** and **Tests Required:** sections
   - Store total as `acceptanceCriteriaVerified`

5. **Calculate spec duration:**
   - READ_FILE(`<specsDir>/<spec-name>/spec.json`) to get the `created` timestamp (already available from step 2)
   - RUN_COMMAND(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) for the current completion time
   - Parse both ISO 8601 timestamps and compute the difference in minutes
   - Store as `specDurationMinutes`
   - This value measures wall-clock elapsed time and may be inaccurate if work was paused between sessions

6. **Write metrics to spec.json:**
   - Assemble the `metrics` object:
     ```json
     {
       "specArtifactTokensEstimate": <integer>,
       "filesChanged": <integer>,
       "linesAdded": <integer>,
       "linesRemoved": <integer>,
       "tasksCompleted": <integer>,
       "acceptanceCriteriaVerified": <integer>,
       "specDurationMinutes": <integer>
     }
     ```
   - EDIT_FILE(`<specsDir>/<spec-name>/spec.json`) to add or update the `metrics` field
   - If any individual metric could not be computed, set its value to 0 rather than omitting it

### Platform Adaptation

All 4 supported platforms have the capabilities required for metrics capture:

| Capability | Claude Code | Cursor | Codex | Copilot | Impact |
|-----------|-------------|--------|-------|---------|--------|
| `canAccessGit` | true | true | true | true | Git diff stats available on all platforms |
| `canExecuteCode` | true | true | true | true | RUN_COMMAND available for git and date commands |

No platform-specific fallbacks are needed — the metrics capture procedure is identical across all platforms.

### Metrics Safety

- **Token estimates are approximate**: The `specArtifactTokensEstimate` uses characters/4 as a rough proxy for tokens. Actual tokenization varies by model and encoding. This metric measures spec artifact size, not API token consumption.
- **Duration includes idle time**: `specDurationMinutes` is wall-clock elapsed time from spec creation to completion. If work was paused between sessions, the duration will overcount active time.
- **Git diff scope**: `filesChanged`, `linesAdded`, and `linesRemoved` reflect repository changes during the spec timeframe. If the spec was implemented on a shared branch with other concurrent work, these numbers may include unrelated changes.
- **Metrics are non-blocking**: If any metric collection substep fails, the affected metric is set to 0 and completion proceeds. Metrics failures never block spec completion.
- **No sensitive data**: Metrics contain only aggregate numerical values — no file contents, no PII, no secrets.
