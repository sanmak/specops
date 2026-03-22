# Implementation Tasks: Unified Spec Decomposition + Cross-Spec Dependencies + Initiative Orchestration + Phase Dispatch

## Spec-Level Dependencies

| Dependent Spec | Reason | Required | Status |
|---|---|---|---|
| None | This is a foundational feature with no spec-level dependencies | — | — |

## Dependency Resolution Log

| Blocker | Resolution Type | Resolution Detail | Date |
|---|---|---|---|
| None | — | — | — |

## Task Breakdown

### Task 1: Create `core/decomposition.md`

**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**IssueID:** #152

**Blocker:** None

**Description:**
New core module covering scope assessment (Phase 1.5), split detection (Phase 2 safety net), initiative data model, cross-spec dependencies (specDependencies), cycle detection (DFS with coloring), initiative order derivation (topological sort into execution waves), Phase 3 dependency gate, scope hammering (blocker response), walking skeleton principle, and cross-linking (relatedSpecs). Uses abstract operations only.

**Implementation Steps:**

1. Create `core/decomposition.md` with all 10 sections (1.1 through 1.10)
2. Phase 1.5 Scope Assessment Gate: complexity signals, proposal format, interactive/non-interactive handling
3. Phase 2 Split Detection: safety net after requirements drafting
4. Initiative Data Model: location, fields, schema reference
5. Cross-Spec Dependencies: specDependencies array format, population during Phase 2 step 3
6. Cycle Detection: DFS with white/gray/black coloring
7. Initiative order derivation: topological sort into execution waves
8. Phase 3 Dependency Gate: required (block) vs advisory (warn), cycle detection safety net
9. Scope Hammering: blocker response options, resolution types, Cross-Spec Blockers table
10. Walking Skeleton Principle: first wave-1 spec flagged as skeleton
11. Cross-Linking: relatedSpecs, informational only

**Acceptance Criteria:**

- [x] Module uses only abstract operations from `core/tool-abstraction.md`
- [x] All 10 sections present with complete instructions
- [x] Cycle detection algorithm specified (DFS with coloring)
- [x] Scope hammering resolution types defined

**Files to Modify:**

- `core/decomposition.md` (new)

**Tests Required:**

- [x] Generated outputs contain DECOMPOSITION_MARKERS after regeneration

---

### Task 2: Create `core/initiative-orchestration.md`

**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**IssueID:** #153

**Blocker:** None

**Description:**
New core module for autonomous execution of multi-spec initiatives. Lightweight orchestrator that dispatches specs through the normal dispatcher. Covers the orchestrator loop (9 steps), initiative mode definition, dispatcher routing patterns, state management (all file-based), and initiative-log.md artifact.

**Implementation Steps:**

1. Create `core/initiative-orchestration.md`
2. Orchestrator loop: read initiative.json → compute waves → select next spec → build handoff bundle → dispatch → verify → update → repeat
3. Initiative Handoff Bundle format: initiative context, spec identity, dependency context, scope constraints
4. Initiative mode definition: minimal modules (initiative-orchestration, config-handling, safety, memory)
5. Dispatcher routing patterns: "initiative <id>", "run initiative <id>", "execute initiative <id>", "resume initiative <id>"
6. State management table: all file-based sources
7. initiative-log.md artifact: chronological execution log format

**Acceptance Criteria:**

- [x] Module uses only abstract operations
- [x] Orchestrator loop fully specified (9 steps)
- [x] Handoff bundle format defined
- [x] File-based state management (no in-memory accumulation)
- [x] initiative-log.md format specified

**Files to Modify:**

- `core/initiative-orchestration.md` (new)

**Tests Required:**

- [x] Generated outputs contain initiative orchestration markers after regeneration

---

### Task 3: Update `spec-schema.json`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #154

**Blocker:** None

**Description:**
Add three optional properties to spec-schema.json: `partOf` (string, initiative ID), `relatedSpecs` (array of strings), `specDependencies` (array of objects with specId, reason, required, contractRef). All with `additionalProperties: false`, `maxLength`, `maxItems`. Not added to `required` array.

