# Design: Local Memory Layer

## Architecture Overview
The Local Memory Layer adds a persistent memory directory (`<specsDir>/memory/`) containing three files that capture cross-session context. A new `core/memory.md` module defines loading behavior (Phase 1, step 3.5 — after steering files), writing behavior (Phase 4, step 2.5 — after implementation.md finalized), and a `/specops memory` subcommand. The module integrates into the generator pipeline following the same pattern as steering, reconciliation, and from-plan modules.

## Technical Decisions

### Decision 1: Convention-Based Directory Discovery
**Context:** Should the memory directory be configured in `.specops.json` or discovered by convention?
**Options Considered:**
1. Schema config (`"memory": { "enabled": true, "dir": "memory" }`) — explicit but adds config surface
2. Convention-based (`<specsDir>/memory/` existence) — simple, matches steering pattern

**Decision:** Convention-based (Option 2)
**Rationale:** Steering files established this pattern successfully. Directory existence is the trigger. No schema changes needed. Zero config for users.

### Decision 2: Three-File Storage Structure
**Context:** How to organize memory data?
**Options Considered:**
1. Single `memory.json` — everything in one file
2. Three files (`decisions.json`, `context.md`, `patterns.json`) — separated by concern
3. Per-spec memory files — memory fragments alongside each spec

**Decision:** Three files (Option 2)
**Rationale:** Separation of concerns: decisions are structured (JSON), context is human-readable narrative (markdown), patterns are derived aggregations (JSON). Users can read `context.md` directly without parsing JSON. Per-spec fragments would require aggregation at load time.

### Decision 3: Append-Only Decision Journal
**Context:** Should decisions.json be rewritten or appended?
**Options Considered:**
1. Full rewrite on each Phase 4 — simple but loses ordering fidelity
2. Append new entries with deduplication by spec+decision number — preserves history

**Decision:** Append with deduplication (Option 2)
**Rationale:** Decisions accumulate over time. Appending preserves chronological order. Deduplication prevents duplicates if `memory seed` is run after manual Phase 4 completion.

### Decision 4: Phase 1 Loading Position
**Context:** Where in Phase 1 should memory load?
**Options Considered:**
1. Before steering (step 2.5) — memory available for steering interpretation
2. After steering (step 3.5) — steering provides project shape before memory adds history
3. After pre-flight (step 4.5) — late, but all context is available

**Decision:** After steering, before pre-flight (step 3.5)
**Rationale:** Steering files define what the project IS (product, tech, structure). Memory adds what the project HAS DONE (decisions, patterns, context). This ordering means memory content is interpreted against the project's foundational context. Loading before pre-flight ensures memory is available for vertical detection and codebase exploration.

## Product Module Design

### Module: core/memory.md
**Responsibility:** Defines the memory layer behavior — loading, writing, subcommand, storage format, and platform adaptation.
**Interface:** Loaded by generator, rendered into platform outputs. No runtime API — all behavior is instructional (the LLM follows the instructions).
**Dependencies:** `core/workflow.md` (Phase 1 and Phase 4 hooks), `core/tool-abstraction.md` (abstract operations), `core/steering.md` (convention-based directory pattern).

### Storage: decisions.json
```json
{
  "version": 1,
  "decisions": [
    {
      "specId": "drift-detection",
      "specType": "feature",
      "number": 1,
      "decision": "Used H3 headings for drift checks instead of H4",
      "rationale": "Heading-level markers prevent substring collision in validators",
      "task": "Task 1 / Task 6",
      "date": "2026-03-08",
      "completedAt": "2026-03-08T09:36:18Z"
    }
  ]
}
```

### Storage: context.md
```markdown
# Project Memory

## Completed Specs

### drift-detection (feature) — 2026-03-08
6 tasks completed. New core/reconciliation.md module with 5 drift checks
(file drift, post-completion mods, task consistency, staleness, cross-spec conflicts).
Audit and reconcile subcommands added to workflow routing.

### steering-files (feature) — 2026-03-08
6 tasks completed. New core/steering.md module with convention-based
<specsDir>/steering/ directory, 3 foundation templates (product.md, tech.md,
structure.md), always/fileMatch/manual inclusion modes.
```

### Storage: patterns.json
```json
{
  "version": 1,
  "decisionCategories": [
    {
      "category": "validator marker alignment",
      "specs": ["bugfix-regression-analysis", "drift-detection"],
      "count": 2,
      "lesson": "H3 headings in core modules must exactly match validator marker strings"
    }
  ],
  "fileOverlaps": [
    {
      "file": "core/workflow.md",
      "specs": ["ears-notation", "bugfix-regression-analysis", "steering-files", "drift-detection"],
      "count": 4
    },
    {
      "file": "generator/validate.py",
      "specs": ["bugfix-regression-analysis", "steering-files", "drift-detection"],
      "count": 3
    }
  ]
}
```

## System Flow

