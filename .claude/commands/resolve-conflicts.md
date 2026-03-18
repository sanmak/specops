Resolve merge conflicts on a GitHub PR by merging the base branch into the PR branch in an isolated git worktree, with JSON/markdown-aware conflict resolution.

## Instructions

Follow these steps precisely. Do NOT add a Co-Authored-By line to commits.

### Argument Parsing

Parse `$ARGUMENTS` for a PR number (e.g., `56`).

If empty, try auto-detection: `gh pr view --json number -q .number 2>/dev/null`. If auto-detection fails, ask the user "Which PR number should I resolve conflicts for?" and wait for their response.

---

### Step 1: Pre-flight checks

1. **GitHub CLI available**: Run `gh --version`. If unavailable, tell the user "GitHub CLI (gh) is required. Install with: brew install gh" and stop.
2. **PR exists, is open, and is conflicting**: Run `gh pr view <PR_NUMBER> --json number,state,headRefName,baseRefName,title,mergeable`. If the PR does not exist or is not open, report the error and stop. If `mergeable` is `UNKNOWN`, retry up to 5 times with 3-second waits — GitHub may still be computing the merge state. If `mergeable` remains `UNKNOWN` after retries, report "PR #<N> mergeability is UNKNOWN after retries — try again shortly" and stop. If `mergeable` is not `CONFLICTING` (i.e., `MERGEABLE`), report "PR #<N> has no merge conflicts (mergeable: <status>)" and stop. Save `headRefName` as `PR_BRANCH`, `baseRefName` as `BASE_BRANCH`, `title` as `PR_TITLE`.
3. **Extract owner/repo**: Run `gh repo view --json owner,name -q '.owner.login + "/" + .name'`. Save as `OWNER_REPO`.
4. **Working tree is clean**: Run `git status --porcelain`. If there are uncommitted changes, tell the user "Working tree has uncommitted changes. Please commit or stash them first." and stop.
5. **Clean stale worktree**: Run `git worktree list`. If an entry exists with path `.claude/worktrees/resolve-conflicts-<PR_NUMBER>`, remove it with `git worktree remove --force <path>`. Only remove the worktree matching the current PR number — do NOT remove other worktrees, as they may belong to concurrent runs.

### Step 2: Identify conflicts

1. Fetch both branches: `git fetch origin <PR_BRANCH> <BASE_BRANCH>`.
2. Run `git merge-tree --write-tree origin/<PR_BRANCH> origin/<BASE_BRANCH>` to preview conflicts without modifying any working tree.
3. Parse the output to extract:
   - List of auto-merged files
   - List of conflicting files (lines containing `CONFLICT`)
4. If no conflicts are found, report "No conflicts detected between `<BASE_BRANCH>` and `<PR_BRANCH>`" and stop.

Display a conflict summary:

```
PR #<N>: <title>
Merge: <BASE_BRANCH> → <PR_BRANCH>

Conflicting files (<K>):
  1. <path1>
  2. <path2>

Auto-merged files: <path>, <path>, ...

Proceeding to resolve conflicts in an isolated worktree.
```

### Step 3: Create worktree

1. Fetch the latest remote state: `git fetch origin <PR_BRANCH>`.
2. Create an isolated worktree attached to a local branch tracking the PR head:
   ```
   git worktree add -b <PR_BRANCH> .claude/worktrees/resolve-conflicts-<PR_NUMBER> origin/<PR_BRANCH>
   ```
   If the local branch already exists, use `git worktree add .claude/worktrees/resolve-conflicts-<PR_NUMBER> <PR_BRANCH>` instead, then sync to the remote HEAD: `git -C .claude/worktrees/resolve-conflicts-<PR_NUMBER> reset --hard origin/<PR_BRANCH>`.
3. If worktree creation fails (e.g., branch already checked out), report the error and stop.

Save `.claude/worktrees/resolve-conflicts-<PR_NUMBER>` as `WORKTREE_DIR`.

### Step 4: Merge base branch into PR branch

Run:
```
git -C <WORKTREE_DIR> merge origin/<BASE_BRANCH> --no-commit
```

The `--no-commit` flag leaves the merge in progress so conflicts can be resolved before committing. If the merge unexpectedly succeeds cleanly (no conflicts), do NOT commit yet — skip to Step 6 to run regeneration and validation, then proceed to Step 7 normally.

### Step 5: Resolve each conflicting file

For each conflicting file, determine the resolution strategy based on file type and conflict nature.

