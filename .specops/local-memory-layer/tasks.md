# Implementation Tasks: Local Memory Layer

## Task Breakdown

### Task 1: Create core/memory.md module
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** None
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core
**Blocker:** None

**Description:**
Create the core memory module defining memory loading (Phase 1), memory writing (Phase 4), storage format specification, memory subcommand (`/specops memory`, `/specops memory seed`), and platform adaptation rules. Use abstract operations only (READ_FILE, WRITE_FILE, FILE_EXISTS, LIST_DIR, NOTIFY_USER, ASK_USER, RUN_COMMAND). Structure with H2/H3 headings that will become validator markers.

**Implementation Steps:**
1. Create `core/memory.md` with these sections:
   - `## Local Memory Layer` (H2 title)
   - `### Memory Storage Format` — decisions.json, context.md, patterns.json schemas
   - `### Memory Loading` — Phase 1 step 3.5 procedure
   - `### Memory Writing` — Phase 4 step 2.5 procedure (Decision Log extraction, context update, pattern detection)
   - `### Pattern Detection` — decision category recurrence, file overlap detection
   - `### Memory Subcommand` — mode detection, view workflow, seed workflow
   - `### Platform Adaptation` — capability-based behavior differences
   - `### Memory Safety` — path containment, content sanitization, no secrets

**Acceptance Criteria:**
- [x] core/memory.md created with all sections using abstract operations only
- [x] No platform-specific tool names in core module
- [x] H3 headings are unique and suitable as validator markers

**Files to Modify:**
- `core/memory.md` (new)

**Tests Required:**
- [x] Verify no raw abstract operations after generation (handled by validate.py)

---

### Task 2: Update core/workflow.md with memory hooks
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** core
**Blocker:** None

**Description:**
Add memory loading to Phase 1 (step 3.5, after steering files) and memory writing to Phase 4 (step 2.5, after implementation.md finalized). Add memory subcommand routing to the Getting Started section (between steering check and audit check).

**Implementation Steps:**
1. Phase 1: Insert step 3.5 after steering file loading (line 14 area) — reference the Local Memory Layer module for loading procedure
2. Phase 4: Insert step 2.5 after implementation.md finalization (before docs check) — reference the Local Memory Layer module for writing procedure
3. Getting Started: Add memory subcommand detection between the steering check (step 6) and audit check (step 7). Patterns: "memory", "show memory", "memory seed"

**Acceptance Criteria:**
- [x] Phase 1 step 3.5 references memory loading
- [x] Phase 4 step 2.5 references memory writing
- [x] Getting Started routes memory subcommand correctly
- [x] Memory subcommand patterns don't conflict with product features (e.g., "add memory cache" is NOT memory mode)

**Files to Modify:**
- `core/workflow.md`

**Tests Required:**
- [x] Memory hooks appear in generated outputs (via validate.py markers)

---

### Task 3: Wire generator pipeline
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**Ship Blocking:** Yes
**Domain:** generator
**Blocker:** None

**Description:**
Add memory module to the generator build system following the established pattern (same as reconciliation, steering, from-plan). Wire context dicts, Jinja2 placeholders, validator markers, and test markers.

**Implementation Steps:**
1. `generator/generate.py`: Add `"memory": core["memory"]` to context dicts in all 4 platform generators (generate_claude, generate_cursor, generate_codex, generate_copilot)
2. `generator/templates/claude.j2`: Add `{{ memory }}` after `{{ steering }}`
3. `generator/templates/cursor.j2`: Add `{{ memory }}` after `{{ steering }}`
4. `generator/templates/codex.j2`: Add `{{ memory }}` after `{{ steering }}`
5. `generator/templates/copilot.j2`: Add `{{ memory }}` after `{{ steering }}`
6. `generator/validate.py`: Define `MEMORY_MARKERS` constant from H3 headings in memory.md
7. `generator/validate.py`: Add `check_markers_present(platform, content, MEMORY_MARKERS, "memory")` to `validate_platform()`
8. `generator/validate.py`: Add `MEMORY_MARKERS` to the cross-platform consistency loop (CRITICAL: both places in same commit — Gap 31 lesson)
9. `tests/test_platform_consistency.py`: Add `"memory"` entry to `REQUIRED_MARKERS` dict with same markers

