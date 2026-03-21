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
- **Test suite** (`scripts/run-tests.sh`): 8 tests covering schema validation, schema constraints, schema sync, platform consistency, build system, spec schema, and spec artifact lint
- **Validator** (`generator/validate.py`): Checks all generated outputs for abstract operation substitution, 28+ marker categories (safety, workflow, template, engineering discipline, memory, steering, etc.), cross-platform consistency, and platform-specific format rules
- **Checksums** (`CHECKSUMS.sha256`): SHA-256 hashes of critical files verified in CI
