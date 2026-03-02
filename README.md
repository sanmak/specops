# SpecOps

**Stop vibe coding. Start spec-driven development.**

[![CI](https://github.com/sanmak/specops/actions/workflows/ci.yml/badge.svg)](https://github.com/sanmak/specops/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/sanmak/specops)](https://github.com/sanmak/specops/releases)
[![GitHub Stars](https://img.shields.io/github/stars/sanmak/specops?style=social)](https://github.com/sanmak/specops)
[![License: MIT](https://img.shields.io/github/license/sanmak/specops)](https://github.com/sanmak/specops/blob/main/LICENSE)

SpecOps transforms how you work with AI coding assistants. Instead of jumping straight into code, it creates structured specifications — requirements, design, tasks — then implements them systematically. Works with **Claude Code**, **Cursor**, **OpenAI Codex**, and **GitHub Copilot**.

## How It Works

<p align="center">
  <img src="assets/workflow.svg" alt="SpecOps 4-phase workflow: Understand, Spec, Implement, Complete" width="800"/>
</p>

One command triggers a 4-phase workflow: understand your codebase, generate a structured spec, implement it, and verify the result.

### Team Review Workflow

<p align="center">
  <img src="assets/review-workflow.svg" alt="SpecOps collaborative review workflow: draft, review, revise, approve, implement" width="800"/>
</p>

For teams, SpecOps adds a structured review cycle between spec creation and implementation. Engineers review specs collaboratively, provide section-by-section feedback, and approve before coding begins. See [TEAM_GUIDE.md](TEAM_GUIDE.md) for the full team workflow.

## Quick Start

### Install

```bash
# One-line install (detects your AI coding tools automatically)
bash <(curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh)
```

### Platform-specific and manual install options

**Non-interactive install:**

```bash
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform claude --scope user
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform cursor
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform codex
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform copilot
```

**Clone and run locally:**

```bash
git clone https://github.com/sanmak/specops.git && cd specops && bash setup.sh
```

**Platform-specific guides:**

- [Claude Code](platforms/claude/README.md)
- [Cursor](platforms/cursor/README.md)
- [OpenAI Codex](platforms/codex/README.md)
- [GitHub Copilot](platforms/copilot/README.md)

### Use

**Claude Code:**

```
/specops Add user authentication with OAuth
/specops view auth-feature
/specops list
```

**Cursor / Codex / Copilot:**

```
Use specops to add user authentication with OAuth
View the auth-feature spec
List all specops specs
```

## What Gets Created

<p align="center">
  <img src="assets/spec-structure.svg" alt="SpecOps generates requirements.md, design.md, and tasks.md for each feature" width="620"/>
</p>

## Platforms

| Platform           | Status    | Trigger                                                                       |
| ------------------ | --------- | ----------------------------------------------------------------------------- |
| **Claude Code**    | Supported | `/specops [description]`, `/specops view`, `/specops list`                    |
| **Cursor**         | Supported | `Use specops to [description]`, `View the ... spec`, `List all specops specs` |
| **OpenAI Codex**   | Supported | `Use specops to [description]`, `View the ... spec`, `List all specops specs` |
| **GitHub Copilot** | Supported | `Use specops to [description]`, `View the ... spec`, `List all specops specs` |
| Windsurf           | Planned   | —                                                                             |
| Continue.dev       | Planned   | —                                                                             |

## Configuration

Create `.specops.json` in your project root. Configuration is optional — SpecOps uses sensible defaults.

```json
{
  "specsDir": ".specops",
  "team": {
    "conventions": ["Use TypeScript", "Write tests for business logic"],
    "reviewRequired": true,
    "specReview": { "enabled": true, "minApprovals": 2 }
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto"
  }
}
```

See [examples/](examples/) for minimal, standard, and full configurations. Full schema reference in [REFERENCE.md](REFERENCE.md).

### Vertical adaptation

SpecOps adapts templates to your project type. Set explicitly in `.specops.json` or let SpecOps auto-detect from your codebase.

| Vertical             | Adaptation                                               |
| -------------------- | -------------------------------------------------------- |
| **Backend**          | Default templates (API endpoints, services, data models) |
| **Frontend**         | State management, components, UI patterns                |
| **Full Stack**       | Handles both frontend and backend layers                 |
| **Infrastructure**   | Resource definitions, topology, IaC                      |
| **Data Engineering** | Pipeline stages, data flow, contracts                    |
| **Library/SDK**      | Public API surface, developer use cases                  |
| **Builder**          | Product modules, ship plans, cross-domain tasks          |

**Backend** / **Full Stack** — Use for API services, microservices, or full-stack web apps. Default templates apply unchanged; specs use standard "User Stories", "Component Design", and "API Changes" vocabulary. See [example: user-authentication](examples/specs/feature-user-authentication/).

**Frontend** — Use when the project is purely client-side (React, Vue, etc.) consuming existing APIs. Adapts design.md: "Data Model Changes" becomes "State Management"; "API Changes" is skipped when only consuming. See [example: dark-mode-toggle](examples/specs/feature-dark-mode-toggle/).

**Infrastructure** — Use for Terraform, Kubernetes, CloudFormation, or other IaC projects. Heavy adaptation: "User Stories" become "Infrastructure Requirements" (As an operator/SRE...), "Components" become "Resources", tasks gain "Validation Steps" and "Rollback Steps". See [example: k8s-autoscaling](examples/specs/feature-k8s-autoscaling/).

**Data Engineering** — Use for ETL pipelines, data warehouses, or streaming systems. Heavy adaptation: "User Stories" become "Data Requirements", "Components" become "Pipeline Stages", adds "Data Quality Requirements" and "Volume & Velocity" sections. See [example: user-activity-pipeline](examples/specs/feature-user-activity-pipeline/).

**Library/SDK** — Use for reusable packages, SDKs, or shared libraries. Medium adaptation: "User Stories" become "Developer Use Cases" (As a developer...), "Components" become "Modules", adds "API Design Principles", "Compatibility Requirements", and "Breaking Change" flags per task. See [example: date-utils-library](examples/specs/feature-date-utils-library/).

**Builder** — Use when you are a solo builder or small team shipping a product end-to-end across multiple domains (frontend, backend, infra, data). Heaviest adaptation: "User Stories" become "Product Requirements" (framed around product outcomes), "Components" become "Product Modules", adds mandatory "Scope Boundary" section, tasks tagged with "Domain" and "Ship Blocking" flags. Includes an explicit simplicity guardrail to keep specs lean despite broad scope. See [example: task-management-saas](examples/specs/feature-task-management-saas/).

#### Full Stack vs Builder — which one should I use?

Both verticals handle work that spans frontend and backend, but they serve different mindsets:

| | **Full Stack** | **Builder** |
|---|---|---|
| **Scope** | Frontend + backend code | Frontend + backend + infra + data + DevOps + anything the product needs |
| **Perspective** | Implementation layers — "what code goes where" | Product outcomes — "what ships and when" |
| **Templates** | Default, unchanged — standard User Stories, Component Design, API Changes | Product-centric — Product Requirements, Product Modules, Integration Points, Ship Plan |
| **Task structure** | Standard tasks grouped by implementation order | Tasks tagged by **Domain** (frontend, backend, infra, data) with **Ship Blocking** flags |
| **Scope control** | Standard spec sections | Mandatory **Scope Boundary** section (v1 vs. deferred) to prevent scope creep |
| **Best for** | Adding a feature to an existing app where infra and deployment are already handled | Building a new product from scratch where you own everything from UI to deployment |

**Rule of thumb:** If someone else handles your infrastructure, CI/CD, and deployment — use **Full Stack**. If you are the infrastructure, CI/CD, and deployment — use **Builder**.

## Architecture

<p align="center">
  <img src="assets/architecture.svg" alt="SpecOps three-layer architecture: core, generator, platforms" width="800"/>
</p>

Three layers, strict separation:

- **`core/`** — Platform-agnostic workflow, templates, and safety rules (single source of truth)
- **`generator/`** — Builds platform-specific outputs from core + platform adapters
- **`platforms/`** — Generated instruction files per platform (checked into git, no build step for users)

See [STRUCTURE.md](STRUCTURE.md) for the full repository layout.

## Simplicity Principle

SpecOps follows a core design principle: **prefer the simplest solution that meets requirements**.

- Specs scale to the task — a small feature does not generate a full rollout plan
- No speculative complexity — no premature abstractions, no "future-proofing"
- Use what exists — prefer existing project patterns over inventing new ones

Red flags the agent actively avoids: abstractions used only once, error handling for impossible scenarios, configuration for unchanging values, designing for hypothetical futures.

## Security

- Convention strings and custom templates are sanitized against prompt injection
- Secrets use placeholders, PII uses synthetic data
- All schema fields have validation constraints (`maxLength`, `maxItems`, `additionalProperties: false`)
- Paths are contained — rejects absolute paths and `../` traversal
- Security audited with no high-confidence vulnerabilities found ([full report](SECURITY-AUDIT.md))

For vulnerability reporting, see [SECURITY.md](SECURITY.md).

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