**Implementation Steps:**

1. Add `partOf` property with type string, maxLength 100, pattern `^[a-zA-Z0-9._-]+$`
2. Add `relatedSpecs` property with type array, maxItems 20, items with maxLength 100 and pattern
3. Add `specDependencies` property with type array, maxItems 50, items as object with specId, reason, required, contractRef — `additionalProperties: false`
4. Verify existing specs still validate (backward compatibility)

**Acceptance Criteria:**

- [x] Three new optional properties added
- [x] All objects use `additionalProperties: false`
- [x] String fields have `maxLength`, arrays have `maxItems`
- [x] Existing specs validate without changes

**Files to Modify:**

- `spec-schema.json`

**Tests Required:**

- [x] `python3 tests/test_spec_schema.py` passes with new fields
- [x] Backward compatibility: existing spec.json files validate

---

### Task 4: Create `initiative-schema.json`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #155

**Blocker:** None

**Description:**
New JSON schema for initiative.json. Fields: id, title, description?, created, updated, author, specs[], order[][] (execution waves), skeleton?, status (active|completed). All with `additionalProperties: false`, `maxLength`, `maxItems`.

**Implementation Steps:**

1. Create `initiative-schema.json` at project root
2. Define all fields with proper types, constraints, and patterns
3. Set required fields: id, title, created, updated, author, specs, order, status
4. Ensure `additionalProperties: false` at all object levels

**Acceptance Criteria:**

- [x] Schema is valid JSON Schema draft-07
- [x] All objects use `additionalProperties: false`
- [x] String fields have `maxLength`, arrays have `maxItems`
- [x] Status enum: active, completed

**Files to Modify:**

- `initiative-schema.json` (new)

**Tests Required:**

- [x] `python3 tests/test_initiative_schema.py` passes

---

### Task 5: Update `index-schema.json`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #156

**Blocker:** None

**Description:**
Add optional `partOf` field to index entry properties in index-schema.json.

**Implementation Steps:**

1. Add `partOf` property with type string, maxLength 100, pattern `^[a-zA-Z0-9._-]+$`
2. Do not add to required array

**Acceptance Criteria:**

- [x] `partOf` field added as optional
- [x] Pattern and maxLength constraints present
- [x] Existing index.json validates without changes

**Files to Modify:**

- `index-schema.json`

**Tests Required:**

- [x] `python3 tests/test_spec_schema.py` passes (index validation)

---

### Task 6: Update `core/workflow.md` — 5 insertions + phase dispatch gates

**Status:** Completed
**Estimated Effort:** L
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #157

**Blocker:** None

**Description:**
Insert scope assessment, split detection, dependency gate, initiative status update, and phase dispatch gates into the workflow. Uses sub-step notation to avoid renumbering existing steps.

**Implementation Steps:**

1. After Phase 1 step 9: Insert step 9.5 — Scope Assessment (always runs, reference decomposition module)
2. Phase 2 after step 1: Insert step 1.5 — Split Detection checkpoint
3. Phase 2 step 3: Extend to populate `partOf`, `specDependencies`, `relatedSpecs` in spec.json, run cycle detection
4. Phase 3 step 1: New gate — Dependency gate (always runs, verify required specDependencies completed, protocol breach if skipped)
5. Phase 4 after step 6: Insert step 6.3 — Initiative status update (check if all member specs completed)
6. After Phase 2 step 6.7: Insert step 6.8 — Phase dispatch gate (write Phase 2 Completion Summary, signal for fresh Phase 3 sub-agent)
7. After Phase 3 step 8: Insert step 8.5 — Phase dispatch gate (write Phase 3 Completion Summary, signal for fresh Phase 4 sub-agent)

**Acceptance Criteria:**

- [x] All 7 insertions present using sub-step notation
- [x] Dependency gate marked as protocol breach if skipped
- [x] Phase dispatch gates include handoff bundle format
- [x] Platform adaptation noted for non-delegating platforms

**Files to Modify:**

- `core/workflow.md`

**Tests Required:**

- [x] Generated outputs contain workflow markers after regeneration

