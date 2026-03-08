# Feature: Drift Detection & Guided Reconciliation

## Overview
Add `audit` and `reconcile` subcommands to SpecOps. `audit` detects drift between spec artifacts and the codebase (file deletions, post-completion modifications, task inconsistencies, staleness, cross-spec conflicts). `reconcile` guides interactive repair. Both run on all 4 platforms; reconcile is gated behind `canAskInteractive`.

## Product Requirements

### Requirement 1: Audit Mode
**As a** developer using SpecOps
**I want** to audit my specs for drift against the codebase
**So that** I can catch silent drift before it makes specs untrustworthy

**Acceptance Criteria (EARS):**
<!-- Ubiquitous: THE SYSTEM SHALL [behavior]
     Event-Driven: WHEN [event] THE SYSTEM SHALL [behavior]
     Unwanted: IF [unwanted condition] THEN THE SYSTEM SHALL [response] -->
- WHEN the user invokes audit mode THE SYSTEM SHALL run 5 drift checks (File Drift, Post-Completion Modification, Task Status Inconsistency, Staleness, Cross-Spec Conflicts) and output a Health Summary per spec
- WHEN all checks pass THE SYSTEM SHALL report overall health as `Healthy`
- WHEN any check finds a mismatch without confirmed data loss THE SYSTEM SHALL report `Warning`
- WHEN any check confirms missing files or irrecoverable drift THE SYSTEM SHALL report `Drift`
- IF `canAccessGit` is false THE SYSTEM SHALL skip git-dependent checks (Post-Completion Modification and Staleness via git) and note each skip in the report
- IF no specs exist in `<specsDir>` THEN THE SYSTEM SHALL report "No specs found to audit"

**Progress Checklist:**
- [x] Audit mode detects and routes on audit trigger patterns
- [x] All 5 checks run and report Healthy/Warning/Drift per check
- [x] Overall health = worst finding across all checks
- [x] Git-dependent checks skipped gracefully when `canAccessGit` is false
- [x] Empty specs directory handled with user-friendly message

### Requirement 2: Reconcile Mode
**As a** developer
**I want** interactive guided repair for drifted specs
**So that** I can fix drift without manually editing multiple spec files

**Acceptance Criteria (EARS):**
- WHEN the user invokes reconcile mode on a spec THE SYSTEM SHALL first run a full audit, then present findings as a numbered list with repair options per finding
- WHEN all checks are Healthy THE SYSTEM SHALL report "No drift detected. No reconciliation needed." and stop
- WHEN the user selects findings to fix THE SYSTEM SHALL apply the chosen repairs, update `spec.json.updated` via `RUN_COMMAND(\`date -u\`)`, and regenerate `index.json`
- IF `canAskInteractive` is false THEN THE SYSTEM SHALL display "Reconcile mode requires interactive input" and stop without making changes

**Progress Checklist:**
- [x] Reconcile routes correctly and runs audit first
- [x] Healthy specs exit with "no drift" message
- [x] Repairs update spec.json.updated and regenerate index.json
- [x] Non-interactive platforms blocked with clear message

### Requirement 3: Generator Pipeline Integration
**As a** SpecOps maintainer
**I want** the reconciliation module included in all 4 platform outputs
**So that** every platform (Claude, Cursor, Codex, Copilot) gets audit and reconcile

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include `core/reconciliation.md` content in all 4 generated platform outputs via the Jinja2 pipeline
- WHEN `python3 generator/validate.py` runs THE SYSTEM SHALL verify all RECONCILIATION_MARKERS are present in every platform output
- THE SYSTEM SHALL include reconciliation markers in the cross-platform consistency check in `tests/test_platform_consistency.py`

**Progress Checklist:**
- [x] `{{ reconciliation }}` placeholder in all 4 Jinja2 templates
- [x] `"reconciliation": core["reconciliation"]` in all 4 context dicts in generate.py
- [x] RECONCILIATION_MARKERS added to validate.py and consistency test

### Requirement 4: Mode Detection in Getting Started
**As a** SpecOps user
**I want** audit and reconcile to be discoverable as first-class subcommands
**So that** the routing is predictable and documented alongside other modes

**Acceptance Criteria (EARS):**
- WHEN the user's request matches audit/reconcile patterns THE SYSTEM SHALL route to reconciliation mode before checking interview mode and the standard workflow
- THE SYSTEM SHALL support trigger patterns: `audit`, `audit <name>`, `health check`, `check drift`, `spec health` for audit; `reconcile <name>`, `fix <name>`, `repair <name>`, `sync <name>` for reconcile

**Progress Checklist:**
- [x] Mode detection added to core/workflow.md Getting Started section
- [x] Audit triggers and reconcile triggers documented
- [x] COMMANDS.md Quick Lookup updated with audit and reconcile rows

## Scope Boundary

**Ships in this spec:**
- `audit` and `reconcile` subcommands via `core/reconciliation.md`
- 5 drift checks: File Drift, Post-Completion Modification, Task Status Inconsistency, Staleness, Cross-Spec Conflicts
- Interactive repair options for all finding types
- Full generator pipeline integration (all 4 platforms)
- COMMANDS.md update

**Deferred to future specs:**
- CI-integrated drift alerts (auto-run audit on push)
- Drift metrics/trends over time
- Auto-fix without interactive prompt (non-interactive reconcile)
- Configurable thresholds for staleness (currently hardcoded 7d/14d/30d)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
