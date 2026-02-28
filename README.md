# SpecOps

Spec-driven development workflow for AI coding assistants. Transform ideas into structured specifications (requirements, design, tasks) before implementation begins.

**SpecOps is a multi-platform spec-driven development system supporting Claude Code, Cursor, OpenAI Codex, and GitHub Copilot** — with more platforms planned.

## Supported Platforms

| Platform | Status | Instruction Format |
|----------|--------|-------------------|
| **Claude Code** | Supported | `/specops` slash command via skill.json |
| **Cursor** | Supported | `.cursor/rules/specops.mdc` |
| **OpenAI Codex** | Supported | `AGENTS.md` |
| **GitHub Copilot** | Supported | `.github/copilot-instructions.md` |
| Windsurf | Planned | `.windsurfrules` |
| Continue.dev | Planned | `.continuerules` |

## Overview

SpecOps brings [Kiro](https://kiro.dev)-inspired spec-driven development to your AI coding assistant:

- **Spec-driven development**: Transform ideas into detailed implementation plans
- **Autonomous execution**: AI handles the full workflow from spec to code
- **Team collaboration**: Shared conventions and trackable progress
- **Configurable**: Adapts to your team's structure and preferences
- **Multi-platform**: Same workflow across Claude Code, Cursor, Codex, and more

## Quick Start

### 1. Install for your platform

```bash
# Interactive setup — detects your tools and installs
bash setup.sh
```

Or install manually for a specific platform:

- **Claude Code**: See [platforms/claude/README.md](platforms/claude/README.md)
- **Cursor**: See [platforms/cursor/README.md](platforms/cursor/README.md)
- **OpenAI Codex**: See [platforms/codex/README.md](platforms/codex/README.md)
- **GitHub Copilot**: See [platforms/copilot/README.md](platforms/copilot/README.md)

### 2. Configure your project

Create `.specops.json` in your project root:

```json
{
  "specsDir": ".specops",
  "team": {
    "conventions": [
      "Use TypeScript for all new code",
      "Write unit tests for business logic"
    ],
    "reviewRequired": true
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto"
  }
}
```

### 3. Use it

**Claude Code:**
```
/specops Add user authentication with OAuth
```

**Cursor / Codex / Copilot:**
```
Use specops to add user authentication with OAuth
```

## How It Works

SpecOps follows a 4-phase workflow:

1. **Understand Context**: Reads config, analyzes your request, explores codebase
2. **Create Specification**: Generates `requirements.md`, `design.md`, `tasks.md`
3. **Implement**: Executes code changes following the spec
4. **Complete**: Verifies acceptance criteria, commits, creates PR

## Simplicity Principle

SpecOps follows a core simplicity principle: prefer the simplest solution that meets the requirements.

- **Specs scale to the task** — a small feature won't generate a full rollout plan or caching strategy
- **No speculative complexity** — implementations avoid premature abstractions and features "for the future"
- **Use what exists** — the agent prefers existing project patterns and utilities over creating new ones

## Configuration

### `.specops.json` Schema

```json
{
  "specsDir": "string",
  "vertical": "string",
  "templates": {
    "feature": "string",
    "bugfix": "string",
    "refactor": "string",
    "design": "string",
    "tasks": "string"
  },
  "team": {
    "conventions": ["string"],
    "reviewRequired": "boolean",
    "taskTracking": "string",
    "codeReview": {
      "required": "boolean",
      "minApprovals": "number",
      "requireTests": "boolean",
      "requireDocs": "boolean"
    }
  },
  "implementation": {
    "autoCommit": "boolean",
    "createPR": "boolean",
    "testing": "string",
    "testFramework": "string",
    "linting": { "enabled": "boolean", "fixOnSave": "boolean" },
    "formatting": { "enabled": "boolean", "tool": "string" }
  },
  "modules": {
    "<module-name>": {
      "specsDir": "string",
      "conventions": ["string"]
    }
  },
  "integrations": {
    "ci": "string",
    "deployment": "string",
    "monitoring": "string",
    "analytics": "string"
  }
}
```

See [examples/](examples/) for minimal, standard, and full configuration examples.

## Vertical Support

SpecOps adapts its templates to your project type:

| Vertical | How SpecOps Adapts |
|----------|-------------------|
| **Backend** | Default templates designed for backend development |
| **Frontend** | Minor adaptations (state management instead of data model) |
| **Full Stack** | Default templates handle both layers |
| **Infrastructure** | Infra requirements, topology, resource definitions |
| **Data Engineering** | Pipeline stages, data flow, data contracts |
| **Library/SDK** | Developer use cases, public API surface |

Configure explicitly or let SpecOps auto-detect:

```json
{
  "vertical": "infrastructure"
}
```

## Architecture

The repository is organized into three layers:

```
core/           Platform-agnostic workflow, templates, safety rules
platforms/      Platform-specific adapters (Claude, Cursor, Codex, Copilot)
generator/      Generates platform outputs from core + adapters
```

The `core/` directory defines the workflow once. The `generator/` system generates platform-specific instruction files. Generated files are checked into git so users never need to run the build.

See [STRUCTURE.md](STRUCTURE.md) for the full repository layout.

## Security

SpecOps includes security features:

- **Prompt injection defense**: Convention strings and custom templates are sanitized
- **Data handling policy**: Secrets use placeholders, PII uses synthetic data
- **Schema hardening**: All fields have validation constraints
- **Path containment**: Rejects absolute paths and `../` traversal
- **Config conflict detection**: Contradictory settings are flagged

For vulnerability reporting, see [SECURITY.md](SECURITY.md).

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for the guide, including how to add support for new platforms.

## License

MIT License - See [LICENSE](LICENSE) for details