---

### Task 7: Update `core/dispatcher.md`

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #158

**Blocker:** None

**Description:**
Add check 8 to Pre-Phase-3 Enforcement Checklist (spec dependency gate), add initiative mode routing patterns to Mode Router table, and add phase dispatch signal handling.

**Implementation Steps:**

1. Add check 8 to Pre-Phase-3 Enforcement Checklist: Spec dependency gate — read specDependencies, verify required deps completed, run cycle detection. Fail → STOP.
2. Add initiative routing patterns to Mode Router: "initiative <id>", "run initiative <id>", "execute initiative <id>", "resume initiative <id>"
3. Add phase dispatch signal handling

**Acceptance Criteria:**

- [x] Check 8 present in enforcement checklist
- [x] Initiative routing patterns in Mode Router
- [x] Phase dispatch signal handling specified

**Files to Modify:**

- `core/dispatcher.md`

**Tests Required:**

- [x] Generated outputs contain dispatcher markers after regeneration

---

### Task 8: Update `core/task-delegation.md`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** Medium
**IssueID:** #159

**Blocker:** None

**Description:**
Lower auto-activation threshold from score 6 to score 4. Add configurable threshold via `config.implementation.delegationThreshold` (integer, default 4).

**Implementation Steps:**

1. Change default threshold from 6 to 4
2. Add delegation threshold config reference
3. Document that configured value overrides default

**Acceptance Criteria:**

- [x] Default threshold is 4
- [x] Configurable via delegationThreshold

**Files to Modify:**

- `core/task-delegation.md`

**Tests Required:**

- [x] Generated outputs reflect updated threshold

---

### Task 9: Update 5 templates with Dependencies & Blockers sections

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #160

**Blocker:** None

**Description:**
Add "Dependencies & Blockers" section to all five spec templates. Feature-requirements, design, bugfix, and refactor get Spec Dependencies table + Cross-Spec Blockers table. Tasks.md gets "Spec-Level Dependencies" table + "Dependency Resolution Log".

**Implementation Steps:**

1. `core/templates/feature-requirements.md`: Insert after "Constraints & Assumptions" (line 44) — Spec Dependencies table + Cross-Spec Blockers table
2. `core/templates/design.md`: Insert after "Risks & Mitigations" (line 103) — same tables
3. `core/templates/bugfix.md`: Insert after "Impact Assessment" (line 26) — same tables
4. `core/templates/refactor.md`: Insert after "Scope & Boundaries" (line 29) — same tables
5. `core/templates/tasks.md`: Insert after title (line 1), before "Task Breakdown" — Spec-Level Dependencies table + Dependency Resolution Log

**Acceptance Criteria:**

- [x] Dependencies & Blockers section in feature-requirements.md
- [x] Dependencies & Blockers section in design.md
- [x] Dependencies & Blockers section in bugfix.md
- [x] Dependencies & Blockers section in refactor.md
- [x] Spec-Level Dependencies and Dependency Resolution Log in tasks.md
- [x] Resolution types documented: scope_cut, interface_defined, completed, escalated, deferred

**Files to Modify:**

- `core/templates/feature-requirements.md`
- `core/templates/design.md`
- `core/templates/bugfix.md`
- `core/templates/refactor.md`
- `core/templates/tasks.md`

**Tests Required:**

- [x] Templates render correctly in generated outputs

---

### Task 10: Update `core/reconciliation.md`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** #161

**Blocker:** None

**Description:**
Add Check 6: Dependency Health — validate specDependencies point to valid specs, detect cycles, flag `implementing` specs with unmet required deps.

**Implementation Steps:**

1. Add Check 6 section after existing checks
2. Validate specDependencies entries reference existing spec IDs
3. Run cycle detection across all specs
4. Flag specs in `implementing` status with unmet required dependencies

**Acceptance Criteria:**

- [x] Check 6 present with all three sub-checks
- [x] Uses abstract operations only

**Files to Modify:**

- `core/reconciliation.md`

**Tests Required:**

- [x] Generated outputs contain reconciliation markers

---

