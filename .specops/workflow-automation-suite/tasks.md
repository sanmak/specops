# Implementation Tasks: Workflow Automation Suite

## Task Breakdown

### Task 1: Create Run Logging Core Module
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**IssueID:** #80
**Blocker:** None
**Domain:** backend

**Description:**
Create `core/run-logging.md` with the run logging module defining log format, entry types, logging procedure, file naming, safety rules, and platform adaptation. Must use abstract operations only.

**Implementation Steps:**
1. Create `core/run-logging.md` with 6 sections: Run Log Format, Log Entry Types, Logging Procedure, Run Log File Naming, Run Log Safety, Platform Adaptation
2. Define the YAML frontmatter format (specId, startedAt, completedAt, finalStatus, phases)
3. Define the 5 log entry types with prescribed formats
4. Specify instrumentation points (config load, steering, spec creation, gates, per-task, acceptance, metrics, memory, docs)
5. Document the `_pending-<timestamp>` naming workaround for unknown spec names
6. Document delegation interaction (orchestrator-only writes)

**Acceptance Criteria:**
- [x] Module uses only abstract operations (READ_FILE, WRITE_FILE, EDIT_FILE, RUN_COMMAND, NOTIFY_USER, FILE_EXISTS)
- [x] All 6 sections present with H3 headings
- [x] YAML frontmatter format documented
- [x] 5 log entry types defined
- [x] Platform adaptation table included

**Files to Modify:**
- `core/run-logging.md` (create)

**Tests Required:**
- [x] No raw abstract operations after generation (checked by validate.py)

**Ship Blocking:** Yes

---

### Task 2: Create Plan Validation Core Module
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**IssueID:** #81
**Blocker:** None
**Domain:** backend

**Description:**
Create `core/plan-validation.md` with the code-grounded plan validation module defining validation scope, procedure, reference resolution, outcomes, safety, and platform adaptation.

**Implementation Steps:**
1. Create `core/plan-validation.md` with 6 sections: Validation Scope, Validation Procedure, Reference Resolution, Validation Outcomes, Plan Validation Safety, Platform Adaptation
2. Define reference extraction from tasks.md (Files to Modify) and design.md
3. Define resolution strategy: repo map first, FILE_EXISTS fallback
4. Define new-file detection heuristic (skip paths with "create", "add new file", "scaffold")
5. Define warn vs strict behavior and platform adaptation for canAskInteractive: false

**Acceptance Criteria:**
- [x] Module uses only abstract operations
- [x] All 6 sections present with H3 headings
- [x] Reference resolution leverages repo map as primary source
- [x] New-file detection heuristic documented
- [x] Path safety (../traversal rejection) documented

**Files to Modify:**
- `core/plan-validation.md` (create)

**Tests Required:**
- [x] No raw abstract operations after generation

**Ship Blocking:** Yes

---

### Task 3: Create Git Checkpointing Core Module
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #82
**Blocker:** None
**Domain:** backend

**Description:**
Create `core/git-checkpointing.md` with the git checkpointing module defining checkpoint configuration, procedure, dirty tree safety, commit messages, autoCommit interaction, safety, and platform adaptation.

**Implementation Steps:**
1. Create `core/git-checkpointing.md` with 7 sections: Checkpoint Configuration, Checkpoint Procedure, Dirty Tree Safety, Checkpoint Commit Messages, Interaction with autoCommit, Git Checkpointing Safety, Platform Adaptation
2. Define 3 checkpoint points with exact commit message formats
3. Document dirty tree detection via RUN_COMMAND(git status --porcelain)
4. Document non-conflicting interaction with autoCommit
5. Document safety rules (never force push, never amend, respect hooks)

**Acceptance Criteria:**
- [x] Module uses only abstract operations
- [x] All 7 sections present with H3 headings
- [x] 3 checkpoint points with exact commit messages
- [x] autoCommit interaction explicitly documented as non-conflicting
- [x] Safety rules documented (never force push, respect hooks)

**Files to Modify:**
- `core/git-checkpointing.md` (create)

**Tests Required:**
- [x] No raw abstract operations after generation

**Ship Blocking:** Yes

---

### Task 4: Create Pipeline Mode Core Module
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**IssueID:** #83
**Blocker:** None
**Domain:** backend

**Description:**
Create `core/pipeline.md` with the automated pipeline mode module defining mode detection, prerequisites, cycle logic, progress, integration with other features, safety, and platform adaptation.

