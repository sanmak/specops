# Feature: Bugfix Regression Risk Analysis

## Overview

Add a structured regression analysis discovery methodology to the SpecOps bugfix template. Currently, the bugfix template provides a format for documenting preserved behaviors (`SHALL CONTINUE TO` notation from Spec 1) but no systematic method for agents to discover which behaviors need protecting. This feature adds a Regression Risk Analysis section with severity-scaled discovery steps, enhanced workflow guidance, and validation markers.

## Product Requirements

### Requirement 1: Regression Risk Analysis Template Section
**As a** developer using SpecOps for bugfixes
**I want** a structured section that guides me through discovering regression risks
**So that** I systematically identify which behaviors to protect before writing the fix

**Acceptance Criteria (EARS):**
<!-- Use the EARS pattern that best fits each criterion:
  Ubiquitous:     THE SYSTEM SHALL [behavior]
  Event-Driven:   WHEN [event] THE SYSTEM SHALL [behavior]
  State-Driven:   WHILE [state] THE SYSTEM SHALL [behavior]
  Optional:       WHERE [feature is enabled] THE SYSTEM SHALL [behavior]
  Unwanted:       IF [unwanted condition] THEN THE SYSTEM SHALL [response]
-->
- WHEN a bugfix spec is created THE SYSTEM SHALL include a Regression Risk Analysis section with subsections for Blast Radius, Behavior Inventory, Test Coverage Assessment, Risk Tier, and Scope Escalation Check
- THE SYSTEM SHALL place the Regression Risk Analysis section between Reproduction Steps and Proposed Fix so that analysis occurs before fix design

**Progress Checklist:**
- [x] Regression Risk Analysis section added to bugfix template
- [x] Section positioned between Reproduction Steps and Proposed Fix

### Requirement 2: Severity-Scaled Analysis Depth
**As a** developer fixing a low-severity bug
**I want** the regression analysis to be proportional to the bug's severity
**So that** trivial fixes don't require exhaustive analysis

**Acceptance Criteria (EARS):**
- WHEN a bug has Critical or High severity THE SYSTEM SHALL require all five analysis subsections (Blast Radius, Behavior Inventory, Test Coverage Assessment, Risk Tier, Scope Escalation Check)
- WHEN a bug has Medium severity THE SYSTEM SHALL require Blast Radius, Behavior Inventory, and a brief Risk Tier
- WHEN a bug has Low severity THE SYSTEM SHALL require only a brief Blast Radius scan

**Progress Checklist:**
- [x] Severity scaling documented in template HTML comments
- [x] Severity-tiered guidance added to Phase 2 workflow

### Requirement 3: Discovery Workflow Guidance
**As an** AI coding agent following the SpecOps workflow
**I want** concrete steps using abstract operations to discover regression risks
**So that** I know exactly what to read, search, and analyze

**Acceptance Criteria (EARS):**
- WHEN Phase 2 processes a bugfix spec THE SYSTEM SHALL provide step-by-step discovery instructions using abstract operations (LIST_DIR, READ_FILE, RUN_COMMAND)
- THE SYSTEM SHALL instruct agents to complete regression analysis BEFORE writing the Proposed Fix
- WHEN the blast radius reveals scope beyond a bugfix THE SYSTEM SHALL provide explicit criteria for escalating to a Feature Spec

**Progress Checklist:**
- [x] Phase 2 bugfix guidance enhanced with discovery procedure
- [x] Abstract operations used throughout (no platform-specific tool names)
- [x] Scope escalation criteria defined

### Requirement 4: Validation of Regression Analysis in Generated Outputs
**As a** SpecOps maintainer
**I want** the validator to check that regression analysis content survives platform generation
**So that** all platforms include the complete bugfix methodology

**Acceptance Criteria (EARS):**
- WHEN platform outputs are validated THE SYSTEM SHALL check for regression analysis markers (section headings and key terms)
- WHEN any regression marker is missing from a platform output THE SYSTEM SHALL report a validation failure

**Progress Checklist:**
- [x] REGRESSION_MARKERS list added to validate.py
- [x] Markers checked in validate_platform()
- [x] Markers included in cross-platform consistency check

## Unchanged Behavior
<!-- These behaviors from Spec 1 MUST be preserved — the regression analysis adds to but does not replace existing bugfix template content. -->
- WHEN a bugfix spec is created THE SYSTEM SHALL CONTINUE TO include the Unchanged Behavior section with SHALL CONTINUE TO EARS notation
- WHEN a bugfix spec is created THE SYSTEM SHALL CONTINUE TO include the three-category Testing Plan (Current Behavior, Expected Behavior, Unchanged Behavior)
- WHEN a bugfix spec is created THE SYSTEM SHALL CONTINUE TO include the Acceptance Criteria checkboxes for bug reproduction, fix verification, and regression testing
- WHEN platform outputs are validated THE SYSTEM SHALL CONTINUE TO check for the existing TEMPLATE_MARKERS including "Bug Fix: [Title]"

## Scope Boundary
**Ships in this spec:**
- Regression Risk Analysis section in bugfix template
- Severity-scaled analysis guidance in Phase 2 workflow
- Validation markers in validate.py
- Regenerated platform outputs

**Deferred:**
- Automated regression test generation from analysis
- Regression analysis for refactor templates
- Machine-readable risk tier output (e.g., JSON)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