### Task 11: Update `core/view.md`

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** #162

**Blocker:** None

**Description:**
Add initiative-grouped list, initiative view/list commands, and dependency display in spec views.

**Implementation Steps:**

1. Add initiative-grouped list view
2. Add `view initiative <id>` command
3. Add `list initiatives` command
4. Add dependency display (specDependencies, relatedSpecs) in spec detail views

**Acceptance Criteria:**

- [x] Initiative list and view commands specified
- [x] Dependency display in spec views
- [x] Initiative-grouped list format defined

**Files to Modify:**

- `core/view.md`

**Tests Required:**

- [x] Generated outputs contain view markers

---

### Task 12: Update `core/task-tracking.md`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** #163

**Blocker:** None

**Description:**
Add conformance rule: spec-level dependency gate must pass before task-level dependencies are evaluated.

**Implementation Steps:**

1. Add conformance rule to task-tracking module
2. Specify ordering: spec-level deps checked first, then task-level deps

**Acceptance Criteria:**

- [x] Conformance rule present
- [x] Clear ordering specified

**Files to Modify:**

- `core/task-tracking.md`

**Tests Required:**

- [x] Generated outputs contain task-tracking markers

---

### Task 13: Update `core/config-handling.md`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** #164

**Blocker:** None

**Description:**
Add `initiatives/` to directory structure, include `partOf` in index regeneration, add `delegationThreshold` config option.

**Implementation Steps:**

1. Add `initiatives/` directory to spec directory structure
2. Include `partOf` field in index regeneration logic
3. Add `config.implementation.delegationThreshold` (integer, default 4) documentation

**Acceptance Criteria:**

- [x] `initiatives/` directory in spec structure
- [x] `partOf` in index regeneration
- [x] `delegationThreshold` config documented

**Files to Modify:**

- `core/config-handling.md`

**Tests Required:**

- [x] Generated outputs contain config markers

---

### Task 14: Update `generator/generate.py`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #165

**Blocker:** None

**Description:**
Add `"decomposition": core["decomposition"]` and `"initiative_orchestration": core["initiative_orchestration"]` to the context dict.

**Implementation Steps:**

1. Add decomposition module to core reading logic
2. Add initiative-orchestration module to core reading logic
3. Add both to context dict (~line 363)

**Acceptance Criteria:**

- [x] Both modules mapped in context dict
- [x] `python3 generator/generate.py --all` succeeds

**Files to Modify:**

- `generator/generate.py`

**Tests Required:**

- [x] `python3 generator/generate.py --all` succeeds without errors

---

### Task 15: Update generator templates (`*.j2`)

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 14
**Priority:** High
**IssueID:** #166

**Blocker:** None

**Description:**
Add `{{ decomposition }}` and `{{ initiative_orchestration }}` template variables to all Jinja2 templates, positioned after `{{ dependency_safety }}`.

**Implementation Steps:**

1. Identify all `.j2` template files in `generator/templates/`
2. Add `{{ decomposition }}` after `{{ dependency_safety }}` in each
3. Add `{{ initiative_orchestration }}` after `{{ decomposition }}` in each

**Acceptance Criteria:**

- [x] Template variables present in all `.j2` files
- [x] Positioned after `{{ dependency_safety }}`

**Files to Modify:**

- `generator/templates/*.j2` (all template files)

**Tests Required:**

- [x] `python3 generator/generate.py --all` produces outputs with decomposition content

---

### Task 16: Update `core/mode-manifest.json`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 2
**Priority:** High
**IssueID:** #167

**Blocker:** None

**Description:**
Add `initiative` mode with modules ["initiative-orchestration", "config-handling", "safety", "memory"]. Add `"decomposition"` to modules for spec, view, audit, and from-plan modes.

**Implementation Steps:**

1. Add `initiative` mode entry with 4 modules
2. Add `"decomposition"` to spec mode modules
3. Add `"decomposition"` to view mode modules
4. Add `"decomposition"` to audit mode modules
5. Add `"decomposition"` to from-plan mode modules

**Acceptance Criteria:**

