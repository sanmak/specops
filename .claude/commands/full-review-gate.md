Perform a comprehensive repository code review in an isolated worktree. Fix P0/P1 findings and ship them as a PR targeting the current branch.

## Instructions

Follow these steps precisely. Do not skip any pass or omit severity classification.

---

## Part 0: Setup

### Step 1: Record State and Confirm Scope

Record the current branch:

```bash
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
```

Ask the user which scope to use:

- **Full-repository scope**: use for complete reviews or release readiness checks.
- **Diff-focused scope**: use only when the user explicitly asks for a PR or diff review. Still inspect adjacent components likely to regress.

### Step 2: Create Worktree

First, clean any stale worktrees from prior interrupted runs:

```bash
git worktree list
```

For any entries with paths containing `.claude/worktrees/review-gate-`, remove them:

```bash
git worktree remove --force <stale-path>
```

Generate a branch slug from `ORIGINAL_BRANCH` (replace `/` and special characters with `-`, truncate to 30 characters). Create the worktree:

```bash
mkdir -p .claude/worktrees
git worktree add .claude/worktrees/review-gate-<branch-slug> HEAD
```

Save the full path as `WORKTREE_DIR`. If creation fails, report the error and stop.

---

## Part 1: Review (in worktree)

### Step 3: Run Baseline Checks

Run the automated baseline from within the worktree:

```bash
cd <WORKTREE_DIR> && bash scripts/run-review-gate.sh
```

If optional tools are missing (shellcheck, gitleaks, pip-audit, govulncheck), continue and note the coverage gaps for the final report.

### Step 4: Perform Manual Passes

Review the codebase from `WORKTREE_DIR` using the criteria below, in this order:

1. **Bug and Regression Pass**
   - Validate correctness for happy path, edge cases, and error handling.
   - Detect behavioral regressions in touched and adjacent modules.
   - Verify tests cover business-critical paths and failure scenarios.
   - Flag missing assertions, brittle tests, or untested branches.

2. **Security Pass**
   - Verify input validation and output encoding at trust boundaries.
   - Verify authorization checks are enforced server-side.
   - Review secret handling, credential storage, and log redaction.
   - Detect injection vectors, unsafe deserialization, and path traversal risks.
   - Verify dependency vulnerabilities and insecure defaults.

3. **PII and Privacy Pass**
   - Identify collection and storage of direct identifiers.
   - Verify logs do not store raw PII, tokens, or credentials.
   - Verify test fixtures use synthetic data rather than real user data.
   - Check retention and data-flow behavior against least-data principles.

4. **Dependency Adoption and Version-Risk Pass**
   - Prefer stable and generally adopted major versions over niche or abandoned packages.
   - Verify active maintenance and recent releases.
   - Avoid pre-release versions unless explicitly required.
   - Check known CVEs and changelog notes for breaking security changes.

All file reads during review must use `<WORKTREE_DIR>/<path>`.

---

## Part 2: Report

### Step 5: Report Findings

Use the severity rubric:

- **P0**: Critical exploit or data-loss risk. Block release immediately.
- **P1**: High-impact bug or security/privacy risk likely in production. Block release until fixed.
- **P2**: Medium risk with bounded impact or mitigations. Fix before next release unless explicitly accepted.
- **P3**: Low risk, quality issue, or improvement. Track and prioritize normally.

List findings first, ordered P0 to P3. For each finding include:

1. Severity
2. File and line reference
3. Exploit or failure scenario
4. Impact
5. Exact remediation
6. Required tests

Then include:

1. Release blocker list
2. Residual risk list
3. Coverage gaps caused by missing tools

Use this response structure:

```text
Findings (P0-P3):
- [Px] Title
  - File: <path>:<line>
  - Scenario:
  - Impact:
  - Fix:
  - Tests:

Release blockers:
- ...

Residual risk:
- ...

Verification rerun:
- verify.sh: pass/fail
- run-tests.sh: pass/fail
- security/PII scans: pass/fail/partial
```

