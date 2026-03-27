# Product Requirements: Add Google Antigravity as 5th Platform

## Overview

Google Antigravity is an agent-first IDE (announced Nov 2025 alongside Gemini 3) with multi-agent orchestration, rules-based instruction system, and broad model support. SpecOps currently supports 4 platforms (Claude, Cursor, Codex, Copilot). Adding Antigravity as a 5th platform extends SpecOps's multi-platform moat and brings support to a new category of agent-first IDEs.

## Product Requirements

<!-- EARS: WHEN Google Antigravity is available as an AI coding platform, THE SYSTEM SHALL support it as a 5th platform alongside Claude, Cursor, Codex, and Copilot. -->

### PR-1: Antigravity Platform Adapter

As a [role not specified], I want SpecOps to support Google Antigravity as a platform so that [benefit not specified].

**Acceptance Criteria:**

- [ ] <!-- EARS: WHEN a user runs the generator for the antigravity platform, THE SYSTEM SHALL produce a `specops.md` output file from the Jinja2 template and platform adapter. --> A `platforms/antigravity/platform.json` adapter exists with correct tool mappings, capabilities, and install location
- [ ] <!-- EARS: WHEN the antigravity platform output is generated, THE SYSTEM SHALL substitute all abstract operations with natural language tool invocations. --> Generated `platforms/antigravity/specops.md` contains no raw abstract operations (READ_FILE, WRITE_FILE, etc.)
- [ ] <!-- EARS: WHEN the antigravity platform output is generated, THE SYSTEM SHALL use an HTML comment for version embedding instead of YAML frontmatter. --> Version is embedded as `<!-- specops-version: "X.Y.Z" -->` (no YAML frontmatter)
- [ ] <!-- EARS: WHEN the platform adapter specifies capabilities, THE SYSTEM SHALL set `canDelegateTask: true` to support Antigravity's Manager View multi-agent orchestration. --> `canDelegateTask` is set to `true` in the platform adapter

### PR-2: Build System Integration

As a [role not specified], I want the generator, validator, and test suite to include Antigravity so that [benefit not specified].

**Acceptance Criteria:**

- [ ] <!-- EARS: WHEN `python3 generator/generate.py --all` is run, THE SYSTEM SHALL generate output for all 5 platforms including antigravity. --> `generate.py` includes `antigravity` in `SUPPORTED_PLATFORMS` and generates output
- [ ] <!-- EARS: WHEN `python3 generator/validate.py` is run, THE SYSTEM SHALL validate the antigravity output with 200+ checks. --> `validate.py` validates `antigravity` platform output including version comment check
- [ ] <!-- EARS: WHEN `bash scripts/run-tests.sh` is run, THE SYSTEM SHALL include antigravity in all platform consistency and build tests. --> `test_build.py` and `test_platform_consistency.py` include antigravity in their platform maps

### PR-3: Installation Support

As a [role not specified], I want to install SpecOps for Antigravity using the standard install scripts so that [benefit not specified].

**Acceptance Criteria:**

- [ ] <!-- EARS: WHEN a user runs `platforms/antigravity/install.sh`, THE SYSTEM SHALL install `specops.md` to `.agents/rules/specops.md` in the target project. --> Platform-specific `install.sh` installs to `.agents/rules/specops.md`
- [ ] <!-- EARS: WHEN a user runs `setup.sh`, THE SYSTEM SHALL detect Antigravity and offer it as a platform option. --> `setup.sh` detects Antigravity (via `antigravity` command or `/Applications/Antigravity.app`)
- [ ] <!-- EARS: WHEN a user runs `scripts/remote-install.sh` for antigravity, THE SYSTEM SHALL install the platform correctly. --> `remote-install.sh` supports the `antigravity` platform

### PR-4: Infrastructure and CI Integration

As a [role not specified], I want Antigravity platform files included in version bumping, verification, pre-commit hooks, checksums, and CI so that [benefit not specified].

**Acceptance Criteria:**

- [ ] <!-- EARS: WHEN `scripts/bump-version.sh` is run, THE SYSTEM SHALL update the version in `platforms/antigravity/platform.json`. --> `bump-version.sh` includes `platforms/antigravity/platform.json`
- [ ] <!-- EARS: WHEN `verify.sh` is run, THE SYSTEM SHALL check for antigravity template, platform loop, and generated output. --> `verify.sh` validates antigravity artifacts
- [ ] <!-- EARS: WHEN files are committed, THE SYSTEM SHALL check antigravity generated files and checksums via the pre-commit hook. --> `hooks/pre-commit` includes antigravity files
- [ ] <!-- EARS: WHEN CI runs, THE SYSTEM SHALL lint `platforms/antigravity/platform.json` for JSON syntax and `platforms/antigravity/install.sh` with ShellCheck. --> `.github/workflows/ci.yml` includes antigravity checks

## Product Quality Attributes

- **Consistency**: Antigravity output must pass the same 200+ validation checks as other platforms
- **No abstract operation leakage**: Generated output must contain zero raw abstract operations
- **Cross-platform parity**: All workflow phases, safety rules, templates, and vertical adaptations must be present in the antigravity output

## Scope Boundary

**Ships in v1:**
- Platform adapter (`platform.json`)
- Jinja2 template (`antigravity.j2`)
- Generated output (`specops.md`)
- Generator, validator, test integration
- Install scripts (`install.sh`, `setup.sh`, `remote-install.sh`)
- Infrastructure files (bump-version, verify, pre-commit, checksums, CI)
- Documentation updates

**Deferred:**
- Antigravity-specific multi-agent orchestration features beyond `canDelegateTask: true`
- Manager View-specific workflow optimizations
- Antigravity marketplace/plugin distribution
- Antigravity-specific steering file integration

## Constraints

[To be defined]

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
