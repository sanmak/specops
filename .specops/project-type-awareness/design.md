# Design: Project-Type-Aware Workflow

## Architecture Overview
Five targeted changes across existing core modules. No new core modules — all changes fit within `core/workflow.md`, `core/init.md`, and `core/verticals.md`. The migration vertical follows the established vertical pattern (additive section in verticals.md + schema enum + validator markers). Greenfield/brownfield detection is behavioral logic within existing workflow steps, using sub-step notation (7.5, 1.5, 4.7) to avoid renumbering.

## Technical Decisions

### Decision 1: Sub-Step Numbering
**Context:** Need to insert new steps into workflow.md and init.md without breaking cross-module references
**Options Considered:**
1. Renumber all steps — Breaks references in memory.md (step 4), steering.md (step 3), task-tracking.md
2. Sub-step notation (1.5, 7.5, 4.7) — Preserves all existing references
**Decision:** Sub-step notation
**Rationale:** Recurring pattern from 3 prior specs (ast-based-repo-map, enforcement-roadmap, drift-detection). Memory pattern: "Avoid renumbering Phase steps when inserting new logic."

### Decision 2: No New Validator Markers for Greenfield/Brownfield
**Context:** Greenfield detection and brownfield assisted steering are behavioral modifications within existing modules, not new modules
**Options Considered:**
1. Add GREENFIELD_MARKERS and INIT_MARKERS — Creates validation surface for behavioral content
2. No new markers — Greenfield/brownfield text appears in generated outputs naturally through existing workflow/init modules
**Decision:** No new markers for greenfield/brownfield, only add `"### migration"` to VERTICAL_MARKERS
**Rationale:** Validator markers exist for new *modules* that must appear in all platforms. Greenfield/brownfield are behavioral branches within existing workflow.md and init.md modules that are already validated by WORKFLOW_MARKERS and init checks.

### Decision 3: Greenfield Detection Heuristic
**Context:** Need a simple way to detect greenfield projects without complex analysis
**Decision:** Count source code files (excluding standard excludes) — ≤ 5 is greenfield
**Rationale:** Most new projects start with only package.json, README.md, .gitignore, maybe a tsconfig.json. This heuristic is confirmed with the user during init and overridable at runtime (step 7.5). It's a behavioral adaptation, not a gate — the user can always override.

### Decision 4: Migration as Vertical, Not Spec Type
**Context:** Migration could be a new spec type (alongside feature/bugfix/refactor) or a vertical adaptation
**Options Considered:**
1. New spec type with migration-specific template files
2. Vertical adaptation of existing feature template
**Decision:** Vertical adaptation
**Rationale:** Follows the established pattern — all other domain specializations (infrastructure, data, library, builder) are verticals, not spec types. A migration spec uses the same structure as a feature spec with renamed sections and added migration-specific content. No new template files needed.

## Product Module Design

### Module 1: Auto-Init Suggestion (workflow.md)
**Responsibility:** Detect missing `.specops.json` and offer init before proceeding
**Change location:** `core/workflow.md` step 1 (line 19)
**Logic:** After the config read attempt, if `.specops.json` does not exist, ASK_USER offering init or defaults. This is a 4-line behavioral addition to the existing step.

### Module 2: Project Type Detection (init.md)
**Responsibility:** Scan repo state and classify as greenfield/brownfield, with migration override
**Change location:** `core/init.md` — new Step 1.5 between Step 1 (line 20) and Step 2 (line 22)
**Logic:**
1. LIST_DIR(`.`) excluding standard directories, count source files
2. Check FILE_EXISTS for docs (README.md, CONTRIBUTING.md) and dependency manifests
3. Classify: ≤ 5 source files → greenfield, else brownfield
4. ASK_USER to confirm with Greenfield/Brownfield/Migration options
5. Store result for downstream steps (template pre-selection, assisted steering trigger)

### Module 3: Greenfield Adaptive Phase 1 (workflow.md)
**Responsibility:** Skip hollow codebase exploration on empty repos, propose structure, auto-populate steering
**Change location:** `core/workflow.md` — new step 7.5 between step 7 (line 54) and step 8 (line 55)
**Logic:**
1. LIST_DIR(`.`) and count source files (same heuristic as init detection)
2. If greenfield: execute steps 8g (propose structure) and 9g (auto-populate steering from conversation)
3. If not greenfield: proceed with original steps 8-9
4. Steps 8-9 get conditional labels: "(Brownfield/migration only)"

### Module 4: Brownfield Assisted Steering (init.md)
**Responsibility:** Auto-populate empty steering files from existing project documentation during init
**Change location:** `core/init.md` — new Step 4.7 after Step 4.6 (line 79)
**Logic:**
1. Only runs when confirmed project type is brownfield
2. For product.md: extract from README.md overview/features
3. For tech.md: extract from package.json/pyproject.toml/Cargo.toml/go.mod dependencies
4. For structure.md: extract from top-level directory listing
5. Only populates files still containing placeholder text

### Module 5: Migration Vertical (verticals.md)
**Responsibility:** Domain vocabulary and template adaptations for migration/re-platforming work
**Change location:** `core/verticals.md` — new `### migration` section after `### builder` (line 51)
**Logic:** Pure additive vertical following the established pattern. Domain vocabulary, requirements.md adaptations, design.md adaptations, tasks.md adaptations, vocabulary verification entry.

## Integration Points

| Change | Touches | Reason |
|--------|---------|--------|
| Migration vertical | `schema.json` | Add "migration" to vertical enum |
| Migration vertical | `generator/validate.py` | Add "### migration" to VERTICAL_MARKERS |
| Migration vertical | `tests/test_platform_consistency.py` | Add "### migration" to verticals markers |
| Migration keywords | `core/workflow.md` step 7 | Add migration keyword list |
| Project state line | `core/templates/implementation.md` | Add project state to context summary |
| All changes | `platforms/*/` | Regenerated by generator |

## Ship Plan
1. Implement migration vertical first (smallest, validates the pipeline)
2. Add auto-init suggestion to workflow.md
3. Add project type detection to init.md
4. Add brownfield assisted steering to init.md
5. Add greenfield adaptive Phase 1 to workflow.md
6. Regenerate all platforms and validate
7. Run full test suite

## Risks & Mitigations
- **Risk:** Greenfield heuristic (≤ 5 files) may misclassify repos with only scaffold — **Mitigation:** User confirms during init; runtime detection is overridable
- **Risk:** Brownfield README parsing may extract irrelevant content — **Mitigation:** Only populates files with placeholder text; user is notified to review
- **Risk:** Migration vertical missing from cross-platform consistency check — **Mitigation:** Memory pattern enforced: add to BOTH per-platform AND cross-platform in same commit
