# Marketplace Submission Content

Copy-paste-ready content for submitting SpecOps to each platform's marketplace.

---

## Claude Code (Anthropic Plugin Marketplace)

**Submission URL**: <https://claude.ai/settings/plugins/submit> (or platform.claude.com/plugins/submit)

| Field | Value |
| ------- | ------- |
| **Name** | specops |
| **Version** | 1.7.0 |
| **Repository** | <https://github.com/sanmak/specops> |
| **Homepage** | <https://github.com/sanmak/specops> |
| **License** | MIT |
| **Category** | development-workflows |
| **Tags** | spec-driven, workflow, planning, requirements, design, tasks |

**Short Description** (one line):
> Spec-driven development workflow -- transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps brings structured spec-driven development to Claude Code. One command triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Features:
>
> - Domain-specific templates for 8 project verticals (backend, frontend, fullstack, infrastructure, data, library, builder, migration)
> - Automatic spec decomposition: large features split into coordinated specs with dependency tracking and initiative orchestration
> - Adversarial evaluation: separate evaluator scores spec quality (Phase 2) and implementation quality (Phase 4) against configurable thresholds
> - Production learnings: capture post-deployment discoveries, link to specs, surface in future work
> - EARS notation for precise, testable acceptance criteria
> - Steering files and local memory for persistent project context across sessions
> - Dependency introduction gate: 5-criteria evaluation before any new package install
> - Dependency safety scanning: CVE and EOL detection with configurable severity thresholds
> - Drift detection: 5 automated checks with audit and reconcile commands
> - Task delegation: fresh sub-agent contexts per task to prevent context exhaustion
> - Built-in team review workflow with configurable approval thresholds
> - Security-hardened spec processing (prompt injection defense, schema validation, path containment)
> - Optional interview mode for vague or exploratory ideas
>
> Commands: `/specops` (subcommands: `init`, `view`, `list`, `interview`, `steering`, `memory`, `learn`, `map`, `audit`, `pipeline`, `initiative`, `from-plan`, `feedback`, `version`, `update`)

**Install commands**:

```text
/plugin marketplace add sanmak/specops
/plugin install specops@specops-marketplace
/reload-plugins
```

---

## Cursor Marketplace

**Submission URL**: <https://cursor.com/marketplace/publish>

| Field | Value |
| ------- | ------- |
| **Name** | SpecOps |
| **Category** | Development Workflows |
| **Rule file** | `platforms/cursor/specops.mdc` |
| **Repository** | <https://github.com/sanmak/specops> |

**Short Description**:
> Spec-driven development workflow -- transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to Cursor. Say "Use specops to add user authentication" and it triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Adapts to 8 project verticals. Includes adversarial evaluation (scored quality gates), production learnings, EARS acceptance criteria, steering files for persistent context, dependency governance, drift detection, team review workflow, and automatic spec decomposition for large features spanning multiple subsystems.
>
> Trigger with: "Use specops to ...", "Create a spec for ...", or mention "spec-driven development".

---

## OpenAI Codex Skills Catalog

**Submission URL**: <https://developers.openai.com/codex/skills/> (or Codex CLI submission portal)

| Field | Value |
| ------- | ------- |
| **Name** | specops |
| **Skill directory** | `.codex/skills/specops/` |
| **Skill file** | `platforms/codex/SKILL.md` |
| **Repository** | <https://github.com/sanmak/specops> |

**Short Description**:
> Spec-driven development workflow -- transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to OpenAI Codex. Say "Use specops to add user authentication" and it generates structured specs (requirements, design, tasks) before implementing.
>
> Codex-specific: runs autonomously without interactive prompts. Documents assumptions in spec files. For reviews, include all feedback and verdict directly in the prompt.
>
> Supports 8 project verticals, adversarial evaluation, production learnings, EARS acceptance criteria, dependency governance, drift detection, team review workflow, and automatic decomposition of large features into coordinated multi-spec initiatives.

---

## GitHub Copilot Extensions Marketplace

**Submission URL**: GitHub Copilot Extensions marketplace (via GitHub Marketplace or partner portal)

| Field | Value |
| ------- | ------- |
| **Name** | specops |
| **Instructions file** | `platforms/copilot/specops.instructions.md` |
| **Install path** | `.github/instructions/specops.instructions.md` |
| **Repository** | <https://github.com/sanmak/specops> |

**Short Description**:
> Spec-driven development workflow -- transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to GitHub Copilot. Say "Use specops to add user authentication" and it triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Works in Copilot's chat interface with interactive clarification. Adapts to 8 project verticals, includes adversarial evaluation, production learnings, EARS acceptance criteria, dependency governance, drift detection, team review workflow with approval gates, and automatic decomposition of large features into coordinated multi-spec initiatives.

---

## Google Antigravity (Agents Rules)

**Submission URL**: Google Antigravity agent rules marketplace (if available)

| Field | Value |
| ------- | ------- |
| **Name** | specops |
| **Rules file** | `platforms/antigravity/specops.md` |
| **Install path** | `.agents/rules/specops.md` |
| **Repository** | <https://github.com/sanmak/specops> |

**Short Description**:
> Spec-driven development workflow -- transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to Google Antigravity. Say "Use specops to add user authentication" and it triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Supports multi-agent orchestration via Manager View with sub-agent delegation. Adapts to 8 project verticals, includes adversarial evaluation, production learnings, EARS acceptance criteria, dependency governance, drift detection, and automatic decomposition of large features into coordinated multi-spec initiatives.

---

## Common Assets

**Logo/Icon**: Use the SpecOps repository social preview or create from repo assets.

**Screenshots to include**:

1. A spec being created (`/specops Add user authentication`)
2. The generated spec structure (requirements.md, design.md, tasks.md)
3. The interview mode in action
4. Team review workflow

**Keywords for SEO**: spec-driven development, specification workflow, AI coding assistant, structured development, requirements engineering, design documents, task breakdown
