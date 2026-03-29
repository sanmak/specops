## Adversarial Evaluation

The adversarial evaluation system adds structurally separated quality scoring to the SpecOps workflow at two touchpoints: spec evaluation (Phase 2 exit gate) and implementation evaluation (Phase 4A). Both use scored quality dimensions with hard thresholds and feedback loops. Evaluation is enabled by default.

The core principle: agents reliably praise their own work. Separating the evaluator from the generator — using a fresh context with explicit skepticism prompting — creates a feedback loop that drives output quality up.

### Evaluation Configuration

Read evaluation settings from `config.implementation.evaluation`. If absent, use defaults:

```json
{
  "enabled": true,
  "minScore": 7,
  "maxIterations": 2,
  "perTask": false,
  "exerciseTests": true
}
```

- `enabled`: Master switch. When false, skip both evaluation touchpoints and use legacy Phase 4 checkbox verification.
- `minScore`: Minimum dimension score (1-10) to pass. Any dimension below this triggers remediation.
- `maxIterations`: Maximum evaluation-remediation cycles before proceeding (1-5).
- `perTask`: When true, run implementation evaluation after each task instead of after all tasks.
- `exerciseTests`: When true, the implementation evaluator runs the project test suite.

### Scoring Rubric

All quality dimensions use this 1-10 integer scale:

| Score | Meaning |
| ------- | --------- |
| 9-10 | Exceeds expectations. Thorough, well-considered, production-ready. |
| 7-8 | Meets expectations. Solid implementation with minor gaps. |
| 5-6 | Below expectations. Notable gaps that should be addressed. |
| 3-4 | Significant problems. Core requirements partially unmet. |
| 1-2 | Fundamentally broken. Does not address the spec. |

### Spec Evaluation Protocol

Spec evaluation runs at the Phase 2 exit boundary — after Phase 2 produces spec artifacts but before Phase 3 dispatch. It verifies that the specification is clear, complete, and implementable.

**Spec evaluation dimensions (all spec types):**

| Dimension | What it measures | Scoring guidance |
| ----------- | ----------------- | ------------------ |
| Criteria Testability | Are acceptance criteria specific, verifiable, and unambiguous? | 7+: each criterion has a binary observable outcome. Below 7: criteria use subjective terms ("works well", "fast enough") without measurable thresholds. |
| Criteria Completeness | Do criteria cover happy path, edge cases, and error states? | 7+: happy path and at least 2 edge cases per requirement. Below 7: only happy path covered, or obvious failure modes missing. |
| Design Coherence | Does the design address all requirements? Are decisions justified? | 7+: every requirement maps to a design element with rationale; if design.md references new dependencies, a ### Dependency Decisions section is present with evaluated rationale. Below 7: requirements without corresponding design, decisions without rationale, or dependencies introduced without evaluation. |
| Task Coverage | Do tasks cover all design components? Are dependencies ordered correctly? | 7+: every design component has at least one task, dependencies form a valid DAG. Below 7: design elements without tasks, or circular/missing dependencies. |

**Spec evaluator prompt** (hardcoded — not configurable via `.specops.json`):

```text
You are a spec quality evaluator. Your job is to find gaps in the specification BEFORE
implementation begins. Errors in the spec cascade into implementation.
Check: Are criteria actually testable? Are edge cases covered? Does the design address
every requirement? Are tasks properly scoped?
Score honestly — a vague spec that passes review will produce a vague implementation.
Do not rewrite the spec artifacts. Provide specific, actionable feedback only.

STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each dimension, list specific evidence (file paths, line references,
   code quotes, section references) BEFORE assigning a score. The score must follow from
   the evidence.
2. Mandatory finding: Each dimension MUST identify at least one concrete finding (gap, risk,
   or improvement opportunity). "No issues found" is not acceptable. If you cannot identify
   a finding, your score for that dimension is capped below the passing threshold.
3. Score variance: If all your dimension scores are identical, your evaluation auto-fails
   and you must re-evaluate with distinct per-dimension justification.
```

**Procedure:**

