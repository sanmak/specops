# Feature: Enforcement Roadmap — Advisory Context to Deterministic Enforcement

## Overview
Convert ~26 purely advisory behavioral mechanisms in SpecOps core modules into deterministic enforcement gates. Dogfooding across 6 specs produced 42 documented gaps proving advisory mechanisms fail repeatedly and consistently — LLMs treat advisory language ("Tip:", "consider", "should", "prefer") as optional and optimize for perceived user value over workflow compliance. File-persisted state machines, validate.py marker checks, and mandatory phase gate checklists have zero recurring gaps — this spec extends those proven patterns to the remaining weak points.

## Product Requirements

### Requirement 1: Spec Artifact Linting
**As a** SpecOps user
**I want** automated validation of spec artifacts (tasks.md, implementation.md)
**So that** checkbox staleness, missing documentation reviews, and invalid version metadata are caught deterministically rather than relying on agent compliance

**Acceptance Criteria (EARS):**
<!-- Ubiquitous: THE SYSTEM SHALL [behavior] -->
<!-- Event-Driven: WHEN [event] THE SYSTEM SHALL [behavior] -->
- WHEN a completed task in tasks.md has unchecked `- [ ]` items outside a Deferred Criteria subsection THE SYSTEM SHALL report a linting error
- WHEN a completed spec's implementation.md lacks a `## Documentation Review` section THE SYSTEM SHALL report a linting error
- WHEN a spec.json contains `specopsCreatedWith` or `specopsUpdatedWith` that does not match a valid semver pattern THE SYSTEM SHALL report a linting error
- WHEN the spec artifact linter runs against existing completed dogfood specs THE SYSTEM SHALL report zero errors (they are correctly completed)

**Progress Checklist:**
- [x] Checkbox staleness detection works
- [x] Documentation Review section detection works
- [x] Version extraction validation works
- [x] Existing dogfood specs pass cleanly

### Requirement 2: Phase 1 Context Summary Gate
**As a** SpecOps user
**I want** a mandatory Phase 1 Context Summary written to implementation.md before Phase 2 starts
**So that** the agent cannot skip steering file loading, repo map checks, or memory loading without it being visible in the persisted file

**Acceptance Criteria (EARS):**
- WHEN Phase 1 completes THE SYSTEM SHALL write a `## Phase 1 Context Summary` section to implementation.md recording config status, context recovery, steering files, repo map, memory, vertical, and affected files
- IF Phase 2 is entered without a Phase 1 Context Summary in implementation.md THEN THE SYSTEM SHALL treat this as a protocol breach

**Progress Checklist:**
- [x] Context Summary template added to implementation.md
- [x] Phase 2 gate references Context Summary

### Requirement 3: Phase 4 Documentation Gate
**As a** SpecOps user
**I want** a mandatory `## Documentation Review` section in implementation.md before spec completion
**So that** the agent cannot skip documentation checks when completing a spec

**Acceptance Criteria (EARS):**
- WHEN Phase 4 documentation check runs THE SYSTEM SHALL write a `## Documentation Review` section to implementation.md listing each doc checked and its status
- IF a spec is marked completed without a Documentation Review section in implementation.md THEN THE SYSTEM SHALL treat this as a linting error

**Progress Checklist:**
- [x] Documentation Review gate added to Phase 4 workflow
- [x] Linter validates Documentation Review section exists

### Requirement 4: Config-to-Workflow Binding
**As a** SpecOps user
**I want** every config value that affects agent behavior to have explicit "Workflow Impact" annotations and corresponding conditionals in the workflow
**So that** config flags like `taskTracking: "github"` are never dead features with zero workflow references

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL annotate each behavioral config value in config-handling.md with a "Workflow Impact" note identifying the workflow step(s) it affects
- WHEN `config.team.taskTracking` is not `"none"` THE SYSTEM SHALL have explicit conditionals in Phase 3 workflow for issue creation before task state transitions

**Progress Checklist:**
- [x] Workflow Impact annotations added to config-handling.md
- [x] Phase 3 conditionals reference taskTracking config

### Requirement 5: Cross-Section Coherence Check
**As a** SpecOps user
**I want** a coherence verification step at the end of Phase 2 that cross-checks NFRs against functional requirements
**So that** contradictions between spec sections are caught before implementation begins

**Acceptance Criteria (EARS):**
- WHEN Phase 2 spec generation completes THE SYSTEM SHALL perform a Coherence Verification step that cross-checks numeric constraints from NFRs against functional requirements
- WHEN the coherence check runs THE SYSTEM SHALL record the result in implementation.md
- THE SYSTEM SHALL include COHERENCE_MARKERS in the generator validator

**Progress Checklist:**
- [x] Coherence Verification step added to Phase 2
- [x] Result recorded in implementation.md
- [x] COHERENCE_MARKERS added to validate.py

### Requirement 6: Pre-Task Anchoring
**As a** SpecOps user
**I want** the agent to read acceptance criteria and write a "Task Scope" note to implementation.md before starting each task
**So that** scope drift is caught via pivot check against the anchored scope

**Acceptance Criteria (EARS):**
- WHEN a task transitions to In Progress THE SYSTEM SHALL read its acceptance criteria and relevant requirements, then write a Task Scope note to implementation.md
- WHEN a task transitions to Completed THE SYSTEM SHALL compare actual changes against the anchored Task Scope

**Progress Checklist:**
- [x] Pre-task anchoring step added to task-tracking.md
- [x] Post-task pivot check references anchored scope

### Requirement 7: Vertical Vocabulary Verification
**As a** SpecOps user
**I want** automatic verification that spec files use the correct vertical-specific vocabulary after Phase 2 generation
**So that** default terms are not left in specs when a vertical vocabulary is configured

**Acceptance Criteria (EARS):**
- WHEN Phase 2 generates spec files for a non-default vertical THE SYSTEM SHALL scan for prohibited default terms and replace with vertical-specific terms
- WHEN vocabulary verification runs THE SYSTEM SHALL record the result in the Context Summary

**Progress Checklist:**
- [x] Vocabulary verification step added to verticals.md
- [x] Result recorded in Context Summary

## Non-Functional Requirements
- All new enforcement gates must follow proven patterns: file-persisted state, validate.py markers, or mandatory phase gate checklists
- Advisory mechanisms that are judgment-based (simplicity principle, communication style, memory heuristics) remain advisory — no false enforcement
- Existing 9 completed dogfood specs must pass the new linter without errors

## Constraints & Assumptions
- Core files must use abstract operations from `core/tool-abstraction.md` only
- Generated platform outputs must be regenerated after each change to core modules
- New validate.py markers must be added to BOTH per-platform validation AND the cross-platform consistency check loop

## Success Metrics
- Zero recurring gaps for mechanisms converted from advisory to enforcement
- All existing tests continue to pass
- New linter catches checkbox staleness, missing docs review, and invalid versions

## Scope Boundary
**Ships in this spec:**
- Spec artifact linter (checkbox staleness, docs review, version validation)
- Phase 1 Context Summary gate
- Phase 4 Documentation Review gate
- Config-to-Workflow binding annotations
- Cross-Section Coherence Check with COHERENCE_MARKERS
- Pre-Task Anchoring in task-tracking.md
- Vertical Vocabulary Verification step

**Deferred:**
- Automated regression testing of enforcement gates (covered by manual test spec verification)
- Runtime enforcement of Phase 1 Context Summary (relies on workflow instruction, not file-system gate)
- Spec artifact drift on pivot detection (v2 backlog — needs Phase 3 pivot detection beyond current pivot check)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
