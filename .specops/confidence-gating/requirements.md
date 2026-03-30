# Confidence Gating on Evaluation Findings

## Overview

The adversarial evaluation system currently treats all findings with equal weight. The "mandatory finding per dimension" rule incentivizes generic filler findings to meet the quota. This creates noise that erodes developer trust -- when 2 of 4 findings are clearly padding, developers stop reading evaluation results.

Confidence gating adds tiered evidence requirements to findings: HIGH confidence requires direct code citations, MODERATE requires pattern-level evidence, and LOW (below 0.50) is advisory-only and excluded from pass/fail scoring.

## Product Requirements

### FR-1: Confidence Tier Classification

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL classify each evaluation finding into one of three confidence tiers: HIGH (0.80+), MODERATE (0.60-0.79), or LOW (below 0.60).

**Acceptance Criteria:**
- [x] Each finding in evaluation.md includes a `Confidence:` annotation with tier and numeric value
- [x] Confidence tiers are: HIGH (>= 0.80), MODERATE (0.60-0.79), LOW (< 0.60)
- [x] Confidence classification applies to both spec evaluation and implementation evaluation findings

### FR-2: Scaled Evidence Requirements

<!-- EARS: State-Driven -->
WHILE a finding is classified HIGH confidence (>= 0.80), THE SYSTEM SHALL require three evidence elements: (1) specific file path and line reference, (2) quoted or described code passage, and (3) concrete consequence or impact statement.

<!-- EARS: State-Driven -->
WHILE a finding is classified MODERATE confidence (0.60-0.79), THE SYSTEM SHALL require two evidence elements: (1) file path or code pattern reference, and (2) likely impact statement.

<!-- EARS: Unwanted Behavior -->
IF a HIGH confidence finding lacks any of the three required evidence elements, THEN THE SYSTEM SHALL downgrade it to MODERATE and append a note: "Downgraded from HIGH -- missing [element]."

**Acceptance Criteria:**
- [x] HIGH findings must cite file:line, specific code, and concrete consequence
- [x] MODERATE findings must cite file or pattern + likely impact
- [x] HIGH findings missing evidence are automatically downgraded to MODERATE
- [x] Downgrade is recorded with reason

### FR-3: Pass/Fail Scoring Exclusion for LOW Findings

<!-- EARS: State-Driven -->
WHILE a finding is classified LOW confidence (< 0.60), THE SYSTEM SHALL mark it as "advisory" and exclude it from the dimension's pass/fail score computation.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL display LOW confidence findings in the evaluation report with an `[Advisory]` prefix but SHALL NOT count them toward the dimension score or trigger remediation.

**Acceptance Criteria:**
- [x] LOW confidence findings are prefixed with `[Advisory]` in evaluation.md
- [x] LOW findings do not affect dimension pass/fail determination
- [x] LOW findings do not trigger remediation instructions
- [x] LOW findings are still visible in the evaluation report (not suppressed)

### FR-4: Evaluation Template Update

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL update the evaluation report template to include a Confidence column in the findings table and group findings by confidence tier.

**Acceptance Criteria:**
- [x] Evaluation template includes Confidence column
- [x] Evaluation report groups or annotates findings by confidence tier
- [x] Template is backward compatible (specs evaluated before this change render correctly)

## Non-Functional Requirements

- **NFR-1**: The confidence classification does not require additional file reads beyond what the evaluation protocol already performs.
- **NFR-2**: The "mandatory finding per dimension" rule remains in effect, but LOW confidence findings satisfy it only if no MODERATE or HIGH findings exist for that dimension.
- **NFR-3**: All changes use abstract operations only in core modules.

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
