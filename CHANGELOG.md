# Changelog

All notable changes to SpecOps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2026-03-22

### Added

- **Spec decomposition**: Automatic scope assessment (Phase 1.5) detects when large features should be split into multiple specs. Split detection (Phase 2 safety net) catches decomposition missed in Phase 1.5. Walking skeleton principle flags the first wave-1 spec as the integration skeleton.
- **Initiative model**: Multi-spec features tracked as initiatives with execution waves derived via topological sort. Initiative data stored in `<specsDir>/initiatives/<id>/initiative.json` with a dedicated schema.
- **Cross-spec dependencies**: `specDependencies` array in `spec.json` declares required and advisory dependencies between specs. Cycle detection (DFS with white/gray/black coloring) prevents circular dependency chains. `relatedSpecs` for informational cross-linking.
- **Dependency gate (Phase 3)**: Blocks implementation when required `specDependencies` are incomplete. Protocol breach if skipped. Scope hammering provides blocker resolution options (scope_cut, interface_defined, completed, escalated, deferred).
- **Initiative orchestration**: Autonomous multi-spec execution via `/specops initiative <id>`. Lightweight orchestrator dispatches specs through the normal dispatcher with handoff bundles containing initiative context, spec identity, dependency context, and scope constraints.
- **Phase dispatch**: Fresh context for Phase 3 and Phase 4 sub-agents. Phase 2 and Phase 3 completion summaries signal handoff to fresh sub-agents, preventing context exhaustion on large specs.
- **Task delegation threshold lowered**: Default auto-activation threshold reduced from 6 to 4, configurable via `implementation.delegationThreshold` in `.specops.json`.
- **Dependencies and Blockers sections**: All 5 spec templates (feature-requirements, design, bugfix, refactor, tasks) include Spec Dependencies and Cross-Spec Blockers tables for multi-spec coordination.

### Schema

- `spec-schema.json`: Added optional `partOf` (string, initiative ID), `relatedSpecs` (array of spec IDs), and `specDependencies` (array of objects with specId, reason, required, contractRef). All backward-compatible — existing specs validate without changes.
- New `initiative-schema.json`: Schema for initiative tracking files with id, title, specs, order (execution waves), skeleton, and status fields.
- `index-schema.json`: Added optional `partOf` field to index entries for initiative membership.

### Note

All new fields are optional. Existing specs, configurations, and workflows continue to work without modification.

## [1.4.1] - 2026-03-22

### Fixed

- **Remote installer crash on empty mode files**: `download_file()` used `exit 1` which killed the entire script even inside `|| true` error suppression — changed to `return 1` so the mode download loop gracefully skips empty files (like `version.md`) while critical downloads still fail-fast via `set -e`. Error messages now go to stderr so `2>/dev/null` properly suppresses them.

## [1.4.0] - 2026-03-22

### Added

