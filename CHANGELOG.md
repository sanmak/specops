# Changelog

All notable changes to SpecOps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Self-review workflow for solo developers**: New `allowSelfApproval` config option in `team.specReview` enables solo developers to review and approve their own specs. Authors go through the full review ritual (read spec, provide feedback, self-approve) with results recorded in `reviews.md` as a self-review
- **`self-approved` spec status**: Distinct from peer `approved` — both allow implementation, but `self-approved` provides audit trail showing no peer review was performed. Reviewer entries include `selfApproval: true` flag
- **Init-time solo/team detection**: `/specops init` now asks "Are you working solo or with a team?" when a review-enabled template is selected, and pre-configures `allowSelfApproval` accordingly
- **Deterministic mode detection**: Review workflow mode detection is now a fully exhaustive decision tree — every combination of inputs maps to exactly one mode with no gaps
- **spec.json validation on read**: Invalid or corrupt `spec.json` files now fall back to legacy mode with a warning instead of undefined behavior
- **Solo review example config**: `examples/.specops.solo-review.json` for solo developers who want the review workflow
- **Self-approved example spec**: `examples/specs/feature-self-approved-example/spec.json`
- **Version tracking in specs**: `specopsCreatedWith` and `specopsUpdatedWith` fields in `spec.json` record which SpecOps version created and last modified each spec
- **`/specops version` subcommand**: Display the installed SpecOps version
- **`/specops update` subcommand**: Check for newer SpecOps versions and guide through upgrading
- **`/ship-pr` slash command**: Commit changes to a new branch, push, and open a PR for review
- **`/docs-sync` slash command**: Detect stale documentation after code changes and propose targeted updates
- **Task state machine**: Formal task state tracking (`core/task-tracking.md`) with Write Ordering Protocol and single-active-task rule
- **`implementation.md` promoted to decision journal**: Always created during implementation, structured as a Decision Log with deviations and blockers
- **EARS notation for acceptance criteria**: Requirements templates use [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/) with five patterns (Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted) for precise, testable criteria. HTML comment annotations guide agents without affecting rendered markdown
- **PII prevention in data handling**: Specs use synthetic data instead of real PII, with classification-aware handling rules
- **Dogfood infrastructure**: `.specops/` directory and `.specops.json` config for building SpecOps using SpecOps itself

### Changed

- **Init merged into main skill**: `/specops:init` is now `/specops init` — a subcommand of the main skill rather than a separate skill. No behavior change for users.
- **Fixed install commands**: Documentation now uses the correct `/plugin marketplace add` + `/plugin install` + `/reload-plugins` flow instead of the non-existent `/install github:` command.
- **Author waiting message improved**: Now suggests `allowSelfApproval: true` for solo developers instead of leaving them at a dead end
- **Implementation gate updated**: Accepts both `approved` and `self-approved` statuses. Self-approved specs show a note: "This spec was self-approved without peer review."
- **Command routing tightened**: Init and update mode patterns now require SpecOps context — bare "setup" or "update" no longer misclassify product feature requests
- **Bugfix and refactor templates include acceptance criteria checklists**: Phase 4 checkbox verification is now uniformly executable across all spec types
- **Deferred criteria pattern**: Task-tracking and workflow support moving deferred items to a "Deferred Criteria" subsection
- **`spec.json` requiredApprovals defaults to 0**: When review is disabled, `requiredApprovals` defaults to 0 instead of requiring a minimum of 1

### Fixed

- **PR review feedback**: Indentation, resilience, schema, and clarity improvements across core modules
- **Pre-commit hook portability**: Use POSIX case statement for symlink path check instead of bash-specific syntax
- **Stale verify.sh reference**: Removed deleted `claude-init.j2` from verify.sh checks
- **Marketplace plugin source path**: Fixed to use valid relative path format
- **Remote installer**: Include init sub-skill in Claude Code remote installer

## [1.2.0] - 2026-03-06

### Added

