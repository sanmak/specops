# Feature: Dependency Introduction Gate

## Overview

Add a core enforcement mechanism that prevents AI agents from casually installing new packages during implementation. All dependency decisions happen during spec creation (Phase 2). Phase 3 only installs what the spec approved. Adversarial evaluation and drift detection close remaining gaps. This complements the existing `core/dependency-safety.md` (CVE/EOL audit) by controlling *which* dependencies enter the project, not just whether existing ones are safe.

## User Stories

### Story 1: Phase 2 Dependency Evaluation

**As a** developer using SpecOps
**I want** all new dependency decisions to be surfaced and approved during spec creation
**So that** no surprise packages appear during implementation

**Acceptance Criteria (EARS):**
<!-- Use the EARS pattern that best fits each criterion:
  Ubiquitous:     THE SYSTEM SHALL [behavior]
  Event-Driven:   WHEN [event] THE SYSTEM SHALL [behavior]
  State-Driven:   WHILE [state] THE SYSTEM SHALL [behavior]
  Optional:       WHERE [feature is enabled] THE SYSTEM SHALL [behavior]
  Unwanted:       IF [unwanted condition] THEN THE SYSTEM SHALL [response]
-->
- WHEN Phase 2 step 5.8 executes THE SYSTEM SHALL scan design.md for install commands and new package references, compare them against the Detected Dependencies in dependencies.md steering file, and surface any net-new dependencies to the user via ASK_USER
- WHEN a new dependency is identified THE SYSTEM SHALL evaluate it against the 5-criteria Build-vs-Install framework (scope match, maintenance health, size proportionality, security surface, license compatibility) and present the evaluation to the user
- WHEN the user approves a dependency THE SYSTEM SHALL record it in design.md under a ### Dependency Decisions section with the evaluation rationale
- WHEN the user rejects a dependency THE SYSTEM SHALL record the rejection and note that a build-it-yourself approach is required in design.md
- THE SYSTEM SHALL run Maintenance Profile Intelligence (3-layer: registry API, source repo, LLM fallback) for each new dependency to assess maintenance health

**Progress Checklist:**

- [x] Phase 2 step 5.8 scans design.md for install commands and new package references
- [x] Net-new dependencies surfaced to user via ASK_USER with Build-vs-Install evaluation
- [x] Approved dependencies recorded in design.md ### Dependency Decisions
- [x] Rejected dependencies recorded with build-it-yourself note
- [x] Maintenance Profile Intelligence runs 3-layer assessment for each new dependency

### Story 2: Phase 3 Spec Adherence Enforcement

**As a** developer using SpecOps
**I want** Phase 3 to only install dependencies that were approved in the spec
**So that** implementation cannot introduce unapproved packages

**Acceptance Criteria (EARS):**
- WHEN Phase 3 encounters an install command (npm install, pip install, cargo add, etc.) THE SYSTEM SHALL verify the target package appears in design.md ### Dependency Decisions before executing the command
- IF an unapproved dependency install is attempted during Phase 3 THEN THE SYSTEM SHALL flag it as a protocol breach and halt until the user either approves the addition or removes the install
- THE SYSTEM SHALL recognize install command patterns across all supported ecosystems (Node.js, Python, Rust, Ruby, Go, PHP, Java/Kotlin)
- WHEN Phase 3 completes THE SYSTEM SHALL verify that all approved dependencies from design.md ### Dependency Decisions were actually installed (no phantom approvals)

**Progress Checklist:**

- [x] Phase 3 verifies packages against design.md ### Dependency Decisions before install
- [x] Unapproved install attempts flagged as protocol breach
- [x] Install command patterns recognized for all supported ecosystems
- [x] Post-Phase-3 verification checks all approved deps were actually installed

### Story 3: Auto-Intelligence Policy Generation

**As a** developer using SpecOps
**I want** the system to auto-generate a Dependency Introduction Policy in the dependencies.md steering file
**So that** project-level dependency governance accumulates automatically over spec runs

**Acceptance Criteria (EARS):**
- WHEN the dependency introduction gate runs for the first time THE SYSTEM SHALL create a ## Dependency Introduction Policy section in dependencies.md with the project's detected ecosystem, default policy (conservative for builder/library, moderate for others), and any team conventions about dependencies
- WHEN a dependency decision is made (approved or rejected) THE SYSTEM SHALL update the Dependency Introduction Policy with the decision pattern (e.g., "Prefer built-in solutions for HTTP clients")
- THE SYSTEM SHALL preserve team-maintained sections in dependencies.md across auto-generation (same pattern as existing Detected Dependencies auto-population)

**Progress Checklist:**

- [x] First-run creates ## Dependency Introduction Policy in dependencies.md
- [x] Policy auto-populated with detected ecosystem and default stance
- [x] Decisions update the policy with patterns
- [x] Team-maintained sections preserved across regeneration

### Story 4: Adversarial Evaluation Integration

**As a** developer using SpecOps
**I want** adversarial evaluation to check dependency governance
**So that** specs and implementations that ignore dependency decisions are scored lower

