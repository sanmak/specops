# Implementation Tasks: Context-Aware Dispatch

## Task Breakdown

### Task 1: Create core/dispatcher.md and core/mode-manifest.json
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #97
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Create the dispatcher core module with routing logic, enforcement gates (including the pre-Phase-3 checklist), dispatch protocol, and shared context block. Create the mode manifest JSON mapping each mode to its required core modules.

**Implementation Steps:**
1. Create `core/dispatcher.md` with: agent identity, version extraction, config loading, safety rules, enforcement gates (pre-Phase-3 checklist with 7 checks), mode router (12 patterns), dispatch protocol (read mode file → prepend shared context → spawn agent → post-verify), shared context block template
2. Create `core/mode-manifest.json` mapping 13 modes to their core module lists
3. Verify manifest references all relevant core/*.md files

**Acceptance Criteria:**
- [x] `core/dispatcher.md` exists with all sections
- [x] Pre-Phase-3 checklist has 7 deterministic checks including IssueID verification
- [x] `core/mode-manifest.json` maps all 13 modes to core modules
- [x] Every core/*.md module appears in at least one mode's module list

**Files to Modify:**
- `core/dispatcher.md` (new)
- `core/mode-manifest.json` (new)

**Tests Required:**
- [x] mode-manifest.json is valid JSON
- [x] All core/*.md files referenced in manifest exist

---

### Task 2: Create claude-dispatcher.j2 template
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #98
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Create the Jinja2 template for the dispatcher SKILL.md. This replaces the monolithic `claude.j2` for the dispatcher output while the monolithic template continues to be used for backward-compatible output.

**Implementation Steps:**
1. Create `generator/templates/claude-dispatcher.j2` with YAML frontmatter, dispatcher module content, and mode routing table
2. Template should reference the dispatcher core module with tool substitution applied
3. Verify template renders to under 400 lines

**Acceptance Criteria:**
- [x] `generator/templates/claude-dispatcher.j2` exists
- [x] Template produces valid SKILL.md with frontmatter
- [x] Output is under 400 lines

**Files to Modify:**
- `generator/templates/claude-dispatcher.j2` (new)

**Tests Required:**
- [x] Template renders without errors

---

### Task 3: Add generate_claude_modes() to generator
**Status:** Completed
**Estimated Effort:** L
**Dependencies:** Task 1, Task 2
**Priority:** High
**IssueID:** #99
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Add the mode file generation function to `generator/generate.py`. This reads `core/mode-manifest.json`, assembles per-mode files by concatenating the listed core modules with tool substitution, and writes them to `platforms/claude/modes/`. Also update `generate_claude()` to produce both dispatcher and mode files.

**Implementation Steps:**
1. Add `generate_claude_modes()` function that reads manifest, concatenates modules per mode, applies tool substitution, writes to `platforms/claude/modes/`
2. Update `generate_claude()` to call the new function alongside existing monolithic generation
3. Add mode files to the `skills/specops/` sync (copy `modes/` directory)
4. Run `python3 generator/generate.py --all` and verify output

**Acceptance Criteria:**
- [x] `platforms/claude/modes/` contains 13 .md files
- [x] Each mode file has tool substitution applied (no raw abstract ops)
- [x] `skills/specops/modes/` synced with `platforms/claude/modes/`
- [x] Monolithic SKILL.md still generated (backward compatibility)
- [x] `python3 generator/generate.py --all` succeeds

**Files to Modify:**
- `generator/generate.py`
- `platforms/claude/modes/` (new, generated)
- `skills/specops/modes/` (new, generated)

**Tests Required:**
- [x] Generator produces all expected files
- [x] No raw abstract operations in any mode file
- [x] `python3 generator/validate.py` passes (deferred to Task 4)

---

### Task 4: Update validator for split-file checking
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3
**Priority:** High
**IssueID:** #101
**Blocker:** None
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Update `generator/validate.py` to check markers across Claude's dispatcher + mode files (union) instead of just the monolithic SKILL.md. Update cross-platform consistency check.

**Implementation Steps:**
1. For Claude: load dispatcher + all mode files, concatenate content, check markers against union
2. Add dispatcher-specific checks: all 12 mode patterns present, safety markers in dispatcher, enforcement gate language present
3. Update cross-platform consistency: Claude's union content vs other platforms' monolithic content
4. Keep existing monolithic check as secondary validation

**Acceptance Criteria:**
- [x] Validator checks Claude markers across dispatcher + mode files
- [x] Dispatcher-specific validation passes
- [x] Cross-platform consistency check passes
- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes

**Files to Modify:**
- `generator/validate.py`

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `python3 tests/test_platform_consistency.py` passes

---

### Task 5: Add /pre-pr IssueID verification
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #102
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Add Step 2e to `.claude/commands/pre-pr.md` that checks IssueID population when taskTracking is configured. Add IssueID Check row to the dashboard.

**Implementation Steps:**
1. Read `.specops.json` to check taskTracking config
2. If not "none": scan implementing/completed specs for missing IssueIDs on High/Medium tasks
3. Add ISSUEID_RESULT to dashboard output
4. FAIL if any IssueIDs are missing

**Acceptance Criteria:**
- [x] Step 2e added to pre-pr.md
- [x] IssueID Check row appears in dashboard
- [x] Check skipped when taskTracking is "none"

**Files to Modify:**
- `.claude/commands/pre-pr.md`

**Tests Required:**
- [x] Command file is valid markdown

---

### Task 6: Update installation scripts
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** High
**IssueID:** #103
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Update `platforms/claude/install.sh` and `scripts/remote-install.sh` to copy the `modes/` directory alongside SKILL.md during Claude installation.

**Implementation Steps:**
1. Update `platforms/claude/install.sh` to copy `modes/` directory
2. Update `scripts/remote-install.sh` to copy `modes/` directory for Claude platform
3. Run shellcheck on modified scripts

**Acceptance Criteria:**
- [x] `install.sh` copies modes/ directory
- [x] `remote-install.sh` copies modes/ directory
- [x] `shellcheck` passes on both scripts

**Files to Modify:**
- `platforms/claude/install.sh`
- `scripts/remote-install.sh`

**Tests Required:**
- [x] `shellcheck platforms/claude/install.sh` passes
- [x] `shellcheck scripts/remote-install.sh` passes

---

### Task 7: Update tests
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3, Task 4
**Priority:** Medium
**IssueID:** #105
**Blocker:** None
**Domain:** backend
**Ship Blocking:** No

**Description:**
Update test suite to verify the new split output: build tests verify generator produces dispatcher + modes, consistency tests verify marker coverage across split files.

**Implementation Steps:**
1. Update `tests/test_build.py` to verify Claude produces dispatcher + 13 mode files
2. Update `tests/test_platform_consistency.py` to verify Claude's split output covers same markers
3. Run full test suite

**Acceptance Criteria:**
- [x] `test_build.py` verifies dispatcher + mode files exist
- [x] `test_platform_consistency.py` verifies cross-platform marker parity
- [x] `bash scripts/run-tests.sh` passes

**Files to Modify:**
- `tests/test_build.py`
- `tests/test_platform_consistency.py`

**Tests Required:**
- [x] `bash scripts/run-tests.sh` passes (all tests)

---

### Task 8: Update documentation
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 3
**Priority:** Medium
**IssueID:** #106
**Blocker:** None
**Domain:** docs
**Ship Blocking:** No

**Description:**
Update README.md with Context-Aware Dispatch section, comparison table row, and "Why SpecOps" bullet. Update CLAUDE.md and docs/STRUCTURE.md with new architecture.

**Implementation Steps:**
1. Add "Context-Aware Dispatch" section to README.md after Architecture
2. Add comparison table row (SpecOps: Yes, Kiro: No, Spec Kit: No)
3. Add "Why SpecOps" bullet about context reduction
4. Update CLAUDE.md with new architecture description
5. Update docs/STRUCTURE.md with `platforms/claude/modes/` directory

**Acceptance Criteria:**
- [x] README.md has Context-Aware Dispatch section
- [x] Comparison table has new row
- [x] CLAUDE.md documents new architecture
- [x] docs/STRUCTURE.md lists modes/ directory

**Files to Modify:**
- `README.md`
- `CLAUDE.md`
- `docs/STRUCTURE.md`

**Tests Required:**
- [x] `python3 generator/validate.py` docs coverage check passes

---

### Task 9: Update plugin distribution
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 3
**Priority:** Medium
**IssueID:** #107
**Blocker:** None
**Domain:** devops
**Ship Blocking:** No

**Description:**
Ensure plugin manifests and skills directory include the modes/ files for Claude plugin distribution.

**Implementation Steps:**
1. Verify `.claude-plugin/plugin.json` structure supports additional files
2. Ensure `skills/specops/modes/` is synced by generator
3. Test plugin installation includes mode files

**Acceptance Criteria:**
- [x] `skills/specops/modes/` exists with all mode files
- [x] Plugin distribution includes mode files

**Files to Modify:**
- `.claude-plugin/plugin.json` (if needed)
- Generator sync logic (already in Task 3)

**Tests Required:**
- [x] Plugin manifest validation passes

---

### Task 10: Update core/dispatcher.md docs coverage
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Low
**IssueID:** None
**Blocker:** None
**Domain:** docs
**Ship Blocking:** No

**Description:**
Add the new core modules to docs/STRUCTURE.md and .claude/commands/docs-sync.md dependency map.

**Implementation Steps:**
1. Add `core/dispatcher.md` and `core/mode-manifest.json` to docs/STRUCTURE.md
2. Add mappings to docs-sync.md dependency map
3. Run docs coverage validation

**Acceptance Criteria:**
- [x] New modules listed in docs/STRUCTURE.md
- [x] docs-sync.md has mappings for new modules
- [x] `python3 generator/validate.py` docs coverage passes

**Files to Modify:**
- `docs/STRUCTURE.md`
- `.claude/commands/docs-sync.md`

**Tests Required:**
- [x] `python3 generator/validate.py` passes

---

## Implementation Order
1. Task 1 (core modules — foundation)
2. Task 5 (/pre-pr IssueID — independent, quick win)
3. Task 2 (dispatcher template — depends on Task 1)
4. Task 3 (generator — depends on Tasks 1, 2)
5. Task 4 (validator — depends on Task 3)
6. Task 6 (installation — depends on Task 3)
7. Task 7 (tests — depends on Tasks 3, 4)
8. Task 8 (documentation — depends on Task 3)
9. Task 9 (plugin — depends on Task 3)
10. Task 10 (docs coverage — depends on Task 1)

## Progress Tracking
- Total Tasks: 10
- Completed: 10
- In Progress: 0
- Blocked: 0
- Pending: 0
