# Implementation Tasks: Dependency Safety Gate

## Task 1: Create core/dependency-safety.md
**Status:** Completed
**Priority:** High
**Effort:** Large
**Dependencies:** None
**IssueID:** #116

**Description:** Create the new core module with the complete dependency safety protocol using abstract operations only.

**Implementation Steps:**
1. Create `core/dependency-safety.md` with all sections: Dependency Detection Protocol, Package Manager Audit Commands, Dependency Safety Gate, Online Verification Protocol, Offline Fallback Protocol, Severity Evaluation and Blocking Logic, Dependency Audit Artifact Format, Auto-Generated Steering File, Platform Adaptation, Configuration defaults
2. Use abstract operations throughout (READ_FILE, WRITE_FILE, RUN_COMMAND, etc.)
3. Include ecosystem detection table, severity classification, and blocking logic

**Acceptance Criteria:**
- [x] Module uses only abstract operations from core/tool-abstraction.md
- [x] All H2/H3 headings match validator markers
- [x] 3-layer verification protocol fully documented
- [x] Severity thresholds (strict/medium/low) defined
- [x] Audit artifact format defined inline
- [x] dependencies.md steering file format defined

**Files to Modify:**
- `core/dependency-safety.md` (CREATE)

## Task 2: Add dependencySafety to schema.json
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** None
**IssueID:** #117

**Description:** Add the `dependencySafety` configuration section to the JSON schema with 5 properties.

**Implementation Steps:**
1. Add `dependencySafety` object with: enabled (boolean, default true), severityThreshold (enum: strict/medium/low, default medium), autoFix (boolean, default false), allowedAdvisories (array of strings, maxLength 100, maxItems 50), scanScope (enum: spec/project, default spec)
2. Place before `integrations` in schema properties
3. Include `additionalProperties: false`

**Acceptance Criteria:**
- [x] Schema validates with `python3 tests/check_schema_sync.py`
- [x] All 5 properties present with correct types and constraints
- [x] `additionalProperties: false` set

**Files to Modify:**
- `schema.json`

## Task 3: Update core/config-handling.md with defaults
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Task 2
**IssueID:** #118

**Description:** Add dependency safety configuration defaults and workflow impact section.

**Implementation Steps:**
1. Add dependencySafety default values to the defaults JSON block
2. Add a new Workflow Impact section documenting Phase 2 step 6.7 gate behavior and Phase 1 steering file loading

**Acceptance Criteria:**
- [x] Default values documented: enabled true, severityThreshold medium, autoFix false, allowedAdvisories [], scanScope spec
- [x] Workflow Impact section explains Phase 2 step 6.7 gate and Phase 1 dependencies.md loading

**Files to Modify:**
- `core/config-handling.md`

## Task 4: Add dependencies.md foundation template to core/steering.md
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** None
**IssueID:** #119

**Description:** Add `dependencies.md` as the 4th foundation template in the steering files system.

**Implementation Steps:**
1. Add `dependencies.md` template in the Foundation File Templates section (after structure.md)
2. Update the Loading Procedure to mention `dependencies.md` in the foundation template creation list
3. Add staleness check for `_generatedAt > 30 days`

**Acceptance Criteria:**
- [x] dependencies.md listed as 4th foundation template
- [x] Loading procedure references dependencies.md
- [x] Staleness notification at 30 days

**Files to Modify:**
- `core/steering.md`

## Task 5: Add step 6.7 to core/workflow.md
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Task 1
**IssueID:** #120

**Description:** Insert the dependency safety gate as step 6.7 in Phase 2.

**Implementation Steps:**
1. Add step 6.7 between step 6.5 (git checkpoint) and step 7 (review check)
2. Include protocol breach enforcement language
3. Reference the Dependency Safety module

**Acceptance Criteria:**
- [x] Step 6.7 inserted at correct location
- [x] Protocol breach language present
- [x] References Dependency Safety module

**Files to Modify:**
- `core/workflow.md`

## Task 6: Add dependency-safety to core/mode-manifest.json
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Task 1
**IssueID:** #121

**Description:** Add `dependency-safety` module to the spec and from-plan modes in the mode manifest.

**Implementation Steps:**
1. Add `"dependency-safety"` to the `spec` mode modules array
2. Add `"dependency-safety"` to the `from-plan` mode modules array

