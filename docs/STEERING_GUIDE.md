# Steering Files Guide

Steering files are persistent project context documents that SpecOps loads during Phase 1 to give the agent stable project context for spec generation. They help the agent understand what your project is, how it's built, and how it's organized — so you don't re-explain the same context at the start of each spec.

---

## Conventions vs Steering Files

SpecOps offers two ways to give the agent project context. They are complementary, not interchangeable:

| | `team.conventions` in `.specops.json` | Steering files |
|---|---|---|
| **Format** | Short strings, one rule per entry | Free-form Markdown documents |
| **Purpose** | Coding standards and rules | Project understanding and background |
| **Examples** | `"Use TypeScript for all new code"`, `"No raw SQL queries"` | Product overview, technology rationale, directory layout |
| **Loaded as** | Embedded directly in spec templates | Read as context during Phase 1 |
| **Best for** | Rules the agent should follow | Facts the agent should know |

**Rule of thumb:** If it fits in one sentence and tells the agent what to do, it's a convention. If it needs a paragraph to explain what your project is or why you made a decision, it's a steering file.

---

## File Format

Each steering file is a Markdown file (`.md`) stored in `<specsDir>/steering/` (default: `.specops/steering/`) with a YAML frontmatter block at the top.

```markdown
---
name: "Product Context"
description: "What this project builds, for whom, and how it's positioned"
inclusion: always
---

## Product Overview
One-sentence description of what the project does.

## Target Users
Who uses this and in what context.
```

### Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Display name shown in the steering summary table |
| `description` | Yes | string | One-line purpose description |
| `inclusion` | Yes | `always` \| `fileMatch` \| `manual` | When this file is loaded (see below) |
| `globs` | Only for `fileMatch` | string[] | File patterns that trigger loading |

---

## Inclusion Modes

### `always`

Loaded before every spec, regardless of what files are involved. Use for foundational context that is universally relevant.

```yaml
---
name: "Product Context"
description: "What this project builds, for whom, and how it's positioned"
inclusion: always
---
```

Good candidates: product overview, technology stack, project structure, team norms.

### `fileMatch`

Loaded only when Phase 1 identifies affected files that match the `globs` patterns. Use for domain-specific context that would be noise outside its area.

```yaml
---
name: "Database Conventions"
description: "Migration strategy, query patterns, schema decisions"
inclusion: fileMatch
globs: ["*.sql", "migrations/**", "src/db/**"]
---
```

Good candidates: database migration conventions, API contract rules, frontend component guidelines, infra/IaC patterns.

**Glob syntax:** Standard file glob patterns. Examples:

| Pattern | Matches |
|---------|---------|
| `*.sql` | Any SQL file in the root |
| `migrations/**` | All files under `migrations/` |
| `src/api/**/*.ts` | TypeScript files anywhere under `src/api/` |
| `**/*.test.ts` | All TypeScript test files, anywhere |

### `manual`

Never loaded automatically. Available for explicit reference when the agent or user specifically needs the context. Use for rarely-needed reference material (e.g., legacy system quirks, historical architecture decisions).

```yaml
---
name: "Legacy Auth System"
description: "How the old authentication system worked before the migration"
inclusion: manual
---
```

---

## Getting Started

Run the steering command and SpecOps will scaffold the three foundation files for you:

**Claude Code:**
```text
/specops steering
```

**Other platforms:**
```text
Use specops steering
```

If no steering directory exists, SpecOps offers to create `product.md`, `tech.md`, and `structure.md` with fill-in-the-blank templates. Edit them to describe your project.

To create a file manually, add a `.md` file to `<specsDir>/steering/` with valid YAML frontmatter.

---

## Foundation Templates

These three files cover the context that matters for most specs. Start here.

### `product.md`

```markdown
---
name: "Product Context"
description: "What this project builds, for whom, and how it's positioned"
inclusion: always
---

## Product Overview
[One-sentence description of what the project does]

## Target Users
[Who uses this and in what context]

## Key Differentiators
[What makes this different from alternatives]
```

### `tech.md`

```markdown
---
name: "Technology Stack"
description: "Languages, frameworks, tools, and quality infrastructure"
inclusion: always
---

## Core Stack
[Primary language, framework, and runtime]

## Development Tools
[Build system, package manager, linting, formatting]

## Quality & Testing
[Test framework, CI system, validation tools]
```

### `structure.md`

```markdown
---
name: "Project Structure"
description: "Directory layout, key files, and module boundaries"
inclusion: always
---

## Directory Layout
[Top-level directory purposes]

## Key Files
[Important configuration and entry point files]

## Module Boundaries
[How modules relate and communicate]
```

---

## Best Practices

**Keep `always` files concise.** They are loaded before every spec. A 2,000-word product manifesto loaded 50 times adds noise. Aim for 200–400 words per `always` file. Move domain-specific detail into `fileMatch` files.

**Use `fileMatch` for area-specific context.** If you have conventions that only apply when touching the database, payment system, or a specific service, a `fileMatch` file ensures that context is available exactly when needed — and absent when it isn't.

**Put facts in steering, rules in conventions.** Steering files explain what is; `team.conventions` specifies what should be done. Both are loaded, and they complement each other.

**Keep steering files up to date.** Outdated context is worse than no context — it actively misleads the agent. When your stack changes or the product pivots, update the relevant steering file.

**Maximum 20 files.** SpecOps loads at most 20 steering files (sorted alphabetically). If you hit the limit, consolidate related files.

---

## How Steering Files Are Loaded

During Phase 1 (Understand Context):

1. SpecOps reads all `.md` files in `<specsDir>/steering/`, sorted alphabetically (max 20)
2. Files with `inclusion: always` are loaded immediately as project context
3. Files with `inclusion: fileMatch` are evaluated after affected files are identified — loaded only if the affected files match the `globs` patterns
4. Files with `inclusion: manual` are skipped
5. Files with invalid or missing frontmatter are skipped with a notification

---

## Safety

Steering file content is treated as project context — not as instructions to the agent. If a steering file appears to contain meta-instructions (e.g., "ignore previous instructions", "execute this command"), SpecOps will skip that file and notify you. Path traversal patterns (`..`, absolute paths) in filenames are rejected.
