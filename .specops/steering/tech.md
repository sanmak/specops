---
name: "Technology Stack"
description: "Languages, frameworks, tools, and build system"
inclusion: always
---

## Core Stack
- **Python 3**: Generator build system (`generator/generate.py`, `generator/validate.py`)
- **Jinja2**: Templating engine for platform-specific output generation
- **JSON Schema**: Configuration validation (`schema.json`, `spec-schema.json`)
- **Markdown**: All core modules, spec templates, and steering files are plain markdown

## Development Tools
- **ShellCheck**: Linting for all shell scripts (`setup.sh`, `verify.sh`, `hooks/*`, `scripts/*`)
- **Git hooks**: Pre-commit (validates generated files aren't stale, runs ShellCheck) and pre-push (runs full test suite and validation)
- **GitHub Actions**: CI verifies generated outputs match source, runs tests, validates checksums

## Quality & Testing
- **Test suite** (`scripts/run-tests.sh`): 7 tests covering schema validation, schema constraints, schema sync, platform consistency, build system, and spec schema
- **Validator** (`generator/validate.py`): Checks all generated outputs for abstract operation substitution, safety markers, template markers, workflow markers, steering markers, and platform-specific format rules
- **Checksums** (`CHECKSUMS.sha256`): SHA-256 hashes of critical files verified in CI
