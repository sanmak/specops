# Implementation Tasks: Plan Mode Blocking Enforcement

## Task Breakdown

### Task 1: Delete `core/dependency-introduction.md`
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #218
**Blocker:** None
**Domain:** cleanup
**Ship Blocking:** Yes

**Description:**
Delete `core/dependency-introduction.md` which was created outside the SpecOps workflow (direct implementation that bypassed from-plan). This is the prerequisite rollback before implementing the blocking enforcement.

**Implementation Steps:**
1. Verify `core/dependency-introduction.md` exists
2. Delete the file
3. Commit with `chore: remove core/dependency-introduction.md created outside SpecOps workflow`

**Acceptance Criteria:**
- [x] `core/dependency-introduction.md` no longer exists
- [x] No references to the deleted file remain in generated outputs

**Files to Modify:**
- `core/dependency-introduction.md` (DELETE)

**Tests Required:**
- [x] `python3 generator/validate.py` passes without the file

---

### Task 2: Update `.claude/settings.local.json`
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #219
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Update the PostToolUse ExitPlanMode hook command from advisory-only to marker-creating. Add a new PreToolUse hook entry for Write|Edit that checks the marker file and blocks non-spec writes.

**Implementation Steps:**
1. Read existing `.claude/settings.local.json`
2. Replace the PostToolUse ExitPlanMode command with the marker-creating version
3. Add a PreToolUse entry with matcher `Write|Edit` and the Python3 guard script
4. Preserve all existing settings (permissions, etc.)

**Acceptance Criteria:**
- [x] PostToolUse hook creates `.plan-pending-conversion` marker file
- [x] PreToolUse hook blocks Write/Edit when marker exists
- [x] PreToolUse hook allows writes to specsDir, `.claude/plans/`, `.claude/memory/`
- [x] Existing settings preserved
- [x] File is valid JSON

**Files to Modify:**
- `.claude/settings.local.json`

**Tests Required:**
- [x] File is valid JSON after modification
- [x] `# specops-hook` marker present in PostToolUse command
- [x] `# specops-plan-guard` marker present in PreToolUse command

---

### Task 3: Update `core/from-plan.md`
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**IssueID:** #220
**Blocker:** None
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Add marker file detection at the start of the from-plan workflow (after step 1) and marker removal after the enforcement pass (step 6.5). Uses abstract operations only.

**Implementation Steps:**
1. After step 1 (plan content received): add marker detection using FILE_EXISTS and NOTIFY_USER
2. After step 6.5 (enforcement pass succeeds): add marker removal using RUN_COMMAND(`rm -f`) and NOTIFY_USER

**Acceptance Criteria:**
- [x] Marker detection added after step 1 with NOTIFY_USER if found
- [x] Marker removal added after step 6.5 with NOTIFY_USER confirmation
- [x] Uses abstract operations only (FILE_EXISTS, RUN_COMMAND, NOTIFY_USER)
- [x] Marker persists if from-plan fails before step 6.5

**Files to Modify:**
- `core/from-plan.md`

**Tests Required:**
- [x] No platform-specific tool names in `core/from-plan.md`
- [x] `python3 generator/validate.py` passes

---

### Task 4: Update `core/dispatcher.md`
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** High
**IssueID:** #221
**Blocker:** None
**Domain:** core
**Ship Blocking:** Yes

**Description:**
Update step 10.5 (post-plan acceptance gate) to reference the marker file and its role in blocking enforcement. The existing behavioral detection remains, now strengthened by the hook-created marker.

**Implementation Steps:**
1. Locate step 10.5 in the Mode Router table
2. Add reference to the `.plan-pending-conversion` marker and PreToolUse blocking
3. Note that the hook creates the marker and the dispatcher should route to from-plan if it exists

**Acceptance Criteria:**
- [x] Step 10.5 references the `.plan-pending-conversion` marker
- [x] Step 10.5 explains that the ExitPlanMode hook creates the marker
- [x] Uses abstract operations only

**Files to Modify:**
- `core/dispatcher.md`

**Tests Required:**
- [x] No platform-specific tool names in `core/dispatcher.md`
- [x] `python3 generator/validate.py` passes

---

### Task 5: Update `platforms/claude/install.sh`
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 2
**Priority:** High
**IssueID:** #222
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Update the PostToolUse hook command from advisory to marker-creating. Add PreToolUse hook installation using the same idempotent Python3 injection pattern. Check for `specops-plan-guard` marker to avoid duplicates.

**Implementation Steps:**
1. Update the PostToolUse hook command string to the marker-creating version
2. Add PreToolUse hook installation after the PostToolUse section
3. Implement idempotent check using `specops-plan-guard` marker
4. Write back to settings file with same pattern as PostToolUse injection

**Acceptance Criteria:**
- [x] PostToolUse hook uses marker-creating command
- [x] PreToolUse hook installed with Write|Edit matcher
- [x] `specops-plan-guard` marker enables idempotent detection
- [x] Running installer twice produces no duplicate hooks
- [x] Pre-existing settings.json content is preserved

