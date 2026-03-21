# Design: Rich Issue Bodies and Auto-Labels

## Architecture Overview

The Issue Creation Protocol in `core/config-handling.md` currently references `<TaskDescription>` without defining its composition. We add two new subsections — Issue Body Composition and GitHub Label Protocol — between the existing "For each eligible task:" line and the platform-specific steps. The platform steps update from `<TaskDescription>` to `<IssueBody>` and add `--label` flags for GitHub. Two cross-references reinforce the protocol breach language in `core/task-tracking.md` and `core/workflow.md`. Validator markers ensure CI catches accidental removal.

## Technical Decisions

### Decision 1: Inline Template vs Separate Module
**Context:** The issue body template could live in its own `core/issue-template.md` module or inline in `core/config-handling.md`.
**Options Considered:**
1. Separate `core/issue-template.md` — requires new module in docs/STRUCTURE.md, docs-sync mapping, generator context entry, Jinja2 variable
2. Inline in `core/config-handling.md` — ~40 lines added to existing Issue Creation Protocol section

**Decision:** Inline in `core/config-handling.md`
**Rationale:** The issue body composition is tightly coupled to the Issue Creation Protocol. The simplicity principle says keep it together — a separate module adds 4 files of overhead for ~40 lines of content.

### Decision 2: Label Namespace
**Context:** GitHub labels for spec names could collide with existing repository labels.
**Options Considered:**
1. Raw spec name as label (e.g., `auth-feature`)
2. Namespaced label (e.g., `spec:auth-feature`)

**Decision:** Namespaced `spec:<spec-id>`
**Rationale:** Prevents collisions with existing repository labels. A spec named "auth" would conflict with an existing "auth" label, but `spec:auth` is unambiguous.

### Decision 3: Type Label Naming
**Context:** Spec types in spec.json are `feature`, `bugfix`, `refactor`. Label names should be short.
**Decision:** Map to conventional commit prefixes: `feature`→`feat`, `bugfix`→`fix`, `refactor`→`refactor`
**Rationale:** Aligns with the project's existing conventional commit convention. Three-letter labels are compact in GitHub's UI.

## Product Module Design

### Module: Issue Body Composition (in core/config-handling.md)
**Responsibility:** Define the deterministic template for composing `<IssueBody>` from spec artifacts
**Interface:** Referenced by the Issue Creation Protocol — agent reads requirements and spec.json, composes the body following the template
**Dependencies:** Requires `requirements.md`/`bugfix.md`/`refactor.md` and `spec.json` to already exist (guaranteed by Phase 2 ordering)

### Module: GitHub Label Protocol (in core/config-handling.md)
**Responsibility:** Define label categories, creation commands, and graceful degradation for non-GitHub trackers
**Interface:** Runs once per spec before first issue creation; labels applied via `--label` flags on `gh issue create`
**Dependencies:** `spec.json` for `id` and `type` fields; `gh` CLI for label creation

### Module: ISSUE_BODY_MARKERS (in generator/validate.py)
**Responsibility:** CI enforcement — verify Issue Body Composition and GitHub Label Protocol appear in all generated outputs
**Interface:** Array of marker strings checked by `check_markers_present()` and cross-platform loop
**Dependencies:** Generated platform output files

## Files to Modify

| File | Change Type | Description |
|------|------------|-------------|
| `core/config-handling.md` | Edit | Add Issue Body Composition subsection, GitHub Label Protocol subsection, update platform steps |
| `core/task-tracking.md` | Edit | Add cross-reference sentence to External Tracker Sync |
| `core/workflow.md` | Edit | Update Phase 2 step 6 wording |
| `generator/validate.py` | Edit | Add ISSUE_BODY_MARKERS, validation call, cross-platform entry |
| `tests/test_platform_consistency.py` | Edit | Add issue_body to REQUIRED_MARKERS |

## Testing Strategy
- `python3 generator/generate.py --all` — regenerate platform outputs with new config-handling content
- `python3 generator/validate.py` — new ISSUE_BODY_MARKERS pass for all 4 platforms
- `bash scripts/run-tests.sh` — full test suite passes
- Grep generated outputs for "Issue Body Composition" and "GitHub Label Protocol"

## Risks & Mitigations
- **Risk:** Marker strings in ISSUE_BODY_MARKERS don't match heading text in core/config-handling.md → **Mitigation:** Copy exact heading text into markers; validator catches mismatches
- **Risk:** `gh label create --force` not available in older gh versions → **Mitigation:** Graceful degradation already exists for CLI failures
