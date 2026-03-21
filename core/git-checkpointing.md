## Git Checkpointing

Git checkpointing commits at three semantic phase boundaries during spec execution: after spec creation (Phase 2), after implementation (Phase 3), and after completion (Phase 4). This complements the per-task `autoCommit` setting (which commits within Phase 3 step 7) with higher-level semantic milestones that enable clean rollback to meaningful workflow states. Both settings can be enabled simultaneously without conflict.

### Checkpoint Configuration

Controlled by `config.implementation.gitCheckpointing` (boolean, default `false`). Checkpointing only fires when:

1. `config.implementation.gitCheckpointing` is `true`
2. The platform has `canAccessGit: true`
3. The working tree was clean at workflow start (see Dirty Tree Safety)

If any condition is false, checkpointing is silently disabled for the entire run.

### Checkpoint Procedure

Three checkpoint points with fixed commit message formats:

**Checkpoint 1 — After Phase 2 step 6 (spec artifacts created):**

- RUN_COMMAND(`git add <specsDir>/<spec-name>/`)
- RUN_COMMAND(`git commit -m "specops(checkpoint): spec-created -- <spec-name>"`)
- Commits only the spec directory (requirements.md, design.md, tasks.md, implementation.md, spec.json)

**Checkpoint 2 — After Phase 3 tasks complete (before Phase 4):**

- RUN_COMMAND(`git add -A`)
- RUN_COMMAND(`git commit -m "specops(checkpoint): implemented -- <spec-name>"`)
- Commits all implementation changes

**Checkpoint 3 — After Phase 4 step 6 (status set to completed):**

- RUN_COMMAND(`git add -A`)
- RUN_COMMAND(`git commit -m "specops(checkpoint): completed -- <spec-name>"`)
- Commits final metadata updates (spec.json status, metrics, memory, index.json)

If any checkpoint commit fails (e.g., nothing to commit because autoCommit captured everything, or a pre-commit hook fails), NOTIFY_USER with the failure reason and continue. Checkpoint failures are never blocking.

### Dirty Tree Safety

At Phase 1, after loading configuration (step 1), if `gitCheckpointing` is enabled:

1. RUN_COMMAND(`git status --porcelain`)
2. If the output is non-empty (uncommitted changes exist): NOTIFY_USER("Working tree has uncommitted changes. Git checkpointing disabled for this run to avoid mixing unrelated changes into checkpoint commits. Commit or stash your changes first to enable checkpointing.") and set `gitCheckpointing` to `false` for this run.
3. If `git status` fails (not a git repository, git not installed): set `gitCheckpointing` to `false` silently.

This check prevents SpecOps from committing the user's unrelated work-in-progress alongside spec artifacts.

### Checkpoint Commit Messages

All checkpoint commits use the fixed prefix `specops(checkpoint):` followed by the phase and spec name:

- `specops(checkpoint): spec-created -- <spec-name>`
- `specops(checkpoint): implemented -- <spec-name>`
- `specops(checkpoint): completed -- <spec-name>`

This format is not configurable. The `specops(checkpoint):` prefix distinguishes these commits from:

- User commits (no prefix or conventional commit prefixes)
- `autoCommit` commits (which use conventional commit prefixes like `feat:`, `fix:`)

### Interaction with autoCommit

`autoCommit` and `gitCheckpointing` are non-conflicting settings that operate at different granularities:

| Setting | When it fires | Granularity | Purpose |
| --- | --- | --- | --- |
| `autoCommit` | Phase 3 step 7 (after each task) | Per-task | Capture implementation progress |
| `gitCheckpointing` | Phase 2/3/4 boundaries | Per-phase | Capture semantic milestones |

When both are enabled:

- Phase 2 checkpoint commits spec artifacts (autoCommit hasn't fired yet — it's Phase 3 only)
- Phase 3: autoCommit commits after each task, then the Phase 3 checkpoint runs `git add -A && git commit`. If autoCommit already committed everything, the checkpoint commit will have nothing to commit — it is skipped silently (this is expected, not an error).
- Phase 4 checkpoint commits final metadata updates

No special interaction logic is needed — they compose naturally.

### Git Checkpointing Safety

- **Never force push**: Checkpoint commits are local commits only. They are never pushed to a remote.
- **Never amend**: Each checkpoint is a new commit. Never `git commit --amend`.
- **Respect hooks**: If pre-commit or pre-push hooks are configured, checkpointing respects them. If a hook fails, the checkpoint is skipped with a warning — checkpointing does not bypass hooks (`--no-verify` is never used).
- **No push**: Checkpointing does not push to remote. Pushing is handled by Phase 4 step 7 (`createPR`) or the user's explicit push command.
- **Non-blocking**: If any git command fails (conflict, hook failure, permissions), NOTIFY_USER and continue the workflow. Checkpoint failures never block spec completion.

### Platform Adaptation

| Capability | Impact |
| --- | --- |
| `canAccessGit: true` (all 4 platforms) | Checkpointing available on all platforms |
| `canAccessGit: false` | Skip checkpointing silently |
| `canExecuteCode: true` (all 4 platforms) | RUN_COMMAND available for git commands |

No platform-specific fallbacks are needed — the checkpointing procedure is identical across all platforms.
