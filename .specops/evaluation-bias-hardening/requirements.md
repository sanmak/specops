# Feature: Harden Adversarial Evaluation

## Overview

Eliminate self-confirmation bias in the adversarial evaluation system by adding three structural countermeasures as baked-in defaults: score variance enforcement (uniform scores auto-fail), mandatory negative findings (every dimension must identify at least one gap/risk/improvement), and evidence-first scoring (evidence listed before numeric score). Additionally, add a model diversity instruction to the dispatcher for platforms with `canDelegateTask: true`.

These countermeasures address production learning L-dependency-introduction-gate-1: "Adversarial evaluation sub-agents score uniformly high (8/10) because the same LLM confirms its own work."

## Product Requirements

### Requirement 1: Score Variance Enforcement

**As a** developer using SpecOps
**I want** evaluations that produce identical scores across all dimensions to auto-fail
**So that** the evaluator is forced to differentiate its assessment per dimension rather than rubber-stamping a uniform score

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN all dimension scores in a spec or implementation evaluation are identical, THE SYSTEM SHALL auto-fail the evaluation with the message "Uniform scores detected -- re-evaluate with distinct per-dimension justification"
<!-- EARS: Event-driven -->
- [x] WHEN a uniform-score auto-fail occurs, THE SYSTEM SHALL re-run the evaluation within the same iteration (this does not consume an additional `maxIterations` cycle)
<!-- EARS: State-driven -->
- [x] WHILE score variance enforcement is active, THE SYSTEM SHALL check for uniform scores after all dimensions are scored and before writing the verdict

### Requirement 2: Mandatory Negative Finding

**As a** developer using SpecOps
**I want** every evaluation dimension to identify at least one concrete finding (gap, risk, or improvement opportunity)
**So that** the evaluator cannot hand-wave high scores without identifying areas for improvement

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN an evaluation dimension has zero findings (gaps, risks, or improvement opportunities), THE SYSTEM SHALL cap that dimension's score at 7 regardless of the assigned score
<!-- EARS: Unwanted behavior -->
- [x] THE SYSTEM SHALL NOT accept "No issues found" or equivalent empty-finding language as valid evaluation evidence
<!-- EARS: State-driven -->
- [x] WHILE the mandatory negative finding rule is active, EACH dimension assessment MUST include at least one entry in a "Findings" list before the score assignment

### Requirement 3: Evidence-First Scoring

**As a** developer using SpecOps
**I want** evaluators to list specific evidence (file paths, line references, test output, code quotes) before assigning a numeric score
**So that** the score is derived from evidence rather than assigned first and justified retroactively

**Acceptance Criteria (EARS):**

<!-- EARS: State-driven -->
- [x] WHILE evidence-first scoring is active, EACH dimension assessment MUST follow the order: (1) evidence list, (2) findings list, (3) numeric score
<!-- EARS: Unwanted behavior -->
- [x] THE SYSTEM SHALL NOT assign a score before listing evidence for that dimension
<!-- EARS: Event-driven -->
- [x] WHEN the evaluation report is written, EACH dimension section SHALL contain an "Evidence" subsection with at least one specific reference (file path, line number, quote, or test output)

### Requirement 4: Model Diversity for Evaluator Dispatch

**As a** developer using SpecOps on a platform with `canDelegateTask: true`
**I want** the dispatcher to instruct the evaluator sub-agent to use a different model when available
**So that** the evaluator and generator are structurally distinct, reducing self-confirmation bias

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN dispatching an evaluation sub-agent on a platform with `canDelegateTask: true`, THE SYSTEM SHALL include an instruction in the sub-agent prompt to use a different model than the generator when available
<!-- EARS: State-driven -->
- [x] WHILE on platforms with `canDelegateTask: false`, THE SYSTEM SHALL NOT include model diversity instructions (no behavioral change for non-delegating platforms)

### Deferred Criteria

- Automated detection of retroactive justification patterns (would require output parsing heuristics beyond simple structural checks)
- Per-project score distribution analysis across specs (requires persistent cross-spec evaluation data)

## Edge Cases

1. **All dimensions genuinely deserve the same score**: The variance enforcement forces re-evaluation, which is the desired behavior. If the re-evaluation still produces identical scores with distinct per-dimension justifications, the evaluator must adjust at least one score to reflect any identified finding (since mandatory findings will surface at least one gap per dimension).
2. **Dimension with only minor findings**: The evaluator must still identify at least one finding. Minor findings are acceptable -- the rule prevents zero-finding assessments, not low-severity ones.
3. **Platform lacks model diversity**: The instruction says "when available." If only one model is available, the evaluator proceeds normally -- no failure.
