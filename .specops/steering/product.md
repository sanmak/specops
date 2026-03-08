---
name: "Product Context"
description: "What SpecOps builds, for whom, and competitive positioning"
inclusion: always
---

## Product Overview
SpecOps is a multi-platform spec-driven development workflow system. It transforms ideas into structured specifications (requirements, design, tasks) before implementation begins, giving AI coding assistants a repeatable, auditable process for software development.

## Target Users
Developers and teams using AI coding assistants (Claude Code, Cursor, Codex, GitHub Copilot) who want structured planning before implementation. Ranges from solo builders shipping MVPs to teams that need collaborative spec review workflows.

## Key Differentiators
- **Multi-platform**: Single source of truth generates output for 4 AI platforms from one codebase
- **Open source and file-based**: All specs are plain markdown files tracked in git — no cloud dependency, no vendor lock-in
- **Vertical adaptations**: Templates adapt vocabulary and structure for 6 domains (backend, frontend, infrastructure, data, library, builder)
- **Safety mechanisms**: Convention sanitization, path containment, template safety — defends against prompt injection in spec content
- **EARS notation**: Acceptance criteria use Easy Approach to Requirements Syntax for precision and testability

## Competitive Positioning
- vs **EPIC/Reload** ($2.275M raised): SpecOps is open source, file-based, no cloud lock-in. EPIC focuses on "memory layer" — SpecOps now has steering files for persistent context plus a local memory layer roadmap
- vs **Kiro** (Amazon): SpecOps is multi-platform (4 platforms), Kiro is single-IDE (VS Code). Both have EARS and steering files. SpecOps adds collaborative review workflows and vertical adaptations
