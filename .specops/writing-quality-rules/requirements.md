# Feature: Writing Quality Rules Module

## Overview
SpecOps generates structured spec artifacts but has no guidance on how those artifacts should be written. Dogfood specs show recurring prose issues: hedging in rationales ("would need", "could potentially"), weak topic sentences in design sections, jargon without definition, and over-explanation. The existing `core/simplicity.md` covers what to include (scope scaling, skip empty sections); this module covers how to express it (precision, ordering, voice, audience awareness). Writing rules are distilled from 9 vetted technical writing references.

## Product Requirements

### Requirement 1: Writing Quality Core Module
**As a** developer using SpecOps
**I want** the agent to follow proven writing principles when generating spec artifacts
**So that** specs are precise, concise, and readable by both implementing agents and human reviewers

**Acceptance Criteria (EARS):**
- WHEN the agent generates any spec artifact during Phase 2 THE SYSTEM SHALL apply writing quality rules covering structure/ordering, precision, clarity, audience awareness, collaborative voice, and self-checking
- WHEN a Design Architecture Overview is generated THE SYSTEM SHALL lead with the problem or constraint being solved, not the feature being built
- WHEN a Decision rationale is generated THE SYSTEM SHALL use declarative language (is, requires, prevents) and not modal hedging (would, could, might)
- WHEN domain-specific terminology is introduced in a spec THE SYSTEM SHALL define it at first use
- IF a spec section contains only disconnected bullet points without narrative connectors THEN THE SYSTEM SHALL add causal narrative linking the points

**Progress Checklist:**
- [x] Writing quality rules applied during Phase 2 spec generation
- [x] Design sections lead with problem, not feature
- [x] Rationales use declarative language, no hedging
- [x] Jargon defined at first use
- [x] Bullet-point walls converted to causal narratives

### Requirement 2: Generator Pipeline Integration
**As a** SpecOps maintainer
**I want** the writing quality module to flow through the generator pipeline to all 4 platform outputs
**So that** writing quality rules are enforced consistently across Claude Code, Cursor, Codex, and Copilot

**Acceptance Criteria (EARS):**
- WHEN `python3 generator/generate.py --all` runs THE SYSTEM SHALL include writing quality rules in all 4 platform outputs
- WHEN `python3 generator/validate.py` runs THE SYSTEM SHALL verify writing quality markers are present in every platform output

**Progress Checklist:**
- [x] Generator includes writing quality module in all platform outputs
- [x] Validator checks writing quality markers across all platforms

### Requirement 3: README Attribution
**As a** potential SpecOps user reading the README
**I want** to see that spec writing quality is informed by respected technical writing leaders
**So that** I understand the intellectual foundations behind the tool's spec generation quality

**Acceptance Criteria (EARS):**
- WHEN a user reads the README THE SYSTEM SHALL include a "Writing Philosophy" section attributing writing principles to the 9 source authors

**Progress Checklist:**
- [x] README contains Writing Philosophy section with 9 attributions

## Scope Boundary
**Ships:**
- `core/writing-quality.md` with imperative rules from 9 references
- Generator pipeline integration (generate.py, 4 Jinja2 templates)
- Validation markers (validate.py, test_platform_consistency.py)
- README attribution section
- Documentation updates (STRUCTURE.md, CLAUDE.md)

**Deferred:**
- Template-level enforcement (embedding writing rules directly into spec templates)
- Automated prose quality scoring or linting

## Constraints & Assumptions
- Module must use no abstract operations (writing rules are prose guidance, not file operations — same pattern as `core/simplicity.md`)
- Module must NOT overlap with `core/simplicity.md` (simplicity = what to include; writing quality = how to express it)
- All rules must be imperative mood ("Write...", "Cut..."), never advisory ("Consider...", "Tip:")
- Target ~100 lines to keep generated SKILL.md growth minimal (~2.8% increase)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
