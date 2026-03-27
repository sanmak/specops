# Feature: Adversarial Evaluation System

## Overview

Add structurally separated adversarial evaluation to the SpecOps workflow at two touchpoints: spec quality review (Phase 2 exit gate) and implementation quality review (Phase 4A). Both use scored quality dimensions (1-10) with hard thresholds, feedback loops with max iterations, and zero-progress detection. Enabled by default as a core quality guarantee.

Inspired by Anthropic's Planner-Generator-Evaluator harness architecture, which demonstrated that separating evaluation from generation -- using a skepticism-prompted evaluator with scored criteria and hard thresholds -- dramatically improves AI agent output quality.

## Product Requirements

### Requirement 1: Spec Evaluation (Phase 2 Exit Gate)

**As a** developer using SpecOps
**I want** spec artifacts to be adversarially evaluated before implementation begins
**So that** specification errors (vague criteria, missing edge cases, design gaps) are caught before they cascade into implementation

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN Phase 2 completes AND evaluation is enabled, THE SYSTEM SHALL dispatch a spec evaluation step that reads requirements, design.md, and tasks.md and scores 4 quality dimensions: Criteria Testability, Criteria Completeness, Design Coherence, and Task Coverage
<!-- EARS: Event-driven -->
- [x] WHEN any spec evaluation dimension scores below `minScore`, THE SYSTEM SHALL write specific, actionable feedback to `evaluation.md` and loop back to Phase 2 for spec revision
<!-- EARS: Event-driven -->
- [x] WHEN all spec evaluation dimensions score at or above `minScore`, THE SYSTEM SHALL proceed to Phase 3 dispatch
<!-- EARS: Event-driven -->
- [x] WHEN spec evaluation iterations reach `maxIterations` without all dimensions passing, THE SYSTEM SHALL notify the user with a failure summary and proceed to Phase 3 with an incomplete evaluation flag
<!-- EARS: Unwanted behavior -->
- [x] THE SYSTEM SHALL NOT allow the spec evaluator to rewrite requirements, design, or tasks directly -- it provides feedback only for the generator to act on

### Requirement 2: Implementation Evaluation (Phase 4A)

**As a** developer using SpecOps
**I want** implementation output to be adversarially evaluated by a fresh agent context before spec completion
**So that** real bugs, quality gaps, and spec deviations are caught by an evaluator that is structurally incentivized to find problems rather than confirm success

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN Phase 3 completes AND evaluation is enabled, THE SYSTEM SHALL dispatch Phase 4A as a fresh agent context (on platforms with `canDelegateTask: true`) with a hardcoded adversarial skepticism prompt
<!-- EARS: Event-driven -->
- [x] WHEN Phase 4A runs, THE SYSTEM SHALL read all spec artifacts and all modified files from implementation, score spec-type-specific quality dimensions (Feature: Functionality Depth, Design Fidelity, Code Quality, Test Verification; Bugfix: Root Cause Accuracy, Fix Completeness, Regression Safety, Test Verification; Refactor: Behavior Preservation, Structural Improvement, API Stability, Test Verification), and write results to `evaluation.md`
<!-- EARS: Event-driven -->
- [x] WHEN `canExecuteCode` is true AND `exerciseTests` is true, THE SYSTEM SHALL run the project's test suite during implementation evaluation and include test results in scoring
<!-- EARS: Event-driven -->
- [x] WHEN `canExecuteCode` is false, THE SYSTEM SHALL perform code-review-only evaluation and cap the Test Verification dimension score at 7
<!-- EARS: Unwanted behavior -->
- [x] THE SYSTEM SHALL NOT allow the evaluator to modify implementation code -- evaluation is read-only except for writing `evaluation.md` and updating the `spec.json` evaluation field

### Requirement 3: Feedback Loop and Remediation (Phase 4B)

**As a** developer using SpecOps
**I want** failed implementation evaluations to trigger targeted remediation with specific feedback
**So that** quality gaps are iteratively fixed rather than silently accepted

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN any implementation evaluation dimension scores below `minScore` AND iteration count is below `maxIterations`, THE SYSTEM SHALL write remediation instructions to `evaluation.md` scoped to specific tasks/files, and dispatch Phase 4B to re-enter Phase 3 with constrained scope (only failing-dimension tasks)
<!-- EARS: Event-driven -->
- [x] WHEN remediation completes, THE SYSTEM SHALL re-enter Phase 4A with an incremented iteration counter
<!-- EARS: Event-driven -->
- [x] WHEN no evaluation score improves between consecutive iterations (zero-progress detection), THE SYSTEM SHALL stop the feedback loop early and notify the user
<!-- EARS: Event-driven -->
- [x] WHEN iteration count reaches `maxIterations`, THE SYSTEM SHALL notify the user with a failure summary and proceed to Phase 4C with an incomplete evaluation flag

### Requirement 4: Quality Dimensions and Scoring Rubric

**As a** developer using SpecOps
**I want** quality to be measured on scored dimensions with a consistent rubric
**So that** evaluation produces concrete, gradable assessments rather than binary checkbox verification

**Acceptance Criteria (EARS):**

