# Multi-Persona Review -- Tasks

## Task 1: Create core/review-agents.md module

**Status:** Completed
**Priority:** High
**IssueID:** #251
**Dependencies:** None
**Estimated effort:** Large

Create the new `core/review-agents.md` module containing:

1. **Persona Registry** (Section 1): Define the 4 personas (Correctness/CORR, Testing/TEST, Standards/STD, Security/SEC) with their activation rules (always-on vs conditional).
2. **Persona Prompts** (Section 2): Write the 4 hardcoded prompts, each including the structural rules (evidence-first, mandatory finding, confidence classification from confidence-gating).
3. **Security-Sensitive File Patterns** (Section 3): Default patterns list + extension mechanism (steering files, CLAUDE.md).
4. **Review Execution Protocol** (Section 4): Step 4A.2.5 procedure -- determine active personas, dispatch each (sub-agent or inline), aggregate findings, deduplicate, determine verdict.
5. **Evaluation Report Extension** (Section 5): Template for the `## Multi-Persona Review` section in evaluation.md.
6. **Interaction with Adversarial Evaluator** (Section 6): Combined verdict logic (PASS only when both dimension scores pass AND persona review passes).
7. **Platform Adaptation** (Section 7): Behavior table for canDelegateTask true/false.

All content must use abstract operations only (READ_FILE, WRITE_FILE, RUN_COMMAND, etc.).

**Acceptance Criteria:**
- [x] Module file exists at `core/review-agents.md`
- [x] 4 personas defined with prefixes (CORR, TEST, STD, SEC)
- [x] 4 hardcoded prompts with structural rules
- [x] Security-sensitive file patterns (10 default patterns)
- [x] Review execution protocol with sub-step numbering (4A.2.5)
- [x] Aggregation and deduplication logic
- [x] Combined verdict logic documented
- [x] Platform adaptation table
- [x] All operations use abstract operations only

## Task 2: Update core/evaluation.md with cross-references

**Status:** Completed
**Priority:** High
**IssueID:** #252
**Dependencies:** Task 1
**Estimated effort:** Medium

Modify `core/evaluation.md` to integrate the multi-persona review:

1. Add a new subsection after "### Implementation Evaluation Protocol" titled "### Multi-Persona Review Integration" that cross-references `core/review-agents.md` and describes the combined verdict logic.
2. Update the Phase 4A flow description to include step 4A.2.5 (multi-persona review after dimension scoring).
3. Update the "Evaluation Safety" section to include: "The multi-persona review module's prompts are defined in `core/review-agents.md` and MUST NOT be overridden."
4. Update "Feedback Loop" section: when multi-persona review triggers remediation via P0/P1 findings, the remediation context includes the specific persona findings (not just dimension scores).

**Acceptance Criteria:**
- [x] Cross-reference to `core/review-agents.md` added
- [x] Phase 4A flow updated with step 4A.2.5
- [x] Evaluation Safety section updated with review-agents prompt safety rule
- [x] Feedback Loop section updated for persona-triggered remediation
- [x] Combined verdict logic documented (dimension scores AND persona findings)

## Task 3: Update core/dispatcher.md with review dispatch

**Status:** Completed
**Priority:** High
**IssueID:** #253
**Dependencies:** Task 1
**Estimated effort:** Medium

Modify `core/dispatcher.md` to handle multi-persona review dispatch:

1. Update the "Implementation evaluation-to-remediation dispatch" section (step 7) to check for both dimension failures AND persona P0/P1 findings when determining if remediation is needed.
2. Add dispatch logic: after the adversarial evaluator sub-agent returns, check if multi-persona review should run. If evaluation is enabled and not lightweight depth, dispatch personas per the protocol in `core/review-agents.md`.
3. Update the remediation context building to include persona findings when they trigger the failure.

**Acceptance Criteria:**
- [x] Dispatcher checks both dimension scores and persona findings for remediation
- [x] Multi-persona review dispatch added after adversarial evaluator returns
- [x] Remediation context includes persona findings when applicable
- [x] Depth calibration respected (lightweight skips multi-persona review)

## Task 4: Update core/workflow.md Phase 4A

**Status:** Completed
**Priority:** High
**IssueID:** #254
**Dependencies:** Task 1
**Estimated effort:** Small

Modify `core/workflow.md` to reference the multi-persona review in Phase 4A:

1. Add step 4A.2.5 after step 4A.2: "Run the Multi-Persona Review Protocol from the Review Agents module (`core/review-agents.md`). Determine active personas, dispatch each following the platform adaptation rules, aggregate findings, and determine the review verdict."
2. Update step 4A.3 to include persona findings in the pass/fail check: "If all dimensions score at or above `minScore` AND no P0/P1 HIGH/MODERATE persona findings exist: proceed to Phase 4C."
3. Add depth calibration note: "If the depth flag is `lightweight`, skip multi-persona review."

**Acceptance Criteria:**
- [x] Step 4A.2.5 added to Phase 4A
- [x] Step 4A.3 updated with combined verdict check
- [x] Depth calibration note added for lightweight skip
- [x] Sub-step numbering follows project convention (no renumbering of existing steps)

## Task 5: Update core/templates/evaluation.md

**Status:** Completed
**Priority:** Medium
**IssueID:** #255
**Dependencies:** Task 1
**Estimated effort:** Small

