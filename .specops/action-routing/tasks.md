# Action Routing -- Tasks

## Task 1: Add action routing subsection to core/evaluation.md

**Status:** Completed
**Priority:** High
**IssueID:** #261
**Dependencies:** None
**Estimated effort:** Large

Add a new subsection to `core/evaluation.md` after "### Multi-Persona Review Integration" titled "### Action Routing for Findings". Content:

1. Fix class definitions (auto_fix, gated_fix, manual, advisory) with examples
2. Routing signal definitions (determinism, scope, risk) with concrete criteria
3. Decision matrix table (6 rows mapping signal combinations to fix classes)
4. Override rules (LOW confidence -> advisory, P3 severity -> advisory with auto_fix exception)
5. Routing procedure (step-by-step algorithm: for each finding, assess signals, apply matrix, apply overrides)
6. Auto-fix execution protocol (apply fix, verify no test breakage, revert + reclassify on failure)
7. Gated fix batching protocol (collect all gated items, present as single batch, handle approval)
8. Platform adaptation for non-interactive (gated_fix -> auto_fix when canAskInteractive is false)

Update the existing "### Feedback Loop" section:
- Phase 4B remediation now separates findings by fix class before acting
- Add the action routing dispatch step between finding aggregation and remediation execution
- Update the remediation instruction format to include fix class

All content must use abstract operations only.

**Acceptance Criteria:**
- [x] Action routing subsection added after Multi-Persona Review Integration
- [x] Four fix classes defined with examples
- [x] Decision matrix table present with 6 signal combinations
- [x] Override rules documented (LOW confidence, P3 severity)
- [x] Routing procedure is step-by-step and deterministic
- [x] Auto-fix execution includes failure handling and reclassification
- [x] Gated fix batching protocol documented
- [x] Platform adaptation for non-interactive documented
- [x] Feedback loop section updated with action routing integration
- [x] All operations use abstract operations only

## Task 2: Update core/pipeline.md with action routing

**Status:** Completed
**Priority:** High
**IssueID:** #262
**Dependencies:** Task 1
**Estimated effort:** Medium

Modify `core/pipeline.md` to integrate action routing into the pipeline cycle:

1. In the pipeline cycle pseudocode, after the evaluation verdict check, add action routing classification of failing findings.
2. Apply auto_fix items within the cycle before checking for gated items.
3. On non-interactive platforms, also apply gated_fix items within the cycle.
4. On interactive platforms, batch gated items for approval between cycles.
5. Manual and advisory items are reported at cycle end.
6. Update the "Pipeline Safety" section to note that auto-fix items respect the same safety rules as manual implementation.

**Acceptance Criteria:**
- [x] Pipeline cycle pseudocode updated with action routing classification
- [x] Auto-fix items applied within pipeline cycle
- [x] Non-interactive platform adaptation documented
- [x] Interactive platform gated-fix batching documented
- [x] Manual and advisory reporting at cycle end
- [x] Pipeline safety section updated

## Task 3: Update core/templates/evaluation.md

**Status:** Completed
**Priority:** Medium
**IssueID:** #263
**Dependencies:** Task 1
**Estimated effort:** Small

Update the evaluation report template:

1. Add `Fix Class` column to the implementation evaluation findings detail table headers.
2. Add `## Action Routing Summary` section after the Multi-Persona Review section with: fix class count table, auto-fix results subsection, gated fix batch subsection, manual findings subsection.
3. Add backward compatibility comment noting this section is additive.

**Acceptance Criteria:**
- [x] Fix Class column added to findings detail tables
- [x] Action Routing Summary section added with count table
- [x] Auto-Fix Results, Gated Fix Batch, Manual Findings subsections present
- [x] Backward compatibility comment added
- [x] Template renders correctly for specs without action routing

## Task 4: Add ACTION_ROUTING_MARKERS to validate.py

**Status:** Completed
**Priority:** High
**IssueID:** #264
**Dependencies:** Task 1
**Estimated effort:** Medium

Add validation markers for action routing content:

1. Define `ACTION_ROUTING_MARKERS` constant with markers:
   - "Action Routing"
   - "auto_fix"
   - "gated_fix"
   - "Fix Determinism"
   - "Fix Scope"
   - "Fix Risk"
   - "Action Routing Summary"
   - "Routing Decision Matrix" or equivalent
   - "Auto-Fix Results"
   - "reclassify"
2. Add markers to `validate_platform()` function (per-platform check).
3. Add markers to the cross-platform consistency check loop.
4. Run `python3 generator/validate.py` to verify.

**Acceptance Criteria:**
- [x] ACTION_ROUTING_MARKERS constant defined with 10+ markers
- [x] Markers added to validate_platform() per-platform check
- [x] Markers added to cross-platform consistency loop
- [x] python3 generator/validate.py passes after regeneration

## Task 5: Update test_platform_consistency.py

**Status:** Completed
**Priority:** High
**IssueID:** #265
**Dependencies:** Task 4
**Estimated effort:** Small

Update the test file:

1. Import `ACTION_ROUTING_MARKERS` from `generator/validate.py`.
2. Add to the `REQUIRED_MARKERS` dictionary.
3. Run `python3 tests/test_platform_consistency.py` to verify.

**Acceptance Criteria:**
- [x] ACTION_ROUTING_MARKERS imported in test file
- [x] Added to REQUIRED_MARKERS dict
- [x] python3 tests/test_platform_consistency.py passes

## Task 6: Regenerate all platforms, run tests, update checksums

**Status:** Completed
**Priority:** High
**IssueID:** #266
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5
**Estimated effort:** Medium

Full regeneration and validation sweep:

1. Run `python3 generator/generate.py --all` to regenerate all 5 platform outputs.
2. Run `python3 generator/validate.py` to verify all markers pass.
3. Run `bash scripts/run-tests.sh` to verify all tests pass.
4. Regenerate checksums for all modified files.
5. Update `.specops/index.json` with the new spec entry.

**Acceptance Criteria:**
- [x] All 5 platform outputs regenerated
- [x] python3 generator/validate.py passes all checks
- [x] bash scripts/run-tests.sh passes all tests
- [x] CHECKSUMS.sha256 updated
- [x] .specops/index.json updated
