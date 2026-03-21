# Implementation Tasks: Rich Issue Bodies and Auto-Labels

## Task Breakdown

### Task 1: Add Issue Body Composition and GitHub Label Protocol to core/config-handling.md
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #90
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Replace the Issue Creation Protocol section (lines 90-114) in core/config-handling.md with three new subsections: Issue Body Composition, GitHub Label Protocol, and updated platform-specific steps. The shell safety paragraph updates `<TaskDescription>` → `<IssueBody>`.

**Implementation Steps:**
1. Add "### Issue Body Composition" subsection after "For each eligible task:" (line 92) with the mandatory template, READ_FILE instructions for requirements/spec.json, "None specified" rule for empty sections, and protocol breach language
2. Add "### GitHub Label Protocol" subsection with label categories (P-high/P-medium, spec:<spec-id>, feat/fix/refactor), `gh label create --force` commands, and Jira/Linear graceful degradation
3. Update the three platform-specific sections: replace `<TaskDescription>` with `<IssueBody>`, add step 1 "Compose `<IssueBody>`...", add `--label` flags to GitHub `gh issue create` command
4. Update shell safety paragraph: `<TaskDescription>` → `<IssueBody>`

**Acceptance Criteria:**
- [x] Issue Body Composition subsection defines the mandatory template with all sections (Context, Spec Artifacts, Description, Implementation Steps, Acceptance Criteria, Files to Modify, Tests Required, metadata footer)
- [x] GitHub Label Protocol subsection defines 3 label categories with `gh label create --force`
- [x] All three platform steps use `<IssueBody>` instead of `<TaskDescription>`
- [x] GitHub step includes `--label` flags
- [x] Protocol breach language present for freeform descriptions
- [x] Abstract operations used (READ_FILE, not platform-specific tool names)

**Files to Modify:**
- `core/config-handling.md`

**Tests Required:**
- [x] Regenerated platform outputs contain "Issue Body Composition" heading
- [x] Regenerated platform outputs contain "GitHub Label Protocol" heading

---

### Task 2: Add cross-reference to core/task-tracking.md
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #91
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Add one sentence to the External Tracker Sync section in core/task-tracking.md reinforcing that issue creation must use the Issue Body Composition template.

**Implementation Steps:**
1. Read core/task-tracking.md to find the External Tracker Sync section (~line 121-125)
2. Append after the Status Sync cross-reference sentence: "Issue creation uses the Issue Body Composition template from the Configuration Handling module — freeform issue bodies are a protocol breach."

**Acceptance Criteria:**
- [x] Cross-reference sentence added to External Tracker Sync section
- [x] Protocol breach language present

**Files to Modify:**
- `core/task-tracking.md`

---

### Task 3: Update Phase 2 step 6 wording in core/workflow.md
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #92
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Update Phase 2 step 6 in core/workflow.md to explicitly reference Issue Body Composition and labels.

**Implementation Steps:**
1. Read core/workflow.md to find Phase 2 step 6 (~line 130)
2. Update the step text to include: "compose the issue body using the Issue Body Composition template (reading spec artifacts for context), create issues via the Issue Creation Protocol (with labels for GitHub)"

**Acceptance Criteria:**
- [x] Phase 2 step 6 references Issue Body Composition template
- [x] Phase 2 step 6 references labels for GitHub

**Files to Modify:**
- `core/workflow.md`

---

### Task 4: Add ISSUE_BODY_MARKERS to generator/validate.py
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #93
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Add ISSUE_BODY_MARKERS constant to validate.py, integrate into validate_platform() and the cross-platform consistency check. Both locations must be updated in the same task (Gap 31 enforcement).

**Implementation Steps:**
1. Add `ISSUE_BODY_MARKERS` constant after `METRICS_MARKERS` (~line 261)
2. Add `check_markers_present()` call in `validate_platform()` function (~line 389)
3. Append `+ ISSUE_BODY_MARKERS` to the cross-platform consistency marker concatenation (line 735)

**Acceptance Criteria:**
- [x] ISSUE_BODY_MARKERS defined with correct heading strings
- [x] Per-platform validation includes issue-body markers
- [x] Cross-platform consistency check includes issue-body markers

**Files to Modify:**
- `generator/validate.py`

---

### Task 5: Add issue_body to tests/test_platform_consistency.py
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 4
**Priority:** High
**IssueID:** #94
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Add `"issue_body"` entry to the REQUIRED_MARKERS dict in test_platform_consistency.py with the same marker strings.

**Implementation Steps:**
1. Read tests/test_platform_consistency.py to find REQUIRED_MARKERS dict (~line 26)
2. Add `"issue_body"` key with the same markers as ISSUE_BODY_MARKERS

**Acceptance Criteria:**
- [x] issue_body entry added to REQUIRED_MARKERS
- [x] Marker strings match ISSUE_BODY_MARKERS in validate.py

**Files to Modify:**
- `tests/test_platform_consistency.py`

---

### Task 6: Regenerate, Validate, and Test
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Tasks 1, 2, 3, 4, 5
**Priority:** High
**IssueID:** #95
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Regenerate all platform outputs, run the validator, and run the full test suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Grep generated outputs for "Issue Body Composition" and "GitHub Label Protocol"

**Acceptance Criteria:**
- [x] Generator succeeds for all 4 platforms
- [x] Validator passes all checks including new issue-body markers
- [x] All tests pass
- [x] Generated outputs contain "Issue Body Composition" and "GitHub Label Protocol"

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/plugin.json` (generated)
- `.claude-plugin/marketplace.json` (generated)

## Implementation Order
1. Task 1 (foundation — core protocol change)
2. Tasks 2, 3 (parallel — cross-references depend on Task 1)
3. Task 4 (validator markers)
4. Task 5 (test markers — depends on Task 4)
5. Task 6 (integration — depends on all above)

## Progress Tracking
- Total Tasks: 6
- Completed: 6
- In Progress: 0
- Blocked: 0
- Pending: 0
