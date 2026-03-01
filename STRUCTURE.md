# SpecOps Repository Structure

## Directory Tree

```
specops/
├── README.md                             # Main documentation
├── QUICKSTART.md                         # Getting started guide
├── TEAM_GUIDE.md                         # Team collaboration guide
├── REFERENCE.md                          # Quick reference card
├── CHANGELOG.md                          # Version history
├── STRUCTURE.md                          # This file
├── CLAUDE.md                             # Claude Code AI assistant instructions
├── LICENSE                               # MIT License
├── SECURITY.md                           # Security policy
├── CONTRIBUTING.md                       # Contributor guidelines
├── SBOM.md                               # Software Bill of Materials
├── CHECKSUMS.sha256                      # SHA-256 checksums
├── .gitignore                            # Git ignore rules
│
├── assets/                               # Visual assets (SVG diagrams)
│   ├── workflow.svg                      # 4-phase workflow diagram
│   ├── architecture.svg                  # Three-layer architecture diagram
│   └── spec-structure.svg                # Spec output structure diagram
├── schema.json                           # JSON Schema for .specops.json
├── setup.sh                              # Universal installer (multi-platform)
├── verify.sh                             # Post-installation verification
│
├── scripts/
│   ├── bump-version.sh                   # Version bumping utility
│   ├── run-tests.sh                      # Test runner
│   └── remote-install.sh                 # Remote installer (curl-based, no clone needed)
│
├── core/                                 # Platform-agnostic source of truth
│   ├── workflow.md                       # 4-phase workflow specification
│   ├── safety.md                         # Security guardrails (injected into all platforms)
│   ├── simplicity.md                     # Simplicity Principle
│   ├── data-handling.md                  # Secrets, PII, data classification rules
│   ├── verticals.md                      # Vertical adaptation rules
│   ├── custom-templates.md               # Custom template resolution logic
│   ├── config-handling.md                # Configuration defaults and handling
│   ├── error-handling.md                 # Error handling, review process, success criteria
│   ├── tool-abstraction.md               # Abstract tool operations and capability flags
│   └── templates/                        # Default spec templates
│       ├── feature-requirements.md       # Feature requirements template
│       ├── bugfix.md                     # Bug fix template
│       ├── refactor.md                   # Refactor template
│       ├── design.md                     # Design document template
│       ├── tasks.md                      # Task breakdown template
│       └── implementation.md             # Implementation notes template
│
├── platforms/                            # Platform-specific adapters
│   ├── claude/                           # Claude Code adapter
│   │   ├── platform.json                 # Capabilities, tool mapping, entry point
│   │   ├── skill.json                    # Claude Code skill metadata
│   │   ├── prompt.md                     # Generated agent instructions
│   │   ├── install.sh                    # Claude-specific installer
│   │   └── README.md                     # Claude Code quickstart
│   ├── cursor/                           # Cursor adapter
│   │   ├── platform.json                 # Capabilities, tool mapping
│   │   ├── specops.mdc                   # Generated Cursor rules file
│   │   ├── install.sh                    # Cursor-specific installer
│   │   └── README.md                     # Cursor quickstart
│   ├── codex/                            # OpenAI Codex adapter
│   │   ├── platform.json                 # Capabilities, tool mapping
│   │   ├── AGENTS.md                     # Generated Codex agent instructions
│   │   ├── install.sh                    # Codex-specific installer
│   │   └── README.md                     # Codex quickstart
│   └── copilot/                          # GitHub Copilot adapter
│       ├── platform.json                 # Capabilities, tool mapping
│       ├── copilot-instructions.md       # Generated Copilot instructions
│       ├── install.sh                    # Copilot-specific installer
│       └── README.md                     # Copilot quickstart
│
├── generator/                                # Build system
│   ├── generate.py                       # Assembles platform outputs from core/
│   ├── validate.py                       # Validates generated outputs
│   └── templates/                        # Platform-specific templates
│       ├── claude.j2                     # Claude Code output template
│       ├── cursor.j2                     # Cursor output template
│       ├── codex.j2                      # Codex output template
│       └── copilot.j2                    # Copilot output template
│
├── skills/                               # Legacy skill directory (backward compat)
│   └── specops/
│       ├── skill.json                    # Same as platforms/claude/skill.json
│       └── prompt.md                     # Original Claude Code prompt
│
├── tests/                                # Test suite
│   ├── test_schema_validation.py         # Validates example configs against schema
│   ├── test_schema_constraints.py        # Tests schema rejects invalid inputs
│   ├── check_schema_sync.py             # Verifies schema sync across all platforms
│   ├── test_platform_consistency.py      # Checks all platform outputs are consistent
│   └── test_build.py                     # Tests build system generates valid outputs
│
├── .github/
│   └── workflows/
│       └── ci.yml                        # CI pipeline
│
└── examples/                             # Example configurations and specs
    ├── .specops.json                     # Standard configuration
    ├── .specops.minimal.json             # Minimal configuration
    ├── .specops.full.json                # Full configuration
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
        └── feature-date-utils-library/
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

**Version**: 2.0.0
**Last Updated**: 2026-02-28