### Memory Loading (Phase 1)
```
Phase 1 starts
  → Step 1: Read .specops.json
  → Step 2: Context recovery (index.json)
  → Step 3: Load steering files
  → Step 3.5: Load memory layer [NEW]
      → FILE_EXISTS(<specsDir>/memory/decisions.json)?
        → Yes: READ_FILE, parse JSON, validate version field
        → No: skip (no memory yet)
      → FILE_EXISTS(<specsDir>/memory/context.md)?
        → Yes: READ_FILE, add to context
        → No: skip
      → FILE_EXISTS(<specsDir>/memory/patterns.json)?
        → Yes: READ_FILE, parse JSON, surface recurring patterns
        → No: skip
      → NOTIFY_USER: "Loaded memory: N decisions, M completed specs, P patterns"
        (or "No memory found — memory will be created after your first spec completes")
  → Step 4: Pre-flight check
  → ... (rest of Phase 1)
```

### Memory Writing (Phase 4)
```
Phase 4 starts
  → Step 1: Verify acceptance criteria
  → Step 2: Finalize implementation.md (Summary populated)
  → Step 2.5: Update memory layer [NEW]
      → READ_FILE(<specsDir>/<spec>/implementation.md)
      → Extract Decision Log entries (parse markdown table rows)
      → READ_FILE(<specsDir>/<spec>/spec.json) for metadata
      → READ_FILE existing decisions.json (or create new)
      → Append new entries, deduplicate by specId+number
      → WRITE_FILE(<specsDir>/memory/decisions.json)
      → READ_FILE existing context.md (or create new)
      → Append spec completion summary
      → WRITE_FILE(<specsDir>/memory/context.md)
      → Detect patterns:
        - Scan decision categories for recurrence
        - Collect "Files to Modify" from tasks.md, cross-reference with prior specs
      → WRITE_FILE(<specsDir>/memory/patterns.json)
      → NOTIFY_USER: "Memory updated: added N decisions, updated context, detected P patterns"
  → Step 3: Documentation check
  → ... (rest of Phase 4)
```

### Memory Subcommand
```
/specops memory
  → Read <specsDir>/memory/ files
  → Display formatted summary (decisions table, context, patterns)

/specops memory seed
  → Scan all completed specs (from index.json)
  → For each: READ_FILE implementation.md, extract Decision Log
  → Build/rebuild decisions.json, context.md, patterns.json
  → NOTIFY_USER: "Seeded memory from N completed specs"
```

## Integration Points

### Generator Pipeline
Same pattern as reconciliation/steering/from-plan:
- `generator/generate.py`: Add `"memory": core["memory"]` to all 4 platform context dicts
- `generator/templates/*.j2` (x4): Add `{{ memory }}` placeholder after `{{ steering }}`
- `generator/validate.py`: Add `MEMORY_MARKERS` to `validate_platform()` AND cross-platform consistency loop
- `tests/test_platform_consistency.py`: Add `"memory"` to `REQUIRED_MARKERS`

### Workflow Hooks
- `core/workflow.md` Phase 1: Add step 3.5 (memory loading)
- `core/workflow.md` Phase 4: Add step 2.5 (memory writing)
- `core/workflow.md` Getting Started: Add memory subcommand routing (between steering and audit checks)

## Security Considerations
- **Path containment**: Memory directory inherits `<specsDir>` containment rules — no `..` traversal, no absolute paths
- **Content safety**: Memory content is treated as project context only (same rules as steering files — skip files with meta-instructions)
- **No secrets**: Memory never stores credentials, tokens, or PII. Decision rationales are architectural, not operational

## Platform Adaptation

| Capability | Impact |
|-----------|--------|
| `canAskInteractive: false` | `memory seed` displays results only (no confirmation prompt). Memory loading and writing work identically |
| `canTrackProgress: false` | Skip UPDATE_PROGRESS calls during memory operations |
| `canExecuteCode: true` (all platforms) | `RUN_COMMAND(date)` for timestamps works on all platforms |

## Testing Strategy
- Generator validation: MEMORY_MARKERS present in all 4 platform outputs
- Cross-platform consistency: memory markers identical across platforms
- Build test: `generate.py --all` succeeds with new module
- Manual: Run `/specops memory seed` on SpecOps repo, verify decisions from 4 completed specs are captured

## Ship Plan
1. Create `core/memory.md` and update `core/workflow.md`
2. Wire generator pipeline (generate.py, templates, validate.py, tests)
3. Regenerate all platform outputs
4. Validate and run full test suite
5. Dogfood: seed memory from Specs 1–4, verify it loads

## Risks & Mitigations
- **Risk:** Decision Log table format varies across specs → **Mitigation:** Format is stable (verified across 4 completed specs). Parser handles missing/empty tables gracefully.
- **Risk:** Large decision count bloats Phase 1 context → **Mitigation:** decisions.json is bounded by spec count (each spec adds 0–3 decisions). At 20 specs, ~60 entries max — well within context limits.
- **Risk:** patterns.json grows stale or misleading → **Mitigation:** Patterns are recomputed on each Phase 4 write. `memory seed` can fully rebuild.
