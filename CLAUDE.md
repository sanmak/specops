# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpecOps is a multi-platform spec-driven development workflow system inspired by [Kiro](https://kiro.dev). It provides a `/specops` slash command (and equivalents for other AI coding assistants) that transforms ideas into structured specifications (requirements, design, tasks) before implementation begins.

**Repository**: https://github.com/sanmak/specops.git

## Key Commands

```bash
# Regenerate all platform outputs after changing core/ or generator/
python3 generator/generate.py --all

# Regenerate for a single platform
python3 generator/generate.py --platform claude

# Validate generated outputs (safety rules, templates, no raw abstract ops)
python3 generator/validate.py

# Lint shell scripts
shellcheck setup.sh verify.sh scripts/bump-version.sh scripts/run-tests.sh scripts/remote-install.sh scripts/install-hooks.sh platforms/*/install.sh hooks/pre-commit hooks/pre-push

# Install git hooks (run once after cloning)
bash scripts/install-hooks.sh

# Run all tests (unified runner, auto-installs jsonschema if missing)
bash scripts/run-tests.sh

# Run individual tests
python3 tests/test_schema_validation.py      # example configs vs schema.json
python3 tests/test_schema_constraints.py     # schema rejects invalid inputs
python3 tests/check_schema_sync.py           # schema parity across platforms
python3 tests/test_platform_consistency.py   # all platform outputs are consistent
python3 tests/test_build.py                  # generator system produces valid outputs
python3 tests/test_spec_schema.py            # spec.json/index.json schema validation

# Run installation verification
bash verify.sh

# Bump version
bash scripts/bump-version.sh 1.2.0
bash scripts/bump-version.sh 1.2.0 --checksums  # also regenerate checksums
```

**Dependencies**: `pip install jsonschema` (tests) and `pip install jinja2` (generator). The `scripts/run-tests.sh` runner auto-installs `jsonschema` if missing.

## Custom Slash Commands

Project-local Claude Code commands in `.claude/commands/` for git workflow automation:

| Command | Description |
|---------|-------------|
| `/commit` | Auto-stage all changes, regenerate derived files if needed, commit with conventional message (no Claude attribution) |
| `/push` | Validate pre-push checks, push to remote |
| `/ship` | Combined commit + push in one operation |
| `/release` | Full release workflow: auto-generate CHANGELOG, bump version, validate, commit, push, and create GitHub Release |
| `/monitor` | Monitor GitHub Actions CI status, diagnose failures, auto-fix and re-push (up to 3 cycles) |
| `/docs-sync` | Detect stale documentation after code changes, propose targeted updates for approval |

