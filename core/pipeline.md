## Automated Pipeline Mode

Pipeline mode automates iterative Phase 3 → Phase 4 acceptance cycling for existing specs. Instead of manually re-invoking SpecOps when acceptance criteria remain unmet, `/specops pipeline <spec-name>` runs implement-verify-fix cycles with a configurable maximum iteration count. Pipeline mode re-uses existing Phase 3 and Phase 4 logic as units — it is an orchestration layer, not a reimplementation.

### Pipeline Mode Detection

Patterns: "pipeline <spec-name>", "auto-implement <spec-name>", "run pipeline for <spec-name>".

These must refer to SpecOps automated implementation cycling, NOT a product feature. Disambiguation: "create CI pipeline", "build data pipeline", "add deployment pipeline", "design pipeline architecture" are NOT pipeline mode — they describe product features that should follow the standard spec workflow.

If detected, follow the Pipeline Mode workflow below instead of the standard phases.

### Pipeline Prerequisites

Before entering the cycle loop, validate:

1. **Spec exists**: FILE_EXISTS(`<specsDir>/<spec-name>/spec.json`). If not found, NOTIFY_USER("Spec '<spec-name>' not found. Create it first with `/specops <description>`.") and stop.
2. **Status is compatible**: READ_FILE(`<specsDir>/<spec-name>/spec.json`). Status must be `draft`, `approved`, `self-approved`, or `implementing`.
   - If `completed`: NOTIFY_USER("Spec '<spec-name>' is already completed.") and stop.
   - If `in-review`: NOTIFY_USER("Spec '<spec-name>' is in review. Approve it first.") and stop.
3. **Spec files present**: FILE_EXISTS for the requirements/bugfix/refactor file, design.md, and tasks.md. If any are missing, NOTIFY_USER("Spec '<spec-name>' is incomplete — missing <file>. Generate the spec first.") and stop.
4. **Read config**: Determine `maxCycles` from `config.implementation.pipelineMaxCycles` (default: 3).
5. **Initialize run log**: Initialize a run log following the Run Logging module (using the known spec name directly — no `_pending` workaround needed since the spec already exists).

### Pipeline Cycle

**Pre-cycle spec evaluation (one-time):** Before entering the cycle loop, if READ_FILE(`.specops.json`) shows `config.implementation.evaluation.enabled` is `true` (default: true), run spec evaluation once since the spec already exists and does not change during pipeline execution:

1. READ_FILE(`<specsDir>/<spec-name>/requirements.md`) (or `bugfix.md`/`refactor.md`), READ_FILE(`<specsDir>/<spec-name>/design.md`), and READ_FILE(`<specsDir>/<spec-name>/tasks.md`).
2. Apply the adversarial spec evaluator against the collected artifacts and WRITE_FILE the results to `<specsDir>/<spec-name>/evaluation.md`.
3. READ_FILE(`<specsDir>/<spec-name>/evaluation.md`) and check the overall verdict. If the verdict is `fail`, NOTIFY_USER("Spec evaluation failed before pipeline start. Review evaluation.md for findings.") and STOP — do not enter the cycle loop. If the verdict is `pass`, proceed to the cycle loop.

If `config.implementation.evaluation.enabled` is explicitly set to `false`, skip this step entirely and proceed directly to the cycle loop.

The core loop:

```text
evaluationEnabled = READ_FILE(.specops.json).config.implementation.evaluation.enabled (default: true)
previousUnmetCriteria = null
previousEvaluationScores = null
cycle = 0

while cycle < maxCycles:
    cycle += 1

    // Log cycle start (if run logging enabled)
    // EDIT_FILE run log: append "## Cycle {cycle}/{maxCycles}"

    // Notify user
    NOTIFY_USER("Pipeline cycle {cycle}/{maxCycles} starting for <spec-name>...")

    // Execute Phase 3 (existing logic)
    // - Implementation gates (review gate, task tracking gate) — run on first cycle only
    // - Set status to "implementing" if not already
    // - Task execution: sequential or delegated per complexity score vs config.implementation.delegationThreshold
    // - autoCommit per task (if enabled)

    // Git checkpoint: implemented (if gitCheckpointing enabled)
    // RUN_COMMAND(git add -A && git commit -m "specops(checkpoint): implemented -- <spec-name>")

    // Phase 4 acceptance check — evaluation-aware (headless mode)
    if evaluationEnabled:
        // Dispatch evaluation with headless: true for structured JSON response
        // The evaluation sub-agent returns a Headless Response Schema JSON object
        evaluationResponse = dispatch evaluation with headless: true

        // Parse structured response (with fallback)
        if evaluationResponse is valid JSON with status, scores, verdict, findings:
            evaluationScores = evaluationResponse.scores
            overallVerdict = evaluationResponse.verdict
            findings = evaluationResponse.findings
            // Persist evaluation results to evaluation.md for audit trail
            // WRITE_FILE <specsDir>/<spec-name>/evaluation.md with formatted results
        else:
            // Fallback: evaluation did not return valid headless JSON
            // Read evaluation.md and parse markdown (backward compatibility)
            // READ_FILE <specsDir>/<spec-name>/evaluation.md
            evaluationScores = map of category -> score from evaluation.md
            overallVerdict = verdict from evaluation.md
            findings = extracted findings from evaluation.md

        if overallVerdict == "pass":
            // All evaluation criteria pass — finalize
            // Execute Phase 4 steps 2-8 (finalize implementation.md, metrics, memory, docs, completion gate, status)
            // Git checkpoint: completed (if enabled)
            NOTIFY_USER("Pipeline completed in {cycle} cycle(s). All evaluation criteria passed.")
            break

        // Zero-progress detection (evaluation-based)
        if evaluationScores == previousEvaluationScores:
            NOTIFY_USER("No progress in cycle {cycle} — evaluation scores unchanged from previous cycle. Stopping to avoid infinite loop.")
            // Do NOT mark spec as completed
            // Leave status as "implementing"
            break

        previousEvaluationScores = evaluationScores
        failingCategories = categories where score < passing threshold

        // Action routing: classify findings and apply auto-fixes within cycle
        // When headless JSON is available, read fix classes directly from findings[].fixClass
        // When using markdown fallback, apply the Action Routing procedure from core/evaluation.md
        // to classify into: auto_fix, gated_fix, manual, advisory

        // Execute auto_fix items immediately (no developer interaction)
        // For each auto_fix finding: EDIT_FILE to apply fix, verify no test regression
        // If auto_fix fails: revert, reclassify as gated_fix

        // Handle gated_fix items based on platform capability
        if canAskInteractive:
            // Batch all gated_fix items and ASK_USER for approval
            // Apply approved fixes, reclassify rejected as manual
        else:
            // Non-interactive: treat gated_fix as auto_fix (apply without asking)

        // Report manual findings to developer via NOTIFY_USER (no fix attempted)
        // Include advisory findings in evaluation report (no action)

    else:
        // Evaluation disabled — use existing checkbox verification
        // READ_FILE requirements/bugfix/refactor file
        // Count checked (- [x]) and unchecked (- [ ]) acceptance criteria
        // Check off criteria that the implementation now satisfies

        unmetCriteria = set of unchecked criteria text

        if unmetCriteria is empty:
            // All criteria pass — finalize
            // Execute Phase 4 steps 2-8 (finalize implementation.md, metrics, memory, docs, completion gate, status)
            // Git checkpoint: completed (if enabled)
            NOTIFY_USER("Pipeline completed in {cycle} cycle(s). All acceptance criteria met.")
            break

        // Zero-progress detection (checkbox-based)
        if unmetCriteria == previousUnmetCriteria:
            NOTIFY_USER("No progress in cycle {cycle} — same {count} criteria unmet as previous cycle. Stopping to avoid infinite loop.")
            // Do NOT mark spec as completed
            // Leave status as "implementing"
            break

        previousUnmetCriteria = unmetCriteria

    if cycle == maxCycles:
        if evaluationEnabled:
            NOTIFY_USER("Pipeline reached max cycles ({maxCycles}). Evaluation still failing on: {failingCategories}. Manual intervention required.")
        else:
            NOTIFY_USER("Pipeline reached max cycles ({maxCycles}). {count} criteria still unmet. Manual intervention required.")
        // Do NOT mark spec as completed
        // Leave status as "implementing"
        // Log incomplete state in run log
        break

    // Prepare for next cycle
    if evaluationEnabled:
        // Reset tasks that map to failing evaluation categories back to Pending
        // EDIT_FILE tasks.md — set relevant tasks to **Status:** Pending
        NOTIFY_USER("Cycle {cycle}/{maxCycles}: evaluation failing on {failingCategories}. Starting next cycle...")
    else:
        // Reset tasks whose acceptance criteria contributed to unmet items back to Pending
        // EDIT_FILE tasks.md — set relevant tasks to **Status:** Pending
        NOTIFY_USER("Cycle {cycle}/{maxCycles}: {unmetCount} criteria unmet. Starting next cycle...")

// Pipeline ends
```

### Cycle Limit and Progress

- **Default max cycles**: 3. Configurable via `config.implementation.pipelineMaxCycles` (integer, min 1, max 10).
- **Progress reporting**: After each cycle, NOTIFY_USER with: cycle number, criteria met count vs total, tasks re-queued count.
- **Progress tracking**: If `canTrackProgress` is true, UPDATE_PROGRESS with cycle progress. If false, report in response text.