- [x] Initiative mode registered with correct modules
- [x] Decomposition added to spec, view, audit, from-plan modes

**Files to Modify:**

- `core/mode-manifest.json`

**Tests Required:**

- [x] Mode manifest remains valid JSON
- [x] Generated mode files include decomposition content

---

### Task 17: Update `generator/validate.py`

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #168

**Blocker:** None

**Description:**
Add DECOMPOSITION_MARKERS and INITIATIVE_MARKERS constants. Add to BOTH `validate_platform()` AND the cross-platform consistency check loop (Gap 31 pattern).

**Implementation Steps:**

1. Add DECOMPOSITION_MARKERS constant with markers: "Scope Assessment", "Split Detection", "initiative", "specDependencies", "Dependency Gate", "Cycle Detection", "Execution Waves", "Walking Skeleton", "decomposition", "relatedSpecs"
2. Add INITIATIVE_MARKERS constant (if separate markers needed for orchestration)
3. Add marker checks to `validate_platform()` (~line 611)
4. Add marker checks to cross-platform consistency loop (line 1121)
5. Both locations must be updated in the same commit

**Acceptance Criteria:**

- [x] DECOMPOSITION_MARKERS defined
- [x] Markers checked in `validate_platform()`
- [x] Markers checked in cross-platform consistency loop
- [x] Both locations updated together

**Files to Modify:**

- `generator/validate.py`

**Tests Required:**

- [x] `python3 generator/validate.py` passes after regeneration

---

### Task 18: Update `tests/test_spec_schema.py`

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3, Task 5
**Priority:** High
**IssueID:** #169

**Blocker:** None

**Description:**
Add test cases for partOf, relatedSpecs, specDependencies fields. Test valid values, invalid patterns, maxItems limits, backward compatibility (existing specs without new fields).

**Implementation Steps:**

1. Add tests for valid `partOf` values
2. Add tests for invalid `partOf` patterns
3. Add tests for valid `relatedSpecs` arrays
4. Add tests for `relatedSpecs` maxItems violation
5. Add tests for valid `specDependencies` with and without `required` field
6. Add tests for `specDependencies` with bad patterns, maxItems violation
7. Add backward compatibility test: spec without new fields still validates
8. Add tests for `partOf` in index entries (index-schema.json)

**Acceptance Criteria:**

- [x] Valid/invalid tests for all three new spec.json fields
- [x] Backward compatibility verified
- [x] Index partOf field tested

**Files to Modify:**

- `tests/test_spec_schema.py`

**Tests Required:**

- [x] `python3 tests/test_spec_schema.py` passes

---

### Task 19: Create `tests/test_initiative_schema.py`

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 4
**Priority:** High
**IssueID:** #170

**Blocker:** None

**Description:**
New test file for initiative-schema.json. Test schema well-formedness, valid initiatives, invalid initiatives, edge cases.

**Implementation Steps:**

1. Create `tests/test_initiative_schema.py`
2. Test schema loads and is valid JSON Schema
3. Test valid initiative with all required fields
4. Test valid initiative with optional fields (description, skeleton)
5. Test invalid: missing required fields
6. Test invalid: bad ID pattern
7. Test invalid: status not in enum
8. Test invalid: specs array exceeds maxItems
9. Test edge case: empty specs array

**Acceptance Criteria:**

- [x] Schema well-formedness test
- [x] Valid/invalid initiative tests
- [x] Edge case tests

**Files to Modify:**

- `tests/test_initiative_schema.py` (new)

**Tests Required:**

- [x] `python3 tests/test_initiative_schema.py` passes

---

### Task 20: Update `tests/test_platform_consistency.py`

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 17
**Priority:** High
**IssueID:** #171

**Blocker:** None

**Description:**
Add DECOMPOSITION_MARKERS to platform consistency tests.

**Implementation Steps:**

1. Import or define DECOMPOSITION_MARKERS
2. Add consistency check for decomposition markers across all platforms

**Acceptance Criteria:**

- [x] DECOMPOSITION_MARKERS checked in platform consistency tests

**Files to Modify:**

- `tests/test_platform_consistency.py`

