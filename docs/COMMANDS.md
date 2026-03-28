# SpecOps Command Reference

All supported commands across Claude Code, Cursor, OpenAI Codex, GitHub Copilot, and Google Antigravity in one place.

---

## Quick Reference

| Command | Claude Code | Cursor / Codex / Copilot |
| --- | --- | --- |
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
| View memory | `/specops memory` | `Use specops memory` |
| Seed memory from specs | `/specops memory seed` | `Use specops memory seed` |
| Capture production learning | `/specops learn <name>` | `Use specops learn <name>` |
| Generate/refresh repo map | `/specops map` | `Use specops map` |
| Auto-implement spec (pipeline) | `/specops pipeline <name>` | `Use specops pipeline for <name>` |
| View initiative | `/specops view initiative <id>` | `View initiative <id>` |
| List initiatives | `/specops list initiatives` | `List all initiatives` |
| Run initiative | `/specops initiative <id>` | `Use specops initiative <id>` |
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

```text
/specops Add a login page with email and password
/specops Build a payment processing system
```text

**Other platforms:**

```text
Use specops to add a login page with email and password
Build a payment processing system using specops
```

**Output:** `requirements.md`, `design.md`, `tasks.md`, `spec.json`

**Note:** Large features may trigger automatic scope assessment (Phase 1.5). If the feature exceeds single-spec complexity thresholds, SpecOps proposes splitting it into multiple specs tracked as an initiative. See [Initiative Management](#initiative-management) below.

---

### Bugfix Spec

Request types: `Fix`, `Bug`

**Claude Code:**

```text
/specops Fix: Users can't submit forms with special characters
/specops Bug Users getting 500 errors on checkout
```text

**Other platforms:**

```text
Use specops to fix users getting 500 errors on checkout
```

**Output:** `bugfix.md` (instead of requirements.md), `design.md`, `tasks.md`, `spec.json`

---

### Refactor Spec

Request types: `Refactor`

**Claude Code:**

```text
/specops Refactor Extract API layer into repository pattern
```text

**Other platforms:**

```text
Use specops to refactor the database layer
```

**Output:** `refactor.md` (instead of requirements.md), `design.md`, `tasks.md`, `spec.json`

---

## Init Config

Creates a `.specops.json` configuration file in the project. Presents template options (minimal, standard, full, review, builder), writes the selected config, creates foundation steering files (`product.md`, `tech.md`, `structure.md` in `<specsDir>/steering/`), and scaffolds the memory directory (`<specsDir>/memory/`).

**Claude Code:**

```text
/specops init
```text

**Other platforms:**

```text
Use specops init
```

**Notes:** Only triggers when the request is specifically about setting up SpecOps itself — not for product features like "set up autoscaling".

---

## Check Version

Displays the installed SpecOps version.

**Claude Code:**

```text
/specops version
/specops --version
/specops -v
```text

**Other platforms:**

```text
Use specops version
```

---

## Update SpecOps

Checks for newer SpecOps versions and guides through upgrading.

**Claude Code:**

```text
/specops update
```

**Other platforms:**

```text
Use specops update
```

**Notes:** Only triggers when the request is about updating SpecOps itself — not for product changes like "update login flow".

---

## Manage Steering Files

Scaffold, view, and manage steering files — markdown files with YAML frontmatter that provide persistent project context (product overview, tech stack, project structure). `always`-included files are loaded before every spec; `fileMatch` files load conditionally; `manual` files are never auto-loaded.

**Claude Code:**

```text
/specops steering
```text

**Other platforms:**

```text
Use specops steering
```

**Workflow:**

- If no steering directory exists, offers to create three foundation files: `product.md`, `tech.md`, `structure.md`
- If the directory exists, shows a summary table of all steering files (name, inclusion mode, description) and offers to add, edit, or done on interactive platforms

**Steering file inclusion modes:**

| Mode | Description |
| ------ | ------------- |
| `always` | Loaded before every spec (use for product overview, tech stack, project structure) |
| `fileMatch` | Loaded only when affected files match the file globs (e.g., `["*.sql", "migrations/**"]`) |
| `manual` | Not loaded automatically — available for explicit reference only |

**Notes:** Only triggers when the request is about managing SpecOps steering files — not for product features like "add steering wheel component". Steering files live in `<specsDir>/steering/` (default: `.specops/steering/`).

**See also:** [Steering Files Guide](STEERING_GUIDE.md) — file format, inclusion modes, glob patterns, and best practices.

---

## Local Memory

### View Memory

Shows decisions, project context, and detected patterns from completed specs.

**Claude Code:**

```text
/specops memory
```

**Other platforms:**

```text
Use specops memory
```

**Output:** Formatted summary of decisions (from `decisions.json`), project history (from `context.md`), and recurring patterns (from `patterns.json`).

### Seed Memory

Populates the memory layer from all completed specs' `implementation.md` decision journals. Use after enabling memory on a project with existing specs.

**Claude Code:**

```text
/specops memory seed
```

**Other platforms:**

```text
Use specops memory seed
```

**Output:** Creates/rebuilds `<specsDir>/memory/decisions.json`, `context.md`, and `patterns.json` from completed specs.

---

## Production Learnings

Capture post-deployment discoveries and link them back to the originating spec. Learnings are stored in `<specsDir>/memory/learnings.json` and surfaced during future spec work when relevant.

### Capture a Learning

**Claude Code:**

```text
/specops learn <spec-name>
```

**Other platforms:**

```text
Use specops learn <spec-name>
```

**Workflow:**

1. Identifies the target spec (must be `completed` status)
2. Asks a set of structured questions about the learning (for example: what was discovered, impact severity, category (performance, security, scalability, UX, architecture, integration, operational), root cause, and what the spec should have included)
3. Creates a learning entry in `learnings.json` with metadata (spec ID, timestamp, severity, category)
4. Optionally proposes updates to the originating spec's requirements or design

**Capture mechanisms:**

| Mechanism | Trigger |
| --- | --- |
| Explicit | `/specops learn <spec-name>` |
| Agent-proposed | Agent detects production issue pattern during spec work |
| Reconciliation-based | `/specops reconcile --learnings` extracts learnings from recent hotfixes |

**Learning retrieval:** During Phase 1, learnings from related specs are automatically loaded and surfaced as context. Filtering uses spec ID, category, and severity to show only relevant learnings.

**Notes:** Only triggers when referring to SpecOps production learnings, not product features like "learn from data". Learnings follow a supersession protocol where newer learnings on the same topic replace older ones.

---

## Drift Detection

### Audit Spec Health

Runs 5 drift checks against one or more specs and produces a health report. Read-only — no files are modified.

**Claude Code:**

```text
/specops audit
/specops audit <name>
/specops health check
/specops check drift
/specops spec health
```

**Other platforms:**

```text
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
| ------- | ----------------- | ---------- |
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

```text
/specops reconcile <name>
/specops fix <name>
/specops repair <name>
/specops sync <name>
```

**Other platforms:**

```text
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
| --------- | --------- |
| Missing file (renamed) | Update path in tasks.md / Skip |
| Missing file (deleted) | Remove reference / Provide new path / Skip |
| Completed task, file missing | Provide new path / Note as discrepancy in tasks.md / Skip |
| Pending task, file already exists | Mark In Progress / Skip |
| Stale spec | Continue as-is / Skip |
| Cross-spec conflict | Informational only — no repair |

**Notes:** Requires interactive platform (`canAskInteractive: true`). On Codex, reconcile is blocked — run audit instead and apply fixes manually. Only triggers when referring to SpecOps spec repair, not product commands like "fix auth bug".

---

## Convert a Plan to a Spec

Convert an existing AI coding assistant plan (from plan mode, a planning session, or any structured outline) into a persistent SpecOps spec. SpecOps faithfully maps the plan into the standard spec structure: goals → requirements with EARS acceptance criteria, approach → design.md, steps → tasks.md. Where the plan omits information, SpecOps uses `[To be defined]` placeholders rather than inferring content.

**Claude Code:**

```text
/specops from-plan
```text

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

## Send Feedback

Submit feedback about SpecOps (bugs, feature requests, friction, improvements) directly as a GitHub issue on the SpecOps repository.

**Claude Code:**

```text
/specops feedback
```text

**Other platforms:**

```text
Use specops feedback
Use specops feedback bug The interview mode skips my follow-up answers
```

**Workflow (interactive):**

1. Select category (bug, feature, friction, improvement, docs gap, other)
2. Describe the feedback
3. Review the draft issue
4. Confirm submission

**Workflow (non-interactive):**

- Provide category and description inline
- Issue is composed and submitted automatically

**Submission tiers:** (1) `gh` CLI creates a GitHub issue directly. (2) If `gh` is unavailable, a pre-filled browser URL is provided. (3) If the URL is too long or both tiers fail, feedback is saved as a local draft with manual submission instructions.

**Notes:** Only triggers when referring to SpecOps feedback, not product features like "add feedback form". Privacy-safe: only SpecOps version, platform, and vertical are included — no project code, paths, or configuration.

---

## Initiative Management

Initiatives track large features that span multiple specs. When a feature request triggers scope assessment (Phase 1.5) and is split into multiple specs, SpecOps creates an initiative to coordinate them.

### How Decomposition Works

1. **Scope assessment (Phase 1.5)** — After Phase 1 context analysis, SpecOps evaluates complexity signals (multiple bounded contexts, cross-cutting concerns, estimated task count). If thresholds are exceeded, it proposes splitting the feature into multiple specs.
2. **Approval** — On interactive platforms, you approve or reject the decomposition. On non-interactive platforms, SpecOps notifies you of the detected components and continues as a single spec (consider splitting manually).
3. **Initiative creation** — An `<id>.json` file is created in `<specsDir>/initiatives/` tracking all member specs, their execution order (waves derived via topological sort), and the walking skeleton. A companion `<id>-log.md` records the execution trace.
4. **Cross-spec dependencies** — Each spec's `spec.json` includes `specDependencies` (required and advisory) and `partOf` (initiative membership). A dependency gate in Phase 3 blocks implementation when required dependencies are incomplete.

### View an Initiative

**Claude Code:**

```text
/specops view initiative oauth-payments
```

**Other platforms:**

```text
View initiative oauth-payments
```

**Output:** Initiative summary with member specs, execution waves, dependency graph, completion status, and the walking skeleton spec.

### List All Initiatives

**Claude Code:**

```text
/specops list initiatives
```

**Other platforms:**

```text
List all initiatives
```

**Output:** Table of all initiatives with ID, title, status (active/completed), member spec count, and completion percentage.

### Run an Initiative

Execute all specs in an initiative autonomously, respecting execution wave order and dependency gates.

**Claude Code:**

```text
/specops initiative oauth-payments
```

**Other platforms:**

```text
Use specops initiative oauth-payments
```

**Workflow:**

1. Reads `initiative.json` and computes execution waves
2. For each wave, dispatches member specs sequentially through the normal SpecOps workflow
3. Each spec gets a fresh context with a handoff bundle (initiative context, spec identity, dependency context, scope constraints)
4. After each spec completes, verifies completion and updates initiative status
5. When all specs complete, marks the initiative as completed

**Notes:** Only triggers for SpecOps initiative execution. The orchestrator uses file-based state management (no in-memory accumulation). An `initiative-log.md` records the chronological execution trace.

---

## View a Spec

Display an existing spec in a structured, readable format.

### View Types

| View type | Description | Keywords |
| ----------- | ------------- | ---------- |
| `summary` (default) | Executive overview with key decisions and progress | (no keyword) or `summary` |
| `full` | Complete spec content: all sections in sequence | `full`, `everything`, `all sections`, `complete` |
| `status` | Metrics only: metadata, progress table, review status | `status`, `progress`, `metadata` |
| `walkthrough` | Guided tour with AI commentary per section | `walkthrough`, `walk me through`, `guided`, `tour` |
| `<section-name>` | Single section only (see Section Names below) | `design`, `requirements`, `tasks`, etc. |
| Multi-section | Combination of specific sections | `requirements design` |

---

### Examples

**Claude Code:**

```text
/specops view login-page
/specops view login-page full
/specops view login-page design
/specops view login-page status
/specops view login-page walkthrough
/specops view login-page requirements design
```

**Other platforms:**

```text
View the login-page spec
Show me the full login-page spec
Show me the login-page design
Walk me through the login-page spec
```

---

## List All Specs

Show a formatted table of all existing specs with status, version, and last updated.

**Claude Code:**

```text
/specops list
```

**Other platforms:**

```text
List all specops specs
```

**Output:** Table with columns: Spec ID, Type (Feature/Bugfix/Refactor), Status, Version, Author, Last Updated. On interactive platforms, offers to view a spec after listing.

---

## Status Dashboard

View a summary of all specs grouped by status, with approval counts and progress.

**Claude Code:**

```text
/specops status
/specops status in-review
```

**Other platforms:**

```text
show specops status
show specops status in-review
```

**Arguments:**

| Argument | Example | Effect |
| ---------- | --------- | -------- |
| None | `/specops status` | Shows all specs grouped by status |
| Status filter | `/specops status in-review` | Shows only specs with that status |

Valid status values: `draft`, `in-review`, `approved`, `self-approved`, `implementing`, `completed`

---

## Interview Mode (Optional)

Guided Q&A session for vague or exploratory ideas. Gathers structured requirements before spec generation.

### Explicit Trigger

**Claude Code:**

```text
/specops interview I want to build something for restaurants
/specops interview Help me design a product
```

**Other platforms:**

```text
Use specops interview to explore a saas idea
```

### Auto-Trigger

Interview mode activates automatically on interactive platforms when:

- Request is **5 words or fewer** (e.g., "I want to build a SaaS")
- **No technical keywords detected** (no mention of infra, data, library, frontend, backend)
- **No action verb** (no Add, Fix, Refactor, Implement, Build, etc.)
- **Explicit signals** like "Help me think about", "Idea:", "Brainstorm", "Need advice"

Examples that auto-trigger:

```text
I have an idea
Something for restaurants
What if we built a product...
Help me design a dashboard
```

Examples that skip interview (too specific):

```text
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

```text
review login-page
```

**Automatic trigger:** Detects review mode when current user's git email differs from spec author.

**Verdicts:** `Approve`, `Approve with suggestions`, `Request changes`

**Output:** Updates `reviews.md` and `spec.json`. Once approvals meet configured `minApprovals`, status becomes `approved`. If `allowSelfApproval: true` and the author self-reviews, status becomes `self-approved`.

---

## Revise a Spec (Team Workflow)

Spec author revises a spec in response to reviewer feedback marked `changes-requested`.

**Any platform:**

```text
revise login-page
```

**Automatic trigger:** Detects revision mode when current user is the author AND spec is `in-review` AND a reviewer has `changes-requested`.

**What happens:** Agent reads `reviews.md`, summarizes requested changes, applies edits, increments version and review rounds, and resets reviewer statuses to `pending`. Status stays `in-review`.

---

## Implement a Spec

Skip spec creation and jump directly to implementation. Reads an existing spec and executes all tasks sequentially.

**Any platform:**

```text
implement login-page
```

**Implementation gate:**

- If spec review is **enabled** and status is `approved` or `self-approved`: Proceeds, sets status to `implementing`
- If spec review is **enabled** and status is NOT `approved`/`self-approved`:
  - Interactive platforms (Claude Code, Cursor, Copilot): Warns and asks for confirmation
  - Non-interactive platform (Codex): Prints error and stops
- If spec review is **disabled**: Always proceeds

**Output:** Executes each task in `tasks.md`, updates task statuses, commits changes, runs tests, updates `implementation.md`, sets status to `completed`.

**Task delegation:**

Phase 3 execution adapts based on `implementation.taskDelegation` in `.specops.json` (defaults to `"auto"` if not set):

| Value | Behavior |
| ------- | ---------- |
| `"auto"` (default) | Delegates to fresh contexts when 4+ pending tasks (prevents context exhaustion) |
| `"always"` | Always delegates regardless of task count |
| `"never"` | Sequential execution in the current context |

Delegation strategy depends on platform capabilities:

- **Claude Code**: Sub-agent delegation (fresh agent per task)
- **Cursor / Copilot**: Session checkpoint (prompts to continue in new session after each task)
- **Codex**: Enhanced sequential (standard execution with detailed checkpointing)

---

## Section Names (for View Commands)

Use these when viewing a specific section or combining sections:

| Section | File | Notes |
| --------- | ------ | ------- |
| `requirements` | `requirements.md` | Only for feature specs; bugfix specs use `bugfix` instead |
| `bugfix` | `bugfix.md` | Only for bugfix-type specs |
| `refactor` | `refactor.md` | Only for refactor-type specs |
| `design` | `design.md` | Present in all spec types |
| `tasks` | `tasks.md` | Present in all spec types |
| `implementation` | `implementation.md` | Optional; created during Phase 3 |
| `reviews` | `reviews.md` | Optional; created during team review cycle |

**Multi-section examples:**

```text
/specops view login-page requirements design
/specops view login-page design tasks
```

---

## Status Values (for Filtering)

These are the valid states a spec can be in, usable as filters with the status command:

| Status | Meaning |
| -------- | --------- |
| `draft` | Spec created, not yet submitted for review (or review not enabled) |
| `in-review` | Submitted for team review, awaiting approvals |
| `approved` | Required approvals met (at least one peer approval), ready for implementation |
| `self-approved` | Author self-approved (via `allowSelfApproval: true`), no peer review |
| `implementing` | Implementation in progress |
| `completed` | All tasks done, acceptance criteria verified |

**Examples:**

```text
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

### Google Antigravity

- **Best for:** Multi-agent orchestration via Manager View
- **Capabilities:** Full feature set including sub-agent delegation (`canDelegateTask: true`)
- **Special features:** Same invocation pattern as Codex. Supports task delegation via Manager View agents.
- **Limitation:** Non-interactive (`canAskInteractive: false`) -- interview mode skipped, reconcile blocked

---

## Quick Lookup: What Command Should I Use?

| Scenario | Command |
| ---------- | --------- |
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
| I want to see project decisions and patterns | `/specops memory` |
| I want to populate memory from existing specs | `/specops memory seed` |
| I want to capture a production learning from a deployed spec | `/specops learn <spec-name>` |
| I want to extract learnings from recent hotfixes | `/specops reconcile --learnings` |
| I want to control how Phase 3 executes tasks | Set `implementation.taskDelegation` in `.specops.json` (`auto`/`always`/`never`) |
| I want to report a bug or suggest a SpecOps improvement | `/specops feedback` |
| I want to update SpecOps | `/specops update` |
| I have a large feature that should be split into specs | Start with `/specops Add <description>` — scope assessment triggers automatically |
| I want to see all multi-spec initiatives | `/specops list initiatives` |
| I want to view an initiative's status and dependency graph | `/specops view initiative <id>` |
| I want to execute all specs in an initiative | `/specops initiative <id>` |
