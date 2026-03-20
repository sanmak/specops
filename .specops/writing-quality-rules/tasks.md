# Implementation Tasks: Writing Quality Rules Module

## Task Breakdown

### Task 1: Create core/writing-quality.md
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — created before task tracking enforcement
**Blocker:** None

**Description:**
Create the writing quality rules module with 6 sections distilled from 9 technical writing references. All rules in imperative mood.

**Implementation Steps:**
1. Create `core/writing-quality.md` with H2 heading "## Writing Quality"
2. Add intro paragraph scoping rules to Phase 2 spec generation
3. Add 6 H3 sections: Structure and Order, Precision and Testability, Clarity and Conciseness, Audience Awareness, Collaborative Voice, Self-Check
4. Add Sources section attributing all 9 references
5. Verify no abstract operations in the file

**Acceptance Criteria:**
- [x] Module has 6 rule sections + sources section
- [x] All rules use imperative mood
- [x] No overlap with core/simplicity.md content
- [x] No abstract operations (READ_FILE, WRITE_FILE, etc.)
- [x] ~100 lines (48 lines — concise)

**Files to Modify:**
- `core/writing-quality.md` (new)

**Tests Required:**
- [x] `grep -n 'READ_FILE\|WRITE_FILE\|EDIT_FILE' core/writing-quality.md` returns empty

---

### Task 2: Wire generator pipeline
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**IssueID:** FAILED — created before task tracking enforcement
**Blocker:** None

**Description:**
Add writing_quality to build_common_context() and all 4 Jinja2 templates.

**Implementation Steps:**
1. Add `"writing_quality": core["writing-quality"]` to `build_common_context()` in `generator/generate.py`
2. Add `{{ writing_quality }}` after `{{ simplicity }}` in `generator/templates/claude.j2`
3. Add `{{ writing_quality }}` after `{{ simplicity }}` in `generator/templates/cursor.j2`
4. Add `{{ writing_quality }}` after `{{ simplicity }}` in `generator/templates/codex.j2`
5. Add `{{ writing_quality }}` after `{{ simplicity }}` in `generator/templates/copilot.j2`

**Acceptance Criteria:**
- [x] build_common_context() includes writing_quality key
- [x] All 4 .j2 templates include {{ writing_quality }}

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds

---

### Task 3: Add validation markers and tests
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 2
**Priority:** High
**IssueID:** FAILED — created before task tracking enforcement
**Blocker:** None

**Description:**
Add WRITING_QUALITY_MARKERS to validate.py (both per-platform and cross-platform) and test_platform_consistency.py.

**Implementation Steps:**
1. Add `WRITING_QUALITY_MARKERS` constant to `generator/validate.py` after DELEGATION_MARKERS
2. Add marker check to `validate_platform()` function
3. Add `+ WRITING_QUALITY_MARKERS` to the cross-platform consistency loop (line 669)
4. Add `writing_quality` markers to `REQUIRED_MARKERS` in `tests/test_platform_consistency.py`

**Acceptance Criteria:**
- [x] WRITING_QUALITY_MARKERS constant defined with 9 markers
- [x] validate_platform() checks writing quality markers
- [x] Cross-platform consistency loop includes WRITING_QUALITY_MARKERS
- [x] test_platform_consistency.py includes writing_quality markers

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 4: Regenerate platform outputs and validate
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** High
**IssueID:** FAILED — created before task tracking enforcement
**Blocker:** None

**Description:**
Regenerate all 4 platform outputs and run full validation + test suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Verify SKILL.md line count grew by ~100 lines

**Acceptance Criteria:**
- [x] All 4 platform outputs regenerated
- [x] Validator passes with 0 errors (2 docs coverage warnings expected — fixed in Task 5)
- [x] All tests pass (7/7)
- [x] SKILL.md line count is 3669 (grew by 50 lines from 3619)

**Files to Modify:**
- `platforms/claude/SKILL.md` (regenerated)
- `platforms/cursor/specops.mdc` (regenerated)
- `platforms/codex/SKILL.md` (regenerated)
- `platforms/copilot/specops.instructions.md` (regenerated)
- `skills/specops/SKILL.md` (regenerated)
- `.claude-plugin/plugin.json` (regenerated)
- `.claude-plugin/marketplace.json` (regenerated)

**Tests Required:**
- [x] `python3 generator/validate.py` — 0 errors
- [x] `bash scripts/run-tests.sh` — all pass

---

### Task 5: Add README attribution and update documentation
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** FAILED — created before task tracking enforcement
**Blocker:** None

**Description:**
Add Writing Philosophy section to README.md and update STRUCTURE.md, CLAUDE.md.

**Implementation Steps:**
1. Add "## Writing Philosophy" section to README.md between Architecture and Contributing
2. Add `writing-quality.md` entry to `docs/STRUCTURE.md` core module listing
3. Add `writing-quality` to CLAUDE.md core modules list and validation section
4. Add mapping to `.claude/commands/docs-sync.md` if it exists

**Acceptance Criteria:**
- [x] README has Writing Philosophy section with 9 attributions
- [x] STRUCTURE.md lists writing-quality.md
- [x] CLAUDE.md references writing-quality in modules list and validation

**Files to Modify:**
- `README.md`
- `docs/STRUCTURE.md`
- `CLAUDE.md`
- `.claude/commands/docs-sync.md`

**Tests Required:**
- [x] Manual review of README attribution accuracy

## Implementation Order
1. Task 1 (foundation — the core module)
2. Task 2 (depends on Task 1 — generator wiring)
3. Task 3 (depends on Task 2 — validation)
4. Task 4 (depends on Task 3 — regenerate and verify)
5. Task 5 (depends on Task 1 — documentation, parallel with Task 2-4)

## Progress Tracking
- Total Tasks: 5
- Completed: 5
- In Progress: 0
- Blocked: 0
- Pending: 0
