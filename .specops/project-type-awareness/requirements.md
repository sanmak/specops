# Feature: Project-Type-Aware Workflow

## Overview
SpecOps currently assumes a brownfield (existing codebase) context for every project. Phase 1 steps 8-9 are hollow on empty repos, init creates empty steering files regardless of existing docs, and there is no vertical for migration/re-platforming. This feature makes SpecOps project-type-aware across greenfield, brownfield, and bluefield projects with five targeted changes.

## Product Requirements

### Requirement 1: Auto-Init Suggestion
**As a** user running SpecOps for the first time
**I want** to be prompted about init when no `.specops.json` exists
**So that** I get proper project setup (steering files, memory) before my first spec

**Acceptance Criteria (EARS):**
- WHEN `.specops.json` does not exist and the user invokes SpecOps THE SYSTEM SHALL suggest running `/specops init` first or continuing with defaults
- WHEN the user chooses init THE SYSTEM SHALL redirect to the Init Mode workflow
- WHEN the user chooses defaults THE SYSTEM SHALL proceed with step 2 using default configuration

**Progress Checklist:**
- [x] Auto-init suggestion added to workflow.md step 1
- [x] Both paths (init redirect, continue with defaults) function correctly

### Requirement 2: Project Type Auto-Detection in Init
**As a** user running `/specops init`
**I want** the init to detect whether my project is greenfield or brownfield
**So that** appropriate defaults are pre-selected and the right setup actions execute

**Acceptance Criteria (EARS):**
- WHEN init is invoked THE SYSTEM SHALL scan the repository to count source code files (excluding `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `vendor/`, `.specops/`)
- WHEN source code file count is 5 or fewer THE SYSTEM SHALL classify as greenfield
- WHEN source code file count exceeds 5 and documentation/dependency files exist THE SYSTEM SHALL classify as brownfield
- THE SYSTEM SHALL present the detected type to the user with options: Greenfield, Brownfield, Migration (override)
- WHEN the user confirms greenfield THE SYSTEM SHALL pre-select the Builder template
- WHEN the user confirms brownfield THE SYSTEM SHALL pre-select the Standard template and enable assisted steering population
- WHEN the user selects migration THE SYSTEM SHALL pre-select Standard template with `vertical: "migration"` customization

**Progress Checklist:**
- [x] Step 1.5 added to init.md with repo scanning logic
- [x] Greenfield/brownfield classification logic documented
- [x] User confirmation with migration override option

### Requirement 3: Greenfield Adaptive Phase 1
**As a** user building a new project from scratch
**I want** Phase 1 to adapt for empty repos
**So that** codebase exploration is replaced with useful work (structure proposal, steering auto-population)

**Acceptance Criteria (EARS):**
- WHEN the project is greenfield (source code count ≤ 5) THE SYSTEM SHALL skip steps 8-9 and execute greenfield alternatives (8g: propose initial structure, 9g: auto-populate steering)
- WHEN steering files contain only placeholder text THE SYSTEM SHALL extract relevant context from the user's request to populate product.md, tech.md, and structure.md
- THE SYSTEM SHALL record `Project state: greenfield — proposed initial structure` in the Phase 1 Context Summary

**Progress Checklist:**
- [x] Step 7.5 greenfield detection added to workflow.md
- [x] Steps 8g and 9g (greenfield alternatives) defined
- [x] Steps 8-9 conditionally gated (brownfield/migration only)
- [x] Project state line added to implementation.md template

### Requirement 4: Brownfield Assisted Steering Population
**As a** user adopting SpecOps into an existing project
**I want** steering files to be pre-populated from existing documentation
**So that** the agent has project context from the first spec without manual steering file editing

**Acceptance Criteria (EARS):**
- WHEN the confirmed project type is brownfield THE SYSTEM SHALL scan for existing documentation (README.md, package.json, pyproject.toml, etc.)
- WHEN README.md exists and steering product.md contains only placeholders THE SYSTEM SHALL extract overview content to populate product.md
- WHEN dependency manifests exist and steering tech.md contains only placeholders THE SYSTEM SHALL extract tech stack information to populate tech.md
- WHEN steering structure.md contains only placeholders THE SYSTEM SHALL populate it from the top-level directory listing
- THE SYSTEM SHALL notify the user that steering files were pre-populated and should be reviewed

**Progress Checklist:**
- [x] Step 4.7 added to init.md (brownfield assisted steering)
- [x] README.md parsing for product.md population
- [x] Dependency file scanning for tech.md population
- [x] Directory listing for structure.md population

### Requirement 5: Migration Vertical
**As a** user re-platforming or migrating an existing system
**I want** SpecOps templates adapted for migration work
**So that** specs include source system analysis, target design, cutover planning, and coexistence strategy

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include `migration` as a valid vertical in schema.json
- WHEN the vertical is `migration` THE SYSTEM SHALL apply domain vocabulary (Migration Requirements, Migration Architecture, Cutover Plan, Integration Boundaries)
- WHEN the vertical is `migration` THE SYSTEM SHALL add Source System Analysis and Compatibility Requirements to requirements.md
- WHEN the vertical is `migration` THE SYSTEM SHALL add Source System, Target System, Coexistence Strategy, and Cutover Plan sections to design.md
- WHEN the vertical is `migration` THE SYSTEM SHALL add Migration Phase tag, Rollback Steps, and Validation Steps per task in tasks.md
- WHEN keywords include migrate, re-platform, modernize, strangler, cutover, or legacy replacement THE SYSTEM SHALL auto-detect the migration vertical

**Progress Checklist:**
- [x] `### migration` section added to verticals.md
- [x] Migration vocabulary verification entry added
- [x] Migration keywords added to workflow.md step 7
- [x] "migration" added to schema.json vertical enum
- [x] "### migration" added to VERTICAL_MARKERS in validate.py
- [x] "### migration" added to test_platform_consistency.py

## Product Quality Attributes
- All generated platform outputs must include the migration vertical content
- All existing tests must continue to pass
- Schema validation must accept `"migration"` as a vertical value
- Cross-platform consistency check must verify `### migration` marker in all 4 platforms

## Scope Boundary

**Ships in this spec:**
- Auto-init suggestion (workflow.md step 1 modification)
- Project type detection in init (init.md step 1.5)
- Greenfield adaptive Phase 1 (workflow.md step 7.5, conditional steps 8-9)
- Brownfield assisted steering population (init.md step 4.7)
- Migration vertical (verticals.md, schema.json, validate.py, tests)
- Implementation.md template update (project state line)

**Deferred:**
- Migration-specific spec template files (migration uses vertical adaptation of feature template)
- Dual-system steering file templates (legacy-system.md, target-architecture.md)
- Migration progress tracking across specs
- "Replaces" relationship between specs and legacy modules
- Architecture-first spec type for greenfield
- Scaffolding workflow guidance for greenfield Phase 3
- Remote installer changes (installer stays distribution-only)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
