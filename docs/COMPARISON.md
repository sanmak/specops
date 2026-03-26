# SpecOps vs Alternatives

How SpecOps compares to other spec-driven and agent-context tools.

## Feature Matrix

| Capability | SpecOps | Superpowers | Kiro (Amazon) | EPIC/Reload | GitHub Spec Kit |
| --- | --- | --- | --- | --- | --- |
| **Spec-driven workflow** | 4-phase (Understand, Spec, Implement, Complete) | Implicit skill chain (brainstorm, plan, execute; no phases or state tracking) | 3-phase (Requirements, Design, Tasks) | Memory layer (no spec workflow) | 5 core commands (specify, plan, tasks, implement, constitution) + 3 optional commands |
| **Platform support** | Claude Code, Cursor, Codex, Copilot, Google Antigravity | Claude Code, Cursor, Codex, OpenCode, Gemini CLI | IDE + CLI + ACP-compatible editors (JetBrains, Zed) | Cursor, Windsurf | 26+ named agents + generic |
| **EARS notation** | Yes (5 patterns, HTML comment guidance) | No | Yes | No | No |
| **Regression analysis** | Yes (severity-scaled discovery) | No | Yes (SHALL CONTINUE TO) | No | No |
| **Steering files** | Yes (always, fileMatch, manual modes) | No (SessionStart hook only) | Yes (+ auto mode) | No | No |
| **Local memory** | Yes (decisions, context, patterns) | No (fresh context each session) | Autonomous agent retains context (no structured memory files) | Yes (cloud-based) | Constitution (project principles, not cross-session learning) |
| **Repo map** | Yes (AST-based, auto-refresh) | No | Code Intelligence with AST navigation (Tree-sitter, 18 languages) | No | No |
| **Production learnings** | Yes (capture, supersession chains, 5-layer retrieval, reconsider-when triggers) | No | No | No | No |
| **Drift detection** | Yes (5 drift checks, audit/reconcile) | No | No | No | Community extensions ("reconcile", "sync") |
| **Spec decomposition** | Yes (scope assessment, split detection, initiatives) | No | No | No | No |
| **Initiative orchestration** | Yes (multi-spec execution with dependency gates) | No | No | No | No |
| **Vertical adaptations** | 7 project types | None | None | None | Generic templates |
| **Team review workflow** | Built-in (draft, review, approve, gate) | No | No | No | Community extension ("review") |
| **Agent hooks** | Yes (ExitPlanMode) | Yes (SessionStart hook injection) | Yes (10 trigger types) | No | Yes (before/after hooks on all core commands) |
| **Subagent architecture** | Phase dispatch + initiative orchestrator | Dispatcher + spec reviewer + code reviewer per task | Up to 4 parallel subagents, isolated contexts | No | Community extension ("conduct") |
| **TDD enforcement** | Acceptance criteria as completion gates | Anti-rationalization tables, strict test-first mandate | No | No | Yes (TDD in core implement command) |
| **Visual brainstorming** | No | Yes (browser-based mockup companion) | No | No | No |
| **MCP integration** | No | No | Yes | No | No |
| **Design-first workflow** | No | No | Yes | No | No |
| **Security hardening** | Yes (injection defense, path containment, PII prevention) | No | Enterprise governance (tool trust, MCP registry); no spec-level hardening | No | No |
| **Storage model** | Local files, git-tracked | Local files, flat skill directories | Local files | Cloud service | Local files |
| **Open source** | Yes (MIT) | Yes (MIT) | No (proprietary) | No (funded startup) | Yes |

## SpecOps vs Superpowers