- **Context-aware dispatch**: Decomposed monolithic `SKILL.md` into a lightweight dispatcher + 13 mode files (`modes/`) for faster loading, reduced context usage, and cleaner separation of concerns
- **Engineering discipline module**: Grounds design, testing, reliability, and constraint rules in named engineering leaders (Parnas, Dijkstra, Lamport, et al.) for principled decision-making
- **Dependency safety gate**: Mandatory CVE, EOL, and best-practices verification before implementation — blocks Phase 3 when critical vulnerabilities or unsupported dependencies are detected
- **Workflow automation suite**: Run logging, plan validation, git checkpointing, and pipeline mode (`/specops pipeline`) for CI-driven spec execution
- **Project-type awareness and proxy metrics**: Auto-detect project type (web app, CLI, library, etc.) and surface domain-appropriate quality proxy metrics during implementation
- **Feedback submission and writing quality rules**: `/specops feedback` command for structured feedback submission; writing quality module enforces clarity, precision, and consistency in spec artifacts
- **Rich issue body composition and GitHub auto-labels**: External task tracking creates detailed issue bodies with acceptance criteria, context links, and auto-applied labels based on spec type and vertical
- **Task delegation with complexity scoring**: Context-managed task execution with complexity-based strategy selection, quality gates, and dependency ordering — extends Phase 3 delegation with sub-agent support, session checkpoints, and sequential fallback
- **`/resolve-conflicts` slash command**: Resolve merge conflicts on a GitHub PR by merging the base branch into the PR branch in an isolated worktree, with JSON/markdown-aware resolution
- **Enforcement gates**: Deterministic enforcement for Phase 1 steering/memory setup, Phase 4 memory write, and Phase 3 task tracking — mandatory steps with verification, not optional suggestions
- **Spec artifact linter**: Structural validation of spec documents — heading hierarchy, required sections, placeholder detection, and cross-reference integrity checks
- **Plan-to-spec transition**: Automated conversion from plan mode to SpecOps workflow with 3-layer enforcement (PostToolUse hook, dispatcher gate, mode instructions)
- **Markdown lint in local validation**: CI-local parity with `markdownlint-cli2` integrated into pre-commit hook and test suite
- **ExitPlanMode PostToolUse hook**: Intercepts plan mode exit to offer SpecOps workflow transition before unstructured implementation begins
- **SHA-256 checksum verification in remote installer**: Integrity verification of downloaded files during remote installation
- **Repo-map refresh in Phase 4**: Automatically refreshes the AST repo map during Phase 4 completion when structural changes are detected
- **Expanded docs-sync dependency map**: Coverage for all `core/*.md` modules in the docs-sync command's change-to-docs mapping

### Changed

- **README and CLAUDE.md rewritten**: Streamlined for developer clarity and conversion — clearer value proposition, simplified architecture explanation, and updated build/validate commands
- **Steering files updated**: Repo-map and tech stack steering files refreshed to reflect current project state

### Fixed

- **Task delegation protocol gaps**: Delegation handoff bundles, blocked task handling, and orchestrator loop correctness
- **Resolve-conflicts correctness**: Ours/theirs semantics, fast-path handling, merge-tree order, checksum list, UNKNOWN mergeability retry, empty-commit guard, and cleanup-on-failure
- **Issue creation shell safety**: Hardened shell quoting, FAILED sentinel mismatch, blocked transition sync, and Phase 2 step ordering
- **JSON error handling in hook installers**: Type guards and error handling for hook installation scripts; restored missing checksum entries
- **Feedback shell expansion bug**: Fixed variable expansion in feedback submission shell commands
- **Validation marker uniqueness**: Replaced non-unique validation markers in `validate.py` with module-specific text to prevent false-positive marker validation
- **Markdownlint compliance**: Resolved 1150+ markdownlint violations across source files
- **RUN_COMMAND noun usage**: Resolved abstract operation verb/noun inconsistency and IssueID guard
- **Linter type safety**: Per-task status filter, resume-plan merge handling, and linter enforcement fixes
- **Checksum alignment**: Aligned checksummed file lists, unique `validate.py` markers, and docs-sync map across all validation surfaces

## [1.3.0] - 2026-03-15

### Added in 1.3.0

