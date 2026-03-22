# Production Learnings — Implementation Journal

## Phase 1 Context Summary

**Spec type:** Feature
**Vertical:** Builder
**Origin:** Converted from plan via `/specops from-plan` (plan file: `~/.claude/plans/humming-pondering-lighthouse.md`)

**Context:** SpecOps specs end at "completed" but production reveals things specs didn't anticipate. This feature adds a production learnings layer that captures post-deployment discoveries, links them to originating specs, and surfaces relevant learnings during future spec work. Design informed by ADR immutability (Netflix), fitness functions (ThoughtWorks), "Reconsider When" triggers, and the principle that knowledge capture must be zero-friction (agent proposes, human approves).

**Key files identified:**
- `core/workflow.md` — Phase 1 (loading) and Phase 4 (capture) integration points
- `core/memory.md` — Existing memory system to extend
- `core/reconciliation.md` — Reconciliation-based extraction extension
- `core/dispatcher.md` — New `learn` mode route
- `core/mode-manifest.json` — Mode-to-module mappings
- `generator/generate.py` — `build_common_context()` for pipeline wiring
- `generator/validate.py` — Marker validation
- `spec-schema.json`, `schema.json` — Schema extensions
- `generator/templates/*.j2` — Template placeholders

**Codebase patterns to follow:**
- Memory module pattern: `core/memory.md` (Phase 1 load, Phase 4 write, pattern detection)
- Steering file pattern: `core/steering.md` (convention-based directory, no schema config)
- Abstract operation usage: all core modules use READ_FILE, WRITE_FILE, etc.
- Gap 31 enforcement: markers in both `validate_platform()` AND cross-platform consistency check
- Sub-step notation: use step N.5 to avoid renumbering existing steps

## Documentation Review

- CLAUDE.md: Updated mode count (15 to 16), added `core/learnings.md` to key modules list
- docs/COMMANDS.md: Added Production Learnings section with command reference, workflow, and capture mechanisms
- docs/STRUCTURE.md: Already lists `core/learnings.md` (verified in sync)
- docs/REFERENCE.md: Already documents `implementation.learnings` config (verified in sync)
- CHANGELOG.md: Added production learnings, learn mode, and from-plan enforcement to Unreleased section

## Decision Log

(Populated during implementation)
