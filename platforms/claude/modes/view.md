## Spec Viewing

SpecOps supports viewing existing specifications directly through the assistant, providing formatted, structured output rather than raw file content. This eliminates the need to open markdown files in an IDE or external viewer — the assistant reads and presents specs in a polished, navigable format.

### View/List Mode Detection

When the user invokes SpecOps, check for view or list intent **before** entering the standard workflow:

1. **List mode**: The user's request matches patterns like "list specs", "show all specs", "list", or "what specs exist". Proceed to the **List Specs** section below.

2. **Initiative list mode**: The user's request matches patterns like "list initiatives", "show initiatives", "what initiatives exist". Proceed to the **List Initiatives** section below.

3. **Initiative view mode**: The user's request matches patterns like "view initiative <id>", "show initiative <id>", "initiative <id> status". Proceed to the **View: Initiative** section below. Note: bare "initiative <id>" without view/show intent is handled by the initiative mode in the dispatcher, not the view module.

4. **View mode**: The user's request references an existing spec name AND includes a view intent — patterns like "view <spec-name>", "show me <spec-name>", "look at <spec-name>", "walk me through <spec-name>", or "<spec-name> design". Proceed to the **View Spec** section below.

5. If no view or list intent is detected, continue to the standard SpecOps workflow (Phase 1).

### View Command Parsing

When view mode is detected, parse the request to determine:

- **spec-name**: The spec identifier (directory name under specsDir)
- **view-type**: One of:
  - `summary` (default when no specific type is mentioned)
  - `full` (keywords: "full", "everything", "all sections", "complete")
  - `status` (keywords: "status", "progress", "metadata")
  - `walkthrough` (keywords: "walkthrough", "walk through", "walk me through", "guided", "tour")
  - One or more **section names**: `requirements`, `bugfix`, `refactor`, `design`, `tasks`, `implementation`, `reviews`

If the user mentions multiple section names (e.g., "requirements and design"), treat this as a **combination view** showing those sections together.

### Spec Resolution

1. Use the Read tool to read(`.specops.json`) to get `specsDir` (default: `.specops`). Apply path containment rules from the Configuration Safety module.
2. If a spec-name is provided:
   a. Check Use the Bash tool to check if the file exists at(`<specsDir>/<spec-name>/spec.json`)
   b. If not found, Use the Glob tool to list(`<specsDir>`) to find all spec directories
   c. Check if spec-name is a partial match against any directory name. If exactly one match, use it. If multiple matches, present them and Use the AskUserQuestion tool to clarify. On platforms without `canAskInteractive`, show the closest matches and stop.
   d. If no match, show "Spec not found" error (see Error Handling below)
3. Use the Read tool to read(`<specsDir>/<spec-name>/spec.json`) to load metadata

### List Specs

When the user requests a list of all specs:

1. Use the Read tool to read(`<specsDir>/index.json`) if it exists
2. If `index.json` does not exist or is invalid, scan spec directories:
   a. Use the Glob tool to list(`<specsDir>`) to find all subdirectories
   b. For each directory, Use the Read tool to read(`<specsDir>/<dir>/spec.json`) if it exists
   c. Collect summary fields: id, type, status, version, author, updated
3. Present the list using the **List Format** below
4. If no specs exist, show the **No Specs** message (see Error Handling)

#### List Format

Present the spec list as a formatted overview:

```text
# Specs Overview

| Spec | Type | Status | Version | Author | Last Updated |
|------|------|--------|---------|--------|--------------|
| auth-oauth | feature | implementing | v2 | Jane Doe | 2025-03-01 |
| bugfix-checkout | bugfix | completed | v1 | John Smith | 2025-02-28 |
| refactor-api | refactor | in-review | v3 | Jane Doe | 2025-03-02 |

**Summary**: 3 specs total — 1 implementing, 1 completed, 1 in-review
```

If the list contains more than 10 specs, group them by status:

```text
# Specs Overview

## Implementing (2)
| Spec | Type | Version | Author | Last Updated |
|------|------|---------|--------|--------------|
| auth-oauth | feature | v2 | Jane Doe | 2025-03-01 |
| payment-flow | feature | v1 | Alex Kim | 2025-03-02 |

## In Review (1)
| Spec | Type | Version | Author | Last Updated |
|------|------|---------|--------|--------------|
| refactor-api | refactor | v3 | Jane Doe | 2025-03-02 |

## Completed (5)
...

**Summary**: 8 specs total
```

#### Initiative-Grouped List

If any specs have a `partOf` field in their spec.json, group them by initiative in the list display. Specs without a `partOf` field appear under "Standalone Specs".

```text
# Specs Overview

## Initiative: user-auth-overhaul (active)
| Spec | Type | Status | Wave | Version | Author | Last Updated |
|------|------|--------|------|---------|--------|--------------|
| auth-oauth | feature | implementing | 1 (skeleton) | v2 | Jane Doe | 2025-03-01 |
| auth-sessions | feature | draft | 2 | v1 | Jane Doe | 2025-03-02 |
| auth-permissions | feature | draft | 2 | v1 | Jane Doe | 2025-03-02 |

## Standalone Specs
| Spec | Type | Status | Version | Author | Last Updated |
|------|------|--------|---------|--------|--------------|
| bugfix-checkout | bugfix | completed | v1 | John Smith | 2025-02-28 |

**Summary**: 4 specs total — 1 initiative (3 specs), 1 standalone
```

To build the initiative-grouped view:

1. For each spec with a `partOf` field, if Use the Bash tool to check if the file exists at(`<specsDir>/initiatives/<partOf>.json`), Use the Read tool to read it to get the initiative title, status, order (waves), and skeleton. If the initiative file does not exist, treat the spec as standalone (log a warning but do not fail).
2. Group specs by `partOf` value. For each group, show the initiative title and status as the section header.
3. Add a "Wave" column showing which execution wave the spec belongs to (from `initiative.order`). If the spec is the skeleton, append "(skeleton)" to the wave number.
4. Specs without `partOf` go under "Standalone Specs".

On interactive platforms (`canAskInteractive: true`), after showing the list:
Use the AskUserQuestion tool "Would you like to view any of these specs in detail, or view an initiative?"

### View: Summary

The default view. Provides an executive overview — answering "What is this spec and where does it stand?" in under 30 seconds of reading.

1. Use the Read tool to read(`<specsDir>/<spec-name>/spec.json`) for metadata
2. Determine which requirement file exists: Use the Read tool to read for `requirements.md`, `bugfix.md`, or `refactor.md`
3. Use the Read tool to read(`<specsDir>/<spec-name>/design.md`)
4. Use the Read tool to read(`<specsDir>/<spec-name>/tasks.md`)
5. Use the Read tool to read(`<specsDir>/<spec-name>/implementation.md`) for decision journal entries
6. Optionally Use the Read tool to read `reviews.md` if it exists

Present using this format:

```text
# <spec-name>

**Type**: Feature | **Status**: Implementing | **Version**: v2 | **Author**: Jane Doe
**Created**: 2025-02-15 | **Updated**: 2025-03-01

---

## What

[2-3 sentence summary extracted from the Overview section of requirements.md/bugfix.md/refactor.md. Capture the essence of what this spec is about.]

## Key Decisions

[Bullet list of Technical Decisions from design.md — just the decision titles and selected options, not the full rationale. If implementation.md has Decision Log entries, append them after the design decisions under a "During Implementation" sub-heading.]

- **Authentication approach**: OAuth 2.0 with PKCE flow
- **Session storage**: Redis with 24h TTL
- **API design**: RESTful with versioned endpoints

**During Implementation:**
- Used `express-rate-limit` instead of custom rate limiter (Task 7)
- Chose `zod` for input validation over `express-validator` (Task 12)

## Progress

[Extract from tasks.md task statuses]

Completed: 4/8 tasks (50%)
[====================....................] 50%

- [x] Task 1: Database schema migration
- [x] Task 2: OAuth provider setup
- [x] Task 3: Login endpoint
- [x] Task 4: Token refresh endpoint
- [ ] Task 5: User profile endpoint (In Progress)
- [ ] Task 6: Session management
- [ ] Task 7: Integration tests
- [ ] Task 8: Documentation

## Review Status

[Only show if reviews.md exists or reviewers array is non-empty in spec.json]

Approvals: 1/2 required
- Jane Doe: Approved (Round 1)
- Bob Lee: Pending
```

The summary extracts and synthesizes. It does NOT show the full content of any file.

### View: Full

Presents the complete content of all spec files, formatted with clear section separators.

1. Use the Read tool to read `spec.json` for metadata
2. Use the Read tool to read the requirements file (requirements.md, bugfix.md, or refactor.md)
3. Use the Read tool to read `design.md`
4. Use the Read tool to read `tasks.md`
5. If Use the Bash tool to check if the file exists at, Use the Read tool to read `implementation.md`
6. If Use the Bash tool to check if the file exists at, Use the Read tool to read `reviews.md`

Present using this format:

```text
# <spec-name> (Full Specification)

**Type**: Feature | **Status**: Implementing | **Version**: v2 | **Author**: Jane Doe
**Created**: 2025-02-15 | **Updated**: 2025-03-01

---

## Requirements

[Full content of requirements.md/bugfix.md/refactor.md, rendered as-is]

---

## Design

[Full content of design.md, rendered as-is]

---

## Tasks

[Full content of tasks.md, rendered as-is]

---

## Implementation Notes

[Full content of implementation.md if it exists, otherwise omit this section entirely]

---

## Reviews

[Full content of reviews.md if it exists, otherwise omit this section entirely]
```

Between each major section, insert a horizontal rule (`---`) for visual separation. Preserve the original markdown formatting of each file. The metadata header appears only once at the top.

### View: Specific Sections

When the user requests one or more specific sections:

1. Use the Read tool to read `spec.json` for metadata (always show the metadata header)
2. For each requested section, map to the correct file:
   - `requirements` → `requirements.md` (or `bugfix.md` / `refactor.md` based on spec type in spec.json)
   - `design` → `design.md`
   - `tasks` → `tasks.md`
   - `implementation` → `implementation.md`
   - `reviews` → `reviews.md`
3. Use the Read tool to read each requested file
4. If a requested file does not exist, note it (see Error Handling)

For a single section:

```text
# <spec-name>: Design

**Type**: Feature | **Status**: Implementing | **Version**: v2

---

[Full content of design.md]
```

For combination views (multiple sections):

```text
# <spec-name>: Requirements + Design

**Type**: Feature | **Status**: Implementing | **Version**: v2

---

## Requirements

[Full content of requirements.md]

---

## Design

[Full content of design.md]
```

### View: Status

A compact metadata and progress view. No spec content is shown — only metrics.

1. Use the Read tool to read `spec.json` for all metadata
2. Use the Read tool to read `tasks.md` and parse task statuses (count Completed, In Progress, Pending)
3. If Use the Bash tool to check if the file exists at `reviews.md`, Use the Read tool to read it to count review rounds

Present using this format:

```text
# <spec-name>: Status

## Metadata
| Field | Value |
|-------|-------|
| Type | Feature |
| Status | Implementing |
| Version | v2 |
| Author | Jane Doe (jane@example.com) |
| Created | 2025-02-15T10:30:00Z |
| Updated | 2025-03-01T14:22:00Z |

## Task Progress

Completed: 4/8 tasks (50%)
[====================....................] 50%

| # | Task | Status | Effort |
|---|------|--------|--------|
| 1 | Database schema migration | Completed | M |
| 2 | OAuth provider setup | Completed | L |
| 3 | Login endpoint | Completed | M |
| 4 | Token refresh endpoint | Completed | S |
| 5 | User profile endpoint | In Progress | M |
| 6 | Session management | Pending | M |
| 7 | Integration tests | Pending | L |
| 8 | Documentation | Pending | S |

## Review Status

Review Rounds: 2
Required Approvals: 2
Current Approvals: 1

| Reviewer | Status | Round | Date |
|----------|--------|-------|------|
| Jane Doe | Approved | 1 | 2025-02-20 |
| Bob Lee | Changes Requested | 1 | 2025-02-21 |
| Jane Doe | Approved | 2 | 2025-02-25 |
| Bob Lee | Pending | 2 | — |
```

If no review data exists (no reviewers in spec.json, no reviews.md), omit the Review Status section entirely.

### View: Walkthrough

An interactive, guided tour through the spec, section by section, with AI commentary.

**On platforms with `canAskInteractive: true`:**

1. Use the Read tool to read `spec.json` for metadata
2. Show the metadata header and a brief overview extracted from the requirements file
3. Use the AskUserQuestion tool "Ready to walk through this spec? I'll go section by section. Say 'next' to continue, 'skip' to skip a section, or name a specific section to jump to."
4. Present each section in order:
   a. **Requirements/Bugfix/Refactor** — Use the Read tool to read and present with full content. After presenting, add a 1-2 sentence AI commentary summarizing key points. Use the AskUserQuestion tool "Next section (Design), skip, or any questions?"
   b. **Design** — Use the Read tool to read and present with full content. Commentary on key architectural decisions. Use the AskUserQuestion tool "Next section (Tasks), skip, or any questions?"
   c. **Tasks** — Use the Read tool to read and present with full content. Commentary on progress and task ordering. Use the AskUserQuestion tool "Next section (Implementation Notes), skip, or done?"
   d. **Implementation Notes** — If Use the Bash tool to check if the file exists at, Use the Read tool to read and present. Commentary on deviations or blockers. Use the AskUserQuestion tool "Next section (Reviews), skip, or done?"
   e. **Reviews** — If Use the Bash tool to check if the file exists at, Use the Read tool to read and present. Commentary on review feedback themes.
