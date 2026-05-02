# Tasks: Confidence Gating on Evaluation Findings

## Task 1: Add Confidence Tiers section to core/evaluation.md

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #244
**Dependencies:** None

**Description:** Add the "Confidence Tiers for Findings" section to `core/evaluation.md` after the Scoring Rubric section. Define the three tiers (HIGH, MODERATE, LOW) with their evidence requirements, evidence validation rules, and scoring impact.

**Implementation Steps:**
1. Read `core/evaluation.md` to locate the Scoring Rubric section
2. Insert the Confidence Tiers section after the Scoring Rubric, before the Spec Evaluation Protocol
3. Include the tier definition table, evidence validation rules, and LOW finding handling
4. Use abstract operations only

**Acceptance Criteria:**
- [x] Confidence Tiers section exists after Scoring Rubric
- [x] Three tiers defined with ranges and evidence requirements
- [x] Evidence validation rules documented (downgrade behavior)
- [x] LOW finding scoring exclusion documented

**Files to Modify:**
- `core/evaluation.md`

## Task 2: Extend evaluator prompts with confidence instructions

**Status:** Completed
**Priority:** High
**Effort:** Small
**IssueID:** #245
**Dependencies:** Task 1

**Description:** Extend both the spec evaluator prompt and implementation evaluator prompt with a 4th structural rule covering confidence classification. The prompts are hardcoded in `core/evaluation.md`.

**Implementation Steps:**
1. Locate the spec evaluator prompt in `core/evaluation.md`
2. Add rule 4 for confidence classification with tier definitions
3. Locate the implementation evaluator prompt
4. Add the same rule 4 for confidence classification

**Acceptance Criteria:**
- [x] Spec evaluator prompt includes confidence classification rule
- [x] Implementation evaluator prompt includes confidence classification rule
- [x] Both prompts define the three tiers with evidence requirements
- [x] Downgrade instruction is included

**Files to Modify:**
- `core/evaluation.md`

## Task 3: Modify evaluation procedure steps for confidence

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #246
**Dependencies:** Task 1

**Description:** Modify the per-dimension evaluation procedure in both the Spec Evaluation Protocol and Implementation Evaluation Protocol. Add step c.5 for confidence classification and modify step c to exclude LOW findings from score computation.

**Implementation Steps:**
1. In the Spec Evaluation Protocol procedure, add step c.5 after step c
2. Modify step c to clarify scores are based on HIGH and MODERATE findings
3. In the Implementation Evaluation Protocol procedure, add the same step c.5
4. Modify step c similarly
5. Update the "mandatory finding" rule: LOW findings satisfy it only when no MODERATE/HIGH exist

**Acceptance Criteria:**
- [x] Spec evaluation has step c.5 for confidence assignment
- [x] Implementation evaluation has step c.5 for confidence assignment
- [x] Score computation explicitly excludes LOW findings
- [x] Mandatory finding rule updated for confidence tiers

**Files to Modify:**
- `core/evaluation.md`

## Task 4: Update evaluation report template

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #247
**Dependencies:** Task 1

**Description:** Update `core/templates/evaluation.md` to include confidence annotations in the evaluation report format. Add a per-dimension findings detail section with Confidence column.

**Implementation Steps:**
1. Read the current evaluation template
2. Add a Confidence-related format to the findings output
3. Add per-dimension findings detail section format
4. Ensure backward compatibility (existing reports without confidence still render)

**Acceptance Criteria:**
- [x] Template includes Confidence annotation format
- [x] Per-dimension findings detail section added
- [x] Backward compatible with existing evaluation reports

**Files to Modify:**
- `core/templates/evaluation.md`

## Task 5: Add confidence markers to validator and regenerate

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #248
**Dependencies:** Tasks 1-4

**Description:** Add confidence-related marker strings to the existing EVALUATION_MARKERS in `generator/validate.py`. Regenerate all platform outputs and verify validation passes.

**Implementation Steps:**
1. Add confidence tier markers to EVALUATION_MARKERS list in validate.py
2. Verify markers are in both validate_platform() and cross-platform consistency loop (Gap 31)
3. Run `python3 generator/generate.py --all` to regenerate
4. Run `python3 generator/validate.py` to verify
5. Run `bash scripts/run-tests.sh` to run full test suite

**Acceptance Criteria:**
- [x] Confidence markers added to EVALUATION_MARKERS
- [x] Markers validated in per-platform check
- [x] Markers validated in cross-platform consistency check
- [x] All platform outputs regenerated
- [x] Validator passes
- [x] All tests pass

**Files to Modify:**
- `generator/validate.py`
- All generated platform outputs (via generate.py)
