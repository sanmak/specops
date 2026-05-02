# Inter-Mode Communication -- Tasks

## Task 1: Add Headless Mode Protocol section to core/dispatcher.md

**Status:** Completed
**Priority:** High
**IssueID:** #273
**Dependencies:** None
**Estimated effort:** Large

Add a new section "## Headless Mode Protocol" to `core/dispatcher.md` after the "## Safety Rules" section. Content:

1. Introduction paragraph explaining headless mode purpose
2. Headless Response Schema (JSON structure with all 6 top-level fields: status, findings, scores, verdict, actionItems, metadata)
3. Finding object schema matching evaluation/persona finding format (id, severity, confidence, confidenceValue, fixClass, description, remediation, file, line)
4. Schema constraints (maxItems, maxLength, additionalProperties: false equivalent)
5. Headless Dispatch subsection: how callers request headless output and how sub-agents respond
6. Participating Modes table: audit (producer), evaluation (producer), pipeline (consumer), all others (none)
7. Fallback behavior: if JSON parsing fails, fall back to markdown (backward compat)

All content must use abstract operations only (READ_FILE, WRITE_FILE, etc.).

**Acceptance Criteria:**
- [x] Headless Mode Protocol section added after Safety Rules
- [x] Headless Response Schema documented with all 6 top-level fields
- [x] Finding object schema matches evaluation finding format
- [x] Schema constraints documented (maxItems, maxLength)
- [x] Headless Dispatch subsection present
- [x] Participating Modes table present with audit, evaluation, pipeline
- [x] Fallback behavior documented
- [x] All operations use abstract operations only

## Task 2: Update Dispatch Protocol for headless mode

**Status:** Completed
**Priority:** High
**IssueID:** #274
**Dependencies:** Task 1
**Estimated effort:** Medium

Update the existing "## Dispatch Protocol" section in `core/dispatcher.md`:

1. Add step 2.5 "Headless mode injection" after step 2: when dispatch context includes headless: true, append headless instruction to sub-agent prompt
2. Update step 6 (Spec evaluation dispatch) to note that when evaluation is dispatched headlessly (from pipeline), the JSON response is passed back to the caller instead of writing to evaluation.md
3. Update step 7 (Implementation evaluation-to-remediation dispatch) to note headless awareness

**Acceptance Criteria:**
- [x] Step 2.5 added for headless mode injection
- [x] Step 6 updated with headless variant for pipeline
- [x] Step 7 notes headless awareness
- [x] Existing non-headless behavior preserved

## Task 3: Update core/pipeline.md for structured consumption

**Status:** Completed
**Priority:** High
**IssueID:** #275
**Dependencies:** Task 1, Task 2
**Estimated effort:** Medium

Update `core/pipeline.md` pipeline cycle pseudocode:

1. Change evaluation invocation to use `headless: true`
2. Add JSON parsing of evaluation response
3. Add fallback to markdown parsing if JSON parse fails
4. Update score extraction to use JSON field access
5. Update verdict determination to use JSON verdict field
6. Update zero-progress detection to compare structured score objects
7. Update action routing classification to read from findings[].fixClass
8. Update Pipeline Integration table to note headless evaluation integration

**Acceptance Criteria:**
- [x] Pipeline cycle invokes evaluation with headless: true
- [x] JSON parsing of evaluation response implemented
- [x] Fallback to markdown parsing on JSON parse failure
- [x] Score extraction uses JSON field access
- [x] Verdict determination uses JSON verdict field
- [x] Zero-progress detection compares structured objects
- [x] Action routing reads findings[].fixClass from JSON

## Task 4: Add HEADLESS_MARKERS to generator/validate.py

**Status:** Completed
**Priority:** High
**IssueID:** #276
**Dependencies:** Task 1
**Estimated effort:** Small

Add validation markers for headless mode content:

1. Define HEADLESS_MARKERS constant with markers that verify headless protocol presence
2. Add check_markers_present call in validate_platform() function
3. Add HEADLESS_MARKERS to the cross-platform consistency check (it gets imported by test_platform_consistency.py)

**Acceptance Criteria:**
- [x] HEADLESS_MARKERS constant defined
- [x] Added to validate_platform() checks
- [x] Ready for cross-platform consistency import

## Task 5: Update tests/test_platform_consistency.py

**Status:** Completed
**Priority:** High
**IssueID:** #276
**Dependencies:** Task 4
**Estimated effort:** Small

Update the cross-platform consistency test:

1. Import HEADLESS_MARKERS from validate.py
2. Add "headless" entry to REQUIRED_MARKERS dict

**Acceptance Criteria:**
- [x] HEADLESS_MARKERS imported
- [x] Added to REQUIRED_MARKERS dict
- [x] Test passes with regenerated platform outputs

## Task 6: Regenerate platform outputs and run tests

**Status:** Completed
**Priority:** High
**IssueID:** #277
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5
**Estimated effort:** Medium

1. Run `python3 generator/generate.py --all` to regenerate all platform outputs
2. Run `python3 generator/validate.py` to verify 200+ checks pass
3. Run `python3 tests/test_platform_consistency.py` to verify cross-platform consistency
4. Run `bash scripts/run-tests.sh` for full test suite
5. Regenerate checksums if needed

**Acceptance Criteria:**
- [x] All platform outputs regenerated
- [x] validate.py passes (0 errors)
- [x] test_platform_consistency.py passes
- [x] Full test suite passes
- [x] CHECKSUMS.sha256 updated if needed