Add the `## Multi-Persona Review` section template to `core/templates/evaluation.md`:

1. Add the section after the existing Implementation Evaluation section.
2. Include: Active Personas table, Findings table, Finding Details subsections, Deduplication Notes, and Review Verdict.
3. Template should be backward compatible (specs evaluated before this change do not have this section, and that is valid).

**Acceptance Criteria:**
- [x] `## Multi-Persona Review` section template added
- [x] Includes Active Personas, Findings table, Finding Details, Deduplication Notes, Review Verdict
- [x] Template is additive (backward compatible)

## Task 6: Update core/mode-manifest.json

**Status:** Completed
**Priority:** Medium
**IssueID:** #256
**Dependencies:** Task 1
**Estimated effort:** Small

Add `review-agents` to the module lists for modes that run evaluation:

1. Add `"review-agents"` to the `spec` mode's modules array.
2. Add `"review-agents"` to the `pipeline` mode's modules array.
3. Verify no other modes need the module (audit, from-plan, etc. do not run Phase 4A evaluation).

**Acceptance Criteria:**
- [x] `review-agents` in spec mode modules array
- [x] `review-agents` in pipeline mode modules array
- [x] No unnecessary additions to other modes

## Task 7: Wire generator pipeline

**Status:** Completed
**Priority:** High
**IssueID:** #257
**Dependencies:** Task 1, Task 6
**Estimated effort:** Large

Update `generator/generate.py` to include the new module:

1. Add `core/review-agents.md` to the core module reading logic (load the file content).
2. Add `review_agents` to the context dict in `build_common_context()`.
3. Update all 5 Jinja2 templates (`generator/templates/claude.j2`, `cursor.j2`, `codex.j2`, `copilot.j2`, `antigravity.j2`) to include the `{{ review_agents }}` variable at the appropriate location (after the evaluation module content).
4. Run `python3 generator/generate.py --all` and verify all 5 platform outputs are regenerated.

**Acceptance Criteria:**
- [x] `core/review-agents.md` loaded in generate.py
- [x] `review_agents` in build_common_context()
- [x] All 5 Jinja2 templates include `{{ review_agents }}`
- [x] `python3 generator/generate.py --all` succeeds
- [x] All 5 platform outputs regenerated

## Task 8: Add REVIEW_AGENTS_MARKERS to validate.py

**Status:** Completed
**Priority:** High
**IssueID:** #258
**Dependencies:** Task 7
**Estimated effort:** Medium

Add validation markers for the new module (Gap 31 pattern -- markers in both per-platform and cross-platform checks):

1. Define `REVIEW_AGENTS_MARKERS` constant with markers for key sections:
   - "Persona Registry" or equivalent heading
   - "Correctness Reviewer"
   - "Testing Reviewer"
   - "Standards Reviewer"
   - "Security Reviewer"
   - "security-sensitive"
   - "Multi-Persona Review"
   - "Review Execution Protocol" or equivalent
   - "P0" or "P1" (severity references)
   - "Finding aggregation" or "deduplication" or equivalent
2. Add the markers to `validate_platform()` function.
3. Add the markers to the cross-platform consistency check loop.
4. Run `python3 generator/validate.py` and verify all checks pass.

**Acceptance Criteria:**
- [x] REVIEW_AGENTS_MARKERS constant defined with 10+ markers
- [x] Markers added to `validate_platform()` (per-platform check)
- [x] Markers added to cross-platform consistency loop
- [x] `python3 generator/validate.py` passes with 0 errors

## Task 9: Update test_platform_consistency.py

**Status:** Completed
**Priority:** High
**IssueID:** #259
**Dependencies:** Task 8
**Estimated effort:** Small

Update the test file to import and verify the new markers:

1. Import `REVIEW_AGENTS_MARKERS` from `generator/validate.py` (or verify it is included in the existing import pattern).
2. Add a test case or update the existing marker consistency test to include REVIEW_AGENTS_MARKERS.
3. Run `python3 tests/test_platform_consistency.py` and verify it passes.

**Acceptance Criteria:**
- [x] REVIEW_AGENTS_MARKERS imported in test file
- [x] Test verifies markers are checked across all platforms
- [x] `python3 tests/test_platform_consistency.py` passes

## Task 10: Regenerate all platforms and update checksums

**Status:** Completed
**Priority:** High
**IssueID:** #260
**Dependencies:** Task 7, Task 8, Task 9
**Estimated effort:** Medium

Full regeneration and validation sweep:

1. Run `python3 generator/generate.py --all` to regenerate all 5 platform outputs.
2. Run `python3 generator/validate.py` to verify all markers pass (200+ checks).
3. Run `bash scripts/run-tests.sh` to verify all 8 tests pass.
4. Regenerate checksums: update `CHECKSUMS.sha256` for all modified files.
5. Update `CLAUDE.md` core modules list to include `core/review-agents.md`.
6. Update `docs/STRUCTURE.md` with the new module.

**Acceptance Criteria:**
- [x] All 5 platform outputs regenerated
- [x] `python3 generator/validate.py` passes all checks
- [x] `bash scripts/run-tests.sh` passes 8/8 tests
- [x] CHECKSUMS.sha256 updated
- [x] CLAUDE.md updated with new module reference
- [x] docs/STRUCTURE.md updated
