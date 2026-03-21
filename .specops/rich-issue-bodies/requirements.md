# Feature: Rich Issue Bodies and Auto-Labels for External Task Tracking

## Overview

GitHub issues created by SpecOps are low quality — bare one-liners like "Create core/run-logging.md module" that lack the context needed for implementation or team coordination. The root cause: the Issue Creation Protocol references `<TaskDescription>` but never defines what it must contain, so agents serialize anything from a single sentence to a full task breakdown. This feature defines a mandatory Issue Body Composition template that pulls context from spec artifacts into every issue, and auto-applies GitHub labels for discoverability.

## Product Requirements

### Requirement 1: Issue Body Composition Template
**As a** developer reading a GitHub issue
**I want** the issue to contain the full context needed to understand and implement the task
**So that** I can work from the issue alone without reading the spec directory

**Acceptance Criteria (EARS):**
<!-- EARS patterns:
  Event-Driven:   WHEN [event] THE SYSTEM SHALL [behavior]
  Ubiquitous:     THE SYSTEM SHALL [behavior]
  Unwanted:       IF [unwanted condition] THEN THE SYSTEM SHALL [response]
-->
- WHEN creating an external issue for a High or Medium priority task THE SYSTEM SHALL compose the issue body using the Issue Body Composition template with sections: Context, Spec Artifacts, Description, Implementation Steps, Acceptance Criteria, Files to Modify, Tests Required (optional), and metadata footer
- WHEN composing the Context section THE SYSTEM SHALL extract 1-3 sentences from the requirements.md Overview (or bugfix.md Bug Description / refactor.md Motivation) explaining why the work exists
- WHEN composing the Spec Artifacts section THE SYSTEM SHALL include relative links to the spec's requirements, design, and tasks files
- IF a task section in tasks.md is empty or missing THEN THE SYSTEM SHALL write "None specified" in the corresponding issue body section rather than omitting it
- IF an agent writes a freeform description instead of following the Issue Body Composition template THEN THE SYSTEM SHALL treat this as a protocol breach

**Progress Checklist:**
- [x] Issue Body Composition template defined in core/config-handling.md
- [x] Template extracts context from requirements.md/bugfix.md/refactor.md
- [x] Protocol breach language enforces mandatory usage
- [x] Empty sections handled with "None specified"

### Requirement 2: GitHub Label Protocol
**As a** team member browsing GitHub issues
**I want** issues to have priority, spec, and type labels auto-applied
**So that** I can filter and find related issues without manual tagging

**Acceptance Criteria (EARS):**
- WHEN creating issues for a spec with `taskTracking: "github"` THE SYSTEM SHALL ensure labels exist by running `gh label create "<label>" --force` once per spec before the first issue
- WHEN creating a GitHub issue THE SYSTEM SHALL apply three labels: priority (`P-high` or `P-medium`), spec name (`spec:<spec-id>`), and type (`feat`, `fix`, or `refactor` — mapping `feature`→`feat`, `bugfix`→`fix`)
- IF label creation or application fails on Jira or Linear THEN THE SYSTEM SHALL skip labels silently without blocking issue creation

**Progress Checklist:**
- [x] GitHub Label Protocol defined in core/config-handling.md
- [x] Labels created idempotently with `--force` flag
- [x] Three label categories applied to every GitHub issue
- [x] Jira/Linear graceful degradation

### Requirement 3: Validation and CI Enforcement
**As a** SpecOps contributor
**I want** the validator to check that Issue Body Composition and GitHub Label Protocol instructions appear in all generated platform outputs
**So that** accidental removal of these instructions is caught in CI

**Acceptance Criteria (EARS):**
- WHEN running `generator/validate.py` THE SYSTEM SHALL check for ISSUE_BODY_MARKERS in all 4 platform outputs
- WHEN running cross-platform consistency checks THE SYSTEM SHALL include ISSUE_BODY_MARKERS in the marker concatenation
- WHEN running `tests/test_platform_consistency.py` THE SYSTEM SHALL verify issue_body markers are present across all platforms

**Progress Checklist:**
- [x] ISSUE_BODY_MARKERS constant added to validate.py
- [x] Per-platform validation includes issue-body markers
- [x] Cross-platform consistency check includes issue-body markers
- [x] test_platform_consistency.py updated

## Product Quality Attributes
- No new config options needed — Issue Body Composition uses existing spec artifacts
- No new dependencies — uses existing `gh` CLI already required for task tracking
- Backward compatible — only affects future issue creation, no retroactive changes

## Scope Boundary
- **Ships now**: Issue Body Composition template, GitHub Label Protocol, validator markers, cross-references in workflow.md and task-tracking.md
- **Deferred**: Retroactive update of existing closed issues, Jira/Linear label parity, issue body validation gate (checking content quality after creation)

## Constraints & Assumptions
- Assumes `requirements.md`/`bugfix.md`/`refactor.md` and `spec.json` are already generated when issue creation runs (true — Phase 2 step 6 runs after spec file generation)
- `gh label create --force` is idempotent — safe to run repeatedly

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