1. READ_FILE the requirements file (requirements.md, bugfix.md, or refactor.md), design.md, and tasks.md.
2. For each spec evaluation dimension:
   a. List specific evidence: quote or reference the artifact section, line, or passage that is relevant to this dimension.
   b. List findings: identify at least one concrete finding (gap, risk, or improvement opportunity) for this dimension. "No issues found" is not acceptable evidence.
   c. Assign a score (1-10 integer) that follows from the evidence and findings above. If the findings list is empty or contains only "No issues found" or equivalent language, cap the score at (`minScore` - 1) and append: "Score capped below threshold -- no concrete finding identified for this dimension."
   d. If below `config.implementation.evaluation.minScore`: write a concrete remediation instruction (e.g., "Acceptance criterion 3 uses 'works well' -- specify a measurable threshold such as response time < 200ms").
3. **Score variance check**: After all dimensions are scored, check whether all dimension scores are identical.
   - If all scores are identical on the first attempt, record "Uniform scores detected -- re-evaluate with distinct per-dimension justification" and re-run once from step 2.
   - If scores are still identical after one re-run, treat the evaluation as failed for this iteration and continue with normal iteration accounting (`maxIterations` applies).
4. WRITE_FILE `<specsDir>/<spec-name>/evaluation.md` using the Evaluation Report Template. If the file already exists, append the new iteration (do not overwrite prior iterations).
5. EDIT_FILE `<specsDir>/<spec-name>/spec.json` to update the `evaluation.spec` object with `iterations`, `passed`, `scores`, and `evaluatedAt`.
6. If ALL dimensions score at or above `minScore`: evaluation passes -- signal for Phase 3 dispatch.
7. If ANY dimension scores below `minScore` AND current iteration < `maxIterations`: evaluation fails -- signal for Phase 2 revision with evaluation.md feedback as input context.
8. If ANY dimension scores below `minScore` AND current iteration >= `maxIterations`: NOTIFY_USER("Spec evaluation did not pass after {iterations} iterations. Proceeding to implementation with known spec gaps: {list of failing dimensions}.") and signal for Phase 3 dispatch with an incomplete evaluation flag.

**Spec evaluator safety rules:**

- The evaluator MUST NOT rewrite requirements, design, or tasks directly. It provides feedback only.
- The evaluator MUST NOT modify any file other than `evaluation.md` and the `spec.json` `evaluation` field.

### Implementation Evaluation Protocol

Implementation evaluation runs as Phase 4A — after Phase 3 completes but before completion steps. It verifies that the implementation matches the spec with quality.

**Implementation evaluation dimensions by spec type:**

**Feature specs:**

| Dimension | What it measures | Scoring guidance |
| ----------- | ----------------- | ------------------ |
| Functionality Depth | Full spec coverage, not just happy path | 7+: all acceptance criteria addressed with implementation evidence. Below 7: criteria checked without corresponding code, or happy-path-only implementation. |
| Design Fidelity | Implementation matches design.md decisions | 7+: each design decision reflected in code; packages introduced by this spec match the approved list in design.md ### Dependency Decisions. Below 7: design decisions ignored or contradicted without documented deviation, or spec-introduced packages not in the approved dependency list. |
| Code Quality | Clean architecture, appropriate abstractions | 7+: no obvious code smells, functions focused, naming clear. Below 7: duplicated logic, unclear naming, overly complex control flow. |
| Test Verification | Tests run and pass, adequate coverage | 7+: tests exist and pass for core functionality. Below 7: no tests, failing tests, or tests that do not exercise the implementation. |

**Bugfix specs:**

| Dimension | What it measures | Scoring guidance |
| ----------- | ----------------- | ------------------ |
| Root Cause Accuracy | Actual root cause addressed, not symptoms | 7+: fix targets the identified root cause. Below 7: fix addresses symptoms only, or root cause analysis is absent. |
| Fix Completeness | All bug manifestations handled | 7+: all reported manifestations verified fixed. Below 7: some manifestations still reproducible, or related paths untested. |
| Regression Safety | Must-Test behaviors from risk analysis preserved | 7+: Regression Risk Analysis Must-Test items verified. Below 7: Must-Test behaviors not checked, or existing tests broken. |
| Test Verification | Reproduction, fix, and regression tests pass | 7+: reproduction test confirms fix, regression tests pass. Below 7: no reproduction test, or regression tests skipped. |

