# Feature: Local Memory Layer

## Overview
A persistent, git-tracked memory system for SpecOps that stores architectural decisions, project context, and recurring patterns across spec sessions. When a spec completes, the memory layer auto-extracts decisions from `implementation.md` and updates project context. When a new spec starts, memory is loaded in Phase 1 so the agent has cross-session awareness of prior work. No cloud dependency — pure local files in `<specsDir>/memory/`.

## Product Requirements

### Requirement 1: Memory Persistence
**As a** developer using SpecOps across multiple sessions
**I want** decisions and context from prior specs to persist automatically
**So that** each new spec session starts with full awareness of what was built before

**Acceptance Criteria (EARS):**
<!-- Event-Driven: memory writing triggered by spec completion -->
- WHEN a spec reaches Phase 4 completion THE SYSTEM SHALL extract Decision Log entries from `implementation.md` and append them to `<specsDir>/memory/decisions.json`
<!-- Event-Driven: memory writing for context -->
- WHEN a spec reaches Phase 4 completion THE SYSTEM SHALL update `<specsDir>/memory/context.md` with a summary entry (spec name, type, key outputs, completion date)
<!-- Ubiquitous: storage format -->
- THE SYSTEM SHALL store all memory files in `<specsDir>/memory/` as git-trackable plain files (JSON and markdown)

**Progress Checklist:**
- [x] Decision Log extraction from implementation.md to decisions.json
- [x] Context summary auto-update in context.md on spec completion
- [x] All memory files stored in `<specsDir>/memory/` directory

### Requirement 2: Memory Loading
**As a** developer starting a new spec
**I want** prior decisions and context loaded automatically
**So that** I don't re-derive architectural choices or lose context from earlier work

**Acceptance Criteria (EARS):**
<!-- Event-Driven: memory loading in Phase 1 -->
- WHEN Phase 1 starts and FILE_EXISTS(`<specsDir>/memory/decisions.json`) THE SYSTEM SHALL load decisions into the agent's context
<!-- Event-Driven: context loading -->
- WHEN Phase 1 starts and FILE_EXISTS(`<specsDir>/memory/context.md`) THE SYSTEM SHALL load project context into the agent's context
<!-- Unwanted: corrupt memory -->
- IF memory files contain invalid JSON or malformed content THEN THE SYSTEM SHALL warn the user and proceed without memory rather than failing

**Progress Checklist:**
- [x] decisions.json loaded in Phase 1 (after steering files)
- [x] context.md loaded in Phase 1 (after steering files)
- [x] Graceful degradation on corrupt/missing memory files

### Requirement 3: Pattern Detection
**As a** developer working through a series of specs
**I want** recurring patterns (repeated decision categories, shared file modifications) detected automatically
**So that** I can spot emerging conventions and avoid repeating mistakes

**Acceptance Criteria (EARS):**
<!-- Event-Driven: pattern detection on write -->
- WHEN memory is written in Phase 4 THE SYSTEM SHALL scan decisions.json for recurring decision categories across specs and record matches in `<specsDir>/memory/patterns.json`
<!-- Event-Driven: cross-spec file overlap -->
- WHEN memory is written THE SYSTEM SHALL check which files were modified across multiple completed specs and record overlaps in patterns.json

**Progress Checklist:**
- [x] Recurring decision category detection across specs
- [x] Cross-spec file modification overlap detection
- [x] Pattern entries written to patterns.json

### Requirement 4: Memory Subcommand
**As a** developer who wants to inspect or seed the memory layer
**I want** a `/specops memory` command to view current memory state
**So that** I can verify what the agent knows and manually seed decisions if needed

**Acceptance Criteria (EARS):**
<!-- Event-Driven: subcommand invocation -->
- WHEN the user invokes `/specops memory` THE SYSTEM SHALL display a formatted summary of decisions, context, and patterns
<!-- Optional: seeding -->
- WHERE the user invokes `/specops memory seed` THE SYSTEM SHALL scan all completed specs' implementation.md files and populate decisions.json from their Decision Log entries

**Progress Checklist:**
- [x] `/specops memory` displays formatted memory summary
- [x] `/specops memory seed` populates from existing specs

## Scope Boundary

**Ships in v1 (this spec):**
- `core/memory.md` module with loading, writing, and subcommand logic
- decisions.json auto-population from implementation.md Decision Log
- context.md auto-update with spec completion summaries
- patterns.json with decision category recurrence and file overlap detection
- Phase 1 integration (load after steering)
- Phase 4 integration (write after implementation.md finalized)
- `/specops memory` view and `memory seed` subcommands
- Generator pipeline wiring (generate.py, templates, validate.py, tests)
- Platform adaptation for non-interactive platforms

**Deferred:**
- AI-driven pattern analysis (semantic similarity across decisions)
- Memory search/query ("what decisions were made about authentication?")
- Memory pruning/archival for long-running projects
- Cross-project memory sharing
- Memory conflict resolution on merge

## Non-Functional Requirements
- Memory files must be human-readable (JSON with indentation, markdown)
- Memory loading must not significantly increase Phase 1 duration (bounded to at most 3 additional memory file reads)
- decisions.json schema must be forward-compatible (version field for future schema changes)

## Constraints & Assumptions
- No cloud dependency — all files are local and git-tracked
- Memory directory uses convention-based discovery (directory existence), not schema config — same pattern as steering files
- Python 3 stdlib only for any memory-related scripts (no new dependencies)
- implementation.md Decision Log table format is stable across all specs (verified by 4 completed specs)

## Success Metrics
- After building this spec, seed memory with decisions from Specs 1–4 and verify they load in subsequent sessions
- Dogfood proof: this spec's own Phase 1 benefits from loaded memory (if seeded before implementation)

## Out of Scope
- Cloud-based memory sync
- Memory encryption or access control
- Real-time memory updates during Phase 3 (memory writes happen only in Phase 4)
- Integration with external knowledge bases

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
