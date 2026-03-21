# Implementation Tasks: ExitPlanMode Hook

## Task Breakdown

### Task 1: Update `platforms/claude/install.sh`
**Status:** Done
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #130
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Add an `install_hook()` function to the local installer that injects the PostToolUse ExitPlanMode hook into the appropriate Claude Code settings.json file. Insert after modes installation (after line 108) and before the `.specops.json` metadata update (line 119).

**Implementation Steps:**
1. Add `install_hook()` function with settings file selection logic (user install -> `~/.claude/settings.json`, project install -> `./.claude/settings.json`, custom path -> `~/.claude/settings.json`)
2. Implement python3 inline JSON injection: load existing settings or create empty dict, ensure `hooks.PostToolUse` array exists, check for existing `specops-hook` marker (idempotent), append hook entry, write back with `indent=2`
3. Add graceful fallback if python3 is unavailable (warning + manual instructions)
4. Call `install_hook` from the main installation flow between modes installation and `.specops.json` metadata update

**Acceptance Criteria:**
- [x] `install_hook()` function exists in `platforms/claude/install.sh`
- [x] Settings file selection implements scope-based targeting
- [x] Running installer twice produces no duplicate hook entry
- [x] Pre-existing settings.json content is preserved
- [x] Graceful warning printed if python3 is missing

**Files to Modify:**
- `platforms/claude/install.sh`

**Tests Required:**
- [x] `shellcheck platforms/claude/install.sh` passes without warnings
- [x] Fresh install creates settings.json with hook
- [x] Repeat install is idempotent (no duplicate)
- [x] Existing settings content preserved after install

---

### Task 2: Mirror in `scripts/remote-install.sh`
**Status:** Done
**Estimated Effort:** M
**Dependencies:** Task 1
**Priority:** High
**IssueID:** #131
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Add identical hook injection inside `install_claude()` in the remote installer after line 389 ("Installed files verified") and before line 391 (`.specops.json` metadata update). Same python3 logic, using `$install_dir` to determine scope. Follows existing duplication pattern between local and remote installers.

**Implementation Steps:**
1. Add hook injection logic inside `install_claude()` after the "Installed files verified" checkpoint
2. Use `$install_dir` to determine settings file scope (same logic as Task 1)
3. Implement same python3 inline JSON injection with idempotent check
4. Add same graceful fallback for missing python3

**Acceptance Criteria:**
- [x] Hook injection present in `scripts/remote-install.sh` `install_claude()` function
- [x] Uses `$install_dir` for scope determination
- [x] Same idempotent behavior as local installer
- [x] Graceful fallback for missing python3

**Files to Modify:**
- `scripts/remote-install.sh`

**Tests Required:**
- [x] `shellcheck scripts/remote-install.sh` passes without warnings
- [x] Remote install produces same hook as local install

---

### Task 3: Dogfood in `.claude/settings.local.json`
**Status:** Done
**Estimated Effort:** S
**Dependencies:** None
**Priority:** Medium
**IssueID:** #132
**Blocker:** None
**Domain:** devops
**Ship Blocking:** No

**Description:**
Add the PostToolUse ExitPlanMode hook to the SpecOps repo's own `.claude/settings.local.json` so the project dogfoods its own hook mechanism. Merge into the existing permissions object without overwriting other settings.

**Implementation Steps:**
1. Read existing `.claude/settings.local.json` content
2. Add `hooks.PostToolUse` array with the ExitPlanMode hook entry
3. Preserve all existing settings (permissions, etc.)

**Acceptance Criteria:**
- [x] `.claude/settings.local.json` contains the PostToolUse hook
- [x] Existing settings (permissions) are preserved
- [x] Hook uses same definition as installer-injected hook

**Files to Modify:**
- `.claude/settings.local.json`

**Tests Required:**
- [x] File is valid JSON after modification

---

### Task 4: Update `docs/COMPARISON.md`
**Status:** Done
**Estimated Effort:** S
**Dependencies:** None
**Priority:** Medium
**IssueID:** #133
**Blocker:** None
**Domain:** docs
**Ship Blocking:** No

**Description:**
Update the comparison documentation to reflect SpecOps' new agent hook support. Two specific changes: update the feature matrix row for agent hooks, and update the Kiro comparison paragraph.

**Implementation Steps:**
1. Line 19: Change `| **Agent hooks** | No | Yes (10 trigger types) | No | No |` to `| **Agent hooks** | Yes (ExitPlanMode) | Yes (10 trigger types) | No | No |`
2. Line 47: Update the agent hooks comparison text to note `SpecOps' 1 (ExitPlanMode auto-trigger)` vs Kiro's 10 trigger types

**Acceptance Criteria:**
- [x] Feature matrix shows "Yes (ExitPlanMode)" for SpecOps agent hooks
- [x] Kiro comparison paragraph references SpecOps' ExitPlanMode hook
- [x] No other rows or sections modified

**Files to Modify:**
- `docs/COMPARISON.md`

**Tests Required:**
- [x] Markdown renders correctly
- [x] No unintended changes to other table rows
