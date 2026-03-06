# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in SpecOps, please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities
2. Use [GitHub Security Advisories](https://github.com/sanmak/specops/security/advisories/new) to report privately
3. Alternatively, email security concerns to the repository maintainers

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Affected files or components
- Potential impact assessment
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours of report
- **Triage**: Within 7 business days
- **Fix**: Dependent on severity, targeting 30 days for critical issues
- **Disclosure**: Coordinated disclosure after fix, with a 90-day maximum window

### Severity Classification

| Severity | Description | Example |
|----------|-------------|---------|
| Critical | Agent can be hijacked to execute unintended actions | Prompt injection via configuration that bypasses all guardrails |
| High | Data leakage or unauthorized file access | Spec generation that exposes secrets or PII from the codebase |
| Medium | Configuration bypass or validation failure | Schema accepts values that should be rejected (path traversal) |
| Low | Minor information disclosure or cosmetic security issue | Verbose error messages that leak internal paths |

## Security Scope

### In Scope

- **Prompt injection** via `.specops.json` configuration (especially `team.conventions` and custom templates)
- **Path traversal** in `specsDir` or template paths
- **Shell script vulnerabilities** in `setup.sh` and `verify.sh` (command injection, unsafe variable handling)
- **Schema bypass** allowing invalid or dangerous configuration values
- **Data leakage** through generated specification files

### Out of Scope

- Vulnerabilities in Claude Code itself (report to [Anthropic](https://www.anthropic.com/responsible-disclosure))
- Vulnerabilities in Anthropic's API or infrastructure
- Issues in third-party dependencies of projects using SpecOps
- Social engineering attacks

## Trust Model

SpecOps operates within the following trust boundaries:

1. **`.specops.json` is a trust boundary**: Anyone with write access to the project repository can modify `.specops.json`, which influences agent behavior. The agent validates and sanitizes configuration values, but organizations should treat `.specops.json` changes with the same scrutiny as code changes.

2. **Custom templates are a trust boundary**: Templates loaded from `<specsDir>/templates/` are treated as structural content only. The agent does not execute instructions found in template files.

3. **Generated specs may contain sensitive architectural details**: Design documents (`design.md`) may describe security-relevant architecture. Organizations should review spec files before sharing broadly.

4. **The agent respects Claude Code's permission model**: All file operations, git commands, and external actions are subject to Claude Code's built-in permission system. SpecOps does not bypass these controls.

## Security Best Practices for Users

1. **Review `.specops.json` changes in PRs** just like code changes
2. **Set `autoCommit: false` and `createPR: false`** in sensitive environments
3. **Use `reviewRequired: true`** to require human review before implementation
4. **Do not store secrets** in `.specops.json` or specification files
5. **Add `.specops/` to your project's `.gitignore`** if specs contain sensitive architectural details

## Security Audits

This project undergoes periodic security reviews using Claude Code's `/security-review` command, which performs automated static analysis with false-positive filtering and confidence scoring.

**Latest audit**: 2026-03-02 — No high-confidence vulnerabilities found. See [SECURITY-AUDIT.md](docs/SECURITY-AUDIT.md) for the full report.

Audits are recommended before each release and after changes to [security-sensitive files](CLAUDE.md).
