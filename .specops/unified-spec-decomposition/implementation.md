# Implementation: Unified Spec Decomposition + Cross-Spec Dependencies + Initiative Orchestration + Phase Dispatch

## Phase 1 Context Summary

### Codebase Understanding

SpecOps uses a three-tier architecture: core modules (`core/*.md`) with abstract operations → platform adapters (`platforms/<platform>/platform.json`) → generated outputs via Jinja2 templates (`generator/templates/*.j2`). The generator (`generator/generate.py`) reads core modules, maps them to template variables, and produces platform-specific skill files. The validator (`generator/validate.py`) enforces marker presence across all platforms.

### Key Files & Insertion Points

| Area | File | Relevance |
|------|------|-----------|
| Workflow | `core/workflow.md` | Phase 1-4 steps; insert scope assessment (step 9.5), split detection (Phase 2 step 1.5), dependency gate (Phase 3 step 1), initiative update (Phase 4 step 6.3), phase dispatch gates (steps 6.8, 8.5) |
| Dispatcher | `core/dispatcher.md` | Mode Router table (add initiative mode), Pre-Phase-3 Enforcement Checklist (add check 8: dependency gate), Dispatch Protocol (phase dispatch signals) |
| Schemas | `spec-schema.json` (159 lines) | Add optional `partOf`, `relatedSpecs`, `specDependencies` — not in `required` array |
| Schemas | `index-schema.json` | Add optional `partOf` to index entry |
| Templates | `core/templates/feature-requirements.md` | Insert Dependencies & Blockers after "Constraints & Assumptions" (line 44) |
| Templates | `core/templates/design.md` | Insert after "Risks & Mitigations" (line 103) |
| Templates | `core/templates/bugfix.md` | Insert after "Impact Assessment" (line 26) |
| Templates | `core/templates/refactor.md` | Insert after "Scope & Boundaries" (line 29) |
| Templates | `core/templates/tasks.md` | Insert Spec-Level Dependencies before "Task Breakdown" (line 3) |
| Generator | `generator/generate.py` | Context dict (~line 363): add `"decomposition"` and `"initiative_orchestration"` mappings |
| Generator | `generator/templates/*.j2` | Add `{{ decomposition }}` and `{{ initiative_orchestration }}` after `{{ dependency_safety }}` |
| Validator | `generator/validate.py` | Add `DECOMPOSITION_MARKERS` constant; add to BOTH `validate_platform()` (~line 611) AND cross-platform consistency loop (line 1121) |
| Mode manifest | `core/mode-manifest.json` | Add `initiative` mode (4 modules), add `decomposition` to spec/view/audit/from-plan modes |
| Reconciliation | `core/reconciliation.md` | Add Check 6: Dependency Health |
| View | `core/view.md` | Initiative-grouped list, initiative view/list commands |
| Task tracking | `core/task-tracking.md` | Spec-level dependency conformance rule |
| Config | `core/config-handling.md` | `initiatives/` directory, `partOf` in index, `delegationThreshold` config |
| Task delegation | `core/task-delegation.md` | Lower threshold from 6 to 4, add configurable `delegationThreshold` |

### Existing Patterns to Follow

- **Sub-step notation** (e.g., step 9.5, step 1.5) to avoid renumbering existing steps
- **Abstract operations only** in core modules: `READ_FILE`, `WRITE_FILE`, `RUN_COMMAND`, `NOTIFY_USER`, `ASK_USER`, `GET_SPECOPS_VERSION`
- **Gap 31 enforcement**: `*_MARKERS` constants must be added to BOTH `validate_platform()` AND the cross-platform consistency loop in the same commit
- **`additionalProperties: false`** on all JSON schema objects, `maxLength` on strings, `maxItems` on arrays
- **EARS patterns** as HTML comments in templates (invisible in rendered markdown, visible to LLMs)
- **Existing marker pattern**: `TASK_TRACKING_MARKERS` (line 107), `DEPENDENCY_SAFETY_MARKERS` (line 353) — follow same structure

### Architecture Decisions (Pre-confirmed)

1. Always-on scope assessment — no config flag (feedback: config flags without deterministic workflow instructions are dead features)
2. Two modules: `core/decomposition.md` (algorithm) + `core/initiative-orchestration.md` (execution) — orchestrator works with manually-created initiatives too
3. Propose-only decomposition — agent recommends, user decides
4. File-based state — orchestrator reads all state from disk, can resume at any point
5. Fresh context per phase — Phase 1+2 together, Phase 3 fresh sub-agent, Phase 4 fresh sub-agent
6. Task delegation threshold lowered from 6 to 4, configurable via `delegationThreshold`

### Risk Factors

- 25 tasks across 6 groups — largest SpecOps spec to date
- Cross-cutting changes: 2 new core modules, 3 schema changes, 8 core module updates, 5 template changes, 4 generator changes, 3 test files, 20+ doc files
- Generator pipeline must stay green throughout — regenerate after each core/template change
- Pre-commit hook enforces: JSON syntax, stale generated files, stale checksums, markdown lint

## Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Added `initiative.md` to EXPECTED_CLAUDE_MODES in test_build.py | Build test had hardcoded list of 13 modes; new initiative mode made it 14 | 2026-03-22 |
| 2 | Updated validate.py mode count from 13 to 14 | Generator checks mode count against mode-manifest.json; new initiative mode added | 2026-03-22 |

## Deviations from Spec

| # | Deviation | Reason | Impact |
|---|-----------|--------|--------|
| — | — | — | — |

## Documentation Review

All documentation updated as part of the implementation:
- `docs/COMMANDS.md` — initiative commands and decomposition workflow
- `docs/REFERENCE.md` — spec directory structure with initiatives
- `docs/STRUCTURE.md` — file layout, initiative schema, flat file format
- `QUICKSTART.md` — initiative directory tree example
- `CHANGELOG.md` — v1.5.0 features
- `CONTRIBUTING.md` — core module addition guidelines
- `CLAUDE.md` — updated mode count, module list, validation pipeline
- `SECURITY.md` — initiative ID path construction security scope
- `docs/SECURITY-AUDIT.md` — decomposition feature audit notes

## Session Log

| Session | Date | Tasks Worked | Outcome |
|---------|------|-------------|---------|
| 1 | 2026-03-22 | Tasks 1-5 (Group 1: Data Model) | All completed — core/decomposition.md, core/initiative-orchestration.md, spec-schema.json, initiative-schema.json, index-schema.json |
| 2 | 2026-03-22 | Tasks 6-13 (Group 2: Core Integration) | All completed — workflow.md, dispatcher.md, task-delegation.md, 5 templates, reconciliation.md, view.md, task-tracking.md, config-handling.md |
| 3 | 2026-03-22 | Tasks 14-17 (Group 3: Generator Pipeline) | All completed — generate.py, 4 .j2 templates, mode-manifest.json, validate.py |
| 4 | 2026-03-22 | Tasks 18-20 (Group 4: Tests) | All completed — test_spec_schema.py (22 new tests), test_initiative_schema.py (27 tests, new), test_platform_consistency.py |
| 5 | 2026-03-22 | Tasks 21-23 (Group 5: Documentation) | All completed — 4 Tier 1 docs, 13 Tier 2 docs, 3 Tier 3 docs |
| 6 | 2026-03-22 | Tasks 24-25 (Group 6: Finalization) | All completed — regenerate, validate, test suite (8/8 pass), version bump to 1.5.0, checksums |
