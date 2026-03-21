# Feature: Engineering Discipline Module

## Overview

SpecOps grounds spec *writing* rules in named leaders (Sutton, Orwell, Bezos, Lamport, Pinker) via `core/writing-quality.md`, but spec *engineering* areas — architecture, testing, reliability, constraints — lack intellectual lineage. Enforcement gates, blast radius analysis, and 200+ validation checks exist without attribution or unifying principles. This asymmetry means writing discipline is codified and teachable; engineering discipline is implicit and fragile.

This feature creates `core/engineering-discipline.md` following the exact pattern of `writing-quality.md` — mapping 11 named thinkers to 14 concrete, testable rules the agent follows during Phase 2 (design) and Phase 3 (implementation).

## User Stories

### US-1: Agent applies engineering discipline rules during spec creation

<!-- EARS: When the agent generates design.md or tasks.md during Phase 2, the agent SHALL apply all 14 engineering discipline rules and silently verify the 3-item self-check before finalizing. -->

As a developer using SpecOps, I want the agent to apply named engineering principles (single responsibility, test-first, failure mode documentation, binding constraint identification) during Phase 2 and Phase 3, so that specs and implementations reflect established engineering discipline rather than ad-hoc decisions.

**Acceptance Criteria:**

- [ ] `core/engineering-discipline.md` exists with 4 domains, 14 rules, a self-check section, and a sources section
- [ ] Module follows the identical structure of `core/writing-quality.md` (section headings, self-check pattern, sources attribution)
- [ ] Rules reference existing modules via `(reinforces: <module>)` cross-references where applicable
- [ ] Module is loaded in `spec` and `from-plan` modes via `core/mode-manifest.json`

### US-2: Engineering discipline propagates to all 4 platforms

<!-- EARS: When the generator runs with --all, the engineering discipline content SHALL appear in all 4 platform outputs (Claude, Cursor, Codex, Copilot). -->

As a SpecOps maintainer, I want engineering discipline rules to propagate through the generator pipeline to all platform outputs, so that every supported platform enforces the same engineering standards.

**Acceptance Criteria:**

- [ ] `generator/generate.py` includes `engineering_discipline` in `build_common_context()`
- [ ] All 4 Jinja2 templates (`claude.j2`, `codex.j2`, `cursor.j2`, `copilot.j2`) include the `{{ engineering_discipline }}` placeholder
- [ ] After regeneration, `grep "Engineering Discipline" platforms/*/` matches all 4 platform outputs
- [ ] `generator/validate.py` has `ENGINEERING_DISCIPLINE_MARKERS` constant with section headings and content markers
- [ ] Validation checks pass for all 4 platforms (`python3 generator/validate.py` exits 0)

### US-3: Documentation reflects the new module

<!-- EARS: While the engineering-discipline module exists in core/, the documentation files SHALL reference it. -->

As a contributor reading the docs, I want `docs/STRUCTURE.md` and `README.md` to document the engineering discipline module, so that the repository's documentation stays complete and accurate.

**Acceptance Criteria:**

- [ ] `docs/STRUCTURE.md` lists `engineering-discipline.md` in the core module directory tree
- [ ] `README.md` mentions engineering discipline in the philosophy section alongside the existing writing quality reference
- [ ] `CHECKSUMS.sha256` is regenerated to include the new file

## Non-Functional Requirements

- The module must be under 60 lines to match the conciseness standard set by `writing-quality.md`
- All rules must be testable — no vague aspirational statements
- The module must use only abstract operations from `core/tool-abstraction.md` (though this module is prose, not code)
- Markdown must pass `markdownlint-cli2` with no violations

## Out of Scope

- Modifying existing enforcement gates or validation logic beyond adding marker checks
- Adding new abstract operations to `core/tool-abstraction.md`
- Creating new spec templates