<!-- EARS: State-driven -->
- [x] WHILE evaluation is enabled, THE SYSTEM SHALL score each quality dimension on a 1-10 integer scale using the rubric: 9-10 (exceeds expectations), 7-8 (meets expectations), 5-6 (below expectations), 3-4 (significant problems), 1-2 (fundamentally broken)
<!-- EARS: State-driven -->
- [x] WHILE evaluation is enabled, THE SYSTEM SHALL use spec-type-specific dimensions: Feature (Functionality Depth, Design Fidelity, Code Quality, Test Verification), Bugfix (Root Cause Accuracy, Fix Completeness, Regression Safety, Test Verification), Refactor (Behavior Preservation, Structural Improvement, API Stability, Test Verification)
<!-- EARS: State-driven -->
- [x] WHILE evaluation is enabled, THE SYSTEM SHALL use spec evaluation dimensions for all spec types: Criteria Testability, Criteria Completeness, Design Coherence, Task Coverage
<!-- EARS: Unwanted behavior -->
- [x] THE SYSTEM SHALL NOT allow the adversarial prompts to be configured via `.specops.json` -- they are hardcoded in `core/evaluation.md` to prevent users from weakening the adversarial nature

### Requirement 5: Configuration

**As a** developer using SpecOps
**I want** evaluation behavior to be configurable per project
**So that** I can tune thresholds, iteration limits, and evaluation scope to match my project needs

**Acceptance Criteria (EARS):**

<!-- EARS: State-driven -->
- [x] WHILE no evaluation config is set, THE SYSTEM SHALL use defaults: `enabled: true`, `minScore: 7`, `maxIterations: 2`, `perTask: false`, `exerciseTests: true`
<!-- EARS: Event-driven -->
- [x] WHEN `evaluation.enabled` is set to `false`, THE SYSTEM SHALL skip both spec evaluation and implementation evaluation and use the existing Phase 4 checkbox verification behavior
<!-- EARS: Event-driven -->
- [x] WHEN `evaluation.perTask` is set to `true`, THE SYSTEM SHALL run implementation evaluation after each task instead of after all tasks
<!-- EARS: Event-driven -->
- [x] WHEN evaluation config is provided in `.specops.json`, THE SYSTEM SHALL validate it against the JSON schema (`additionalProperties: false`, integer constraints on `minScore` 1-10, `maxIterations` 1-5)

### Requirement 6: Platform Adaptation

**As a** developer using SpecOps on any supported platform
**I want** evaluation to adapt to each platform's capabilities
**So that** all 5 platforms benefit from evaluation regardless of delegation and code execution support

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN `canDelegateTask` is true, THE SYSTEM SHALL run both spec and implementation evaluation as fresh sub-agents (structural adversarial separation)
<!-- EARS: Event-driven -->
- [x] WHEN `canDelegateTask` is false AND `canAskInteractive` is true, THE SYSTEM SHALL run evaluation in the same context with strong skepticism prompting, and prompt the user for a fresh session if remediation is needed
<!-- EARS: Event-driven -->
- [x] WHEN both `canDelegateTask` and `canAskInteractive` are false, THE SYSTEM SHALL run evaluation sequentially in the same context with skepticism prompting to compensate for shared context

### Requirement 7: Pipeline Mode Integration

**As a** developer using SpecOps pipeline mode
**I want** evaluation to integrate with the pipeline's Phase 3/4 cycling
**So that** automated implementation cycling uses quality scores instead of checkbox-only verification

**Acceptance Criteria (EARS):**

<!-- EARS: Event-driven -->
- [x] WHEN pipeline mode runs with evaluation enabled, THE SYSTEM SHALL use implementation evaluation scores as the pass/fail signal for each cycle (replacing checkbox-only verification)
<!-- EARS: Event-driven -->
- [x] WHEN pipeline mode runs with evaluation disabled, THE SYSTEM SHALL preserve the existing checkbox-based pass/fail behavior
<!-- EARS: Event-driven -->
- [x] WHEN pipeline mode starts, THE SYSTEM SHALL run spec evaluation once before the first cycle (since the spec is already written)

## Product Quality Attributes

- Evaluation module MUST be kept concise (<5KB rendered content) to avoid context window exhaustion on non-delegation platforms
- Spec evaluation MUST be read-only (no test execution) to keep it fast
- Both evaluation touchpoints MUST produce structured output in `evaluation.md` with iteration history preserved (append, not overwrite)
- Machine-readable evaluation results MUST be stored in `spec.json` for downstream tooling
- All generated platform outputs MUST include evaluation markers (validated by `generator/validate.py`)

## Scope Boundary

This spec covers the evaluation system within the SpecOps workflow. It does NOT cover:
- Custom user-defined quality dimensions (future enhancement)
- Auto-mode that skips evaluation for simple specs below a complexity threshold (future enhancement)
- Integration with external QA tools or CI systems beyond running the project's test suite
- Evaluation of non-spec artifacts (e.g., standalone code review outside the spec workflow)

## Constraints

- Must follow the three-tier architecture: new content in `core/evaluation.md`, platform adapters map abstract operations, generated outputs include evaluation instructions
- Must not change the 4-phase numbering (Phase 1-4) -- evaluation is internal restructuring within Phase 2's exit gate and Phase 4's sub-phases
- `EVALUATION_MARKERS` must be added to `validate_platform()`, cross-platform consistency loop, AND `tests/test_platform_consistency.py` in the same commit (per CLAUDE.md rule)
- JSON schema objects must use `additionalProperties: false`; string fields need `maxLength`; arrays need `maxItems`
- After changing `core/`, `generator/templates/`, or any `platform.json`: must run `python3 generator/generate.py --all` and commit regenerated files alongside changes