#### Step 5a: Classify files

Classify each conflicting file:

- **Generated files**: `platforms/claude/SKILL.md`, `platforms/cursor/specops.mdc`, `platforms/codex/SKILL.md`, `platforms/copilot/specops.instructions.md`, `skills/specops/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
  Resolution: Accept the base branch version (`git -C <WORKTREE_DIR> checkout --theirs <path>`) — these will be fully regenerated in Step 6.
  Note: If generated files conflict but no source files (`core/`, `generator/templates/`, `platforms/*/platform.json`) appear in the merge diff, Step 6 will not trigger regeneration. In this case the base-branch version is accepted as-is. This scenario only arises if a generated file was directly edited (a convention violation per CLAUDE.md).

- **Checksummed artifact**: `CHECKSUMS.sha256`
  Resolution: Accept the base branch version (`git -C <WORKTREE_DIR> checkout --theirs <path>`) — this will be regenerated in Step 6.

- **JSON files** (`.json`): Use JSON-aware merge (Step 5b).

- **Markdown files** (`.md`): Use markdown-aware merge (Step 5c).

- **Other files**: Use content analysis (Step 5d).

Stage generated and checksummed files immediately: `git -C <WORKTREE_DIR> add <path>`.

#### Step 5b: JSON conflict resolution

Read all three versions of the conflicting file:
- Base (merge base): `git -C <WORKTREE_DIR> show :1:<path>`
- Ours (PR branch): `git -C <WORKTREE_DIR> show :2:<path>`
- Theirs (base branch / main): `git -C <WORKTREE_DIR> show :3:<path>`

Parse all three as JSON. For each key:

1. **Array fields** (e.g., `decisions`, `decisionCategories`, `fileOverlaps`, entries in `index.json`):
   - If the base array is a prefix of both the ours and theirs arrays (both sides appended new entries): concatenate. Take the base entries, then the PR-branch additions (ours / :2:), then the base-branch additions (theirs / :3:).
   - If both sides modified existing entries at the same position: present to user.

2. **Object fields with updated scalar values**: If both sides modified the same key to different values, present to user:
   ```
   Conflict in <path> at key "<key>":
     Base:   <base value>
     Main:   <main value>
     PR:     <pr value>
   Which value should be used? (main/pr/custom)
   ```

3. **Object fields where only one side changed**: Take the changed side.

4. **Nested objects with `count` + `specs` pattern** (e.g., patterns.json fileOverlaps):
   - `specs` array: Union (combine both, deduplicate)
   - `count`: Set to the length of the merged `specs` array (do NOT use max, as the union may exceed either side's count)

After resolution, write the merged JSON (pretty-printed with 2-space indent) and stage it:
`git -C <WORKTREE_DIR> add <path>`.

Report:
```
Resolved <path>:
  Strategy: JSON array merge
  Result: <brief description, e.g., "9 decisions (7 base + 1 from main + 1 from PR)">
```

#### Step 5c: Markdown conflict resolution

Read all three versions (same stage extraction as 5b).

Diff base vs ours and base vs theirs to identify what each side added/changed.

1. **Additive sections at end of file**: If both sides appended new sections to the end (the most common case — e.g., new spec summaries in context.md), include both. PR-branch additions first (ours / :2:), then base-branch additions (theirs / :3:).

2. **Non-overlapping edits**: If edits are in completely different regions of the file, combine both changes (take ours version as base, apply theirs additions).

3. **Overlapping edits**: If both sides modified the same lines, present to user:
   ```
   Conflict in <path> at lines <N-M>:

   === PR version (ours) ===
   <pr text>

   === Main version (theirs) ===
   <main text>

   Which version? (pr/main/both/custom)
   ```

After resolution, write the merged content and stage it.

Report:
```
Resolved <path>:
  Strategy: additive markdown sections
  Result: <brief description, e.g., "8 spec summaries (6 base + 1 from main + 1 from PR)">
```

#### Step 5d: Other file conflict resolution (fallback)

For any file that is not JSON, markdown, generated, or checksummed:
1. Read all three versions
2. Try to detect if the conflict is purely additive (both sides added content at the same location)
3. If additive, include both additions (PR branch first, then base branch)
4. If truly conflicting (overlapping edits to existing content), present the conflict to the user with full context and ask for resolution
5. Write the resolved content and stage it

### Step 6: Regenerate and validate

Check the list of all files affected by the merge (both auto-merged and conflict-resolved) using `git -C <WORKTREE_DIR> diff --cached --name-only`.

**If any files under `core/`, `generator/templates/`, `generator/generate.py`, or `platforms/*/platform.json` are present:**
- Run `python3 generator/generate.py --all` from `WORKTREE_DIR`
- Stage regenerated files: `git -C <WORKTREE_DIR> add platforms/ skills/ .claude-plugin/`

**If any checksummed files were affected** (`skills/specops/SKILL.md`, `schema.json`, `platforms/claude/SKILL.md`, `platforms/claude/platform.json`, `platforms/cursor/specops.mdc`, `platforms/cursor/platform.json`, `platforms/codex/SKILL.md`, `platforms/codex/platform.json`, `platforms/copilot/specops.instructions.md`, `platforms/copilot/platform.json`, `core/workflow.md`, `core/safety.md`, `core/reconciliation.md`, `hooks/pre-commit`, `hooks/pre-push`, `scripts/install-hooks.sh`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`):
- Regenerate checksums from `WORKTREE_DIR`:
  ```
  cd <WORKTREE_DIR> && shasum -a 256 skills/specops/SKILL.md schema.json platforms/claude/SKILL.md platforms/claude/platform.json platforms/cursor/specops.mdc platforms/cursor/platform.json platforms/codex/SKILL.md platforms/codex/platform.json platforms/copilot/specops.instructions.md platforms/copilot/platform.json core/workflow.md core/safety.md core/reconciliation.md hooks/pre-commit hooks/pre-push scripts/install-hooks.sh .claude-plugin/plugin.json .claude-plugin/marketplace.json > CHECKSUMS.sha256
  ```
