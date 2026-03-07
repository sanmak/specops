# Feature: EARS Notation for Requirements

## Overview

Add support for EARS (Easy Approach to Requirements Syntax) notation to SpecOps requirements templates. EARS produces structured, testable, traceable requirements using the format `WHEN [condition/event] THE SYSTEM SHALL [expected behavior]`. This replaces or augments the current checkbox-based acceptance criteria with precise, verifiable statements that map directly to test cases.

## Product Requirements

### Requirement 1: EARS-Formatted Acceptance Criteria in Feature Specs
**As a** developer using SpecOps
**I want** acceptance criteria written in EARS notation
**So that** requirements are unambiguous, testable, and directly traceable to implementation

**Acceptance Criteria:**
- [x] Feature requirements template includes EARS notation section with `WHEN [condition] THE SYSTEM SHALL [behavior]` format
- [x] EARS criteria appear alongside or replace existing checkbox criteria
- [x] Agent generates EARS-formatted criteria automatically during Phase 2
- [x] Generated criteria are specific enough to derive test cases from

### Requirement 2: Regression Protection in Bugfix Specs (`SHALL CONTINUE TO`)
**As a** developer fixing bugs with SpecOps
**I want** bugfix specs to explicitly capture unchanged behavior using `SHALL CONTINUE TO` notation
**So that** regressions are prevented by making preserved behavior explicit and testable

**Acceptance Criteria:**
- [x] Bugfix template includes "Unchanged Behavior" section
- [x] Unchanged behaviors use `WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior]` format
- [x] Testing plan is structured into three categories: Current Behavior, Expected Behavior, Unchanged Behavior
- [x] Agent is instructed to identify and document all affected behaviors, not just the broken one

### Requirement 3: Workflow Integration
**As a** developer using SpecOps
**I want** the workflow to instruct agents to produce EARS criteria during spec generation
**So that** EARS notation is consistently used across all specs without manual intervention

**Acceptance Criteria:**
- [x] `core/workflow.md` Phase 2 includes EARS generation instructions
- [x] Agents understand the five EARS patterns: Ubiquitous, Event-Driven, State-Driven, Optional Feature, Unwanted Behavior
- [x] Agent selects appropriate EARS pattern based on requirement type
- [x] Generated platform outputs include EARS instructions for all 4 platforms

### Requirement 4: Builder Vertical Adaptation
**As a** developer building products with SpecOps (builder vertical)
**I want** EARS notation adapted for product requirements
**So that** product-focused requirements remain outcome-oriented while gaining EARS precision

**Acceptance Criteria:**
- [x] Builder vertical maps EARS to product outcomes via existing vertical renaming rules (agents contextually adapt "THE SYSTEM SHALL" to product language)

**Deferred Criteria:**
- Product Quality Attributes use EARS for measurable criteria *(deferred — template uses generic format; vertical-specific EARS adaptation is a future enhancement)*
- Scope Boundary items are expressed as deferral statements *(deferred — scope boundary is prose, not EARS-formatted; would add ceremony without value)*

## Product Quality Attributes
- **Backward Compatibility**: Existing specs without EARS remain valid and functional
- **Simplicity**: EARS adds precision without adding ceremony — small features should have 2-3 EARS statements, not 20
- **Platform Parity**: All 4 platform outputs (Claude, Cursor, Codex, Copilot) include identical EARS guidance

## Scope Boundary
**Ships in v1 (this spec):**
- EARS notation in feature requirements template
- `SHALL CONTINUE TO` in bugfix template
- Workflow Phase 2 instructions for EARS generation
- All 5 EARS patterns documented for agents
- Platform output regeneration

**Deferred:**
- Automated test generation from EARS statements
- EARS validation/linting (checking that EARS statements are well-formed)
- EARS-specific review workflow (reviewing EARS criteria quality)
- Refactor template EARS adaptation (refactors don't need behavioral requirements)

## Constraints & Assumptions
- `core/` files must remain platform-agnostic (use abstract operations only)
- Templates are the source of truth; platform outputs are generated
- EARS is additive — it enhances existing templates, doesn't break them

## Success Metrics
- All 4 platform outputs include EARS notation guidance after regeneration
- `python3 generator/validate.py` passes with no new failures
- All existing tests continue to pass
- Generated specs produce EARS-formatted acceptance criteria

## Team Conventions
`.specops.json` at the project root defines SpecOps configuration (builder vertical).
