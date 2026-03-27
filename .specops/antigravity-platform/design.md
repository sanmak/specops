# Product Module Design: Add Google Antigravity as 5th Platform

## Overview

This design adds Google Antigravity as the 5th supported platform in SpecOps's multi-platform generation system. The implementation follows the established three-tier architecture: a platform adapter (`platform.json`), a Jinja2 template (`antigravity.j2`), and generated output (`specops.md`).

## Architecture Decisions

### AD-1: Output file is `specops.md` installed to `.agents/rules/specops.md`

**Decision**: Install the generated file as `.agents/rules/specops.md` rather than `GEMINI.md` or `AGENTS.md`.

**Rationale**: Avoids conflicting with user's own `GEMINI.md`/`AGENTS.md` files. Follows the workspace rules convention that Antigravity supports via the `.agents/rules/` directory.

### AD-2: Single-file pattern (not dispatcher + modes)

**Decision**: Use a single monolithic output file like Cursor, Copilot, and Codex -- not the dispatcher + mode files pattern used by Claude.

**Rationale**: Antigravity does not have a native slash command system for rules. The single-file pattern is appropriate for keyword-based trigger platforms.

### AD-3: No YAML frontmatter -- version as HTML comment

**Decision**: Embed version as `<!-- specops-version: "X.Y.Z" -->` instead of YAML frontmatter.

**Rationale**: Antigravity rules are plain markdown with no frontmatter support (unlike Cursor/Codex/Copilot which use YAML frontmatter). Version information must still be machine-readable for `GET_SPECOPS_VERSION` to work.

### AD-4: Keyword-based entry point

**Decision**: Use the same keyword-based entry point pattern as Cursor, Copilot, and Codex.

**Rationale**: Antigravity has no native slash command system for rules. Keyword triggers are the standard approach for non-Claude platforms.

### AD-5: `canDelegateTask: true`

**Decision**: Enable task delegation capability in the platform adapter.

**Rationale**: Antigravity's Manager View supports multi-agent orchestration, making it the second platform (after Claude) with delegation support. This is unique among non-Claude platforms.

### AD-6: Generic natural language tool mappings

**Decision**: Use the same generic natural language tool mappings as Cursor, Copilot, and Codex (e.g., "Read the file at", "Create the file at").

**Rationale**: Antigravity does not have platform-specific tool APIs that require custom mappings.

## Product Module Design

### Platform Adapter (`platforms/antigravity/platform.json`)

- `instructionFormat: "agents_rules"` -- new format type for Antigravity
- `installLocation.project: ".agents/rules/specops.md"` -- workspace rules location
- `canDelegateTask: true` -- unique among non-Claude platforms
- Tool mappings: generic natural language (same as Cursor/Copilot)
- `GET_SPECOPS_VERSION`: greps version from `.agents/rules/specops.md` HTML comment

### Jinja2 Template (`generator/templates/antigravity.j2`)

- Based on `copilot.j2` structure (all 30+ module variables)
- No frontmatter section -- generator prepends HTML comment version marker
- Includes Antigravity-specific note about Manager View for task delegation

### Generator Integration (`generator/generate.py`)

- Add `"antigravity"` to `SUPPORTED_PLATFORMS`
- New `generate_antigravity()` function: loads template, renders, substitutes tools, prepends version comment, writes output
- Register in `GENERATORS` dict

### Validator Integration (`generator/validate.py`)

- Add `"antigravity": "specops.md"` to `get_generated_files()`
- Add platform-specific validation: check for version HTML comment instead of YAML frontmatter

### Test Integration

- `test_build.py`: add to `EXPECTED_OUTPUTS`
- `test_platform_consistency.py`: add to `PLATFORM_FILES`

## Integration Points

### Install Scripts
- `platforms/antigravity/install.sh`: Modeled after `platforms/cursor/install.sh`, installs to `.agents/rules/specops.md`
- `setup.sh`: Detect via `antigravity` command or `/Applications/Antigravity.app`
- `scripts/remote-install.sh`: Add `antigravity` to valid platform cases

### Infrastructure
- `scripts/bump-version.sh`: Add `platforms/antigravity/platform.json` to `FILES` array
- `verify.sh`: Add antigravity template check, platform loop inclusion, generated output check
- `hooks/pre-commit`: Add `platforms/antigravity/specops.md` to `GENERATED_FILES` and `CHECKSUMMED_FILES`
- `CHECKSUMS.sha256`: Add hashes for `platforms/antigravity/specops.md` and `platforms/antigravity/platform.json`
- `.github/workflows/ci.yml`: Add JSON syntax check and ShellCheck for antigravity files

### Documentation
- Update platform count references from 4 to 5 across CLAUDE.md, README.md, QUICKSTART.md, docs/STRUCTURE.md, CONTRIBUTING.md
- Add Antigravity to platform lists and install examples
- Update steering files (structure.md, product.md)

## System Flow

1. Developer creates/edits `platforms/antigravity/platform.json` (adapter)
2. Developer creates/edits `generator/templates/antigravity.j2` (template)
3. `python3 generator/generate.py --all` reads adapter + template, substitutes abstract ops with tool mappings, prepends version comment, writes `platforms/antigravity/specops.md`
4. `python3 generator/validate.py` checks the output for marker presence, abstract op absence, and format compliance
5. User runs `bash platforms/antigravity/install.sh /path/to/project` to install into their Antigravity workspace
6. Antigravity IDE loads `.agents/rules/specops.md` as workspace rules

## Ship Plan

1. Create platform adapter and template (foundation)
2. Integrate into generator and verify output generation
3. Integrate into validator and verify all checks pass
4. Update tests and verify test suite passes
5. Create install script and platform README
6. Update infrastructure files (bump-version, verify, pre-commit, CI)
7. Update steering files and documentation
8. Regenerate checksums and run full validation
