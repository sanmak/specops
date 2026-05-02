# Design: Depth Calibration System

## Architecture

The depth calibration system is implemented as inline additions to existing core modules rather than a new standalone module. This keeps the feature lightweight and avoids adding another module to the generator pipeline.

### Depth Assessment Algorithm

The complexity assessment runs at the end of Phase 1, after scope assessment (step 9.5) but before Phase 2 entry. It uses three signals already available at that point:

```
Signal 1: Estimated task count (from request analysis)
Signal 2: File domain breadth (count of distinct top-level directories in affected files)
Signal 3: New dependency presence (from request keywords: "install", "add dependency", package names)

IF task_count <= 2 AND domain_count <= 1 AND no_new_deps:
    depth = "lightweight"
ELIF task_count > 8 OR domain_count > 3 OR has_cross_domain_changes:
    depth = "deep"
ELSE:
    depth = "standard"

Cross-domain detection: if affected files span core/ AND (generator/ OR tests/ OR platforms/)
                        then cross_domain = true
```

### Depth Flag Persistence

The depth flag is stored in two places:
1. `implementation.md` Phase 1 Context Summary as `- Depth: <flag> [computed | user override]`
2. `spec.json` as `"depth": "<flag>"` (string enum: "lightweight", "standard", "deep")

### Conditional Step Behavior Matrix

Each affected workflow step checks the depth flag and adjusts behavior:

| Step | Location | Lightweight | Standard | Deep |
|---|---|---|---|---|
| Repo map refresh (1 step 3.5) | `core/workflow.md` | Skip (use existing) | Use if exists | Force refresh |
| Scope assessment (1 step 9.5) | `core/workflow.md` | Pass trivially | Run normally | Run + initiative check |
| Spec evaluation (2 step 6.85) | `core/workflow.md` | Skip | 1 iteration max | Up to maxIterations |
| Impl evaluation (4A) | `core/workflow.md` | AC check only | Full 4-dimension | Full + per-task if >5 tasks |
| Dependency gate (2 step 5.8) | `core/workflow.md` | Skip if no new deps | Run normally | Run + extended analysis |

### User Override Detection

In Phase 1 step 6 (request analysis), scan the user's request for depth keywords:

- `lightweight` keywords: "quick", "lightweight", "simple", "trivial", "minor"
- `deep` keywords: "thorough", "deep", "deep dive", "exhaustive", "comprehensive"

If detected, override the computed depth. Record as user override in implementation.md.

### Dispatcher Integration

In `core/dispatcher.md`, the Shared Context Block already passes config and steering context. Add the depth flag to this block so dispatched modes can read it. The depth is computed during Phase 1 in the spec mode, so the dispatcher itself does not compute it -- it passes through the value set during Phase 1.

### Config Schema Extension

Add `depth` field to `spec-schema.json` (the per-spec schema), not to `schema.json` (the project config schema). The depth is per-spec metadata, not project configuration:

```json
"depth": {
  "type": "string",
  "enum": ["lightweight", "standard", "deep"],
  "description": "Complexity depth flag computed during Phase 1"
}
```

### Files Modified

| File | Change |
|---|---|
| `core/workflow.md` | Add depth assessment step (9.7), add conditional behavior to steps 3.5, 9.5, 6.85, Phase 4A |
| `core/dispatcher.md` | Pass depth flag in Shared Context Block |
| `core/config-handling.md` | Document depth flag in spec.json structure |
| `spec-schema.json` | Add `depth` field to spec schema |
| `generator/generate.py` | No change needed (workflow.md already included) |
| `generator/validate.py` | Add DEPTH_MARKERS for validation |

### Dependency Decisions

No new external dependencies required.
