## Dependency Safety

LLMs have knowledge cutoffs and may recommend vulnerable, deprecated, or end-of-life dependencies. The dependency safety gate actively verifies project dependencies against CVEs, EOL status, and best practices before implementation begins.

### Dependency Detection Protocol

Detect project ecosystems by scanning for indicator files:

| Indicator File | Ecosystem | Audit Command | Lock File |
| --- | --- | --- | --- |
| `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | Node.js | `npm audit --json` | `package-lock.json` |
| `requirements.txt` / `Pipfile.lock` / `poetry.lock` | Python | `pip-audit --format json` | `requirements.txt` |
| `Cargo.lock` | Rust | `cargo audit --json` | `Cargo.lock` |
| `Gemfile.lock` | Ruby | `bundle audit check --format json` | `Gemfile.lock` |
| `go.sum` | Go | `govulncheck -json ./...` | `go.sum` |
| `composer.lock` | PHP | `composer audit --format json` | `composer.lock` |
| `pom.xml` / `build.gradle` | Java/Kotlin | (LLM fallback — no standard CLI) | `pom.xml` |

Detection procedure:

1. LIST_DIR(`.`) to find project root files
2. For each indicator file in the table, FILE_EXISTS check
3. If `config.dependencySafety.scanScope` is `"spec"`, cross-reference detected ecosystems with the spec's affected files to narrow the scan scope. If `"project"`, scan all detected ecosystems.

### Package Manager Audit Commands

| Ecosystem | Command | JSON Output | Install Instructions |
| --- | --- | --- | --- |
| Node.js | `npm audit --json` | `{ "vulnerabilities": {...} }` | Bundled with Node.js |
| Python | `pip-audit --format json` | `[{ "name": ..., "version": ..., "vulns": [...] }]` | `pip install pip-audit` |
| Rust | `cargo audit --json` | `{ "vulnerabilities": {...} }` | `cargo install cargo-audit` |
| Ruby | `bundle audit check --format json` | JSON advisory list | `gem install bundler-audit` |
| Go | `govulncheck -json ./...` | `{ "vulns": [...] }` | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| PHP | `composer audit --format json` | `{ "advisories": {...} }` | Bundled with Composer 2.4+ |

If the audit tool is not installed: NOTIFY_USER("Audit tool '<tool>' not found for <ecosystem>. Skipping Layer 1 for this ecosystem — falling through to online verification.") and proceed to Layer 2.

### Dependency Safety Gate

**Phase 2 step 6.7 — MANDATORY gate.** If `config.dependencySafety.enabled` is not `false` (default: true), execute this gate. Skipping this gate when dependency safety is enabled is a protocol breach.

#### Gate Procedure

1. **Run Dependency Detection Protocol** — identify all ecosystems present in the project.
2. **No ecosystems detected** — if no indicator files are found, record "No dependency ecosystems detected" in dependency-audit.md and proceed. The gate passes.
3. **For each detected ecosystem**, execute the 3-layer verification:

   **Layer 1 — Local Audit Tools:**
   - RUN_COMMAND the appropriate audit command from the Package Manager Audit Commands table.
   - Parse JSON output to extract vulnerabilities with severity scores.
   - If the command fails (tool not installed, parse error), NOTIFY_USER and fall through to Layer 2.

   **Layer 2 — Online Verification:**
   - Execute the Online Verification Protocol (OSV.dev + endoflife.date).
   - If online queries fail (network timeout, API error), fall through to Layer 3.

   **Layer 3 — LLM Knowledge Fallback:**
   - Execute the Offline Fallback Protocol.
   - Use training data knowledge to assess known vulnerabilities for detected dependencies.

4. **Compile findings** — merge results from all layers, deduplicate by CVE ID. Classify each finding:
   - **Critical**: CVSS >= 9.0
   - **High**: CVSS 7.0–8.9
   - **Medium**: CVSS 4.0–6.9
   - **Low**: CVSS < 4.0
   - **Advisory**: informational, no CVSS score

5. **Apply severityThreshold** from `config.dependencySafety.severityThreshold` (default: `"medium"`). See the Severity Evaluation and Blocking Logic section for threshold behavior.

6. **Filter allowedAdvisories** — if `config.dependencySafety.allowedAdvisories` contains CVE IDs that match findings, mark those findings as acknowledged. They are recorded in the audit artifact but do not count toward the blocking threshold.

7. **Auto-fix** — if `config.dependencySafety.autoFix` is `true`:
   - Node.js: RUN_COMMAND(`npm audit fix`)
   - Rust: RUN_COMMAND(`cargo update`)
   - Other ecosystems: NOTIFY_USER("Auto-fix not available for <ecosystem>.")
   - After auto-fix, re-run Layer 1 audit to update findings.

8. **Blocking decision**:
   - If remaining findings (after allowedAdvisories filter) exceed the severity threshold → **BLOCK**. On interactive platforms (`canAskInteractive = true`): ASK_USER("Dependency safety gate found <N> blocking issue(s). Options: (1) Review and add to allowedAdvisories, (2) Attempt auto-fix, (3) Stop implementation."). On non-interactive platforms (`canAskInteractive = false`): list all findings and halt — do not proceed to implementation.
   - If findings are below the threshold → **WARN** and proceed. NOTIFY_USER with a summary of non-blocking findings.

9. **Write dependency-audit.md** artifact — WRITE_FILE(`<specsDir>/<spec-name>/dependency-audit.md`) with the Dependency Audit Artifact Format.

10. **Update dependencies.md steering file** — create or update `<specsDir>/steering/dependencies.md` following the Auto-Generated Steering File format.

11. **Record freshness timestamp** — RUN_COMMAND(`date -u +"%Y-%m-%dT%H:%M:%SZ"`) and include in both artifacts.

### Online Verification Protocol

For the top 10 dependencies (by import frequency or lock file position):

**OSV.dev API** — query for known vulnerabilities:

- RUN_COMMAND(`curl -s --max-time 10 -X POST "https://api.osv.dev/v1/query" -H "Content-Type: application/json" -d '{"package":{"name":"<pkg>","ecosystem":"<ecosystem>"}}'`)
- Parse the response for vulnerability entries. Extract CVE IDs and severity scores.
- If the request times out or returns an error, NOTIFY_USER("OSV.dev query failed for <pkg> — falling through to LLM fallback.") and continue.

**endoflife.date API** — check runtime/framework EOL status:

- RUN_COMMAND(`curl -s --max-time 10 "https://endoflife.date/api/<product>.json"`)
- Parse the response to find the project's runtime version and its EOL date.
- If the runtime is past EOL or within 6 months of EOL, flag as a finding.
- If the request fails, NOTIFY_USER("endoflife.date query failed for <product> — falling through to LLM fallback.") and continue.

Network failure at any point is non-blocking — fall through to Layer 3.

### Offline Fallback Protocol

When Layers 1 and 2 are both unavailable (no audit tools installed, no network access):

- The LLM uses its training data knowledge to assess the project's dependencies.
- Review the dependency list (from lock files or manifest files) and flag:
  - Known CVEs from training data
  - Dependencies known to be deprecated or unmaintained
  - Runtimes or frameworks known to be past EOL
- **Every finding from this layer MUST be annotated**: "(offline — based on training data, may not reflect latest advisories)"
- The gate still runs — it never silently passes. Even with no tools and no network, the LLM produces a best-effort assessment.

### Severity Evaluation and Blocking Logic

Threshold behavior based on `config.dependencySafety.severityThreshold`:

| Threshold | Block On | Warn On | Pass On | Audience |
| --- | --- | --- | --- | --- |
| `strict` | Any finding (Critical, High, Medium, Low, Advisory) | — | — | Enterprises, regulated industries |
| `medium` (default) | Critical, High | Medium | Low, Advisory | Growth teams, standard projects |
| `low` | — | Critical, High, Medium, Low | Advisory | Fast-moving startups, prototypes |

- `"strict"`: block on any finding. Every vulnerability, deprecation, or EOL status is a showstopper.
- `"medium"` (default): block on Critical and High. Warn on Medium. Pass on Low and Advisory.
- `"low"`: warn only, never block. All findings are informational. Implementation proceeds regardless.

### Dependency Audit Artifact Format

The audit artifact is written per-spec to `<specsDir>/<spec-name>/dependency-audit.md`. Template (defined inline — not in core/templates/):

```markdown
# Dependency Audit: [Spec Name]

