# Implementation Tasks: Install Integrity Verification

## Task Breakdown

### Task 1: Add checksum verification to remote-install.sh
**Status:** Completed
**Estimated Effort:** M
**Dependencies:** None
**Priority:** High
**Blocker:** None

**Description:**
Add `detect_hash_cmd()`, `fetch_checksums()`, and `verify_file()` functions to `scripts/remote-install.sh`. Wire verification into each platform installer function after the `download_file` call. Add `--no-verify` flag to argument parsing.

**Implementation Steps:**
1. Add `--no-verify` to argument parsing (after existing flags)
2. Add `detect_hash_cmd()` that checks for `sha256sum` then `shasum -a 256`
3. Add `fetch_checksums()` that downloads CHECKSUMS.sha256 to a temp file using the existing `download_file` helper
4. Add `verify_file()` that computes the hash of the local file and greps the checksums file for a match
5. Call `detect_hash_cmd()` and `fetch_checksums()` after argument parsing (skip if `--no-verify`)
6. Add `verify_file` call after each `download_file` in the 4 platform installer functions
7. Add trap to clean up checksums temp file on EXIT

**Acceptance Criteria:**
- [x] `--no-verify` flag is parsed and documented in usage
- [x] `detect_hash_cmd` finds sha256sum or shasum, exits if neither
- [x] CHECKSUMS.sha256 is fetched from the same version ref
- [x] Each downloaded file is verified against checksums
- [x] Verification failure removes the file and exits non-zero
- [x] Missing checksums file prompts in interactive mode, aborts in non-interactive

**Files to Modify:**
- `scripts/remote-install.sh`

**Tests Required:**
- [x] ShellCheck passes on modified remote-install.sh

---

### Task 2: Update SECURITY.md with install trust model
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** High
**Blocker:** None

**Description:**
Add an "Install Verification" subsection to the Trust Model section of SECURITY.md. Document the trust chain, manual verification steps, and `--no-verify` flag.

**Implementation Steps:**
1. Add "Install Verification" subsection under "Trust Model" (after existing items 1-4)
2. Document the trust chain: HTTPS transport → versioned content → SHA-256 verification
3. Add manual verification commands (`shasum -a 256 -c CHECKSUMS.sha256 --ignore-missing`)
4. Document `--no-verify` flag and appropriate use cases
5. Document residual risks (repo compromise)

**Acceptance Criteria:**
- [x] Trust chain documented with clear explanation
- [x] Manual verification commands provided
- [x] `--no-verify` flag documented with use cases
- [x] Residual risks acknowledged

**Files to Modify:**
- `SECURITY.md`

**Tests Required:**
- [ ] No broken markdown links

---

### Task 3: Update SBOM.md integrity verification section
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**Blocker:** None

**Description:**
Update the "Integrity Verification" section in `docs/SBOM.md` to reflect that the remote installer now performs automatic checksum verification.

**Implementation Steps:**
1. Update the "Integrity Verification" section to note automatic verification in remote installs
2. Keep manual verification commands as a secondary option
3. Update "Supply Chain Transparency" to mention checksum verification

**Acceptance Criteria:**
- [x] SBOM.md reflects automatic verification
- [x] Manual verification still documented

**Files to Modify:**
- `docs/SBOM.md`

**Tests Required:**
- [ ] No broken markdown links

---

### Task 4: Update SECURITY-AUDIT.md with resolved finding
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1
**Priority:** Medium
**Blocker:** None

**Description:**
Update the security audit report to reflect that finding #2 (checksum verification) is now addressed, and add the Agent Trust Hub audit findings as a new section.

**Implementation Steps:**
1. Update finding #2 verdict from "False positive" to note it has been addressed
2. Add a section for the Agent Trust Hub audit (March 2026) with status of each finding

**Acceptance Criteria:**
- [x] Finding #2 updated to reflect the fix
- [x] Agent Trust Hub audit findings documented with resolution status

**Files to Modify:**
- `docs/SECURITY-AUDIT.md`

**Tests Required:**
- [ ] No broken markdown links

---

### Task 5: Validate and test
**Status:** Completed
**Estimated Effort:** S
**Dependencies:** Task 1, Task 2, Task 3, Task 4
**Priority:** High
**Blocker:** None

**Description:**
Run ShellCheck on the modified script, run the existing test suite, and verify the remote installer works with checksum verification.

**Implementation Steps:**
1. Run `shellcheck scripts/remote-install.sh`
2. Run `bash scripts/run-tests.sh`
3. Test remote-install.sh locally: verify it fetches checksums and validates files

**Acceptance Criteria:**
- [x] ShellCheck passes with no warnings
- [x] All 7 existing tests pass
- [x] Remote installer successfully verifies checksums for at least one platform

**Files to Modify:**
- `scripts/remote-install.sh` (fixes from ShellCheck if any)

**Tests Required:**
- [x] ShellCheck passes
- [x] Full test suite passes

## Implementation Order
1. Task 1 (core implementation — checksum verification in remote-install.sh)
2. Task 2 (SECURITY.md documentation)
3. Task 3, Task 4 (parallel — SBOM.md and SECURITY-AUDIT.md updates)
4. Task 5 (validation and testing)

## Progress Tracking
- Total Tasks: 5
- Completed: 5
- In Progress: 0
- Blocked: 0
- Pending: 0
