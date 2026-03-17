# Feature: Install Integrity Verification

## Overview
Add SHA-256 checksum verification to the remote installer and document the security/trust model for SpecOps installations. Addresses findings from the Agent Trust Hub security audit (March 2026) — specifically the HIGH-priority `curl|bash` remote code execution finding and the non-verified source concern.

## Product Requirements

### Requirement 1: Checksum Verification in Remote Installer
**As a** developer installing SpecOps via `curl | bash`
**I want** downloaded files verified against published checksums
**So that** I can trust the installed files haven't been tampered with in transit or at the source

**Acceptance Criteria (EARS):**
<!-- EARS: Event-Driven and Unwanted Behavior patterns -->
- WHEN the remote installer downloads a platform file (SKILL.md, specops.mdc, specops.instructions.md) THE SYSTEM SHALL fetch the corresponding CHECKSUMS.sha256 from the same version ref and verify the downloaded file's SHA-256 hash matches before placing it on disk
- IF a checksum verification fails THEN THE SYSTEM SHALL display an error with the expected and actual hashes, remove the downloaded file, and exit with a non-zero status code
- IF CHECKSUMS.sha256 cannot be fetched (network error, 404) THEN THE SYSTEM SHALL display a warning and prompt for confirmation before proceeding with unverified installation (non-interactive mode: abort by default, `--no-verify` flag to skip)
- WHEN `--no-verify` flag is provided THE SYSTEM SHALL skip checksum verification and display a warning that integrity is not verified

**Progress Checklist:**
- [x] Downloaded files are verified against CHECKSUMS.sha256
- [x] Failed verification aborts with clear error
- [x] Missing CHECKSUMS.sha256 prompts user / aborts in non-interactive mode
- [x] `--no-verify` flag skips verification with warning

### Requirement 2: Security Model Documentation
**As a** developer evaluating SpecOps for adoption
**I want** clear documentation of the trust model, verification steps, and security posture
**So that** I can make an informed decision about installing and understand how to verify my installation

**Acceptance Criteria (EARS):**
<!-- EARS: Ubiquitous and Event-Driven patterns -->
- THE SYSTEM SHALL document the install trust model in SECURITY.md: what is trusted (GitHub HTTPS, release tags), what is verified (checksums), and what residual risks remain (repo compromise)
- THE SYSTEM SHALL provide manual verification instructions: how to verify installed files against CHECKSUMS.sha256 independently of the installer
- THE SYSTEM SHALL document the `--no-verify` flag and when it is appropriate to use

**Progress Checklist:**
- [x] Trust model documented in SECURITY.md
- [x] Manual verification steps documented
- [x] `--no-verify` flag documented

## Scope Boundary
**Ships in this spec:**
- Checksum verification in `remote-install.sh`
- Updated SECURITY.md with install trust model
- Updated SBOM.md with verification instructions
- `--no-verify` bypass flag

**Deferred:**
- GPG signing of releases (significant key management overhead for a solo maintainer)
- Reproducible builds / provenance attestations (GitHub Artifact Attestations)
- Automated CHECKSUMS.sha256 generation in CI release workflow

## Constraints & Assumptions
- The installer must work with both `sha256sum` (Linux) and `shasum -a 256` (macOS) — the script already has precedent for this in `bump-version.sh`
- CHECKSUMS.sha256 is already published in the repo and verified in CI
- No new dependencies — verification uses only `sha256sum`/`shasum` and standard shell builtins

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
