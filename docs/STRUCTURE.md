# SpecOps Repository Structure

## Directory Tree

```
specops/
├── README.md                             # Main documentation
├── QUICKSTART.md                         # Getting started guide
├── CHANGELOG.md                          # Version history
├── CLAUDE.md                             # Claude Code AI assistant instructions
├── LICENSE                               # MIT License
├── SECURITY.md                           # Security policy
├── CONTRIBUTING.md                       # Contributor guidelines
├── CHECKSUMS.sha256                      # SHA-256 checksums
├── .gitignore                            # Git ignore rules
│
├── docs/                                 # Documentation
│   ├── COMMANDS.md                       # Command reference
│   ├── REFERENCE.md                      # Quick reference card
│   ├── STRUCTURE.md                      # This file
│   ├── TEAM_GUIDE.md                     # Team collaboration guide
│   ├── SBOM.md                           # Software Bill of Materials
│   ├── STEERING_GUIDE.md                 # Steering files guide
│   ├── DIAGRAMS.md                       # Mermaid sequence diagrams for all workflows
│   ├── PLAN-VS-SPEC.md                   # Plan Mode vs Spec Mode comparison
│   ├── SECURITY-AUDIT.md                 # Security audit results
│   ├── COMPARISON.md                     # Competitive comparison (vs Kiro, EPIC/Reload, Spec Kit)
│   └── MARKETPLACE_SUBMISSIONS.md        # Marketplace submission content
│
├── assets/                               # Visual assets (SVG diagrams)
│   ├── workflow.svg                      # 4-phase workflow diagram
│   ├── architecture.svg                  # Three-layer architecture diagram
│   ├── spec-structure.svg                # Spec output structure diagram
│   ├── review-workflow.svg               # Review workflow diagram
│   └── interview-workflow.svg            # Interview workflow diagram
│
├── schema.json                           # JSON Schema for .specops.json
├── spec-schema.json                      # JSON Schema for spec.json validation
├── index-schema.json                     # JSON Schema for index.json validation
├── setup.sh                              # Universal installer (multi-platform)
├── verify.sh                             # Post-installation verification
│
├── scripts/
│   ├── bump-version.sh                   # Version bumping utility
│   ├── run-tests.sh                      # Test runner
│   ├── remote-install.sh                 # Remote installer (curl-based, no clone needed)
│   ├── install-hooks.sh                  # Git hooks installer
│   └── run-review-gate.sh               # Review gate runner script
│
├── hooks/                                # Git hooks
│   ├── pre-commit                        # JSON validation, ShellCheck, stale file checks
│   └── pre-push                          # Platform validation, checksums, full test suite
│
├── .claude/                              # Claude Code project commands
│   └── commands/
│       ├── commit.md                     # /commit command
│       ├── push.md                       # /push command
│       ├── ship.md                       # /ship command
│       ├── ship-pr.md                    # /ship-pr command
│       ├── pr-fix.md                     # /pr-fix command
│       ├── release.md                    # /release command
│       ├── monitor.md                    # /monitor command
│       ├── docs-sync.md                  # /docs-sync command
│       ├── full-review-gate.md           # /full-review-gate command
│       ├── core-review.md               # /core-review command
│       └── resolve-conflicts.md         # /resolve-conflicts command
│
├── core/                                 # Platform-agnostic source of truth
│   ├── workflow.md                       # 4-phase workflow specification
│   ├── safety.md                         # Security guardrails (injected into all platforms)
│   ├── simplicity.md                     # Simplicity Principle
│   ├── config-handling.md                # Configuration defaults and handling
│   ├── data-handling.md                  # Secrets, PII, data classification rules
│   ├── error-handling.md                 # Error handling, success criteria
│   ├── verticals.md                      # Vertical adaptation rules
│   ├── custom-templates.md               # Custom template resolution logic
│   ├── view.md                           # Spec viewing and listing
│   ├── interview.md                      # Interview mode for vague requests
│   ├── init.md                           # Init mode (config creation)
│   ├── update.md                         # Update mode (version checking)
│   ├── review-workflow.md                # Collaborative spec review workflow
│   ├── steering.md                       # Steering files system (persistent project context)
│   ├── reconciliation.md                 # Drift detection and reconciliation
│   ├── from-plan.md                      # Convert plan mode output to spec
│   ├── feedback.md                       # User feedback submission to SpecOps repo
│   ├── memory.md                         # Local memory layer
│   ├── repo-map.md                       # Agent-driven codebase structural map
│   ├── task-tracking.md                  # Task state machine and ordering
│   ├── task-delegation.md                # Task delegation for Phase 3 context management
│   ├── writing-quality.md                # Writing quality rules for spec artifacts
│   ├── tool-abstraction.md               # Abstract tool operations and capability flags
│   └── templates/                        # Default spec templates
│       ├── feature-requirements.md       # Feature requirements template
│       ├── bugfix.md                     # Bug fix template
│       ├── refactor.md                   # Refactor template
│       ├── design.md                     # Design document template
│       ├── tasks.md                      # Task breakdown template
│       ├── implementation.md             # Implementation notes template
│       └── reviews.md                    # Review feedback template
│
├── platforms/                            # Platform-specific adapters
│   ├── claude/                           # Claude Code adapter
│   │   ├── platform.json                 # Capabilities, tool mapping, entry point
│   │   ├── SKILL.md                      # Generated Claude Code skill file
│   │   ├── install.sh                    # Claude-specific installer
│   │   └── README.md                     # Claude Code quickstart
│   ├── cursor/                           # Cursor adapter
│   │   ├── platform.json                 # Capabilities, tool mapping
│   │   ├── specops.mdc                   # Generated Cursor rules file
│   │   ├── install.sh                    # Cursor-specific installer
│   │   └── README.md                     # Cursor quickstart
│   ├── codex/                            # OpenAI Codex adapter
│   │   ├── platform.json                 # Capabilities, tool mapping
│   │   ├── SKILL.md                      # Generated Codex skill file
│   │   ├── install.sh                    # Codex-specific installer
│   │   └── README.md                     # Codex quickstart
│   └── copilot/                          # GitHub Copilot adapter
│       ├── platform.json                 # Capabilities, tool mapping
│       ├── specops.instructions.md       # Generated Copilot scoped instructions
│       ├── install.sh                    # Copilot-specific installer
│       └── README.md                     # Copilot quickstart
│
├── generator/                            # Build system
│   ├── generate.py                       # Assembles platform outputs from core/
│   ├── validate.py                       # Validates generated outputs
│   └── templates/                        # Platform-specific templates
│       ├── claude.j2                     # Claude Code output template
│       ├── cursor.j2                     # Cursor output template
│       ├── codex.j2                      # Codex output template
│       └── copilot.j2                    # Copilot output template
│
├── .claude-plugin/                       # Claude Code plugin manifests (generated)
│   ├── plugin.json                       # Plugin metadata and version
│   └── marketplace.json                  # Marketplace catalog entry
│
├── skills/                               # Plugin skills directory
│   └── specops/
│       └── SKILL.md                      # Copy of platforms/claude/SKILL.md
│
├── tests/                                # Test suite
│   ├── test_schema_validation.py         # Validates example configs against schema
│   ├── test_schema_constraints.py        # Tests schema rejects invalid inputs
│   ├── check_schema_sync.py             # Validates schema.json is well-formed
│   ├── test_platform_consistency.py      # Checks all platform outputs are consistent
│   ├── test_build.py                     # Tests build system generates valid outputs
│   └── test_spec_schema.py              # Validates spec.json against spec-schema.json
│
├── .github/
│   └── workflows/
│       ├── ci.yml                        # CI pipeline
│       ├── codeql.yml                    # CodeQL security analysis
│       └── release.yml                   # Release version bump automation
│
└── examples/                             # Example configurations and specs
    ├── .specops.json                     # Standard configuration
    ├── .specops.minimal.json             # Minimal configuration
    ├── .specops.full.json                # Full configuration
    ├── .specops.review.json              # Review-enabled configuration
    ├── .specops.builder.json             # Builder vertical configuration
    ├── .specops.solo-review.json         # Solo developer review configuration
    ├── templates/                        # Vertical-specific templates
    │   ├── infra-requirements.md
    │   ├── infra-design.md
    │   ├── data-pipeline-requirements.md
    │   ├── data-pipeline-design.md
    │   ├── library-requirements.md
    │   └── library-design.md
    └── specs/                            # Example specifications (one per vertical)
        ├── feature-user-authentication/
        ├── feature-dark-mode-toggle/
        ├── feature-k8s-autoscaling/
        ├── feature-user-activity-pipeline/
        ├── feature-date-utils-library/
        ├── feature-task-management-saas/
        └── feature-self-approved-example/
```

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────┐
│                  core/                          │
│  Platform-agnostic workflow, templates, safety  │
│  Single source of truth for all platforms       │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┼────────────┬────────────┐
         ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
│  Claude Code │ │  Cursor  │ │  Codex  │ │  Copilot │
│  platforms/  │ │platforms/│ │platforms/│ │platforms/ │
│  claude/     │ │cursor/   │ │codex/   │ │copilot/  │
└──────────────┘ └──────────┘ └─────────┘ └──────────┘
```

### Build System

The `generator/generate.py` script assembles platform-specific outputs:

1. Loads all `core/*.md` modules
2. Loads `platforms/{name}/platform.json` for tool mappings and capabilities
3. Renders through `generator/templates/{name}.j2` templates
4. Substitutes abstract tool operations with platform-specific language
5. Writes output to `platforms/{name}/`

Generated files are checked into git so end users never need to run the build.

### Adding a New Platform

1. Create `platforms/{name}/platform.json` with capabilities and tool mapping
2. Create `generator/templates/{name}.j2` with the platform's instruction format
3. Add the platform to `SUPPORTED_PLATFORMS` in `generator/generate.py`
4. Create `platforms/{name}/install.sh`
5. Run `python3 generator/generate.py --platform {name}`
6. Add to `generator/validate.py` and `tests/test_platform_consistency.py`

## Version

**Version**: 1.3.0
**Last Updated**: 2026-03-18
