# Design: Drift Detection & Guided Reconciliation

## Architecture Overview
A new `core/reconciliation.md` module added as the 17th core module, following the same integration pattern as `core/steering.md` (Spec 3). The module is loaded by `generator/generate.py`, rendered into all 4 platform outputs via Jinja2 templates, and validated by `generator/validate.py`. Mode detection is added to `core/workflow.md` Getting Started section.

## Technical Decisions

### Decision 1: Module placement in Jinja2 templates
**Context:** Where to insert `{{ reconciliation }}` in the 4 Jinja2 templates.
**Options Considered:**
1. After `{{ view }}`, before `{{ interview }}` — groups all subcommand/mode handlers together near the workflow
2. After `{{ update }}`, before `{{ safety }}` — groups with version-management commands

**Decision:** After `{{ view }}`, before `{{ interview }}`
**Rationale:** `view`, `list`, `audit`, and `reconcile` are all spec-inspection modes. Grouping them together makes the mode detection chain easier to follow. This matches the pattern from `drift-reconciliation-planner.md`.

### Decision 2: Reconciliation markers (Gap 13 lesson)
**Context:** Markers must be specific enough to not match workflow prose (substring collision), and must use heading-level anchors.
**Decision:** Use heading-prefixed markers: `"## Audit Mode"`, `"## Reconcile Mode"`, `"### File Drift"`, `"### Post-Completion Modification"`, `"### Task Status Inconsistency"`, `"### Staleness"`, `"### Cross-Spec Conflicts"`, `"### Health Summary"`, `"### Audit Report"`
**Rationale:** Heading-level markers are unique to the reconciliation module and cannot collide with prose references to the same concepts in other modules.

### Decision 3: No schema changes
**Context:** Should staleness thresholds or other reconciliation config be added to `schema.json`?
**Decision:** No schema changes. All thresholds hardcoded (7d/14d/30d for staleness, 20-file limit for tasks.md scanning).
**Rationale:** Simplicity principle — hardcoded sensible defaults avoid premature configuration. The design document in `internal/drift-reconciliation-planner.md` explicitly calls this out.

### Decision 4: reconcile gated behind canAskInteractive
**Context:** Reconcile repairs require interactive user selection. How should non-interactive platforms handle it?
**Decision:** Audit mode works on all platforms. Reconcile mode is blocked on non-interactive platforms (`canAskInteractive = false`) with a clear message. This is explicit in the module — no fallback repair sequence.
**Rationale:** Repair decisions (delete reference, update path, mark pending/completed) require human judgment. Auto-applying repairs without confirmation would be dangerous. Non-interactive platforms can still run `audit` for the read-only report.

## Component Design

### core/reconciliation.md
**Responsibility:** Platform-agnostic specification of audit and reconcile workflows using abstract tool operations
**Interface:** Mode detection patterns + audit workflow + reconcile workflow + report format + platform adaptation rules
**Dependencies:** Assumes `FILE_EXISTS`, `READ_FILE`, `LIST_DIR`, `RUN_COMMAND`, `ASK_USER`, `NOTIFY_USER` abstract ops; reads from `<specsDir>/*/spec.json` and `<specsDir>/*/tasks.md`

### generator/generate.py (modification)
**Responsibility:** Load `core/reconciliation.md` and inject into all 4 platform context dicts
**Change:** Add `"reconciliation": core["reconciliation"]` to context in `generate_claude`, `generate_cursor`, `generate_codex`, `generate_copilot`

### generator/templates/*.j2 (modification — 4 files)
**Responsibility:** Place `{{ reconciliation }}` at the right insertion point
**Change:** Insert `{{ reconciliation }}` after `{{ view }}` in all 4 templates

### generator/validate.py (modification)
**Responsibility:** Verify reconciliation module content is present in all generated outputs
**Change:** Add `RECONCILIATION_MARKERS` list (9 markers), call `check_markers_present` in `validate_platform`, add markers to cross-platform consistency check

### tests/test_platform_consistency.py (modification)
**Responsibility:** Verify all platforms have reconciliation content consistently
**Change:** Add `"reconciliation"` category with the same 9 markers to `REQUIRED_MARKERS`

## Audit Mode Flow

```text
User invokes audit
      │
      ▼
Parse spec name (or "all non-completed specs")
      │
      ▼
For each target spec:
  ├── Check 1: File Drift (FILE_EXISTS for each "Files to Modify" path)
  ├── Check 2: Post-Completion Modification (git log after spec.json.updated, completed only)
  ├── Check 3: Task Status Inconsistency (completed tasks with missing files; pending tasks with existing files)
  ├── Check 4: Staleness (age of spec.json.updated vs thresholds)
  └── Check 5: Cross-Spec Conflicts (multiple active specs referencing same files)
      │
      ▼
Produce Health Summary (Healthy/Warning/Drift per check, overall = worst)
```

## Report Format

### Single-spec report
```
# Audit: <spec-name>

**Status**: <status> | **Version**: v<version> | **Updated**: <updated>

## Health Summary

| Check | Result | Details |
|-------|--------|---------|
| File Drift | Healthy | 4 files checked, 0 issues |
| Post-Completion Mods | Healthy | 0 files modified after completion |
| Task Consistency | Warning | Task 3 marked Completed, file missing |
| Staleness | Healthy | 2 days since last activity |
| Cross-Spec Conflicts | Healthy | No shared files |

**Overall Health**: Warning

## Findings
[Per-check details for non-Healthy checks only]
```

### All-specs report
```
# SpecOps Audit Report

**Audited**: N specs | **Date**: <current date>

## Summary

| Spec | Status | Health | Issues |
|------|--------|--------|--------|
| auth-feature | implementing | Warning | 1 task inconsistency |
| oauth-refresh | implementing | Drift | 2 missing files |

**Overall**: 1 Healthy, 1 Warning, 1 Drift
```

## Reconcile Flow

```text
Run full audit on target spec
      │
      ▼
All Healthy? → "No drift detected. No reconciliation needed." → stop
      │
      ▼
Present numbered finding list with repair options per finding type
      │
      ▼
ASK_USER: "fix all", "fix 1,3", or "skip"
      │
      ▼
For each selected finding, apply repair:
  - File deleted → remove reference from tasks.md / provide new path / skip
  - File renamed → update path in tasks.md / skip
  - Stale spec → set draft / set completed / skip
  - Cross-spec conflict → informational only (no repair)
      │
      ▼
Update spec.json.updated (RUN_COMMAND(`date -u`))
Regenerate index.json
Present fix summary
```

## Platform Adaptation

| Capability | Impact on Reconciliation |
|-----------|--------------------------|
| `canAccessGit: false` | Skip Check 2 (post-completion mods) and Check 4 git path; note in report |
| `canAskInteractive: false` | Audit works fully; Reconcile mode blocked with message |
| `canTrackProgress: false` | Progress in response text instead of todo system |

## Security Considerations
- Spec file paths from `tasks.md` are read-only during audit (no writes)
- `git log` commands use `--` path separator and quoted paths to prevent injection
- Reconcile only writes to spec artifact files within `<specsDir>` (path containment inherited from specsDir safety rules)