**Refactor specs:**

| Dimension | What it measures | Scoring guidance |
| ----------- | ----------------- | ------------------ |
| Behavior Preservation | Existing functionality unchanged | 7+: all existing tests pass, no behavioral change. Below 7: existing tests fail, or observable behavior changed. |
| Structural Improvement | Code measurably better organized | 7+: clear reduction in complexity, duplication, or coupling. Below 7: no measurable improvement, or new complexity introduced. |
| API Stability | Public interfaces preserved or properly migrated | 7+: public APIs unchanged, or migration path provided. Below 7: breaking changes without migration, or undocumented API changes. |
| Test Verification | All existing tests pass, new structural tests added | 7+: existing tests pass, new tests cover structural changes. Below 7: existing tests fail, or structural changes untested. |

**Implementation evaluator prompt** (hardcoded — not configurable via `.specops.json`):

```text
You are an adversarial evaluator. Your job is to FIND PROBLEMS, not confirm success.
Assume the implementation has flaws until proven otherwise.
Do not take the implementer's word for anything — verify by reading code and running tests.
Score honestly. 7 means "acceptable." 5 means "significant gaps." 3 means "broken."
If you cannot verify a dimension (e.g., no tests exist to run), score lower, not higher.

STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each dimension, list specific evidence (file paths, line references,
   code quotes, test output) BEFORE assigning a score. The score must follow from the evidence.
2. Mandatory finding: Each dimension MUST identify at least one concrete finding (gap, risk,
   or improvement opportunity). "No issues found" is not acceptable. If you cannot identify
   a finding, your score for that dimension is capped below the passing threshold.
3. Score variance: If all your dimension scores are identical, your evaluation auto-fails
   and you must re-evaluate with distinct per-dimension justification.
```

**Procedure:**

1. READ_FILE the requirements file, design.md, tasks.md, and implementation.md.
2. READ_FILE each file listed in the implementation.md Session Log "Files to Modify" entries to inspect the actual implementation.
3. If `canExecuteCode` is true AND `config.implementation.evaluation.exerciseTests` is true: RUN_COMMAND to execute the project's test suite. Record test output (pass count, fail count, specific failures).
4. If `canExecuteCode` is false: note "Tests not exercised -- code review only" and cap the Test Verification dimension score at 7 (cannot verify higher without running tests).
5. For each dimension (selected by spec type from the tables above):
   a. List specific evidence: cite file paths, line references, code quotes, or test output that are relevant to this dimension.
   b. List findings: identify at least one concrete finding (gap, risk, or improvement opportunity) for this dimension. "No issues found" is not acceptable evidence.
   c. Assign a score (1-10 integer) that follows from the evidence and findings above. If the findings list is empty or contains only "No issues found" or equivalent language, cap the score at (`minScore` - 1) and append: "Score capped below threshold -- no concrete finding identified for this dimension."
   d. If below `minScore`: write a concrete remediation instruction scoped to specific tasks and files.
6. **Score variance check**: After all dimensions are scored, check whether all dimension scores are identical.
   - If all scores are identical on the first attempt, record "Uniform scores detected -- re-evaluate with distinct per-dimension justification" and re-run once from step 5.
   - If scores are still identical after one re-run, treat the evaluation as failed for this iteration and continue with normal iteration accounting (`maxIterations` applies).
7. WRITE_FILE (or append to) `<specsDir>/<spec-name>/evaluation.md` with the implementation evaluation iteration. Append under the `## Implementation Evaluation` section.
8. EDIT_FILE `<specsDir>/<spec-name>/spec.json` to update the `evaluation.implementation` object.
9. If ALL dimensions score at or above `minScore`: evaluation passes -- proceed to Phase 4C (completion steps).
10. If ANY dimension scores below `minScore` AND current iteration < `maxIterations`: evaluation fails -- signal Phase 4B (remediation).
11. If ANY dimension scores below `minScore` AND current iteration >= `maxIterations`: NOTIFY_USER("Implementation evaluation did not pass after {iterations} iterations. Proceeding to completion with known quality gaps: {list of failing dimensions and scores}.") and proceed to Phase 4C.

**Implementation evaluator safety rules:**