**Verified:** YYYY-MM-DDTHH:MM:SSZ
**Threshold:** [strict|medium|low]
**Result:** [PASS|WARN|BLOCK]

## Dependency Inventory

| Package | Version | Ecosystem | Source |
| --- | --- | --- | --- |
| [name] | [version] | [ecosystem] | [lock file] |

## CVE Scan Results

| CVE ID | Package | Severity | CVSS | Description | Layer |
| --- | --- | --- | --- | --- | --- |
| [CVE-YYYY-NNNNN] | [package] | [Critical/High/Medium/Low] | [score] | [brief] | [1/2/3] |

## EOL Status

| Product | Version | EOL Date | Status |
| --- | --- | --- | --- |
| [runtime/framework] | [version] | [date] | [Active/EOL/Approaching EOL] |

## Verification Method

- Layer 1 (Local audit): [used/skipped — reason]
- Layer 2 (Online APIs): [used/skipped — reason]
- Layer 3 (LLM fallback): [used/not needed]

## Allowed Advisories

[List of CVE IDs from allowedAdvisories config that were found and excluded from blocking, or "None"]
```

### Auto-Generated Steering File: dependencies.md

The `dependencies.md` steering file is the 4th foundation template alongside `product.md`, `tech.md`, and `structure.md`. It uses the `_generated: true` pattern (same as `repo-map.md`) for machine-managed content.

Frontmatter:

```yaml
---
name: "Dependency Safety"
description: "Project dependencies, known issues, approved versions, and migration timelines"
inclusion: always
_generated: true
_generatedAt: "YYYY-MM-DDTHH:MM:SSZ"
---
```

Auto-populated sections (written by the agent during the dependency safety gate):

```markdown
## Detected Dependencies

