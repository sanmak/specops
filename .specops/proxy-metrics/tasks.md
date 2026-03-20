# Implementation Tasks: Proxy Metrics Tracking

## Task Breakdown

### Task 1: Add metrics schema to spec-schema.json
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — internal dogfood spec
**Blocker:** None

**Description:**
Add an optional `metrics` object to `spec-schema.json` with 7 integer fields (specArtifactTokensEstimate, filesChanged, linesAdded, linesRemoved, tasksCompleted, acceptanceCriteriaVerified, specDurationMinutes). All with `minimum: 0`, `additionalProperties: false`. Not added to `required` array.

**Implementation Steps:**
1. Read `spec-schema.json`
2. Add `metrics` property definition before `additionalProperties`
3. Verify existing specs still validate

**Acceptance Criteria:**
- [x] `metrics` object schema added with 7 integer properties
- [x] `additionalProperties: false` on metrics object
- [x] `metrics` is NOT in the `required` array
- [x] Existing spec.json files without `metrics` still validate

**Files to Modify:**
- `spec-schema.json`

**Tests Required:**
- [x] Schema validation test passes

---

### Task 2: Create core/metrics.md module
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** FAILED — internal dogfood spec
**Blocker:** None

**Description:**
Create the platform-agnostic metrics module with sections for metrics capture procedure, platform adaptation, and safety documentation. Uses abstract operations only.

**Implementation Steps:**
1. Create `core/metrics.md` with `## Proxy Metrics` heading
2. Write `### Metrics Capture Procedure` with 6-step collection process
3. Write `### Platform Adaptation` table
4. Write `### Metrics Safety` documenting limitations

**Acceptance Criteria:**
- [x] Module uses only abstract operations (READ_FILE, RUN_COMMAND, EDIT_FILE, NOTIFY_USER)
- [x] All 7 metrics defined with collection methodology
- [x] Safety limitations documented (chars/4 approximation, wall-clock duration, git diff scope)
- [x] Validation marker headings present: `## Proxy Metrics`, `### Metrics Capture Procedure`, `### Metrics Safety`

**Files to Modify:**
- `core/metrics.md` (new)

**Tests Required:**
- [x] Validator markers present after regeneration

---

### Task 3: Insert step 2.5 into Phase 4 in core/workflow.md
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 2
**Priority:** High
**IssueID:** FAILED — internal dogfood spec
**Blocker:** None

**Description:**
Add step 2.5 to Phase 4 using sub-step notation. References the Proxy Metrics module. No renumbering of existing steps.

**Implementation Steps:**
1. Read `core/workflow.md` Phase 4 section
2. Insert step 2.5 between step 2 and step 3
3. Verify no cross-references in `core/memory.md` are broken

**Acceptance Criteria:**
- [x] Step 2.5 inserted after step 2 (Finalize implementation.md)
- [x] No existing step numbers changed
- [x] Cross-references in `core/memory.md` still correct

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] No cross-reference breakage verified

---

### Task 4: Wire metrics into generator pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 2
**Priority:** High
**IssueID:** FAILED — internal dogfood spec
**Blocker:** None

**Description:**
Add `metrics` key to `build_common_context()` in `generator/generate.py`. Add `{{ metrics }}` to all 4 Jinja2 templates after `{{ task_delegation }}`.

**Implementation Steps:**
1. Add `"metrics": core["metrics"]` to `build_common_context()`
2. Add `{{ metrics }}` to `claude.j2` after `{{ task_delegation }}`
3. Add `{{ metrics }}` to `cursor.j2` after `{{ task_delegation }}`
4. Add `{{ metrics }}` to `codex.j2` after `{{ task_delegation }}`
5. Add `{{ metrics }}` to `copilot.j2` after `{{ task_delegation }}`

**Acceptance Criteria:**
- [x] `metrics` key in `build_common_context()` dict
- [x] `{{ metrics }}` in all 4 templates
- [x] Generator runs without errors

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds

---

### Task 5: Add validation markers
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 4
**Priority:** High
**IssueID:** FAILED — internal dogfood spec
**Blocker:** None

**Description:**
Add `METRICS_MARKERS` constant to `generator/validate.py` and check in both `validate_platform()` AND the cross-platform consistency loop. Add matching markers to `tests/test_platform_consistency.py`.

