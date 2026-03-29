# Implementation Tasks: Harden Adversarial Evaluation

## Task 1: Update evaluator prompts with structural rules

**Status:** Completed
**Priority:** High
**IssueID:** None
**Dependencies:** None
**Files:** `core/evaluation.md`

Add the STRUCTURAL RULES block to both the spec evaluator prompt and the implementation evaluator prompt in `core/evaluation.md`. The block covers evidence-first, mandatory finding, and score variance rules.

**Acceptance Criteria:**
- [x] Spec evaluator prompt contains STRUCTURAL RULES block with all 3 rules
- [x] Implementation evaluator prompt contains STRUCTURAL RULES block with all 3 rules
- [x] Rules use imperative language (MUST, SHALL) not advisory language

## Task 2: Update spec evaluation procedure with structural steps

**Status:** Completed
**Priority:** High
**IssueID:** None
**Dependencies:** Task 1
**Files:** `core/evaluation.md`

Modify the spec evaluation procedure to enforce evidence-first ordering, mandatory negative findings, and score variance checking. Insert steps into the per-dimension loop and after all dimensions are scored.

**Acceptance Criteria:**
- [x] Per-dimension step requires evidence list before score assignment
- [x] Per-dimension step requires at least one finding before score assignment
- [x] Score cap at 7 applied when findings list is empty
- [x] Post-scoring step checks for uniform scores and triggers re-evaluation
- [x] Re-evaluation does not consume a `maxIterations` cycle

## Task 3: Update implementation evaluation procedure with structural steps

**Status:** Completed
**Priority:** High
**IssueID:** None
**Dependencies:** Task 1
**Files:** `core/evaluation.md`

Mirror the spec evaluation procedure changes into the implementation evaluation procedure. Same three structural steps with identical semantics.

**Acceptance Criteria:**
- [x] Per-dimension step requires evidence list before score assignment
- [x] Per-dimension step requires at least one finding before score assignment
- [x] Score cap at 7 applied when findings list is empty
- [x] Post-scoring step checks for uniform scores and triggers re-evaluation
- [x] Re-evaluation does not consume a `maxIterations` cycle

## Task 4: Update evaluation report template

**Status:** Completed
**Priority:** High
**IssueID:** None
**Dependencies:** Task 1
**Files:** `core/templates/evaluation.md`

Replace the current evaluation table format with the new evidence-first structure: `| Dimension | Evidence | Findings | Score | Threshold | Pass/Fail |` in both the spec evaluation and implementation evaluation sections.

**Acceptance Criteria:**
- [x] Spec evaluation table has Evidence and Findings columns
- [x] Implementation evaluation table has Evidence and Findings columns
- [x] Old Key Finding column removed
- [x] Template is valid markdown

## Task 5: Add model diversity instruction to dispatcher

**Status:** Completed
**Priority:** Medium
**IssueID:** None
**Dependencies:** None
**Files:** `core/dispatcher.md`

Add model diversity instruction to dispatcher steps 6 and 7 for `canDelegateTask: true` platforms. The instruction tells the evaluator sub-agent to use a different model when available.

**Acceptance Criteria:**
- [x] Step 6 (spec eval dispatch) includes model diversity instruction for `canDelegateTask: true`
- [x] Step 7 (impl eval dispatch) includes model diversity instruction for `canDelegateTask: true`
- [x] Instruction is advisory ("when available"), not mandatory
- [x] No change for `canDelegateTask: false` paths

## Task 6: Fix EVALUATION_MARKERS in cross-platform consistency loop

**Status:** Completed
**Priority:** Medium
**IssueID:** None
**Dependencies:** None
**Files:** `generator/validate.py`

Add `EVALUATION_MARKERS` to the cross-platform consistency check loop on line 1248. This is a pre-existing gap -- EVALUATION_MARKERS is checked per-platform in `validate_platform()` but missing from the cross-platform consistency loop.

**Acceptance Criteria:**
- [x] EVALUATION_MARKERS appears in the consistency check `for marker in ...` concatenation
- [x] Validation passes with the addition

## Task 7: Regenerate all platforms and validate

**Status:** Completed
**Priority:** High
**IssueID:** None
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
**Files:** All generated platform outputs

Run `python3 generator/generate.py --all`, then `python3 generator/validate.py`, then `bash scripts/run-tests.sh`.

**Acceptance Criteria:**
- [x] All 5 platforms regenerated successfully
- [x] Validation passes (0 errors)
- [x] All tests pass