[Superpowers](https://github.com/obra/superpowers) is a behavioral methodology framework for AI coding agents with 103k+ GitHub stars (as of 2026-03-22)[^sp-stars], officially listed in the Claude Code plugin marketplace[^sp-marketplace]. Both tools make AI agents think before coding, but they deliver different things to the developer. SpecOps gives you structured spec documents (requirements, design, tasks) that persist in git, track progress across sessions, and catch drift between what was specified and what was built. Superpowers gives you behavioral guardrails: strict TDD enforcement, systematic debugging methodology, and multi-agent code review where separate agents check spec compliance and code quality. They are complementary: a team could use Superpowers' TDD discipline during implementation and SpecOps' structured specs as the planning foundation.

**Choose Superpowers** if you want your agent to follow strict TDD (test before code, no exceptions), run systematic debugging workflows, dispatch separate reviewer agents for each task, or brainstorm visually in the browser.

**Choose SpecOps** if you want persistent spec documents that survive sessions, automatic detection when code drifts from the spec, domain-specific templates for your project type, team review with approval gates before coding starts, or multi-spec coordination when features span multiple bounded contexts.

### Where Superpowers leads

- **Multi-agent code review**: every task gets reviewed by two separate agents (one checks spec compliance, one checks code quality) before it's considered done. In SpecOps, you review the output yourself or through a team review workflow.
- **TDD enforcement**: the agent writes the test first. Always. If it writes production code before a failing test, the skill instructs it to delete the code and start over. SpecOps verifies acceptance criteria at the end but does not enforce test-first order during implementation.
- **Visual brainstorming**: opens a browser-based companion where you see mockups and diagrams while discussing design. SpecOps produces text-based spec documents only.
- **Parallel task execution**: independent tasks run simultaneously in separate git worktrees, each handled by a fresh agent. SpecOps' initiative orchestrator runs specs in dependency order but executes them sequentially within each wave.
- **Systematic debugging**: when you hit a bug, the agent follows a structured 4-phase process (investigate, analyze patterns, test hypotheses, implement fix) instead of guessing. SpecOps has a bugfix spec template focused on regression analysis, not a debugging methodology.
- **Platform breadth**: runs on 5 platforms (Claude Code, Cursor, Codex, OpenCode, Gemini CLI). SpecOps runs on 5 (Claude Code, Cursor, Codex, Copilot, Google Antigravity).
- **Adoption**: 103k+ GitHub stars (as of 2026-03-22)[^sp-stars], officially listed in the Claude Code plugin marketplace[^sp-marketplace].

### Where SpecOps leads

- **Specs that persist and track progress**: requirements.md, design.md, and tasks.md are git-tracked files with lifecycle states (draft, review, approved, implementing, completed). You can close your terminal, come back next week, and resume exactly where you left off. Superpowers produces free-form docs with no lifecycle tracking; context resets each session.
- **Drift detection**: after implementation, SpecOps checks whether what you built matches what you specified. Five automated checks catch spec-code divergence, stale specs, and orphaned implementations. Superpowers has no drift detection because its design docs are free-form text with no structure to compare against.
- **Local memory**: decisions, context, and patterns from completed specs are saved and loaded automatically in future sessions. Your agent remembers what was decided and why. Superpowers starts fresh every session.
- **EARS requirements**: acceptance criteria use five patterns (event-driven, state-driven, optional, unwanted, ubiquitous) that produce testable statements like `WHEN [event] THE SYSTEM SHALL [behavior]`. Superpowers uses free-form requirements.
- **Domain-specific templates**: seven project types (backend, frontend, infra, data pipeline, library, fullstack, builder) generate spec sections relevant to your domain. An infra spec includes rollback steps; a data pipeline spec includes data contracts. Superpowers applies the same workflow regardless of project type.
- **Team review before coding**: specs go through a draft/review/approve cycle with configurable approval counts before implementation begins. Superpowers has no team review mechanism.
- **Multi-spec coordination**: large features are automatically assessed for scope and split into multiple specs with dependency tracking, execution waves, and initiative dashboards. Superpowers can parallelize independent tasks but has no initiative-level planning, dependency gates, or execution waves across specs.
- **Writing and engineering discipline**: spec artifacts follow traceable rules grounded in named thought leaders (Orwell on clarity, Kent Beck on testing, Dijkstra on proof limits, Brooks on design integrity). Every requirement is ANT-tested for falsifiability. Superpowers' anti-rationalization tables enforce agent behavior but do not apply a writing or engineering methodology to the artifacts produced.

## SpecOps vs Kiro

[Kiro](https://kiro.dev/) is Amazon's IDE with built-in spec-driven development. Both tools share the core philosophy of specs before code. Kiro has expanded significantly since its launch, adding a CLI, ACP editor compatibility, subagents, an autonomous agent, and enterprise governance features.

**Choose Kiro** if you want an integrated IDE experience with agent hooks (event-driven automation), design-first workflows, MCP integration, or enterprise governance controls.

**Choose SpecOps** if you need platform independence across multiple AI coding tools, domain-specific templates, team review workflows, drift detection, multi-spec coordination, or want your spec tooling to be open source and git-tracked with no vendor lock-in.

### Where SpecOps leads

- **Platform independence**: SpecOps works natively in Claude Code, Cursor, Codex, Copilot, and Google Antigravity from a single install. Kiro extends beyond its IDE to a CLI and ACP-compatible editors (JetBrains, Zed) but remains centered on the Kiro ecosystem.
- **Vertical adaptations**: 7 domain-specific template sets (infra, data, library, backend, frontend, fullstack, builder). Kiro has Powers bundles for specific AWS services, but no general project-type adaptations.
- **Drift detection**: 5 automated drift checks with audit/reconcile subcommands. Kiro has no drift detection.
- **Spec decomposition**: large features are automatically split into coordinated specs with dependency tracking, execution waves, and initiative orchestration. Kiro has no multi-spec coordination.
- **Team review**: structured review workflow with approval gates, self-review for solo devs. Kiro has no team review mechanism.
- **Refactor specs**: dedicated spec type Kiro does not offer.
- **Security**: spec-level prompt injection defense, path containment, and PII prevention. Kiro offers enterprise governance (tool trust, MCP registry, model governance) but no spec-level hardening.
- **Local memory**: persistent decisions, context, and patterns saved as structured files and loaded each session. Kiro's autonomous agent retains context across tasks but does not produce structured memory files.
- **Writing and engineering discipline**: spec artifacts grounded in named thought leaders (Orwell, Beck, Dijkstra, Brooks). Kiro generates specs with EARS but does not apply a traceable writing or engineering methodology.

### Where Kiro leads

- **Agent hooks**: 10 trigger types (file events, agent lifecycle, task events) with chaining and Pre/Post Tool Use hooks. SpecOps has 1 hook (ExitPlanMode auto-trigger).
- **Design-first workflow**: start from technical architecture, derive requirements.
- **MCP integration**: connect to external tools, databases, APIs through MCP servers.
- **Subagents**: up to 4 parallel subagents with isolated contexts, automatically selected based on the task. SpecOps dispatches fresh contexts per phase and task but does not auto-select agent type.
- **Autonomous agent**: handles long-running tasks asynchronously across multiple repos, creates PRs, and learns from code review feedback (preview, paid tiers).
- **AST-based code editing**: structural edits using Tree-sitter with typed operations across 18 languages.
- **Powers ecosystem**: curated bundles of MCP servers, steering files, and hooks for specific AWS services (SAM, Lambda, IAM, CloudWatch).
- **Enterprise governance**: organizations control approved MCP servers, model lists, and tool trust scoping. GovCloud support in progress.
- **Spec referencing**: `#spec` in chat to reference any spec inline.
- **Multimodal input**: upload UI designs, whiteboard photos, and documents (PDF, CSV, DOC, XLSX, HTML; up to 5 per message).

## SpecOps vs EPIC/Reload

[EPIC/Reload](https://www.epicai.dev/) is a funded startup ($2.275M pre-seed)[^epic-funding] building a "memory and architecture layer for coding agents." EPIC launched in February 2026 and currently supports Cursor and Windsurf.

**Choose EPIC** if you want a managed cloud service for agent memory.

**Choose SpecOps** if you want spec-driven development with local, git-tracked memory and no cloud dependency.

### Key differences

- **Scope**: SpecOps is a complete spec workflow (requirements, design, tasks, review, implementation). EPIC is a memory/context layer without a spec workflow.
- **Storage**: SpecOps stores everything in local files committed to git. EPIC uses a cloud service.
- **Memory**: Both offer persistent memory across sessions. SpecOps stores decisions, context, and patterns locally. EPIC stores memories in the cloud.
- **Vendor lock-in**: SpecOps is MIT-licensed, file-based, no account required. EPIC requires a cloud account.

## SpecOps vs GitHub Spec Kit

[Spec Kit](https://github.com/github/spec-kit) is GitHub's open-source spec-driven development framework with 80k+ stars and 100+ contributors (as of 2026-03-22)[^sk-stats]. It has evolved rapidly, adding an extension marketplace (22 community extensions), a hook lifecycle, a preset system, and a constitution command for persistent project principles.

**Choose Spec Kit** if you need the broadest agent support (26+), a community extension ecosystem, or are exploring spec-driven development as an individual or small team.

**Choose SpecOps** if you need domain-specific templates, team review, built-in drift detection, structured cross-session memory, security hardening, or multi-spec coordination.

| Capability | SpecOps | GitHub Spec Kit |
| --- | --- | --- |
| Supported platforms | 4 (Claude Code, Cursor, Codex, Copilot) | 26+ named agents + generic |
| Installation | Plugin marketplace or `curl \| bash` | Python 3.11+ and uv |
| Team review workflow | Built-in | Community extension ("review") |
| Vertical-aware templates | 7 project types | Generic (preset system exists, no official vertical presets) |
| Security hardening | Yes | Not documented |
| Steering files | Yes | No |
| Memory layer | Yes (auto-write after specs, auto-load each session) | Constitution (one-time project principles) |
| Drift detection | Yes (built-in, 5 checks) | Community extensions ("reconcile", "sync") |
| Agent hooks | Yes (ExitPlanMode) | Yes (before/after hooks on all core commands) |
| Extension ecosystem | No | Yes (22 community extensions) |
| TDD enforcement | Acceptance criteria as completion gates | Yes (TDD in core implement command) |

### Where Spec Kit leads

- **Agent breadth**: 26+ named agents and a generic option for bring-your-own-agent. SpecOps supports 5 platforms.
- **Extension marketplace**: 22 community extensions covering drift detection, code review, sub-agent delegation, fleet orchestration, and issue tracker integrations (Jira, Azure DevOps). SpecOps has no extension system.
- **Hook lifecycle**: before/after hooks on all core commands. SpecOps has one hook (ExitPlanMode).
- **Community**: 80k+ stars, 100+ contributors, active release cadence (v0.3.2, shipping every 2-3 days) (as of 2026-03-22)[^sk-stats].
- **Preset system**: customize templates without writing extensions.
- **TDD in core**: implement command follows a TDD approach by default.

### Where SpecOps leads

- **Built-in drift detection**: 5 automated checks are a core capability, not a community extension that may or may not be maintained.
- **Structured memory**: decisions, context, and patterns are auto-written after specs and auto-loaded each session. Spec Kit's constitution is a one-time project principles document without cross-session learning.
- **EARS notation**: 5 requirement patterns producing testable acceptance criteria. Not available in Spec Kit.
- **Regression analysis**: severity-scaled discovery for bugfix specs. Not available in Spec Kit.
- **Steering files**: convention-based guidance files with always, fileMatch, and manual modes. Not available in Spec Kit.
- **Security hardening**: spec-level prompt injection defense, path containment, PII prevention. Not documented in Spec Kit.
- **Spec decomposition**: automatic scope assessment, split detection, initiative orchestration with dependency gates. Not available in Spec Kit core.
- **Writing and engineering discipline**: spec artifacts grounded in named thought leaders with ANT/OAT testing for every requirement. Spec Kit uses generic templates.

## Dogfood Proof

SpecOps was used to build itself across 6 features in a public dogfood cycle. Every feature (EARS notation, regression analysis, steering files, drift detection, local memory, and AST-based repo map) was specified, designed, implemented, and verified using the SpecOps workflow. The specs live in [`.specops/`](../.specops/) and the friction log documenting 42 lessons learned is in [`internal/dogfood-friction.md`](../internal/dogfood-friction.md).

[^sp-stars]: <https://github.com/obra/superpowers> (retrieved 2026-03-22)
[^sp-marketplace]: <https://claude.com/plugins/superpowers> (retrieved 2026-03-22)
[^epic-funding]: <https://theaiinsider.tech/2026/02/24/reload-closes-2-275m-in-funding-and-launches-epic-to-manage-ai-agents-as-a-digital-workforce/> (retrieved 2026-03-22)
[^sk-stats]: <https://github.com/github/spec-kit> (retrieved 2026-03-22)