**Implementation Steps:**
1. Add `METRICS_MARKERS` constant to `validate.py`
2. Add `check_markers_present()` call in `validate_platform()`
3. Add `METRICS_MARKERS` to cross-platform consistency loop
4. Add markers to `tests/test_platform_consistency.py`

**Acceptance Criteria:**
- [x] `METRICS_MARKERS` constant with 8 markers
- [x] Markers checked in `validate_platform()` per-platform
- [x] Markers checked in cross-platform consistency loop
- [x] Matching markers in `test_platform_consistency.py`

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 6: Add spec schema tests
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**IssueID:** FAILED — internal dogfood spec
**Blocker:** None

**Description:**
Add test cases to `tests/test_spec_schema.py` for the new `metrics` object: valid with metrics, valid without (backward compat), invalid extra properties, invalid negative values.

**Implementation Steps:**
1. Read existing test patterns in `test_spec_schema.py`
2. Add test for valid spec with full metrics
3. Add test for valid spec without metrics
4. Add test for invalid extra property in metrics
5. Add test for invalid negative metric value

**Acceptance Criteria:**
- [x] 4 test cases added
- [x] All tests pass

**Files to Modify:**
- `tests/test_spec_schema.py`

**Tests Required:**
- [x] `python3 tests/test_spec_schema.py` passes

---

### Task 7: Create documentation
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1, Task 2
**Priority:** Medium
**IssueID:** FAILED — internal dogfood spec
**Domain:** docs
**Blocker:** None

**Description:**
Create `docs/TOKEN-USAGE.md` with metric definitions, benchmark data, and ROI guidance. Update `docs/REFERENCE.md`, `README.md`, `docs/STRUCTURE.md`, `.claude/commands/docs-sync.md`, and `CLAUDE.md`.

**Implementation Steps:**
1. Create `docs/TOKEN-USAGE.md`
2. Add Usage Metrics section to `docs/REFERENCE.md`
3. Add brief mention to `README.md`
4. Add `core/metrics.md` to `docs/STRUCTURE.md`
5. Add docs-sync mapping in `.claude/commands/docs-sync.md`
6. Add `metrics` to CLAUDE.md core modules list

**Acceptance Criteria:**
- [x] `docs/TOKEN-USAGE.md` created with metric definitions and benchmarks
- [x] `docs/REFERENCE.md` has Usage Metrics section
- [x] `README.md` mentions proxy metrics
- [x] `docs/STRUCTURE.md` lists `core/metrics.md`
- [x] `CLAUDE.md` core modules list includes `metrics`

**Files to Modify:**
- `docs/TOKEN-USAGE.md` (new)
- `docs/REFERENCE.md`
- `README.md`
- `docs/STRUCTURE.md`
- `.claude/commands/docs-sync.md`
- `CLAUDE.md`

**Tests Required:**
- [x] All doc references are consistent

---

### Task 8: Regenerate and validate
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7
**Priority:** High
**IssueID:** FAILED — internal dogfood spec
**Ship Blocking:** Yes
**Blocker:** None

**Description:**
Regenerate all platform outputs, run validator, run full test suite.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Verify generated files contain metrics content with platform-specific tool language

**Acceptance Criteria:**
- [x] Generator produces output without errors
- [x] Validator passes with 0 errors (including METRICS_MARKERS)
- [x] All tests pass
- [x] No raw abstract operations in generated outputs

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/plugin.json` (generated)
- `.claude-plugin/marketplace.json` (generated)

**Tests Required:**
- [x] `bash scripts/run-tests.sh` — all tests pass

---

## Implementation Order
1. Task 1 (schema) — foundation, no dependencies
2. Task 2 (core module) — foundation, no dependencies
3. Task 3 (workflow step) — depends on Task 2
4. Task 4 (generator) — depends on Task 2
5. Task 5 (validation) — depends on Task 4
6. Task 6 (schema tests) — depends on Task 1
7. Task 7 (documentation) — depends on Task 1, Task 2
8. Task 8 (regenerate) — depends on all above

## Progress Tracking
- Total Tasks: 8
- Completed: 8
- In Progress: 0
- Blocked: 0
- Pending: 0
