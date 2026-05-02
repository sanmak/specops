# Design: Solution Exploration Mode

## Overview

Solution Exploration mode adds a new "explore" mode to SpecOps that sits between interview (convergent idea refinement) and spec (committed design). When a developer knows the problem but not the approach, explore mode generates 3-5 codebase-grounded solution approaches with tradeoff analysis. The user selects an approach, which flows into Phase 2 as a pre-populated design direction.

## Architecture

### New Core Module: `core/explore.md`

The explore module defines:

1. **Explore Mode Detection** -- trigger patterns and disambiguation rules
2. **Explore Workflow** -- a state machine: `loading -> generating -> presenting -> selected`
3. **Approach Generation** -- how to produce codebase-grounded approaches
4. **Approach Format** -- the structured output for each approach
5. **Selection Flow** -- how the selected approach feeds into Phase 2
6. **Platform Adaptation** -- interactive vs non-interactive behavior

### Explore Workflow State Machine

```
loading -> generating -> presenting -> selected -> (exits to Phase 2)
                                    -> more_options -> generating (loop)
```

**Phase: Loading**
1. Load project context: repo map, steering files, memory
2. Parse the user's problem statement
3. Determine depth flag influence on approach count

**Phase: Generating**
1. Analyze the problem against the codebase structure
2. Generate approaches (count based on depth: lightweight=2-3, standard=3-4, deep=4-5)
3. Each approach must reference at least 2 real files from the repo map

**Phase: Presenting**
1. Display approaches in structured format
2. Interactive: ask user to select, request more options, or refine problem
3. Non-interactive: output all approaches and exit

**Phase: Selected**
1. Package the selected approach as a design direction
2. Flow into Phase 2 with the approach as pre-populated context

### Approach Format

Each approach is presented with:

```
### Approach N: [Name]

**Description:** [1-2 sentence summary of the approach]

**Key Files to Modify:**
- `path/to/file1.ext` -- [what changes and why]
- `path/to/file2.ext` -- [what changes and why]

**Tradeoff Analysis:**
| Factor | Assessment |
| --- | --- |
| Pros | [list of advantages] |
| Cons | [list of disadvantages] |
| Complexity | Low / Medium / High |
| Risk | Low / Medium / High |

**Implementation Sketch:** [2-3 sentence high-level implementation approach]
```

### Dispatcher Integration

New entry in the Mode Router table at step 11.75 (between initiative at 11.5 and interview at 12):

| Step | Mode | Detection Patterns | Disambiguation |
| --- | --- | --- | --- |
| 11.75 | **explore** | "explore", "explore options", "what are my options", "solution options", "approaches for", "how should I", "what's the best way to" | Must co-occur with a problem description. Bare "explore" with no context routes to explore mode which will ask for the problem. "explore the codebase" is NOT explore mode (that is map mode). |

### Mode Manifest Registration

```json
{
  "explore": {
    "description": "Generate codebase-grounded solution approaches for a known problem",
    "modules": ["explore", "config-handling", "repo-map", "steering", "memory"],
    "templates": []
  }
}
```

### Generator Pipeline Integration

1. **generate.py**: Add `explore` to `build_common_context()` as `core["explore"]`
2. **validate.py**: Add `EXPLORE_MARKERS` constant with key markers from `core/explore.md`; add to `validate_platform()` and cross-platform consistency loop; import in `test_platform_consistency.py`
3. **Claude mode generation**: Handled automatically by `generate_claude_modes()` since explore is registered in `mode-manifest.json`
4. **Validator mode count**: Update expected mode count from 15 to 16 in `validate_claude_dispatcher()`

### Phase 2 Handoff

When the user selects an approach, the explore mode constructs a handoff context:

```
## Explore Mode Selection

**Problem:** [original problem statement]
**Selected Approach:** [approach name]
**Approach Description:** [description]
**Key Files:** [file list]
**Tradeoff Summary:** [pros/cons summary]
```

This context is passed to the spec mode as enriched input, similar to how interview mode produces an enriched request description. The spec mode's Phase 2 uses this as design direction guidance (not a rigid constraint).

## Files Changed

| File | Change |
| --- | --- |
| `core/explore.md` | New file -- explore mode module |
| `core/dispatcher.md` | Add explore mode to Mode Router table |
| `core/mode-manifest.json` | Register explore mode with required modules |
| `generator/generate.py` | Add explore to `build_common_context()` |
| `generator/validate.py` | Add `EXPLORE_MARKERS`, validate in `validate_platform()` and consistency loop |
| `tests/test_platform_consistency.py` | Import `EXPLORE_MARKERS` and add to `REQUIRED_MARKERS` |
| `docs/STRUCTURE.md` | Add `core/explore.md` to directory tree |
| `.claude/commands/docs-sync.md` | Add `core/explore.md` mapping |
| `CLAUDE.md` | Update core modules list |
| `.specops/index.json` | Register spec entry |

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Generated approaches are too generic | Require at least 2 real file references per approach from repo map |
| Mode count change breaks validator | Update expected count in `validate_claude_dispatcher()` |
| Explore mode confused with interview | Clear disambiguation in dispatcher: interview is for vague ideas, explore is for clear problems |
| Non-interactive platforms get no value | Output all approaches as a structured report they can review offline |
