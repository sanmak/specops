# Implementation Tasks: EARS Notation for Requirements

## Task Breakdown

### Task 1: Update Feature Requirements Template with EARS Notation
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add EARS notation guidance and format to `core/templates/feature-requirements.md`. Replace checkbox-only acceptance criteria with EARS-primary format. Include all five EARS patterns as inline guidance.

**Implementation Steps:**
1. Add EARS pattern reference (five patterns, one line each with example)
2. Update each user story section to include `Acceptance Criteria (EARS):` with `WHEN/THE SYSTEM SHALL` format
3. Add optional `Progress Checklist:` section (checkboxes derived from EARS)
4. Ensure vertical adaptations still apply (section renaming works on the new structure)

**Acceptance Criteria:**
- [x] Template includes all 5 EARS patterns: Ubiquitous, Event-Driven, State-Driven, Optional Feature, Unwanted Behavior
- [x] Each user story has EARS-formatted acceptance criteria
- [x] Progress checklist is optional, not mandatory
- [x] Template remains platform-agnostic (no tool-specific language)

**Files to Modify:**
- `core/templates/feature-requirements.md`

**Tests Required:**
- [x] Existing tests pass unchanged

---

### Task 2: Update Bugfix Template with SHALL CONTINUE TO and Three-Category Testing
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add "Unchanged Behavior" section to `core/templates/bugfix.md` using `SHALL CONTINUE TO` EARS notation. Restructure the Testing Plan into three categories: Current Behavior, Expected Behavior, Unchanged Behavior.

**Implementation Steps:**
1. Add "Unchanged Behavior" section after "Proposed Fix" with `SHALL CONTINUE TO` format and guidance
2. Restructure "Testing Plan" into three subsections with EARS-formatted test expectations
3. Add guidance for when a bugfix reveals need for a Feature Spec (scope expansion detection)

**Acceptance Criteria:**
- [x] "Unchanged Behavior" section uses `WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior]` format
- [x] Testing Plan has three categories: Current Behavior, Expected Behavior, Unchanged Behavior
- [x] Template includes guidance on scope expansion detection
- [x] Template remains platform-agnostic

**Files to Modify:**
- `core/templates/bugfix.md`

**Tests Required:**
- [x] Existing tests pass unchanged

---

### Task 3: Update Workflow Phase 2 with EARS Generation Instructions
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add instructions to `core/workflow.md` Phase 2 telling agents to generate EARS-formatted acceptance criteria. Reference the five patterns and instruct pattern selection based on requirement type.

**Implementation Steps:**
1. Add EARS instruction block to Phase 2, step 2 (requirements.md creation)
2. Include brief pattern selection guidance (which EARS pattern for which requirement type)
3. Add bugfix-specific instruction for `SHALL CONTINUE TO` and three-category testing
4. Maintain simplicity principle reference (2-3 EARS statements for small features)

**Acceptance Criteria:**
- [x] Phase 2 instructions reference EARS notation
- [x] Agent is instructed to select appropriate EARS pattern
- [x] Bugfix-specific EARS guidance is included
- [x] Simplicity principle is maintained (lean specs for small features)

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Existing tests pass unchanged

---

### Task 4: Regenerate All Platform Outputs
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3
**Priority:** High
**Domain:** build
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Run the generator to rebuild all platform outputs from the updated core templates and workflow. Validate the outputs.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Verify EARS-related content appears in all 4 platform outputs
4. Run `bash scripts/run-tests.sh` to ensure all tests pass

**Acceptance Criteria:**
- [x] All 4 platform outputs regenerated successfully
- [x] `generator/validate.py` passes
- [x] All tests pass
- [x] EARS notation guidance appears in Claude SKILL.md, Cursor .mdc, Codex SKILL.md, Copilot .instructions.md

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/` manifests (generated)

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

## Implementation Order
1. Task 1 and Task 2 (parallel — independent template changes)
2. Task 3 (depends on Task 1 & 2 — references template patterns)
3. Task 4 (depends on all — regenerates from updated core)

## Progress Tracking
- Total Tasks: 4
- Completed: 4
- In Progress: 0
- Blocked: 0
- Pending: 0