**Tests Required:**

- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 21: Tier 1 documentation updates

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #172

**Blocker:** None

**Description:**
Critical documentation that must ship with the feature: CHANGELOG.md, docs/COMMANDS.md, README.md, docs/STRUCTURE.md.

**Implementation Steps:**

1. CHANGELOG.md: New version entry with Added (spec decomposition, scope assessment, split detection, initiative model, cross-spec dependencies, dependency gate, initiative orchestration, phase dispatch). Schema additions. Backward compatibility note.
2. docs/COMMANDS.md: Add `view initiative <id>`, `list initiatives` to Quick Reference. New "Initiative Management" section. Update "Spec Creation" note.
3. README.md: Add "Multi-Spec Features" section with decomposition, initiatives, example. Update differentiators.
4. docs/STRUCTURE.md: Add `core/decomposition.md`, `core/initiative-orchestration.md` to module listing. Add `initiative-schema.json`. Add `.specops/initiatives/`.

**Acceptance Criteria:**

- [x] CHANGELOG.md updated
- [x] COMMANDS.md updated with initiative commands
- [x] README.md updated with multi-spec features
- [x] STRUCTURE.md updated with new files

**Files to Modify:**

- `CHANGELOG.md`
- `docs/COMMANDS.md`
- `README.md`
- `docs/STRUCTURE.md`

**Tests Required:**

- [x] Markdown lint passes

---

### Task 22: Tier 2 documentation updates

**Status:** Completed
**Estimated Effort:** L
**Dependencies:** Task 21
**Priority:** Medium
**IssueID:** #173

**Blocker:** None

**Description:**
Important documentation for pre-release: CLAUDE.md, QUICKSTART.md, CONTRIBUTING.md, docs/REFERENCE.md, docs/TEAM_GUIDE.md, docs/PLAN-VS-SPEC.md, docs/COMPARISON.md, docs/DIAGRAMS.md, docs/MARKETPLACE_SUBMISSIONS.md, SECURITY.md, docs/SECURITY-AUDIT.md, internal/ROADMAP.md, .claude/commands/docs-sync.md.

**Implementation Steps:**

1. CLAUDE.md: Add decomposition module to Three-Tier Architecture, DECOMPOSITION_MARKERS to validation pipeline, `initiatives/` to file relationships
2. QUICKSTART.md: Add "Example: Large Feature" showing decomposition flow, update "What Gets Created", add `view initiative`
3. CONTRIBUTING.md: Core Modules section: registering new modules in generator. Validator guidelines: markers in both locations.
4. docs/REFERENCE.md: Initiative commands to Common Usage Patterns, `initiatives/` to Spec Structure, specDependencies fields
5. docs/TEAM_GUIDE.md: "Managing Large Multi-Team Features" subsection
6. docs/PLAN-VS-SPEC.md: Update "When to Use What" table, "What Spec Mode Adds"
7. docs/COMPARISON.md: Add initiative model row to Feature Matrix
8. docs/DIAGRAMS.md: New "Spec Decomposition Workflow" Mermaid diagram
9. docs/MARKETPLACE_SUBMISSIONS.md: Update all 4 platform descriptions
10. SECURITY.md: Add `initiatives/` path construction to "In Scope"
11. docs/SECURITY-AUDIT.md: Note re-audit needed, initiative ID pattern
12. internal/ROADMAP.md: Move decomposition from planned to shipped
13. .claude/commands/docs-sync.md: Add decomposition module to dependency map

**Acceptance Criteria:**

- [x] All 13 files updated
- [x] Markdown lint passes

**Files to Modify:**

- `CLAUDE.md`
- `QUICKSTART.md`
- `CONTRIBUTING.md`
- `docs/REFERENCE.md`
- `docs/TEAM_GUIDE.md`
- `docs/PLAN-VS-SPEC.md`
- `docs/COMPARISON.md`
- `docs/DIAGRAMS.md`
- `docs/MARKETPLACE_SUBMISSIONS.md`
- `SECURITY.md`
- `docs/SECURITY-AUDIT.md`
- `internal/ROADMAP.md`
- `.claude/commands/docs-sync.md`