- The evaluator MUST NOT modify implementation code. Evaluation is read-only except for `evaluation.md` and `spec.json`.
- The evaluator MUST NOT mark the spec as completed. Only Phase 4C can set status to `completed`.
- The evaluator MUST NOT change acceptance criteria checkboxes. Checkbox verification is a Phase 4C responsibility.

### Feedback Loop

**Spec evaluation feedback (Phase 2 revision):**

When spec evaluation fails, the evaluator has written specific feedback to `evaluation.md`. The revision step:

1. READ_FILE `<specsDir>/<spec-name>/evaluation.md` to get the failing dimensions and remediation instructions.
2. For each failing dimension: revise the corresponding artifact (requirements, design, or tasks) following the remediation instructions.
3. After revisions: re-run spec evaluation (increment iteration counter).

**Implementation evaluation feedback (Phase 4B remediation):**

When implementation evaluation fails, the evaluator has written remediation instructions scoped to specific tasks and files. The remediation step:

1. READ_FILE `<specsDir>/<spec-name>/evaluation.md` to get the failing dimensions and remediation instructions.
2. Identify which tasks in tasks.md relate to the failing dimensions (the evaluator specifies this in the remediation section).
3. Re-implement only the failing-dimension tasks following the remediation instructions. Do not re-implement tasks whose dimensions passed.
4. After remediation: re-run Phase 4A implementation evaluation (increment iteration counter).

**Zero-progress detection:**

Before starting a new evaluation iteration, compare the current dimension scores against the previous iteration's scores. If no dimension improved by more than 0.5 points compared to the prior iteration, the feedback loop is stuck:

- NOTIFY_USER("Evaluation feedback loop made no progress — scores unchanged after iteration {N}. Stopping to avoid infinite loop.")
- Proceed to Phase 4C (for implementation evaluation) or Phase 3 dispatch (for spec evaluation) with an incomplete evaluation flag.

### Platform Adaptation

Evaluation behavior adapts to platform capability flags:

| Capability | Spec Evaluation Behavior | Implementation Evaluation Behavior |
| ------------ | ------------------------- | ----------------------------------- |
| `canDelegateTask: true` | Dispatch as a fresh sub-agent. The evaluator gets a clean context with spec artifacts and the adversarial prompt. This is the strongest separation mode. | Dispatch Phase 4A as a fresh sub-agent. The evaluator does not see the generator's session history. |
| `canDelegateTask: false`, `canAskInteractive: true` | Run in the same context with the adversarial prompt prepended to the evaluation instructions. If remediation is needed, write feedback to evaluation.md and prompt the user to start a fresh session. | Run Phase 4A in the same context with adversarial prompt. If remediation is needed, write feedback and prompt the user. |
| `canDelegateTask: false`, `canAskInteractive: false` | Run sequentially in the same context. Adversarial prompt compensates for shared context. Remediation runs sequentially. | Run sequentially. Adversarial prompt compensates. Remediation runs sequentially. |
| `canExecuteCode: true` | Not applicable (spec evaluation is read-only). | Run the test suite. Full Test Verification scoring. |
| `canExecuteCode: false` | Not applicable. | Code review only. Test Verification dimension capped at 7 with note "Tests not exercised." |

### Evaluation Safety

These rules are mandatory and cannot be overridden by configuration:

1. **Read-only evaluation**: The evaluator MUST NOT modify implementation code, spec artifacts (requirements, design, tasks), or any project file other than `evaluation.md` and the `spec.json` `evaluation` field.
2. **No completion authority**: The evaluator MUST NOT set spec status to `completed`. Only Phase 4C completion steps can do this.
3. **No checkbox manipulation**: The evaluator MUST NOT check or uncheck acceptance criteria checkboxes. Checkbox verification is Phase 4C's responsibility.
4. **Hardcoded prompts**: The adversarial evaluator prompts are defined in this module and MUST NOT be overridden via `.specops.json` or any other configuration mechanism.
5. **Append-only history**: If `evaluation.md` already exists from a prior iteration, append the new iteration under the appropriate section. Do not overwrite prior iteration data — the full evaluation trail must be preserved.
6. **Iteration limits**: The `maxIterations` configuration value MUST be respected. Exceeding it is a protocol breach.
