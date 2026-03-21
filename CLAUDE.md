# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is SpecOps

SpecOps is a spec-driven development workflow for AI coding assistants. It transforms ideas into structured specifications (requirements, design, tasks) before implementation, following a 4-phase workflow: Understand → Spec → Implement → Complete. It supports four platforms (Claude Code, Cursor, Codex, Copilot) from a single source of truth.

## Build & Validate Commands

```bash
# Run all tests (single command)
bash scripts/run-tests.sh

# Generate all platform outputs (required after changing core/, generator/templates/, or platform.json)
python3 generator/generate.py --all

# Generate for a single platform
python3 generator/generate.py --platform claude

# Validate generated outputs (200+ checks)
python3 generator/validate.py

# Lint shell scripts
shellcheck setup.sh verify.sh scripts/*.sh platforms/*/install.sh hooks/pre-commit hooks/pre-push

# Lint markdown (core and docs only)
npx markdownlint-cli2 "core/**/*.md" "docs/**/*.md"

# Verify file integrity
shasum -a 256 -c CHECKSUMS.sha256

# Run individual test files
python3 tests/test_build.py
python3 tests/test_platform_consistency.py
python3 tests/test_schema_validation.py    # requires: pip install jsonschema
python3 tests/test_schema_constraints.py
python3 tests/test_spec_schema.py
python3 tests/check_schema_sync.py

# Version bumping
bash scripts/bump-version.sh 1.2.0 --checksums
```

## Three-Tier Architecture

**Tier 1 — Core Modules** (`core/*.md`): Platform-agnostic workflow logic using abstract operations (`READ_FILE`, `WRITE_FILE`, `RUN_COMMAND`, etc. defined in `core/tool-abstraction.md`). Never use platform-specific tool names here.

**Tier 2 — Platform Adapters** (`platforms/<platform>/platform.json`): Maps abstract operations to platform-specific tool invocations (e.g., `READ_FILE` → `Use the Read tool to read(...)` for Claude).

**Tier 3 — Generated Outputs** (`platforms/<platform>/SKILL.md` etc.): Built by `generator/generate.py` using Jinja2 templates (`generator/templates/*.j2`) that combine core modules + platform adapters. **Never edit generated output files directly** — edit `core/` or `generator/templates/` then regenerate.

The generator produces: Claude (`SKILL.md` dispatcher + 13 mode files in `modes/`), Cursor (`specops.mdc`), Codex (`SKILL.md`), Copilot (`specops.instructions.md`).

## Critical Development Rules

- **After changing `core/`, `generator/templates/`, or any `platform.json`**: run `python3 generator/generate.py --all` and commit the regenerated files alongside your changes. The pre-commit hook enforces this.
- **After changing checksummed files** (listed in `CHECKSUMS.sha256`): regenerate checksums and stage `CHECKSUMS.sha256`. The pre-commit hook enforces this.
- **JSON schema objects** must use `additionalProperties: false`. String fields need `maxLength`, arrays need `maxItems`.
- **When adding `*_MARKERS` constants to `validate.py`**: add to both `validate_platform()` AND the cross-platform consistency check loop in the same commit.
- **Commit convention**: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:` prefixes.

## Key Validation Pipeline

`generator/validate.py` checks that generated outputs:

1. Contain no unsubstituted abstract operations (e.g., `READ_FILE(` must not appear)
2. Include all safety markers from `core/safety.md`
3. Include all template markers and workflow markers
4. Meet platform-specific format requirements

The pre-commit hook (`hooks/pre-commit`) runs 7 checks: JSON syntax, ShellCheck, stale generated files, stale checksums, PII/absolute-path detection, spec checkbox staleness, and markdown lint.

## Mode Architecture (Claude Platform)

The Claude platform uses a dispatcher (`platforms/claude/SKILL.md`) that loads one of 13 modes on demand from `platforms/claude/modes/`. The primary mode is `spec` (full 4-phase workflow in `core/workflow.md`). Other modes: init, view, interview, steering, memory, map, audit, pipeline, from-plan, feedback, update, version.

## Testing

Tests use Python's `unittest` module (no external test framework). The `jsonschema` pip package is required for schema validation tests. Run `bash scripts/run-tests.sh` for the full suite with summary output.

## File Relationships to Know

- `skills/specops/` mirrors `platforms/claude/` (symlinks for dev, copies for distribution)
- `.claude-plugin/` contains plugin marketplace metadata (also generated)
- `.specops/` contains this project's own specs (dogfood) — not part of the distributed tool
- `core/templates/` holds spec document templates (requirements, bugfix, design, tasks, etc.)
- `generator/templates/` holds Jinja2 build templates (different purpose than core/templates)
