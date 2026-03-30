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

### Confidence Tiers for Findings

Each finding produced during evaluation (spec or implementation) carries a confidence classification that determines its evidence requirements and scoring impact.

| Tier | Range | Evidence Requirements | Scoring Impact |
| ------ | ------- | ---------------------- | ---------------- |
| HIGH | >= 0.80 | (1) Specific file path and line reference, (2) quoted or described code passage, (3) concrete consequence or impact statement. All three required. | Counts toward pass/fail scoring |
| MODERATE | 0.60-0.79 | (1) File path or code pattern reference, (2) likely impact statement. Both required. | Counts toward pass/fail scoring |
| LOW | < 0.60 | No minimum evidence required | Advisory only -- excluded from pass/fail scoring |

**Evidence validation rules:**

- If a HIGH confidence finding is missing any of the three required evidence elements, downgrade it to MODERATE and append: "Downgraded from HIGH -- missing [element]."
- LOW confidence findings are prefixed with `[Advisory]` in the evaluation report and do not affect dimension pass/fail determination or trigger remediation instructions.
- LOW confidence findings satisfy the "mandatory finding per dimension" rule only when no MODERATE or HIGH findings exist for that dimension. If at least one MODERATE or HIGH finding exists, LOW findings are supplementary.
- Dimension scores are computed from HIGH and MODERATE confidence findings only. LOW findings provide context but do not influence the score.

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
4. Confidence classification: For each finding, assign a confidence value (0.00-1.00).
   - HIGH (>= 0.80): You can point to a specific file:line, quote the code, and describe
     a concrete consequence. All three must be present.
   - MODERATE (0.60-0.79): You can reference a file or pattern and describe a likely impact.
   - LOW (< 0.60): You suspect an issue but cannot point to specific evidence. Mark as
     [Advisory]. These do not affect the dimension score.
   If you assign HIGH but cannot provide all three evidence elements, downgrade to MODERATE.
```

**Procedure:**

1. READ_FILE the requirements file (requirements.md, bugfix.md, or refactor.md), design.md, and tasks.md.
2. For each spec evaluation dimension:
   a. List specific evidence: quote or reference the artifact section, line, or passage that is relevant to this dimension.
   b. List findings: identify at least one concrete finding (gap, risk, or improvement opportunity) for this dimension. "No issues found" is not acceptable evidence.
   c. Assign a score (1-10 integer) based on HIGH and MODERATE confidence findings only. LOW confidence findings are excluded from score computation. If the findings list is empty or contains only "No issues found" or equivalent language, cap the score at (`minScore` - 1) and append: "Score capped below threshold -- no concrete finding identified for this dimension."
   c.5. For each finding listed in step b, assign a confidence tier (HIGH/MODERATE/LOW) with a numeric value (0.00-1.00). Validate evidence requirements per the Confidence Tiers table above. If a finding is classified HIGH but is missing any of the three required evidence elements, downgrade to MODERATE and note the reason. If a finding is classified LOW (< 0.60), prefix it with `[Advisory]` in the evaluation report — it does not affect the dimension score.
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
4. Confidence classification: For each finding, assign a confidence value (0.00-1.00).
   - HIGH (>= 0.80): You can point to a specific file:line, quote the code, and describe
     a concrete consequence. All three must be present.
   - MODERATE (0.60-0.79): You can reference a file or pattern and describe a likely impact.
   - LOW (< 0.60): You suspect an issue but cannot point to specific evidence. Mark as
     [Advisory]. These do not affect the dimension score.
   If you assign HIGH but cannot provide all three evidence elements, downgrade to MODERATE.
```

**Procedure:**

1. READ_FILE the requirements file, design.md, tasks.md, and implementation.md.
2. READ_FILE each file listed in the implementation.md Session Log "Files to Modify" entries to inspect the actual implementation.
3. If `canExecuteCode` is true AND `config.implementation.evaluation.exerciseTests` is true: RUN_COMMAND to execute the project's test suite. Record test output (pass count, fail count, specific failures).
4. If `canExecuteCode` is false: note "Tests not exercised -- code review only" and cap the Test Verification dimension score at 7 (cannot verify higher without running tests).
5. For each dimension (selected by spec type from the tables above):
   a. List specific evidence: cite file paths, line references, code quotes, or test output that are relevant to this dimension.
   b. List findings: identify at least one concrete finding (gap, risk, or improvement opportunity) for this dimension. "No issues found" is not acceptable evidence.
   c. Assign a score (1-10 integer) based on HIGH and MODERATE confidence findings only. LOW confidence findings are excluded from score computation. If the findings list is empty or contains only "No issues found" or equivalent language, cap the score at (`minScore` - 1) and append: "Score capped below threshold -- no concrete finding identified for this dimension."
   c.5. For each finding listed in step b, assign a confidence tier (HIGH/MODERATE/LOW) with a numeric value (0.00-1.00). Validate evidence requirements per the Confidence Tiers table. If a finding is classified HIGH but is missing any required evidence element, downgrade to MODERATE and note the reason. If a finding is classified LOW (< 0.60), prefix it with `[Advisory]` — it does not affect the dimension score.
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

