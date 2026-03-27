# Design: Adversarial Evaluation System

## Architecture Overview

The adversarial evaluation system adds two evaluation touchpoints to the SpecOps workflow without changing the 4-phase numbering. Both touchpoints use structurally separated agent contexts with hardcoded skepticism prompting, scored quality dimensions, and feedback loops.

**Touchpoint 1 -- Spec Evaluation**: A Phase 2 exit gate between spec generation and implementation. Evaluates spec artifact quality (criteria testability, completeness, design coherence, task coverage) before Phase 3 begins.

**Touchpoint 2 -- Implementation Evaluation**: Phase 4 restructured into sub-phases 4A (evaluate), 4B (remediate), 4C (complete). Phase 4A uses a fresh agent context to adversarially score implementation quality against spec-type-specific dimensions.

Both touchpoints share the same scoring rubric (1-10), threshold logic, and feedback loop mechanics. Configuration lives under `implementation.evaluation` in `.specops.json`.

## Architecture Decisions

### Decision 1: Restructure Phase 4 into 4A/4B/4C sub-phases (not add a 5th phase)

**Context:** The evaluation system needs a place in the workflow. Options were: add Phase 3.5, add Phase 5, restructure Phase 4, or create a standalone `/specops evaluate` mode.

**Options Considered:**
1. Add Phase 3.5 or Phase 5 -- new phase number
2. Restructure Phase 4 into sub-phases -- internal restructuring
3. Standalone `/specops evaluate` mode -- manual invocation

**Decision:** Restructure Phase 4 into 4A/4B/4C sub-phases.

**Rationale:**
- `WORKFLOW_MARKERS` in `validate.py` validate Phase 1-4 headings -- adding phases would break markers or require awkward naming
- Phase 4 already dispatches to a fresh sub-agent on Claude (`canDelegateTask: true`) -- making that context adversarial is a natural extension
- Pipeline mode already cycles Phase 3 to Phase 4 -- evaluation inside Phase 4 composes naturally with the existing cycle
- A standalone mode would make evaluation optional and manual -- agents and users would skip it, defeating the purpose

### Decision 2: Spec evaluation as Phase 2 exit gate (not a new phase)

**Context:** Pre-implementation spec quality review needs a place in the workflow. Options were: new Phase 2.5, Phase 2 exit gate, or Phase 3 entry gate.

**Options Considered:**
1. New Phase 2.5 -- explicit sub-phase for spec evaluation
2. Phase 2 exit gate -- evaluation runs at the Phase 2 to Phase 3 dispatch boundary
3. Phase 3 entry gate -- evaluation runs as the first step of Phase 3

**Decision:** Phase 2 exit gate at the dispatch boundary.

**Rationale:**
- Phase 2.5 already exists for spec review (when `specReview.enabled`) -- spec evaluation is conceptually similar (a quality gate before implementation)
- Placing it at the dispatch boundary means it runs after Phase 2 Completion Summary is written but before Phase 3 dispatch, which is the natural chokepoint
- Phase 3 entry gate would mix evaluation logic into the implementation phase, muddying the separation of concerns

### Decision 3: Hardcoded adversarial prompts (not configurable)

**Context:** The evaluator's skepticism prompt is the core mechanism that makes evaluation adversarial. Making it configurable via `.specops.json` would let users weaken or disable the adversarial nature.

**Decision:** Adversarial prompts are hardcoded in `core/evaluation.md` and cannot be overridden via configuration.

**Rationale:** The article demonstrates that tuning a standalone evaluator to be skeptical is the key lever. If users can configure the prompt to be lenient, the entire system loses its value. The scoring threshold (`minScore`) provides sufficient flexibility without compromising the adversarial nature.

### Decision 4: Enabled by default

**Context:** Evaluation could be opt-in (disabled by default) or opt-out (enabled by default).

**Decision:** Enabled by default (`evaluation.enabled: true`).

**Rationale:** The goal is to make SpecOps a dependable quality guarantee. If evaluation is opt-in, most users will never turn it on. Enabling by default ensures every spec benefits from adversarial evaluation. Users who want to skip it for a specific project can set `enabled: false`. The cost (1 extra agent dispatch per evaluation touchpoint) is justified by the quality lift.

### Decision 5: Evaluation artifact structure

**Context:** Evaluation results need to be stored for both human review and machine consumption.

**Decision:** Dual storage: `evaluation.md` (human-readable report with iteration history) and `spec.json` `evaluation` field (machine-readable scores).

**Rationale:**
- `evaluation.md` serves as the audit trail -- iteration history is appended, not overwritten, so the full evaluation journey is preserved
- `spec.json` `evaluation` field enables downstream tooling (dashboards, CI gates, reporting) to consume evaluation results programmatically
- Both `spec` and `implementation` sub-objects are stored separately since they measure different things at different times

### Decision 6: Per-spec evaluation default (not per-task)

**Context:** Evaluation could run after each task (per-task) or after all tasks complete (per-spec).

**Decision:** Per-spec evaluation by default. Per-task evaluation available via `perTask: true` config.

**Rationale:** The article's V2 harness (with Opus 4.6) removed per-sprint evaluation in favor of single-pass, noting that better models make single-pass sufficient for most tasks. Per-task evaluation multiplies context switches and agent dispatches. Per-spec is the right default; `perTask: true` is available for high-stakes specs.

### Decision 7: New core module `core/evaluation.md`

**Context:** The evaluation protocol, dimensions, scoring rubric, feedback loops, platform adaptation, and safety rules need a home.

**Decision:** Single new core module `core/evaluation.md` containing all evaluation logic. Added to `spec` and `pipeline` modes in `core/mode-manifest.json`.

**Rationale:**
- Follows the existing pattern of one module per concern (like `core/safety.md`, `core/decomposition.md`)
- Single module keeps the evaluation system cohesive and discoverable
- Added to both `spec` and `pipeline` modes since both need evaluation capabilities

## Integration Points

| Integration Point | Mechanism |
|-------------------|-----------|
| Phase 2 exit gate | `core/workflow.md` Phase 2 dispatch boundary -- evaluation runs between Completion Summary and Phase 3 dispatch |
| Phase 4A/4B/4C | `core/workflow.md` Phase 4 restructured -- evaluation replaces checkbox verification |
| Dispatcher | `core/dispatcher.md` handles evaluation dispatch at both boundaries and remediation re-dispatch |
| Pipeline mode | `core/pipeline.md` uses evaluation scores as pass/fail signal when enabled |
| Config | `schema.json` adds `implementation.evaluation` schema; `core/config-handling.md` adds defaults |
| Validation | `generator/validate.py` adds `EVALUATION_MARKERS`; cross-platform consistency enforced |
| Generator | `generator/generate.py` adds `evaluation` to `build_common_context()`; all 5 Jinja2 templates include `{{ evaluation }}` |

## Security Considerations

- Evaluator runs in read-only mode (cannot modify implementation code)
- Evaluator cannot mark spec as completed (only Phase 4C can)
- Evaluator cannot change acceptance criteria checkboxes (Phase 4C responsibility)
- Adversarial prompts cannot be overridden via config (prevents weakening)
- Evaluation.md appends iterations (prevents history tampering)
- Path containment rules apply to all evaluation file operations
