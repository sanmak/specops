Monitor GitHub Actions CI status for the current branch. If any workflow fails, diagnose the failure, fix it, commit, push, and re-monitor — up to 3 cycles.

## Instructions

Follow these steps precisely. This command assumes a push has already happened (via `/push`, `/ship`, or manual `git push`).

### Step 1: Pre-flight checks

Run `git status` to check the working tree.

If there are uncommitted changes (modified or untracked files), warn the user: "There are uncommitted changes that could interfere with automated fixes. Run /commit first or commit manually." and stop.

### Step 2: Identify CI runs

Get the current commit SHA and branch:

```bash
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
```

List workflow runs for this commit:

```bash
gh run list --branch <branch> --commit <sha> --json databaseId,status,conclusion,name,event --limit 20
```

If no runs are found, wait 10 seconds and retry. Repeat up to 3 times. If still no runs after 3 polls, tell the user: "No CI runs found for commit <sha>. CI may not be configured for this branch." and stop.

### Step 3: Wait for runs to complete

If any runs have `status` of `in_progress`, `queued`, or `pending`:

1. Tell the user which workflows are still running (list their names and statuses)
2. Wait 30 seconds
3. Re-fetch the run list with the same `gh run list` command
4. Repeat until all runs have `status: completed`

Safety: if you have polled more than 30 times (~15 minutes), stop and tell the user: "CI runs are taking too long. Check GitHub Actions manually." and stop.

### Step 4: Check results

Examine the `conclusion` field of each completed run.

If ALL runs have `conclusion: success`:

- Report to the user: "All CI checks passed!" with a list of the workflow names
- Stop — you are done

If ANY run has `conclusion: failure` (or `cancelled`, `timed_out`):

- Report which workflows failed (list names and conclusions)
- Proceed to Step 5

### Step 5: Diagnose failures

For each failed run, fetch the failure logs:

```bash
gh run view <databaseId> --log-failed
```

Analyze the log output to determine the root cause. Common failures in this project:

- **build-platforms**: Generated files are stale → run `python3 generator/generate.py --all`
- **verify-checksums**: Checksums are stale → regenerate with `shasum -a 256 -c CHECKSUMS.sha256` to identify mismatches, then regenerate
- **shellcheck**: Shell script lint errors → fix the flagged script
- **validate-json**: Malformed JSON → fix the JSON file
- **schema-validation**: Config doesn't match schema → fix the config or schema
- **schema-structure**: Schema well-formedness issue → fix schema.json
- **verify**: verify.sh failed → check output and fix
- **codeql**: Security issue found → fix the flagged code

If you cannot determine the cause from the logs, report the raw failure output to the user and stop.

### Step 6: Fix the issue

Apply the appropriate fix based on your diagnosis from Step 5.

After fixing:

1. Stage only the specific files you changed: `git add <file1> <file2> ...`
2. If you changed files in `core/`, `generator/templates/`, or `platforms/*/platform.json`, also run `python3 generator/generate.py --all` and stage the regenerated outputs: `git add platforms/ skills/ .claude-plugin/`
3. If you changed checksummed files, regenerate checksums:

   ```bash
   shasum -a 256 skills/specops/SKILL.md schema.json platforms/claude/SKILL.md \
     platforms/claude/platform.json platforms/cursor/specops.mdc \
     platforms/cursor/platform.json platforms/codex/SKILL.md \
     platforms/codex/platform.json platforms/copilot/specops.instructions.md \
     platforms/copilot/platform.json core/workflow.md core/safety.md \
     hooks/pre-commit hooks/pre-push scripts/install-hooks.sh \
     .claude-plugin/plugin.json .claude-plugin/marketplace.json > CHECKSUMS.sha256
   ```

   Then `git add CHECKSUMS.sha256`

Commit with a conventional message describing the fix. Use a heredoc:

```bash
git commit -m "$(cat <<'EOF'
fix: <concise description of what was fixed for CI>
EOF
)"
```

Do NOT add a Co-Authored-By line to the commit.
Do NOT use `--no-verify` — let the pre-commit hook run.

If the pre-commit hook fails, read the error, fix the issue, re-stage, and create a NEW commit (do not amend). Allow up to 2 hook retries before stopping and reporting to the user.

### Step 7: Push the fix

Run `git push`. Do NOT use `--no-verify`.

If the push fails due to the pre-push hook, read the error, fix the issue, re-stage, commit, and retry the push. Allow up to 2 hook retries before stopping and reporting to the user.

If the push fails for another reason (e.g., rejected by remote), report the error to the user and stop.

### Step 8: Loop back

This was fix-push cycle number N. If N >= 3, stop and report to the user:
"Reached maximum of 3 fix-push cycles. Remaining CI failures may require manual investigation."
List which workflows are still failing and what was attempted.

Otherwise, go back to Step 2 with the new commit SHA and repeat the monitoring cycle.

### Reporting

Throughout the process, keep the user informed:

- Which cycle you are on (e.g., "Monitoring cycle 1 of 3")
- Which workflows are running/passing/failing
- What failure was detected and what fix is being applied
- The commit SHA and message for each fix commit