- Stage: `git -C <WORKTREE_DIR> add CHECKSUMS.sha256`

Run validation from `WORKTREE_DIR`:
1. `python3 generator/validate.py`
2. `shasum -a 256 -c CHECKSUMS.sha256`
3. `bash scripts/run-tests.sh`

If any validation fails, attempt to fix (up to 2 retries). If still failing, report the errors and stop — do NOT push broken code.

### Step 7: Commit and push

1. Stage all remaining files: `git -C <WORKTREE_DIR> add -A`
1b. **Check for staged changes**: Run `git -C <WORKTREE_DIR> diff --cached --name-only`. If empty (no changes staged), the merge produced no net diff — skip to Step 8 (cleanup) and report "Merge resolved to no-op — no changes to commit" in Step 9.
2. Un-stage sensitive files if any are present:
   - `.env`, `.env.*`
   - `credentials.json`, `secrets.json`, `*.pem`, `*.key`
   - Any file with "secret", "credential", or "token" in its name
   - `id_rsa`, `id_ed25519`, or any SSH private key files
3. Commit using heredoc:
   ```
   git -C <WORKTREE_DIR> commit -m "$(cat <<'EOF'
   fix: resolve merge conflicts with <BASE_BRANCH>

   Merge <BASE_BRANCH> into <PR_BRANCH> to resolve <K> conflicts:
   - <path1>: <brief resolution description>
   - <path2>: <brief resolution description>
   - <path3>: <brief resolution description>
   EOF
   )"
   ```
4. Do NOT use `--no-verify`. If the pre-commit hook fails:
   - Read the error output
   - Fix the issue (regenerate files, fix JSON, etc.)
   - Re-stage changes
   - Try the commit again
   - If the hook fails a second time, report the errors to the user and stop
5. Push: `git -C <WORKTREE_DIR> push origin <PR_BRANCH>`. Do NOT use `--no-verify`.

### Step 8: Cleanup worktree

```
git worktree remove <WORKTREE_DIR> --force
```

If the `.claude/worktrees/` directory is empty after cleanup, remove it: `rmdir .claude/worktrees/ 2>/dev/null`.

If any step after Step 3 fails and the command must stop, run this cleanup step before exiting.

### Step 9: Confirm

Report the result:

```
Merge conflicts resolved for PR #<PR_NUMBER>

Conflicts resolved (<K>):
  - <path1>: <strategy and brief description>
  - <path2>: <strategy and brief description>
  - <path3>: <strategy and brief description>

Files regenerated: <list or "none">
Commit: <short-sha> — fix: resolve merge conflicts with <BASE_BRANCH>
PR: https://github.com/<OWNER_REPO>/pull/<PR_NUMBER>
```

Suggest: "Check the PR to verify the merge is clean. CI should re-run automatically."
