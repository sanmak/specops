# Feature: Proxy Metrics Tracking

## Overview
Token consumption is a real adoption barrier for SpecOps — companies cannot measure ROI without usage data. Since no supported platform exposes token-counting APIs to custom instructions, SpecOps captures deterministic proxy metrics at Phase 4 completion that correlate with productivity and resource usage.

## Product Requirements

### Requirement 1: Metrics Capture at Completion
**As a** developer using SpecOps
**I want** productivity metrics automatically captured when a spec completes
**So that** I can measure ROI and track resource usage patterns across specs

**Acceptance Criteria (EARS):**
- WHEN a spec transitions to `completed` status THE SYSTEM SHALL capture proxy metrics (artifact token estimates, code change stats, task counts, duration) and write them to `spec.json`
- IF any metric collection substep fails THEN THE SYSTEM SHALL set that metric to 0 and continue without blocking completion
- THE SYSTEM SHALL work identically across all 4 platforms (Claude Code, Cursor, Codex, Copilot)

**Progress Checklist:**
- [x] Metrics captured at Phase 4 completion
- [x] Failure in one metric does not block others
- [x] Works on all 4 platforms

### Requirement 2: Schema Validation
**As a** developer
**I want** the metrics object validated by the spec-schema.json
**So that** metrics data is consistent and trustworthy across all specs

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL validate the `metrics` object in `spec.json` against `spec-schema.json`
- WHEN a `spec.json` does not contain a `metrics` field THE SYSTEM SHALL still validate successfully (backward compatibility)
- IF the `metrics` object contains unknown properties THEN THE SYSTEM SHALL reject validation

**Progress Checklist:**
- [x] metrics schema added to spec-schema.json
- [x] Existing specs without metrics still validate
- [x] Extra properties rejected

### Requirement 3: Documentation
**As a** prospective SpecOps adopter
**I want** published documentation about token usage patterns and metrics
**So that** I can evaluate SpecOps ROI before adopting it

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include a dedicated `docs/TOKEN-USAGE.md` with metric definitions, benchmark data, and ROI guidance
- THE SYSTEM SHALL mention proxy metrics in `README.md` with a link to the detailed doc
- THE SYSTEM SHALL document the `metrics` object in `docs/REFERENCE.md`

**Progress Checklist:**
- [x] docs/TOKEN-USAGE.md created
- [x] README.md updated
- [x] docs/REFERENCE.md updated

## Scope Boundary
**Ships in v1:**
- 7 proxy metrics in spec.json (specArtifactTokensEstimate, filesChanged, linesAdded, linesRemoved, tasksCompleted, acceptanceCriteriaVerified, specDurationMinutes)
- Core module, workflow integration, generator pipeline, validation
- Documentation with benchmark examples

**Deferred:**
- Actual platform token counting (requires platform API support)
- User-reported manual token input fields
- Aggregated cross-spec analytics dashboard
- Cost estimation configuration in .specops.json

## Product Quality Attributes
- Backward compatible: existing specs without metrics remain valid
- Deterministic: same spec state produces same metrics
- Platform-agnostic: all 4 platforms produce identical metrics

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
