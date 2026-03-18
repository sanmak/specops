# Feature: Workflow Enforcement Gates

## Overview
Convert three weak workflow points — Phase 1 steering/memory setup, Phase 4 memory write, and Phase 3 task tracking gate — into enforcement gates with "protocol breach" consequences. Real-world usage in the ship-kit project revealed that agents skip non-mandatory steps, causing steering files to never be created, memory writes to be skipped, and taskTracking config to be ignored entirely.

## Product Requirements

### Requirement 1: Phase 1 Pre-flight Enforcement
**As a** SpecOps user
**I want** Phase 1 to enforce steering and memory setup with protocol breach consequences
**So that** agents cannot skip infrastructure creation and proceed to spec generation without project context

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven pattern -->
- WHEN the agent reaches Phase 1 step 5 THE SYSTEM SHALL verify that `<specsDir>/steering/` exists AND contains at least one `.md` file
- WHEN the agent reaches Phase 1 step 5 THE SYSTEM SHALL verify that `<specsDir>/memory/` exists
- IF any pre-flight check fails after corrective action THEN THE SYSTEM SHALL STOP and not proceed to Phase 2
<!-- EARS: Ubiquitous pattern -->
- THE SYSTEM SHALL label proceeding past Phase 1 without completing the pre-flight gate as a "protocol breach"

**Progress Checklist:**
- [x] Pre-flight check includes "protocol breach" language
- [x] Content-level check added (LIST_DIR for at least one .md file)
- [x] STOP consequence added after corrective action failure
- [x] .gitignore check visually separated from enforcement bullets

### Requirement 2: Phase 4 Memory Write Enforcement
**As a** SpecOps user
**I want** Phase 4 memory write to be labeled as mandatory with protocol breach consequences
**So that** agents cannot skip memory updates, which breaks cross-spec learning

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL label Phase 4 step 3 (memory update) as "(mandatory)" in the heading
- THE SYSTEM SHALL state that skipping memory update is a "protocol breach"
- THE SYSTEM SHALL include a forward reference to step 5's completion gate verification

**Progress Checklist:**
- [x] Step 3 heading includes "(mandatory)"
- [x] "protocol breach" language added to step 3
- [x] Forward reference to step 5 verification included

### Requirement 3: Phase 3 Task Tracking Gate Enforcement
**As a** SpecOps user with `taskTracking` configured
**I want** the task tracking gate to enforce attempted issue creation with protocol breach consequences
**So that** agents cannot silently skip external issue creation when the config says to use it

**Acceptance Criteria (EARS):**
- WHEN `config.team.taskTracking` is not `"none"` THE SYSTEM SHALL attempt external issue creation for all High/Medium priority tasks before implementation begins
- IF the agent never attempts issue creation when taskTracking is configured THEN THE SYSTEM SHALL classify this as a "protocol breach"
- WHEN issue creation fails for individual tasks (CLI error) THE SYSTEM SHALL apply Graceful Degradation rules and proceed
- WHEN issue creation fails for ALL tasks THE SYSTEM SHALL notify the user and proceed with internal tracking only
<!-- EARS: Ubiquitous pattern -->
- THE SYSTEM SHALL distinguish between "agent didn't try" (protocol breach) and "CLI tool failed" (graceful degradation)

**Progress Checklist:**
- [x] "advisory, not blocking" language removed from config-handling.md
- [x] "protocol breach" language added for skipping the gate
- [x] Partial success and total failure scenarios specified separately
- [x] "attempted creation" enforcement principle documented
- [x] Phase 3 step 1 restructured as sub-list with named gates

### Requirement 4: Validation Marker Propagation
**As a** SpecOps maintainer
**I want** the new enforcement language to be verified in generated platform outputs
**So that** all platforms receive the enforcement gates consistently

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include "attempted creation" in the EXTERNAL_TRACKING_MARKERS validation list
- THE SYSTEM SHALL include "attempted creation" in the test_platform_consistency.py REQUIRED_MARKERS
- WHEN platform outputs are regenerated THE SYSTEM SHALL pass validation with the new marker

**Progress Checklist:**
- [x] Marker added to generator/validate.py
- [x] Marker mirrored in tests/test_platform_consistency.py
- [x] All tests pass after regeneration

## Constraints & Assumptions
- core/ files must use abstract operations only (READ_FILE, WRITE_FILE, etc.)
- No step renumbering — preserve existing Phase 1-4 structure
- No schema changes to .specops.json
- Generated platform outputs must be regenerated and committed

## Scope Boundary
**Ships in this spec:**
- Enforcement language changes in core/workflow.md and core/config-handling.md
- Validation marker updates
- Regenerated platform outputs

**Deferred:**
- Checkbox staleness validation tooling (systemic issue, separate spec)
- Phase 3 pivot detection (systemic issue, separate spec)
- Full spec fidelity layer (broader initiative)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
