# Tasks: Adversarial Evaluation System

## Task 1: Create core/evaluation.md module

**Status:** Completed
**Priority:** High
**Effort:** L
**Domain:** core
**IssueID:** #205
**Dependencies:** None
**Ship Blocking:** Yes

**Description:**
Create the primary evaluation core module containing: spec evaluation protocol, implementation evaluation protocol, quality dimensions definitions per spec type, scoring rubric (1-10 scale), hardcoded adversarial prompts (spec evaluator + implementation evaluator), feedback loop mechanics (failure detection, remediation scoping, re-dispatch, zero-progress detection), platform adaptation table, and evaluation safety rules. All instructions must use abstract operations (READ_FILE, WRITE_FILE, RUN_COMMAND, NOTIFY_USER, etc.) per the three-tier architecture.

**Implementation Steps:**
1. Create `core/evaluation.md` with the following sections:
   - Adversarial Evaluation Overview (what, when, backward compatibility)
   - Spec Evaluation Protocol (Phase 2 exit gate procedure)
   - Implementation Evaluation Protocol (Phase 4A procedure)
   - Quality Dimensions (spec evaluation: 4 universal dimensions; implementation evaluation: 4 per spec type)
   - Scoring Rubric (1-10 scale with descriptors)
   - Feedback Loop Mechanics (spec revision loop, implementation remediation loop, zero-progress detection, max iterations)
   - Platform Adaptation (canDelegateTask, canAskInteractive, canExecuteCode behavior matrix)
   - Evaluation Safety Rules (read-only, no completion, no checkbox changes, hardcoded prompts, append-only history)
2. Include the hardcoded adversarial prompts verbatim (spec evaluator prompt + implementation evaluator prompt)
3. Define the evaluation.md artifact structure (both spec and implementation sections with iteration history)

**Acceptance Criteria:**
- [x] Module uses only abstract operations (no platform-specific tool names)
- [x] Spec evaluation procedure covers all 4 dimensions with scoring instructions
- [x] Implementation evaluation procedure covers all 3 spec types with 4 dimensions each
- [x] Feedback loop includes zero-progress detection and max iteration handling
- [x] Platform adaptation covers all 3 capability combinations
- [x] Safety rules are explicit and imperative (not advisory)
- [x] Module content is under 5KB to avoid context window pressure

**Files to Modify:**
- `core/evaluation.md` (new file)

**Tests Required:**
- [x] Validation markers present after regeneration
- [x] No abstract operations left unsubstituted in generated outputs

---

## Task 2: Create core/templates/evaluation.md report template

**Status:** Completed
**Priority:** High
**Effort:** S
**Domain:** core
**IssueID:** #206
**Dependencies:** Task 1
**Ship Blocking:** Yes

**Description:**
Create the evaluation report template that lives in the spec directory. Includes both spec evaluation and implementation evaluation sections, with iteration tables showing dimension scores, thresholds, pass/fail, and findings.

**Implementation Steps:**
1. Create `core/templates/evaluation.md` with template structure for both sections
2. Include table format for dimension scores per iteration
3. Include verdict and remediation instruction sections
4. Include test exercise results section (for implementation evaluation)

**Acceptance Criteria:**
- [x] Template has `## Spec Evaluation` and `## Implementation Evaluation` sections
- [x] Each iteration shows dimension scores in a table with Pass/Fail column
- [x] Verdict section shows overall PASS/FAIL with counts
- [x] Remediation section has placeholder for specific, actionable instructions

**Files to Modify:**
- `core/templates/evaluation.md` (new file)

**Tests Required:**
- [x] Template renders correctly when populated

---

## Task 3: Update schema.json and spec-schema.json

**Status:** Completed
**Priority:** High
**Effort:** M
**Domain:** schema
**IssueID:** #207
**Dependencies:** Task 1
**Ship Blocking:** Yes

**Description:**
Add the evaluation configuration schema under `implementation.evaluation` in `schema.json` and the evaluation results schema to `spec-schema.json`. Both must use `additionalProperties: false` per project rules.

**Implementation Steps:**
1. Add `evaluation` object to `schema.json` under `implementation.properties`:
   - `enabled` (boolean, default: true)
   - `minScore` (integer, min: 1, max: 10, default: 7)
   - `maxIterations` (integer, min: 1, max: 5, default: 2)
   - `perTask` (boolean, default: false)
   - `exerciseTests` (boolean, default: true)
2. Add `evaluation` object to `spec-schema.json` with `spec` and `implementation` sub-objects:
   - Each with `iterations` (integer), `passed` (boolean), `scores` (object with dimension name to integer 1-10 mapping), `evaluatedAt` (ISO 8601 string)
3. Ensure all objects have `additionalProperties: false`
4. Ensure strings have `maxLength`, arrays have `maxItems`

