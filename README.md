# SpecOps

**Spec-driven development that adapts to your stack, your team, and your workflow.**

[![CI](https://github.com/sanmak/specops/actions/workflows/ci.yml/badge.svg)](https://github.com/sanmak/specops/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/sanmak/specops)](https://github.com/sanmak/specops/releases)
[![GitHub Stars](https://img.shields.io/github/stars/sanmak/specops?style=social)](https://github.com/sanmak/specops)
[![License: MIT](https://img.shields.io/github/license/sanmak/specops)](https://github.com/sanmak/specops/blob/main/LICENSE)

SpecOps brings structured spec-driven development to your AI coding assistant — with domain-specific templates for infrastructure, data pipelines, and SDKs, and a built-in team review workflow for shared codebases. Works with **Claude Code**, **Cursor**, **OpenAI Codex**, and **GitHub Copilot**.

## Why SpecOps

### Specs built for your project type

Infrastructure specs include Rollback Steps and Resource Definitions. Data pipeline specs include Data Contracts and Backfill Strategy. Library specs flag Breaking Changes per task. Backend and fullstack use clean defaults — no unnecessary ceremony.

### Spec review before code ships

Draft a spec, get section-by-section feedback from teammates, revise, and only implement once `minApprovals` is met. Git identity detection, configurable approval thresholds, and an implementation gate that blocks unapproved specs from proceeding.

### One command, nothing to install

`curl | bash`. No Python, no uv, no package manager setup. SpecOps installs as a skill file your AI coding assistant reads — there is no runtime to maintain.

### Specs are prompts — treated with security rigor

Convention strings and custom templates are sanitized against prompt injection. Secrets use placeholders, PII uses synthetic data, all config fields enforce strict schema validation, and path traversal is rejected at the boundary.

### Specs that scale to the task

Small features get lean specs. The agent actively avoids premature abstractions, one-use configurations, and speculative future-proofing. Over-engineering patterns are flagged as red flags during spec creation.

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

## Troubleshooting

### SpecOps skill not found / incomplete spec output

**Symptom:** SpecOps runs but skips creating `spec.json` / `index.json`, or the workflow behavior seems improvised rather than following the standard phases.

**Cause:** Your project has `.claude/` in `.gitignore`, so the installed `SKILL.md` is silently ignored by git (and sometimes by your AI editor). Your AI assistant falls back to its own understanding instead of the SpecOps workflow, leading to incomplete or incorrect output.

**Fix — Option 1: Use user-level installation (recommended)**

User-level installation puts SpecOps in `~/.claude/skills/specops/`, which is unaffected by your project's `.gitignore`:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh) --platform claude --scope user
```

This makes SpecOps available in all your projects globally, and your team members install independently.

**Fix — Option 2: Selectively un-ignore .claude/skills/**

If you want project-level installation (to distribute it with your repo), add this line to your project's `.gitignore`:

```
!.claude/skills/
```

This keeps the SpecOps skill tracked in git while ignoring other `.claude/` config:

```gitignore
# Ignore Claude Code local session state
.claude/
# But track the SpecOps skill for the team
!.claude/skills/
```

Then reinstall: `bash setup.sh` and choose "project" installation.

---

## How It Works

<p align="center">
  <img src="assets/workflow.svg" alt="SpecOps 4-phase workflow with optional interview mode: Understand, Spec, Implement, Complete" width="900"/>
</p>

One command triggers a 4-phase workflow: understand your codebase, generate a structured spec, implement it, and verify the result. For vague or high-level ideas, an optional interview mode gathers structured requirements before spec generation.

### Interview Mode (Optional)

When your idea is still forming or you want to refine requirements before specs, SpecOps can guide you through a structured interview:

<p align="center">
  <img src="assets/interview-workflow.svg" alt="SpecOps interview mode: gathering questions → clarifying vague answers → confirming summary → proceeding to Phase 1" width="900"/>
</p>

**How to use:**
- **Explicit**: `/specops interview I want to build something for restaurants`
- **Auto-trigger**: Say something vague like "I have an idea" and SpecOps detects it (≤5 words, no technical keywords)

The interview asks 5 structured questions with smart follow-ups:
1. **Problem** - What are you solving?
2. **Users** - Who benefits?
3. **Features** - What are the 2–3 core capabilities?
4. **Constraints** - Tech stack, integrations, timelines?
5. **Done Criteria** - How do you know it's complete?

Once you approve the summary, SpecOps proceeds to Phase 1 with the enriched context, producing better specs for unclear or exploratory work.

*Non-interactive platforms (Codex) skip interview mode and proceed with best-effort spec generation.*

### Team Review Workflow

<p align="center">
  <img src="assets/review-workflow.svg" alt="SpecOps collaborative review workflow: draft, review, revise, approve, implement" width="800"/>
</p>

For teams, SpecOps adds a structured review cycle between spec creation and implementation. Engineers review specs collaboratively, provide section-by-section feedback, and approve before coding begins. See [TEAM_GUIDE.md](TEAM_GUIDE.md) for the full team workflow.

## What Gets Created

<p align="center">
  <img src="assets/spec-structure.svg" alt="SpecOps generates spec.json, requirements.md, design.md, tasks.md, and optional implementation.md and reviews.md" width="700"/>
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

## How SpecOps Compares

SpecOps and [Spec Kit](https://github.com/github/spec-kit) share the same core philosophy: specs before code. We think Spec Kit is excellent — and we're building on the same principles with a different focus.

**Choose Spec Kit** if you want the broadest agent support (18+) and are exploring SDD as an individual or small team.

**Choose SpecOps** if you're a team shipping to production and need specs that match your project type, structured review before implementation, and security-hardened spec processing.

| Capability | SpecOps | GitHub Spec Kit |
|---|---|---|
| **Supported platforms** | Claude Code, Cursor, OpenAI Codex, GitHub Copilot | 18+ agents |
| **Installation** | Single `curl \| bash`, no dependencies | Python 3.11+ and uv |
| **Team review workflow** | Built-in (draft → review → revise → approve → gate) | Not available |
| **Configurable approval thresholds** | Yes — `minApprovals` in config | Not available |
| **Vertical-aware templates** | 7 project types (infra, data, library, builder, etc.) | Generic templates |
| **Infrastructure specs** | Rollback steps, topology, resource definitions | Generic |
| **Data pipeline specs** | Data contracts, backfill strategy, pipeline SLAs | Generic |
| **Library/SDK specs** | Breaking change flags, public API surface | Generic |
| **Simplicity guardrails** | Built-in anti-over-engineering checks | Not available |
| **Security hardening** | Prompt injection defense, schema validation, path containment | Not documented |
| **Monorepo support** | Per-module config overrides | Not documented |
| **Platform breadth** | 4 platforms | 18+ platforms |
| **Research workflow** | Planned | Yes |
| **EARS-style requirements** | Planned | Yes |

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

SpecOps is the only spec-driven development tool with domain-specific templates. It adapts spec structure, vocabulary, and required sections based on your project type. Set explicitly in `.specops.json` or let SpecOps auto-detect from your codebase.

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

Specs are prompts — they can contain user-supplied content that reaches the agent context. SpecOps treats spec inputs with the same security discipline as any prompt surface.

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
