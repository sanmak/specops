# Inter-Mode Communication -- Design

## Architecture Overview

Inter-mode communication is a protocol addition to core/dispatcher.md, not a new core module. It defines a JSON response schema and a headless dispatch flag. Participating modes (audit, evaluation, pipeline) adopt the schema when invoked headlessly. The change is additive -- no existing behavior is modified.

```
Current flow (markdown-based):
  Pipeline -> dispatch evaluation -> evaluation writes evaluation.md -> pipeline reads evaluation.md -> parses markdown for scores/verdict

New flow (headless):
  Pipeline -> dispatch evaluation with headless:true -> evaluation produces JSON response -> pipeline reads JSON directly
```

## Design Decisions

### D1: Protocol in dispatcher, not separate module

The headless response schema and dispatch protocol live in `core/dispatcher.md` as a new section. Rationale: this is a dispatch-level concern (how modes communicate), not a workflow concern. It does not warrant a separate core module, which would require mode-manifest changes, generator registration, and Jinja2 template updates. Keeping it in the dispatcher minimizes the blast radius.

### D2: JSON schema inline in core/dispatcher.md

The headless response JSON schema is documented inline in core/dispatcher.md rather than as a separate JSON schema file. Rationale: the schema is consumed by LLM agents, not by code validators. Inline documentation is more accessible to the agent and avoids adding another file to the build pipeline. The schema follows the same object constraint conventions as spec-schema.json (additionalProperties: false, maxLength on strings, maxItems on arrays).

### D3: Participating modes are opt-in

Only modes that currently chain into other modes gain headless support: audit, evaluation (implicit in dispatcher step 6), and pipeline. This keeps the change small. Other modes can be added later by following the same pattern.

### D4: Pipeline as primary consumer

Pipeline mode is the primary beneficiary. It currently uses text parsing to extract evaluation scores and verdicts from evaluation.md. With headless mode, it gets deterministic JSON. The pipeline cycle pseudocode is updated to invoke evaluation with `headless: true` and consume the response directly.

### D5: Backward compatibility via fallback

Pipeline mode checks whether the evaluation response is JSON. If not (older version, evaluation disabled), it falls back to the existing markdown parsing. This ensures no breaking change.

## Detailed Design

### Section 1: Headless Response Schema (added to core/dispatcher.md)

New section "## Headless Mode Protocol" added after the "## Safety Rules" section in core/dispatcher.md:

```
## Headless Mode Protocol

When a mode is invoked with headless: true in the dispatch context, the mode
produces a JSON response conforming to the Headless Response Schema instead
of human-readable markdown.

### Headless Response Schema

{
  "status": "success" | "failure" | "partial",
  "findings": [
    {
      "id": "string (max 50)",
      "severity": "P0" | "P1" | "P2" | "P3",
      "confidence": "HIGH" | "MODERATE" | "LOW",
      "confidenceValue": 0.00-1.00,
      "fixClass": "auto_fix" | "gated_fix" | "manual" | "advisory" | null,
      "description": "string (max 2000)",
      "remediation": "string (max 2000)",
      "file": "string (max 500, optional)",
      "line": integer (optional)
    }
  ],
  "scores": {
    "<dimensionName>": integer (1-10)
  },
  "verdict": "pass" | "fail" | null,
  "actionItems": ["string (max 500)"],
  "metadata": {
    "mode": "string (max 50)",
    "specId": "string (max 100, optional)",
    "timestamp": "ISO 8601 string",
    "headless": true
  }
}

Constraints:
- findings array: maxItems 100
- actionItems array: maxItems 50
- scores object: max 20 dimension entries
- All string fields have maxLength as annotated
- All objects use additionalProperties: false equivalent (agents must
  not add extra fields)

### Headless Dispatch

When dispatching a mode headlessly:

1. Add `headless: true` to the dispatch context in the Shared Context Block.
2. Add this instruction to the sub-agent prompt:
   "You are invoked in headless mode. Instead of producing human-readable
   markdown, output a single JSON object conforming to the Headless Response
   Schema. Do not include any text before or after the JSON. The JSON must be
   valid and parseable."
3. After the sub-agent returns, parse the response as JSON.
   - If parsing succeeds, use the structured response.
   - If parsing fails, treat as a non-headless response and fall back to
     markdown parsing (backward compatibility).

### Participating Modes

| Mode | Headless Support | Role |
| --- | --- | --- |
| audit | Producer | Outputs structured health findings |
| evaluation (step 6/7) | Producer | Outputs structured scores, findings, verdict |
| pipeline | Consumer | Invokes evaluation headlessly, consumes JSON |
| All other modes | None | Unchanged behavior |
```