### Multi-Persona Review Integration

After the implementation evaluator completes dimension scoring (step 4A.2), the multi-persona review system runs as step 4A.2.5. The full protocol is defined in `core/review-agents.md`.

**Combined verdict logic:**

- **PASS**: All dimensions score at or above `minScore` AND no P0/P1 findings with HIGH or MODERATE confidence exist from the multi-persona review.
- **FAIL**: Any dimension scores below `minScore` OR any P0/P1 finding with HIGH or MODERATE confidence exists from the multi-persona review.
- Persona findings can override a dimension-score pass to fail, but cannot upgrade a fail to pass.
- LOW confidence findings from persona reviewers are advisory only and never contribute to a fail verdict.

When the multi-persona review triggers remediation (P0/P1 HIGH/MODERATE findings while dimensions pass), the remediation context includes the specific persona findings -- finding IDs, severities, evidence, and remediation instructions -- not just dimension scores.

**Depth calibration**: If the depth flag is `lightweight`, skip the multi-persona review entirely. The existing dimension scoring is sufficient for lightweight specs.

### Action Routing for Findings

After finding aggregation (dimension findings from the adversarial evaluator + persona findings from the multi-persona review), the action router classifies each finding into a fix class that determines how remediation handles it. Action routing is always active when evaluation is enabled -- there is no separate config switch.

**Fix class definitions:**

| Fix Class | Description | Agent Behavior |
| --- | --- | --- |
| `auto_fix` | Deterministic, narrow scope, low risk. Agent fixes without asking. | Apply fix immediately during Phase 4B. No developer interaction. |
| `gated_fix` | Deterministic but wider scope or moderate risk. Agent proposes, developer approves in batch. | Collect all gated fixes and present as a single batch for approval. |
| `manual` | Non-deterministic, architectural, or high risk. Flagged for developer, no agent fix. | Report finding with full details. Do not attempt a fix. |
| `advisory` | Informational only. No fix expected. | Include in evaluation report. No action taken. |

Examples by fix class:

- **auto_fix**: Missing import statement, formatting violation, naming convention deviation, missing test assertion, trivial comment typo
- **gated_fix**: Renaming a function across 3+ files, adding error handling to multiple call sites, updating multiple test files for a new parameter
- **manual**: Changing architectural patterns, resolving ambiguous requirement interpretation, security vulnerability remediation requiring design judgment
- **advisory**: LOW confidence findings, P3 style observations, potential future improvements

**Routing signals:**

Each finding is assessed on three signals before applying the Routing Decision Matrix:

1. **Fix Determinism**: Can the agent reliably generate the correct fix?
   - *Deterministic*: Only one correct fix exists (e.g., "add missing import X to file Y")
   - *Non-deterministic*: Multiple valid approaches exist (e.g., "refactor error handling strategy")

2. **Fix Scope**: How many files does the fix affect?
   - *Narrow*: 1-2 files
   - *Wide*: 3 or more files

3. **Fix Risk**: Could the fix introduce regressions?
   - *Low*: Isolated change, no callers affected, no behavioral change
   - *Moderate*: Change affects known callers but behavior is preserved
   - *High*: Change may alter observable behavior or requires architectural judgment

**Routing Decision Matrix:**

| Fix Determinism | Fix Scope | Fix Risk | Fix Class |
| --- | --- | --- | --- |
| Deterministic | Narrow | Low | auto_fix |
| Deterministic | Narrow | Moderate | gated_fix |
| Deterministic | Wide | Low | gated_fix |
| Deterministic | Wide | Moderate | gated_fix |
| Deterministic | Any | High | manual |
| Non-deterministic | Any | Any | manual |

**Override rules** (applied after the matrix):

- **LOW confidence override**: Any finding with confidence < 0.60 (LOW tier) is classified as `advisory` regardless of the matrix result. LOW confidence findings lack sufficient evidence for any fix attempt.
- **P3 severity override**: Any finding with severity P3 is classified as `advisory`, unless the matrix already yielded `auto_fix` (trivial fixes should still be auto-fixed even at P3).

**Routing procedure** (for each finding after aggregation):

