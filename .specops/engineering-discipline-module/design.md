# Design: Engineering Discipline Module

## Overview

We add a new core module `core/engineering-discipline.md` that grounds architecture, testing, reliability, and constraint rules in 11 named thinkers. The module follows the identical pattern established by `core/writing-quality.md` — prose rules organized by domain, a silent self-check, and a sources section attributing each rule to its intellectual origin. Integration follows the standard core module pipeline: add to generator context, add template placeholders, wire mode manifest, add validation markers.

## Architecture Decision: Module Structure

**Decision:** Mirror `writing-quality.md` exactly — 4 domain sections with 14 rules, a Self-Check section (3 items), and a Sources section (11 leaders).

**Rationale:** `writing-quality.md` established a proven pattern: domain-grouped rules with cross-references to existing modules via `(reinforces: <module>)`. Reusing this structure means the agent already knows how to apply it (same pattern recognition), maintainers already know how to extend it, and validation follows the same marker-checking approach.

**Alternatives considered:** A single flat list of rules (rejected: loses domain grouping that aids comprehension) or a separate file per domain (rejected: 4 files for 14 rules is excessive overhead for the generator pipeline).

## Architecture Decision: Four Domains

**Decision:** Organize rules into 4 domains mapping to engineering concerns that already exist implicitly in SpecOps:

1. **Architecture & Design Integrity** (Brooks, Liskov, Hohpe) — 4 rules
2. **Testing & Validation Philosophy** (Beck, Dijkstra, Feathers) — 4 rules
3. **Reliability & Failure Reasoning** (Leveson, Taleb) — 3 rules
4. **Constraints & Quality Gates** (Goldratt, Deming, Humble) — 3 rules

**Rationale:** These 4 domains map to Phase 2 (architecture, constraints) and Phase 3 (testing, reliability) where engineering discipline is applied. Each domain has 3-4 rules — enough to be substantive, few enough to be memorable.

## Architecture Decision: Reinforcement Cross-References

**Decision:** Rules that reinforce existing SpecOps modules include a `(reinforces: <module>)` parenthetical linking to the existing enforcement point.

**Rationale:** This turns the module into both a discipline codex and an index into existing enforcement. When an agent reads "Record every technical decision in design.md before implementing" with `(reinforces: implementation.md template Decision Log)`, it understands the rule is not aspirational — it connects to an existing template field.

**Cross-reference map:**

| Rule | Reinforces |
|---|---|
| Record decisions in design.md before implementing | implementation.md template Decision Log |
| Passing tests are necessary evidence, not sufficient proof | Phase 4 acceptance criteria verification |
| Evaluate changes as interactions | bugfix blast radius analysis |
| Quality gates are load-bearing structure | existing enforcement gates |
| Scope each spec to one verifiable increment | simplicity.md "scale specs to the task" |

## Architecture Decision: Generator Integration

**Decision:** Follow the standard module integration pattern:
1. Add `"engineering_discipline": core["engineering-discipline"]` to `build_common_context()` in `generate.py`
2. Add `{{ engineering_discipline }}` to all 4 Jinja2 templates after `{{ writing_quality }}`
3. Add `"engineering-discipline"` to `spec` and `from-plan` mode modules in `mode-manifest.json`

**Rationale:** Every previous core module (dependency-safety, pipeline, git-checkpointing, etc.) followed this exact integration path. Deviating would create a maintenance anomaly.

## Architecture Decision: Validation Markers

**Decision:** Add `ENGINEERING_DISCIPLINE_MARKERS` to `validate.py` with section headings and two distinctive content markers (`substitutability`, `characterization test`). Add to all 3 required locations (constant, `validate_platform()`, cross-platform consistency) in the same commit.

**Rationale:** The `*_MARKERS` constant + 3-location pattern is documented in CLAUDE.md as a critical rule. The two content markers (`substitutability`, `characterization test`) are distinctive enough to avoid false positives while confirming the module's unique content is present.

## Module Placement in Templates

In all 4 Jinja2 templates, `{{ engineering_discipline }}` is placed immediately after `{{ writing_quality }}`. This groups the two discipline modules together — writing discipline followed by engineering discipline — creating a coherent "principles" block in the generated output.

## File Changes Summary

| File | Change Type | Description |
|---|---|---|
| `core/engineering-discipline.md` | New | The module itself (~55 lines, 4 domains, 14 rules) |
| `generator/generate.py` | Modify | Add to `build_common_context()` |
| `generator/templates/claude.j2` | Modify | Add `{{ engineering_discipline }}` after `{{ writing_quality }}` |
| `generator/templates/codex.j2` | Modify | Add `{{ engineering_discipline }}` after `{{ writing_quality }}` |
| `generator/templates/cursor.j2` | Modify | Add `{{ engineering_discipline }}` after `{{ writing_quality }}` |
| `generator/templates/copilot.j2` | Modify | Add `{{ engineering_discipline }}` after `{{ writing_quality }}` |
| `core/mode-manifest.json` | Modify | Add to `from-plan` and `spec` mode modules |
| `generator/validate.py` | Modify | Add markers constant + 2 check sites |
| `docs/STRUCTURE.md` | Modify | Add to core module listing |
| `README.md` | Modify | Add engineering philosophy mention |
| `CHECKSUMS.sha256` | Modify | Regenerate |
