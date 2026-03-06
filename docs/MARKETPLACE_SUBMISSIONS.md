# Marketplace Submission Content

Copy-paste-ready content for submitting SpecOps to each platform's marketplace.

---

## Claude Code (Anthropic Plugin Marketplace)

**Submission URL**: https://claude.ai/settings/plugins/submit (or platform.claude.com/plugins/submit)

| Field | Value |
|-------|-------|
| **Name** | specops |
| **Version** | 1.1.0 |
| **Repository** | https://github.com/sanmak/specops |
| **Homepage** | https://github.com/sanmak/specops |
| **License** | MIT |
| **Category** | development-workflows |
| **Tags** | spec-driven, workflow, planning, requirements, design, tasks |

**Short Description** (one line):
> Spec-driven development workflow — transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps brings structured spec-driven development to Claude Code. One command triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Features:
> - Domain-specific templates for backend, frontend, fullstack, infrastructure, data pipelines, libraries, and builder projects
> - Built-in team review workflow with configurable approval thresholds
> - Security-hardened spec processing (prompt injection defense, schema validation, path containment)
> - Optional interview mode for vague or exploratory ideas
> - Spec viewing, listing, and status tracking
>
> Commands: `/specops`, `/specops:init`

**Install command**: `/install github:sanmak/specops`

---

## Cursor Marketplace

**Submission URL**: https://cursor.com/marketplace/publish

| Field | Value |
|-------|-------|
| **Name** | SpecOps |
| **Category** | Development Workflows |
| **Rule file** | `platforms/cursor/specops.mdc` |
| **Repository** | https://github.com/sanmak/specops |

**Short Description**:
> Spec-driven development workflow — transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to Cursor. Say "Use specops to add user authentication" and it triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Adapts to your project type (backend, frontend, fullstack, infrastructure, data pipelines, libraries). Includes team review workflow, security-hardened processing, and optional interview mode for exploratory ideas.
>
> Trigger with: "Use specops to ...", "Create a spec for ...", or mention "spec-driven development".

---

## OpenAI Codex Skills Catalog

**Submission URL**: https://developers.openai.com/codex/skills/ (or Codex CLI submission portal)

| Field | Value |
|-------|-------|
| **Name** | specops |
| **Skill directory** | `.codex/skills/specops/` |
| **Skill file** | `platforms/codex/SKILL.md` |
| **Repository** | https://github.com/sanmak/specops |

**Short Description**:
> Spec-driven development workflow — transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to OpenAI Codex. Say "Use specops to add user authentication" and it generates structured specs (requirements, design, tasks) before implementing.
>
> Codex-specific: runs autonomously without interactive prompts. Documents assumptions in spec files. For reviews, include all feedback and verdict directly in the prompt.
>
> Supports 7 project verticals, team review workflow, and security-hardened spec processing.

---

## GitHub Copilot Extensions Marketplace

**Submission URL**: GitHub Copilot Extensions marketplace (via GitHub Marketplace or partner portal)

| Field | Value |
|-------|-------|
| **Name** | specops |
| **Instructions file** | `platforms/copilot/specops.instructions.md` |
| **Install path** | `.github/instructions/specops.instructions.md` |
| **Repository** | https://github.com/sanmak/specops |

**Short Description**:
> Spec-driven development workflow — transforms ideas into structured specifications before implementation.

**Full Description**:
> SpecOps adds spec-driven development to GitHub Copilot. Say "Use specops to add user authentication" and it triggers a 4-phase workflow: understand your codebase, generate a structured spec (requirements, design, tasks), implement it, and verify the result.
>
> Works in Copilot's chat interface with interactive clarification. Adapts to 7 project types, includes team review workflow with approval gates, and security-hardened spec processing.

---

## Common Assets

**Logo/Icon**: Use the SpecOps repository social preview or create from repo assets.

**Screenshots to include**:
1. A spec being created (`/specops Add user authentication`)
2. The generated spec structure (requirements.md, design.md, tasks.md)
3. The interview mode in action
4. Team review workflow

**Keywords for SEO**: spec-driven development, specification workflow, AI coding assistant, structured development, requirements engineering, design documents, task breakdown
