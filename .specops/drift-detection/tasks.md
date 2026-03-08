# Implementation Tasks: Drift Detection & Guided Reconciliation

## Task Breakdown

### Task 1: Create core/reconciliation.md
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Create `core/reconciliation.md` as the platform-agnostic reconciliation module. Must use abstract tool operations in argument form throughout (`READ_FILE(<path>)`, not bare `READ_FILE`). Must include non-interactive fallback for reconcile mode.

**Implementation Steps:**
1. Write mode detection section (trigger patterns for audit and reconcile)
2. Write audit workflow (5 checks with Healthy/Warning/Drift per check)
3. Write audit report format (single-spec and all-specs)
4. Write reconcile workflow (interactive repair per finding type)
5. Write platform adaptation rules (canAccessGit, canAskInteractive)
6. Verify: generate one platform output and read it to confirm all abstract op substitutions are grammatical

**Acceptance Criteria:**
- [x] Module covers all 5 audit checks with correct severity levels
- [x] All abstract operations use argument form: `READ_FILE(<path>)`, `FILE_EXISTS(<path>)`, `RUN_COMMAND(<cmd>)`, `LIST_DIR(<path>)`, `ASK_USER(<msg>)`, `NOTIFY_USER(<msg>)`
- [x] Non-interactive fallback for reconcile is explicit (`canAskInteractive = false` → blocked with message)
- [x] `canAccessGit = false` graceful degradation documented
- [x] git commands use quoted path arguments (security — no command injection)

**Files to Modify:**
- `core/reconciliation.md` (new file)

**Tests Required:**
- [x] Manual: read generated platform output and verify no "at and" / "using " broken phrases from missing args

---

### Task 2: Update core/workflow.md for mode detection
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**Domain:** core
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add audit/reconcile mode detection to the Getting Started routing chain in `core/workflow.md`. Insert between steering and interview steps. Use semantic reference (not a hard-coded step number) to avoid Gap 21 drift.

**Implementation Steps:**
1. Open `core/workflow.md` Getting Started section
2. After the steering command check, add: "Check if the request is an **audit** or **reconcile** command (see Reconciliation module). Patterns: `audit`, `audit <name>`, `health check`, `check drift`, `spec health` for audit; `reconcile <name>`, `fix <name>`, `repair <name>`, `sync <name>` for reconcile. These must refer to SpecOps spec health, NOT product features. If so, follow the Reconciliation module workflow instead of the standard phases below."

**Acceptance Criteria:**
- [x] New routing step added to Getting Started between steering and interview
- [x] Trigger patterns match what is documented in core/reconciliation.md
- [x] No hard-coded step numbers used in the new text

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Read the updated section and verify wording is unambiguous

---

### Task 3: Wire into generator pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**Domain:** generator
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add `"reconciliation": core["reconciliation"]` to all 4 context dicts in `generator/generate.py`. Add `{{ reconciliation }}` placeholder to all 4 Jinja2 templates after `{{ view }}`.

**Implementation Steps:**
1. Edit `generator/generate.py`: add `"reconciliation": core["reconciliation"]` to context in `generate_claude`, `generate_cursor`, `generate_codex`, `generate_copilot`
2. Edit `generator/templates/claude.j2`: add `{{ reconciliation }}` after `{{ view }}`
3. Edit `generator/templates/cursor.j2`: add `{{ reconciliation }}` after `{{ view }}`
4. Edit `generator/templates/codex.j2`: add `{{ reconciliation }}` after `{{ view }}`
5. Edit `generator/templates/copilot.j2`: add `{{ reconciliation }}` after `{{ view }}`

**Acceptance Criteria:**
- [x] All 4 context dicts in generate.py include `"reconciliation"` key
- [x] All 4 Jinja2 templates include `{{ reconciliation }}` after `{{ view }}`
- [x] `python3 generator/generate.py --all` runs without errors

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

