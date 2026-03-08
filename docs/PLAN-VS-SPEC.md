# Plan Mode vs Spec Mode

AI coding assistants ship with a "plan mode" — a read-only exploration phase before coding. SpecOps adds a "spec mode" on top. This guide explains when to use each and how they work together.

## The Problem Both Solve

Coding without thinking leads to rework. Both plan mode and spec mode address this by inserting a deliberate thinking step before implementation. The difference is in scope, persistence, and structure.

## What Plan Mode Gives You

Plan mode (available in Claude Code, Cursor, Copilot, and others) lets you explore a codebase and sketch an approach before writing code:

- **Read-only exploration** — search files, read code, understand patterns
- **Freeform planning** — draft an approach in natural language
- **Quick iteration** — adjust the plan through conversation
- **Zero overhead** — no files created, no config needed

Plan mode is excellent for tactical decisions: "How should I implement this function?" or "What's the best way to refactor this module?"

**Limitation**: The plan lives in your conversation context. Close the session and it's gone. Switch to a teammate and they start from scratch. Come back tomorrow and you re-explain everything.

## What Spec Mode Adds

SpecOps creates git-tracked specification files that persist across sessions, developers, and time:

- **Structured templates** — domain-specific formats for features, bugfixes, and refactors (infrastructure specs look different from frontend specs)
- **EARS acceptance criteria** — precise, testable requirements (`WHEN [event] THE SYSTEM SHALL [behavior]`) that become completion gates
- **Lifecycle tracking** — specs move through `draft → review → approved → implementing → completed` with status visible to the whole team
- **Decision memory** — an implementation journal tracks what was decided, what deviated from the design, and why
- **Regression safety** — bugfix specs include Regression Risk Analysis (blast radius, behavior inventory, test coverage gaps) before any code is written
- **Context recovery** — resume where you left off across sessions without re-explaining the problem
- **Team review** — structured review workflow with approval gates before implementation begins

## Side-by-Side

| Dimension | Plan Mode | Spec Mode (SpecOps) |
|-----------|-----------|---------------------|
| **Persistence** | Session-scoped (lost on close) | Git-tracked files (permanent) |
| **Collaboration** | Single developer | Multi-stakeholder review workflow |
| **Structure** | Freeform markdown | Domain-specific templates (7 verticals) |
| **Verification** | Advisory (no enforcement) | Acceptance criteria as completion gates |
| **Lifecycle** | None | draft → review → approved → implementing → completed |
| **Cross-session** | Must re-explain context | Auto-recovery from spec files |
| **Decision tracking** | Forgotten | Implementation journal (decisions, deviations, blockers) |
| **Regression analysis** | None | Blast Radius, Behavior Inventory, Risk Tier |
| **Scope control** | None | Scope Boundary, Scope Escalation Check |

**The metaphor**: Plan mode is a whiteboard sketch. Spec mode is an architectural blueprint. You wouldn't build a house from a whiteboard sketch, and you wouldn't sketch on a blueprint. Both have their place.

## When to Use What

| Scenario | Use | Why |
|----------|-----|-----|
| Quick bug fix (< 30 min) | Plan mode | Lightweight, no overhead needed |
| Small feature (1-2 files) | Plan mode | Spec would be heavier than the code |
| Team feature (multi-day) | SpecOps | Needs review, tracking, cross-session persistence |
| Complex bugfix (regression risk) | SpecOps | Regression Risk Analysis prevents breaking existing behavior |
| Refactor (preserve behavior) | SpecOps | Scope boundaries and acceptance criteria prevent scope creep |
| Cross-session work | SpecOps | Context recovery picks up where you left off |
| Solo side project | Either | SpecOps has a self-review mode if you want the structure |

**Rule of thumb**: If the work will take more than one session, involve more than one person, or touch code where regressions matter — use SpecOps.

## Using Both Together

The most effective workflow layers both:

| Phase | What happens | Plan mode role |
|-------|-------------|----------------|
| **Phase 1: Understand** | SpecOps reads the codebase, detects the project vertical, identifies affected components | Plan mode's exploration is built into this phase |
| **Phase 2: Spec** | SpecOps creates requirements, design, and task breakdown | Not needed — SpecOps provides the structure |
| **Phase 3: Implement** | Execute tasks from the spec | Use plan mode *within* each task for tactical "how" decisions |
| **Phase 4: Complete** | Verify acceptance criteria, check docs, finalize | Not needed — SpecOps provides the verification protocol |

**Example — Adding OAuth authentication:**

Without SpecOps:
```text
Enter plan mode → sketch approach → exit → code → close session →
reopen → re-explain context → code more → forget edge cases →
ship → discover regressions
```

With SpecOps:
```text
/specops Add OAuth authentication
→ Structured requirements with EARS criteria
→ Design doc with technical decisions recorded
→ Task breakdown with dependencies
→ Implement each task (use plan mode for tricky parts)
→ Verify all acceptance criteria are met
→ Done — with a complete audit trail in git
```

The spec survives session boundaries. The decisions are recorded. The acceptance criteria are verified. And plan mode still helps with the tactical details during implementation.

## Getting Started

```bash
# Install SpecOps (Claude Code)
bash <(curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh)

# Create your first spec
/specops Add user authentication with OAuth

# View existing specs
/specops list
```

See the [Quickstart Guide](../QUICKSTART.md) for full installation instructions across all platforms.
