# Feature: Steering Files — Persistent Project Context

## Overview

Add a steering files system that provides persistent project context to the SpecOps workflow. Steering files are markdown documents with YAML frontmatter that live in `.specops/steering/` and are automatically loaded during Phase 1 (Understand Context). They give the agent foundational knowledge about the project — what it builds, what tech stack it uses, and how the codebase is organized — so every spec starts with informed context rather than cold exploration.

## Product Requirements

### Requirement 1: Steering File Format and Storage
**As a** developer setting up SpecOps
**I want** to create markdown files with structured metadata in a well-known directory
**So that** the agent consistently discovers and interprets my project context

**Acceptance Criteria (EARS):**
<!-- Event-Driven: file creation and discovery -->
- WHEN a markdown file with valid YAML frontmatter exists in `<specsDir>/steering/` THE SYSTEM SHALL recognize it as a steering file
- WHEN the YAML frontmatter contains `name`, `description`, and `inclusion` fields THE SYSTEM SHALL parse the file as a valid steering file
- IF a steering file has invalid or missing frontmatter THEN THE SYSTEM SHALL skip it with a warning and continue loading other files

**Progress Checklist:**
- [x]Steering files recognized from `<specsDir>/steering/` directory
- [x]YAML frontmatter parsed for name, description, inclusion fields
- [x]Invalid files skipped with warning

### Requirement 2: Inclusion Modes
**As a** developer with diverse project context
**I want** to control when each steering file is loaded
**So that** the agent gets relevant context without unnecessary noise

**Acceptance Criteria (EARS):**
<!-- Event-Driven + State-Driven: mode-dependent loading -->
- WHEN a steering file has `inclusion: always` THE SYSTEM SHALL load it in every Phase 1 execution
- WHEN a steering file has `inclusion: fileMatch` and `globs` patterns THE SYSTEM SHALL load it only when affected files match any glob pattern
- WHEN a steering file has `inclusion: manual` THE SYSTEM SHALL skip it during automatic loading (loaded only on explicit reference)
- IF the `inclusion` field has an unrecognized value THEN THE SYSTEM SHALL skip the file with a warning

**Progress Checklist:**
- [x]`always` mode loads unconditionally in Phase 1
- [x]`fileMatch` mode loads conditionally based on glob patterns
- [x]`manual` mode skips automatic loading
- [x]Unrecognized inclusion values handled with warning

### Requirement 3: Phase 1 Integration
**As a** developer using SpecOps
**I want** steering files loaded automatically before the agent explores my codebase
**So that** specs are informed by persistent project context from the first interaction

**Acceptance Criteria (EARS):**
<!-- Event-Driven: Phase 1 workflow trigger -->
- WHEN Phase 1 begins and `<specsDir>/steering/` exists THE SYSTEM SHALL load steering files between config reading and pre-flight check
- WHEN `always` steering files are loaded THE SYSTEM SHALL inject their content as project context before codebase exploration
- WHEN `fileMatch` steering files exist THE SYSTEM SHALL defer their evaluation until after request analysis identifies affected files
- IF `config.steering.enabled` is `false` THE SYSTEM SHALL skip steering file loading entirely
- IF the number of steering files exceeds `config.steering.maxFiles` (default 20) THE SYSTEM SHALL load only up to the limit and warn about skipped files

**Progress Checklist:**
- [x]Steering loading integrated into Phase 1 workflow
- [x]Always-included files loaded before codebase exploration
- [x]fileMatch files deferred until after request analysis
- [x]Loading disabled when config.steering.enabled is false
- [x]maxFiles limit enforced with warning

### Requirement 4: Foundation File Templates
**As a** developer starting with steering files
**I want** starter templates for common project context types
**So that** I can quickly create useful steering files without designing the format from scratch

**Acceptance Criteria (EARS):**
<!-- Ubiquitous: template availability -->
- THE SYSTEM SHALL provide foundation templates for three file types: product.md, tech.md, structure.md
- WHEN creating steering files THE SYSTEM SHALL use the foundation templates as starting points with appropriate section headings
- THE SYSTEM SHALL include YAML frontmatter with `inclusion: always` in all foundation templates

**Progress Checklist:**
- [x]product.md template defined (Product Overview, Target Users, Key Differentiators)
- [x]tech.md template defined (Core Stack, Development Tools, Quality & Testing)
- [x]structure.md template defined (Directory Layout, Key Files, Module Boundaries)
- [x]All templates include proper YAML frontmatter

## Scope Boundary

**Ships in this spec:**
- `core/steering.md` module with format, inclusion modes, loading procedure, safety rules, foundation templates
- `core/workflow.md` Phase 1 update with steering loading step
- `schema.json` optional steering config (`enabled`, `maxFiles`)
- Generator pipeline integration (generate.py + 4 platform templates)
- Validation markers (`STEERING_MARKERS` in validate.py)
- Platform consistency tests
- All regenerated platform outputs

**Deferred:**
- Global scope (`~/.specops/steering/`) — project scope covers primary use cases
- `auto` inclusion mode (semantic matching) — `fileMatch` with globs is deterministic
- `team.conventions` migration to steering files — complementary systems, no breaking change needed
- Init subcommand integration (`/specops init --with-steering`) — separate concern
- File references syntax (`#[[file:<path>]]`) — unnecessary complexity for v1

## Product Quality Attributes
- **Performance**: Loading 20 steering files should add negligible overhead to Phase 1 (file reads only)
- **Safety**: Convention Sanitization rules apply to steering content; meta-instructions are rejected
- **Compatibility**: Existing projects without steering files are unaffected (no breaking change)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
