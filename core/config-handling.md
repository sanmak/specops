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
    "delegationThreshold": 4,
    "validateReferences": "warn",
    "gitCheckpointing": false,
    "pipelineMaxCycles": 3,
    "evaluation": {
      "enabled": true,
      "minScore": 7,
      "maxIterations": 2,
      "perTask": false,
      "exerciseTests": true
    }
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

For each eligible task, READ_FILE `<specsDir>/<spec-name>/requirements.md` (or `bugfix.md`/`refactor.md`), READ_FILE `<specsDir>/<spec-name>/spec.json`, and extract:

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

RUN_COMMAND(`gh label create "<label>" --force --description "<description>"`)

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
2. WRITE_FILE a temp file with `<IssueBody>` as content
3. RUN_COMMAND(`gh issue create --title '<EscapedTaskTitle>' --body-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue URL/number from stdout
5. EDIT_FILE `tasks.md` — set the task's `**IssueID:**` to the returned issue identifier (e.g., `#42`)

**Jira** (`taskTracking: "jira"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. WRITE_FILE a temp file with `<IssueBody>` as content
3. RUN_COMMAND(`jira issue create --type=Task --summary='<EscapedTaskTitle>' --description-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue key from stdout (e.g., `PROJ-123`)
5. EDIT_FILE `tasks.md` — set the task's `**IssueID:**` to the returned key

**Linear** (`taskTracking: "linear"`):

1. Compose `<IssueBody>` following the Issue Body Composition template above
2. WRITE_FILE a temp file with `<IssueBody>` as content
3. RUN_COMMAND(`linear issue create --title '<EscapedTaskTitle>' --description-file <tempFile> --label '<priorityLabel>' --label 'spec:<spec-id>' --label '<typeLabel>'`)
4. Parse the issue identifier from stdout
5. EDIT_FILE `tasks.md` — set the task's `**IssueID:**` to the returned identifier

### Graceful Degradation

If the CLI tool is not installed or the command fails:

1. NOTIFY_USER("Warning: Could not create external issue for Task <N> — <error>. Continuing without external tracking for this task.")
2. EDIT_FILE `tasks.md` — set `**IssueID:**` to `FAILED — <reason>` on the affected task
3. Do NOT block implementation — proceed with the internal state machine

### Status Sync

When task status changes in `tasks.md` (as part of the Task State Machine):

- **Pending → In Progress**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, update the external issue:
  - GitHub: RUN_COMMAND(`gh issue edit <number> --add-label "in-progress"`)
  - Jira: RUN_COMMAND(`jira issue move <key> "In Progress"`)
  - Linear: RUN_COMMAND(`linear issue update <id> --status "In Progress"`)
- **In Progress → Completed**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, close the external issue:
  - GitHub: RUN_COMMAND(`gh issue close <number>`)
  - Jira: RUN_COMMAND(`jira issue move <key> "Done"`)
  - Linear: RUN_COMMAND(`linear issue update <id> --status "Done"`)
- **In Progress → Blocked**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, update the external issue to blocked state:
  - GitHub: RUN_COMMAND(`gh issue edit <number> --add-label "blocked"`)
  - Jira: RUN_COMMAND(`jira issue move <key> "Blocked"`)
  - Linear: RUN_COMMAND(`linear issue update <id> --status "Blocked"`)
- **Blocked → In Progress**: If IssueID exists and is neither `None` nor prefixed with `FAILED`, move the external issue back to in-progress:
  - GitHub: RUN_COMMAND(`gh issue edit <number> --remove-label "blocked" --add-label "in-progress"`)
  - Jira: RUN_COMMAND(`jira issue move <key> "In Progress"`)
  - Linear: RUN_COMMAND(`linear issue update <id> --status "In Progress"`)

Status Sync failures are warned (NOTIFY_USER), not blocking.

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

1. READ_FILE `tasks.md` — identify all tasks with `**Priority:** High` or `**Priority:** Medium`
2. For each eligible task, require `**IssueID:**` to be either:
   - a valid tracker identifier for the configured platform (e.g., `#42`, `PROJ-123`), or
   - `FAILED — <reason>` produced by Graceful Degradation after an attempted creation
   Values like `TBD`, `N/A`, or other placeholders do not satisfy the gate.
3. If any are missing: attempt issue creation for the missing tasks using the Issue Creation Protocol above
4. If issue creation succeeds for some tasks but fails for others (CLI tool error, network failure): NOTIFY_USER("Partial external tracking — <N>/<M> task(s) created, <F> failed") and proceed. The Graceful Degradation rules apply to individual failures.
5. If issue creation fails for ALL eligible tasks: NOTIFY_USER("External tracking unavailable — all <N> issue creation attempts failed. Proceeding with internal task tracking only.") and proceed.
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

### Workflow Impact: Task delegation (auto) / delegationThreshold

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