- **AST-based repo map**: Machine-generated structural map of the codebase stored as a steering file (`<specsDir>/steering/repo-map.md`) with `inclusion: always`. 4-tier language extraction (Python AST signatures, TS/JS exports, Go/Rust/Java declarations, other files), staleness detection (time-based 7 days + hash-based file list comparison), scope control (100 files, depth 3, ~3000 token budget)
- **`/specops map` subcommand**: Generate or refresh the repo map on demand. Auto-detects missing or stale maps during Phase 1 step 3.5
- **Local Memory Layer**: Persistent project memory extracted from completed specs — decisions (`decisions.json`), project context (`context.md`), and recurring patterns (`patterns.json`) stored in `<specsDir>/memory/`. Loaded automatically during Phase 1; updated during Phase 4
- **`/specops memory` and `/specops memory seed` subcommands**: View accumulated decisions, context, and patterns. `seed` populates memory from existing completed specs' `implementation.md` decision journals
- **`/specops from-plan` subcommand**: Convert an existing AI coding assistant plan (from plan mode or any structured outline) into a persistent SpecOps spec. Faithfully maps goals → requirements, approach → design, steps → tasks with `[To be defined]` placeholders for missing sections
- **Drift detection & reconciliation**: New `audit` and `reconcile` subcommands (`core/reconciliation.md`). `audit` runs 5 drift checks (File Drift, Post-Completion Modification, Task Status Inconsistency, Staleness, Cross-Spec Conflicts) and produces a health report per spec. `reconcile` guides interactive repair of findings. Git-dependent checks degrade gracefully when `canAccessGit: false`; reconcile is blocked on non-interactive platforms with a clear message
- **Steering files system**: Persistent project context in `<specsDir>/steering/` — markdown files with YAML frontmatter loaded automatically during Phase 1. Three inclusion modes: `always` (every spec), `fileMatch` (only when affected files match globs), and `manual` (on-demand). Foundation templates: `product.md`, `tech.md`, `structure.md`
- **`/specops steering` subcommand**: On-demand command to scaffold, view, and manage steering files
- **EARS notation for acceptance criteria**: Requirements templates use [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/) with five patterns (Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted) for precise, testable criteria. HTML comment annotations guide agents without affecting rendered markdown
- **Regression risk analysis**: Severity-scaled discovery methodology for bugfix specs — Blast Radius, Behavior Inventory, Test Coverage Assessment, Risk Tier, and Scope Escalation Check
- **Self-review workflow for solo developers**: New `allowSelfApproval` config option in `team.specReview` enables solo developers to review and approve their own specs with distinct `self-approved` audit trail
- **Version Extraction Protocol**: Deterministic version detection via `GET_SPECOPS_VERSION` abstract operation — never guesses or invents version numbers for `spec.json` metadata
- **Version tracking in specs**: `specopsCreatedWith` and `specopsUpdatedWith` fields in `spec.json` record which SpecOps version created and last modified each spec
- **`/specops version` and `/specops update` subcommands**: Display installed version and check for newer versions
- **`/specops audit` and `/specops reconcile` subcommands**: Detect drift between spec artifacts and codebase; interactively repair drifted specs
- **Task state machine**: Formal task state tracking (`core/task-tracking.md`) with Write Ordering Protocol and single-active-task rule
- **`implementation.md` promoted to decision journal**: Always created during implementation, structured as a Decision Log with deviations and blockers
- **`/ship-pr` slash command**: Commit changes to a new branch, push, and open a PR for review
- **`/docs-sync` slash command**: Detect stale documentation after code changes and propose targeted updates
- **`/full-review-gate` slash command**: Comprehensive code review gate with worktree isolation — runs bug, security, PII/privacy, and dependency risk checks with P0–P3 severity findings and go/no-go release status
- **`/core-review` slash command**: Review code changes against SpecOps project-specific patterns — tool abstraction violations, generated file drift, cross-platform consistency gaps
- **Plan Mode vs Spec Mode comparison guide**: `docs/PLAN-VS-SPEC.md` documenting when to use plan mode vs spec mode
- **Competitive comparison guide**: `docs/COMPARISON.md` with feature matrix comparing SpecOps to Kiro, EPIC/Reload, and GitHub Spec Kit
- **Sequence diagrams**: `docs/DIAGRAMS.md` with 8 Mermaid sequence diagrams covering all major SpecOps workflows
- **PII prevention in data handling**: Specs use synthetic data instead of real PII, with classification-aware handling rules

### Changed in 1.3.0

- **Init merged into main skill**: `/specops:init` is now `/specops init` — a subcommand of the main skill rather than a separate skill
- **Bugfix and refactor templates include acceptance criteria checklists**: Phase 4 checkbox verification is now uniformly executable across all spec types
- **Deferred criteria pattern**: Task-tracking and workflow support moving deferred items to a "Deferred Criteria" subsection
- **`spec.json` requiredApprovals defaults to 0**: When review is disabled, `requiredApprovals` defaults to 0 instead of requiring a minimum of 1
- **Steering is convention-based**: Steering file configuration is not stored in `.specops.json` — it is convention-based (files in `<specsDir>/steering/` with YAML frontmatter)
- **Command routing tightened**: Init and update mode patterns now require SpecOps context — bare "setup" or "update" no longer misclassify product feature requests
- **README updated**: Competitive comparison with Kiro, EPIC/Reload, and Spec Kit; dogfood proof section