1. If the finding has LOW confidence (< 0.60): classify as `advisory`. Done.
2. Assess Fix Determinism: READ_FILE the finding's evidence and remediation instruction. If the remediation specifies a single, unambiguous change (add line X, rename Y to Z, delete line N), classify as deterministic. If the remediation describes a strategy or lists alternatives, classify as non-deterministic.
3. Assess Fix Scope: count the number of distinct files referenced in the finding's evidence and remediation. If 1-2 files, classify as narrow. If 3+, classify as wide.
4. Assess Fix Risk: if the fix changes only comments, formatting, imports, or test-only code, classify as low risk. If the fix changes implementation logic but preserves the same API surface, classify as moderate risk. If the fix changes public interfaces, removes functionality, or requires design judgment, classify as high risk.
5. Apply the Routing Decision Matrix to get the base fix class.
6. Apply override rules: if severity is P3 and base class is not `auto_fix`, reclassify as `advisory`.
7. Record the fix class, routing signals, and rationale in the evaluation report.

**Auto-fix execution protocol** (Phase 4B):

1. Collect all findings classified as `auto_fix`.
2. For each auto_fix finding, in order:
   a. EDIT_FILE to apply the fix as specified in the finding's remediation instruction.
   b. If `canExecuteCode` is true, RUN_COMMAND the project's test suite. If any test that was previously passing now fails, the auto-fix introduced a regression.
   c. If the fix succeeds (no edit errors, no test regressions): log the fix in `implementation.md` as "Auto-fixed: [finding ID] -- [description]".
   d. If the fix fails (edit error or test regression): revert the change, reclassify the finding as `gated_fix`, and log "Auto-fix failed for [finding ID] -- reclassified as gated_fix. Reason: [error/regression details]".
3. After all auto_fix items are processed, proceed to gated_fix batching.

**Gated fix batching protocol** (Phase 4B, after auto-fix):

1. Collect all findings classified as `gated_fix` (including those reclassified from failed auto-fixes).
2. If `canAskInteractive` is true: present all gated fixes as a single batch to the developer via ASK_USER. For each finding, show: finding ID, description, proposed change (file path + change summary), and risk assessment. The developer can approve all, reject all, or selectively approve individual fixes.
3. If `canAskInteractive` is false: treat all `gated_fix` items as `auto_fix` and apply them without asking. On non-interactive platforms, the developer reviews changes in the git diff after completion.
4. Apply approved gated fixes. Log each in `implementation.md`.
5. Rejected gated fixes are reclassified as `manual` and reported to the developer.

**Manual and advisory reporting** (Phase 4B, after gated fixes):

1. `manual` findings: NOTIFY_USER with each manual finding's ID, severity, confidence, evidence, and description. Note that no agent fix is attempted.
2. `advisory` findings: include in the evaluation report Action Routing Summary section. No notification or action required.

### Feedback Loop

**Spec evaluation feedback (Phase 2 revision):**

When spec evaluation fails, the evaluator has written specific feedback to `evaluation.md`. The revision step:

1. READ_FILE `<specsDir>/<spec-name>/evaluation.md` to get the failing dimensions and remediation instructions.
2. For each failing dimension: revise the corresponding artifact (requirements, design, or tasks) following the remediation instructions.
3. After revisions: re-run spec evaluation (increment iteration counter).

**Implementation evaluation feedback (Phase 4B remediation):**

When implementation evaluation fails, the evaluator has written remediation instructions scoped to specific tasks and files. The remediation step uses action routing to classify and handle findings by fix class:

1. READ_FILE `<specsDir>/<spec-name>/evaluation.md` to get the failing dimensions, remediation instructions, and (if present) persona findings with finding IDs, evidence, and remediation instructions.
2. **Action routing classification**: For each finding (dimension-based or persona-based), apply the Action Routing procedure to classify it into a fix class (auto_fix, gated_fix, manual, advisory).
3. **Auto-fix execution**: Apply all `auto_fix` classified findings immediately following the auto-fix execution protocol. Log results in `implementation.md`.
4. **Gated fix batching**: Present all `gated_fix` findings as a batch for developer approval (or auto-apply on non-interactive platforms) following the gated fix batching protocol.
5. **Manual reporting**: Report all `manual` findings to the developer with full context. Do not attempt fixes.
6. **Advisory reporting**: Include `advisory` findings in the evaluation report for context. No action taken.
7. For dimension failures not addressed by auto-fix or gated-fix (e.g., broad code quality issues), identify which tasks in tasks.md relate to the failing dimensions and re-implement those tasks following the remediation instructions.
8. After remediation: re-run Phase 4A implementation evaluation (increment iteration counter).

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
4. **Hardcoded prompts**: The adversarial evaluator prompts are defined in this module and MUST NOT be overridden via `.specops.json` or any other configuration mechanism. The multi-persona review module's prompts are defined in `core/review-agents.md` and MUST NOT be overridden.
5. **Append-only history**: If `evaluation.md` already exists from a prior iteration, append the new iteration under the appropriate section. Do not overwrite prior iteration data — the full evaluation trail must be preserved.
6. **Iteration limits**: The `maxIterations` configuration value MUST be respected. Exceeding it is a protocol breach.
