# Feature: Workflow Automation Suite

## Overview
SpecOps captures what happened (metrics) and what was decided (memory), but not how work progressed (no execution trace), whether spec references are accurate before implementation (no pre-implementation validation), how to recover from mid-workflow failures (no phase-boundary snapshots), or how to run iterative implement-verify cycles without manual intervention (no automated pipeline). These four gaps reduce auditability, waste implementation effort on bad references, complicate rollback, and require developer babysitting for multi-cycle specs.

## Product Requirements

### Requirement 1: Run Logging
**As a** developer reviewing a completed or failed spec
**I want** a timestamped execution trace of every phase, step, decision, and error during the workflow
**So that** I can audit how the spec was executed, debug failures, and understand why specific decisions were made

**Acceptance Criteria (EARS):**
- WHEN a SpecOps workflow starts THE SYSTEM SHALL create a log file at `<specsDir>/runs/<spec-name>-<timestamp>.log.md` with YAML frontmatter
- WHEN a phase transition occurs THE SYSTEM SHALL append a timestamped `## Phase N: <name>` entry to the run log
- WHEN a task completes or blocks THE SYSTEM SHALL append the task outcome to the run log
- WHEN the workflow completes THE SYSTEM SHALL update the run log frontmatter with `completedAt` and `finalStatus`
- WHERE `config.implementation.runLogging` is `"off"` THE SYSTEM SHALL skip all run log operations

**Progress Checklist:**
- [x] Run log file created at workflow start
- [x] Phase transitions logged with timestamps
- [x] Task outcomes logged (complete/blocked)
- [x] Run log finalized at workflow end
- [x] Config gating works (on/off)

### Requirement 2: Code-Grounded Plan Validation
**As a** developer about to implement a spec
**I want** file paths and code references in design.md and tasks.md validated against the actual codebase
**So that** I avoid wasting implementation effort on specs with wrong file paths, renamed functions, or non-existent modules

**Acceptance Criteria (EARS):**
- WHEN Phase 2 generates spec files AND `config.implementation.validateReferences` is not `"off"` THE SYSTEM SHALL extract file paths from "Files to Modify" sections and validate each against the repo map and FILE_EXISTS
- WHEN a referenced file path does not exist AND the task does not describe creating that file THE SYSTEM SHALL flag it as unresolved
- WHERE `validateReferences` is `"warn"` THE SYSTEM SHALL notify the user of unresolved references and continue
- WHERE `validateReferences` is `"strict"` THE SYSTEM SHALL block implementation until the user confirms proceeding
- IF a file path contains `../` traversal THEN THE SYSTEM SHALL reject it as an invalid reference

**Progress Checklist:**
- [x] File paths extracted from tasks.md and design.md
- [x] Paths validated against repo map and FILE_EXISTS
- [x] New-file detection heuristic works
- [x] Warn mode notifies but continues
- [x] Strict mode blocks with user prompt
- [x] Results recorded in implementation.md

### Requirement 3: Git Checkpointing
**As a** developer implementing a spec
**I want** automatic git commits at phase boundaries (spec-created, implemented, completed)
**So that** I can roll back to semantic milestones if something goes wrong, without mixing unrelated changes

**Acceptance Criteria (EARS):**
- WHERE `config.implementation.gitCheckpointing` is true AND the working tree is clean THE SYSTEM SHALL commit spec artifacts after Phase 2 with message `specops(checkpoint): spec-created -- <spec-name>`
- WHERE `config.implementation.gitCheckpointing` is true THE SYSTEM SHALL commit all changes after Phase 3 with message `specops(checkpoint): implemented -- <spec-name>`
- WHERE `config.implementation.gitCheckpointing` is true THE SYSTEM SHALL commit final metadata after Phase 4 with message `specops(checkpoint): completed -- <spec-name>`
- IF the working tree has uncommitted changes at Phase 1 THEN THE SYSTEM SHALL disable checkpointing for the run and notify the user
- IF a git commit fails THEN THE SYSTEM SHALL notify the user and continue without blocking the workflow

**Progress Checklist:**
- [x] Dirty tree detection at Phase 1
- [x] Phase 2 checkpoint (spec-created)
- [x] Phase 3 checkpoint (implemented)
- [x] Phase 4 checkpoint (completed)
- [x] Non-blocking on git failures
- [x] No conflict with autoCommit

### Requirement 4: Automated Pipeline Mode
**As a** developer with a completed spec
**I want** to run `/specops pipeline <spec-name>` to automatically cycle through implement-verify-fix loops
**So that** I can start a complex spec and come back to a finished implementation without manual babysitting

**Acceptance Criteria (EARS):**
- WHEN the user invokes `pipeline <spec-name>` THE SYSTEM SHALL validate the spec exists and has a compatible status
- WHEN a pipeline cycle completes THE SYSTEM SHALL check acceptance criteria and either finalize or start the next cycle
- WHILE the cycle count is below `config.implementation.pipelineMaxCycles` AND criteria remain unmet THE SYSTEM SHALL start a new implementation cycle
- IF all acceptance criteria pass THE SYSTEM SHALL finalize the spec (Phase 4 steps 2-8) and stop
- IF the maximum cycle count is reached THE SYSTEM SHALL stop and notify the user of unmet criteria
- IF a cycle makes zero progress (same criteria unmet as previous cycle) THEN THE SYSTEM SHALL stop early to prevent infinite loops

**Progress Checklist:**
- [x] Pipeline mode detection in Getting Started
- [x] Spec existence and status validation
- [x] Implement-verify cycle loop
- [x] Early stop on all criteria passing
- [x] Max cycle enforcement
- [x] Zero-progress detection
- [x] Integration with run logging, checkpointing, and delegation

## Product Quality Attributes
- **Reliability**: All 4 features are non-blocking — failures in logging, checkpointing, or validation never prevent spec completion
- **Performance**: Run logging adds minimal overhead (append-only file writes)
- **Backward compatibility**: All new config options have sensible defaults; existing `.specops.json` files remain valid without changes

## Scope Boundary
**Ships in this spec:**
- 4 new `core/*.md` modules
- Schema config for each feature
- Validation markers for each feature
- Generator integration (build_common_context + j2 templates)
- Platform consistency tests

**Deferred:**
- Per-cycle git checkpoints in pipeline mode (only phase-boundary for now)
- Run log viewer subcommand (`/specops runs`)
- Pipeline mode stop/resume between sessions
- Configurable run log retention/cleanup

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