5. After the last section: "That covers the full spec. Any questions or would you like to see any section again?"

**On platforms with `canAskInteractive: false` (e.g., Codex):**

Fall back to the Full view with AI commentary. Present all sections sequentially with a brief commentary paragraph before each section:

```text
# <spec-name>: Walkthrough

**Type**: Feature | **Status**: Implementing | **Version**: v2

---

## Requirements

**Overview**: This section defines 3 user stories focused on OAuth authentication. The primary acceptance criteria cover the complete token lifecycle.

[Full content of requirements.md]

---

## Design

**Overview**: The design selects OAuth 2.0 with PKCE. Key components include an OAuth client wrapper, token storage service, and session middleware.

[Full content of design.md]

---

[...remaining sections with commentary...]
```

### View: Initiative

When the user requests to view a specific initiative (`view initiative <id>`, `show initiative <id>`):

1. Use the Read tool to read(`.specops.json`) to get `specsDir` (default: `.specops`). Apply path containment rules.
2. Validate the initiative ID matches pattern `^(?!\\.{1,2}$)[a-zA-Z0-9._-]+$` (rejects `.` and `..` to prevent path traversal).
3. If Use the Bash tool to check if the file exists at(`<specsDir>/initiatives/<id>.json`), Use the Read tool to read it. If not found, Display a message to the user("Initiative '{id}' not found.") and show available initiatives.
4. For each spec ID in `initiative.specs`, Use the Read tool to read(`<specsDir>/<spec-id>/spec.json`) if it exists to get current status and metadata.

Present using this format:

```text
# Initiative: <title>

**ID**: <id> | **Status**: active | **Created**: 2025-03-01 | **Updated**: 2025-03-10
**Author**: Jane Doe | **Skeleton**: auth-oauth

## Execution Waves

### Wave 1
| Spec | Status | Type | Skeleton |
|------|--------|------|----------|
| auth-oauth | implementing | feature | Yes |

### Wave 2
| Spec | Status | Type | Dependencies |
|------|--------|------|-------------|
| auth-sessions | draft | feature | auth-oauth |
| auth-permissions | draft | feature | auth-oauth |

## Progress

Completed: 0/3 specs (0%)
[........................................] 0%

## Execution Log

[Last 10 entries from <specsDir>/initiatives/<id>-log.md if it exists]
```

### List Initiatives

When the user requests a list of all initiatives (`list initiatives`, `show initiatives`):

1. Use the Read tool to read(`.specops.json`) to get `specsDir` (default: `.specops`).
2. If Use the Bash tool to check if the file exists at(`<specsDir>/initiatives/`), Use the Glob tool to list(`<specsDir>/initiatives/`) to find all `.json` files (excluding `-log.md` files).
3. For each initiative JSON file, Use the Read tool to read it and collect summary fields: id, title, status, spec count, completed spec count.
4. If no initiatives exist, Display a message to the user("No initiatives found.") and stop.

Present using this format:

```text
# Initiatives Overview

| Initiative | Status | Specs | Completed | Last Updated |
|-----------|--------|-------|-----------|--------------|
| user-auth-overhaul | active | 3 | 0/3 | 2025-03-10 |
| payment-refactor | completed | 2 | 2/2 | 2025-03-05 |

**Summary**: 2 initiatives — 1 active, 1 completed
```

On interactive platforms (`canAskInteractive: true`), after showing the list:
Use the AskUserQuestion tool "Would you like to view any of these initiatives in detail?"

### Dependency Display in Spec Views

When displaying a spec in summary, full, or status views, include dependency information if the spec has `specDependencies` or `relatedSpecs` in its spec.json.

**In summary view**, add a "Dependencies" subsection after "Key Decisions":

```text
## Dependencies

**Part of**: user-auth-overhaul (Wave 2)

| Dependency | Required | Status |
|-----------|----------|--------|
| auth-oauth | Yes | completed |
| auth-sessions | No (advisory) | implementing |

**Related specs**: auth-permissions, payment-flow
```

**In status view**, add a "Dependencies" section after "Task Progress":

```text
## Dependencies

| Spec | Required | Status | Reason |
|------|----------|--------|--------|
| auth-oauth | Yes | completed | OAuth provider must be set up first |
| auth-sessions | No | implementing | Session storage is shared |

Related: auth-permissions
```

**In full view**, include the dependency display after the metadata header, before the Requirements section.

To build the dependency display:

1. Use the Read tool to read the spec's `spec.json` for `specDependencies`, `relatedSpecs`, and `partOf`.
2. For each entry in `specDependencies`, if Use the Bash tool to check if the file exists at(`<specsDir>/<dep-spec-id>/spec.json`), Use the Read tool to read it to get its current status. If the file does not exist, show the dependency as "not-created".
3. If `partOf` is set and Use the Bash tool to check if the file exists at(`<specsDir>/initiatives/<partOf>.json`), Use the Read tool to read the initiative JSON to get wave information. If the file does not exist, omit initiative context from the display.
4. If neither `specDependencies` nor `relatedSpecs` is present and `partOf` is not set, omit the Dependencies section entirely.

### Task Progress Parsing

To calculate task progress from tasks.md:

1. Count lines matching `**Status:** Completed` or `**Status:** completed` as completed tasks
2. Count lines matching `**Status:** In Progress` or `**Status:** in progress` as in-progress tasks
3. Count lines matching `**Status:** Pending` or `**Status:** pending` as pending tasks
4. Count lines matching `**Status:** Blocked` or `**Status:** blocked` as blocked tasks
5. Total = completed + in_progress + pending + blocked
6. Percentage = (completed / total) * 100, rounded to nearest integer

The progress bar format uses 40 characters width:

- Filled portion: `=`
- Empty portion: `.`
- Example: `[========================................] 60%`

### View/List Error Handling

**Spec not found:**

```text
Could not find spec "<spec-name>" in <specsDir>/.

Available specs:
- auth-oauth
- bugfix-checkout
- refactor-api

Did you mean one of these?
```

If no specs exist at all:

```text
No specs found in <specsDir>/. Create your first spec to get started.
```

**Section not found:**
When a requested section file does not exist:

```text
The section "implementation" does not exist for spec "<spec-name>".
This spec has: requirements, design, tasks
```

Then proceed to show the sections that do exist. Do not treat a missing optional section (implementation.md, reviews.md) as an error in full/summary/walkthrough views — simply omit it silently unless the user specifically requested that section.

**Corrupt or missing spec.json:**
If `spec.json` is missing or invalid JSON:

```text
Warning: spec.json is missing or invalid for "<spec-name>". Showing available files without metadata.
```

Proceed to show whatever spec files exist, with a minimal header (just the spec name, no metadata fields).

**Empty specsDir:**
If the specsDir directory does not exist:

```text
The specs directory (<specsDir>) does not exist. Create your first spec to get started.
```


## Configuration Handling

Load configuration from `.specops.json` at project root. If not found, use these defaults:

```json
{
  "specsDir": ".specops",
  "vertical": null,
  "templates": {
    "feature": "default",
    "bugfix": "default",
    "refactor": "default",
    "design": "default",
    "tasks": "default"
  },
  "team": {
    "conventions": [],
    "reviewRequired": false,
    "taskTracking": "none",
    "codeReview": {
      "required": false,
      "minApprovals": 1,
      "requireTests": true,
      "requireDocs": false
    }
  },
  "implementation": {
    "autoCommit": false,
    "createPR": false,
    "testing": "auto",
    "linting": { "enabled": true, "fixOnSave": false },
    "formatting": { "enabled": true },
    "delegationThreshold": 4
  },
  "dependencySafety": {
    "enabled": true,
    "severityThreshold": "medium",
    "autoFix": false,
    "allowedAdvisories": [],
    "scanScope": "spec"
  }
}
```

## Spec Directory Structure

Create specs in this structure:

```text
<specsDir>/
  index.json             (auto-generated spec index — rebuilt after every spec.json mutation)
  initiatives/           (initiative tracking — created when decomposition is approved)
    <initiative-id>.json (initiative definition — specs, waves, status)
    <initiative-id>-log.md (chronological execution log)
  <spec-name>/
    spec.json            (per-spec lifecycle metadata — always created)
    requirements.md      (or bugfix.md for bugs, refactor.md for refactors)
    design.md
    tasks.md
    implementation.md    (decision journal — always created)
    reviews.md           (optional - created during review cycle)
```

Example: `.specops/user-auth-oauth/requirements.md`

## Spec Review Configuration

If `config.team.specReview` is configured:

- **`enabled: true`**: Activate the collaborative review workflow. Specs pause after generation for team review.
- **`minApprovals`**: Number of approvals required before a spec can proceed to implementation. Default 1.
- **`allowSelfApproval: true`**: Allow the spec author to self-review and self-approve their own specs. When enabled, solo developers can go through the full review ritual (read spec, provide feedback, approve). Self-approvals are recorded with `selfApproval: true` on the reviewer entry and result in a `"self-approved"` status (distinct from peer `"approved"`). Default false.

If `specReview` is not configured, fall back to `reviewRequired`:

- `reviewRequired: true` enables review with `minApprovals = 1`.
- `reviewRequired: false` (default) disables the review workflow.

When both `specReview.enabled` and `reviewRequired` are set, `specReview.enabled` takes precedence.

### Workflow Impact: specReview / reviewRequired

- **Phase 2 step 7**: If enabled, set status to `in-review` and pause for review cycle.
- **Phase 2.5**: Full review/revision/self-review workflow activates.
- **Phase 3 step 1 (review gate)**: Blocks implementation until `approved` or `self-approved` status.

## Index Regeneration

The agent rebuilds `<specsDir>/index.json` after every `spec.json` creation or update:

1. Scan all subdirectories of `<specsDir>` for `spec.json` files (skip the `initiatives/` subdirectory — it contains initiative files, not spec files)
2. Collect summary fields from each: `id`, `type`, `status`, `version`, `author` (name), `updated`, and `partOf` (if present — the initiative ID this spec belongs to)
3. Write the summaries as a JSON array to `<specsDir>/index.json`

The index is a derived file — per-spec `spec.json` files are always the source of truth. If `index.json` is missing or has merge conflicts, regenerate it from per-spec files.

## Task Tracking Integration

If `config.team.taskTracking` is not `"none"`:

### Issue Creation Timing

After Phase 2 generates `tasks.md` and before Phase 3 begins, create external issues for all tasks with `**Priority:** High` or `**Priority:** Medium`. Low-priority tasks are tracked only in `tasks.md`.

### Issue Creation Protocol

For each eligible task:

#### Issue Body Composition

Before creating each issue, compose `<IssueBody>` by extracting content from spec artifacts. This composition is mandatory — writing a freeform description instead of following this template is a protocol breach.

For each eligible task, Use the Read tool to read `<specsDir>/<spec-name>/requirements.md` (or `bugfix.md`/`refactor.md`), Use the Read tool to read `<specsDir>/<spec-name>/spec.json`, and extract:

1. **Context**: The spec's Overview/Product Requirements first paragraph (1-3 sentences explaining "why")
2. **Spec type**: From `spec.json` `type` field
3. **Spec name**: From `spec.json` `id` field

Compose `<IssueBody>` using this template:

```text
## Context

<1-3 sentence summary from requirements.md/bugfix.md/refactor.md Overview explaining why this work exists>

**Spec:** `<spec-id>` | **Type:** <spec-type>

## Spec Artifacts

- [Requirements](<specsDir>/<spec-name>/<specArtifact>) where <specArtifact> is `requirements.md` for features, `bugfix.md` for bugfixes, or `refactor.md` for refactors
- [Design](<specsDir>/<spec-name>/design.md)
- [Tasks](<specsDir>/<spec-name>/tasks.md)

## Description

<Full text from the task's **Description:** section in tasks.md>

## Implementation Steps

<Numbered list from the task's **Implementation Steps:** section in tasks.md>

## Acceptance Criteria

<Checkbox items from the task's **Acceptance Criteria:** section in tasks.md>

## Files to Modify

<Bulleted list from the task's **Files to Modify:** section in tasks.md>

## Tests Required

<Checkbox items from the task's **Tests Required:** section in tasks.md. If the task has no Tests Required section, omit this entire section.>

---

**Priority:** <task priority> | **Effort:** <task effort> | **Dependencies:** <task dependencies>
```

Every section above (except Tests Required) is mandatory. If a section's source data is empty in `tasks.md`, write "None specified" rather than omitting the section.

#### GitHub Label Protocol

When `taskTracking` is `"github"`, apply labels to each created issue. Labels make issues searchable and categorizable.

**Label set per issue:**