**Tests Required:**
- [x] Run `python3 generator/generate.py --all` without errors

---

### Task 4: Add RECONCILIATION_MARKERS to validate.py
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** High
**Domain:** generator
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add `RECONCILIATION_MARKERS` list to `generator/validate.py` and integrate into `validate_platform()` and the cross-platform consistency check. Markers must use heading-level anchors to avoid collisions with prose (Gap 13 lesson).

**Implementation Steps:**
1. Add `RECONCILIATION_MARKERS` list with 9 heading-prefixed markers
2. Call `check_markers_present(platform, content, RECONCILIATION_MARKERS, "reconciliation")` inside `validate_platform()`
3. Add `RECONCILIATION_MARKERS` to the consistency markers list in `main()`

**Markers to add:**
```python
RECONCILIATION_MARKERS = [
    "## Audit Mode",
    "## Reconcile Mode",
    "### File Drift",
    "### Post-Completion Modification",
    "### Task Status Inconsistency",
    "### Staleness",
    "### Cross-Spec Conflicts",
    "### Health Summary",
    "### Audit Report",
]
```

**Acceptance Criteria:**
- [x] `RECONCILIATION_MARKERS` list defined in validate.py with 9 markers
- [x] `validate_platform()` calls `check_markers_present` with RECONCILIATION_MARKERS
- [x] `main()` cross-platform consistency check includes RECONCILIATION_MARKERS

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [x] Run `python3 generator/validate.py` and verify all platforms pass

---

### Task 5: Add reconciliation to test_platform_consistency.py
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 4
**Priority:** High
**Domain:** tests
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Add `"reconciliation"` category to `REQUIRED_MARKERS` in `tests/test_platform_consistency.py` with the same 9 markers as validate.py.

**Implementation Steps:**
1. Add `"reconciliation"` key to `REQUIRED_MARKERS` dict with 9 markers

**Acceptance Criteria:**
- [x] `"reconciliation"` category present in REQUIRED_MARKERS
- [x] Markers match RECONCILIATION_MARKERS in validate.py exactly

**Files to Modify:**
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] Run `python3 tests/test_platform_consistency.py` and verify pass

---

### Task 6: Regenerate outputs, validate, run tests, update COMMANDS.md
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Tasks 1–5
**Priority:** High
**Domain:** generator
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Run the full generation + validation pipeline. Update COMMANDS.md. Run the full test suite. Verify the dogfood proof: run `/specops audit` on all 3 completed specs.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Add `audit` and `reconcile` rows to COMMANDS.md Quick Lookup table and add a "Drift Detection" section
4. Run `bash scripts/run-tests.sh`
5. **Dogfood proof**: invoke `audit` on `.specops/ears-notation`, `.specops/bugfix-regression-analysis`, `.specops/steering-files` — record findings in implementation.md

**Acceptance Criteria:**
- [x] `python3 generator/generate.py --all` succeeds without errors
- [x] `python3 generator/validate.py` PASSED
- [x] COMMANDS.md Quick Lookup has rows for `audit` and `reconcile`
- [x] `bash scripts/run-tests.sh` all tests pass
- [x] Dogfood audit on 3 completed specs produces a real health report

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `docs/COMMANDS.md`

**Tests Required:**
- [x] All 7 tests in `bash scripts/run-tests.sh` pass

---

## Implementation Order
1. Task 1 — core module (foundation, no dependencies)
2. Task 2 — workflow routing (depends on Task 1 for trigger patterns)
3. Task 3 — generator pipeline (depends on Task 1 for module to wire)
4. Task 4 — validate.py markers (depends on Task 3 — generated outputs must exist)
5. Task 5 — consistency test (depends on Task 4 — matches same markers)
6. Task 6 — full integration (depends on all prior tasks)

## Progress Tracking
- Total Tasks: 6
- Completed: 6
- In Progress: 0
- Blocked: 0
- Pending: 0
