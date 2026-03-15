# Feature: AST-Based Repo Map

## Overview
Add a persistent, machine-generated structural map of the user's codebase to SpecOps. The repo map is stored as a steering file at `<specsDir>/steering/repo-map.md` with `inclusion: always`, giving the agent structural context ("what files exist, what do they define") automatically during Phase 1. It complements hand-written steering files (product.md, tech.md, structure.md) with machine-generated structural detail, and supports auto-refresh when stale.

## Product Requirements

### Requirement 1: Repo Map Generation
**As a** developer using SpecOps
**I want** the agent to generate a structural map of my codebase automatically
**So that** the agent has better context about file organization and code structure when creating specs

**Acceptance Criteria (EARS):**
<!-- EARS patterns:
  Event-Driven:   WHEN [event] THE SYSTEM SHALL [behavior]
  Unwanted:       IF [unwanted condition] THEN THE SYSTEM SHALL [response]
-->
- WHEN a repo map is requested or missing THE SYSTEM SHALL discover project files using `git ls-files` (with LIST_DIR fallback), classify files by language tier, extract structural declarations, and write the result to `<specsDir>/steering/repo-map.md`
- WHEN generating a repo map THE SYSTEM SHALL respect scope limits: max 100 files, max depth 3 levels, and a ~3000 token budget for the output
- WHEN generating a repo map THE SYSTEM SHALL extract declarations at different detail levels by language: Python (function/class signatures via `ast.parse`), TypeScript/JavaScript (export statements), Go/Rust/Java (top-level declarations), other (file path only)
- IF `git ls-files` is unavailable THEN THE SYSTEM SHALL fall back to LIST_DIR with `.gitignore` exclusion
- IF Python `ast.parse()` fails for a file THEN THE SYSTEM SHALL fall back to file-path-only listing for that file

**Progress Checklist:**
- [x] Agent-driven file discovery with git ls-files + LIST_DIR fallback
- [x] 4-tier language extraction (Python signatures, TS/JS exports, Go/Rust/Java declarations, other)
- [x] Scope limits enforced (100 files, depth 3, ~3000 token budget)
- [x] Graceful fallback on tool unavailability

### Requirement 2: Staleness Detection & Auto-Refresh
**As a** developer using SpecOps across multiple sessions
**I want** the repo map to auto-refresh when it becomes stale
**So that** the agent always has an up-to-date structural view of my codebase

**Acceptance Criteria (EARS):**
- WHEN Phase 1 loads steering files and a repo map exists THE SYSTEM SHALL check staleness using time-based (>7 days since `_generatedAt`) and hash-based (`_sourceHash` mismatch against current file list) detection
- WHEN the repo map is stale THE SYSTEM SHALL auto-refresh it and notify the user
- WHEN Phase 1 runs and no repo map exists THE SYSTEM SHALL offer to generate one on interactive platforms, or display a tip message on non-interactive platforms

**Progress Checklist:**
- [x] Time-based staleness check (7-day threshold)
- [x] Hash-based staleness check (file list hash comparison)
- [x] Auto-refresh on stale detection with user notification
- [x] Interactive prompt when missing / non-interactive tip message

### Requirement 3: Explicit Map Subcommand
**As a** developer
**I want** to explicitly generate or refresh the repo map via `/specops map`
**So that** I can trigger a refresh without waiting for staleness detection

**Acceptance Criteria (EARS):**
- WHEN the user invokes `/specops map` THE SYSTEM SHALL generate a new repo map (or refresh an existing one) and display a summary of what was mapped
- WHEN the user invokes `/specops map` and a repo map already exists THE SYSTEM SHALL show the current map metadata (generated at, file count, hash) before refreshing

**Progress Checklist:**
- [x] `/specops map` subcommand detection and routing
- [x] Map generation/refresh workflow
- [x] Display map metadata summary

## Scope Boundary

**Ships in this spec:**
- `core/repo-map.md` module with generation algorithm, staleness detection, scope control, safety
- Phase 1 step 3.5 integration (auto-detect missing/stale, refresh)
- `/specops map` subcommand routing in workflow.md
- Generator pipeline wiring (all 4 platforms)
- Validator markers (per-platform + cross-platform)
- `core/steering.md` extended with `_generated`, `_generatedAt`, `_sourceHash` frontmatter fields

**Deferred:**
- `scripts/repo-map.py` accelerator script *(deferred — agent-driven generation sufficient for v1)*
- Configurable scope limits in `.specops.json` *(deferred — hardcoded defaults sufficient for v1)*
- Per-language configuration *(deferred — 4-tier system covers major languages)*

## Non-Functional Requirements
- **Performance**: Generation should complete in <30 seconds for repos with ≤100 files
- **Token budget**: Output capped at ~3000 tokens (~12K characters) to fit in agent context
- **Safety**: Path containment rules apply — no absolute paths or `../` traversal in generated map

## Constraints & Assumptions
- Assumes Python 3 is available for `ast.parse()` extraction (graceful fallback if not)
- Assumes `git` is available for file discovery (graceful fallback to LIST_DIR)
- Repo map is a single file — not split per language or per directory

## Success Metrics
- Agent has structural context about the codebase without manual setup
- Repo map stays fresh across sessions via staleness detection
- All 4 platform outputs include repo map module with correct tool substitution

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