**Files to Modify:**
- `platforms/claude/install.sh`

**Tests Required:**
- [x] `shellcheck platforms/claude/install.sh` passes
- [x] Fresh install creates both hooks in settings.json
- [x] Repeat install is idempotent

---

### Task 6: Update `scripts/remote-install.sh`
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** Task 5
**Priority:** High
**IssueID:** #223
**Blocker:** None
**Domain:** devops
**Ship Blocking:** Yes

**Description:**
Mirror the PostToolUse and PreToolUse hook changes from the local installer into the remote installer. Same Python3 injection pattern, using `$install_dir` to determine scope.

**Implementation Steps:**
1. Update the PostToolUse hook command in `install_claude()` to the marker-creating version
2. Add PreToolUse hook installation mirroring local installer
3. Same idempotent check using `specops-plan-guard` marker

**Acceptance Criteria:**
- [x] PostToolUse hook uses marker-creating command (same as local installer)
- [x] PreToolUse hook installed (same as local installer)
- [x] Uses `$install_dir` for scope determination
- [x] Idempotent behavior matches local installer

**Files to Modify:**
- `scripts/remote-install.sh`

**Tests Required:**
- [x] `shellcheck scripts/remote-install.sh` passes
- [x] Remote install produces same hooks as local install

---

### Task 7: Update `.gitignore`
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** None
**Priority:** Medium
**IssueID:** #224
**Blocker:** None
**Domain:** config
**Ship Blocking:** No

**Description:**
Add `.plan-pending-conversion` to `.gitignore` to prevent the ephemeral marker file from being committed.

**Implementation Steps:**
1. Add a comment and the marker file pattern to `.gitignore`

**Acceptance Criteria:**
- [x] `.plan-pending-conversion` is listed in `.gitignore`
- [x] Comment explains the marker is ephemeral

**Files to Modify:**
- `.gitignore`

**Tests Required:**
- [x] `git check-ignore .specops/.plan-pending-conversion` returns the file

---

### Task 8: Regenerate Platform Outputs
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Tasks 3, 4
**Priority:** High
**IssueID:** #225
**Blocker:** None
**Domain:** build
**Ship Blocking:** Yes

**Description:**
Regenerate all platform outputs after modifying `core/from-plan.md` and `core/dispatcher.md`. Required by the project's build rules.

**Implementation Steps:**
1. Run `python3 generator/generate.py --all`
2. Verify no errors in output

**Acceptance Criteria:**
- [x] `python3 generator/generate.py --all` completes without errors
- [x] Generated files reflect the core module changes

**Files to Modify:**
- All files under `platforms/*/` (generated)

**Tests Required:**
- [x] `python3 generator/validate.py` passes
- [x] `bash scripts/run-tests.sh` passes

---

### Task 9: Validate and Test
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 8
**Priority:** High
**IssueID:** #226
**Blocker:** None
**Domain:** test
**Ship Blocking:** Yes

**Description:**
Run the full validation and test suite to ensure all changes are correct and no regressions were introduced.

**Implementation Steps:**
1. Run `python3 generator/validate.py`
2. Run `bash scripts/run-tests.sh`
3. Run `shellcheck platforms/claude/install.sh scripts/remote-install.sh`

**Acceptance Criteria:**
- [x] `python3 generator/validate.py` passes (200+ checks)
- [x] `bash scripts/run-tests.sh` passes (all tests)
- [x] ShellCheck clean on modified shell scripts

**Files to Modify:**
- None (validation only)

**Tests Required:**
- [x] All validation and test commands pass

---

### Task 10: Update Documentation and Checksums
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 9
**Priority:** Medium
**IssueID:** #227
**Blocker:** None
**Domain:** docs
**Ship Blocking:** No

**Description:**
Update documentation files to reflect the new blocking enforcement mechanism. Regenerate checksums for all modified checksummed files.

**Implementation Steps:**
1. Update `CLAUDE.md` to mention plan enforcement hooks
2. Update `docs/REFERENCE.md` to document the marker file and hooks behavior
3. Update `CHANGELOG.md` with the enforcement upgrade
4. Run `bash scripts/bump-version.sh` or regenerate checksums manually

**Acceptance Criteria:**
- [x] `CLAUDE.md` references plan enforcement hooks
- [x] `docs/REFERENCE.md` documents marker file lifecycle
- [x] `CHANGELOG.md` includes the enforcement upgrade entry
- [x] Checksums valid after regeneration

**Files to Modify:**
- `CLAUDE.md`
- `docs/REFERENCE.md`
- `CHANGELOG.md`
- `CHECKSUMS.sha256`

**Tests Required:**
- [x] `shasum -a 256 -c CHECKSUMS.sha256` passes
- [x] Markdown lint passes on modified docs