**Acceptance Criteria:**
- [x] `schema.json` has `implementation.evaluation` with all 5 properties
- [x] `spec-schema.json` has `evaluation` with `spec` and `implementation` sub-objects
- [x] All objects use `additionalProperties: false`
- [x] Integer fields have `minimum` and `maximum` constraints
- [x] Schema validation tests pass

**Files to Modify:**
- `schema.json`
- `spec-schema.json`

**Tests Required:**
- [x] `python3 tests/test_schema_validation.py` passes
- [x] `python3 tests/test_schema_constraints.py` passes

---

## Task 4: Update config-handling.md and mode-manifest.json

**Status:** Completed
**Priority:** High
**Effort:** S
**Domain:** core
**IssueID:** #208
**Dependencies:** Task 1
**Ship Blocking:** Yes

**Description:**
Add evaluation config defaults to `core/config-handling.md` and add the `evaluation` module to `spec` and `pipeline` modes in `core/mode-manifest.json`.

**Implementation Steps:**
1. In `core/config-handling.md`, add evaluation defaults to the defaults section:
   ```json
   "evaluation": {
     "enabled": true,
     "minScore": 7,
     "maxIterations": 2,
     "perTask": false,
     "exerciseTests": true
   }
   ```
2. In `core/mode-manifest.json`, add `"evaluation"` to the `modules` array for both `spec` and `pipeline` modes

**Acceptance Criteria:**
- [x] Config defaults are documented with correct default values
- [x] `mode-manifest.json` includes `evaluation` in `spec.modules` and `pipeline.modules`
- [x] JSON syntax is valid

**Files to Modify:**
- `core/config-handling.md`
- `core/mode-manifest.json`

**Tests Required:**
- [x] `python3 tests/test_build.py` passes (mode-manifest structure valid)

---

## Task 5: Update generator pipeline (generate.py + Jinja2 templates)

**Status:** Completed
**Priority:** High
**Effort:** M
**Domain:** generator
**IssueID:** #209
**Dependencies:** Task 1, Task 4
**Ship Blocking:** Yes

**Description:**
Wire the evaluation module into the generator pipeline: add `evaluation` to `build_common_context()` in `generate.py`, and add `{{ evaluation }}` to all 5 Jinja2 templates.

**Implementation Steps:**
1. In `generator/generate.py` `build_common_context()` function, add:
   ```python
   "evaluation": core["evaluation"],
   ```
2. In `generator/templates/claude.j2`, add `{{ evaluation }}` after `{{ decomposition }}` (the last module reference)
3. In `generator/templates/cursor.j2`, add `{{ evaluation }}` in the appropriate position
4. In `generator/templates/codex.j2`, add `{{ evaluation }}` in the appropriate position
5. In `generator/templates/copilot.j2`, add `{{ evaluation }}` in the appropriate position
6. In `generator/templates/antigravity.j2`, add `{{ evaluation }}` in the appropriate position