**Implementation Steps:**
1. Create `core/pipeline.md` with 7 sections: Pipeline Mode Detection, Pipeline Prerequisites, Pipeline Cycle, Cycle Limit and Progress, Pipeline Integration, Pipeline Safety, Platform Adaptation
2. Define detection patterns ("pipeline <spec-name>", "auto-implement <spec-name>") with disambiguation from product pipelines
3. Define prerequisite checks (spec exists, compatible status, files present)
4. Define the cycle loop: Phase 3 → acceptance check → pass/fail/max-cycles branching
5. Define zero-progress detection (same criteria unmet as previous cycle)
6. Document integration with run logging, checkpointing, delegation, validation, metrics

**Acceptance Criteria:**
- [x] Module uses only abstract operations
- [x] All 7 sections present with H3 headings
- [x] Detection patterns include disambiguation
- [x] Zero-progress detection documented
- [x] Integration with all 3 other new features documented

**Files to Modify:**
- `core/pipeline.md` (create)

**Tests Required:**
- [x] No raw abstract operations after generation

**Ship Blocking:** Yes

---

### Task 5: Add Workflow Hooks to core/workflow.md
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 2, Task 3, Task 4
**Priority:** High
**IssueID:** #84
**Blocker:** None
**Domain:** backend

**Description:**
Add workflow hooks for all 4 features to `core/workflow.md` at the correct phase boundaries. Use sub-step notation (established pattern) to avoid renumbering existing steps.

**Implementation Steps:**
1. Phase 1, after step 1 (config load): insert step 1.1 (dirty tree check for gitCheckpointing) and step 1.5 (run log initialization)
2. Phase 2, after step 5.6 (vocabulary verification): insert step 5.7 (plan validation)
3. Phase 2, after step 6 (issue creation): insert step 6.5 (spec-created checkpoint)
4. Phase 3, after the task loop: insert step 8 (implemented checkpoint)
5. Phase 4, after step 6 (status completed): insert step 6.5 (completed checkpoint + run log finalization)
6. Getting Started, after step 11.5: insert step 11.7 (pipeline mode detection)

**Acceptance Criteria:**
- [x] Sub-step notation used (no renumbering)
- [x] Run log hooks in Phase 1 (init) and Phase 4 (finalize)
- [x] Plan validation hook in Phase 2 step 5.7
- [x] 3 checkpoint hooks at correct phase boundaries
- [x] Pipeline detection in Getting Started step 11.7

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Workflow markers still present after changes (checked by validate.py)

**Ship Blocking:** Yes

---

### Task 6: Update Schema and Config Handling
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #85
**Blocker:** None
**Domain:** backend

**Description:**
Add 4 new config options to `schema.json` under `implementation` and update example configs.

**Implementation Steps:**
1. Add `runLogging` (enum ["on","off"], default "on") to schema.json implementation properties
2. Add `validateReferences` (enum ["off","warn","strict"], default "off") to schema.json
3. Add `gitCheckpointing` (boolean, default false) to schema.json
4. Add `pipelineMaxCycles` (integer, min 1, max 10, default 3) to schema.json
5. Update `examples/.specops.full.json` with all 4 new properties

**Acceptance Criteria:**
- [x] All 4 properties added under `implementation` with correct types and defaults
- [x] `additionalProperties: false` maintained on `implementation` object
- [x] `pipelineMaxCycles` has minimum: 1 and maximum: 10
- [x] Enum strings have maxLength constraints
- [x] Example config updated

**Files to Modify:**
- `schema.json`
- `examples/.specops.full.json`

**Tests Required:**
- [x] Schema validation passes (test_schema_validation.py)
- [x] Invalid values rejected (test_schema_constraints.py)
- [x] Schema sync check passes (check_schema_sync.py)

**Ship Blocking:** Yes

---

### Task 7: Wire Generator Pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 2, Task 3, Task 4
**Priority:** High
**IssueID:** #86
**Blocker:** None
**Domain:** backend

**Description:**
Add 4 new modules to the generator pipeline: build_common_context entries, j2 template inclusions, validation markers, and platform consistency tests.

