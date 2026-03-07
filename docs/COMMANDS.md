# SpecOps Command Reference

All supported commands across Claude Code, Cursor, OpenAI Codex, and GitHub Copilot in one place.

---

## Quick Reference

| Command | Claude Code | Cursor / Codex / Copilot |
|---------|-------------|--------------------------|
| Create spec (feature) | `/specops <description>` | `Use specops to <description>` |
| Create spec (bugfix) | `/specops Fix: <description>` | `Use specops to fix <description>` |
| Create spec (refactor) | `/specops Refactor <description>` | `Use specops to refactor <description>` |
| View spec (summary) | `/specops view <name>` | `View the <name> spec` |
| View spec (full) | `/specops view <name> full` | `Show me the full <name> spec` |
| View spec (status) | `/specops view <name> status` | `Show status of <name> spec` |
| View spec (walkthrough) | `/specops view <name> walkthrough` | `Walk me through the <name> spec` |
| View spec (section) | `/specops view <name> design` | `Show me the <name> design` |
| View spec (multi-section) | `/specops view <name> requirements design` | `View <name> requirements and design` |
| List all specs | `/specops list` | `List all specops specs` |
| Status dashboard | `/specops status` | `show specops status` |
| Status dashboard (filtered) | `/specops status in-review` | `show specops status in-review` |
| Interview (explicit) | `/specops interview <idea>` | `Use specops interview <idea>` |
| Init config | `/specops init` | `Use specops init` |
| Check version | `/specops version` | `Use specops version` |
| Update SpecOps | `/specops update` | `Use specops update` |
| Review a spec | `review <spec-name>` | `review <spec-name>` |
| Revise a spec | `revise <spec-name>` | `revise <spec-name>` |
| Implement a spec | `implement <spec-name>` | `implement <spec-name>` |

---

## Spec Creation

Creates a structured specification before implementation.

### Feature Spec
Request types: `Add`, `Build`, `Create`, `Implement`

**Claude Code:**
```
/specops Add a login page with email and password
/specops Build a payment processing system
```

**Other platforms:**
```
Use specops to add a login page with email and password
Build a payment processing system using specops
```

**Output:** `requirements.md`, `design.md`, `tasks.md`, `spec.json`

---

### Bugfix Spec
Request types: `Fix`, `Bug`

**Claude Code:**
```
/specops Fix: Users can't submit forms with special characters
/specops Bug Users getting 500 errors on checkout
```

**Other platforms:**
```
Use specops to fix users getting 500 errors on checkout
```

**Output:** `bugfix.md` (instead of requirements.md), `design.md`, `tasks.md`, `spec.json`

---

### Refactor Spec
Request types: `Refactor`

**Claude Code:**
```
/specops Refactor Extract API layer into repository pattern
```

**Other platforms:**
```
Use specops to refactor the database layer
```

**Output:** `refactor.md` (instead of requirements.md), `design.md`, `tasks.md`, `spec.json`

---

## Init Config

Creates a `.specops.json` configuration file in the project. Presents template options (minimal, standard, full, review, builder) and writes the selected config.

**Claude Code:**
```
/specops init
```

**Other platforms:**
```
Use specops init
```

**Notes:** Only triggers when the request is specifically about setting up SpecOps itself — not for product features like "set up autoscaling".

---

## Check Version

Displays the installed SpecOps version.

**Claude Code:**
```
/specops version
/specops --version
/specops -v
```

**Other platforms:**
```
Use specops version
```

---

## Update SpecOps

Checks for newer SpecOps versions and guides through upgrading.

**Claude Code:**
```
/specops update
```

**Other platforms:**
```
Use specops update
```

**Notes:** Only triggers when the request is about updating SpecOps itself — not for product changes like "update login flow".

---

## View a Spec

Display an existing spec in a structured, readable format.

### View Types

