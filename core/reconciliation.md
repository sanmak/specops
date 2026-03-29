## Audit Mode

SpecOps `audit` detects drift between spec artifacts and the live codebase. It runs 7 checks and produces a health report. `reconcile` guides interactive repair of findings.

### Mode Detection

When the user invokes SpecOps, check for audit or reconcile intent after the steering command check and before the interview check:

- **Audit mode**: request matches `audit`, `audit <name>`, `health check`, `check drift`, `spec health`. These must refer to SpecOps spec health, NOT a product feature like "audit log" or "health endpoint". If detected, follow the Audit Workflow below.
- **Reconcile mode**: request matches `reconcile <name>`, `fix <name>` (when referring to a spec, not code), `repair <name>`, `sync <name>`. If detected, follow the Reconcile Workflow below.

If neither pattern matches, continue to interview check and the standard phases.

### Audit Workflow

1. If FILE_EXISTS(`.specops.json`), READ_FILE(`.specops.json`) to get `specsDir`; otherwise use default `.specops`
2. Parse target spec name from the request if present.
   - If a name is given, audit that spec (any status, including completed — Post-Completion Modification runs for completed specs only when audited by name).
   - If no name is given, LIST_DIR(`<specsDir>`) to enumerate candidate directories, keep only entries where FILE_EXISTS(`<specsDir>/<dir>/spec.json`) is true (skipping non-spec folders like `steering/`), load each retained `spec.json`, then audit all specs whose `status` is not `completed` (completed specs are frozen; use `/specops audit <name>` to explicitly audit a completed spec).
3. For each target spec:
   a. If FILE_EXISTS(`<specsDir>/<name>/spec.json`), READ_FILE(`<specsDir>/<name>/spec.json`) to load metadata. If not found, NOTIFY_USER(`"Spec '<name>' not found in <specsDir>. Run '/specops list' to see available specs."`) and stop.
   b. If FILE_EXISTS(`<specsDir>/<name>/tasks.md`), READ_FILE(`<specsDir>/<name>/tasks.md`) to load tasks.
   c. Run the 7 drift checks below. Record each result as `Healthy`, `Warning`, or `Drift`.
   d. Overall health = worst result across all checks.
4. Present the Audit Report (format below).

### Seven Drift Checks

### File Drift

Verify all "Files to Modify" paths in `tasks.md` still exist.

- Parse all file paths listed under `**Files to Modify:**` sections across all tasks
- For each path, check FILE_EXISTS(`<path>`)
- If FILE_EXISTS returns false AND `canAccessGit` is true: RUN_COMMAND(`git log --diff-filter=R --summary --oneline -- "<path>"`) to detect renames; RUN_COMMAND(`git log --diff-filter=D --oneline -- "<path>"`) to detect deletions
  - Renamed file → **Warning** (note new path if found)
  - Deleted file → **Drift**
  - No git available → **Warning** (cannot confirm deletion vs rename)
- If no "Files to Modify" entries found → skip check, note "No file paths to check" in report
- If wildcard/glob paths found → skip those paths, note in report

### Post-Completion Modification

For completed specs, detect files modified after `spec.json.updated` timestamp.

- Only runs when `spec.json.status == "completed"`
- Requires `canAccessGit: true`; if false → skip with note "git unavailable, skipped"
- For each file path from "Files to Modify": RUN_COMMAND(`git log --after="<spec.json.updated>" --oneline -- "<path>"`)
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