**Tests Required:**

- [x] Markdown lint passes

---

### Task 23: Tier 3 documentation updates

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 22
**Priority:** Low
**IssueID:** None
**Blocker:** None

**Description:**
Nice-to-have polish documentation: docs/STEERING_GUIDE.md, docs/TOKEN-USAGE.md, internal/dogfood-friction.md.

**Implementation Steps:**

1. docs/STEERING_GUIDE.md: Best practices for project-specific decomposition rules via steering files
2. docs/TOKEN-USAGE.md: Note Phase 1.5 overhead (~50-100 tokens), initiative management negligible
3. internal/dogfood-friction.md: Post-implementation friction log section for decomposition

**Acceptance Criteria:**

- [x] Three files updated
- [x] Markdown lint passes

**Files to Modify:**

- `docs/STEERING_GUIDE.md`
- `docs/TOKEN-USAGE.md`
- `internal/dogfood-friction.md`

**Tests Required:**

- [x] Markdown lint passes

---

### Task 24: Regenerate all platform outputs

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 14, Task 15, Task 16, Task 17
**Priority:** High
**IssueID:** #174

**Blocker:** None

**Description:**
Run `python3 generator/generate.py --all` to regenerate all platform outputs with the new decomposition and initiative orchestration content.

**Implementation Steps:**

1. Run `python3 generator/generate.py --all`
2. Verify all platforms generated successfully
3. Spot-check outputs for decomposition markers
4. Run `python3 generator/validate.py` to verify all checks pass

**Acceptance Criteria:**

- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes
- [x] Decomposition markers present in all 4 platform outputs

**Files to Modify:**

- `platforms/claude/SKILL.md` (generated)
- `platforms/claude/modes/*.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)

**Tests Required:**

- [x] Validation passes with DECOMPOSITION_MARKERS

---

### Task 25: Checksums and version bump

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 24
**Priority:** High
**IssueID:** #175

**Blocker:** None

**Description:**
Regenerate checksums and bump version for release.

**Implementation Steps:**

1. Run `bash scripts/bump-version.sh <new-version> --checksums`
2. Verify CHECKSUMS.sha256 is up to date
3. Run `shasum -a 256 -c CHECKSUMS.sha256` to verify integrity
4. Run full test suite: `bash scripts/run-tests.sh`
5. Verify pre-commit hook passes

**Acceptance Criteria:**

- [x] Checksums regenerated and valid
- [x] Version bumped
- [x] Full test suite passes
- [x] Pre-commit hook passes

**Files to Modify:**

- `CHECKSUMS.sha256`
- Version files (via bump script)

**Tests Required:**

- [x] `bash scripts/run-tests.sh` passes
- [x] `shasum -a 256 -c CHECKSUMS.sha256` passes

---

## Implementation Order

1. Tasks 1-5 — Group 1: Data model (parallel, no dependencies) — `core/decomposition.md`, `core/initiative-orchestration.md`, `spec-schema.json`, `initiative-schema.json`, `index-schema.json`
2. Tasks 6-13 — Group 2: Core integration (depends on Group 1) — `core/workflow.md`, `core/dispatcher.md`, `core/task-delegation.md`, templates, `core/reconciliation.md`, `core/view.md`, `core/task-tracking.md`, `core/config-handling.md`
3. Tasks 14-17 — Group 3: Generator pipeline (depends on Group 1) — `generator/generate.py`, templates `.j2`, `mode-manifest.json`, `validate.py`
4. Tasks 18-20 — Group 4: Tests (depends on Groups 2-3) — `test_spec_schema.py`, `test_initiative_schema.py`, `test_platform_consistency.py`
5. Tasks 21-23 — Group 5: Documentation (depends on Groups 1-3) — Tier 1, Tier 2, Tier 3 docs
6. Tasks 24-25 — Group 6: Finalization (depends on all) — regenerate, checksums, version bump

## Progress Tracking

- Total Tasks: 25
- Completed: 25
- In Progress: 0
- Blocked: 0
- Pending: 0
