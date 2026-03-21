## Audit Mode

SpecOps `audit` detects drift between spec artifacts and the live codebase. It runs 5 checks and produces a health report. `reconcile` guides interactive repair of findings.

### Mode Detection

When the user invokes SpecOps, check for audit or reconcile intent after the steering command check and before the interview check:

- **Audit mode**: request matches `audit`, `audit <name>`, `health check`, `check drift`, `spec health`. These must refer to SpecOps spec health, NOT a product feature like "audit log" or "health endpoint". If detected, follow the Audit Workflow below.
- **Reconcile mode**: request matches `reconcile <name>`, `fix <name>` (when referring to a spec, not code), `repair <name>`, `sync <name>`. If detected, follow the Reconcile Workflow below.

If neither pattern matches, continue to interview check and the standard phases.

### Audit Workflow

1. If Use the Bash tool to check if the file exists at(`.specops.json`), Use the Read tool to read(`.specops.json`) to get `specsDir`; otherwise use default `.specops`
2. Parse target spec name from the request if present.
   - If a name is given, audit that spec (any status, including completed — Post-Completion Modification runs for completed specs only when audited by name).
   - If no name is given, Use the Glob tool to list(`<specsDir>`) to enumerate candidate directories, keep only entries where Use the Bash tool to check if the file exists at(`<specsDir>/<dir>/spec.json`) is true (skipping non-spec folders like `steering/`), load each retained `spec.json`, then audit all specs whose `status` is not `completed` (completed specs are frozen; use `/specops audit <name>` to explicitly audit a completed spec).
3. For each target spec:
   a. If Use the Bash tool to check if the file exists at(`<specsDir>/<name>/spec.json`), Use the Read tool to read(`<specsDir>/<name>/spec.json`) to load metadata. If not found, Display a message to the user(`"Spec '<name>' not found in <specsDir>. Run '/specops list' to see available specs."`) and stop.
   b. If Use the Bash tool to check if the file exists at(`<specsDir>/<name>/tasks.md`), Use the Read tool to read(`<specsDir>/<name>/tasks.md`) to load tasks.
   c. Run the 5 drift checks below. Record each result as `Healthy`, `Warning`, or `Drift`.
   d. Overall health = worst result across all checks.
4. Present the Audit Report (format below).

### Five Drift Checks

### File Drift

Verify all "Files to Modify" paths in `tasks.md` still exist.

- Parse all file paths listed under `**Files to Modify:**` sections across all tasks
- For each path, check Use the Bash tool to check if the file exists at(`<path>`)
- If Use the Bash tool to check if the file exists at returns false AND `canAccessGit` is true: Use the Bash tool to run(`git log --diff-filter=R --summary --oneline -- "<path>"`) to detect renames; Use the Bash tool to run(`git log --diff-filter=D --oneline -- "<path>"`) to detect deletions
  - Renamed file → **Warning** (note new path if found)
  - Deleted file → **Drift**
  - No git available → **Warning** (cannot confirm deletion vs rename)
- If no "Files to Modify" entries found → skip check, note "No file paths to check" in report
- If wildcard/glob paths found → skip those paths, note in report

### Post-Completion Modification

For completed specs, detect files modified after `spec.json.updated` timestamp.

- Only runs when `spec.json.status == "completed"`
- Requires `canAccessGit: true`; if false → skip with note "git unavailable, skipped"
- For each file path from "Files to Modify": Use the Bash tool to run(`git log --after="<spec.json.updated>" --oneline -- "<path>"`)
- Any output (commits found) → **Warning** with commit summaries listed
- No commits → **Healthy**

### Task Status Inconsistency

Detect tasks whose claimed status conflicts with file reality.

- **Completed tasks with missing files**: If a task is marked `Completed` and any of its "Files to Modify" paths do not exist → **Drift**
- **Pending tasks with early implementations**: If `canAccessGit` is true and a task is `Pending` and its "Files to Modify" files have commits after `spec.json.created` → **Warning**; if `canAccessGit` is false → skip this sub-check and note "git unavailable, cannot detect early implementation" in the report
- Tasks with no "Files to Modify" section → skip that task
- If no inconsistencies found → **Healthy**

### Staleness

Detect specs stuck without activity.