| View type | Description | Keywords |
|-----------|-------------|----------|
| `summary` (default) | Executive overview with key decisions and progress | (no keyword) or `summary` |
| `full` | Complete spec content: all sections in sequence | `full`, `everything`, `all sections`, `complete` |
| `status` | Metrics only: metadata, progress table, review status | `status`, `progress`, `metadata` |
| `walkthrough` | Guided tour with AI commentary per section | `walkthrough`, `walk me through`, `guided`, `tour` |
| `<section-name>` | Single section only (see Section Names below) | `design`, `requirements`, `tasks`, etc. |
| Multi-section | Combination of specific sections | `requirements design` |

---

### Examples

**Claude Code:**
```
/specops view login-page
/specops view login-page full
/specops view login-page design
/specops view login-page status
/specops view login-page walkthrough
/specops view login-page requirements design
```

**Other platforms:**
```
View the login-page spec
Show me the full login-page spec
Show me the login-page design
Walk me through the login-page spec
```

---

## List All Specs

Show a formatted table of all existing specs with status, version, and last updated.

**Claude Code:**
```
/specops list
```

**Other platforms:**
```
List all specops specs
```

**Output:** Table with columns: Spec ID, Type (Feature/Bugfix/Refactor), Status, Version, Author, Last Updated. On interactive platforms, offers to view a spec after listing.

---

## Status Dashboard

View a summary of all specs grouped by status, with approval counts and progress.

**Claude Code:**
```
/specops status
/specops status in-review
```

**Other platforms:**
```
show specops status
show specops status in-review
```

**Arguments:**

| Argument | Example | Effect |
|----------|---------|--------|
| None | `/specops status` | Shows all specs grouped by status |
| Status filter | `/specops status in-review` | Shows only specs with that status |

Valid status values: `draft`, `in-review`, `approved`, `self-approved`, `implementing`, `completed`

---

## Interview Mode (Optional)

Guided Q&A session for vague or exploratory ideas. Gathers structured requirements before spec generation.

### Explicit Trigger

**Claude Code:**
```
/specops interview I want to build something for restaurants
/specops interview Help me design a product
```

**Other platforms:**
```
Use specops interview to explore a saas idea
```

### Auto-Trigger

Interview mode activates automatically on interactive platforms when:
- Request is **5 words or fewer** (e.g., "I want to build a SaaS")
- **No technical keywords detected** (no mention of infra, data, library, frontend, backend)
- **No action verb** (no Add, Fix, Refactor, Implement, Build, etc.)
- **Explicit signals** like "Help me think about", "Idea:", "Brainstorm", "Need advice"

Examples that auto-trigger:
```
I have an idea
Something for restaurants
What if we built a product...
Help me design a dashboard
```

Examples that skip interview (too specific):
```
Add OAuth authentication to the API
Fix the 500 error on checkout
Refactor the database layer
```

### Interview Questions

Fixed set of 5 questions, each with conditional follow-ups:

1. **Problem** — What are you solving or what gap are you filling?
2. **Users** — Who are the primary users? Describe them briefly.
3. **Core Features** — What are 2–3 core things this needs to do?
4. **Constraints** — Any hard constraints? (Tech stack, integrations, timeline, dependencies)
5. **Done Criteria** — How will you know this is done? What does success look like?

**Supported on:** Claude Code, Cursor, Copilot (interactive platforms only). Codex skips interview and proceeds directly to spec generation.

---

## Review a Spec (Team Workflow)

Teammate reviews a spec in `draft` or `in-review` status, provides section-by-section feedback, and approves or requests changes.

**Any platform:**
```
review login-page
```

**Automatic trigger:** Detects review mode when current user's git email differs from spec author.

**Verdicts:** `Approve`, `Approve with suggestions`, `Request changes`

**Output:** Updates `reviews.md` and `spec.json`. Once approvals meet configured `minApprovals`, status becomes `approved`. If `allowSelfApproval: true` and the author self-reviews, status becomes `self-approved`.

---

## Revise a Spec (Team Workflow)

Spec author revises a spec in response to reviewer feedback marked `changes-requested`.

**Any platform:**
```
revise login-page
```

**Automatic trigger:** Detects revision mode when current user is the author AND spec is `in-review` AND a reviewer has `changes-requested`.

**What happens:** Agent reads `reviews.md`, summarizes requested changes, applies edits, increments version and review rounds, and resets reviewer statuses to `pending`. Status stays `in-review`.

---