### Fixed in 1.3.0

- **PR review feedback**: Extensive review-driven fixes across 15 PRs — indentation, resilience, schema, and clarity improvements across core modules
- **Pre-commit hook portability**: Use POSIX case statement for symlink path check instead of bash-specific syntax
- **macOS compatibility**: Hash computation uses `shasum -a 256` with fallback for environments without `sha256sum`
- **Worktree cleanup**: Scoped pr-fix compact state files and worktree cleanup to avoid concurrent run collisions
- **spec.json validation**: Malformed spec.json files now fall back to legacy mode with a warning instead of undefined behavior
- **Memory seed workflow**: Guard index.json reads, unconditional context.md writes, and self-exclusion handling
- **Remote installer**: Include init sub-skill in Claude Code remote installer
- **Marketplace plugin source path**: Fixed to use valid relative path format

## [1.2.0] - 2026-03-06

### Added in 1.2.0

- **Plugin marketplace distribution**: `.claude-plugin/plugin.json` and `marketplace.json` manifests for distributing SpecOps via Claude Code, Cursor, Codex, and Copilot plugin marketplaces. Install with `/plugin marketplace add sanmak/specops` then `/plugin install specops@specops-marketplace`
- **`/specops:init` skill**: Interactive config initialization that presents 5 template options (minimal, standard, full, review, builder) and writes `.specops.json` to the user's project
- **Interview mode**: Optional structured interview for vague or exploratory ideas — gathers requirements before spec generation. Trigger with `/specops interview ...` or auto-triggered for ambiguous inputs
- **Development Process prompt**: On first spec creation, prompts to add a Development Process section to the project's README
- **`/monitor` slash command**: Monitor GitHub Actions CI status, diagnose failures, auto-fix and re-push (up to 3 cycles)
- **`/release` slash command**: Automated release workflow — CHANGELOG generation, version bump, validation, commit, push, and GitHub Release creation
- **Command reference guide**: Comprehensive `docs/COMMANDS.md` with all commands, triggers, and platform differences
- **Marketplace submission content**: `docs/MARKETPLACE_SUBMISSIONS.md` with copy-paste-ready content for all 4 platform marketplaces

### Changed in 1.2.0

- **Documentation reorganized**: Moved TEAM_GUIDE.md, REFERENCE.md, STRUCTURE.md into `docs/` folder
- **README streamlined**: Simplified for first-time visitors with competitive differentiation against Spec Kit, marketplace install as primary method
- **CI dependencies bumped**: `actions/checkout` v4→v6, `github/codeql-action` v3→v4

### Fixed in 1.2.0

- **verify.sh file paths**: Updated after docs/ folder reorganization
- **Gitignore warning**: Warns when `.claude` or platform dirs are gitignored (prevents silent install failures)
- **Validator cleanup**: Removed unused imports in `generator/validate.py`

## [1.1.0] - 2026-03-02

### Added in 1.1.0

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

### Changed in 1.1.0

- **Platform output filenames standardized**: Claude (`prompt.md` → `SKILL.md`), Codex (`AGENTS.md` → `SKILL.md`), Copilot (`copilot-instructions.md` → `specops.instructions.md`), legacy skill (`prompt.md` → `SKILL.md`)
- **Legacy `skill.json` files removed** in favor of SKILL.md frontmatter metadata
- **README overhauled** with badges, visual diagrams, and streamlined installation instructions
- **Build system streamlined**: generator and validator updated for new filenames and frontmatter conventions
- **Installer scripts simplified** for Codex and Copilot platforms
- **CI workflow updated** for new file paths and ShellCheck coverage of hooks
- **CHECKSUMS.sha256 expanded** to include `hooks/pre-commit`, `hooks/pre-push`, and `scripts/install-hooks.sh`
- **Security review integrated** into `/ship` workflow with security-sensitive file advisory

## [1.0.0] - 2026-02-28

### Added in 1.0.0

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
