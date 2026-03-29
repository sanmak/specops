# Design: Harden Adversarial Evaluation

## Design Approach

All three structural countermeasures are baked into the evaluator procedure and prompt text in `core/evaluation.md`. No new configuration flags, no new capability flags, no new files. The countermeasures become mandatory default behavior for all evaluations across all 5 platforms.

The model diversity instruction is added to the dispatcher's evaluation dispatch steps (6 and 7) in `core/dispatcher.md`, scoped to `canDelegateTask: true` platforms only.

## Component Design

### 1. Evaluation Procedure Changes (`core/evaluation.md`)

Both the spec evaluation procedure and the implementation evaluation procedure get three new structural steps inserted into the scoring loop:

**Evidence-first ordering** (inserted into the per-dimension assessment loop):
- Before scoring each dimension, the evaluator MUST list specific evidence (file paths, line references, code quotes, test output).
- After evidence, the evaluator MUST list at least one finding (gap, risk, or improvement opportunity).
- Only then does the evaluator assign a numeric score.

**Mandatory negative finding gate** (inserted after per-dimension scoring):
- After scoring a dimension, check whether the findings list is empty or contains only "No issues found" / equivalent language.
- If empty: cap the dimension score at 7 and append a note: "Score capped at 7 -- no concrete finding identified for this dimension."

**Score variance enforcement** (inserted after all dimensions are scored, before verdict):
- After all dimensions are scored, check whether all scores are identical.
- If identical: auto-fail with "Uniform scores detected -- re-evaluate with distinct per-dimension justification." Re-run the evaluation within the same iteration.

### 2. Evaluator Prompt Updates (`core/evaluation.md`)

Both the spec evaluator prompt and the implementation evaluator prompt get three additional instruction paragraphs:

```text
STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each dimension, list specific evidence (file paths, line references,
   code quotes, test output) BEFORE assigning a score. The score must follow from the evidence.
2. Mandatory finding: Each dimension MUST identify at least one concrete finding (gap, risk,
   or improvement opportunity). "No issues found" is not acceptable. If you cannot identify
   a finding, your score for that dimension is capped at 7.
3. Score variance: If all your dimension scores are identical, your evaluation auto-fails and
   you must re-evaluate with distinct per-dimension justification.
```

### 3. Evaluation Report Template Update (`core/templates/evaluation.md`)

The template table gains two new columns to enforce structure:

| Dimension | Evidence | Findings | Score | Threshold | Pass/Fail |

This replaces the current `| Dimension | Score | Threshold | Pass/Fail | Key Finding |` format.

### 4. Dispatcher Model Diversity (`core/dispatcher.md`)

Steps 6 and 7 gain a model diversity instruction for `canDelegateTask: true` dispatch:

> When dispatching the evaluator sub-agent, include this instruction in the sub-agent prompt: "If your platform supports model selection, use a different model than the one that generated the artifacts being evaluated. Model diversity reduces self-confirmation bias."

This is a prompt-level instruction, not a platform capability. It applies to Claude Code and Antigravity (the two `canDelegateTask: true` platforms).

### 5. Validation Alignment (`generator/validate.py`)

No new EVALUATION_MARKERS needed -- the existing markers cover the section headings, and the new content sits within those sections. However, EVALUATION_MARKERS must be added to the cross-platform consistency check loop (it is currently missing -- this is a pre-existing gap).

## Design Decisions

1. **Baked-in, not configurable**: These countermeasures are hardcoded defaults with no config override. This prevents projects from disabling the bias protections.
2. **Re-evaluation within same iteration**: A uniform-score auto-fail does not consume a `maxIterations` cycle. This avoids penalizing the evaluator for a structural check failure.
3. **Cap at 7, not auto-fail**: Mandatory findings use a score cap rather than an auto-fail because a missing finding for one dimension should not invalidate the entire evaluation.
4. **Template table restructure**: The evaluation report template changes column structure. Existing evaluation.md files are not migrated -- the new format applies to future evaluations only.
5. **Prompt-level model diversity**: The instruction is advisory ("when available") because model selection mechanisms vary by platform and runtime. Enforcing a specific model would require platform-specific tooling that does not exist.
