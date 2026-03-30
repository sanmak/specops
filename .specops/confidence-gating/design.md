# Design: Confidence Gating on Evaluation Findings

## Architecture

Confidence gating is implemented as modifications to the existing `core/evaluation.md` module and the evaluation report template. No new module is created.

### Confidence Tier Definitions

Added to the Adversarial Evaluation module after the Scoring Rubric section:

```
### Confidence Tiers for Findings

Each finding produced during evaluation (spec or implementation) carries a confidence classification:

| Tier | Range | Evidence Requirements | Scoring Impact |
|------|-------|----------------------|----------------|
| HIGH | >= 0.80 | file:line + specific code + concrete consequence | Counts toward pass/fail |
| MODERATE | 0.60-0.79 | file or pattern + likely impact | Counts toward pass/fail |
| LOW | < 0.60 | No minimum evidence | Advisory only -- excluded from pass/fail |

Evidence validation rules:
- HIGH findings missing any required element are downgraded to MODERATE with note
- LOW findings satisfy the "mandatory finding per dimension" rule only when no MODERATE or HIGH findings exist
- Dimension scores are computed from HIGH and MODERATE findings only
```

### Evaluator Prompt Changes

The hardcoded evaluator prompts (both spec and implementation) are extended with confidence classification instructions:

```
4. Confidence classification: For each finding, assign a confidence value (0.00-1.00).
   - HIGH (>= 0.80): You can point to a specific file:line, quote the code, and describe
     a concrete consequence. All three must be present.
   - MODERATE (0.60-0.79): You can reference a file or pattern and describe a likely impact.
   - LOW (< 0.60): You suspect an issue but cannot point to specific evidence. Mark as
     [Advisory]. These do not affect the dimension score.
   If you assign HIGH but cannot provide all three evidence elements, downgrade to MODERATE.
```

### Evaluation Procedure Changes

In both the Spec Evaluation Protocol and Implementation Evaluation Protocol, the per-dimension procedure (step 2/5) is extended:

Current step c: "Assign a score (1-10 integer)..."
New step c.5: "For each finding listed in step b, assign a confidence tier (HIGH/MODERATE/LOW) with a numeric value. Validate evidence requirements per tier. Downgrade if evidence is insufficient."
Modified step c: "Assign a score (1-10 integer) based on HIGH and MODERATE findings only. LOW findings are excluded from score computation."

### Evaluation Template Changes

The evaluation report template (`core/templates/evaluation.md`) is updated:

- The findings column in the dimension table becomes a summary reference
- A per-dimension findings detail section is added below the table with Confidence annotations:

```
#### [Dimension Name] Findings

| # | Finding | Confidence | Evidence | Impact |
|---|---------|-----------|----------|--------|
| 1 | [description] | HIGH (0.85) | file:line, code quote | [consequence] |
| 2 | [description] | LOW (0.45) | [Advisory] | [suspected impact] |
```

### Files Modified

| File | Change |
|---|---|
| `core/evaluation.md` | Add Confidence Tiers section, extend evaluator prompts, modify procedure steps |
| `core/templates/evaluation.md` | Add Confidence column, add per-dimension findings detail format |
| `generator/validate.py` | Add confidence-related markers to EVALUATION_MARKERS |

### Dependency Decisions

No new external dependencies required.
