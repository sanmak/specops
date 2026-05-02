# Action Routing for Evaluation Findings

## Overview

The current evaluation system (adversarial evaluator + multi-persona review) produces findings with severity (P0-P3) and confidence (HIGH/MODERATE/LOW), but treats all findings uniformly during remediation. Every finding requires the developer to review and approve each fix individually. This creates unnecessary friction when many findings are trivially fixable by the agent (missing imports, formatting violations, naming convention deviations) while others genuinely require human judgment (architectural changes, ambiguous requirements).

Action routing classifies evaluation findings into four fix classes based on fix determinism, scope, and risk. The agent resolves auto-fixable items immediately, batches gated items for a single approval, flags manual items for developer attention, and reports advisory items without blocking.

Developer problem: "SpecOps found 6 issues, 3 are trivial formatting fixes it could have just done, but it asks about all 6 one by one."

## Product Requirements

### FR-1: Fix Class Definitions

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL classify each evaluation finding into exactly one of four fix classes:

1. **auto_fix**: Agent fixes without asking. The fix is deterministic, narrow in scope (1-2 files), and low risk. Examples: missing import, formatting fix, naming convention violation, missing test assertion, trivial typo in comments.
2. **gated_fix**: Agent proposes the fix, developer approves in batch. The fix is deterministic but affects wider scope (3+ files) or carries moderate risk. Examples: renaming a function across multiple files, adding error handling to multiple call sites, updating multiple test files.
3. **manual**: Flagged for developer, no agent fix attempted. The fix is non-deterministic, architectural, or high risk. Examples: design decision changes, architectural refactoring, ambiguous requirement interpretation, security vulnerability remediation.
4. **advisory**: Informational only, no fix expected. Examples: LOW confidence findings, P3 observations, style preferences, potential future improvements.

**Acceptance Criteria:**
- [x] Four fix classes defined with clear boundaries
- [x] Each fix class has a deterministic selection rule (not subjective judgment)
- [x] Fix class is orthogonal to severity (a P0 can be auto_fix if deterministic and safe)
- [x] Fix class is orthogonal to confidence (a HIGH confidence finding can be advisory if P3)

### FR-2: Routing Decision Matrix

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL determine the fix class for each finding using a decision matrix based on three routing signals:

1. **Fix Determinism**: Can the agent reliably generate the correct fix? (deterministic / non-deterministic)
   - Deterministic: only one correct fix exists (e.g., add missing import X)
   - Non-deterministic: multiple valid approaches exist (e.g., refactor error handling)
2. **Fix Scope**: How many files are affected? (narrow: 1-2 files / wide: 3+ files)
3. **Fix Risk**: Could the fix introduce regressions? (low / moderate / high)
   - Low: isolated change, no callers affected
   - Moderate: change affects known callers but behavior is preserved
   - High: change may alter observable behavior or requires architectural judgment

Decision matrix:

| Determinism | Scope | Risk | Fix Class |
| --- | --- | --- | --- |
| Deterministic | Narrow | Low | auto_fix |
| Deterministic | Narrow | Moderate | gated_fix |
| Deterministic | Wide | Low | gated_fix |
| Deterministic | Wide | Moderate | gated_fix |
| Deterministic | Any | High | manual |
| Non-deterministic | Any | Any | manual |

Override rules:
- LOW confidence findings are always classified as `advisory` regardless of the matrix result.
- P3 severity findings are classified as `advisory` unless the matrix yields `auto_fix` (then remain auto_fix -- trivial fixes should still be auto-fixed even at P3).

**Acceptance Criteria:**
- [x] Decision matrix uses three routing signals: determinism, scope, risk
- [x] Matrix produces a deterministic fix class for every combination
- [x] LOW confidence override routes all LOW findings to advisory
- [x] P3 override routes most P3 findings to advisory
- [x] Matrix documented in core/evaluation.md

### FR-3: Auto-Fix Execution

<!-- EARS: Event-Driven -->
WHEN the action router classifies a finding as `auto_fix`, THE SYSTEM SHALL apply the fix immediately without developer interaction during the Phase 4B remediation cycle.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL execute all auto_fix items before presenting gated_fix items for approval.

<!-- EARS: Unwanted Behavior -->
IF an auto_fix application fails (edit fails, test breaks after applying), THEN THE SYSTEM SHALL revert the change and reclassify the finding as `gated_fix`.

**Acceptance Criteria:**
- [x] Auto-fix items applied without developer interaction
- [x] Auto-fix execution happens before gated_fix presentation
- [x] Failed auto-fixes are reverted and reclassified as gated_fix
- [x] Auto-fix changes are logged in implementation.md