- **Plugin marketplace distribution**: `.claude-plugin/plugin.json` and `marketplace.json` manifests for distributing SpecOps via Claude Code, Cursor, Codex, and Copilot plugin marketplaces. Install with `/plugin marketplace add sanmak/specops` then `/plugin install specops@specops-marketplace`
- **`/specops:init` skill**: Interactive config initialization that presents 5 template options (minimal, standard, full, review, builder) and writes `.specops.json` to the user's project
- **Interview mode**: Optional structured interview for vague or exploratory ideas — gathers requirements before spec generation. Trigger with `/specops interview ...` or auto-triggered for ambiguous inputs
- **Development Process prompt**: On first spec creation, prompts to add a Development Process section to the project's README
- **`/monitor` slash command**: Monitor GitHub Actions CI status, diagnose failures, auto-fix and re-push (up to 3 cycles)
- **`/release` slash command**: Automated release workflow — CHANGELOG generation, version bump, validation, commit, push, and GitHub Release creation
- **Command reference guide**: Comprehensive `docs/COMMANDS.md` with all commands, triggers, and platform differences
- **Marketplace submission content**: `docs/MARKETPLACE_SUBMISSIONS.md` with copy-paste-ready content for all 4 platform marketplaces

### Changed

- **Documentation reorganized**: Moved TEAM_GUIDE.md, REFERENCE.md, STRUCTURE.md into `docs/` folder
- **README streamlined**: Simplified for first-time visitors with competitive differentiation against Spec Kit, marketplace install as primary method
- **CI dependencies bumped**: `actions/checkout` v4→v6, `github/codeql-action` v3→v4

### Fixed

- **verify.sh file paths**: Updated after docs/ folder reorganization
- **Gitignore warning**: Warns when `.claude` or platform dirs are gitignored (prevents silent install failures)
- **Validator cleanup**: Removed unused imports in `generator/validate.py`

## [1.1.0] - 2026-03-02

### Added

- **Builder vertical**: `builder` vertical for end-to-end product development across all domains (frontend, backend, infrastructure, data, DevOps) with Product Requirements, System Flow, Ship Plan templates, domain-tagged tasks, and scope boundary guardrails
- **Example builder project**: `examples/specs/feature-task-management-saas/` with full requirements, design, tasks, and spec.json for a SaaS task management product
- **Example builder config**: `examples/.specops.builder.json`
- **Remote installer**: `scripts/remote-install.sh` for curl-based clone-free installation with interactive and non-interactive modes, platform selection, and scope configuration
- **Visual assets**: SVG diagrams for workflow (`assets/workflow.svg`), architecture (`assets/architecture.svg`), and spec structure (`assets/spec-structure.svg`)
- **Git hooks**: `hooks/pre-commit` (JSON validation, ShellCheck, stale generated files, stale checksums) and `hooks/pre-push` (platform validation, checksums, freshness, schema, full test suite)
- **Hook installer**: `scripts/install-hooks.sh` for symlinking hooks into `.git/hooks/`
- **Slash commands**: `.claude/commands/commit.md`, `.claude/commands/push.md`, `.claude/commands/ship.md` for git workflow automation with conventional commits, auto-regeneration, and security-sensitive file advisories
- **Security audit documentation**: `SECURITY-AUDIT.md` with static analysis results
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

### Changed

- **Platform output filenames standardized**: Claude (`prompt.md` → `SKILL.md`), Codex (`AGENTS.md` → `SKILL.md`), Copilot (`copilot-instructions.md` → `specops.instructions.md`), legacy skill (`prompt.md` → `SKILL.md`)
- **Legacy `skill.json` files removed** in favor of SKILL.md frontmatter metadata
- **README overhauled** with badges, visual diagrams, and streamlined installation instructions
- **Build system streamlined**: generator and validator updated for new filenames and frontmatter conventions
- **Installer scripts simplified** for Codex and Copilot platforms
- **CI workflow updated** for new file paths and ShellCheck coverage of hooks
- **CHECKSUMS.sha256 expanded** to include `hooks/pre-commit`, `hooks/pre-push`, and `scripts/install-hooks.sh`
- **Security review integrated** into `/ship` workflow with security-sensitive file advisory

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
