# Design: Proxy Metrics Tracking

## Architecture Overview
Proxy metrics follows the established 3-layer pattern: a new `core/metrics.md` module defines the collection procedure using abstract operations, the generator pipeline includes it via `build_common_context()`, and all 4 platform templates render it with tool-substituted language. The metrics object is stored in `spec.json` as an optional field validated by `spec-schema.json`.

## Technical Decisions

### Decision 1: Proxy Metrics vs Actual Token Counting
**Context:** None of the 4 supported platforms expose token-counting APIs to custom instructions.
**Options Considered:**
1. Proxy metrics (deterministic output measurements) — reliable, multi-platform, no API dependency
2. Character-based estimation engine — fully automated but risk of inaccurate numbers
3. User-reported manual input — accurate but depends on user discipline

**Decision:** Option 1 — Proxy metrics
**Rationale:** Deterministic measurements are trustworthy and platform-agnostic. Inaccurate automated estimates would hurt adoption more than having no numbers.

### Decision 2: Sub-step Notation (step 2.5) vs Renumbering
**Context:** Inserting a new step in Phase 4 would break cross-references in `workflow.md` and `memory.md`.
**Options Considered:**
1. Renumber steps 3-8 → 4-9 and update all cross-references
2. Use sub-step notation (step 2.5) as established by 4 prior specs

**Decision:** Option 2 — Sub-step notation
**Rationale:** Project memory pattern "step numbering" (4 recurrences) established this convention. Cross-references to steps 3, 4, 5 exist in both workflow.md and memory.md.

### Decision 3: Metrics Placement in Phase 4
**Context:** Metrics must be captured after acceptance criteria verification (for accurate counts) but before the completion status update.
**Decision:** Step 2.5 — after finalizing implementation.md (step 2), before memory update (step 3)
**Rationale:** Acceptance criteria are checked in step 1, so counts are accurate. Memory update in step 3 can reference metrics if desired.

## Product Module Design

### Module: core/metrics.md
**Responsibility:** Defines the 6-step metrics capture procedure using abstract operations
**Interface:** READ_FILE, RUN_COMMAND, EDIT_FILE abstract ops
**Dependencies:** core/tool-abstraction.md (abstract ops), spec-schema.json (metrics schema)

### Module: spec-schema.json (extension)
**Responsibility:** Validates the optional `metrics` object in spec.json
**Interface:** JSON Schema validation
**Dependencies:** None (self-contained schema)

## System Flow

```
Phase 4 step 1 (verify criteria) → step 2 (finalize impl.md)
  → step 2.5 (capture metrics):
      READ_FILE spec artifacts → count chars → specArtifactTokensEstimate
      RUN_COMMAND git diff --stat → filesChanged, linesAdded, linesRemoved
      Parse tasks.md → tasksCompleted, acceptanceCriteriaVerified
      Compute timestamps → specDurationMinutes
      EDIT_FILE spec.json → add metrics object
  → step 3 (memory update) → step 4 (docs check) → step 5 (completion gate)
```

## Integration Points
- Generator pipeline: `build_common_context()` in `generator/generate.py`
- Validation: `METRICS_MARKERS` in `generator/validate.py`
- Tests: `tests/test_spec_schema.py`, `tests/test_platform_consistency.py`

## Ship Plan
1. Schema + core module (foundation)
2. Workflow integration + generator pipeline (wiring)
3. Validation + tests (verification)
4. Documentation (adoption)
5. Regenerate + validate (release gate)

## Risks & Mitigations
- **Risk:** Git diff may include changes from other work if spec branch is not isolated → **Mitigation:** Documented in Metrics Safety section; proxy metrics are explicitly labeled as estimates
- **Risk:** Duration includes idle time between sessions → **Mitigation:** Documented as wall-clock time, not active time
