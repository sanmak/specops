# Implementation Tasks: Steering Files

## Task Breakdown

### Task 1: Create core/steering.md Module
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core
**Blocker:** None

**Description:**
Create the new core module that defines the steering files system: file format, YAML frontmatter schema, inclusion modes (always, fileMatch, manual), loading procedure using abstract operations, safety rules, and inline foundation templates (product.md, tech.md, structure.md).

**Implementation Steps:**
1. Create `core/steering.md` with all sections
2. Use only abstract operations (FILE_EXISTS, LIST_DIR, READ_FILE, WRITE_FILE, ASK_USER, NOTIFY_USER)
3. Include inline foundation templates for product, tech, and structure
4. Add safety section referencing convention sanitization and path containment

**Acceptance Criteria:**
- [x] `core/steering.md` exists with all sections: overview, format, inclusion modes, loading procedure, safety, templates
- [x] Only abstract operations used (no platform-specific tool names)
- [x] Foundation templates include proper YAML frontmatter examples

**Files to Modify:**
- `core/steering.md` (create)

**Tests Required:**
- [x] Abstract operations verified (no raw tool names)

---

### Task 2: Update core/workflow.md Phase 1
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core
**Blocker:** None

**Description:**
Insert a new step in Phase 1 between "Context recovery" (step 2) and "Pre-flight check" (step 3) that loads steering files. Keep the workflow.md text brief — reference the Steering Files module for the full procedure.

**Implementation Steps:**
1. Read current workflow.md Phase 1 structure
2. Insert new step 3: "Load steering files"
3. Renumber subsequent steps (3→4, 4→5, etc.)

**Acceptance Criteria:**
- [x] New "Load steering files" step exists in Phase 1 between context recovery and pre-flight check
- [x] Step references the Steering Files module for full procedure
- [x] Subsequent steps renumbered correctly

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Phase 1 step numbering is sequential and correct

---

### Task 3: Finalize Convention-Based Steering Scope
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core
**Blocker:** None

**Description:**
Remove schema/config steering assumptions from the spec artifacts and align them with the shipped convention-based behavior: steering activates via `<specsDir>/steering/` and enforces a fixed 20-file safety limit.

**Implementation Steps:**
1. Remove references to `steering.enabled` / `steering.maxFiles` from spec docs
2. Update design and requirements docs to describe directory-driven activation and fixed limit
3. Update this tasks file to document the convention-based scope

**Acceptance Criteria:**
- [x] Spec docs no longer claim a schema-level `steering` object
- [x] Requirement and design language matches convention-based `<specsDir>/steering/` behavior
- [x] Fixed 20-file safety limit is documented consistently

**Files to Modify:**
- `.specops/steering-files/design.md`
- `.specops/steering-files/requirements.md`
- `.specops/steering-files/tasks.md`

**Tests Required:**
- [x] `python3 generator/validate.py`

---

### Task 4: Update Generator Pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** generator
**Blocker:** None

**Description:**
Add `"steering": core["steering"]` to all 4 platform context dicts in generate.py. Add `{{ steering }}` placeholder to all 4 platform templates after `{{ config_handling }}` and before `{{ review_workflow }}`.

**Implementation Steps:**
1. Add `"steering": core["steering"]` to generate_claude(), generate_cursor(), generate_codex(), generate_copilot()
2. Insert `{{ steering }}` in claude.j2, cursor.j2, codex.j2, copilot.j2

**Acceptance Criteria:**
- [x] All 4 generate functions include `steering` in context dict
- [x] All 4 templates include `{{ steering }}` after `{{ config_handling }}`
- [x] Generator runs without errors (`python3 generator/generate.py --all`)

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

**Tests Required:**
- [x] Generator produces output without errors
- [x] All 4 platform outputs contain steering content

---

### Task 5: Update Validation and Tests
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 4
**Priority:** High
**Ship Blocking:** Yes
**Domain:** test
**Blocker:** None

**Description:**
Add STEERING_MARKERS to validate.py and integrate into per-platform validation. Add steering markers to test_platform_consistency.py.

**Implementation Steps:**
1. Define STEERING_MARKERS list in validate.py
2. Add check_markers_present() call in validate_platform()
3. Add steering markers to test_platform_consistency.py

**Acceptance Criteria:**
- [x] STEERING_MARKERS defined with distinctive markers
- [x] validate_platform() checks steering markers
- [x] Platform consistency test includes steering markers
- [x] All validation passes (`python3 generator/validate.py`)
- [x] All tests pass (`bash scripts/run-tests.sh`)

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] Validation passes with steering markers
- [x] Platform consistency tests pass

---

### Task 6: Regenerate All Platform Outputs
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 4, Task 5
**Priority:** High
**Ship Blocking:** Yes
**Domain:** build
**Blocker:** None

**Description:**
Run the full regeneration pipeline and verify all outputs include steering content. Run full validation and test suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Verify steering content in all 4 platform outputs

**Acceptance Criteria:**
- [x] All platform outputs regenerated without errors
- [x] Validation passes including STEERING_MARKERS
- [x] All tests pass
- [x] No unmapped abstract operations in generated outputs (FILE_EXISTS is intentionally preserved as a conditional guard)

**Files to Modify:**
- `platforms/claude/SKILL.md` (regenerated)
- `platforms/cursor/specops.mdc` (regenerated)
- `platforms/codex/SKILL.md` (regenerated)
- `platforms/copilot/specops.instructions.md` (regenerated)
- `skills/specops/SKILL.md` (regenerated)

**Tests Required:**
- [x] Full validation passes
- [x] Full test suite passes

## Implementation Order
1. Task 1 + Task 3 (parallel — independent core changes)
2. Task 2 (depends on Task 1)
3. Task 4 (depends on Task 1)
4. Task 5 (depends on Task 4)
5. Task 6 (depends on Tasks 4 + 5)

## Progress Tracking
- Total Tasks: 6
- Completed: 6
- In Progress: 0
- Blocked: 0
- Pending: 0
