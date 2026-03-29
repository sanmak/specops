# Implementation Journal: Plan Mode Blocking Enforcement

## Summary

Upgraded the ExitPlanMode hook enforcement from advisory to blocking using a marker file state machine. The PostToolUse hook now creates a `.plan-pending-conversion` marker in specsDir when a plan is approved. A new PreToolUse Write|Edit guard blocks non-spec writes (exit code 2) when the marker exists, allowing only writes to specsDir, `.claude/plans/`, and `.claude/memory/`. The marker is removed by `from-plan` mode after the post-conversion enforcement pass (step 6.5) succeeds. Both local and remote installers updated with idempotent hook installation. Core modules (`core/from-plan.md`, `core/dispatcher.md`) document the marker lifecycle using abstract operations. All 10 tasks completed, 8/8 tests pass, 200+ validation checks pass, ShellCheck clean, checksums valid.

## Phase 1 Context Summary
- Config: loaded from `.specops.json` -- vertical: builder, specsDir: .specops, taskTracking: github
- Context recovery: none (from-plan conversion)
- Conversion source: file path (~/.claude/plans/nifty-beaming-gray.md)
- Steering directory: verified
- Memory directory: verified
- Vertical: builder (configured)
- Affected files: .claude/settings.local.json, platforms/claude/install.sh, scripts/remote-install.sh, core/from-plan.md, core/dispatcher.md, .gitignore, core/dependency-introduction.md, CLAUDE.md, docs/REFERENCE.md, CHANGELOG.md
- Project state: brownfield

## Decision Log

| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used `fp.startswith(a)` instead of `a in fp` for allowed path prefix matching in PreToolUse guard | Design used `any(a in fp for a in allowed)` which could match substrings anywhere in the path (e.g., `.specops/` matching inside `/foo/.specops/bar`). `startswith` is more precise for path prefix checking. | Task 2 | 2026-03-28 |
| 2 | PostToolUse hook replacement (not skip) when `specops-hook` marker already exists | Old installer skipped if existing hook found; new installer replaces advisory hook with marker-creating version, ensuring upgrades apply correctly. | Task 5 | 2026-03-28 |
| 3 | Used step 1.5 numbering for marker detection in from-plan.md | Avoids renumbering existing steps while inserting the marker detection between step 1 (receive plan) and step 2 (parse plan). Consistent with the step 3.5 precedent from AST Repo Map. | Task 3 | 2026-03-28 |

## Deviations from Design

| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| Design used `any(a in fp for a in allowed)` for path matching | Used `any(fp.startswith(a) for a in allowed)` | More precise path prefix matching; prevents false positives from substring matching | Task 2 |

## Blockers Encountered

| Blocker | Resolution | Impact | Task |
|---------|------------|--------|------|

## Documentation Review

| File | Status | Notes |
|------|--------|-------|
| CLAUDE.md | Updated | Added Plan Enforcement Hooks section |
| docs/REFERENCE.md | Updated | Added Plan Enforcement section with marker lifecycle |
| CHANGELOG.md | Updated | Added Unreleased entry for blocking enforcement |

## Session Log
<!-- Each implementation session appends a brief entry here. -->

### 2026-03-28: Phase 3 Implementation

Implemented all 10 tasks for plan mode blocking enforcement:
- Task 1: Confirmed `core/dependency-introduction.md` already deleted (pre-workflow)
- Task 2: Updated `.claude/settings.local.json` with marker-creating PostToolUse hook and PreToolUse Write|Edit guard
- Task 3: Added marker detection (step 1.5) and removal (after step 6.5) to `core/from-plan.md`
- Task 4: Updated dispatcher step 10.5 to reference marker file and PreToolUse blocking
- Task 5: Rewrote `platforms/claude/install.sh` hook installation with upgrade-in-place logic and PreToolUse guard
- Task 6: Mirrored hook changes in `scripts/remote-install.sh`
- Task 7: Added `.plan-pending-conversion` to `.gitignore`
- Task 8: Regenerated all platform outputs (35 files)
- Task 9: All validation (200+ checks), 8 tests, and ShellCheck pass
- Task 10: Updated CLAUDE.md, docs/REFERENCE.md, CHANGELOG.md; regenerated checksums

## Phase 3 Completion Summary

All 10 tasks completed successfully. The plan mode blocking enforcement feature is fully implemented:

**Core changes:**
- `core/from-plan.md`: Marker detection at step 1.5, marker removal after step 6.5 enforcement pass
- `core/dispatcher.md`: Step 10.5 updated to reference marker file and PreToolUse blocking

**Hook changes:**
- PostToolUse ExitPlanMode: Upgraded from advisory message to marker-creating (`touch <specsDir>/.plan-pending-conversion`)
- PreToolUse Write|Edit: New guard that blocks non-spec writes when marker exists (exit code 2)

**Installer changes:**
- `platforms/claude/install.sh`: Installs both hooks, upgrades existing advisory hooks in-place
- `scripts/remote-install.sh`: Mirrors local installer changes

**Supporting changes:**
- `.gitignore`: Marker file pattern added
- `.claude/settings.local.json`: Dogfood configuration with both hooks
- Documentation: CLAUDE.md, docs/REFERENCE.md, CHANGELOG.md updated
- Checksums: CHECKSUMS.sha256 regenerated

**Validation results:**
- `python3 generator/validate.py`: PASSED (all platforms, all checks)
- `bash scripts/run-tests.sh`: 8/8 PASSED
- `shellcheck`: Clean on both install scripts
- `shasum -a 256 -c CHECKSUMS.sha256`: All 20 files OK
- `npx markdownlint-cli2`: 0 errors on modified docs
