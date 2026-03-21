# Feature: Dependency Safety Gate

## Overview

LLMs have knowledge cutoffs and may recommend vulnerable, deprecated, or EOL dependencies. SpecOps currently trusts the LLM to "know things" — which works for workflow structure but fails for time-sensitive engineering context (CVEs, EOL dates, API version changes). This feature adds an active, mandatory verification gate that scans project dependencies against CVEs, EOL status, and best practices before implementation begins — ensuring developers are always in safe hands, from growth startups to large enterprises.

## Product Requirements

### User Story 1: Automated Dependency Audit
**As a** developer using SpecOps
**I want** my project dependencies to be automatically scanned for vulnerabilities and EOL status during spec generation
**So that** I never unknowingly start implementing features on top of vulnerable or deprecated foundations

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven, Optional Feature -->
- WHEN a spec enters Phase 2 step 6.7 THE SYSTEM SHALL execute the dependency safety verification protocol using a 3-layer approach (local audit tools, online APIs, LLM fallback)
- WHERE dependency safety is enabled THE SYSTEM SHALL block implementation when findings exceed the configured severity threshold
- IF dependency safety is enabled and the gate is skipped THEN THE SYSTEM SHALL treat this as a protocol breach

**Progress Checklist:**
- [x] 3-layer verification protocol implemented (local → online → LLM fallback)
- [x] Phase 2 step 6.7 gate blocks implementation on threshold breach
- [x] Protocol breach enforcement language present

### User Story 2: Configurable Severity Thresholds
**As a** team lead
**I want** to configure how strictly dependency issues block implementation
**So that** I can balance speed (startups) vs. compliance (enterprises)

**Acceptance Criteria (EARS):**
<!-- EARS: Optional Feature, State-Driven -->
- WHERE severityThreshold is "strict" THE SYSTEM SHALL block on any finding
- WHERE severityThreshold is "medium" THE SYSTEM SHALL block on Critical/High findings and warn on Medium/Low
- WHERE severityThreshold is "low" THE SYSTEM SHALL warn only and never block
- WHILE no severityThreshold is configured THE SYSTEM SHALL default to "medium"

**Progress Checklist:**
- [x] Three severity thresholds implemented (strict, medium, low)
- [x] Default to "medium" when not configured
- [x] Configuration schema added to schema.json

### User Story 3: Auto-Generated Dependencies Steering File
**As a** developer
**I want** a `dependencies.md` steering file auto-generated from my project's dependency landscape
**So that** the SpecOps agent has persistent awareness of my project's dependency health across specs

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven, Ubiquitous -->
- WHEN the dependency safety gate runs THE SYSTEM SHALL create or update `<specsDir>/steering/dependencies.md` with detected dependencies and runtime status
- THE SYSTEM SHALL use the `_generated: true` pattern (same as repo-map.md) for machine-managed content
- WHEN `_generatedAt` exceeds 30 days THE SYSTEM SHALL notify the user during Phase 1 that dependency data is stale

**Progress Checklist:**
- [x] dependencies.md created as 4th foundation template in steering.md
- [x] Auto-generated with `_generated: true` pattern
- [x] Staleness detection at 30 days

### User Story 4: Per-Spec Audit Artifact
**As a** developer
**I want** a `dependency-audit.md` artifact created in each spec directory
**So that** I have a time-stamped record of the dependency health at the time each spec was created

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven -->
- WHEN the dependency safety gate completes THE SYSTEM SHALL write `dependency-audit.md` to the spec directory with a `**Verified:** YYYY-MM-DDTHH:MM:SSZ` freshness timestamp
- WHEN online verification is unavailable THE SYSTEM SHALL annotate findings with "(offline — based on training data, may not reflect latest advisories)"

**Progress Checklist:**
- [x] dependency-audit.md artifact written per spec
- [x] Freshness timestamp at top
- [x] Offline fallback clearly annotated

## Non-Functional Requirements

- Online API calls must timeout after 10 seconds (no blocking on slow networks)
- Gate must run even with no audit tools installed and no network (LLM fallback)
- Configuration must validate against schema.json with `additionalProperties: false`
- All headings in core module must be H2/H3 level to match validator marker conventions

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
