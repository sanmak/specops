# Design: Enforcement Roadmap — Advisory Context to Deterministic Enforcement

## Architecture Overview
This spec converts advisory behavioral mechanisms into deterministic enforcement using three proven approaches: (A) validate.py / CI gates for generated output checks, (B) file-persisted state for runtime enforcement, and (C) phase gate checklists for workflow transitions. A new spec artifact linter script provides runtime validation of spec files that validate.py (which checks generated platform outputs) cannot cover.

## Technical Decisions

### Decision 1: Enforcement Approach Selection
**Context:** 35 behavioral mechanisms exist; ~5 are enforced, ~26 are advisory. Need to select the right enforcement approach for each.
**Options Considered:**
1. Enforce everything via validate.py markers — Pros: deterministic CI gate; Cons: validate.py checks generated output, not runtime spec artifacts
2. Enforce everything via workflow language ("MUST", "protocol breach") — Pros: simple; Cons: mixed results for multi-step sequences (dogfood evidence)
3. Tiered approach matching enforcement mechanism to failure type — Pros: uses proven patterns where they work; Cons: more complex implementation

**Decision:** Option 3 — Tiered enforcement
**Rationale:** Dogfood evidence shows: validate.py markers have zero gaps for output checks, file-persisted state machines have zero gaps for runtime enforcement, and mandatory checklists have zero gaps for phase transitions. Match each mechanism to the proven pattern that fits its failure mode.

### Decision 2: Spec Artifact Linter as Separate Script
**Context:** Need to validate spec artifacts (tasks.md, implementation.md, spec.json) — these are runtime files, not generated platform outputs.
**Options Considered:**
1. Extend validate.py — Pros: single validation tool; Cons: validate.py checks generated files in platforms/, mixing concerns
2. New script `scripts/lint-spec-artifacts.py` — Pros: clean separation, conditional on specsDir existence; Cons: another script to maintain

**Decision:** Option 2 — Separate `scripts/lint-spec-artifacts.py`
**Rationale:** validate.py validates the generator pipeline (core → platforms). Spec artifacts are user-project files with different validation rules. Separation keeps each script focused and allows the linter to run conditionally only when a specsDir exists.

### Decision 3: Advisory Tier Preserved
**Context:** ~11 mechanisms are judgment-based with no machine-verifiable criterion.
**Decision:** Keep advisory — no enforcement
**Rationale:** Simplicity principle, communication style, high autonomy mode, memory heuristics, codebase exploration, team conventions, data handling, custom templates, integration references, EARS notation, and interview answers all require human judgment. Forcing enforcement would create false positives or meaningless gates.

## Component Design

### Component 1: Spec Artifact Linter (`scripts/lint-spec-artifacts.py`)
**Responsibility:** Validate spec artifacts in `<specsDir>/` for:
- Checkbox staleness: completed tasks with unchecked items (excluding Deferred Criteria subsections)
- Documentation Review: completed specs must have `## Documentation Review` in implementation.md
- Version validation: `specopsCreatedWith`/`specopsUpdatedWith` must match semver pattern or be absent

**Interface:** `python3 scripts/lint-spec-artifacts.py [specsDir]` (defaults to `.specops`)
**Dependencies:** Standard library only (no pip dependencies). Uses `re`, `json`, `os`, `sys`, `glob`.

### Component 2: Phase 1 Context Summary (workflow gate)
**Responsibility:** Enforce that Phase 1 steps 3, 3.5, 4 execute by requiring their output in implementation.md
**Interface:** New `## Phase 1 Context Summary` section template in `core/templates/implementation.md`. Workflow instruction in `core/workflow.md` Phase 1 requiring the section be written before Phase 2.

### Component 3: Phase 4 Documentation Review (workflow gate)
**Responsibility:** Enforce that documentation check executes by requiring `## Documentation Review` in implementation.md
**Interface:** Workflow instruction in `core/workflow.md` Phase 4 requiring the section be written. Linter validates presence for completed specs.

### Component 4: Config-to-Workflow Annotations
**Responsibility:** Make config → workflow bindings explicit and auditable
**Interface:** `### Workflow Impact` subsections in `core/config-handling.md` per config value. Explicit conditionals in `core/workflow.md`.

### Component 5: Coherence Verification (Phase 2 gate)
**Responsibility:** Cross-check NFRs against functional requirements after spec generation
**Interface:** New step at end of Phase 2 in `core/workflow.md`. COHERENCE_MARKERS in `generator/validate.py`.

### Component 6: Pre-Task Anchoring (task-tracking enhancement)
**Responsibility:** Anchor task scope before implementation to enable meaningful pivot checks
**Interface:** New step in `core/task-tracking.md` before In Progress transition. Post-task comparison against anchored scope.

### Component 7: Vertical Vocabulary Verification (verticals enhancement)
**Responsibility:** Verify vertical-specific vocabulary was applied after Phase 2 generation
**Interface:** New verification step in `core/verticals.md`. Result recorded in Context Summary.

## Sequence Diagrams

### Flow 1: Spec Artifact Linting
```
Linter -> specsDir: scan for spec directories
specsDir -> Linter: list of spec directories
Linter -> tasks.md: parse task statuses and checkboxes
Linter -> implementation.md: check for Documentation Review section
Linter -> spec.json: validate version fields
Linter -> stdout: report errors/warnings/pass
```

### Flow 2: Phase 1 Context Summary Gate
```
Agent -> config: load .specops.json
Agent -> steering: load steering files
Agent -> repo-map: check/refresh repo map
Agent -> memory: load memory layer
Agent -> implementation.md: WRITE Phase 1 Context Summary
Agent -> Phase 2: proceed (gate passed)
```

## Testing Strategy
- **Linter tests:** Run `scripts/lint-spec-artifacts.py` against all 9 existing completed dogfood specs — expect zero errors
- **Validation tests:** Run `python3 generator/validate.py` — new COHERENCE_MARKERS pass
- **Platform consistency:** Run `python3 tests/test_platform_consistency.py` — new markers present across all 4 platforms
- **Build test:** Run `python3 tests/test_build.py` — generator produces valid outputs with new content
- **Full suite:** `bash scripts/run-tests.sh` — all tests pass

## Risks & Mitigations
- **Risk 1:** New workflow gates increase agent instruction length, potentially causing context window pressure → **Mitigation:** Keep gate instructions concise; use imperative single-line instructions, not explanatory paragraphs
- **Risk 2:** COHERENCE_MARKERS may not be present in all generated outputs if the Coherence Verification section is not added to all platform templates → **Mitigation:** Add to core/workflow.md (which flows to all platforms via generator), verify with cross-platform consistency check
- **Risk 3:** Spec artifact linter may false-positive on edge cases (e.g., tasks with no acceptance criteria) → **Mitigation:** Only lint tasks explicitly marked Completed; skip tasks without Acceptance Criteria sections
