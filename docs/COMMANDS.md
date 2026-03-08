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
| Manage steering files | `/specops steering` | `Use specops steering` |
| Audit spec health | `/specops audit <name>` | `audit <name>` |
| Audit all active specs | `/specops audit` | `health check` or `check drift` or `spec health` |
| Reconcile a drifted spec | `/specops reconcile <name>` | `reconcile <name>` or `fix <name>` |
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

## Manage Steering Files

Scaffold, view, and manage steering files — markdown files with YAML frontmatter that provide persistent project context (product overview, tech stack, project structure). `always`-included files are loaded before every spec; `fileMatch` files load conditionally; `manual` files are never auto-loaded.

**Claude Code:**
```text
/specops steering
```

**Other platforms:**
```text
Use specops steering
```

**Workflow:**
- If no steering directory exists, offers to create three foundation files: `product.md`, `tech.md`, `structure.md`
- If the directory exists, shows a summary table of all steering files (name, inclusion mode, description) and offers to add, edit, or done on interactive platforms

**Steering file inclusion modes:**

| Mode | Description |
|------|-------------|
| `always` | Loaded before every spec (use for product overview, tech stack, project structure) |
| `fileMatch` | Loaded only when affected files match the file globs (e.g., `["*.sql", "migrations/**"]`) |
| `manual` | Not loaded automatically — available for explicit reference only |

**Notes:** Only triggers when the request is about managing SpecOps steering files — not for product features like "add steering wheel component". Steering files live in `<specsDir>/steering/` (default: `.specops/steering/`).

**See also:** [Steering Files Guide](STEERING_GUIDE.md) — file format, inclusion modes, glob patterns, and best practices.

---

## Drift Detection

### Audit Spec Health

Runs 5 drift checks against one or more specs and produces a health report. Read-only — no files are modified.

**Claude Code:**
```
/specops audit
/specops audit <name>
/specops health check
/specops check drift
/specops spec health
```

**Other platforms:**
```
audit <name>
health check
check drift
spec health
```

**Behavior:**
- With a name: audits that single spec
- Without a name: audits all specs whose status is not `completed`

**5 Drift Checks:**

| Check | What it detects | Severity |
|-------|-----------------|----------|
| File Drift | "Files to Modify" paths that no longer exist | Drift / Warning |
| Post-Completion Modification | Files changed after a completed spec's `updated` timestamp | Warning |
| Task Status Inconsistency | Completed tasks with missing files; pending tasks with early implementations | Drift / Warning |
| Staleness | Specs inactive beyond threshold (>14d implementing → Drift, >7d → Warning) | Drift / Warning |
| Cross-Spec Conflicts | Multiple active specs referencing the same file paths | Warning |

**Result levels:** `Healthy` → `Warning` → `Drift`. Overall = worst check across all 5.

**Notes:** Check 2 (post-completion mods) degrades gracefully when `canAccessGit: false` — it skips with a note. Check 4 (staleness) works via `spec.json.updated` timestamp regardless of git access. Only triggers for SpecOps spec health — not for product features like "audit log" or "health endpoint".

---

### Reconcile a Spec

Guided interactive repair for drifted specs. Presents numbered findings and applies selected fixes to `tasks.md` and `spec.json`.

**Claude Code:**
```
/specops reconcile <name>
/specops fix <name>
/specops repair <name>
/specops sync <name>
```

**Other platforms:**
```
reconcile <name>
fix <name>
repair <name>
sync <name>
```

**Workflow:**
1. Runs a full audit on the target spec
2. If healthy → notifies no action needed
3. Presents numbered findings list
4. Asks which findings to fix (`all`, comma-separated numbers, or `skip`)
5. Applies repairs: update/remove file paths, update task statuses, update `spec.json.updated`
6. Regenerates `index.json`

**Available repairs by finding type:**

| Finding | Options |
|---------|---------|
| Missing file (renamed) | Update path in tasks.md / Skip |
| Missing file (deleted) | Remove reference / Provide new path / Skip |
| Completed task, file missing | Provide new path / Note as discrepancy in tasks.md / Skip |
| Pending task, file already exists | Mark In Progress / Skip |
| Stale spec | Continue as-is / Skip |
| Cross-spec conflict | Informational only — no repair |

**Notes:** Requires interactive platform (`canAskInteractive: true`). On Codex, reconcile is blocked — run audit instead and apply fixes manually. Only triggers when referring to SpecOps spec repair, not product commands like "fix auth bug".

---

## Convert a Plan to a Spec

Convert an existing AI coding assistant plan (from plan mode, a planning session, or any structured outline) into a persistent SpecOps spec. SpecOps faithfully maps the plan into the standard spec structure: goals → requirements with EARS acceptance criteria, approach → design.md, steps → tasks.md. Codebase analysis fills any gaps the plan omitted.

**Claude Code:**
```text
/specops from-plan
```

**Other platforms:**
```text
Use specops from-plan
```

**Workflow:**
1. If no plan content is included in the invocation, prompts you to paste the plan
2. Parses the plan to identify goals, approach, steps, acceptance criteria, constraints, and file paths
3. Shows a mapping summary before generating (e.g., "Found 2 goals → requirements.md, 8 steps → tasks.md")
4. Generates spec files using faithful conversion — preserves the plan's intent without re-deriving
5. Proceeds to review gate (if spec review is enabled) or notifies you the spec is ready

**Faithful conversion:** From Plan mode does not second-guess the plan or re-derive requirements independently. If a section is missing from the plan (e.g., no acceptance criteria), it adds `[To be defined]` placeholders rather than inventing content.

**Supported plan formats:** Free-form markdown, numbered steps, structured headers — any format accepted. SpecOps extracts sections using keyword heuristics.

**Notes:** Only triggers when the request is about converting an AI coding plan into a spec — not for product features like "import plan data from an external system". On platforms where `canAskInteractive = false` (e.g., Codex), the plan content must be included inline in the request.

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
| I want to create or manage steering files | `/specops steering` |
| I want to check if a spec has drifted from the codebase | `/specops audit <name>` |
| I want to audit all active specs at once | `/specops audit` |
| I want to fix drift findings interactively | `/specops reconcile <name>` |
| I have an AI plan and want to convert it to a spec | `/specops from-plan` |
| I want to check my SpecOps version | `/specops version` |
| I want to update SpecOps | `/specops update` |
