# Production Learnings — Requirements

## Overview

Add a production learnings layer to SpecOps that captures post-deployment discoveries, links them to originating specs, detects cross-spec patterns, and surfaces relevant learnings during future spec work. Inspired by ADR immutability (Netflix), fitness functions (ThoughtWorks), and "Reconsider When" triggers from ADR practice.

## User Stories

### US-1: Capture learning at moment of discovery

As a developer fixing a production bug, I want to capture what the original spec missed so future specs don't repeat the same mistake.

### US-2: Surface relevant learnings in future specs

As a developer starting a new spec, I want the agent to surface relevant production learnings from past specs touching the same modules so I can factor in hard-won production knowledge.

### US-3: Detect cross-spec learning patterns

As a team lead, I want to see cross-spec learning patterns to identify systemic gaps in our spec process.

## Acceptance Criteria

<!-- EARS: WHEN <trigger> THE SYSTEM SHALL <response> -->

### AC-1: Explicit learning capture

WHEN a developer invokes `/specops learn <spec-name>`, THE SYSTEM SHALL prompt for learning details (category, description, affected files, reconsiderWhen conditions) and store the learning in `<specsDir>/memory/learnings.json`.

### AC-2: Agent-proposed learning extraction

WHEN the agent is working on a bugfix spec linked to a prior spec, THE SYSTEM SHALL propose a learning extraction: "This fix suggests [insight]. Capture as production learning for [spec]?"

### AC-3: Filtered learning surfacing in Phase 1

WHEN Phase 1 loads memory for a new spec, THE SYSTEM SHALL filter learnings by file-path proximity, recurrence count, severity, and validity conditions — surfacing only relevant, non-invalidated learnings (max 3 per load).

### AC-4: Validity condition evaluation

WHEN a learning has a `reconsiderWhen` condition that evaluates to true (file removed, version changed, threshold exceeded), THE SYSTEM SHALL flag it as "potentially invalidated" rather than presenting it as fact.

### AC-5: Cross-spec pattern detection

WHEN 2+ specs share learnings in the same category, THE SYSTEM SHALL detect this as a recurring pattern and store it in `patterns.json` under a `learningPatterns` array.

### AC-6: Immutable records

WHEN a learning needs correction, THE SYSTEM SHALL create a new learning with `supersedes` reference to the old one, and mark the old learning's `supersededBy` field — never editing the original record.

### AC-7: Reconciliation-based extraction

WHEN a developer invokes `/specops reconcile --learnings`, THE SYSTEM SHALL scan recent git history for hotfix patterns linked to specs and propose learnings for approval.

## Constraints

- Learnings are immutable records (ADR pattern) — supersede, never edit
- No secrets, PII, credentials, or connection strings stored in learnings
- Learnings storage must follow path containment rules (within specsDir)
- Agent surfaces max 3 learnings per Phase 1 load (configurable via `maxSurfaced`, cap 10)
- `reconsiderWhen` conditions must be evaluable by the agent (file existence, version checks, metric thresholds — not subjective judgments)
- Core module must use abstract operations only (READ_FILE, WRITE_FILE, etc.)
- New markers must be added to both `validate_platform()` and cross-platform consistency check (Gap 31)
