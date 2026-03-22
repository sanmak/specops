# Security Audit Report

| Field | Value |
| ------- | ------- |
| **Date** | 2026-03-02 |
| **Tool** | Claude Code `/security-review` |
| **Scope** | Full codebase (shell scripts, Python, JSON schemas, agent instructions) |
| **Result** | No high-confidence vulnerabilities found |

## Methodology

Three-phase review process:

1. **Initial scan** — Automated static analysis of all source files covering: input validation, command injection, path traversal, template injection, unsafe deserialization, insecure download patterns, schema bypass, and prompt injection vectors
2. **False-positive filtering** — Each finding independently validated against actual code behavior, data flow, and threat model context
3. **Confidence scoring** — Remaining findings scored 1–10 for exploitability and impact. Only findings scoring 8+ are reported as true vulnerabilities

## Findings

5 of 6 initial findings were validated as low-confidence false positives after Phase 2 filtering. Finding #2 (supply chain integrity) has since been remediated with SHA-256 checksum verification for defense-in-depth.

| # | Category | File(s) | Initial Finding | Confidence | Verdict |
| --- | ---------- | --------- | ----------------- | ----------- | --------- |
| 1 | Code Injection | `verify.sh:156` | `$json_file` interpolated into `python3 -c` string | 3/10 | False positive — all filenames are hardcoded string literals with no path to untrusted input |
| 2 | Supply Chain | `scripts/remote-install.sh` | Downloads agent instruction files without checksum verification | 3/10 | **Addressed** — SHA-256 checksum verification added to remote installer (v1.3.0). Downloaded files are now verified against `CHECKSUMS.sha256` before installation |
| 3 | Command Injection | `scripts/run-tests.sh:23`, `hooks/pre-push:33` | `eval` used to execute command strings | 2/10 | False positive — all `eval` arguments are hardcoded string literals within the same file |
| 4 | URL Injection | `scripts/remote-install.sh:49` | `SPECOPS_VERSION` path traversal could redirect downloads | 3/10 | False positive — CLI flags are trusted user input, self-inflicted attack scenario |
| 5 | Path Traversal | `platforms/{cursor,codex,copilot}/install.sh` | Install directory `$1` accepted without validation | 2/10 | False positive — user provides the path, scripts only `mkdir + cp` a non-executable config file |
| 6 | Schema Bypass | `schema.json:15` | `specsDir` regex allows `..` without trailing slash | 2/10 | False positive — `core/safety.md` independently blocks any `..` substring at runtime |

## Existing Security Infrastructure

The project has comprehensive security mechanisms in place:

- **Input sanitization** — `core/safety.md` defines convention sanitization, template safety, and path containment rules enforced across all platforms
- **Schema validation** — `schema.json` enforces `additionalProperties: false`, `maxLength`, and `maxItems` on all fields
- **Integrity verification** — `CHECKSUMS.sha256` with SHA-256 hashes of critical files, verified in CI
- **Static analysis** — CodeQL (Python) runs on every push and PR, plus weekly scheduled scans
- **Shell linting** — ShellCheck enforced in CI and pre-push hooks for all shell scripts
- **Supply chain** — Zero runtime dependencies (see `SBOM.md`)
- **Git hooks** — Pre-commit and pre-push hooks validate JSON, checksums, generated file freshness, and run the full test suite

## Hardening Recommendations

These are not vulnerabilities but optional improvements for defense in depth:

1. **`verify.sh` — use `sys.argv` pattern** — Replace `python3 -c "...open('$json_file')..."` with `python3 -c "...open(sys.argv[1])..." "$json_file"` for consistency with the safer pattern already used in `hooks/pre-commit`
2. **`remote-install.sh` — validate version input** — Add a regex check (`^[a-zA-Z0-9._-]+$`) on `SPECOPS_VERSION` to reject path traversal characters
3. **Platform install scripts — add path validation** — Apply the same validation from `platforms/claude/install.sh` (rejects `..`, control characters, warns on system paths) to the cursor, codex, and copilot installers
4. **`schema.json` — tighten `specsDir` regex** — Change `(?!.*\\.\\./)` to `(?!.*\\.\\.)` to block `..` without trailing slash (already caught by `core/safety.md` at runtime)

## Agent Trust Hub Audit (March 2026)

An external audit by [Agent Trust Hub](https://skills.sh/sanmak/specops/specops/security/agent-trust-hub) flagged SpecOps as HIGH risk across 5 categories. Assessment and resolution status:

| # | Category | Risk | Status | Resolution |
| --- | ---------- | ------ | -------- | ------------ |
| 1 | Remote Code Execution | HIGH | **Addressed** | SHA-256 checksum verification added to remote installer. Downloaded files are verified against published hashes before installation. `--no-verify` flag available for development use. |
| 2 | External Downloads | MEDIUM | **Documented** | Install trust model documented in SECURITY.md. Manual verification instructions provided. Residual repo-compromise risk acknowledged. |
| 3 | Command Execution | LOW | **Expected behavior** | Shell commands for file management and git operations are core to a development workflow tool. Not a vulnerability. |
| 4 | Data Exfiltration | LOW | **Expected behavior** | Reading git config for author names is standard. No sensitive data is transmitted externally. |
| 5 | Prompt Injection | LOW | **Non-issue** | The audit itself acknowledges these are "constraints rather than security bypasses." `CRITICAL`/`IMPORTANT` directives are standard instruction formatting. |

## Decomposition Feature — Audit Notes (v1.5.0)

The spec decomposition feature introduces new path construction patterns that should be reviewed in the next audit:

- **Initiative ID in path construction**: Initiative IDs are used to construct directory paths (`<specsDir>/initiatives/<id>/`). The ID pattern is constrained by `initiative-schema.json` to `^[a-zA-Z0-9._-]+$`, which prevents path traversal. Runtime validation should also apply containment checks (no `..`, no absolute paths).
- **Spec dependency references**: `specDependencies[].specId` values reference other spec directories. These are validated against the same pattern constraint.
- **Cycle detection**: The DFS-based cycle detection algorithm processes user-influenced data (spec IDs and dependency graphs). Malformed dependency graphs are bounded by `maxItems: 50` on the `specDependencies` array.

**Status**: Re-audit recommended before v1.5.0 release.

## Next Audit

Recommended before the next minor or major release, or after significant changes to [security-sensitive files](../CLAUDE.md).