**Acceptance Criteria:**
- [x] `"memory"` key in all 4 platform context dicts in generate.py
- [x] `{{ memory }}` placeholder in all 4 .j2 templates
- [x] MEMORY_MARKERS defined in validate.py
- [x] MEMORY_MARKERS in validate_platform() check
- [x] MEMORY_MARKERS in cross-platform consistency loop
- [x] "memory" entry in test_platform_consistency.py REQUIRED_MARKERS

**Files to Modify:**
- `generator/generate.py`
- `generator/templates/claude.j2`
- `generator/templates/cursor.j2`
- `generator/templates/codex.j2`
- `generator/templates/copilot.j2`
- `generator/validate.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] validate.py passes with MEMORY_MARKERS in all platforms
- [x] test_platform_consistency.py passes with memory markers

---

### Task 4: Regenerate outputs, validate, and run full test suite
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 2, Task 3
**Priority:** High
**Ship Blocking:** Yes
**Domain:** build
**Blocker:** None

**Description:**
Regenerate all platform outputs, run validation, and execute the full test suite. Update docs/COMMANDS.md with memory subcommand entry.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py`
3. Run `bash scripts/run-tests.sh`
4. Update `docs/COMMANDS.md` with memory subcommand row in Quick Lookup table
5. Fix any issues found in steps 1–3

**Acceptance Criteria:**
- [x] All platform outputs regenerated successfully
- [x] validate.py passes with zero errors
- [x] All tests pass
- [x] docs/COMMANDS.md has memory subcommand entry

**Files to Modify:**
- `platforms/claude/SKILL.md` (generated)
- `platforms/cursor/specops.mdc` (generated)
- `platforms/codex/SKILL.md` (generated)
- `platforms/copilot/specops.instructions.md` (generated)
- `skills/specops/SKILL.md` (generated)
- `.claude-plugin/` (generated)
- `docs/COMMANDS.md`

**Tests Required:**
- [x] `python3 generator/validate.py` exits 0
- [x] `bash scripts/run-tests.sh` exits 0

---

### Task 5: Dogfood — seed memory from Specs 1–4
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 4
**Priority:** Medium
**Ship Blocking:** No
**Domain:** dogfood
**Blocker:** None

**Description:**
Manually seed the memory layer by reading all 4 completed specs' implementation.md files and creating the initial `decisions.json`, `context.md`, and `patterns.json`. This proves the memory layer works and provides real data for the content artifact.

**Implementation Steps:**
1. Create `.specops/memory/` directory
2. Read all 4 implementation.md files, extract Decision Log entries
3. Create `decisions.json` with extracted decisions
4. Create `context.md` with spec completion summaries
5. Create `patterns.json` with detected patterns (decision categories, file overlaps)
6. Verify: simulated Phase 1 loading reads the files correctly

**Acceptance Criteria:**
- [x] `.specops/memory/decisions.json` populated with decisions from Specs 1–4
- [x] `.specops/memory/context.md` has completion summaries for all 4 specs
- [x] `.specops/memory/patterns.json` has detected patterns
- [x] Memory files are valid JSON / well-formed markdown

**Files to Modify:**
- `.specops/memory/decisions.json` (new)
- `.specops/memory/context.md` (new)
- `.specops/memory/patterns.json` (new)

**Tests Required:**
- [x] decisions.json is valid JSON with version field
- [x] patterns.json is valid JSON with version field

---

## Implementation Order
1. Task 1 (core module — foundation)
2. Task 2 + Task 3 (parallel — workflow hooks + generator pipeline, independent changes)
3. Task 4 (integration — regenerate and validate)
4. Task 5 (dogfood — seed with real data, non-blocking)

## Progress Tracking
- Total Tasks: 5
- Completed: 5
- In Progress: 0
- Blocked: 0
- Pending: 0