## Implement a Spec

Skip spec creation and jump directly to implementation. Reads an existing spec and executes all tasks sequentially.

**Any platform:**
```
implement login-page
```

**Implementation gate:**
- If spec review is **enabled** and status is `approved` or `self-approved`: Proceeds, sets status to `implementing`
- If spec review is **enabled** and status is NOT `approved`/`self-approved`:
  - Interactive platforms (Claude Code, Cursor, Copilot): Warns and asks for confirmation
  - Non-interactive platform (Codex): Prints error and stops
- If spec review is **disabled**: Always proceeds

**Output:** Executes each task in `tasks.md`, updates task statuses, commits changes, runs tests, updates `implementation.md`, sets status to `completed`.

---

## Section Names (for View Commands)

Use these when viewing a specific section or combining sections:

| Section | File | Notes |
|---------|------|-------|
| `requirements` | `requirements.md` | Only for feature specs; bugfix specs use `bugfix` instead |
| `bugfix` | `bugfix.md` | Only for bugfix-type specs |
| `refactor` | `refactor.md` | Only for refactor-type specs |
| `design` | `design.md` | Present in all spec types |
| `tasks` | `tasks.md` | Present in all spec types |
| `implementation` | `implementation.md` | Optional; created during Phase 3 |
| `reviews` | `reviews.md` | Optional; created during team review cycle |

**Multi-section examples:**
```
/specops view login-page requirements design
/specops view login-page design tasks
```

---

## Status Values (for Filtering)

These are the valid states a spec can be in, usable as filters with the status command:

| Status | Meaning |
|--------|---------|
| `draft` | Spec created, not yet submitted for review (or review not enabled) |
| `in-review` | Submitted for team review, awaiting approvals |
| `approved` | Required approvals met (at least one peer approval), ready for implementation |
| `self-approved` | Author self-approved (via `allowSelfApproval: true`), no peer review |
| `implementing` | Implementation in progress |
| `completed` | All tasks done, acceptance criteria verified |

**Examples:**
```
/specops status draft
/specops status in-review
/specops status completed
```

---

## Platform Notes

### Claude Code
- **Best for:** Interactive exploration with slash commands
- **Capabilities:** Full — interviews, interactive questions, built-in progress tracking (TodoWrite), direct file editing
- **Special features:** `/specops interview` auto-detection, `/specops view` with view type modifiers

### Cursor
- **Best for:** Natural language in the IDE
- **Capabilities:** Interactive questions, rules-based triggering
- **Special features:** Auto-triggers on mention of "specops", "spec-driven", or "create a spec"
- **Limitation:** Progress tracked in `tasks.md` instead of built-in UI

### OpenAI Codex
- **Best for:** Non-interactive, autonomous spec generation and implementation
- **Capabilities:** Full feature set, but non-interactive
- **Special features:** Interview mode **skipped entirely** (proceeds with assumptions), walkthrough falls back to full+commentary
- **Limitation:** Cannot ask clarifying questions; user must provide all details upfront

### GitHub Copilot
- **Best for:** Multi-file context with IDE integration
- **Capabilities:** Interactive questions (via chat), but cannot directly create/edit files (generates as suggestions)
- **Special features:** Auto-detect like Cursor
- **Limitation:** Spec content generated as suggestions; user manually applies recommendations

---

## Quick Lookup: What Command Should I Use?

| Scenario | Command |
|----------|---------|
| I have a vague idea | Use interview mode (explicit or auto) |
| I want to create a spec for a feature | `/specops Add <description>` |
| I want to create a spec for a bug | `/specops Fix: <description>` |
| I want to create a spec for refactoring | `/specops Refactor <description>` |
| I want to see all my specs | `/specops list` |
| I want to read a spec without opening files | `/specops view <name>` |
| I want to see what's in review | `/specops status in-review` |
| I'm reviewing a teammate's spec | `review <name>` |
| I'm updating my spec after feedback | `revise <name>` |
| I'm ready to code | `implement <name>` |
| I want to set up SpecOps in my project | `/specops init` |
| I want to check my SpecOps version | `/specops version` |
| I want to update SpecOps | `/specops update` |