- **Priority label**: `P-high` or `P-medium` (matching the task's `**Priority:**` field; Low tasks are not created as issues)
- **Spec label**: `spec:<spec-id>` where `<spec-id>` is the `id` from `spec.json` (e.g., `spec:proxy-metrics`)
- **Type label**: `<typeLabel>` where `<typeLabel>` is derived from the `type` field in `spec.json` using this mapping: `feature` → `feat`, `bugfix` → `fix`, `refactor` → `refactor`

**Label safety**: Before interpolating `<spec-id>` or `<typeLabel>` into label commands, validate that each value matches `^[a-z0-9][a-z0-9:_-]*$` (lowercase alphanumeric, hyphens, underscores, colons). Reject or normalize any value that doesn't match — this prevents shell injection via malformed spec IDs.

**Label creation**: Before creating the first issue for a spec, ensure all required labels exist. For each label in the set, run:

Use the Bash tool to run(`gh label create "<label>" --force --description "<description>"`)

The `--force` flag creates the label if it is missing and updates/overwrites its metadata (name/description/color) if it already exists. It is effectively idempotent only when you re-run it with the same arguments. Run this once per unique label definition, not once per issue.

Label descriptions:

- `P-high`: "High priority task"
- `P-medium`: "Medium priority task"
- `spec:<spec-id>`: "SpecOps spec: <spec-id>"
- `feat`: "Feature implementation"
- `fix`: "Bug fix"
- `refactor`: "Code refactoring"

**Jira and Linear**: Label/tag support varies. For Jira, use `--label` flag if available in the CLI version. For Linear, use `--label` flag. If the flag is unavailable or fails, skip labels silently — labels are enhancement, not requirement. Do not block issue creation on label failure.

**Shell safety**: `<TaskTitle>` and `<IssueBody>` contain user-controlled text. Before interpolating into shell commands, write the title and body to temporary files and pass via file-based arguments (e.g., `--body-file`). If file-based arguments are unavailable for the tracker CLI, single-quote the values with internal single-quotes escaped (`'` → `'\''`). Never pass unescaped user text directly in shell command strings. In command templates below, `<EscapedTaskTitle>` denotes the title after applying this escaping.

**GitHub** (`taskTracking: "github"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. Use the Write tool to create a temp file with `<IssueBody>` as content
3. Use the Bash tool to run(`gh issue create --title '<taskPrefix><EscapedTaskTitle>' --body-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue URL/number from stdout
5. Use the Edit tool to modify `tasks.md` — set the task's `**IssueID:**` to the returned issue identifier (e.g., `#42`)

**Jira** (`taskTracking: "jira"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. Use the Write tool to create a temp file with `<IssueBody>` as content
3. Use the Bash tool to run(`jira issue create --type=Task --summary='<taskPrefix><EscapedTaskTitle>' --description-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue key from stdout (e.g., `PROJ-123`)
5. Use the Edit tool to modify `tasks.md` — set the task's `**IssueID:**` to the returned key

**Linear** (`taskTracking: "linear"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. Use the Write tool to create a temp file with `<IssueBody>` as content
3. Use the Bash tool to run(`linear issue create --title '<taskPrefix><EscapedTaskTitle>' --description-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue identifier from stdout
5. Use the Edit tool to modify `tasks.md` — set the task's `**IssueID:**` to the returned identifier

If `config.team.taskPrefix` is set, prepend it to the issue title.

### Graceful Degradation

If the CLI tool is not installed or the command fails:

1. Display a message to the user("Warning: Could not create external issue for Task <N> — <error>. Continuing without external tracking for this task.")
2. Use the Edit tool to modify `tasks.md` — set `**IssueID:**` to `FAILED — <reason>` on the affected task
3. Do NOT block implementation — proceed with the internal state machine

### Status Sync

When task status changes in `tasks.md` (as part of the Task State Machine):

- **Pending → In Progress**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, update the external issue:
  - GitHub: Use the Bash tool to run(`gh issue edit <number> --add-label "in-progress"`)
  - Jira: Use the Bash tool to run(`jira issue move <key> "In Progress"`)
  - Linear: Use the Bash tool to run(`linear issue update <id> --status "In Progress"`)
- **In Progress → Completed**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, close the external issue:
  - GitHub: Use the Bash tool to run(`gh issue close <number>`)
  - Jira: Use the Bash tool to run(`jira issue move <key> "Done"`)
  - Linear: Use the Bash tool to run(`linear issue update <id> --status "Done"`)
- **In Progress → Blocked**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, update the external issue to blocked state:
  - GitHub: Use the Bash tool to run(`gh issue edit <number> --add-label "blocked"`)
  - Jira: Use the Bash tool to run(`jira issue move <key> "Blocked"`)
  - Linear: Use the Bash tool to run(`linear issue update <id> --status "Blocked"`)
- **Blocked → In Progress**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, move the external issue back to in-progress:
  - GitHub: Use the Bash tool to run(`gh issue edit <number> --remove-label "blocked" --add-label "in-progress"`)
  - Jira: Use the Bash tool to run(`jira issue move <key> "In Progress"`)
  - Linear: Use the Bash tool to run(`linear issue update <id> --status "In Progress"`)

Status Sync failures are warned (Display a message to the user), not blocking.

### Commit Linking

When `taskTracking` is not `"none"` and the current task has a valid IssueID (neither `None` nor prefixed with `FAILED`):

- If `autoCommit` is true: include the IssueID in the commit message (e.g., `feat: implement login form (#42)` or `feat: implement login form (PROJ-123)`)
- If `autoCommit` is false: suggest the commit format to the user: "Suggested commit: `<message> (<IssueID>)`"

### Workflow Impact: taskTracking

- **Phase 2 step 6**: If not `"none"`, create external issues for High/Medium tasks via Issue Creation Protocol.
- **Phase 3 step 1 (task tracking gate)**: Verifies issue creation was attempted — skipping is a protocol breach.
- **Phase 3 step 3**: On every task status transition, sync to external tracker via Status Sync.
- **Phase 3 step 7**: If `autoCommit` and valid IssueID, include IssueID in commit message via Commit Linking.

### Task Tracking Gate

At the start of Phase 3, after the review gate check, verify external issue creation. Skipping this gate when `config.team.taskTracking` is not `"none"` is a protocol breach.

1. Use the Read tool to read `tasks.md` — identify all tasks with `**Priority:** High` or `**Priority:** Medium`
2. For each eligible task, require `**IssueID:**` to be either:
   - a valid tracker identifier for the configured platform (e.g., `#42`, `PROJ-123`), or
   - `FAILED — <reason>` produced by Graceful Degradation after an attempted creation
   Values like `TBD`, `N/A`, or other placeholders do not satisfy the gate.
3. If any are missing: attempt issue creation for the missing tasks using the Issue Creation Protocol above
4. If issue creation succeeds for some tasks but fails for others (CLI tool error, network failure): Display a message to the user("Partial external tracking — <N>/<M> task(s) created, <F> failed") and proceed. The Graceful Degradation rules apply to individual failures.
5. If issue creation fails for ALL eligible tasks: Display a message to the user("External tracking unavailable — all <N> issue creation attempts failed. Proceeding with internal task tracking only.") and proceed.
6. The gate enforces attempted creation, not 100% success. An agent that never attempts issue creation when `taskTracking` is configured has committed a protocol breach.

## Team Conventions

Always incorporate `config.team.conventions` into:

- Requirements (add "Team Conventions" section)
- Design decisions (validate against conventions)
- Implementation (follow conventions strictly)
- Code review considerations

## Code Review Integration

If `config.team.codeReview` is configured:

- **`required: true`**: After implementation, summarize changes for review and note that code review is required before merging
- **`minApprovals`**: Include the required approval count in PR description
- **`requireTests: true`**: Ensure all tasks include tests; block completion if test coverage is insufficient
- **`requireDocs: true`**: Ensure public APIs have documentation; add JSDoc/docstrings as part of implementation

### Workflow Impact: codeReview

- **Phase 3 step 6**: If `requireTests`, run tests for every task; block completion on insufficient coverage.
- **Phase 4 step 7**: If `required`, include review requirement and `minApprovals` count in PR description.

## Linting & Formatting

If `config.implementation.linting` is configured:

- **`enabled: true`**: Run the project's linter after implementing each task. Fix any violations before marking the task complete.
- **`fixOnSave: true`**: Note in implementation that auto-fix is expected; don't manually fix auto-fixable issues.

If `config.implementation.formatting` is configured:

- **`enabled: true`**: Run the configured formatting tool (`prettier`, `black`, `rustfmt`, `gofmt`) before committing.
- **`tool`**: Use the specified formatter. If not specified, detect from project config files (e.g., `.prettierrc`, `pyproject.toml`).

### Workflow Impact: linting / formatting

- **Phase 3 step 6**: If `linting.enabled`, run linter after each task and fix violations before marking complete.
- **Phase 3 step 7**: If `formatting.enabled`, run formatter before committing.

## Test Framework

If `config.implementation.testFramework` is set (e.g., `jest`, `mocha`, `pytest`, `vitest`):

- Use the specified framework when generating test files
- Use the framework's assertion style and conventions
- Run tests with the appropriate command (e.g., `npx jest`, `pytest`, `npx vitest`)

If not set, detect the test framework from the project's existing test files and `package.json`/`pyproject.toml`.

### Workflow Impact: testing / testFramework

- **Phase 3 step 6**: If `testing` is `"auto"`, run tests after each task. If `"skip"`, skip testing (with safety warning). If `"manual"`, note that tests should be run.
- **Phase 3 step 6**: If `testFramework` is set, use that framework for test generation and execution.

### Workflow Impact: autoCommit / createPR

- **Phase 3 step 7**: If `autoCommit`, commit changes after each task. If false, suggest commit format.
- **Phase 4 step 7**: If `createPR`, create a pull request after implementation completes.

### Workflow Impact: taskDelegation

- **Phase 3 step 2**: If `"auto"`, compute a complexity score from pending tasks (effort weights + file count) and activate delegation when score >= threshold. The threshold is determined by `config.implementation.delegationThreshold` (integer, default 4). If `"always"`, activate regardless. If `"never"`, use sequential execution.

### Workflow Impact: delegationThreshold

- **Phase 3 step 2 (auto mode)**: The `delegationThreshold` config (integer, default 4) sets the complexity score at which task delegation auto-activates. Lower values activate delegation more aggressively (more specs benefit from fresh-context task execution). The score formula is: `sum(effort_weights) + floor(distinct_files / 5)` where effort weights are S=1, M=2, L=3. Examples at threshold 4: 4 small tasks (score 4), 2 medium tasks (score 4), 1 large + 1 small task (score 4).

## Module-Specific Configuration

If `config.modules` is configured (for monorepo/multi-module projects):

- Each module can define its own `specsDir` and `conventions`
- Module conventions **merge with** root `team.conventions` (module-specific conventions take priority on conflicts)
- Create specs in the module-specific specsDir: `<module.specsDir>/<spec-name>/`
- When a request targets a specific module, apply that module's conventions
- If no module is specified and the request is ambiguous, ask which module to target

## Integrations

If `config.integrations` is configured, use these as **contextual information**:

- **`ci`**: Reference the CI system in rollout plans (e.g., "Run in GitHub Actions pipeline")
- **`deployment`**: Include deployment target in rollout plans (e.g., "Deploy to Vercel")
- **`monitoring`**: Reference monitoring in risk mitigations (e.g., "Monitor errors in Sentry")
- **`analytics`**: Include analytics tracking in acceptance criteria when relevant

These are informational — the agent uses them to generate more accurate specs, not to directly invoke the tools.

### Workflow Impact: dependencySafety

- **Phase 1 step 3**: If `dependencies.md` steering file exists and `_generatedAt` is over 30 days old, notify the user about stale dependency data.
- **Phase 2 step 6.7 (mandatory gate)**: If `enabled` is not `false`, execute the dependency safety verification. Block implementation when findings exceed `severityThreshold`. Skipping this gate when enabled is a protocol breach.
- **Phase 2 step 6.7**: If `autoFix` is `true`, attempt automatic remediation before re-evaluating.
- **Phase 2 step 6.7**: Filter `allowedAdvisories` CVE IDs from blocking decisions (still recorded in audit artifact).
- **Phase 2 step 6.7**: `scanScope` controls whether to audit only spec-relevant ecosystems (`"spec"`) or all detected ecosystems (`"project"`).

### Workflow Impact: integrations

- **Informational only**: Referenced in Phase 2 spec generation (rollout plans, risk mitigations, acceptance criteria). No workflow conditionals — context enrichment only.

## System-Managed Fields

The following `.specops.json` fields are written by installers and must not be prompted for or modified by the agent:

- **`_installedVersion`**: The SpecOps version that was installed. Set by `install.sh` and `remote-install.sh`.
- **`_installedAt`**: ISO 8601 timestamp of when SpecOps was installed.

When modifying `.specops.json` (e.g., during `/specops init`), preserve these fields if they already exist. Do not include them in configuration prompts or templates shown to users.


## Spec Decomposition

Spec Decomposition provides multi-spec intelligence: automatic scope assessment, split detection, an initiative data model for tracking related specs, cross-spec dependencies with enforcement, cycle detection, dependency gates, scope hammering for blocker resolution, and the walking skeleton principle. All behavior is always-on — no configuration flag to enable or disable.

### 1. Scope Assessment Gate (Phase 1.5)

After Phase 1 step 9 (context summary), before Phase 2, run the Scope Assessment Gate. This gate is always-on and runs unconditionally for every spec.

**Complexity signals** — check the user's feature request for the following indicators:

| Signal | Detection Method |
| --- | --- |
| Independent deliverables | 2+ distinct functional units that could ship separately |
| Distinct code domains | >2 separate code areas (e.g., API + UI + database) |
| Language signals | Phrases like "and also", "plus", "additionally", "as well as" joining unrelated capabilities |
| Estimated task count | >8-10 tasks estimated from the request scope |
| Independent criteria clusters | Acceptance criteria that group into separable clusters with no cross-references |

**Assessment procedure:**

1. Evaluate the feature request against all 5 complexity signals.
2. If 2 or more signals are present, decomposition is recommended.
3. If fewer than 2 signals are present, proceed as a single spec — no decomposition needed.

**When decomposition is recommended:**

1. Build a decomposition proposal with the following fields for each proposed spec:

| Field | Description |
| --- | --- |
| Name | Descriptive spec identifier (kebab-case) |
| Description | 1-2 sentence summary of scope |
| Estimated tasks | Rough count (S: 1-3, M: 4-6, L: 7-10) |
| Execution order | Which wave this spec belongs to (wave 1 = no dependencies, wave 2 = depends on wave 1, etc.) |
| Dependency rationale | Why this spec depends on or is independent of others |

1. If `canAskInteractive` is true: Use the AskUserQuestion tool("This feature request has multiple independent components. I recommend splitting into {N} specs:\n\n{proposal table}\n\nApprove decomposition? (yes/no/modify)")
   - If approved: proceed to initiative creation (step 3).
   - If declined: proceed as a single spec — continue to Phase 2.
   - If modified: adjust the proposal per user feedback and re-present.

2. If `canAskInteractive` is false: Display a message to the user("Scope assessment detected {N} independent components. Proceeding as a single spec in non-interactive mode. Consider splitting manually:\n\n{proposal table}") and continue to Phase 2 as a single spec.

**When decomposition is approved (interactive mode):**

1. Create the initiative:
   - Generate an initiative ID from the feature name (kebab-case, matching pattern `^[a-zA-Z0-9._-]+$`).
   - Compute execution waves from the proposed dependency rationale (see section 6: Initiative Order Derivation).
   - Identify the walking skeleton (see section 9: Walking Skeleton Principle).
   - Use the Bash tool to run(`mkdir -p <specsDir>/initiatives`)
   - Use the Bash tool to run(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) to capture the current timestamp.
   - Use the Write tool to create(`<specsDir>/initiatives/<initiative-id>.json`) with the initiative data model (see section 3).
   - Display a message to the user("Created initiative '{initiative-id}' with {N} specs in {W} execution waves.")

2. Continue with the first spec (wave 1, walking skeleton) — proceed to Phase 2. The current spec's `partOf` field in spec.json will be set to the initiative ID during Phase 2 step 3.

### 2. Split Detection (Phase 2 Safety Net)

After Phase 2 step 1 (requirements drafting), if Phase 1.5 did NOT recommend decomposition, run a second-pass split detection as a safety net.

**Procedure:**

1. Review the drafted requirements for criteria clustering:
   - Group acceptance criteria by functional area.
   - If criteria cluster into 2+ independent groups (groups with no cross-references between them), decomposition may have been missed.

2. If independent clusters are detected:
   - Follow the same proposal format as Phase 1.5 (step 4).
   - Follow the same interactive/non-interactive decision flow as Phase 1.5 (steps 5-6).
   - If approved: create the initiative (Phase 1.5 step 7) and continue with the current spec as the first spec in the initiative.

3. If no independent clusters are detected, continue with Phase 2 as normal.

This check fires only when Phase 1.5 did not trigger (either because signals were below threshold or because the user declined). It does not run if decomposition was already approved.

### 3. Initiative Data Model

An initiative groups related specs created through decomposition (or manually) into a tracked unit with execution ordering.

**Location:** `<specsDir>/initiatives/<initiative-id>.json`

**Fields:**

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | Yes | Initiative identifier, pattern `^[a-zA-Z0-9._-]+$` |
| `title` | string | Yes | Human-readable title (maxLength 200) |
| `description` | string | No | Detailed description (maxLength 2000) |
| `created` | string | Yes | ISO 8601 timestamp of creation |
| `updated` | string | Yes | ISO 8601 timestamp of last modification |
| `author` | string | Yes | Author name (maxLength 100) |
| `specs` | string[] | Yes | Array of spec IDs belonging to this initiative (maxItems 50) |
| `order` | string[][] | Yes | Execution waves — array of arrays where each inner array is a wave of spec IDs that can execute in parallel (maxItems 20 waves, inner maxItems 50) |
| `skeleton` | string | No | Spec ID of the walking skeleton (first wave-1 spec) |
| `status` | string | Yes | `active` or `completed` — derived from member spec statuses |

**Schema:** Validated against `initiative-schema.json` (draft-07, `additionalProperties: false` at all object levels).

**Status derivation:**

- `active`: At least one member spec has `status` other than `completed`.
- `completed`: All member specs have `status == "completed"`.

Status is recomputed whenever a member spec's status changes (Phase 4 step 6.3).

### 4. Cross-Spec Dependencies

Cross-spec dependencies declare explicit relationships between specs, enabling enforcement of execution ordering and blocker tracking.

**Declaration format in spec.json:**

The `specDependencies` array (optional, maxItems 50) contains dependency entries:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `specId` | string | Yes | ID of the dependency spec (maxLength 100, pattern `^[a-zA-Z0-9._-]+$`) |
| `reason` | string | Yes | Why this spec depends on the other (maxLength 500) |
| `required` | boolean | No | If `true`, this is a hard dependency — Phase 3 is blocked until the dependency is completed. If `false` or omitted, this is an advisory dependency — a warning is shown but Phase 3 proceeds. |
| `contractRef` | string | No | Path to an interface contract or shared artifact (maxLength 200) |

**Population:** During Phase 2 step 3, when writing spec.json:

- If the spec belongs to an initiative (`partOf` is set), populate `specDependencies` based on the initiative's execution wave ordering. Only add dependencies where actual coupling exists (shared data, API contracts, or integration points) — do not blindly depend on every spec in the prior wave.
- The `relatedSpecs` array (optional, maxItems 20) lists informational references to specs that are related but not dependencies (see section 10: Cross-Linking).
- Run cycle detection (section 5) before writing spec.json. If a cycle is detected, do not write and STOP with the cycle chain.

### 5. Cycle Detection

Cycle detection prevents circular dependencies across specs. It uses depth-first search (DFS) with three-color marking (white/gray/black).

**Algorithm:**

1. Use the Read tool to read(`<specsDir>/index.json`) to enumerate all specs. For each spec, if Use the Bash tool to check if the file exists at(`<specsDir>/<spec-id>/spec.json`), Use the Read tool to read it to get its `specDependencies` array.

2. Build an adjacency list: for each spec with `specDependencies`, create edges from the spec to each `specId` in its dependencies.

3. Initialize all nodes as white (unvisited).

4. For each white node, run DFS:
   - Mark node gray (in progress).
   - For each neighbor (dependency):
     - If gray: cycle detected — record the cycle chain from the current node back through the gray nodes.
     - If white: recurse.
   - Mark node black (completed).

5. If any cycle is detected:
   - Display a message to the user("Circular dependency detected: {cycle chain, e.g., spec-a → spec-b → spec-c → spec-a}. Resolve by removing or making one dependency advisory (required: false).")
   - STOP — do not proceed. Circular dependencies are a protocol breach.

6. If no cycles: continue.

**When cycle detection runs:**

- Phase 2 step 3: Before writing `specDependencies` to spec.json.
- Phase 3 step 1: As part of the dependency gate (section 7).
- Reconciliation: Check 6 (Dependency Health).

### 6. Initiative Order Derivation

Execution waves are derived from the dependency graph via topological sort.

**Algorithm:**

1. Build the dependency graph from all specs in the initiative:
   - For each spec in `initiative.specs`, read its `specDependencies` from spec.json.
   - Only consider dependencies where the `specId` is also in `initiative.specs` (ignore external dependencies for wave ordering).

2. Topological sort with wave assignment:
   - Wave 1: All specs with no intra-initiative dependencies.
   - Wave N: All specs whose intra-initiative dependencies are all in waves 1 through N-1.

3. Run cycle detection (section 5) on the intra-initiative graph. If a cycle is detected, STOP.

4. Write the computed waves to `initiative.order` as an array of arrays.

5. Update `initiative.updated` timestamp: Use the Bash tool to run(`date -u +"%Y-%m-%dT%H:%M:%SZ"`).

6. Use the Write tool to create(`<specsDir>/initiatives/<initiative-id>.json`) with the updated order.

**Recomputation trigger:** Whenever `specDependencies` change for any spec in the initiative (Phase 2 step 3 writes, reconciliation updates, manual edits).

### 7. Phase 3 Dependency Gate

At Phase 3 step 1, before any implementation work begins, run the dependency gate. This gate is mandatory — skipping it is a protocol breach.

**Procedure:**

1. Use the Read tool to read(`<specsDir>/<spec-name>/spec.json`) to get `specDependencies`.

2. If `specDependencies` is absent or empty, the gate passes — proceed to implementation.

3. For each entry in `specDependencies`:
   a. Use the Read tool to read(`<specsDir>/<entry.specId>/spec.json`) to get the dependency's status.
   b. If the dependency spec.json does not exist: Display a message to the user("Warning: Dependency '{entry.specId}' not found. Treating as unmet.") and treat as unmet.

4. **Required dependencies** (`required: true`):
   - If any required dependency has `status` other than `completed`: STOP.
   - Display a message to the user("Phase 3 BLOCKED: Required dependency '{entry.specId}' has status '{status}'. Cannot proceed until it is completed.")
   - Present scope hammering options (section 8).

5. **Advisory dependencies** (`required: false` or `required` omitted):
   - If an advisory dependency is not completed: Display a message to the user("Advisory: Dependency '{entry.specId}' is not yet completed (status: {status}). Proceeding with implementation, but be aware of potential integration issues.")
   - Continue — advisory dependencies do not block.

6. Run cycle detection (section 5) as a safety net — even if cycles were checked at write time, re-verify before implementation.

7. If all required dependencies are completed (or no required dependencies exist), the gate passes — proceed to implementation.

### 8. Scope Hammering

When a spec encounters a dependency blocker (Phase 3 dependency gate fails), present structured resolution options instead of indefinite waiting.

**Options:**

| Option | Resolution Type | Description |
| --- | --- | --- |
| Cut scope | `scope_cut` | Remove the blocked functionality from this spec. Update requirements and tasks to exclude the dependent feature. |
| Define interface contract | `interface_defined` | Define the expected interface or contract for the dependency, create a stub implementation, and proceed. Record the contract path in `contractRef`. |
| Wait | `deferred` | Defer this spec until the dependency completes. Do not proceed to Phase 3. |
| Escalate | `escalated` | Flag the blocker for human decision. Record the escalation in the blockers table. |

**Procedure:**

1. If `canAskInteractive` is true: Use the AskUserQuestion tool("Dependency '{entry.specId}' is blocking Phase 3. Options:\n1. Cut scope — remove dependent functionality\n2. Define interface — create contract + stub, proceed\n3. Wait — defer until dependency completes\n4. Escalate — flag for human decision\n\nChoose an option:")

2. If `canAskInteractive` is false: Display a message to the user("Dependency '{entry.specId}' is blocking Phase 3. Deferring until dependency completes.") and use `deferred` as the resolution type.

3. Record the resolution in the Cross-Spec Blockers table in the spec's `tasks.md` (and `requirements.md` / `design.md` if present):

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| --- | --- | --- | --- | --- |
| {description} | {specId} | {scope_cut/interface_defined/deferred/escalated} | {detail} | {open/resolved} |

1. If `scope_cut`: Update requirements.md and tasks.md to remove the blocked functionality. Use the Read tool to read spec.json, remove the dependency entry from `specDependencies` (or set `required: false`), Use the Write tool to create spec.json. Proceed to Phase 3 with reduced scope.
2. If `interface_defined`: Use the Write tool to create the interface contract. Use the Read tool to read spec.json, update the specDependency entry's `contractRef` field with the contract path, Use the Write tool to create spec.json. Proceed to Phase 3 with stub implementation.
3. If `deferred`: Do not proceed to Phase 3. The spec remains in its current status until the dependency completes.
4. If `escalated`: Do not proceed to Phase 3. Display a message to the user("Blocker escalated. Awaiting human decision.")

### 9. Walking Skeleton Principle

When an initiative is created, the first spec in wave 1 is designated as the walking skeleton.

**Purpose:** The walking skeleton establishes an end-to-end integration path across all architectural layers touched by the initiative. Subsequent specs build on this proven foundation.

**Designation:**

1. From the initiative's execution waves (section 6), identify wave 1 specs.
2. If wave 1 has a single spec, it is the skeleton.
3. If wave 1 has multiple specs, select the one that touches the most architectural layers (based on the decomposition proposal's domain analysis).
4. Record the skeleton spec ID in `initiative.skeleton`.

**Skeleton spec guidance:**

- The skeleton spec should prioritize breadth over depth — it establishes the integration path, not full feature implementation.
- During Phase 2 of the skeleton spec, include a requirement that the implementation proves the end-to-end path works (e.g., data flows from input to output through all layers).
- Display a message to the user("Spec '{skeleton-id}' is the walking skeleton for initiative '{initiative-id}'. It should establish the end-to-end integration path.")

### 10. Cross-Linking

The `relatedSpecs` array in spec.json provides informational cross-references between specs.

**Format:** Array of spec ID strings (maxItems 20, each maxLength 100, pattern `^[a-zA-Z0-9._-]+$`).

**Population:** During Phase 2 step 3, populate `relatedSpecs` with:

- Other specs in the same initiative (if `partOf` is set).
- Specs that modify overlapping files (detected from memory patterns if available).
- Specs explicitly mentioned in the feature request.

**Usage:** `relatedSpecs` is informational only — it does not affect execution ordering or gates. It appears in spec view output (core/view.md) and audit reports (core/reconciliation.md) to help developers understand the broader context.

### Platform Adaptation

| Capability | Impact |
| --- | --- |
| `canAskInteractive: true` | Full interactive decomposition approval, scope hammering options presented as choices |
| `canAskInteractive: false` | Decomposition notified but not applied (proceed as single spec). Scope hammering defaults to `deferred`. |
| `canExecuteCode: true` (all platforms) | Shell commands available for `mkdir -p`, `date`, cycle detection graph traversal via file reads |
| `canTrackProgress: false` | Report decomposition and dependency status in response text |
| `canDelegateTask: true` | Initiative orchestrator can dispatch specs as fresh sub-agents (see core/initiative-orchestration.md) |
| `canDelegateTask: false` | Initiative specs executed sequentially or via checkpoint+prompt |
