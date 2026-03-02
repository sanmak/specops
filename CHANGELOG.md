# Changelog

All notable changes to SpecOps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Spec viewing**: `view <spec-name>` with 5 view modes — summary (default), full, section-specific, walkthrough, and status
- **Spec listing**: `list` command for overview dashboard of all specs with status, type, author, and progress
- **View combinations**: view multiple sections together (e.g., `view auth-feature requirements design`)
- **Interactive walkthrough**: guided section-by-section tour with AI commentary (falls back to annotated full view on non-interactive platforms)
- **Collaborative spec review workflow**: structured team review with approval gates
- `team.specReview` configuration (`enabled`, `minApprovals`) for team review workflow
- `spec.json` per-spec metadata file (always created) tracking lifecycle status, author, reviewers, approvals
- `index.json` auto-generated global spec index for quick dashboard lookups
- `reviews.md` structured review feedback organized by review rounds
- Review mode auto-detection via git email comparison with spec author
- Revision mode for addressing reviewer feedback and resubmitting
- Implementation gate blocking Phase 3 until required approvals are met
- Spec lifecycle: draft → in-review → approved → implementing → completed
- Status dashboard (`/specops status`) for team visibility into all active specs
- `spec-schema.json` and `index-schema.json` for validating metadata files
- `assets/review-workflow.svg` diagram for the review process
- Platform-specific review behavior documentation in TEAM_GUIDE.md
- Review safety rules in core/safety.md
- Example review-enabled config (`examples/.specops.review.json`)
- Example spec.json and reviews.md in feature-user-authentication example

## [1.0.0] - 2026-02-28

### Added

- **Multi-platform support**: SpecOps works with Claude Code, Cursor, OpenAI Codex, and GitHub Copilot
- **Core module architecture**: Platform-agnostic workflow, templates, and safety rules in `core/` directory
- **Build system**: `generator/generate.py` assembles platform-specific instruction files from core modules + platform adapters
- **Platform adapters**: `platforms/claude/`, `platforms/cursor/`, `platforms/codex/`, `platforms/copilot/` with per-platform configuration, installers, and READMEs
- **Tool abstraction layer**: `core/tool-abstraction.md` defines abstract operations mapped to each platform's tools
- **Vertical support**: `vertical` configuration field with 6 options: `backend`, `frontend`, `fullstack`, `infrastructure`, `data`, `library`
- **Auto-detection**: Agent infers vertical from request keywords and codebase analysis when not configured
- **Vertical adaptation rules**: Default templates adapt per vertical (section renaming, skipping, domain vocabulary)
- **Extended custom templates**: Custom template loading supports `design.md` and `tasks.md`
- **Template variables**: `{{vertical}}` available in custom template substitution
- **Example templates**: 5 vertical-specific templates in `examples/templates/`
- **Security policy**: `SECURITY.md` with vulnerability reporting, response timelines, trust model, and severity classification
- **Contributing guidelines**: `CONTRIBUTING.md` with PR workflow, review requirements, and security-sensitive change guidance
- **Software Bill of Materials**: `SBOM.md` documenting zero-dependency runtime
- **File integrity verification**: `CHECKSUMS.sha256` with SHA-256 checksums for installed files
- **CI/CD pipeline**: `.github/workflows/ci.yml` with JSON validation, schema validation, schema sync check, ShellCheck, and verify.sh jobs
- **Automated version management**: `.github/workflows/release.yml` bumps version across all files when a GitHub Release is published
- **Test suite**: `tests/` directory with schema validation, schema constraints, schema sync, platform consistency, and build tests
- **Configuration safety**: Convention sanitization (prompt injection defense), template file safety, path containment, and config conflict detection
- **Data handling**: Secrets exclusion, PII redaction, data classification awareness, and spec sensitivity notices
- **Schema hardening**: `pattern` on `specsDir`, `maxLength` on all string fields, `maxItems` on arrays, `additionalProperties: false` on all objects
- **Universal installer**: `setup.sh` detects installed AI tools and installs SpecOps for selected platforms
- **Platform consistency tests**: `tests/test_platform_consistency.py` verifies all platforms have identical workflow/safety content
- **Build tests**: `tests/test_build.py` validates the generation pipeline
- **Spec-driven development workflow**: `/specops` command with 4-phase workflow (Understand, Spec, Implement, Complete)
- **Three-file spec structure**: requirements.md, design.md, tasks.md
- **`.specops.json` configuration system**: specsDir, templates, team conventions, implementation settings
- **Support for feature development, bug fixes, and refactoring**
- **Team collaboration**: configurable conventions, review required mode, task tracking (GitHub, Jira, Linear)
- **Implementation features**: auto-commit, auto-create PR, configurable testing strategy
- **Custom template support**: load templates from `<specsDir>/templates/` with `{{variable}}` substitution
- **Simplicity Principle**: specs and implementations scale to task complexity
- **Optional `implementation.md`**: tracking decisions, deviations, and blockers
- **Example configurations**: minimal, standard, full

### Configuration Schema

- `specsDir` - Configurable location for spec files
- `vertical` - Project vertical for template adaptation
- `templates` - Custom templates for different spec types (feature, bugfix, refactor, design, tasks)
- `team.conventions` - Team-specific development conventions
- `team.reviewRequired` - Require approval before implementation
- `team.taskTracking` - Integration with task tracking tools (github, jira, linear)
- `team.codeReview` - Code review requirements (required, minApprovals, requireTests, requireDocs)
- `implementation.autoCommit` - Automatic commit after tasks
- `implementation.createPR` - Automatic PR creation
- `implementation.testing` - Testing strategy (auto/manual/skip)
- `implementation.testFramework` - Preferred test framework
- `implementation.linting` - Linter configuration (enabled, fixOnSave)
- `implementation.formatting` - Formatter configuration (enabled, tool)
- `modules` - Module-specific configuration for monorepo projects
- `integrations` - External tool integrations (CI, deployment, monitoring, analytics)

### Templates

- Feature requirement template with user stories
- Bug fix template with root cause analysis
- Design document template with architecture decisions
- Task breakdown template with dependencies
- Refactoring template with motivation and migration strategy
- Optional implementation notes template
