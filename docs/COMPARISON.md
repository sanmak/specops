# SpecOps vs Alternatives

How SpecOps compares to other spec-driven and agent-context tools.

## Feature Matrix

| Capability | SpecOps | Kiro (Amazon) | EPIC/Reload | GitHub Spec Kit |
| --- | --- | --- | --- | --- |
| **Spec-driven workflow** | 4-phase (Understand, Spec, Implement, Complete) | 3-phase (Requirements, Design, Tasks) | Memory layer (no spec workflow) | 3-phase (similar to Kiro) |
| **Platform support** | Claude Code, Cursor, Codex, Copilot | Kiro IDE only | IDE-specific | 18+ agents |
| **EARS notation** | Yes (5 patterns, HTML comment guidance) | Yes | No | No |
| **Regression analysis** | Yes (severity-scaled discovery) | Yes (SHALL CONTINUE TO) | No | No |
| **Steering files** | Yes (always, fileMatch, manual modes) | Yes (+ auto mode) | No | No |
| **Local memory** | Yes (decisions, context, patterns) | No | Yes (cloud-based) | No |
| **Repo map** | Yes (AST-based, auto-refresh) | No | No | No |
| **Drift detection** | Yes (5 drift checks, audit/reconcile) | No | No | No |
| **Vertical adaptations** | 7 project types | None | None | Generic templates |
| **Team review workflow** | Built-in (draft, review, approve, gate) | No | No | No |
| **Agent hooks** | Yes (ExitPlanMode) | Yes (10 trigger types) | No | No |
| **MCP integration** | No | Yes | No | No |
| **Design-first workflow** | No | Yes | No | No |
| **Security hardening** | Yes (injection defense, schema validation, path containment) | No | No | No |
| **Storage model** | Local files, git-tracked | Local files | Cloud service | Local files |
| **Open source** | Yes (MIT) | No (proprietary IDE) | No (funded startup) | Yes |

## SpecOps vs Kiro

[Kiro](https://kiro.dev/) is Amazon's IDE with built-in spec-driven development. Both tools share the core philosophy of specs before code.

**Choose Kiro** if you work in a single IDE and want agent hooks (event-driven automation) or design-first workflows.

**Choose SpecOps** if you need multi-platform support, domain-specific templates, team review workflows, drift detection, or want your spec tooling to be open source and git-tracked with no vendor lock-in.

### Where SpecOps leads

- **Multi-platform**: 4 platforms from a single source of truth vs Kiro's single IDE
- **Vertical adaptations**: 7 domain-specific template sets (infra, data, library, backend, frontend, fullstack, builder) vs none
- **Drift detection**: 5 automated drift checks with audit/reconcile subcommands
- **Team review**: Structured review workflow with approval gates, self-review for solo devs
- **Refactor specs**: Dedicated spec type Kiro doesn't offer
- **Security**: Convention sanitization, prompt injection defense, path containment, PII prevention
- **Local memory**: Persistent decisions, context, and patterns extracted from completed specs
- **Repo map**: AST-based structural map with staleness detection, auto-refresh

### Where Kiro leads

- **Agent hooks**: 10 trigger types (file events, agent lifecycle, task events) with chaining vs SpecOps' 1 (ExitPlanMode auto-trigger)
- **Design-first workflow**: Start from technical architecture, derive requirements
- **MCP integration**: Connect to external tools, databases, APIs
- **Spec referencing**: `#spec` in chat to reference any spec inline
- **Multimodal input**: Upload UI designs and whiteboard photos

## SpecOps vs EPIC/Reload

[EPIC/Reload](https://www.epicai.dev/) is a funded startup ($2.275M) building a "memory and architecture layer for coding agents."

**Choose EPIC** if you want a managed cloud service for agent memory.

**Choose SpecOps** if you want spec-driven development with local, git-tracked memory and no cloud dependency.

### Key differences

- **Scope**: SpecOps is a complete spec workflow (requirements, design, tasks, review, implementation). EPIC is a memory/context layer without a spec workflow.
- **Storage**: SpecOps stores everything in local files committed to git. EPIC uses a cloud service.
- **Memory**: Both offer persistent memory across sessions. SpecOps stores decisions, context, and patterns locally. EPIC stores memories in the cloud.
- **Vendor lock-in**: SpecOps is MIT-licensed, file-based, no account required. EPIC requires a cloud account.

## SpecOps vs GitHub Spec Kit

[Spec Kit](https://github.com/github/spec-kit) is GitHub's open-source spec-driven development framework.

**Choose Spec Kit** if you need the broadest agent support (18+) and are exploring SDD as an individual or small team.

**Choose SpecOps** if you need domain-specific templates, team review, security hardening, or persistent project memory.

| Capability | SpecOps | GitHub Spec Kit |
| --- | --- | --- |
| Supported platforms | 4 (Claude Code, Cursor, Codex, Copilot) | 18+ agents |
| Installation | Plugin marketplace or `curl \| bash` | Python 3.11+ and uv |
| Team review workflow | Built-in | Not available |
| Vertical-aware templates | 7 project types | Generic templates |
| Security hardening | Yes | Not documented |
| Steering files | Yes | No |
| Memory layer | Yes | No |
| Drift detection | Yes | No |

## Dogfood Proof

SpecOps was used to build itself across 6 features in a public dogfood cycle. Every feature — EARS notation, regression analysis, steering files, drift detection, local memory, and AST-based repo map — was specified, designed, implemented, and verified using the SpecOps workflow. The specs live in [`.specops/`](../.specops/) and the friction log documenting 42 lessons learned is in [`internal/dogfood-friction.md`](../internal/dogfood-friction.md).