- Parse `spec.json.updated` and compute age using RUN_COMMAND(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) for current time
- Rules by status:
  - `implementing`: > 14 days inactive → **Drift**; > 7 days → **Warning**
  - `draft` or `in-review`: > 30 days → **Warning**
  - `completed`: always **Healthy** (completed specs don't go stale)
- If `spec.json.updated` is missing (malformed or legacy spec) → **Warning** (cannot determine age)

### Cross-Spec Conflicts

Detect multiple active (non-completed) specs referencing the same files.

- LIST_DIR(`<specsDir>`) to find candidate directories; keep only those where FILE_EXISTS(`<specsDir>/<dir>/spec.json`) is true; READ_FILE each `<specsDir>/<dir>/spec.json` to load metadata
- For each spec with `status ≠ completed` (active specs only): READ_FILE(`<specsDir>/<dir>/tasks.md`) if it exists, collect all "Files to Modify" paths
- Build a map: `file_path → [distinct spec names]` (deduplicate spec names per file — a single spec referencing the same file in multiple tasks counts as one)
- Any file with 2+ distinct specs → **Warning** (no repair available — informational only)
- For single-spec audit: still load all active specs to detect conflicts involving the target

### Dependency Health

Validate cross-spec dependency integrity.

- **Invalid references**: For each spec with a `specDependencies` array in its spec.json, verify that each `specId` references a spec that actually exists in `<specsDir>`. READ_FILE(`<specsDir>/index.json`) to get the full list of spec IDs. For each `specId` in `specDependencies`, check that it appears in the index. Missing spec reference → **Warning** with details of which dependency points to a non-existent spec.

- **Cycle detection**: Run cycle detection across all specs using DFS with white/gray/black coloring (see `core/decomposition.md` section 5). Build the adjacency list from all specs' `specDependencies` arrays. If a cycle is detected → **Drift** with the cycle chain (e.g., "spec-a → spec-b → spec-c → spec-a"). If no cycles → continue.

- **Unmet required dependencies on implementing specs**: For each spec with `status == "implementing"`, check its `specDependencies` for entries with `required: true`. For each required dependency, READ_FILE the dependency's spec.json and verify `status == "completed"`. If any required dependency is not completed → **Warning** ("Spec '{spec-id}' is implementing but required dependency '{dep-id}' has status '{status}'"). This flags specs that may have bypassed the dependency gate.

- If no issues found across all three sub-checks → **Healthy**

### Dependency Drift

Detect packages installed in the project that were not approved in any spec's dependency decisions.

1. **Detect ecosystems**: Use the Dependency Detection Protocol from `core/dependency-safety.md` to identify which ecosystems are present (scan for indicator files: `package-lock.json`, `requirements.txt`, `Cargo.lock`, etc.).

2. **Collect installed packages**: For each detected ecosystem, READ_FILE the lock file and extract the list of installed package names:
   - Node.js: READ_FILE(`package-lock.json`) or READ_FILE(`yarn.lock`) -- extract package names from the `dependencies` or `packages` sections
   - Python: READ_FILE(`requirements.txt`) -- extract package names (one per line, strip version specifiers)
   - Rust: READ_FILE(`Cargo.lock`) -- extract `name` fields from `[[package]]` sections
   - Ruby: READ_FILE(`Gemfile.lock`) -- extract package names from the `GEM > specs` section
   - Go: READ_FILE(`go.sum`) -- extract module paths
   - PHP: READ_FILE(`composer.lock`) -- extract `name` fields from `packages` array
   - Java/Kotlin: READ_FILE(`pom.xml`) or READ_FILE(`build.gradle`) -- extract dependency names

3. **Collect approved dependencies**: READ_FILE(`<specsDir>/index.json`) to enumerate all specs. For each spec with `status` in (`"completed"`, `"in-progress"`, `"in-review"`), READ_FILE(`<specsDir>/<spec-name>/design.md`) and extract packages from the `### Dependency Decisions` table where `Decision` is `Approved`. Build a union set of all approved packages across all matching specs. Including in-progress and in-review specs prevents false warnings for dependencies that were approved in a spec's design but whose spec is not yet completed.

4. **Compare**: For each installed package, check if it appears in the approved union set. If a package is installed but not in any spec's approved list → **Warning** (not Drift, since it may be a pre-existing dependency that predates SpecOps adoption or was added to the project before dependency introduction tracking began).

5. If no unapproved packages found → **Healthy**

### Health Summary

Overall health = worst result across all 7 checks (Drift > Warning > Healthy).

Report each check as:

| Check | Result | Details |
| --- | --- | --- |
| File Drift | Healthy / Warning / Drift | N files checked, M issues |
| Post-Completion Mods | Healthy / Warning / Skipped | Notes |
| Task Consistency | Healthy / Warning / Drift | N tasks checked, M issues |
| Staleness | Healthy / Warning / Drift | N days since last activity |
| Cross-Spec Conflicts | Healthy / Warning | N shared files |
| Dependency Health | Healthy / Warning / Drift | N dependency issues |
| Dependency Drift | Healthy / Warning | N unapproved packages |

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
| Dependency Health | Healthy | 0 dependency issues |
| Dependency Drift | Healthy | 0 unapproved packages |

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

1. If FILE_EXISTS(`.specops.json`), READ_FILE(`.specops.json`) to get `specsDir`; otherwise use default `.specops`
2. Parse target spec name from the request. Reconcile requires a target — if no name given, NOTIFY_USER(`"Reconcile requires a specific spec name. Example: 'reconcile <spec-name>'. Run 'audit' to see all specs."`) and stop.
3. **Platform check**: If `canAskInteractive` is false, NOTIFY_USER(`"Reconcile mode requires interactive input. Run audit to see findings. Manual fixes can be applied to tasks.md and spec.json directly."`) and stop.
4. Run full audit on the target spec (all 7 checks).
5. If all checks Healthy → NOTIFY_USER(`"No drift detected in <spec-name>. No reconciliation needed."`) and stop.
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

1. For each repair: EDIT_FILE(`<specsDir>/<name>/tasks.md`) to apply path or status changes.
2. Update `spec.json`: RUN_COMMAND(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) and EDIT_FILE(`<specsDir>/<name>/spec.json`) to set `updated` to the current timestamp and `specopsUpdatedWith` to the cached SpecOps version (from the Version Extraction Protocol).
3. Regenerate `<specsDir>/index.json` from all `*/spec.json` files.
4. NOTIFY_USER(`"Reconciliation complete. Applied N fix(es) to <spec-name>."`)

### Platform Adaptation

| Capability | Impact |
| --- | --- |
| `canAccessGit: false` | Checks 2 (post-completion mods) degrade gracefully; Check 1 loses rename detection; Check 4 (staleness) works via `spec.json.updated` timestamp regardless of git access; each skipped check notes the reason in the report |
| `canAskInteractive: false` | Audit works fully (read-only report); Reconcile mode blocked with message |
| `canTrackProgress: false` | Report progress in response text instead of the built-in todo system |

### Reconciliation-Based Learning Extraction

When reconciliation mode is invoked with `--learnings` (e.g., `/specops reconcile --learnings`), scan recent git history for hotfix patterns and propose production learnings. This extends the standard reconciliation with a learning discovery pass.

1. If `canAccessGit` is false, NOTIFY_USER("Git access required for reconciliation-based learning extraction.") and stop.
2. RUN_COMMAND(`git log --oneline --since="30 days ago" -- .`) to get recent commits.
3. Filter for commits matching hotfix patterns: commit messages containing `fix:`, `hotfix:`, `patch:`, `revert:`, or `incident`.
4. For each matching commit, RUN_COMMAND(`git show --stat <hash>`) to get affected files.
5. Cross-reference affected files against completed specs: READ_FILE(`<specsDir>/index.json`), then for each completed spec READ_FILE its `tasks.md` and collect "Files to Modify" paths. Match commit files against spec file sets.
6. For each match, propose a learning: "Commit `<hash>` (`<message>`) touches files from spec '<specId>'. Capture as learning?"
7. If `canAskInteractive`: for each proposed learning, ASK_USER for category, severity, and prevention rule. Capture following the Production Learnings module Learn Subcommand (step 4 onwards).
8. If not interactive: display the list of proposed learnings and NOTIFY_USER("Reconciliation found {N} potential learnings. Run `/specops learn <spec-name>` to capture each.") and stop.
9. After all captures, run learning pattern detection following the Production Learnings module.
10. NOTIFY_USER("Reconciliation complete. Captured {N} learnings from {M} hotfix commits.")