| Package | Version | Ecosystem | Last Audited |
| --- | --- | --- | --- |
| [name] | [version] | [ecosystem] | [timestamp] |

## Runtime & Framework Status

| Product | Version | EOL Date | Status |
| --- | --- | --- | --- |
| [runtime] | [version] | [date] | [Active/EOL/Approaching] |
```

Team-maintained sections (preserved across regeneration — agent must not overwrite):

```markdown
## Approved Versions

[Team-maintained: list approved dependency versions and ranges]

## Banned Libraries

[Team-maintained: libraries that must not be used, with reasons]

## Migration Timelines

[Team-maintained: planned dependency upgrades and deadlines]

## Known Accepted Risks

[Team-maintained: acknowledged vulnerabilities with justification]
```

**Staleness**: During Phase 1 steering file loading, if `dependencies.md` exists and `_generatedAt` is more than 30 days old, NOTIFY_USER("Dependency safety data in `dependencies.md` is over 30 days old. It will be refreshed during the next dependency safety gate run.").

### Platform Adaptation

All 4 supported platforms have `canExecuteCode: true`, so the full audit + curl workflow is available everywhere.

- **`canAskInteractive = true`** (Claude Code, Cursor, Copilot): On blocking findings, offer the user choices: review and allowlist, attempt auto-fix, or stop.
- **`canAskInteractive = false`** (Codex): On blocking findings, list all findings and halt. Do not prompt — the user must resolve findings before re-running.
- **`canTrackProgress = false`** (Cursor, Codex, Copilot): Report audit progress in text output rather than a progress tracker.

### Dependency Safety Configuration

Read `config.dependencySafety` and apply defaults for any missing fields:

```json
{
  "dependencySafety": {
    "enabled": true,
    "severityThreshold": "medium",
    "autoFix": false,
    "allowedAdvisories": [],
    "scanScope": "spec"
  }
}
```

- **`enabled`** (boolean, default `true`): Master switch. Set to `false` to disable the dependency safety gate entirely.
- **`severityThreshold`** (string, default `"medium"`): Controls blocking behavior. One of `"strict"`, `"medium"`, `"low"`.
- **`autoFix`** (boolean, default `false`): Attempt automatic remediation (e.g., `npm audit fix`) before re-evaluating.
- **`allowedAdvisories`** (string array, default `[]`): CVE IDs that are acknowledged and excluded from blocking. Maximum 50 entries.
- **`scanScope`** (string, default `"spec"`): Scope of the dependency scan. `"spec"` scans only ecosystems relevant to the current spec's affected files. `"project"` scans all detected ecosystems.
