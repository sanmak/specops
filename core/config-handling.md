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

```
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

**Shell safety**: `<TaskTitle>` and `<TaskDescription>` contain user-controlled text. Before interpolating into shell commands, write the title and body to temporary files and pass via file-based arguments (e.g., `--body-file`). If file-based arguments are unavailable for the tracker CLI, single-quote the values with internal single-quotes escaped (`'` → `'\''`). Never pass unescaped user text directly in shell command strings.

**GitHub** (`taskTracking: "github"`):
1. WRITE_FILE a temp file with `<TaskDescription>` as content
2. RUN_COMMAND(`gh issue create --title '<taskPrefix><TaskTitle>' --body-file <tempFile>`)
3. Parse the issue URL/number from stdout
4. EDIT_FILE `tasks.md` — set the task's `**IssueID:**` to the returned issue identifier (e.g., `#42`)

**Jira** (`taskTracking: "jira"`):
1. WRITE_FILE a temp file with `<TaskDescription>` as content
2. RUN_COMMAND(`jira issue create --type=Task --summary='<taskPrefix><TaskTitle>' --description-file <tempFile>`)
3. Parse the issue key from stdout (e.g., `PROJ-123`)
4. EDIT_FILE `tasks.md` — set the task's `**IssueID:**` to the returned key

**Linear** (`taskTracking: "linear"`):
1. WRITE_FILE a temp file with `<TaskDescription>` as content
2. RUN_COMMAND(`linear issue create --title '<taskPrefix><TaskTitle>' --description-file <tempFile>`)
3. Parse the issue identifier from stdout
4. EDIT_FILE `tasks.md` — set the task's `**IssueID:**` to the returned identifier

If `config.team.taskPrefix` is set, prepend it to the issue title.

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
- **`requireDocs: true`**: Ensure public APIs have documentation; add JSDoc/docstrings as part of implementation

## Linting & Formatting

If `config.implementation.linting` is configured:
- **`enabled: true`**: Run the project's linter after implementing each task. Fix any violations before marking the task complete.
- **`fixOnSave: true`**: Note in implementation that auto-fix is expected; don't manually fix auto-fixable issues.

If `config.implementation.formatting` is configured:
- **`enabled: true`**: Run the configured formatting tool (`prettier`, `black`, `rustfmt`, `gofmt`) before committing.
- **`tool`**: Use the specified formatter. If not specified, detect from project config files (e.g., `.prettierrc`, `pyproject.toml`).

## Test Framework

If `config.implementation.testFramework` is set (e.g., `jest`, `mocha`, `pytest`, `vitest`):
- Use the specified framework when generating test files
- Use the framework's assertion style and conventions
- Run tests with the appropriate command (e.g., `npx jest`, `pytest`, `npx vitest`)

If not set, detect the test framework from the project's existing test files and `package.json`/`pyproject.toml`.

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

## System-Managed Fields

The following `.specops.json` fields are written by installers and must not be prompted for or modified by the agent:

- **`_installedVersion`**: The SpecOps version that was installed. Set by `install.sh` and `remote-install.sh`.
- **`_installedAt`**: ISO 8601 timestamp of when SpecOps was installed.

When modifying `.specops.json` (e.g., during `/specops init`), preserve these fields if they already exist. Do not include them in configuration prompts or templates shown to users.
