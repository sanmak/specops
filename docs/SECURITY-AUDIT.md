# Security Audit Report

| Field | Value |
|-------|-------|
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

All 6 initial findings were validated as false positives after Phase 2 filtering.

| # | Category | File(s) | Initial Finding | Confidence | Verdict |
|---|----------|---------|-----------------|-----------|---------|
| 1 | Code Injection | `verify.sh:156` | `$json_file` interpolated into `python3 -c` string | 3/10 | False positive — all filenames are hardcoded string literals with no path to untrusted input |
| 2 | Supply Chain | `scripts/remote-install.sh` | Downloads agent instruction files without checksum verification | 3/10 | False positive — HTTPS provides transport integrity, standard practice for CLI install scripts |
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

## Next Audit

Recommended before the next minor or major release, or after significant changes to [security-sensitive files](../CLAUDE.md).