### FR-4: Gated Fix Batching

<!-- EARS: Event-Driven -->
WHEN the action router classifies one or more findings as `gated_fix`, THE SYSTEM SHALL present all gated fixes as a single batch for developer approval.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL present each gated fix with: finding ID, description, proposed change (file path + diff summary), and risk assessment.

<!-- EARS: State-Driven -->
WHILE the platform capability `canAskInteractive` is false, THE SYSTEM SHALL treat all `gated_fix` items as `auto_fix` (apply without asking) since there is no mechanism for developer approval.

**Acceptance Criteria:**
- [x] Gated fixes presented as a single batch (not one-by-one)
- [x] Each gated fix includes finding ID, description, proposed change, and risk
- [x] Developer can approve all, reject all, or selectively approve
- [x] Non-interactive platforms auto-apply gated fixes
- [x] Batch presentation happens after all auto-fixes are applied

### FR-5: Manual Finding Reporting

<!-- EARS: Event-Driven -->
WHEN the action router classifies a finding as `manual`, THE SYSTEM SHALL report it to the developer with the finding details, evidence, and a note that agent remediation is not attempted.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL NOT attempt to fix `manual` findings. Manual findings are reported for developer awareness only.

**Acceptance Criteria:**
- [x] Manual findings reported with full details (ID, severity, evidence, description)
- [x] No fix attempted for manual findings
- [x] Manual findings clearly distinguished from advisory findings in the report

### FR-6: Advisory Finding Reporting

<!-- EARS: Event-Driven -->
WHEN the action router classifies a finding as `advisory`, THE SYSTEM SHALL include it in the evaluation report as informational context.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL NOT count advisory findings toward the pass/fail verdict or trigger remediation.

**Acceptance Criteria:**
- [x] Advisory findings appear in evaluation report
- [x] Advisory findings do not affect pass/fail verdict
- [x] Advisory findings do not trigger remediation cycles
- [x] LOW confidence findings always routed to advisory

### FR-7: Evaluation Template Update

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL add a `Fix Class` column to the evaluation findings table in `core/templates/evaluation.md`.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL add an `## Action Routing Summary` section to the evaluation template showing counts per fix class and the routing decision for each finding.

**Acceptance Criteria:**
- [x] Fix Class column added to findings tables in evaluation template
- [x] Action Routing Summary section added to evaluation template
- [x] Summary includes counts: N auto_fix, N gated_fix, N manual, N advisory
- [x] Template is backward compatible (specs without action routing render correctly)

### FR-8: Pipeline Integration

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL integrate action routing into the pipeline mode's remediation cycle, applying auto_fix items before re-evaluation and batching gated items.

<!-- EARS: State-Driven -->
WHILE the pipeline is in an automated cycle, THE SYSTEM SHALL apply auto_fix items and (on non-interactive platforms) gated_fix items without stopping the cycle.

**Acceptance Criteria:**
- [x] Pipeline mode uses action routing during Phase 4B remediation
- [x] Auto-fix items applied within the pipeline cycle without stopping
- [x] Gated items batched for approval (interactive) or auto-applied (non-interactive)
- [x] Pipeline cycle count respects maxCycles even with action routing

### FR-9: Generator Pipeline Wiring

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL update the generator pipeline to validate action routing content in all 5 platform outputs.

**Acceptance Criteria:**
- [x] ACTION_ROUTING_MARKERS constant defined in validate.py
- [x] Markers checked in validate_platform() per-platform validation
- [x] Markers checked in cross-platform consistency loop
- [x] MARKERS imported in test_platform_consistency.py
- [x] All 5 platform outputs regenerated with action routing content

## Non-Functional Requirements

- **NFR-1**: Action routing adds no additional sub-agent dispatches. It operates as a classification step within the existing evaluation flow.
- **NFR-2**: All additions use abstract operations only in core modules (no platform-specific tool names).
- **NFR-3**: The routing decision matrix is deterministic -- same inputs always produce the same fix class. No stochastic or LLM-judgment-dependent classification.
- **NFR-4**: Action routing is always active when evaluation is enabled. There is no separate config switch.
- **NFR-5**: Backward compatibility -- specs evaluated before this change render correctly (action routing sections are additive).

## Deferred Criteria

- **Per-finding auto-fix confidence tracking** (future): Track success rate of auto-fixes per finding pattern to improve routing accuracy over time.
- **Custom routing rules** (future): Allow projects to override the routing matrix via `.specops.json` for domain-specific classification.

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