### Section 2: Dispatcher Dispatch Protocol Update

Update the existing "## Dispatch Protocol" section, step 2 ("Build sub-agent prompt"):

Add after the current step 2:
```
2.5. **Headless mode injection**: If the dispatch context includes `headless: true`,
     append the headless mode instruction to the sub-agent prompt (from the
     Headless Mode Protocol section). The instruction tells the sub-agent to
     output JSON instead of markdown.
```

### Section 3: Dispatcher Step 6 Update (Spec Evaluation Dispatch)

The existing step 6 describes spec evaluation dispatch. Add a headless variant:

When evaluation is dispatched headlessly (called from pipeline mode), the evaluation sub-agent returns a JSON response. The dispatcher passes this JSON back to the calling pipeline instead of writing to evaluation.md.

When evaluation is dispatched normally (at Phase 2 exit), the existing behavior is unchanged -- the evaluator writes to evaluation.md.

### Section 4: Pipeline Mode Update (core/pipeline.md)

Update the pipeline cycle pseudocode in the "### Pipeline Cycle" section:

```
// Phase 4 acceptance check -- evaluation-aware (updated for headless)
if evaluationEnabled:
    // Invoke evaluation with headless: true
    // Parse JSON response
    evaluationResponse = dispatch evaluation with headless: true

    if evaluationResponse is valid JSON:
        evaluationScores = evaluationResponse.scores
        overallVerdict = evaluationResponse.verdict
        findings = evaluationResponse.findings
    else:
        // Fallback: read evaluation.md and parse markdown (backward compat)
        // ... existing markdown parsing logic ...
```

The rest of the pipeline cycle logic remains the same -- it operates on scores, verdict, and findings regardless of source (JSON or markdown).

### Section 5: Audit Mode Headless Output

When audit mode is invoked with `headless: true`, it produces JSON instead of the markdown audit report. The findings array contains one entry per health check finding (drift, staleness, inconsistency, etc.). The status is `"success"` if all checks pass, `"failure"` if any check fails, `"partial"` if some checks could not run.

This is documented in core/dispatcher.md under the "### Participating Modes" subsection.

### Section 6: Validation Markers

Add `HEADLESS_MARKERS` to `generator/validate.py`:

```python
HEADLESS_MARKERS = [
    "Headless Mode Protocol",
    "Headless Response Schema",
    "Headless Dispatch",
    "headless: true",
    "Participating Modes",
    "headless mode",
]
```

These markers verify that all generated platform outputs include the headless protocol documentation.

### Files Modified

| File | Change |
| --- | --- |
| `core/dispatcher.md` | Add Headless Mode Protocol section, update Dispatch Protocol step 2, update step 6 |
| `core/pipeline.md` | Update pipeline cycle pseudocode to use headless evaluation |
| `generator/validate.py` | Add HEADLESS_MARKERS, add to validate_platform(), add to consistency loop |
| `tests/test_platform_consistency.py` | Import HEADLESS_MARKERS, add to REQUIRED_MARKERS |
| Generated platform outputs | Regenerate with `python3 generator/generate.py --all` |

### Dependency Decisions

No new dependencies introduced. This feature uses only existing SpecOps infrastructure (dispatcher, pipeline, evaluation, generator).