### Pipeline Integration

Pipeline mode connects to other SpecOps features:

| Feature | Integration |
| --- | --- |
| **Run logging** | Each cycle writes a `## Cycle N` section in the run log with cycle-specific entries |
| **Git checkpointing** | "implemented" checkpoint fires after each cycle's Phase 3. "completed" checkpoint fires once at final completion. |
| **Task delegation** | Within each cycle, task execution uses auto-delegation (complexity score vs `config.implementation.delegationThreshold`). If delegation is active, the pipeline orchestrator delegates tasks the same way Phase 3 does. |
| **Plan validation** | Runs once in Phase 2 (before pipeline starts). Not repeated per cycle — the spec references don't change between cycles. |
| **Metrics** | Captured once at final completion (Phase 4 step 2.5), not per cycle. `specDurationMinutes` includes all cycle time. |
| **Action routing** | Within each cycle, evaluation findings are classified by fix class. Auto-fix items are applied within the cycle without stopping. Gated items are batched for approval (interactive) or auto-applied (non-interactive). Manual and advisory items are reported at cycle end. |
| **Headless evaluation** | Pipeline dispatches evaluation with headless: true to receive structured JSON (scores, verdict, findings with fix classes). Falls back to markdown parsing if headless response is unavailable. Structured consumption eliminates brittle text parsing for score extraction and verdict determination. |
| **autoCommit** | Fires per-task within each cycle (Phase 3 step 7). Composes with checkpointing as usual. |

### Pipeline Safety

- **Max cycles cap**: `pipelineMaxCycles` is capped at 10 in the schema (maximum: 10). This prevents runaway loops from misconfiguration.
- **Zero-progress detection**: If the same acceptance criteria are unmet after consecutive cycles, the pipeline stops early. This catches scenarios where the implementation repeatedly fails to address specific criteria.
- **Blocked task handling**: If a task is set to `Blocked` during a cycle and cannot be resolved, the pipeline stops and NOTIFY_USER with the blocker details.
- **Safety inheritance**: Pipeline mode inherits all safety rules from the Safety module (convention sanitization, path containment, no secrets in specs).
- **No spec artifact modification**: Pipeline mode does not modify requirements.md or design.md — it only re-executes tasks and re-checks acceptance criteria. Spec content is frozen during pipeline execution.
- **Auto-fix safety**: Auto-fix items applied during action routing follow the same safety rules as manual implementation — path containment, no secrets, convention sanitization. If an auto-fix introduces a test regression, it is reverted and reclassified as gated_fix.

### Platform Adaptation

| Capability | Impact |
| --- | --- |
| `canAskInteractive: true` | After max cycles reached, ASK_USER("Pipeline exhausted max cycles. Run another round, or stop?"). If user chooses another round, increment maxCycles by the original value and continue. |
| `canAskInteractive: false` | After max cycles reached, stop with NOTIFY_USER. Note remaining unmet criteria as assumptions. |
| `canDelegateTask: true` | Task delegation available within each cycle |
| `canTrackProgress: true` | Cycle progress tracked via UPDATE_PROGRESS |
| `canTrackProgress: false` | Cycle progress reported in response text |

### Headless Mode Protocol for Pipeline

Pipeline mode is the primary consumer of the Headless Mode Protocol defined in the dispatcher. When pipeline dispatches evaluation within a cycle, it sets `headless: true` to receive structured JSON instead of markdown.

#### Headless Response Schema

The headless mode response is a JSON object with these fields:

- `status`: `"success"`, `"failure"`, or `"partial"`
- `findings`: Array of finding objects (id, severity, confidence, confidenceValue, fixClass, description, remediation, file, line)
- `scores`: Object mapping dimension names to integer scores (1-10)
- `verdict`: `"pass"`, `"fail"`, or `null`
- `actionItems`: Array of action strings for the caller
- `metadata`: Object with mode name, specId, timestamp, and `headless: true`

#### Headless Dispatch in Pipeline

1. Pipeline sets `headless: true` when dispatching evaluation
2. Evaluation sub-agent returns JSON conforming to the Headless Response Schema
3. Pipeline parses the JSON and extracts scores, verdict, findings directly
4. If JSON parsing fails, pipeline falls back to reading evaluation.md and parsing markdown (backward compatibility)

#### Participating Modes

Pipeline interacts with these headless mode producers:

- **evaluation**: Returns structured scores, findings (with fix classes from action routing), and verdict
- **audit**: Returns structured health check findings when invoked headlessly

All other modes remain interactive-only and do not produce headless output.
