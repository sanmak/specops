# Feature: ExitPlanMode Hook for Auto-Triggering SpecOps

## Overview

When a user approves a plan in Claude Code (ExitPlanMode fires), SpecOps should automatically take over via `/specops from-plan` instead of letting the agent implement directly. Today this relies on behavioral detection (Step 10.5 in workflow.md) which is unreliable. Claude Code's `PostToolUse` hooks provide a deterministic trigger point -- the hook fires every time ExitPlanMode is called, checks for `.specops.json`, and emits an instruction the agent treats as user feedback.

## Product Requirements

### Requirement 1: Hook Injection in Local Installer
**As a** SpecOps user installing via `install.sh`
**I want** the installer to register a PostToolUse hook for ExitPlanMode in Claude Code settings
**So that** plan approval automatically triggers `/specops from-plan` in SpecOps-configured projects

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN `install.sh` runs for Claude THE SYSTEM SHALL inject a PostToolUse hook entry matching ExitPlanMode into the appropriate settings.json -->
<!-- EARS: WHEN the target is a user install (~/.claude/skills/specops) THE SYSTEM SHALL write the hook to ~/.claude/settings.json -->
<!-- EARS: WHEN the target is a project install (./.claude/skills/specops) THE SYSTEM SHALL write the hook to ./.claude/settings.json -->
<!-- EARS: WHEN the hook already exists (identified by # specops-hook marker) THE SYSTEM SHALL skip injection (idempotent) -->
<!-- EARS: IF python3 is unavailable THEN THE SYSTEM SHALL print a warning with manual instructions instead of failing -->

**Progress Checklist:**
- [ ] `install_hook()` function added to `platforms/claude/install.sh`
- [ ] Settings file selection logic implements scope-based targeting
- [ ] Idempotent check using `specops-hook` marker
- [ ] Graceful fallback when python3 is unavailable

### Requirement 2: Hook Injection in Remote Installer
**As a** SpecOps user installing via `remote-install.sh`
**I want** the remote installer to register the same PostToolUse hook
**So that** the hook is installed regardless of installation method

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN `remote-install.sh` runs install_claude() THE SYSTEM SHALL inject the same PostToolUse hook as the local installer -->
<!-- EARS: THE SYSTEM SHALL use $install_dir to determine settings file scope (same logic as local installer) -->

**Progress Checklist:**
- [ ] Hook injection mirrored in `scripts/remote-install.sh` `install_claude()` function
- [ ] Same python3 injection logic as local installer

### Requirement 3: Dogfood in SpecOps Repo
**As a** SpecOps contributor
**I want** the hook active in the SpecOps repo itself
**So that** the project dogfoods its own hook mechanism

**Acceptance Criteria (EARS):**
<!-- EARS: THE SYSTEM SHALL add the PostToolUse hook to .claude/settings.local.json in the SpecOps repo -->
<!-- EARS: THE SYSTEM SHALL merge the hook into the existing permissions object without overwriting other settings -->

**Progress Checklist:**
- [ ] Hook added to `.claude/settings.local.json`
- [ ] Existing settings preserved

### Requirement 4: Documentation Update
**As a** potential SpecOps user evaluating the tool
**I want** the comparison documentation updated to reflect agent hook support
**So that** the feature matrix accurately represents SpecOps capabilities

**Acceptance Criteria (EARS):**
<!-- EARS: WHEN viewing docs/COMPARISON.md THE SYSTEM SHALL show "Yes (ExitPlanMode)" in the Agent hooks row for SpecOps -->
<!-- EARS: THE SYSTEM SHALL update the Kiro comparison section to note SpecOps' 1 hook type vs Kiro's 10 -->

**Progress Checklist:**
- [ ] Feature matrix row updated (line 19)
- [ ] Kiro comparison text updated (line 47)

## Scope Boundary

**Ships in v1:**
- Hook injection in local installer (`install.sh`)
- Hook injection in remote installer (`remote-install.sh`)
- Dogfood in `.claude/settings.local.json`
- Documentation update in `docs/COMPARISON.md`

**Deferred:**
- [To be defined]

## Product Quality Attributes
- Hook must be idempotent (running installer twice produces no duplicate)
- Hook must be inert in non-SpecOps projects (`test -f .specops.json` guard)
- No new dependencies required
- Existing settings.json content must be preserved during injection
- ShellCheck must pass on modified shell scripts

## Constraints
- `# specops-hook` marker enables future uninstall tooling
- "protocol breach" language matches existing enforcement pattern
- Python3 injection reuses existing pattern from installer (lines 120-138)
- `.claude/settings.json` is gitignored by `.claude/*` pattern, so dogfood uses `.claude/settings.local.json`

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
