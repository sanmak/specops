# Feature: Context-Aware Dispatch

## Overview
The SpecOps SKILL.md is 4,596 lines loaded into every invocation, but only 5% (220 lines) is needed for routing. Under context pressure, enforcement gates get dropped — GitHub issue creation was skipped twice despite being a documented protocol breach. This feature decomposes the monolithic skill into a lightweight dispatcher (~350 lines) that spawns focused sub-agents with only the mode-specific instructions needed, reducing context load by 42-88% per invocation.

## Product Requirements

### Requirement 1: Dispatcher SKILL.md for Claude
**As a** SpecOps user on Claude Code
**I want** the skill to load only routing + enforcement logic (~350 lines) instead of the full 4,596 lines
**So that** enforcement gates are reliably executed under reduced context pressure

**Acceptance Criteria (EARS):**
- WHEN `/specops` is invoked on Claude Code THE SYSTEM SHALL load a dispatcher SKILL.md containing only version extraction, config loading, safety rules, enforcement gates, and mode routing (~350 lines)
- WHEN a mode is detected THE SYSTEM SHALL read the corresponding mode file from `modes/` and spawn a sub-agent with that content
- THE SYSTEM SHALL prepend a shared context block (safety rules, loaded config, version) to every sub-agent prompt

**Progress Checklist:**
- [x] Dispatcher SKILL.md generated at ~350 lines
- [x] Mode files generated in `platforms/claude/modes/`
- [x] Sub-agent dispatch protocol works end-to-end

### Requirement 2: Pre-Phase-3 Enforcement Checklist
**As a** SpecOps user
**I want** a deterministic 7-point checklist that runs in the dispatcher before Phase 3 is dispatched
**So that** enforcement gates (like task tracking IssueID population) cannot be skipped

**Acceptance Criteria (EARS):**
- WHEN Phase 3 dispatch is requested THE SYSTEM SHALL run 7 deterministic file-based checks: spec.json status, implementation.md context summary, tasks.md existence, design.md existence, IssueID population (if taskTracking configured), steering directory, memory directory
- IF any check fails THEN THE SYSTEM SHALL display the specific failure and STOP — Phase 3 sub-agent is not spawned

**Progress Checklist:**
- [x] Pre-Phase-3 checklist in dispatcher with 7 checks
- [x] IssueID check (#5) validates High/Medium priority tasks

### Requirement 3: Generator Split Output
**As a** SpecOps contributor
**I want** the generator to produce dispatcher + per-mode files for Claude while keeping monolithic output for other platforms
**So that** the 3-layer architecture is preserved and other platforms are unaffected

**Acceptance Criteria (EARS):**
- WHEN `python3 generator/generate.py --all` runs THE SYSTEM SHALL produce both `platforms/claude/SKILL.md` (dispatcher) and `platforms/claude/modes/*.md` (13 mode files)
- WHEN generating for Cursor, Codex, or Copilot THE SYSTEM SHALL produce monolithic output unchanged
- THE SYSTEM SHALL apply tool substitution to all mode files identically to the current monolithic output

**Progress Checklist:**
- [x] Generator produces dispatcher + 13 mode files for Claude
- [x] Other 3 platforms produce identical monolithic output
- [x] Tool substitution applied to all mode files

### Requirement 4: Validator Support for Split Files
**As a** SpecOps contributor
**I want** `validate.py` to check markers across Claude's dispatcher + mode files
**So that** CI catches missing content regardless of the split architecture

**Acceptance Criteria (EARS):**
- WHEN `validate.py` validates Claude THE SYSTEM SHALL check markers across the union of dispatcher + all mode files
- WHEN checking cross-platform consistency THE SYSTEM SHALL verify Claude's split files collectively contain the same markers as other platforms' monolithic files

**Progress Checklist:**
- [x] Validator checks Claude markers across all files (union)
- [x] Cross-platform consistency check updated

### Requirement 5: /pre-pr IssueID Verification
**As a** SpecOps contributor
**I want** `/pre-pr` to verify IssueID population when taskTracking is configured
**So that** missing issue creation is caught before opening a PR

**Acceptance Criteria (EARS):**
- WHEN `/pre-pr` runs AND `taskTracking` is not "none" THE SYSTEM SHALL scan implementing/completed specs for High/Medium priority tasks with `IssueID: None`
- WHEN missing IssueIDs are found THE SYSTEM SHALL report them as a FAIL in the dashboard

**Progress Checklist:**
- [x] Step 2e added to pre-pr.md
- [x] IssueID Check row in dashboard

### Requirement 6: Installation Support for Mode Files
**As a** SpecOps user installing via setup.sh or remote-install.sh
**I want** the `modes/` directory copied alongside SKILL.md during installation
**So that** the dispatcher can read mode files after installation

**Acceptance Criteria (EARS):**
- WHEN `install.sh` runs for Claude THE SYSTEM SHALL copy the `modes/` directory alongside SKILL.md
- WHEN `remote-install.sh` runs for Claude THE SYSTEM SHALL copy the `modes/` directory

**Progress Checklist:**
- [x] `platforms/claude/install.sh` copies modes/
- [x] `scripts/remote-install.sh` copies modes/

### Requirement 7: README Documentation
**As a** potential SpecOps user evaluating the tool
**I want** the context-aware dispatch architecture documented in the README
**So that** I understand this differentiator when comparing SpecOps to alternatives

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include a "Context-Aware Dispatch" section in README.md after the Architecture section
- THE SYSTEM SHALL add a "Context-aware dispatch" row to the comparison table
- THE SYSTEM SHALL add a bullet to "Why SpecOps" highlighting the context reduction benefit

**Progress Checklist:**
- [x] README section added
- [x] Comparison table row added
- [x] "Why SpecOps" bullet added

## Scope Boundary

**Ships in v1:**
- Dispatcher + mode files for Claude
- Pre-Phase-3 enforcement checklist
- Generator split output
- Validator updates
- /pre-pr IssueID check
- Installation support
- README documentation

**Deferred:**
- Sub-agent dispatch for other platforms (they lack canDelegateTask)
- Lazy-loading mode files from remote URLs
- Configurable mode groupings via .specops.json
- Post-dispatch verification for all 18 enforcement gates (start with the top 7)

## Product Quality Attributes
- Dispatcher SKILL.md must be under 400 lines
- Mode files must collectively contain all content from the current monolithic output
- No new Python dependencies
- Pre-commit hook must remain under 5 seconds
- Other platforms' output must be byte-identical before and after this change

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