Save the findings internally for use in the PR body.

### Step 6: Early Exit Check

If there are **zero P0 or P1 findings**:

1. Report "No release blockers found. No PR needed."
2. Skip directly to Step 10 (cleanup).

---

## Part 3: Fix and Ship

### Step 7: Fix P0/P1 Issues in Worktree

For each P0 and P1 finding:

1. Read the affected file from `<WORKTREE_DIR>/<path>`.
2. Apply the fix in the worktree.
3. Note what was changed.

After all fixes, run the regeneration and validation cycle:

- If any files under `core/`, `generator/templates/`, `generator/generate.py`, or `platforms/*/platform.json` were modified:
  ```bash
  cd <WORKTREE_DIR> && python3 generator/generate.py --all
  ```

- Run validation from the worktree:
  ```bash
  cd <WORKTREE_DIR> && python3 generator/validate.py
  cd <WORKTREE_DIR> && bash scripts/run-tests.sh
  ```

- If validation fails, attempt to fix (up to 2 retries). If still failing, report and stop.

Re-run baseline checks to confirm blockers are closed:

```bash
cd <WORKTREE_DIR> && bash scripts/run-review-gate.sh
```

### Step 8: Commit and Push from Worktree

1. Create a new branch in the worktree:
   ```bash
   git -C <WORKTREE_DIR> checkout -b fix/review-gate-<branch-slug>
   ```
   If the branch name already exists, append `-2` (or `-3`, etc.).

2. Stage all modified files:
   ```bash
   git -C <WORKTREE_DIR> add -A
   ```

3. Un-stage any sensitive files (`.env*`, `credentials.json`, `*.pem`, `*.key`).

4. Generate a commit message with `fix:` prefix summarizing the findings. Commit using heredoc:
   ```bash
   git -C <WORKTREE_DIR> commit -m "$(cat <<'EOF'
   fix: resolve P0/P1 review gate findings
   EOF
   )"
   ```
   Do NOT use `--no-verify`. If the pre-commit hook fails, fix and retry (up to 2 times).

5. Push the fix branch:
   ```bash
   git -C <WORKTREE_DIR> push -u origin fix/review-gate-<branch-slug>
   ```

Save the branch name as `FIX_BRANCH`.

### Step 9: Create PR

Create a PR targeting the original branch:

```bash
gh pr create --base <ORIGINAL_BRANCH> --head <FIX_BRANCH> \
  --title "fix: review gate P0/P1 remediations for <ORIGINAL_BRANCH>" \
  --body "$(cat <<'EOF'
## Review Gate Findings

This PR addresses P0 and P1 findings from a full review gate run.

### Fixed (P0/P1)

<for each fixed finding:>
- **[Px]** <title> — <file>:<line>
  - <one-line fix description>

### Remaining (P2/P3)

<for each unfixed finding:>
- **[Px]** <title> — <file>:<line>
  - <one-line description>

## Verification

- `run-review-gate.sh`: <pass/fail after fixes>
- `run-tests.sh`: <pass/fail>
- `validate.py`: <pass/fail>
- Coverage gaps: <list any missing tools>

## Test Plan

- [ ] Verify P0/P1 fixes do not introduce regressions
- [ ] Run `bash scripts/run-review-gate.sh` on the merged result
- [ ] Confirm P2/P3 items are tracked for follow-up
EOF
)"
```

Save the PR URL.

---

## Part 4: Cleanup

### Step 10: Cleanup and Report

Remove the worktree:

```bash
git worktree remove <WORKTREE_DIR> --force
rmdir .claude/worktrees/ 2>/dev/null
```

Report the result:

- If no P0/P1 findings (early exit): "Review gate passed. No release blockers found."
- If P0/P1 findings were fixed:
  - PR URL
  - Fix branch name and target branch
  - Number of P0/P1 findings fixed
  - Number of P2/P3 findings remaining
  - Reminder: "Your `<ORIGINAL_BRANCH>` branch is unchanged. Merge the PR to incorporate fixes."
