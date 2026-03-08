# Design: Steering Files — Persistent Project Context

## Architecture Overview

Steering files add a new layer of persistent project context to SpecOps. They are plain markdown files with YAML frontmatter, stored in `<specsDir>/steering/`, and loaded during Phase 1 before the agent explores the codebase. The implementation follows SpecOps's established three-layer architecture: a new `core/steering.md` module defines the behavior platform-agnostically, the generator includes it in all platform outputs, and the validator ensures consistency.

## Technical Decisions

### Decision 1: Steering File Location
**Context:** Where should steering files live?
**Options Considered:**
1. `<specsDir>/steering/` (inside specs directory) — co-located with specs, single config controls both
2. `.steering/` (separate root directory) — independent of specsDir
3. Inside `.specops.json` (inline config) — no extra files

**Decision:** Option 1 — `<specsDir>/steering/`
**Rationale:** Co-locating with specs keeps all SpecOps artifacts in one directory controlled by `specsDir`. No new top-level directories needed. Path containment rules already apply.

### Decision 2: Inclusion Modes
**Context:** How to control when steering files are loaded?
**Options Considered:**
1. Three modes: `always`, `fileMatch`, `manual` — explicit, deterministic
2. Four modes: add `auto` (semantic matching by description) — more convenient but non-deterministic
3. Single mode: always load everything — simplest

**Decision:** Option 1 — three deterministic modes
**Rationale:** `always` covers foundational context (95% use case), `fileMatch` covers domain-specific context, `manual` covers rarely-needed reference. The `auto` mode requires semantic matching which is unreliable and adds complexity without clear v1 value.

### Decision 3: Foundation Templates Location
**Context:** Where to define the product/tech/structure starter templates?
**Options Considered:**
1. Inline in `core/steering.md` — simple, follows init.md pattern
2. Separate files in `core/templates/` — consistent with spec templates

**Decision:** Option 1 — inline in `core/steering.md`
**Rationale:** Foundation templates are short stubs (5-10 lines each). Separate files would require extending `render_templates_section()` and adding template ordering logic. The init module already inlines config templates successfully.

### Decision 4: Convention-Based Scope
**Context:** How should steering activation and safety limits be defined?
**Options Considered:**
1. Convention-based: steering activates when `<specsDir>/steering/` exists, with a fixed safety limit of 20 files
2. Schema-based: add `.specops.json` `steering` config (`enabled`, `maxFiles`)

**Decision:** Option 1 — convention-based with fixed limit
**Rationale:** The shipped implementation is directory-driven and does not add schema/config fields. This keeps steering metadata in one place (the steering files themselves) and avoids dual-source drift between docs and config.

## Product Module Design

### Module: Steering Files (`core/steering.md`)
**Responsibility:** Define steering file format, inclusion modes, loading procedure, safety rules, and foundation templates
**Interface:** Loaded as `{{ steering }}` in platform templates, positioned after config handling
**Dependencies:** `core/tool-abstraction.md` (abstract operations), `core/safety.md` (convention sanitization)

### Module: Workflow Update (`core/workflow.md`)
**Responsibility:** Integrate steering loading into Phase 1 step sequence
**Interface:** New step between "Context recovery" and "Pre-flight check"
**Dependencies:** `core/steering.md` (references steering module for full procedure)

### Module: Convention Handling (`core/steering.md`)
**Responsibility:** Define directory-driven steering activation and enforce the fixed 20-file safety limit
**Interface:** Steering loads when `<specsDir>/steering/` exists; no schema-level steering contract
**Dependencies:** None

### Module: Generator Pipeline
**Responsibility:** Include steering module in all platform outputs
**Interface:** `"steering": core["steering"]` in context dicts, `{{ steering }}` in templates
**Dependencies:** `generator/generate.py`, `generator/templates/*.j2`

## System Flow

```
Phase 1 Start
    │
    ▼
Read .specops.json config
    │
    ▼
Context recovery (index.json)
    │
    ▼
┌─────────────────────────┐
│  Load Steering Files    │ ← NEW STEP
│  1. Check steering/     │
│  2. Read each .md file  │
│  3. Parse frontmatter   │
│  4. Load always files   │
│  5. Defer fileMatch     │
└─────────────────────────┘
    │
    ▼
Pre-flight check
    │
    ▼
Analyze request → identify affected components/files → match fileMatch globs → load matching steering
    │
    ▼
Explore codebase (with steering context)
```

## Integration Points

| Integration | Type | Description |
|-------------|------|-------------|
| `generator/generate.py` | Build pipeline | Add `steering` to all 4 platform context dicts |
| `generator/templates/*.j2` | Template | Add `{{ steering }}` placeholder after `{{ config_handling }}` |
| `generator/validate.py` | Validation | Add `STEERING_MARKERS` to per-platform and cross-platform checks |
| `tests/test_platform_consistency.py` | Test | Add steering markers to required markers |

## Security Considerations
- **Convention Sanitization**: Steering file content is treated as project context only. Meta-instructions detected in steering content are skipped with a warning (same rules as `team.conventions`).
- **Path Containment**: Steering file names must not contain `..` or absolute paths. The steering directory inherits `specsDir` path containment.
- **Max Files**: Fixed limit of 20 steering files prevents excessive context injection.

## Ship Plan

1. Create `core/steering.md` — the core module (no dependencies, can be developed independently)
2. Update `core/workflow.md` — Phase 1 integration (depends on steering.md existing)
3. Finalize convention-based scope (no schema/config steering fields)
4. Update generator pipeline — include in all platforms (depends on steering.md)
5. Update validation + tests — ensure consistency (depends on generator changes)
6. Regenerate all platform outputs — final integration step
7. Create SpecOps's own steering files — dogfood proof

## Risks & Mitigations
- **Abstract op prefix collision** (dogfood gap #9, #16) → Use bare abstract ops as verbs in `core/steering.md`, verify generated output reads naturally after substitution
- **Marker uniqueness** (dogfood gap #13) → Use multi-word markers and heading-level prefixes where needed
- **Checkbox staleness** (dogfood gap #1, #11) → Explicitly check all checkboxes in Phase 4 before completion