**Acceptance Criteria:**
- [x] dependency-safety in spec mode modules
- [x] dependency-safety in from-plan mode modules

**Files to Modify:**
- `core/mode-manifest.json`

## Task 7: Add dependency_safety to build_common_context()
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Task 1
**IssueID:** #122

**Description:** Wire the new core module through the generator's shared context builder.

**Implementation Steps:**
1. Add `"dependency_safety": core["dependency-safety"]` to the return dict in `build_common_context()`

**Acceptance Criteria:**
- [x] dependency_safety key present in build_common_context return dict

**Files to Modify:**
- `generator/generate.py`

## Task 8: Add {{ dependency_safety }} to all 4 .j2 templates
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Task 7
**IssueID:** #123

**Description:** Insert the dependency_safety template variable in all 4 Jinja2 templates.

**Implementation Steps:**
1. Add `{{ dependency_safety }}` after `{{ safety }}` and before `## Specification Templates` in each template
2. Update: claude.j2, cursor.j2, codex.j2, copilot.j2

**Acceptance Criteria:**
- [x] All 4 templates include {{ dependency_safety }}
- [x] Placement is after safety and before Specification Templates

**Files to Modify:**
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

## Task 9: Add DEPENDENCY_SAFETY_MARKERS to validate.py
**Status:** Completed
**Priority:** High
**Effort:** Medium
**Dependencies:** Task 1
**IssueID:** #124

**Description:** Add dependency safety markers to the validator for both per-platform and cross-platform checks.

**Implementation Steps:**
1. Define DEPENDENCY_SAFETY_MARKERS constant with ~11 markers
2. Add `check_markers_present()` call in `validate_platform()`
3. Append markers to the cross-platform consistency loop

**Acceptance Criteria:**
- [x] DEPENDENCY_SAFETY_MARKERS defined
- [x] Added to validate_platform() checks
- [x] Added to cross-platform consistency loop (Gap 31 pattern)

**Files to Modify:**
- `generator/validate.py`

## Task 10: Regenerate and validate
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Tasks 1-9
**IssueID:** #125

**Description:** Run the generator for all platforms and validate outputs.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Fix any validation errors

**Acceptance Criteria:**
- [x] Generator succeeds for all 4 platforms
- [x] Validator passes with 0 errors

**Files to Modify:**
- `platforms/claude/` (generated)
- `platforms/cursor/` (generated)
- `platforms/codex/` (generated)
- `platforms/copilot/` (generated)

## Task 11: Update docs and examples
**Status:** Completed
**Priority:** Medium
**Effort:** Medium
**Dependencies:** Tasks 2, 5
**IssueID:** #127

**Description:** Update documentation and example configurations.

**Implementation Steps:**
1. Add 5 config rows for `dependencySafety.*` to `docs/REFERENCE.md`
2. Add `dependency-safety.md` to `docs/STRUCTURE.md` core listing
3. Add `dependency-safety` to `CLAUDE.md` core modules list and security-sensitive files
4. Add mapping row in `.claude/commands/docs-sync.md`
5. Add `dependencySafety` to `examples/.specops.json` and `examples/.specops.full.json`

**Acceptance Criteria:**
- [x] REFERENCE.md has 5 new config rows
- [x] STRUCTURE.md lists dependency-safety.md
- [x] CLAUDE.md updated with module and security listing
- [x] docs-sync.md has mapping
- [x] Example configs include dependencySafety

**Files to Modify:**
- `docs/REFERENCE.md`
- `docs/STRUCTURE.md`
- `CLAUDE.md`
- `.claude/commands/docs-sync.md`
- `examples/.specops.json`
- `examples/.specops.full.json`

## Task 12: Run full test suite
**Status:** Completed
**Priority:** High
**Effort:** Small
**Dependencies:** Task 10
**IssueID:** #126

**Description:** Run the complete test suite to verify everything passes.

**Implementation Steps:**
1. Run `bash scripts/run-tests.sh`
2. Fix any failures

**Acceptance Criteria:**
- [x] All tests pass

**Tests Required:**
- [x] `python3 tests/check_schema_sync.py` passes
- [x] `python3 tests/test_build.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes
- [x] `bash scripts/run-tests.sh` passes (full suite)
