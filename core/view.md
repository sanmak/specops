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

1. READ_FILE(`.specops.json`) to get `specsDir` (default: `.specops`). Apply path containment rules from the Configuration Safety module.
2. If a spec-name is provided:
   a. Check FILE_EXISTS(`<specsDir>/<spec-name>/spec.json`)
   b. If not found, LIST_DIR(`<specsDir>`) to find all spec directories
   c. Check if spec-name is a partial match against any directory name. If exactly one match, use it. If multiple matches, present them and ASK_USER to clarify. On platforms without `canAskInteractive`, show the closest matches and stop.
   d. If no match, show "Spec not found" error (see Error Handling below)
3. READ_FILE(`<specsDir>/<spec-name>/spec.json`) to load metadata

### List Specs

When the user requests a list of all specs:

1. READ_FILE(`<specsDir>/index.json`) if it exists
2. If `index.json` does not exist or is invalid, scan spec directories:
   a. LIST_DIR(`<specsDir>`) to find all subdirectories
   b. For each directory, READ_FILE(`<specsDir>/<dir>/spec.json`) if it exists
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

1. For each spec with a `partOf` field, if FILE_EXISTS(`<specsDir>/initiatives/<partOf>.json`), READ_FILE it to get the initiative title, status, order (waves), and skeleton. If the initiative file does not exist, treat the spec as standalone (log a warning but do not fail).
2. Group specs by `partOf` value. For each group, show the initiative title and status as the section header.
3. Add a "Wave" column showing which execution wave the spec belongs to (from `initiative.order`). If the spec is the skeleton, append "(skeleton)" to the wave number.
4. Specs without `partOf` go under "Standalone Specs".

On interactive platforms (`canAskInteractive: true`), after showing the list:
ASK_USER "Would you like to view any of these specs in detail, or view an initiative?"

### View: Summary

The default view. Provides an executive overview — answering "What is this spec and where does it stand?" in under 30 seconds of reading.

1. READ_FILE(`<specsDir>/<spec-name>/spec.json`) for metadata
2. Determine which requirement file exists: READ_FILE for `requirements.md`, `bugfix.md`, or `refactor.md`
3. READ_FILE(`<specsDir>/<spec-name>/design.md`)
4. READ_FILE(`<specsDir>/<spec-name>/tasks.md`)
5. READ_FILE(`<specsDir>/<spec-name>/implementation.md`) for decision journal entries
6. Optionally READ_FILE `reviews.md` if it exists

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

1. READ_FILE `spec.json` for metadata
2. READ_FILE the requirements file (requirements.md, bugfix.md, or refactor.md)
3. READ_FILE `design.md`
4. READ_FILE `tasks.md`
5. If FILE_EXISTS, READ_FILE `implementation.md`
6. If FILE_EXISTS, READ_FILE `reviews.md`

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

1. READ_FILE `spec.json` for metadata (always show the metadata header)
2. For each requested section, map to the correct file:
   - `requirements` → `requirements.md` (or `bugfix.md` / `refactor.md` based on spec type in spec.json)
   - `design` → `design.md`
   - `tasks` → `tasks.md`
   - `implementation` → `implementation.md`
   - `reviews` → `reviews.md`
3. READ_FILE each requested file
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

1. READ_FILE `spec.json` for all metadata
2. READ_FILE `tasks.md` and parse task statuses (count Completed, In Progress, Pending)
3. If FILE_EXISTS `reviews.md`, READ_FILE it to count review rounds

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

1. READ_FILE `spec.json` for metadata
2. Show the metadata header and a brief overview extracted from the requirements file
3. ASK_USER "Ready to walk through this spec? I'll go section by section. Say 'next' to continue, 'skip' to skip a section, or name a specific section to jump to."
4. Present each section in order:
   a. **Requirements/Bugfix/Refactor** — READ_FILE and present with full content. After presenting, add a 1-2 sentence AI commentary summarizing key points. ASK_USER "Next section (Design), skip, or any questions?"
   b. **Design** — READ_FILE and present with full content. Commentary on key architectural decisions. ASK_USER "Next section (Tasks), skip, or any questions?"
   c. **Tasks** — READ_FILE and present with full content. Commentary on progress and task ordering. ASK_USER "Next section (Implementation Notes), skip, or done?"
   d. **Implementation Notes** — If FILE_EXISTS, READ_FILE and present. Commentary on deviations or blockers. ASK_USER "Next section (Reviews), skip, or done?"
   e. **Reviews** — If FILE_EXISTS, READ_FILE and present. Commentary on review feedback themes.
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

1. READ_FILE(`.specops.json`) to get `specsDir` (default: `.specops`). Apply path containment rules.
2. Validate the initiative ID matches pattern `^(?!\\.{1,2}$)[a-zA-Z0-9._-]+$` (rejects `.` and `..` to prevent path traversal).
3. If FILE_EXISTS(`<specsDir>/initiatives/<id>.json`), READ_FILE it. If not found, NOTIFY_USER("Initiative '{id}' not found.") and show available initiatives.
4. For each spec ID in `initiative.specs`, READ_FILE(`<specsDir>/<spec-id>/spec.json`) if it exists to get current status and metadata.

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

1. READ_FILE(`.specops.json`) to get `specsDir` (default: `.specops`).
2. If FILE_EXISTS(`<specsDir>/initiatives/`), LIST_DIR(`<specsDir>/initiatives/`) to find all `.json` files (excluding `-log.md` files).
3. For each initiative JSON file, READ_FILE it and collect summary fields: id, title, status, spec count, completed spec count.
4. If no initiatives exist, NOTIFY_USER("No initiatives found.") and stop.

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
ASK_USER "Would you like to view any of these initiatives in detail?"

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

1. READ_FILE the spec's `spec.json` for `specDependencies`, `relatedSpecs`, and `partOf`.
2. For each entry in `specDependencies`, if FILE_EXISTS(`<specsDir>/<dep-spec-id>/spec.json`), READ_FILE it to get its current status. If the file does not exist, show the dependency as "not-created".
3. If `partOf` is set and FILE_EXISTS(`<specsDir>/initiatives/<partOf>.json`), READ_FILE the initiative JSON to get wave information. If the file does not exist, omit initiative context from the display.
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