**Implementation Steps:**
1. Add 4 entries to `build_common_context()` in `generator/generate.py`: `run_logging`, `plan_validation`, `git_checkpointing`, `pipeline`
2. Add `{{ run_logging }}`, `{{ plan_validation }}`, `{{ git_checkpointing }}`, `{{ pipeline }}` to all 4 `.j2` templates (after `{{ metrics }}`)
3. Add 4 marker constants to `generator/validate.py`: `RUN_LOGGING_MARKERS`, `PLAN_VALIDATION_MARKERS`, `GIT_CHECKPOINT_MARKERS`, `PIPELINE_MARKERS`
4. Add marker checks to `validate_platform()` function
5. Add all 4 marker sets to the cross-platform consistency loop
6. Add 4 marker categories to `tests/test_platform_consistency.py`

**Acceptance Criteria:**
- [x] 4 entries in build_common_context
- [x] 4 template inclusions in all 4 j2 files
- [x] 4 marker constants defined
- [x] Markers checked in validate_platform()
- [x] Markers added to cross-platform consistency loop (known footgun — must be same commit)
- [x] 4 categories in test_platform_consistency.py

**Files to Modify:**
- `generator/generate.py`
- `generator/validate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

**Ship Blocking:** Yes

---

### Task 8: Add Pipeline Entry Points and Schema Tests
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 4, Task 6
**Priority:** Medium
**IssueID:** #87
**Blocker:** None
**Domain:** backend

**Description:**
Add pipeline examples to platform entry points and schema constraint tests for new config options.

**Implementation Steps:**
1. Add `"/specops pipeline auth-feature"` to Claude platform.json entryPoint.examples
2. Add equivalent pipeline examples to cursor, codex, copilot platform.json files
3. Add test cases to `tests/test_schema_constraints.py` for:
   - `pipelineMaxCycles: 15` → rejected
   - `pipelineMaxCycles: 0` → rejected
   - `validateReferences: "invalid"` → rejected
   - `runLogging: "maybe"` → rejected

**Acceptance Criteria:**
- [x] Pipeline examples in all 4 platform.json files
- [x] Schema constraint tests for out-of-range/invalid values
- [x] All tests pass

**Files to Modify:**
- `platforms/claude/platform.json`
- `platforms/cursor/platform.json`
- `platforms/codex/platform.json`
- `platforms/copilot/platform.json`
- `tests/test_schema_constraints.py`

**Tests Required:**
- [x] `python3 tests/test_schema_constraints.py` passes

**Ship Blocking:** No

---

### Task 9: Regenerate Platform Outputs and Update Documentation
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 5, Task 6, Task 7, Task 8
**Priority:** High
**IssueID:** #88
**Blocker:** None
**Domain:** backend

**Description:**
Regenerate all platform outputs, validate, run full test suite, and update documentation.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py` — verify 0 errors
3. Run `bash scripts/run-tests.sh` — verify all tests pass
4. Update `docs/STRUCTURE.md` with 4 new core module entries
5. Update `docs/REFERENCE.md` with 4 new config option rows
6. Update `docs/COMMANDS.md` with `/specops pipeline` entry
7. Update `.claude/commands/docs-sync.md` with 4 new module mappings
8. Update `CLAUDE.md` core module listing if needed

**Acceptance Criteria:**
- [x] All platform outputs regenerated
- [x] Validator passes with 0 errors
- [x] All tests pass
- [x] Documentation updated (STRUCTURE, REFERENCE, COMMANDS)
- [x] No raw abstract operations in generated files

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/plugin.json` (generated)
- `.claude-plugin/marketplace.json` (generated)
- `docs/STRUCTURE.md`
- `docs/REFERENCE.md`
- `docs/COMMANDS.md`
- `.claude/commands/docs-sync.md`
- `CLAUDE.md`

**Tests Required:**
- [x] `python3 generator/validate.py` — 0 errors
- [x] `bash scripts/run-tests.sh` — all pass
- [x] `python3 tests/check_schema_sync.py` — passes

**Ship Blocking:** Yes

## Implementation Order
1. Tasks 1-4 (parallel — 4 core modules, no cross-dependencies)
2. Task 6 (schema — no module dependencies)
3. Task 5 (workflow hooks — depends on modules existing)
4. Task 7 (generator pipeline — depends on modules + schema)
5. Task 8 (entry points + schema tests)
6. Task 9 (regenerate + validate + docs)

## Progress Tracking
- Total Tasks: 9
- Completed: 9
- In Progress: 0
- Blocked: 0
- Pending: 0