These commands enforce project conventions automatically: conventional commit prefixes (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`), sensitive file exclusion, automatic regeneration of platform outputs and checksums when source files change, and pre-commit/pre-push hook compliance (never bypasses hooks).

## Simplicity Principle

SpecOps embeds a simplicity principle throughout: prefer the simplest solution that meets requirements. Specs scale to the task (small features don't get full rollout plans), empty sections are skipped rather than filled with boilerplate, and implementations avoid premature abstractions. Red flags: abstractions used once, error handling for impossible scenarios, configuration for unchanging values, designing for hypothetical futures.

## Architecture

### Three-Layer Design

```
core/           Platform-agnostic source of truth (workflow, safety, templates)
platforms/      Platform-specific adapters + generated output files
generator/      Generates platform outputs from core + platform adapters
```

The `core/` directory defines the workflow, safety rules, templates, and vertical adaptations once. The `generator/generate.py` script assembles platform-specific instruction files by:
1. Loading all `core/*.md` modules (workflow, safety, config-handling, verticals, simplicity, data-handling, error-handling, custom-templates, view, and spec templates from `core/templates/`)
2. Loading `platforms/{name}/platform.json` for tool mappings and capabilities
3. Rendering through `generator/templates/{name}.j2` Jinja2-style templates
4. Substituting abstract tool operations (e.g., `READ_FILE`) with platform-specific language from each platform's `toolMapping`
5. Writing output to `platforms/{name}/`

**Generated files are checked into git** so end users never need to run the build.

### Tool Abstraction

`core/` files use abstract operations (`READ_FILE`, `WRITE_FILE`, `EDIT_FILE`, `LIST_DIR`, `FILE_EXISTS`, `RUN_COMMAND`, `ASK_USER`, `NOTIFY_USER`, `UPDATE_PROGRESS`) defined in `core/tool-abstraction.md`. Each platform's `platform.json` provides a `toolMapping` that translates these into platform-specific language. The generator performs this substitution during build.

### Platform Capabilities

Each `platform.json` declares capability flags (`canExecuteCode`, `canEditFiles`, `canCreateFiles`, `canAskInteractive`, `canTrackProgress`, `canAccessGit`). These affect generated behavior — e.g., platforms with `canAskInteractive: false` (Codex) note assumptions instead of asking, platforms with `canTrackProgress: false` (Cursor, Codex, Copilot) track progress in `tasks.md` instead of a built-in todo system.

### Platform Outputs (generated — do NOT edit directly)

| Platform | Generated File | Entry Point |
|----------|---------------|-------------|
| Claude Code | `platforms/claude/SKILL.md` | `/specops`, `/specops view`, `/specops list` |
| Cursor | `platforms/cursor/specops.mdc` | `Use specops to ...`, `View the ... spec`, `List all specops specs` |
| OpenAI Codex | `platforms/codex/SKILL.md` | `Use specops to ...`, `View the ... spec`, `List all specops specs` |
| GitHub Copilot | `platforms/copilot/specops.instructions.md` | `Use specops to ...`, `View the ... spec`, `List all specops specs` |

### Plugin Distribution

SpecOps is distributed as a Claude Code plugin via `.claude-plugin/` at the repo root. Users install with:
```
/plugin marketplace add sanmak/specops
/plugin install specops@specops-marketplace
```

The plugin provides one skill:
- `/specops` — spec-driven development workflow with subcommands: `init`, `view`, `list`, `interview` (from `skills/specops/SKILL.md`)

Plugin manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) are **generated** by `generator/generate.py` — do not edit directly. Version is synced from `platforms/claude/platform.json`.

### Skills Directory

`skills/specops/` is generated by the build system and used for plugin discovery. The canonical source is in `platforms/claude/`. Both locations are kept in sync by the generator.

## Editing Guidelines

- **Never edit generated platform output files directly** (`SKILL.md`, `specops.mdc`, `specops.instructions.md`). Edit `core/` modules or `generator/templates/*.j2` instead, then regenerate with `python3 generator/generate.py --all`.
- **`core/` must remain platform-agnostic** — use abstract operations from `core/tool-abstraction.md` (e.g., `READ_FILE`, `WRITE_FILE`), never platform-specific tool names.
- **Preserve the 4-phase workflow structure** in `core/workflow.md`: Understand → Spec → Implement → Complete.
- **Preserve the Simplicity Principle** in `core/simplicity.md` and all safety mechanisms in `core/safety.md`.
- **`schema.json`** is the single source of truth for `.specops.json` configuration validation. Run `python3 tests/check_schema_sync.py` to verify it is well-formed.
- **All JSON schema objects** must use `"additionalProperties": false`, strings must have `maxLength`, arrays must have `maxItems`.
- **Shell scripts** must pass ShellCheck without warnings, use `set -e`, and quote all variable expansions.

### Security-Sensitive Files

These files require extra scrutiny when modified — they can alter agent behavior, security guardrails, or configuration validation: `core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `schema.json`, `spec-schema.json`, `platforms/claude/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `setup.sh`, `scripts/remote-install.sh`, `generator/generate.py`, `hooks/pre-commit`, `hooks/pre-push`.

## What to Do After Changes

| What you changed | Required follow-up |
|---|---|
| `core/*.md` or `core/templates/*.md` | `python3 generator/generate.py --all` then `python3 generator/validate.py` |
| `generator/templates/*.j2` | `python3 generator/generate.py --all` then `python3 generator/validate.py` |
| `platforms/{name}/platform.json` | `python3 generator/generate.py --platform {name}` then `python3 generator/validate.py` |
| `schema.json` | Run `python3 tests/check_schema_sync.py` to verify schema is well-formed |
| Shell scripts | Run `shellcheck` on modified scripts |
| `hooks/*` | Run `shellcheck hooks/pre-commit hooks/pre-push` |
| Security-sensitive files | Consider running `/security-review` before pushing |

## Commit Conventions

Prefix commits: `feat:` (new feature/platform), `fix:` (bug fix), `chore:` (version bumps, CI, deps), `docs:` (documentation only), `test:` (test additions/fixes), `refactor:` (no behavior change).

## CI Notes

CI verifies generated files aren't stale — after regenerating, the diff of `platforms/`, `skills/`, and `.claude-plugin/` must be committed. The `build-platforms` job runs `git diff --exit-code` and fails if generated outputs don't match what's checked in.

## Checksums

`CHECKSUMS.sha256` contains SHA-256 hashes of critical files (SKILL.md, platform.json, workflow.md, safety.md). These are verified in CI. Regenerate with `bash scripts/bump-version.sh <version> --checksums`.

## Validation

`python3 generator/validate.py` checks all generated platform outputs for:
- **No raw abstract operations** — ensures `READ_FILE(`, `WRITE_FILE(` etc. were properly substituted
- **Safety markers present** — convention sanitization, template safety, path containment rules
- **Template markers present** — all spec templates (feature-requirements, bugfix, refactor, design, tasks, implementation)
- **Workflow markers present** — all four phases documented
- **Review markers present** — spec.json, reviews.md, review mode, revision mode, implementation gate, status dashboard
- **View markers present** — spec viewing, view/list mode detection, list specs, summary/full/walkthrough/status views
- **Vertical markers present** — all vertical adaptation rules included
- **Format-specific rules** — e.g., Cursor `.mdc` files must have YAML frontmatter with `description`, Claude/Codex `SKILL.md` must have `name` and `description` in frontmatter, Copilot `specops.instructions.md` must have `applyTo` in frontmatter
- **Plugin manifests** — `.claude-plugin/plugin.json` and `marketplace.json` exist, valid JSON, required fields present, version consistency with `platform.json`
- **Init mode** — init config templates and workflow markers present within Claude `SKILL.md`

## Configuration

The SpecOps agent reads `.specops.json` from the target project (not this repo). Configuration is validated against `schema.json`. Example configs live in `examples/` (`.specops.json`, `.specops.minimal.json`, `.specops.full.json`).

## Adding a New Platform

1. Create `platforms/{name}/platform.json` with capabilities and tool mapping
2. Create `generator/templates/{name}.j2` with the platform's instruction format
3. Add the platform to `SUPPORTED_PLATFORMS` in `generator/generate.py`
4. Create `platforms/{name}/install.sh`
5. Run `python3 generator/generate.py --platform {name}`
6. Add to `generator/validate.py` and `tests/test_platform_consistency.py`

## Release Process

Releases are automated via GitHub Actions (`release.yml`). Create a tag (e.g., `v1.1.0`) through GitHub's Releases UI — the workflow extracts the version, updates all JSON files, regenerates checksums, and pushes to `main`. For manual version bumps during development, use `bash scripts/bump-version.sh`.
