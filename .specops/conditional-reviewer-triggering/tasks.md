# Conditional Reviewer Triggering -- Tasks

## Task 1: Add Triggering Conditions section and refactor Persona Registry in core/review-agents.md

**Status:** Completed
**Priority:** High
**IssueID:** #278
**Dependencies:** None
**Estimated effort:** Large

Update `core/review-agents.md`:

1. Update the Persona Registry table to document activationMode per persona (Activation column already exists, update to reference triggering conditions).
2. Add a new "### Triggering Conditions" subsection after the Persona Registry, before Persona Prompts:
   - Document the activationMode field ("always" vs "conditional")
   - Document the filePatterns field (glob array)
   - Document the contentPatterns field (regex array, secondary fallback)
   - Document the manual override syntax (`--with-<persona>-review`)
3. Rename "### Security-Sensitive File Patterns" to "### Persona Trigger Patterns" and restructure:
   - The hardcoded patterns become Security persona's default filePatterns
   - The extended patterns loading from steering files and CLAUDE.md remains
   - Note that always-on personas do not have trigger patterns

All content must use abstract operations only.

**Acceptance Criteria:**
- [x] Persona Registry table updated with triggering reference
- [x] Triggering Conditions subsection added with activationMode, filePatterns, contentPatterns
- [x] Manual override syntax documented
- [x] Security-Sensitive File Patterns refactored to Persona Trigger Patterns
- [x] Extended pattern loading preserved for Security
- [x] Persona prompts NOT modified

## Task 2: Update Review Execution Protocol step 1 in core/review-agents.md

**Status:** Completed
**Priority:** High
**IssueID:** #279
**Dependencies:** Task 1
**Estimated effort:** Medium

Replace step 1 in the Review Execution Protocol with generalized activation logic:

1. Collect changed files from implementation.md session log
2. Check for manual overrides in user request text
3. For each persona: evaluate activationMode, filePatterns, contentPatterns
4. Record activation results with reasons for the evaluation report

The activation reason must be captured for each persona:
- Always-on: "always-on"
- Conditional match: "matched pattern: <pattern> on file: <file>"
- Content match: "content matched pattern: <pattern> in file: <file>"
- Manual override: "manual override (--with-<prefix>-review)"
- Skipped: "no changed files match <persona> trigger patterns"

All operations must use abstract operations only (READ_FILE for content pattern matching).

**Acceptance Criteria:**
- [x] Step 1 replaced with generalized activation logic
- [x] File pattern matching uses glob semantics
- [x] Content pattern matching uses regex and only runs when no file match
- [x] Manual override detection documented
- [x] Activation reasons captured for every persona
- [x] Uses abstract operations for file reads

## Task 3: Update Multi-Persona Review Report Template in core/review-agents.md

**Status:** Completed
**Priority:** Medium
**IssueID:** #280
**Dependencies:** Task 2
**Estimated effort:** Small

Update the "### Multi-Persona Review Report Template" section in core/review-agents.md:

1. Change Active Personas list to include activation reasons
2. Show examples for always-on, conditional match, manual override, and skipped

**Acceptance Criteria:**
- [x] Active Personas template includes activation reasons
- [x] Examples cover all activation modes
- [x] Format is consistent with the activation reason strings from Task 2

## Task 4: Update core/templates/evaluation.md

**Status:** Completed
**Priority:** Medium
**IssueID:** #281
**Dependencies:** Task 3
**Estimated effort:** Small

Update the Multi-Persona Review section in `core/templates/evaluation.md`:

1. Update Active Personas template to show activation reason format
2. Include both always-on and conditional examples

**Acceptance Criteria:**
- [x] Active Personas section updated with activation reason format
- [x] Template shows both always-on and conditional examples
- [x] Existing template structure preserved (additive change)

## Task 5: Add TRIGGERING_MARKERS to generator/validate.py

**Status:** Completed
**Priority:** High
**IssueID:** #282
**Dependencies:** Task 1
**Estimated effort:** Small

Add validation markers for conditional reviewer triggering:

1. Define TRIGGERING_MARKERS constant
2. Add check_markers_present call in validate_platform() function
3. Add TRIGGERING_MARKERS to the cross-platform consistency check loop

**Acceptance Criteria:**
- [x] TRIGGERING_MARKERS constant defined with markers for triggering content
- [x] Added to validate_platform() checks
- [x] Added to cross-platform consistency check loop

## Task 6: Update tests/test_platform_consistency.py

**Status:** Completed
**Priority:** High
**IssueID:** #282
**Dependencies:** Task 5
**Estimated effort:** Small

1. Import TRIGGERING_MARKERS from validate.py
2. Add "triggering" entry to REQUIRED_MARKERS dict

**Acceptance Criteria:**
- [x] TRIGGERING_MARKERS imported
- [x] Added to REQUIRED_MARKERS dict

## Task 7: Regenerate platform outputs and run tests

**Status:** Completed
**Priority:** High
**IssueID:** #283
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
**Estimated effort:** Medium

1. Run `python3 generator/generate.py --all` to regenerate all platform outputs
2. Run `python3 generator/validate.py` to verify all checks pass
3. Run `python3 tests/test_platform_consistency.py` to verify cross-platform consistency
4. Run `bash scripts/run-tests.sh` for full test suite
5. Regenerate checksums if needed

**Acceptance Criteria:**
- [x] All platform outputs regenerated
- [x] validate.py passes (0 errors)
- [x] test_platform_consistency.py passes
- [x] Full test suite passes
- [x] CHECKSUMS.sha256 updated if needed