- Parse `spec.json.updated` and compute age using Use the Bash tool to run(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) for current time
- Rules by status:
  - `implementing`: > 14 days inactive → **Drift**; > 7 days → **Warning**
  - `draft` or `in-review`: > 30 days → **Warning**
  - `completed`: always **Healthy** (completed specs don't go stale)
- If `spec.json.updated` is missing (malformed or legacy spec) → **Warning** (cannot determine age)

### Cross-Spec Conflicts

Detect multiple active (non-completed) specs referencing the same files.

- Use the Glob tool to list(`<specsDir>`) to find candidate directories; keep only those where Use the Bash tool to check if the file exists at(`<specsDir>/<dir>/spec.json`) is true; Use the Read tool to read each `<specsDir>/<dir>/spec.json` to load metadata
- For each spec with `status ≠ completed` (active specs only): Use the Read tool to read(`<specsDir>/<dir>/tasks.md`) if it exists, collect all "Files to Modify" paths
- Build a map: `file_path → [distinct spec names]` (deduplicate spec names per file — a single spec referencing the same file in multiple tasks counts as one)
- Any file with 2+ distinct specs → **Warning** (no repair available — informational only)
- For single-spec audit: still load all active specs to detect conflicts involving the target

### Health Summary

Overall health = worst result across all 5 checks (Drift > Warning > Healthy).

Report each check as:

| Check | Result | Details |
| --- | --- | --- |
| File Drift | Healthy / Warning / Drift | N files checked, M issues |
| Post-Completion Mods | Healthy / Warning / Skipped | Notes |
| Task Consistency | Healthy / Warning / Drift | N tasks checked, M issues |
| Staleness | Healthy / Warning / Drift | N days since last activity |
| Cross-Spec Conflicts | Healthy / Warning | N shared files |

**Overall Health**: Healthy / Warning / Drift

Only show the **Findings** section for non-Healthy checks.

### Audit Report

#### Single-Spec Report

```text
# Audit: <spec-name>

**Status**: <status> | **Version**: v<version> | **Updated**: <updated>

## Health Summary

| Check | Result | Details |
|-------|--------|---------|
| File Drift | Healthy | 4 files checked, 0 issues |
| Post-Completion Mods | Healthy | 0 files modified after completion |
| Task Consistency | Warning | Task 3 marked Completed, 1 file missing |
| Staleness | Healthy | 2 days since last activity |
| Cross-Spec Conflicts | Healthy | No shared files |

**Overall Health**: Warning

## Findings

### Task Consistency
- Task 3 ("Add EARS templates"): status Completed but `core/templates/feature.md` does not exist
```

#### All-Specs Report

```text
# SpecOps Audit Report

**Audited**: N specs | **Date**: <current date>

## Summary

| Spec | Status | Health | Issues |
|------|--------|--------|--------|
| auth-feature | implementing | Warning | 1 task inconsistency |
| oauth-refresh | implementing | Drift | 2 missing files, stale (18d) |

**Overall**: 1 Healthy, 1 Warning, 1 Drift
```

---

## Reconcile Mode

Guided interactive repair for drifted specs. Available only on platforms with `canAskInteractive: true`.

### Reconcile Workflow

1. If Use the Bash tool to check if the file exists at(`.specops.json`), Use the Read tool to read(`.specops.json`) to get `specsDir`; otherwise use default `.specops`
2. Parse target spec name from the request. Reconcile requires a target — if no name given, Display a message to the user(`"Reconcile requires a specific spec name. Example: 'reconcile <spec-name>'. Run 'audit' to see all specs."`) and stop.
3. **Platform check**: If `canAskInteractive` is false, Display a message to the user(`"Reconcile mode requires interactive input. Run audit to see findings. Manual fixes can be applied to tasks.md and spec.json directly."`) and stop.
4. Run full audit on the target spec (all 5 checks).
5. If all checks Healthy → Display a message to the user(`"No drift detected in <spec-name>. No reconciliation needed."`) and stop.
6. Present numbered findings list to the user.
7. Prompt the user: "Which findings to fix? Enter 'all', comma-separated numbers (e.g. '1,3'), or 'skip' to exit."
8. For each selected finding, apply the appropriate repair:

| Finding Type | Repair Options |
| --- | --- |
| File missing (renamed) | Update path in tasks.md / Skip |
| File missing (deleted) | Remove reference from tasks.md / Provide new path / Skip |
| Completed task, file missing | Provide new path / Note as discrepancy in tasks.md / Skip |
| Pending task, file already exists | Mark task In Progress / Skip |
| Stale spec | Continue as-is / Skip |
| Cross-spec conflict | Informational only — no repair action |

1. For each repair: Use the Edit tool to modify(`<specsDir>/<name>/tasks.md`) to apply path or status changes.
2. Update `spec.json`: Use the Bash tool to run(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) and Use the Edit tool to modify(`<specsDir>/<name>/spec.json`) to set `updated` to the current timestamp and `specopsUpdatedWith` to the cached SpecOps version (from the Version Extraction Protocol).
3. Regenerate `<specsDir>/index.json` from all `*/spec.json` files.
4. Display a message to the user(`"Reconciliation complete. Applied N fix(es) to <spec-name>."`)

### Platform Adaptation

| Capability | Impact |
| --- | --- |
| `canAccessGit: false` | Checks 2 (post-completion mods) degrade gracefully; Check 1 loses rename detection; Check 4 (staleness) works via `spec.json.updated` timestamp regardless of git access; each skipped check notes the reason in the report |
| `canAskInteractive: false` | Audit works fully (read-only report); Reconcile mode blocked with message |
| `canTrackProgress: false` | Report progress in response text instead of the built-in todo system |


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
    "formatting": { "enabled": true }
  }
}
```

## Spec Directory Structure

Create specs in this structure:

```text
<specsDir>/
  index.json             (auto-generated spec index — rebuilt after every spec.json mutation)
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

1. Scan all subdirectories of `<specsDir>` for `spec.json` files
2. Collect summary fields from each: `id`, `type`, `status`, `version`, `author` (name), `updated`
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

- **Phase 3 step 2**: If `"auto"`, compute a complexity score from pending tasks (effort weights + file count) and activate delegation when score >= 6. If `"always"`, activate regardless. If `"never"`, use sequential execution.

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

### Workflow Impact: integrations

- **Informational only**: Referenced in Phase 2 spec generation (rollout plans, risk mitigations, acceptance criteria). No workflow conditionals — context enrichment only.

## System-Managed Fields

The following `.specops.json` fields are written by installers and must not be prompted for or modified by the agent:

- **`_installedVersion`**: The SpecOps version that was installed. Set by `install.sh` and `remote-install.sh`.
- **`_installedAt`**: ISO 8601 timestamp of when SpecOps was installed.

When modifying `.specops.json` (e.g., during `/specops init`), preserve these fields if they already exist. Do not include them in configuration prompts or templates shown to users.
