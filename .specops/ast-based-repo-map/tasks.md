# Implementation Tasks: AST-Based Repo Map

## Task Breakdown

### Task 1: Create `core/repo-map.md` Module
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core

**Description:**
Create the new core module defining the repo map format, generation algorithm, staleness detection, scope control, language tiers, `/specops map` subcommand, safety rules, and platform adaptation. All instructions use abstract operations from `core/tool-abstraction.md`.

**Implementation Steps:**
1. Create `core/repo-map.md` with 8 H3 sections under an H2 heading
2. Define the repo-map.md output format with YAML frontmatter fields (`_generated`, `_generatedAt`, `_sourceHash`)
3. Write the generation algorithm using LIST_DIR, READ_FILE, RUN_COMMAND, FILE_EXISTS, WRITE_FILE
4. Define 4-tier language extraction (Python, TS/JS, Go/Rust/Java, other)
5. Define staleness detection (time-based 7 days + hash-based file list comparison)
6. Define scope control (100 files, depth 3, ~3000 token budget, tiered truncation)
7. Define `/specops map` subcommand detection and workflow
8. Define safety rules (path containment, no secrets, convention sanitization)
9. Define platform adaptation table

**Acceptance Criteria:**
- [x] Module uses only abstract operations (no platform-specific tool names)
- [x] All 8 H3 sections present (these become validator markers)
- [x] Generation algorithm is complete and self-contained
- [x] Staleness detection covers both time and hash checks
- [x] Safety rules follow existing patterns from steering.md and memory.md

**Files to Modify:**
- `core/repo-map.md` (new)

**Tests Required:**
- [x] Module passes abstract operation check (no raw tool names)

---

### Task 2: Wire Repo Map into `core/workflow.md`
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core

**Description:**
Insert repo map integration into two locations in `core/workflow.md`: Phase 1 step 3.5 (auto-detect missing/stale repo map) and Getting Started subcommand routing (new step 8 for `/specops map`).

**Implementation Steps:**
1. Add step 3.5 between step 3 (Load steering files) and step 4 (Load memory) in Phase 1
2. Step 3.5 references the Repo Map module for the full algorithm
3. Add `/specops map` detection to Getting Started as new step 8
4. Renumber steps 8-15 to 9-16 in Getting Started
5. Add disambiguation rule: "map" must refer to SpecOps repo map, not product features

**Acceptance Criteria:**
- [x] Phase 1 step 3.5 added with repo map freshness check
- [x] Getting Started step 8 routes `/specops map` subcommand
- [x] Subsequent Getting Started steps renumbered correctly
- [x] Disambiguation rule present for "map" keyword

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Workflow markers still present after edit (Phase 1-4, Version Extraction Protocol)

---

### Task 3: Update `core/steering.md` with Generated-File Fields
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core

**Description:**
Document three new YAML frontmatter fields for machine-generated steering files in `core/steering.md`: `_generated` (boolean), `_generatedAt` (ISO 8601), `_sourceHash` (string). Add note about read-only display in `/specops steering`.

**Implementation Steps:**
1. Add rows to the frontmatter fields table for `_generated`, `_generatedAt`, `_sourceHash`
2. Add note: underscore-prefixed fields are system-managed, not user-editable
3. Update `/specops steering` command section: files with `_generated: true` shown as read-only

**Acceptance Criteria:**
- [x] Three new fields documented in frontmatter table
- [x] System-managed field convention noted
- [x] Steering command updated for read-only display

**Files to Modify:**
- `core/steering.md`

**Tests Required:**
- [x] Steering markers still present after edit

---

### Task 4: Wire `repo_map` into Generator Pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** generator

**Description:**
Add `repo_map` to the generator context dictionary in `generate.py` and add `{{ repo_map }}` placeholder to all 4 Jinja2 templates.

**Implementation Steps:**
1. In `generator/generate.py`, add `"repo-map"` to core module loading (it auto-loads from `core/repo-map.md`)
2. Add `"repo_map": core["repo-map"]` to the context dict passed to `render_template()`
3. In each Jinja2 template, add `{{ repo_map }}` after `{{ memory }}`

**Acceptance Criteria:**
- [x] `repo_map` context variable available in all 4 platform generators
- [x] `{{ repo_map }}` placeholder in claude.j2, cursor.j2, codex.j2, copilot.j2
- [x] Placeholder positioned after `{{ memory }}`

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`

**Tests Required:**
- [x] `python3 generator/generate.py --all` succeeds

---

### Task 5: Add REPO_MAP_MARKERS to Validator + Cross-Platform Check
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** tests

**Description:**
Define `REPO_MAP_MARKERS` in `generator/validate.py` matching the H2/H3 headings from `core/repo-map.md`. Add to both `validate_platform()` (per-platform check) and the cross-platform consistency concatenation on line 535. Also add to `tests/test_platform_consistency.py`. **Gap 31 enforcement: both locations in same commit.**

**Implementation Steps:**
1. Define `REPO_MAP_MARKERS` list matching H2/H3 headings from Task 1
2. Add `check_markers_present(platform, content, REPO_MAP_MARKERS, "repo-map")` to `validate_platform()`
3. Add `+ REPO_MAP_MARKERS` to the cross-platform consistency loop (line 535)
4. Add repo map markers to `REQUIRED_MARKERS` in `tests/test_platform_consistency.py`

**Acceptance Criteria:**
- [x] REPO_MAP_MARKERS defined with correct heading strings
- [x] Per-platform validation includes repo-map markers
- [x] Cross-platform consistency check includes repo-map markers
- [x] test_platform_consistency.py updated

**Files to Modify:**
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes with repo-map markers
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 6: Regenerate Platform Outputs + Validate
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5
**Priority:** High
**Ship Blocking:** Yes
**Domain:** generator

**Description:**
Run the full generator pipeline, validate all outputs, and run the test suite to confirm everything passes.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Verify no raw abstract operations in generated outputs
5. Verify REPO_MAP_MARKERS present in all 4 platforms

**Acceptance Criteria:**
- [x] Generator succeeds for all 4 platforms
- [x] Validator passes all checks including repo-map markers
- [x] All tests pass
- [x] No raw abstract operations in generated output

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

---

### Task 7: Update Documentation
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 2
**Priority:** Medium
**Ship Blocking:** No
**Domain:** docs

**Description:**
Add `/specops map` to the command reference in `docs/COMMANDS.md` and update `CLAUDE.md` if needed.

**Implementation Steps:**
1. Add row to `docs/COMMANDS.md` Quick Reference table for `/specops map`
2. Check if `core/repo-map.md` should be in `CLAUDE.md` security-sensitive files list
3. Update `CLAUDE.md` "What to Do After Changes" table if needed

**Acceptance Criteria:**
- [x] `/specops map` row in COMMANDS.md Quick Reference
- [x] CLAUDE.md updated if applicable (not needed — follows existing pattern)

**Files to Modify:**
- `docs/COMMANDS.md`
- `CLAUDE.md`

**Tests Required:**
- [x] No broken markdown formatting

---

## Implementation Order
1. Task 1 (foundation — core module)
2. Task 2 + Task 3 (parallel — workflow + steering, both depend on Task 1)
3. Task 4 (generator pipeline — depends on Task 1)
4. Task 5 (validator — depends on Task 1 headings)
5. Task 6 (regenerate + validate — depends on Tasks 1-5)
6. Task 7 (docs — depends on Task 2 for subcommand name)

## Progress Tracking
- Total Tasks: 7
- Completed: 7
- In Progress: 0
- Blocked: 0
- Pending: 0
