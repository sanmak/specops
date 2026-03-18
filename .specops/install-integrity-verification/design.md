# Design: Install Integrity Verification

## Architecture Overview
Add a checksum verification layer to `remote-install.sh` that fetches `CHECKSUMS.sha256` from the same version ref and validates each downloaded file before placing it on disk. Update security documentation to explain the trust model and manual verification workflow.

## Technical Decisions

### Decision 1: Verification Placement
**Context:** Where in the install flow should verification happen?
**Options Considered:**
1. Verify after each `download_file` call — immediate feedback per file
2. Download all files first, verify all at end — single batch check

**Decision:** Option 1 — verify immediately after each download
**Rationale:** Fail-fast behavior. If the first file fails verification, don't bother downloading remaining files. Also simpler since each platform installer function is self-contained.

### Decision 2: Hash Utility Detection
**Context:** macOS has `shasum`, Linux has `sha256sum`. Need cross-platform support.
**Options Considered:**
1. Detect once at script start, store in a variable
2. Detect in each verification call

**Decision:** Option 1 — detect once at startup
**Rationale:** Already have precedent in `bump-version.sh` (`shasum -a 256`). Detect early, fail early if neither is available.

### Decision 3: Checksums Fetch Strategy
**Context:** CHECKSUMS.sha256 needs to be fetched from the same version ref as the installed files.
**Options Considered:**
1. Fetch CHECKSUMS.sha256 once into a temp file, grep for each file's hash
2. Fetch and parse into shell variables

**Decision:** Option 1 — fetch once into a temp file
**Rationale:** CHECKSUMS.sha256 is a small file (~1KB). Fetching once and grepping is simpler than parsing into variables. The temp file is cleaned up on exit.

### Decision 4: `--no-verify` Flag Behavior
**Context:** Users may want to skip verification (air-gapped environments with custom mirrors, development testing).
**Options Considered:**
1. `--no-verify` silently skips
2. `--no-verify` shows warning then skips

**Decision:** Option 2 — always warn
**Rationale:** Users should be aware they are bypassing integrity verification. A single warning line is not intrusive.

## Product Module Design

### Module: Checksum Verification (in remote-install.sh)

**Responsibility:** Download CHECKSUMS.sha256, verify each platform file against it
**Interface:**
- `detect_hash_cmd()` — returns `sha256sum` or `shasum -a 256`, exits if neither found
- `fetch_checksums()` — downloads CHECKSUMS.sha256 to temp file, returns path
- `verify_file(file_path, expected_filename)` — computes hash of local file, compares against CHECKSUMS.sha256 entry

**Flow:**
```
Script start
  → detect_hash_cmd()
  → Parse --no-verify flag
  → If not --no-verify: fetch_checksums()
  → For each platform install:
    → download_file()
    → If not --no-verify: verify_file()
      → Match? Continue
      → Mismatch? Error + remove file + exit 1
      → No entry in checksums? Warning (file not in CHECKSUMS.sha256)
```

### Module: Documentation Updates

**SECURITY.md** — New subsection under "Trust Model":
- Install trust chain: GitHub HTTPS → versioned raw content → checksum verification
- Manual verification steps with exact commands
- `--no-verify` documentation

**docs/SBOM.md** — Update "Integrity Verification" section:
- Remote install verification is now automatic
- Manual verification still available

## Security Considerations
- Checksums are fetched over HTTPS from the same GitHub ref as the installed files. This means if the repo itself is compromised, checksums would also be compromised. This is a known limitation documented in the trust model.
- `--no-verify` is an explicit opt-in to reduced security, not a default.
- Temp files are cleaned up via trap on EXIT.

## Risks & Mitigations
- **Risk:** CHECKSUMS.sha256 format changes breaking grep → **Mitigation:** Format is stable (`<hash>  <path>`) and already used in CI; any format change would break CI first
- **Risk:** `sha256sum` vs `shasum` output format differences → **Mitigation:** Both produce `<hash>  <path>` format; normalize by extracting first field
