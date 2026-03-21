Run a comprehensive pre-PR quality gate that chains existing quality tools into a single check. This catches issues that code review bots (CodeRabbit, Copilot, Greptile) would flag, reducing PR review noise by ~62%.

## Instructions

Follow these steps precisely. Do not skip any step.

---

### Step 1: Run /core-review on current changes

Run the `/core-review` command with the `current` argument to check all uncommitted changes against SpecOps-specific patterns.

This catches ~40% of issues that bots would flag:
- P0: Raw abstract operations in generated outputs, detached HEAD patterns
- P1: Generated file edits, cross-platform marker gaps, variable inconsistency, missing checksums
- P2: Security-sensitive file advisories, spec alignment, step reference errors
- P3: EARS notation, empty sections, malformed checkboxes

If P0 or P1 findings exist, offer to auto-fix them before continuing.

Save the `/core-review` result summary (pass/fail, finding counts by severity) as `CORE_REVIEW_RESULT`.

---

### Step 2: Run automated validation battery

Run these checks sequentially. Record each result.

**2a. Platform validation:**
```bash
python3 generator/validate.py
```
Save exit code as `VALIDATE_RESULT` (0 = PASS, non-zero = FAIL).

**2b. Spec artifact lint:**
```bash
bash scripts/lint-specs.sh
```
Save exit code as `LINT_RESULT` (0 = PASS, non-zero = FAIL).

**2c. Checksum verification:**
```bash
shasum -a 256 -c CHECKSUMS.sha256
```
Save exit code as `CHECKSUMS_RESULT` (0 = PASS, non-zero = FAIL).

**2d. Full test suite:**
```bash
bash scripts/run-tests.sh
```
Save exit code as `TESTS_RESULT` (0 = PASS, non-zero = FAIL).

**2e. IssueID verification (when taskTracking configured):**

Read `.specops.json` and check `team.taskTracking`. If taskTracking is not `"none"`:
1. Read `.specops/index.json` (or scan spec directories) to find specs with status `implementing` or `completed`
2. For each such spec, read its `tasks.md` and find all tasks with `**Priority:** High` or `**Priority:** Medium`
3. Check that each eligible task has `**IssueID:**` set to a valid identifier (not `None`, not empty)
4. If any eligible tasks have missing IssueIDs, set `ISSUEID_RESULT` to `FAIL` and list the affected spec + task names

If taskTracking is `"none"` or `.specops.json` does not exist, set `ISSUEID_RESULT` to `SKIP (taskTracking not configured)`.

If any check fails, display the failure output to the user but continue running the remaining checks. All results feed into the dashboard.

---

### Step 3: Documentation sync check

Check if source files that affect documentation were modified:

```bash
git diff HEAD --name-only
```

If any files match `core/*.md`, `generator/templates/*.j2`, `generator/generate.py`, `schema.json`, or `docs/*.md`:
- Inform the user: "Source files with documentation impact were modified. Running docs-sync check..."
- Run the `/docs-sync` command
- Save the result as `DOCS_RESULT`

If no documentation-impacting files were modified:
- Set `DOCS_RESULT` to "SKIP (no doc-impacting changes)"

---

### Step 4: Display summary dashboard

Present the results in this format:

```
Pre-PR Quality Gate
════════════════════════════════════════
  Core Review:   {PASS/FAIL} ({P0 count} P0, {P1 count} P1, {P2 count} P2, {P3 count} P3)
  Validate:      {PASS/FAIL}
  Lint Specs:    {PASS/FAIL}
  Checksums:     {PASS/FAIL}
  Tests:         {PASS/FAIL} ({pass_count}/{total_count})
  IssueID Check: {PASS/FAIL/SKIP}
  Docs Sync:     {PASS/FAIL/SKIP}
════════════════════════════════════════
  Verdict: {verdict}
```

**Verdict logic:**
- If ALL checks pass: "Ready to ship. Run `/ship-pr` to create the PR."
- If only P2/P3 findings in core-review and all automated checks pass: "Ready to ship (advisory findings only). Run `/ship-pr` to create the PR."
- If any automated check fails OR P0/P1 findings remain: "Fix the issues above before creating a PR."

---

### Step 5: Security advisory (informational)

Check if any security-sensitive files appear in the diff:

```bash
git diff HEAD --name-only
```

Security-sensitive files: `core/workflow.md`, `core/safety.md`, `core/review-workflow.md`, `schema.json`, `spec-schema.json`, `platforms/claude/SKILL.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `setup.sh`, `scripts/remote-install.sh`, `generator/generate.py`, `hooks/pre-commit`, `hooks/pre-push`.

If any are modified, display:

> **Security advisory**: This change includes security-sensitive files: {list}. Consider running `/full-review-gate` for a deeper security review before shipping.

If none are modified, skip this step silently.
