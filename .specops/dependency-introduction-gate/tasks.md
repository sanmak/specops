# Implementation Tasks: Dependency Introduction Gate

## Spec-Level Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| dependency-safety-gate | Shares ecosystem detection, dependencies.md | No | Completed |
| adversarial-evaluation | Scoring dimensions to extend | No | Completed |

## Dependency Resolution Log

<!-- Resolution types: scope_cut, interface_defined, completed, escalated, deferred -->

| Blocker | Resolution Type | Resolution Detail | Date |
| ------- | --------------- | ----------------- | ---- |
| -- | -- | -- | -- |

## Task Breakdown

### Task 1: Create core/dependency-introduction.md

**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**IssueID:** #228
**Blocker:** None

**Description:**
Create the new core module `core/dependency-introduction.md` containing: Install Command Patterns table, Build-vs-Install Evaluation framework (5 criteria), Maintenance Profile Intelligence (3-layer: registry API, source repo, LLM fallback), Phase 2 step 5.8 Gate Procedure, Phase 3 Spec Adherence Enforcement rules, and Auto-Intelligence Policy Generation logic. Use abstract operations only (READ_FILE, WRITE_FILE, EDIT_FILE, RUN_COMMAND, ASK_USER, NOTIFY_USER).

**Implementation Steps:**

1. Create `core/dependency-introduction.md` with top-level heading `## Dependency Introduction Gate`
2. Add Install Command Patterns table covering all 7 ecosystems (Node.js, Python, Rust, Ruby, Go, PHP, Java/Kotlin)
3. Add Build-vs-Install Evaluation section with 5-criteria table (scope match, maintenance health, size proportionality, security surface, license compatibility)
4. Add Maintenance Profile Intelligence section with 3-layer approach (registry APIs, GitHub API, LLM fallback)
5. Add Phase 2 Gate Procedure (step 5.8) with full algorithm: scan design.md, compare against Detected Dependencies, evaluate new deps, ASK_USER, record decisions
6. Add Phase 3 Spec Adherence Enforcement section: verify before install, protocol breach on unapproved, post-Phase-3 verification
7. Add Auto-Intelligence Policy Generation section: first-run creation, decision pattern accumulation, team-section preservation
8. Add Platform Adaptation section matching existing module patterns

**Acceptance Criteria:**

- [x] Module uses only abstract operations from core/tool-abstraction.md
- [x] Install command patterns cover all 7 ecosystems from dependency-safety.md
- [x] Build-vs-Install framework has 5 clearly defined criteria
- [x] Maintenance Profile Intelligence has 3 layers with graceful fallback
- [x] Phase 2 gate procedure is step-by-step deterministic
- [x] Phase 3 enforcement uses "protocol breach" for unapproved installs
- [x] Auto-intelligence policy section defines the dependencies.md ## Dependency Introduction Policy structure

**Files to Modify:**

- `core/dependency-introduction.md` (new file)

**Tests Required:**

- [x] Validate module generates without abstract operation leaks via `python3 generator/validate.py`

---

### Task 2: Update core/workflow.md with Phase 2 step 5.8 and Phase 3 enforcement

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #229
**Blocker:** None

**Description:**
Add the dependency introduction gate as Phase 2 step 5.8 (after code-grounded plan validation at 5.7, before external issue creation at 6). Add Phase 3 enforcement rule requiring all install commands to be verified against design.md ### Dependency Decisions.

**Implementation Steps:**

1. Add step 5.8 to Phase 2 in core/workflow.md after step 5.7
2. Add Phase 3 enforcement instruction in the implementation gates section (step 1 area)
3. Reference `core/dependency-introduction.md` for the full gate procedure

**Acceptance Criteria:**

- [x] Phase 2 step 5.8 references the Dependency Introduction Gate module
- [x] Phase 3 includes dependency adherence enforcement in implementation gates
- [x] Step numbering is consistent (5.8 follows 5.7)
- [x] Uses abstract operations only

**Files to Modify:**

- `core/workflow.md`

**Tests Required:**

- [x] Workflow markers still pass in `python3 generator/validate.py`

---

### Task 3: Update core/evaluation.md with dependency scoring guidance

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #230
**Blocker:** None

**Description:**
Add dependency-aware scoring guidance to the Design Coherence (spec evaluation) and Design Fidelity (implementation evaluation) dimensions. This is guidance text only -- no structural changes to the scoring rubric or thresholds.

