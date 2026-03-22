# Contributing to SpecOps

Thank you for your interest in contributing to SpecOps! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Report unacceptable behavior via [GitHub Security Advisories](https://github.com/sanmak/specops/security/advisories/new).

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/sanmak/specops/issues) for bug reports and feature requests
- For security vulnerabilities, see [SECURITY.md](SECURITY.md) instead

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** from `main` (`git checkout -b feature/your-feature`)
3. **Make your changes** following the guidelines below
4. **Test your changes** (see Testing section)
5. **Commit** with a descriptive message
6. **Push** to your fork and open a **Pull Request**

### Pull Request Requirements

- All PRs require at least one review before merge
- CI checks must pass (JSON validation, shellcheck, schema tests)
- PRs should have a clear description of what changed and why

## Development Guidelines

### Shell Scripts (`setup.sh`, `verify.sh`)

- Must pass [ShellCheck](https://www.shellcheck.net/) without warnings
- Use `set -e` for early exit on errors
- Quote all variable expansions (`"$VAR"`, not `$VAR`)
- Use `read -r` to prevent backslash interpretation
- Validate all user input before using in file operations
- Prefer POSIX-compatible constructs where possible

### JSON Files (`schema.json`, example configs)

- Must be valid JSON (validated in CI)
- All nested objects must use `"additionalProperties": false`
- String fields must have `maxLength` constraints
- Array fields must have `maxItems` constraints

### Core Modules (`core/`)

- `core/` is the platform-agnostic source of truth — do NOT use platform-specific tool names here
- Preserve the 4-phase workflow structure: Understand, Spec, Implement, Complete
- Preserve the Simplicity Principle
- Preserve all safety mechanisms (convention sanitization, template safety, path containment)
- Use abstract operations from `core/tool-abstraction.md` (e.g., `READ_FILE`, `WRITE_FILE`)
- After changing core modules, regenerate platform outputs: `python3 generator/generate.py --all`
- When adding a new core module, register it in `generator/generate.py` (add to core reading logic and context dict) and update the relevant Jinja2 templates in `generator/templates/` to include the new template variable. Also update `docs/STRUCTURE.md` with the new module entry, add a mapping to `.claude/commands/docs-sync.md`, and update the CLAUDE.md core modules list
- When adding a new mode, register it in `core/mode-manifest.json` with its required module list

### Validator Guidelines

- When adding `*_MARKERS` constants to `generator/validate.py`, add to **both** `validate_platform()` AND the cross-platform consistency check loop in the **same commit**. This prevents marker validation from passing on one surface while being absent on the other.

### Platform Adapters (`platforms/`)

- Each platform adapter has a `platform.json` defining capabilities and tool mappings
- Generated output files (SKILL.md, specops.mdc, specops.instructions.md) should NOT be edited directly
- Edit `core/` modules or `generator/templates/*.j2` instead, then regenerate
- When adding a new platform, see STRUCTURE.md for the step-by-step guide

### Example Files (`examples/`)

- Example configs must validate against `schema.json`
- Example specs should be realistic and comprehensive
- Do not include real secrets, credentials, or PII in examples

## Security-Sensitive Changes

The following files require extra scrutiny during review:

| File | Risk | Review Focus |
| --- | --- | --- |
| `core/workflow.md` | Agent behavior | Could alter what the agent does autonomously |
| `core/safety.md` | Security guardrails | Must be preserved in all platform outputs |
| `core/review-workflow.md` | Review integrity | Could bypass approval gates |
| `schema.json` | Configuration validation | Could allow unsafe configuration values |
| `platforms/claude/SKILL.md` | Generated skill file | Contains YAML frontmatter and agent instructions |
| `.claude-plugin/plugin.json` | Plugin metadata | Could alter plugin behavior or distribution |
| `setup.sh` | File system operations | Could introduce path traversal or injection |
| `scripts/remote-install.sh` | Remote execution | Runs via curl pipe, extra scrutiny needed |
| `generator/generate.py` | Output generation | Could omit safety rules from generated outputs |
| `hooks/pre-commit`, `hooks/pre-push` | Git hooks | Could skip validation or introduce injection |

Changes to these files should include:

- An explanation of why the change is needed
- Analysis of security implications
- Updated tests if applicable

For PRs that touch these files, consider running Claude Code's `/security-review` command before submitting. See [SECURITY-AUDIT.md](docs/SECURITY-AUDIT.md) for the latest audit results and methodology.

## Testing

Before submitting a PR, verify:

```bash
# Run all tests with a single command
bash scripts/run-tests.sh

# Or run individual checks:

# Validate all JSON files
python3 -c "import json; json.load(open('schema.json'))"

# Regenerate platform outputs (after changing core/ or generator/)
python3 generator/generate.py --all

# Validate generated outputs
python3 generator/validate.py

# Lint shell scripts (requires shellcheck)
shellcheck setup.sh verify.sh scripts/bump-version.sh scripts/run-tests.sh scripts/remote-install.sh scripts/install-hooks.sh platforms/*/install.sh hooks/pre-commit hooks/pre-push

# Run verification
bash verify.sh

# Run test suite
python3 tests/check_schema_sync.py
python3 tests/test_platform_consistency.py
python3 tests/test_build.py
```

## Commit Guidelines

- Write clear, descriptive commit messages
- Reference issue numbers where applicable (e.g., `Fixes #42`)
- Keep commits focused on a single change
- Sign commits when possible (`git commit -S`)

### Commit Message Convention

Prefix commits with a type for clarity in the changelog:

| Prefix | When to use |
| --- | --- |
| `feat:` | New workflow behavior, new platform, new feature |
| `fix:` | Bug fix in generator, validator, or shell scripts |
| `chore:` | Version bumps, dependency updates, CI changes |
| `docs:` | Documentation only |
| `test:` | Test additions or fixes |
| `refactor:` | Code restructuring with no behavior change |

Examples:

- `feat: add Gemini platform adapter`
- `fix: validator false-positive on abstraction section headers`
- `chore: bump version to 1.2.0`
- `docs: clarify specsDir path constraints in REFERENCE.md`

## Release Process

Releases are automated via GitHub Actions. To create a new release:

1. Go to **Releases** on the GitHub repository page
2. Click **Draft a new release**
3. Create a tag matching the target version (e.g., `v1.1.0`)
4. Write release notes describing notable changes
5. Click **Publish release**

The `release.yml` workflow will automatically:

- Extract the version from the tag (stripping the `v` prefix)
- Validate it is valid semver
- Update the version in all JSON files
- Regenerate `CHECKSUMS.sha256`
- Commit and push changes to `main`

For manual version bumping (e.g., during development):

```bash
bash scripts/bump-version.sh 1.2.0
bash scripts/bump-version.sh 1.2.0 --checksums  # also regenerate checksums
```

## Questions?

Open a [GitHub Discussion](https://github.com/sanmak/specops/discussions) or issue for questions about contributing.
