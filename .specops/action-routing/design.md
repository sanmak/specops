# Action Routing -- Design

## Architecture Overview

Action routing is a classification layer that sits between finding aggregation (from the adversarial evaluator + multi-persona review) and remediation dispatch (Phase 4B). It does not add new evaluation passes or sub-agent dispatches -- it classifies existing findings into fix classes and orchestrates remediation accordingly.

```
Phase 4A Flow (updated):
  1. Adversarial evaluator (existing) --> dimension scores + findings
  2. Multi-persona review (existing) --> persona findings
  3. Finding aggregation (existing) --> unified finding list
  4. Action routing (new) --> classified findings with fix classes
  5. Combined verdict (existing) --> PASS/FAIL

Phase 4B Flow (updated):
  1. Separate findings by fix class
  2. Execute auto_fix items (immediate, no interaction)
  3. If auto_fix failures: reclassify as gated_fix
  4. Present gated_fix batch for approval (or auto-apply on non-interactive)
  5. Report manual items (no fix attempted)
  6. Report advisory items (informational)
  7. Re-evaluate (existing)
```

## Design: Action Routing in core/evaluation.md

Action routing is added as a new subsection within `core/evaluation.md` rather than a separate module. Rationale: it is tightly coupled to the evaluation finding format and remediation loop -- it classifies evaluation findings and changes remediation behavior. Creating a separate module would require extensive cross-referencing for a relatively contained feature.

### Section: Action Routing for Findings

New subsection after "### Multi-Persona Review Integration" in `core/evaluation.md`:

**Content:**
1. Fix class definitions (auto_fix, gated_fix, manual, advisory)
2. Routing signal definitions (determinism, scope, risk)
3. Decision matrix
4. Override rules (LOW confidence, P3 severity)
5. Routing procedure (step-by-step classification algorithm)
6. Remediation flow update (auto-fix execution, gated batching, manual reporting)

### Section: Updated Remediation Flow

Update the existing "### Feedback Loop" section to incorporate action routing:

- Phase 4B remediation now separates findings by fix class before acting
- Auto-fix items are applied first, silently
- Gated items are batched for a single approval prompt
- Manual items are reported but not fixed
- Advisory items are noted but do not trigger any action

## Design: Pipeline Integration in core/pipeline.md

Add action routing awareness to the pipeline cycle:

- After evaluation in each cycle, classify findings using the action routing matrix
- Apply auto_fix items within the cycle without stopping
- On non-interactive platforms, also apply gated_fix items
- On interactive platforms, batch gated items for approval between cycles
- Manual and advisory items are reported at cycle end

## Design: Evaluation Template Update

Update `core/templates/evaluation.md`:

1. Add `Fix Class` column to the implementation evaluation findings detail tables
2. Add `## Action Routing Summary` section after the Multi-Persona Review section

Template addition:
```markdown
## Action Routing Summary

| Fix Class | Count | Findings |
| --- | --- | --- |
| auto_fix | [N] | [finding IDs] |
| gated_fix | [N] | [finding IDs] |
| manual | [N] | [finding IDs] |
| advisory | [N] | [finding IDs] |

### Auto-Fix Results
<!-- For each auto_fix finding: applied successfully / failed and reclassified -->

### Gated Fix Batch
<!-- For each gated_fix finding: proposed change summary, approval status -->

### Manual Findings
<!-- For each manual finding: reported to developer -->
```

## Files Modified

| File | Change Type | Description |
| --- | --- | --- |
| `core/evaluation.md` | Modify | Add action routing subsection (fix classes, decision matrix, routing procedure, updated remediation flow) |
| `core/pipeline.md` | Modify | Add action routing awareness to pipeline cycle remediation |
| `core/templates/evaluation.md` | Modify | Add Fix Class column and Action Routing Summary section |
| `generator/validate.py` | Modify | Add ACTION_ROUTING_MARKERS constant, add to validate_platform() and cross-platform loop |
| `tests/test_platform_consistency.py` | Modify | Import ACTION_ROUTING_MARKERS |
| `platforms/*/` | Regenerated | All 5 platform outputs regenerated |
| `CHECKSUMS.sha256` | Regenerated | Updated checksums for modified files |

## Design Decisions

### D1: Extend evaluation.md vs New Module
**Decision**: Add action routing as a subsection of `core/evaluation.md` rather than creating a new `core/action-routing.md` module.
**Rationale**: Action routing is a classification step within the evaluation flow, not a standalone feature. It operates on evaluation findings and modifies remediation behavior. A separate module would require a new entry in generate.py, all 5 Jinja2 templates, mode-manifest.json, and validate.py -- significant overhead for what is essentially a subsection of evaluation logic. The multi-persona-review spec created a separate module because it introduced entirely new personas and prompts; action routing only adds a classification matrix and remediation flow changes.

### D2: Deterministic Matrix vs LLM Classification
**Decision**: Use a deterministic decision matrix rather than asking the LLM to classify findings.
**Rationale**: LLM classification would be non-deterministic -- the same finding might get different fix classes in different runs. A matrix based on observable signals (determinism, scope, risk) produces consistent results. The routing signals are assessed by the evaluation logic that already understands the finding context.

### D3: Auto-Fix Failure Reclassification
**Decision**: Failed auto-fixes are reclassified as `gated_fix`, not `manual`.
**Rationale**: If the fix was deterministic enough to attempt auto-fix but the application failed (e.g., conflicting edit), the fix is still deterministic -- it just needs human oversight. Escalating to `manual` would lose the proposed fix entirely. `gated_fix` preserves the fix proposal while adding the developer approval gate.

### D4: Non-Interactive Platforms Auto-Apply Gated Fixes
**Decision**: On platforms where `canAskInteractive` is false, treat `gated_fix` as `auto_fix`.
**Rationale**: Non-interactive platforms have no mechanism for batch approval. The finding was already classified as having a deterministic fix -- the only reason it was gated was scope or moderate risk. On non-interactive platforms, applying the fix is better than leaving it unresolved (the developer can review the changes in the git diff).

### D5: No Config Switch for Action Routing
**Decision**: Action routing is always active when evaluation is enabled. No separate `config.implementation.evaluation.actionRouting` switch.
**Rationale**: Action routing improves the remediation experience for all users. Making it optional would add configuration complexity and require testing both code paths. Following the same pattern as confidence-gating and multi-persona review -- these are always-on quality improvements.
