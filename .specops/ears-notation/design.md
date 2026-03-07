# Design: EARS Notation for Requirements

## Architecture Overview

EARS notation is integrated at the template layer (`core/templates/`) and workflow instruction layer (`core/workflow.md`). No new modules or files are created — this is a template enhancement that flows through the existing generator pipeline to all platform outputs.

The change touches three layers:
1. **Templates** — add EARS sections to `feature-requirements.md` and `bugfix.md`
2. **Workflow** — add EARS generation instructions to Phase 2
3. **Generated outputs** — regenerated automatically via `generator/generate.py`

## Technical Decisions

### Decision 1: EARS Alongside Checkboxes, Not Replacing
**Context:** Should EARS replace checkbox acceptance criteria or supplement them?
**Options Considered:**
1. Replace checkboxes entirely — cleaner, but breaks mental model for users familiar with checkbox criteria
2. Add EARS section alongside checkboxes — more verbose, but backward compatible and lets users transition gradually
3. EARS as the primary format with optional checkbox shorthand — best of both worlds

**Decision:** Option 3 — EARS as primary format with checkboxes as optional shorthand
**Rationale:** EARS statements are the authoritative criteria. Checkboxes can optionally summarize them for progress tracking. This keeps specs lean (agents generate EARS, checkboxes are derived) while giving users the tracking UI they expect. The template shows EARS as the primary section; checkboxes are a "Progress Checklist" that maps 1:1 to EARS statements.

### Decision 2: Five EARS Patterns in Template Guidance
**Context:** EARS defines five requirement patterns. Should we teach agents all five or simplify?
**Options Considered:**
1. All five patterns with examples — comprehensive but adds template length
2. Only the two most common (Event-Driven, State-Driven) — simpler but loses precision for edge cases
3. All five patterns, concise — one-line format per pattern with inline examples

**Decision:** Option 3 — All five patterns, concise format
**Rationale:** Agents can select the right pattern contextually. One-line definitions with inline examples add minimal template bulk. Omitting patterns would reduce the quality of generated requirements.

### Decision 3: Bugfix Template Three-Category Testing
**Context:** How to structure the bugfix testing plan around EARS?
**Options Considered:**
1. Keep existing flat testing plan, add EARS to acceptance criteria only
2. Restructure testing into three explicit categories with EARS for each

**Decision:** Option 2 — Three-category testing structure
**Rationale:** The three categories (Current/Expected/Unchanged) are the core value of EARS for bugfixes. A flat testing plan doesn't distinguish between "test the fix" and "test nothing else broke." This structure makes regression prevention explicit.

## Product Module Design

### Module: EARS Template Enhancement (`core/templates/feature-requirements.md`)
**Responsibility:** Define the EARS acceptance criteria format for feature specs
**Changes:**
- Add "Acceptance Criteria (EARS)" subsection under each user story / product requirement
- Include five EARS patterns as inline guidance comments
- Keep "Progress Checklist" (checkboxes) as optional derived section

### Module: Bugfix EARS Enhancement (`core/templates/bugfix.md`)
**Responsibility:** Add regression protection via `SHALL CONTINUE TO`
**Changes:**
- Add "Unchanged Behavior" section after "Proposed Fix"
- Restructure "Testing Plan" into three categories
- Add EARS format guidance for each category

### Module: Workflow EARS Instructions (`core/workflow.md`)
**Responsibility:** Instruct agents to generate EARS criteria during Phase 2
**Changes:**
- Add EARS generation step to Phase 2, step 2 (when creating requirements.md)
- Reference the five patterns
- Instruct agent to match pattern to requirement type

## System Flow

```text
User Request
  → Phase 1: Understand (no EARS impact)
  → Phase 2: Create Spec
      → Agent reads feature-requirements template
      → Template includes EARS pattern guidance
      → Agent generates EARS-formatted acceptance criteria
      → Agent optionally generates progress checklist from EARS
      → Writes requirements.md with EARS sections
  → Phase 3: Implement (EARS criteria used as acceptance tests)
  → Phase 4: Complete (verify EARS criteria met)
```

## Integration Points

- **Generator pipeline**: No changes to `generator/generate.py` — templates are embedded in `core/` which the generator already includes
- **Vertical adaptations**: `core/verticals.md` already adapts section names per vertical. EARS guidance is in the template itself, so vertical renaming (e.g., "User Stories" → "Product Requirements") applies automatically
- **Platform outputs**: Regenerated via `python3 generator/generate.py --all` — no template changes needed in `generator/templates/*.j2`

## Security Considerations
- No security impact — this is a template change with no code execution
- EARS notation is plain text, no injection vectors

## Testing Strategy
- **Existing tests**: Run `bash scripts/run-tests.sh` — all must pass unchanged
- **Validation**: Run `python3 generator/validate.py` — must pass (templates are included in core content)
- **Platform consistency**: Run `python3 tests/test_platform_consistency.py` — all platforms must include EARS markers
- **Manual**: Generate a spec using the updated templates, verify EARS format appears

## Ship Plan
1. Update `core/templates/feature-requirements.md` with EARS sections
2. Update `core/templates/bugfix.md` with SHALL CONTINUE TO and three-category testing
3. Update `core/workflow.md` Phase 2 with EARS instructions
4. Regenerate all platform outputs
5. Run validation and tests
6. Verify a generated spec includes EARS criteria

## Risks & Mitigations
- **Risk:** EARS notation makes specs feel more formal/heavy for small features → **Mitigation:** Simplicity principle applies — agent should generate 2-3 EARS statements for small features, not exhaustive lists
- **Risk:** Platform outputs may not include EARS markers if core content isn't properly assembled → **Mitigation:** Validation step checks for EARS-related content in all outputs
