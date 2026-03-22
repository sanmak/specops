# Feature: From-Plan Enforcement Checklist Integration

## Overview

Add a post-conversion enforcement pass to from-plan mode so that specs created via plan conversion undergo the same 8 enforcement checks the dispatcher applies before Phase 3. Currently, from-plan generates spec artifacts (requirements.md, design.md, tasks.md, spec.json, implementation.md) but skips to "spec is ready" without verifying IssueID population, steering/memory directory existence, or Phase 1 Context Summary -- checks that the dispatcher's Pre-Phase-3 Enforcement Checklist would catch for normal specs.

## User Stories

### Story 1: Post-Conversion Enforcement Pass

**As a** developer using SpecOps from-plan mode
**I want** the converted spec to pass the same enforcement checks the dispatcher uses
**So that** the spec is fully ready for implementation without missing IssueIDs, steering directories, or context summaries

**Acceptance Criteria (EARS):**
<!-- Event-Driven: WHEN [event] THE SYSTEM SHALL [behavior] -->
<!-- Unwanted: IF [condition] THEN THE SYSTEM SHALL [response] -->
- WHEN from-plan mode completes spec artifact generation (step 5) THE SYSTEM SHALL run a post-conversion enforcement pass before notifying the user the spec is ready
- WHEN taskTracking is configured and High/Medium priority tasks exist THE SYSTEM SHALL verify all have valid IssueIDs and create external issues if missing
- WHEN the steering directory does not exist after conversion THE SYSTEM SHALL create it with foundation templates
- WHEN the memory directory does not exist after conversion THE SYSTEM SHALL create it
- WHEN implementation.md is missing the Phase 1 Context Summary THE SYSTEM SHALL write the context summary using from-plan conversion context
- IF any enforcement check fails and cannot be auto-remediated THEN THE SYSTEM SHALL notify the user with the specific failure and stop before declaring the spec ready

**Progress Checklist:**

- [x] Post-conversion enforcement pass added to core/from-plan.md between step 6 and step 7
- [x] IssueID population check integrated (respects taskTracking config)
- [x] Steering directory existence check with auto-creation
- [x] Memory directory existence check with auto-creation
- [x] Phase 1 Context Summary written to implementation.md
- [x] Enforcement failure stops spec completion with specific error message

### Story 2: Spec Dependency Gate for Converted Specs

**As a** developer converting a plan that targets a spec with dependencies
**I want** spec dependency checks to run on the converted spec
**So that** required upstream specs are verified complete before I start implementation

**Acceptance Criteria (EARS):**
<!-- Event-Driven: WHEN [event] THE SYSTEM SHALL [behavior] -->
- WHEN spec.json contains specDependencies with required entries THE SYSTEM SHALL verify each required dependency has status "completed"
- WHEN specDependencies is absent or empty THE SYSTEM SHALL pass this check trivially

**Progress Checklist:**

- [x] Spec dependency gate included in post-conversion enforcement
- [x] Required dependency status verification

### Story 3: Consistent Enforcement Between Spec and From-Plan Modes

**As a** SpecOps maintainer
**I want** from-plan and spec modes to share the same enforcement standard
**So that** specs created via either path have identical readiness guarantees

**Acceptance Criteria (EARS):**
<!-- Ubiquitous: THE SYSTEM SHALL [behavior] -->
- THE SYSTEM SHALL run all 8 checks from the dispatcher's Pre-Phase-3 Enforcement Checklist in the from-plan post-conversion pass
- THE SYSTEM SHALL use protocol breach language for skipping the enforcement pass

**Progress Checklist:**

- [x] All 8 dispatcher enforcement checks represented in from-plan
- [x] Protocol breach language in core/from-plan.md
- [x] Validator markers updated to verify enforcement presence in from-plan output

## Non-Functional Requirements

- Performance: Enforcement pass adds at most 8 file existence/read checks -- negligible overhead
- Maintainability: Enforcement checks reference the dispatcher's checklist by name so changes in one location are discoverable

## Constraints & Assumptions

- Core files must use abstract operations only (READ_FILE, WRITE_FILE, FILE_EXISTS, etc.)
- The enforcement pass is auto-remediation-first: create missing directories/files rather than just reporting failures
- IssueID creation follows the existing Task Tracking Integration protocol -- no new issue creation mechanism
- The from-plan mode does not run full Phase 1 (no steering file loading, no repo map, no memory loading) -- the enforcement pass only verifies structural prerequisites exist

## Dependencies & Blockers

### Spec Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| workflow-enforcement-gates | Established the 8-check enforcement pattern | No | Completed |
| plan-to-specops-automation | Created the current from-plan workflow | No | Completed |
| context-aware-dispatch | Moved enforcement to dispatcher | No | Completed |

### Cross-Spec Blockers

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| ------- | ------------- | --------------- | ----------------- | ------ |
| ---     | ---           | ---             | ---               | ---    |

## Success Metrics

- Specs created via from-plan pass the dispatcher's Pre-Phase-3 Enforcement Checklist without manual intervention
- No more missing IssueIDs when taskTracking is configured (the issue observed during production-learnings spec)

## Out of Scope

- Full Phase 1 execution within from-plan (steering file loading, repo map generation, memory loading) -- from-plan is a lightweight conversion, not a full workflow run
- Refactoring the 8 checks into a shared function callable by both dispatcher and from-plan -- this would require changes to the generator architecture beyond the scope of this fix
- Changes to the dispatcher's Pre-Phase-3 Enforcement Checklist itself

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
