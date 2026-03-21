# Design: Dependency Safety Gate

## Technical Decisions

**Decision:** 3-layer verification protocol (local → online → LLM fallback)
**Rationale:** Maximizes coverage across environments — enterprises with audit tooling get precise results, air-gapped environments still get LLM knowledge, and online APIs fill the gap between. Each layer is optional, ensuring graceful degradation.

**Decision:** Inline audit artifact template (not in core/templates/)
**Rationale:** `generator/generate.py` auto-loads ALL `core/templates/*.md` into the `_templates` dict — adding a file there would cause it to be loaded as a spec-type template even though it isn't one. The artifact format is defined inline in `core/dependency-safety.md`.

**Decision:** Phase 2 step 6.7 placement (between git checkpoint 6.5 and review 7)
**Rationale:** Dependency audit must happen after spec content is finalized (to know which ecosystems are relevant) but before review or implementation begins. The git checkpoint at 6.5 captures the spec pre-audit, and the audit artifact becomes part of the spec before review.

**Decision:** `dependencies.md` as 4th foundation steering file using `_generated: true` pattern
**Rationale:** Follows the established `repo-map.md` pattern — machine-generated but team-enrichable. The `_generated: true` flag distinguishes auto-populated content from manually maintained sections.

## Component Design

### core/dependency-safety.md
**Responsibility:** Defines the 3-layer verification protocol, severity evaluation, blocking logic, artifact formats, and steering file auto-generation.
**Interface:** Abstract operations only (READ_FILE, WRITE_FILE, RUN_COMMAND, NOTIFY_USER, ASK_USER, FILE_EXISTS, LIST_DIR).

### schema.json — dependencySafety section
**Responsibility:** Validates the new configuration section with 5 properties.
**Interface:** JSON Schema with `additionalProperties: false`.

### generator pipeline
**Responsibility:** Includes `dependency_safety` in `build_common_context()`, wires through all 4 `.j2` templates.
**Interface:** `{{ dependency_safety }}` template variable.

### validator — DEPENDENCY_SAFETY_MARKERS
**Responsibility:** Validates all 4 platform outputs contain required dependency safety markers.
**Interface:** Marker list checked per-platform and cross-platform.

## Integration Points

```text
core/dependency-safety.md ──┐
                            ├──> generator/generate.py (build_common_context)
core/workflow.md (step 6.7) │
                            ├──> generator/templates/*.j2 ({{ dependency_safety }})
core/steering.md (4th tpl)  │
                            ├──> generator/validate.py (DEPENDENCY_SAFETY_MARKERS)
core/config-handling.md     │
                            └──> schema.json (dependencySafety section)
core/mode-manifest.json
```

## Sequence Diagram

```
User -> SpecOps: Create spec for feature X
SpecOps -> Phase1: Understand context, load steering
SpecOps -> Phase2: Create spec files (steps 1-6.5)
Phase2 -> DepSafety: Step 6.7 — Dependency Safety Gate
DepSafety -> Layer1: Run local audit (npm audit, pip-audit, etc.)
Layer1 --> DepSafety: Results or skip
DepSafety -> Layer2: Query OSV.dev + endoflife.date (curl, 10s timeout)
Layer2 --> DepSafety: Results or skip
DepSafety -> Layer3: LLM knowledge fallback
Layer3 --> DepSafety: Results (annotated as offline)
DepSafety -> DepSafety: Compile findings, apply threshold
DepSafety -> SpecDir: Write dependency-audit.md
DepSafety -> SteeringDir: Write/update dependencies.md
DepSafety --> Phase2: Pass (proceed to review) or Block
```