**Implementation Steps:**

1. In the spec evaluation dimensions table, update Design Coherence scoring guidance to mention dependency decision completeness
2. In the feature specs implementation evaluation dimensions table, update Design Fidelity scoring guidance to mention dependency adherence
3. Keep changes minimal -- add clauses to existing guidance text, do not restructure

**Acceptance Criteria:**

- [x] Design Coherence scoring guidance mentions dependency decisions
- [x] Design Fidelity scoring guidance mentions dependency adherence
- [x] No changes to scoring rubric structure, thresholds, or evaluator prompts
- [x] Evaluation markers still pass validation

**Files to Modify:**

- `core/evaluation.md`

**Tests Required:**

- [x] Evaluation markers still pass in `python3 generator/validate.py`

---

### Task 4: Update core/reconciliation.md with 7th drift check

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #231
**Blocker:** None

**Description:**
Add a 7th drift check (Dependency Drift) to the audit mode. This check compares installed packages (from lock files) against the union of approved dependencies across all completed specs' design.md ### Dependency Decisions sections. Unapproved packages are flagged as Warning. Update the Health Summary table to include 7 checks.

**Implementation Steps:**

1. Add ### Dependency Drift section after ### Dependency Health in core/reconciliation.md
2. Define the check: read lock files, enumerate completed specs, collect approved deps from ### Dependency Decisions, compare
3. Update the Health Summary table to show 7 checks (add Dependency Drift row)
4. Update "Overall health" text to mention 7 checks
5. Update the Audit Report templates to include the new check

**Acceptance Criteria:**

- [x] Dependency Drift check defined with clear algorithm
- [x] Uses ecosystem detection from dependency-safety.md
- [x] Unapproved packages flagged as Warning (not Drift)
- [x] Health Summary table updated to 7 checks
- [x] Audit Report templates include Dependency Drift

**Files to Modify:**

- `core/reconciliation.md`

**Tests Required:**

- [x] Reconciliation markers still pass in `python3 generator/validate.py`

---

### Task 5: Update core/steering.md dependencies.md template

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** #232
**Blocker:** None

**Description:**
Add the ## Dependency Introduction Policy section to the dependencies.md foundation template in core/steering.md. This section is auto-populated by the dependency introduction gate and team-maintained for pattern accumulation.

**Implementation Steps:**

1. Add ## Dependency Introduction Policy section to the dependencies.md foundation template
2. Include placeholder subsections: Default Stance, Approved Patterns, Rejected Patterns
3. Mark as team-maintained (preserved across regeneration)

**Acceptance Criteria:**

- [x] dependencies.md template includes ## Dependency Introduction Policy
- [x] Subsections defined: Default Stance, Approved Patterns, Rejected Patterns
- [x] Team-maintained marker present (same pattern as other team sections)

**Files to Modify:**

- `core/steering.md`

**Tests Required:**

- [x] Steering markers still pass in `python3 generator/validate.py`

---

### Task 6: Update generator pipeline (generate.py, templates, mode-manifest.json)

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #233
**Blocker:** None

**Description:**
Wire the new core module into the generator pipeline: add `dependency_introduction` to `build_common_context()`, add `{{ dependency_introduction }}` placeholder to all 5 Jinja2 templates, and add `dependency-introduction` to mode-manifest.json for the `spec` and `from-plan` mode module lists.

**Implementation Steps:**

1. In `generator/generate.py` `build_common_context()`, add `"dependency_introduction": core["dependency-introduction"]`
2. In each of the 5 Jinja2 templates (claude.j2, cursor.j2, codex.j2, copilot.j2, antigravity.j2), add `{{ dependency_introduction }}` after `{{ dependency_safety }}`
3. In `core/mode-manifest.json`, add `"dependency-introduction"` to the `spec` mode modules list (after `dependency-safety`) and to the `from-plan` mode modules list (after `dependency-safety`)

**Acceptance Criteria:**

- [x] `build_common_context()` includes `dependency_introduction` key
- [x] All 5 Jinja2 templates include `{{ dependency_introduction }}`
- [x] mode-manifest.json `spec` mode includes `dependency-introduction`
- [x] mode-manifest.json `from-plan` mode includes `dependency-introduction`

**Files to Modify:**

- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`
- `generator/templates/antigravity.j2`
- `core/mode-manifest.json`

**Tests Required:**

- [x] `python3 generator/generate.py --all` completes without errors
- [x] Generated outputs include dependency introduction content

---

### Task 7: Add DEPENDENCY_INTRODUCTION_MARKERS to validate.py and test_platform_consistency.py

**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 6
**Priority:** High
**IssueID:** #234
**Blocker:** None

**Description:**
Define DEPENDENCY_INTRODUCTION_MARKERS constant in validate.py, add the check to validate_platform(), add it to the cross-platform consistency loop, and import it in test_platform_consistency.py. This must all happen in the same commit per the Gap 31 pattern documented in memory.

**Implementation Steps:**

1. In `generator/validate.py`, define `DEPENDENCY_INTRODUCTION_MARKERS` constant with markers matching the new core module's headings
2. In `validate_platform()`, add the markers check call (after dependency safety check)
3. In `tests/test_platform_consistency.py`, add `DEPENDENCY_INTRODUCTION_MARKERS` to the import list
4. In `tests/test_platform_consistency.py`, add `"dependency_introduction": DEPENDENCY_INTRODUCTION_MARKERS` to the `REQUIRED_MARKERS` dict

**Acceptance Criteria:**

- [x] DEPENDENCY_INTRODUCTION_MARKERS defined with markers matching core module headings
- [x] validate_platform() includes the markers check
- [x] test_platform_consistency.py imports DEPENDENCY_INTRODUCTION_MARKERS
- [x] test_platform_consistency.py REQUIRED_MARKERS includes the new category
- [x] All changes in the same commit (Gap 31 pattern)

**Files to Modify:**

- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**

- [x] `python3 generator/validate.py` passes with new markers
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 8: Regenerate platform outputs and run full test suite

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
**Priority:** High
**IssueID:** #235
**Blocker:** None

**Description:**
Run the full generator to produce updated platform outputs, then run the complete test suite to verify everything passes.

**Implementation Steps:**

1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Fix any failures and re-run

**Acceptance Criteria:**

- [x] `python3 generator/generate.py --all` completes successfully
- [x] `python3 generator/validate.py` passes all checks including new DEPENDENCY_INTRODUCTION_MARKERS
- [x] `bash scripts/run-tests.sh` passes all tests
- [x] All 5 platform outputs contain dependency introduction gate content

**Files to Modify:**

- `platforms/claude/SKILL.md` (generated)
- `platforms/claude/SKILL.monolithic.md` (generated)
- `platforms/claude/modes/spec.md` (generated)
- `platforms/claude/modes/from-plan.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `platforms/antigravity/specops.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `skills/specops/SKILL.monolithic.md` (generated)
- `skills/specops/modes/spec.md` (generated)
- `skills/specops/modes/from-plan.md` (generated)

**Tests Required:**

- [x] Full test suite passes

---

### Task 9: Update documentation (STRUCTURE.md, docs-sync.md, CLAUDE.md)

**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** #236
**Blocker:** None

**Description:**
Add the new core module to documentation files that track core modules: docs/STRUCTURE.md, .claude/commands/docs-sync.md, and CLAUDE.md.

**Implementation Steps:**

1. Add `core/dependency-introduction.md` entry to docs/STRUCTURE.md core module listing
2. Add mapping to .claude/commands/docs-sync.md dependency map
3. Add to CLAUDE.md core modules description if appropriate

**Acceptance Criteria:**

- [x] docs/STRUCTURE.md lists dependency-introduction.md
- [x] .claude/commands/docs-sync.md has mapping for dependency-introduction.md
- [x] Documentation coverage check passes in validate.py

**Files to Modify:**

- `docs/STRUCTURE.md`
- `.claude/commands/docs-sync.md`
- `CLAUDE.md`

**Tests Required:**

- [x] `python3 generator/validate.py` docs coverage check passes

---

## Implementation Order

1. Task 1 (foundation -- core module)
2. Task 2, Task 3, Task 4, Task 5 (parallel -- workflow/eval/audit/steering updates)
3. Task 6 (generator pipeline -- depends on Task 1)
4. Task 7 (validation markers -- depends on Task 1, Task 6)
5. Task 8 (regenerate and test -- depends on all above)
6. Task 9 (documentation -- can run after Task 1 but before Task 8)

## Progress Tracking

- Total Tasks: 9
- Completed: 9
- In Progress: 0
- Blocked: 0
- Pending: 0