**Acceptance Criteria (EARS):**
- WHEN spec evaluation runs (Phase 2 exit gate) THE SYSTEM SHALL include dependency decision completeness in the Design Coherence dimension scoring guidance -- specs that introduce dependencies in design.md without a ### Dependency Decisions section score lower
- WHEN implementation evaluation runs (Phase 4A) THE SYSTEM SHALL include dependency adherence in the Design Fidelity dimension scoring guidance -- implementations that install packages not listed in ### Dependency Decisions score lower
- THE SYSTEM SHALL add scoring guidance text to both dimensions without changing the scoring rubric structure or thresholds

**Progress Checklist:**

- [x] Design Coherence scoring guidance updated for dependency decision completeness
- [x] Design Fidelity scoring guidance updated for dependency adherence
- [x] Scoring guidance additions do not change rubric structure or thresholds

### Story 5: Audit Mode Dependency Drift Check

**As a** developer using SpecOps
**I want** audit mode to detect dependency drift between specs and the live codebase
**So that** dependencies added outside the spec workflow are caught

**Acceptance Criteria (EARS):**
- WHEN audit mode runs THE SYSTEM SHALL execute a 7th drift check (Dependency Drift) that compares installed packages against the union of all approved dependencies across completed specs
- IF a package is installed but not approved in any spec THEN THE SYSTEM SHALL flag it as Warning (not Drift, since it may have been a pre-existing dependency)
- THE SYSTEM SHALL detect packages by reading lock files (package-lock.json, yarn.lock, requirements.txt, Cargo.lock, etc.) using the same ecosystem detection from core/dependency-safety.md

**Progress Checklist:**

- [x] 7th drift check (Dependency Drift) added to audit mode
- [x] Compares installed packages against union of approved dependencies
- [x] Unapproved packages flagged as Warning
- [x] Uses ecosystem detection from existing dependency-safety.md

### Story 6: Generator Pipeline Integration

**As a** developer maintaining SpecOps
**I want** the new core module to be integrated into the generator pipeline
**So that** all 5 platforms include the dependency introduction gate

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL add `dependency_introduction` to `build_common_context()` in generate.py
- THE SYSTEM SHALL add `{{ dependency_introduction }}` to all 5 Jinja2 templates (claude.j2, cursor.j2, codex.j2, copilot.j2, antigravity.j2)
- THE SYSTEM SHALL add `dependency-introduction` to mode-manifest.json for the spec mode and from-plan mode modules lists
- THE SYSTEM SHALL define DEPENDENCY_INTRODUCTION_MARKERS in validate.py, add the check to validate_platform(), add it to the cross-platform consistency loop, and import it in test_platform_consistency.py
- WHEN `python3 generator/generate.py --all` runs THE SYSTEM SHALL produce outputs that pass `python3 generator/validate.py` including the new markers

**Progress Checklist:**

- [x] `dependency_introduction` added to `build_common_context()` in generate.py
- [x] `{{ dependency_introduction }}` added to all 5 Jinja2 templates
- [x] `dependency-introduction` added to mode-manifest.json (spec and from-plan modes)
- [x] DEPENDENCY_INTRODUCTION_MARKERS defined in validate.py
- [x] Markers check added to validate_platform() function
- [x] Markers added to cross-platform consistency loop in validate.py
- [x] DEPENDENCY_INTRODUCTION_MARKERS imported in test_platform_consistency.py
- [x] Generated outputs pass validation

## Non-Functional Requirements

- Performance: The dependency introduction gate must not add more than 5 seconds to Phase 2 execution (registry API calls use 10-second timeouts)
- No configuration: The gate is always active with no config knobs, no bypass, deterministic behavior
- Backward compatibility: Specs created before this feature work unchanged (gate passes trivially when no ### Dependency Decisions section exists)

## Constraints & Assumptions

- This gate complements but does not replace `core/dependency-safety.md` -- that module handles CVE/EOL auditing of *existing* dependencies; this module governs *introduction* of new ones
- No new npm/pip dependencies required for this feature (pure markdown/workflow logic)
- The gate is always active -- no `enabled: false` switch, no `config.dependencyIntroduction` section
- Registry API calls (npmjs.com, pypi.org) may fail -- the 3-layer fallback (API, source repo, LLM) handles this gracefully

## Dependencies & Blockers

### Spec Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| dependency-safety-gate | Shares ecosystem detection, dependencies.md steering file | No | Completed |
| adversarial-evaluation | Scoring dimensions to extend | No | Completed |

### Cross-Spec Blockers

<!-- Resolution types: scope_cut, interface_defined, completed, escalated, deferred -->

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| ------- | ------------- | --------------- | ----------------- | ------ |
| -- | -- | -- | -- | -- |

## Success Metrics

- All 5 platform outputs include DEPENDENCY_INTRODUCTION_MARKERS and pass validation
- Phase 2 surfaces new dependencies to the user before Phase 3 begins
- Phase 3 blocks unapproved installs with protocol breach flag
- Audit mode detects packages not approved in any spec

## Out of Scope

- Replacing or modifying the existing dependency-safety.md CVE/EOL audit flow
- Adding configuration knobs (enabled/disabled, thresholds, etc.) to .specops.json
- Dependency version pinning or lock file management
- Automatic dependency removal or uninstall commands
- Monorepo per-workspace dependency scoping

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