**Acceptance Criteria:**
- [x] `build_common_context()` includes `evaluation` key
- [x] All 5 Jinja2 templates include `{{ evaluation }}`
- [x] `python3 generator/generate.py --all` succeeds
- [x] Generated outputs contain evaluation content

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`
- `generator/templates/antigravity.j2`

**Tests Required:**
- [x] `python3 generator/generate.py --all` completes without errors
- [x] `python3 tests/test_build.py` passes

---

## Task 6: Add EVALUATION_MARKERS to validate.py and test_platform_consistency.py

**Status:** Completed
**Priority:** High
**Effort:** M
**Domain:** validation
**IssueID:** #210
**Dependencies:** Task 1, Task 5
**Ship Blocking:** Yes

**Description:**
Add `EVALUATION_MARKERS` constant to `generator/validate.py` and wire it into `validate_platform()`, the cross-platform consistency check loop, and import it in `tests/test_platform_consistency.py`. Per CLAUDE.md: all three changes MUST be in the same commit.

**Implementation Steps:**
1. In `generator/validate.py`, add `EVALUATION_MARKERS` constant with markers from `core/evaluation.md` section headings
2. In `validate_platform()`, add `check_markers_present(platform, content, EVALUATION_MARKERS, "evaluation")` call
3. In the cross-platform consistency check loop, add `EVALUATION_MARKERS` to the combined marker list
4. In `tests/test_platform_consistency.py`, import `EVALUATION_MARKERS` and add to `REQUIRED_MARKERS` dict

**Acceptance Criteria:**
- [x] `EVALUATION_MARKERS` constant defined with markers matching `core/evaluation.md` headings
- [x] `validate_platform()` calls `check_markers_present` for evaluation markers
- [x] Cross-platform consistency loop includes `EVALUATION_MARKERS`
- [x] `tests/test_platform_consistency.py` imports and uses `EVALUATION_MARKERS`
- [x] `python3 generator/validate.py` passes with regenerated outputs

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

## Task 7: Modify core/workflow.md -- spec evaluation exit gate and Phase 4 restructure

**Status:** Completed
**Priority:** High
**Effort:** L
**Domain:** core
**IssueID:** #211
**Dependencies:** Task 1
**Ship Blocking:** Yes

**Description:**
This is the primary behavioral change. Modify `core/workflow.md` to: (1) add spec evaluation as a Phase 2 exit gate at the Phase 2 to Phase 3 dispatch boundary, and (2) restructure Phase 4 into 4A (evaluate), 4B (remediate), 4C (complete) sub-phases.

**Implementation Steps:**
1. In Phase 2, after the Phase 2 Completion Summary (step 8) and before Phase 3 dispatch, add the spec evaluation exit gate:
   - Load evaluation config
   - If evaluation enabled: dispatch spec evaluation (reference `core/evaluation.md` Spec Evaluation Protocol)
   - If pass: proceed to Phase 3 dispatch
   - If fail: loop back to Phase 2 revision with feedback from evaluation.md
   - If disabled: proceed to Phase 3 dispatch (existing behavior)
2. Restructure Phase 4 into three named sub-phases:
   - **Phase 4A: Adversarial Evaluation** -- load evaluation config, if enabled run implementation evaluation (reference `core/evaluation.md` Implementation Evaluation Protocol), write results
   - **Phase 4B: Remediation Loop** (conditional) -- if any dimension fails and iterations < max, scope remediation, re-dispatch Phase 3 with constrained scope, re-enter Phase 4A
   - **Phase 4C: Completion** -- existing Phase 4 steps 2-8 (finalize implementation.md, metrics, memory, learnings, docs check, completion gate, issue closure, set status)
3. Ensure Phase 4A handles the case where evaluation is disabled (skip to Phase 4C step 1 for backward compatibility)

**Acceptance Criteria:**
- [x] Spec evaluation gate runs at Phase 2 to Phase 3 boundary
- [x] Phase 4A, 4B, 4C sub-phase headings are present
- [x] Phase 4A references `core/evaluation.md` evaluation procedure
- [x] Phase 4B has constrained-scope remediation dispatch
- [x] Phase 4C preserves all existing completion steps
- [x] Backward compatibility: evaluation disabled falls through to existing behavior
- [x] Uses abstract operations only

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Validation markers still present after regeneration
- [x] Workflow markers (Phase 1-4) still pass validation

---

## Task 8: Modify core/dispatcher.md -- evaluation dispatch handling

**Status:** Completed
**Priority:** High
**Effort:** M
**Domain:** core
**IssueID:** #212
**Dependencies:** Task 7
**Ship Blocking:** Yes

**Description:**
Update `core/dispatcher.md` to handle evaluation dispatch at both the Phase 2 to Phase 3 boundary (spec evaluation) and within Phase 4 (implementation evaluation and remediation re-dispatch).

**Implementation Steps:**
1. In the Phase dispatch signal handling section, add spec evaluation dispatch:
   - When Phase 2 Completion Summary is detected AND evaluation is enabled: dispatch spec evaluation sub-agent before Phase 3 dispatch
   - Spec evaluation sub-agent receives: spec artifacts + evaluation module instructions + shared context block
2. In the Phase dispatch signal handling section, add evaluation-to-remediation dispatch:
   - When Phase 4A writes evaluation failure to `evaluation.md`: detect failure and dispatch remediation Phase 3 context
   - Remediation context receives: evaluation report + constrained task scope + shared context block
3. Add evaluation iteration tracking to the dispatch state

**Acceptance Criteria:**
- [x] Spec evaluation dispatch occurs at Phase 2 exit boundary
- [x] Implementation evaluation failure triggers remediation dispatch
- [x] Remediation context receives evaluation report
- [x] Dispatch handles all platform capability combinations
- [x] Uses abstract operations only

**Files to Modify:**
- `core/dispatcher.md`

**Tests Required:**
- [x] Validation markers present after regeneration

---

## Task 9: Modify core/pipeline.md -- evaluation in pipeline cycling

**Status:** Completed
**Priority:** Medium
**Effort:** M
**Domain:** core
**IssueID:** #213
**Dependencies:** Task 7
**Ship Blocking:** No

**Description:**
Integrate implementation evaluation into pipeline mode's Phase 3/4 cycling. When evaluation is enabled, pipeline uses evaluation scores as the pass/fail signal. When disabled, existing checkbox behavior is preserved.

**Implementation Steps:**
1. In the Pipeline Cycle section, modify the Phase 4 acceptance check to:
   - If evaluation enabled: run Phase 4A evaluation and use dimension scores for pass/fail
   - If evaluation disabled: use existing checkbox verification (current behavior)
2. Add spec evaluation as a one-time pre-cycle step (runs before the first cycle since spec already exists)
3. Extend zero-progress detection to compare evaluation scores between iterations
4. Ensure `pipelineMaxCycles` interacts correctly with `evaluation.maxIterations`

**Acceptance Criteria:**
- [x] Pipeline uses evaluation scores when enabled
- [x] Pipeline uses checkboxes when evaluation disabled
- [x] Spec evaluation runs once before first cycle
- [x] Zero-progress detection works with evaluation scores
- [x] Pipeline cycle count and evaluation iteration count interact correctly

**Files to Modify:**
- `core/pipeline.md`

**Tests Required:**
- [x] Validation markers present after regeneration

---

## Task 10: Regenerate all platform outputs and validate

**Status:** Completed
**Priority:** High
**Effort:** S
**Domain:** generator
**IssueID:** #214
**Dependencies:** Task 5, Task 6, Task 7, Task 8, Task 9
**Ship Blocking:** Yes

**Description:**
Regenerate all platform outputs after all core module and generator changes are complete, then run the full validation suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Fix any validation failures

**Acceptance Criteria:**
- [x] All 5 platforms regenerated successfully
- [x] `python3 generator/validate.py` passes (200+ checks including new EVALUATION_MARKERS)
- [x] `bash scripts/run-tests.sh` passes all tests
- [x] No unsubstituted abstract operations in generated outputs

**Files to Modify:**
- `platforms/claude/SKILL.md`
- `platforms/claude/SKILL.monolithic.md`
- `platforms/claude/modes/spec.md`
- `platforms/claude/modes/pipeline.md`
- `platforms/cursor/specops.mdc`
- `platforms/codex/SKILL.md`
- `platforms/copilot/specops.instructions.md`
- `platforms/antigravity/specops.md`
- `skills/specops/` (synced from platforms/claude/)
- `.claude-plugin/` (if applicable)

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes

---

## Task 11: Update documentation

**Status:** Completed
**Priority:** Medium
**Effort:** S
**Domain:** docs
**IssueID:** #215
**Dependencies:** Task 1, Task 3, Task 7
**Ship Blocking:** No

**Description:**
Update project documentation to reflect the new evaluation system: CLAUDE.md core modules list, docs/STRUCTURE.md module listing, docs/REFERENCE.md config options, and examples.

**Implementation Steps:**
1. In `CLAUDE.md`, add `core/evaluation.md` to the Tier 1 core modules description
2. In `docs/STRUCTURE.md`, add `evaluation.md` to core module listing and `evaluation.md` to templates listing
3. In `docs/REFERENCE.md`, add `implementation.evaluation` config options to the Configuration Options table
4. In `examples/.specops.full.json`, add the evaluation config section

**Acceptance Criteria:**
- [x] CLAUDE.md lists evaluation module with description
- [x] docs/STRUCTURE.md lists both core module and template
- [x] docs/REFERENCE.md has all 5 evaluation config options
- [x] Example config shows evaluation configuration

**Files to Modify:**
- `CLAUDE.md`
- `docs/STRUCTURE.md`
- `docs/REFERENCE.md`
- `examples/.specops.full.json`

**Tests Required:**
- [x] Markdown lint passes: `npx markdownlint-cli2 "CLAUDE.md" "docs/**/*.md"`

---

## Task 12: Regenerate checksums and final validation

**Status:** Completed
**Priority:** High
**Effort:** S
**Domain:** build
**IssueID:** #216
**Dependencies:** Task 10, Task 11
**Ship Blocking:** Yes

**Description:**
Regenerate CHECKSUMS.sha256 for all modified checksummed files and run the complete validation pipeline.

**Implementation Steps:**
1. Regenerate checksums: run `bash scripts/bump-version.sh` or manually regenerate `CHECKSUMS.sha256`
2. Run full validation: `python3 generator/validate.py`
3. Run full test suite: `bash scripts/run-tests.sh`
4. Run shellcheck: `shellcheck setup.sh verify.sh scripts/*.sh platforms/*/install.sh hooks/pre-commit hooks/pre-push`
5. Run markdown lint: `npx markdownlint-cli2 "core/**/*.md" "docs/**/*.md" "CLAUDE.md"`
6. Verify checksums: `shasum -a 256 -c CHECKSUMS.sha256`

**Acceptance Criteria:**
- [x] CHECKSUMS.sha256 is up to date
- [x] All validation checks pass
- [x] All tests pass
- [x] ShellCheck passes
- [x] Markdown lint passes
- [x] Checksum verification passes

**Files to Modify:**
- `CHECKSUMS.sha256`

**Tests Required:**
- [x] Full pipeline: `bash scripts/run-tests.sh`
- [x] `shasum -a 256 -c CHECKSUMS.sha256`
