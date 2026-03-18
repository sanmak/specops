# Feature: Plan Mode → SpecOps Workflow Automation

## Overview
Automate the transition from Claude Code's plan mode to the SpecOps workflow so that plan acceptance in SpecOps-configured projects routes through structured spec creation (from-plan) before implementation begins. This eliminates ad-hoc implementation of planned features.

## Product Requirements

### Requirement 1: Plan File Input for From-Plan Mode
**As a** developer using SpecOps
**I want** from-plan mode to accept a plan file path directly
**So that** I can convert existing plan files without manually pasting content

**Acceptance Criteria (EARS):**
<!-- Event-Driven: WHEN [event] THE SYSTEM SHALL [behavior] -->
- WHEN a file path is provided with "from-plan" invocation THE SYSTEM SHALL validate the path (no `../`, must be `.md`, must exist) and read the file content
- WHEN no content or path is provided and the platform has `planFileDirectory` configured THE SYSTEM SHALL auto-discover recent plan files and present them to the user
- IF the provided path contains traversal sequences (`../`) THEN THE SYSTEM SHALL reject the path and notify the user

**Progress Checklist:**
- [x] File path input branch added to from-plan step 1
- [x] Path validation (no `../`, `.md` extension, existence check)
- [x] Auto-discovery branch using platform `planFileDirectory`

### Requirement 2: Post-Plan-Acceptance Enforcement Gate
**As a** developer using SpecOps
**I want** plan acceptance to automatically route through from-plan mode
**So that** planned features always get proper spec artifacts before implementation

**Acceptance Criteria (EARS):**
- WHEN the user's request is a short acceptance phrase AND the conversation contains a structured plan AND `.specops.json` exists THE SYSTEM SHALL route through From Plan Mode
- WHEN a plan acceptance is detected in a SpecOps-configured project THE SYSTEM SHALL treat ad-hoc implementation without spec conversion as a protocol breach

**Progress Checklist:**
- [x] Step 10.5 added to workflow.md Getting Started
- [x] Protocol breach language for skipping from-plan
- [x] Detection patterns for acceptance phrases

### Requirement 3: Resume-Plan SpecOps Handoff
**As a** developer using Claude Code's `/resume-plan` command
**I want** the command to automatically invoke SpecOps from-plan after presenting a plan
**So that** plan-to-spec conversion happens seamlessly without a separate manual step

**Acceptance Criteria (EARS):**
- WHEN `/resume-plan` presents a plan and `.specops.json` exists in the project THE SYSTEM SHALL invoke SpecOps from-plan with the plan content
- WHEN `/resume-plan` presents a plan and no `.specops.json` exists THE SYSTEM SHALL report "No SpecOps configuration found" and proceed with direct implementation

**Progress Checklist:**
- [x] Step 8 added to resume-plan.md
- [x] SpecOps detection via .specops.json existence check
- [x] Plan content passed to from-plan workflow

### Requirement 4: Platform Plan File Directory Config
**As a** platform adapter for Claude Code
**I want** a `planFileDirectory` field in platform.json
**So that** from-plan auto-discovery knows where Claude Code stores plan files without hardcoding

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include a `planFileDirectory` field in Claude's platform.json pointing to `~/.claude/plans`
- WHEN a platform does not have `planFileDirectory` configured THE SYSTEM SHALL skip auto-discovery and fall back to asking the user

**Progress Checklist:**
- [x] `planFileDirectory` added to platforms/claude/platform.json
- [x] Other platforms unaffected (no field = skip auto-discovery)

## Constraints
- Core files (`core/*.md`) must use abstract operations only — no platform-specific tool names
- Universal enforcement — no `.specops.json` config flag for opt-in/opt-out
- Protocol breach language for enforcement (per prior feedback: advisory steps get skipped)
- Must work within Claude Code's existing architecture (no custom runtime hooks exist for plan mode exit)

## Scope Boundary
**Ships in this spec:**
- Enhanced `core/from-plan.md` with file path + auto-discovery
- Post-plan-acceptance gate in `core/workflow.md`
- SpecOps handoff step in `.claude/commands/resume-plan.md`
- `planFileDirectory` in `platforms/claude/platform.json`
- Regenerated platform outputs + validation

**Deferred:**
- Plan mode exit hooks (not available in Claude Code architecture)
- Cross-platform plan file directory support (only Claude has `~/.claude/plans/`)
- Automated plan content extraction from conversation context (relies on behavioral detection)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
