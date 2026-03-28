# Feature: Plan Mode Blocking Enforcement

## Overview

Upgrade the ExitPlanMode hook enforcement from advisory to blocking. When a plan is approved in a SpecOps-configured project, Write/Edit operations on non-spec files are blocked until `/specops from-plan` converts the plan into a structured spec. Uses a PreToolUse guard with a marker file state machine. Benefits both the SpecOps project itself and end users who adopt SpecOps.

## Product Requirements

### Requirement 1: Marker File State Machine
**As a** SpecOps user approving a plan in Claude Code
**I want** Write/Edit operations on non-spec files to be blocked until the plan is converted to a spec
**So that** implementation cannot bypass the spec-driven workflow

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN ExitPlanMode fires in a SpecOps-configured project THE SYSTEM SHALL create a `.plan-pending-conversion` marker file in the specsDir directory -->
<!-- EARS: WHEN the marker file exists AND a Write or Edit operation targets a file outside specsDir, .claude/plans/, or .claude/memory/ THE SYSTEM SHALL block the operation with exit code 2 and a message directing the user to run /specops from-plan -->
<!-- EARS: WHEN the marker file exists AND a Write or Edit operation targets a file inside specsDir, .claude/plans/, or .claude/memory/ THE SYSTEM SHALL allow the operation (exit code 0) -->
<!-- EARS: WHEN /specops from-plan completes its enforcement pass successfully THE SYSTEM SHALL remove the marker file, unblocking all Write/Edit operations -->
<!-- EARS: IF /specops from-plan fails before the enforcement pass THE SYSTEM SHALL retain the marker file so writes remain blocked until conversion succeeds -->

### Requirement 2: PostToolUse Hook Upgrade
**As a** SpecOps user
**I want** the existing PostToolUse ExitPlanMode hook to create the marker file instead of only emitting an advisory message
**So that** enforcement is deterministic rather than relying on agent compliance

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN ExitPlanMode fires THE SYSTEM SHALL read specsDir from .specops.json (defaulting to .specops), create the directory if needed, and touch the .plan-pending-conversion marker -->
<!-- EARS: WHEN .specops.json does not exist THE SYSTEM SHALL exit silently (not a SpecOps project) -->
<!-- EARS: THE SYSTEM SHALL emit a user-visible message stating that Write/Edit is blocked until /specops from-plan runs -->

### Requirement 3: PreToolUse Write/Edit Guard
**As a** SpecOps user
**I want** a PreToolUse hook that intercepts Write and Edit operations when the marker file is present
**So that** the agent cannot bypass the spec conversion step

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN a Write or Edit tool is invoked THE SYSTEM SHALL check for the .plan-pending-conversion marker file -->
<!-- EARS: WHEN the marker does not exist THE SYSTEM SHALL allow the operation immediately (exit code 0) -->
<!-- EARS: WHEN the marker exists THE SYSTEM SHALL read the target file_path from stdin JSON and check if it is within an allowed prefix (specsDir, .claude/plans/, .claude/memory/) -->
<!-- EARS: WHEN the target path is not in an allowed prefix THE SYSTEM SHALL print a blocking message to stderr and exit with code 2 -->
<!-- EARS: IF .specops.json does not exist THEN THE SYSTEM SHALL allow all operations (exit code 0) -->

### Requirement 4: Core Module Updates
**As a** SpecOps contributor
**I want** `core/from-plan.md` and `core/dispatcher.md` to reference the marker file lifecycle
**So that** the workflow documentation reflects the blocking enforcement mechanism

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN from-plan mode starts and the marker file exists THE SYSTEM SHALL notify the user that the marker was detected and writes will be unblocked after conversion -->
<!-- EARS: WHEN from-plan mode completes the enforcement pass (step 6.5) successfully THE SYSTEM SHALL remove the marker file and notify the user that Write/Edit is unblocked -->
<!-- EARS: THE SYSTEM SHALL update dispatcher step 10.5 to reference the marker file and its role in blocking enforcement -->

### Requirement 5: Installer Updates for End Users
**As a** SpecOps user installing via `install.sh` or `remote-install.sh`
**I want** both installers to register the PreToolUse guard hook alongside the updated PostToolUse hook
**So that** blocking enforcement is active for all SpecOps users without manual configuration

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN `platforms/claude/install.sh` runs THE SYSTEM SHALL install the PreToolUse Write|Edit guard hook in addition to the updated PostToolUse hook -->
<!-- EARS: WHEN `scripts/remote-install.sh` runs THE SYSTEM SHALL mirror the same PreToolUse hook installation -->
<!-- EARS: WHEN the PreToolUse hook already exists (identified by specops-plan-guard marker) THE SYSTEM SHALL skip injection (idempotent) -->
<!-- EARS: WHEN the PostToolUse hook already exists (identified by specops-hook marker) THE SYSTEM SHALL replace it with the marker-creating version -->

## Scope Boundary

**Ships in this spec:**
- PostToolUse hook upgrade from advisory to marker-creating
- PreToolUse Write/Edit guard with marker check
- Marker file lifecycle in `core/from-plan.md`
- Dispatcher step 10.5 reference update in `core/dispatcher.md`
- Local installer (`platforms/claude/install.sh`) updates
- Remote installer (`scripts/remote-install.sh`) updates
- `.gitignore` update for marker file
- Dogfood in `.claude/settings.local.json`
- Documentation updates (CLAUDE.md, docs/REFERENCE.md, CHANGELOG.md)
- Delete `core/dependency-introduction.md` (created outside SpecOps workflow)

**Deferred:**
- [To be defined]

## Product Quality Attributes
- Hooks must be idempotent (running installer twice produces no duplicate)
- Hooks must be inert in non-SpecOps projects (`.specops.json` guard)
- Marker file must be ephemeral (gitignored, removed on successful conversion)
- Existing settings.json content must be preserved during injection
- PreToolUse guard must allow spec-related writes (specsDir, .claude/plans/, .claude/memory/)
- ShellCheck must pass on modified shell scripts
- All existing tests must continue to pass after changes

## Constraints
- `# specops-hook` marker on PostToolUse hook enables future uninstall tooling
- `# specops-plan-guard` marker on PreToolUse hook enables identification
- Python3 inline script reuses existing installer injection pattern
- `.claude/settings.json` is gitignored by `.claude/*` pattern, so dogfood uses `.claude/settings.local.json`
- Must regenerate platform outputs after changing `core/` files
- Must regenerate checksums after changing checksummed files
- Prerequisite: delete `core/dependency-introduction.md` before starting implementation

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
