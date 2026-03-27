---
name: "Project Structure"
description: "Three-layer architecture, key directories, and module boundaries"
inclusion: always
---

## Directory Layout
- **`core/`** — Platform-agnostic source of truth. Contains workflow, safety, config-handling, steering, templates, verticals, and all other modules. Uses abstract operations (`READ_FILE`, `WRITE_FILE`, etc.) that get substituted during generation.
- **`platforms/`** — Platform-specific adapters. Each platform (claude, cursor, codex, copilot, antigravity) has a `platform.json` (tool mappings, capabilities, version) and generated output files.
- **`generator/`** — Build system. `generate.py` assembles platform outputs from core modules + platform adapters. `validate.py` checks generated outputs. `templates/*.j2` are Jinja2 templates per platform.
- **`.specops/`** — Dogfood specs (this project uses SpecOps to build itself). Contains completed specs, steering files, and `index.json`.
- **`tests/`** — Test suite: schema validation, platform consistency, build system tests.
- **`examples/`** — Example `.specops.json` configuration files (minimal, standard, full, review, builder).
- **`internal/`** — Dogfood playbook, friction log, gap analysis (not published to users).

## Key Files
- `core/workflow.md` — Defines the 4-phase lifecycle (Understand, Spec, Implement, Complete)
- `core/safety.md` — Security guardrails (convention sanitization, template safety, path containment)
- `core/steering.md` — Steering files system (persistent project context)
- `schema.json` — Single source of truth for `.specops.json` validation
- `generator/generate.py` — Build pipeline that produces all platform outputs

## Module Boundaries
- **Core modules** use abstract operations only — never platform-specific tool names
- **Platform adapters** map abstractions to platform tools via `toolMapping` in `platform.json`
- **Generated files** are checked into git (users never run the generator) — CI validates they're not stale
- **The generator** is the only bridge between core and platforms — it loads, renders, substitutes, and writes
