## Audit Mode

SpecOps `audit` detects drift between spec artifacts and the live codebase. It runs 6 checks and produces a health report. `reconcile` guides interactive repair of findings.

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
   c. Run the 6 drift checks below. Record each result as `Healthy`, `Warning`, or `Drift`.
   d. Overall health = worst result across all checks.
4. Present the Audit Report (format below).

### Six Drift Checks

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

### Dependency Health

Validate cross-spec dependency integrity.

- **Invalid references**: For each spec with a `specDependencies` array in its spec.json, verify that each `specId` references a spec that actually exists in `<specsDir>`. Use the Read tool to read(`<specsDir>/index.json`) to get the full list of spec IDs. For each `specId` in `specDependencies`, check that it appears in the index. Missing spec reference → **Warning** with details of which dependency points to a non-existent spec.

- **Cycle detection**: Run cycle detection across all specs using DFS with white/gray/black coloring (see `core/decomposition.md` section 5). Build the adjacency list from all specs' `specDependencies` arrays. If a cycle is detected → **Drift** with the cycle chain (e.g., "spec-a → spec-b → spec-c → spec-a"). If no cycles → continue.

- **Unmet required dependencies on implementing specs**: For each spec with `status == "implementing"`, check its `specDependencies` for entries with `required: true`. For each required dependency, Use the Read tool to read the dependency's spec.json and verify `status == "completed"`. If any required dependency is not completed → **Warning** ("Spec '{spec-id}' is implementing but required dependency '{dep-id}' has status '{status}'"). This flags specs that may have bypassed the dependency gate.

- If no issues found across all three sub-checks → **Healthy**

### Health Summary

Overall health = worst result across all 6 checks (Drift > Warning > Healthy).

Report each check as:

| Check | Result | Details |
| --- | --- | --- |
| File Drift | Healthy / Warning / Drift | N files checked, M issues |
| Post-Completion Mods | Healthy / Warning / Skipped | Notes |
| Task Consistency | Healthy / Warning / Drift | N tasks checked, M issues |
| Staleness | Healthy / Warning / Drift | N days since last activity |
| Cross-Spec Conflicts | Healthy / Warning | N shared files |
| Dependency Health | Healthy / Warning / Drift | N dependency issues |

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
4. Run full audit on the target spec (all 6 checks).
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
      "requireTests": true
    }
  },
  "implementation": {
    "autoCommit": false,
    "createPR": false,
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
3. Use the Bash tool to run(`gh issue create --title '<EscapedTaskTitle>' --body-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue URL/number from stdout
5. Use the Edit tool to modify `tasks.md` — set the task's `**IssueID:**` to the returned issue identifier (e.g., `#42`)

**Jira** (`taskTracking: "jira"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. Use the Write tool to create a temp file with `<IssueBody>` as content
3. Use the Bash tool to run(`jira issue create --type=Task --summary='<EscapedTaskTitle>' --description-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue key from stdout (e.g., `PROJ-123`)
5. Use the Edit tool to modify `tasks.md` — set the task's `**IssueID:**` to the returned key

**Linear** (`taskTracking: "linear"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. Use the Write tool to create a temp file with `<IssueBody>` as content
3. Use the Bash tool to run(`linear issue create --title '<EscapedTaskTitle>' --description-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue identifier from stdout
5. Use the Edit tool to modify `tasks.md` — set the task's `**IssueID:**` to the returned identifier

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

### Workflow Impact: codeReview

- **Phase 3 step 6**: If `requireTests`, run tests for every task; block completion on insufficient coverage.
- **Phase 4 step 7**: If `required`, include review requirement and `minApprovals` count in PR description.

## Linting & Formatting

Run the project's linter after implementing each task. Fix any violations before marking the task complete. Run the project's formatting tool before committing. Detect the linter and formatter from project config files (e.g., `.eslintrc`, `.prettierrc`, `pyproject.toml`, `setup.cfg`).

### Workflow Impact: linting / formatting

- **Phase 3 step 6**: Run linter after each task and fix violations before marking complete.
- **Phase 3 step 7**: Run formatter before committing.

## Testing

Run tests automatically after implementing each task. Detect the test framework from the project's existing test files and dependency manifests (`package.json`, `pyproject.toml`, etc.). Use the detected framework's assertion style, conventions, and runner command.

### Workflow Impact: testing

- **Phase 3 step 6**: Run tests automatically after each task.

### Workflow Impact: autoCommit / createPR

- **Phase 3 step 7**: If `autoCommit`, commit changes after each task. If false, suggest commit format.
- **Phase 4 step 7**: If `createPR`, create a pull request after implementation completes.

### Workflow Impact: taskDelegation / delegationThreshold

- **Phase 3 step 2**: Compute a complexity score from pending tasks (effort weights + file count) and activate delegation when score >= `config.implementation.delegationThreshold` (integer, default 4). Lower values activate delegation more aggressively. The score formula is: `sum(effort_weights) + floor(distinct_files / 5)` where effort weights are S=1, M=2, L=3. Examples at threshold 4: 4 small tasks (score 4), 2 medium tasks (score 4), 1 large + 1 small task (score 4).

## Module-Specific Configuration

If `config.modules` is configured (for monorepo/multi-module projects):

- Each module can define its own `specsDir` and `conventions`
- Module conventions **merge with** root `team.conventions` (module-specific conventions take priority on conflicts)
- Create specs in the module-specific specsDir: `<module.specsDir>/<spec-name>/`
- When a request targets a specific module, apply that module's conventions
- If no module is specified and the request is ambiguous, ask which module to target

### Workflow Impact: dependencySafety

- **Phase 1 step 3**: If `dependencies.md` steering file exists and `_generatedAt` is over 30 days old, notify the user about stale dependency data.
- **Phase 2 step 6.7 (mandatory gate)**: If `enabled` is not `false`, execute the dependency safety verification. Block implementation when findings exceed `severityThreshold`. Skipping this gate when enabled is a protocol breach.
- **Phase 2 step 6.7**: If `autoFix` is `true`, attempt automatic remediation before re-evaluating.
- **Phase 2 step 6.7**: Filter `allowedAdvisories` CVE IDs from blocking decisions (still recorded in audit artifact).
- **Phase 2 step 6.7**: `scanScope` controls whether to audit only spec-relevant ecosystems (`"spec"`) or all detected ecosystems (`"project"`).

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
