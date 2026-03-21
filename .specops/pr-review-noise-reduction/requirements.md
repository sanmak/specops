# Feature: PR Review Noise Reduction

## Overview
Across 26 closed PRs, three review bots (CodeRabbit, Copilot, Greptile) produced 715 actionable comments. 33.6% targeted generated files that are symptoms of source-level issues. 12 systemic patterns recur across multiple PRs. The repo has powerful quality tools (`/core-review`, `/full-review-gate`, `/docs-sync`, `lint-specs.sh`, `validate.py`) that are not wired into the PR creation pipeline. This feature chains existing tools and fills tooling gaps to catch issues before PRs are opened, targeting a 62% reduction in bot review comments.

## Product Requirements

### Requirement 1: Bot Configuration to Skip Generated Files
**As a** contributor
**I want** review bots to skip commenting on generated platform output files
**So that** PR review comments focus on root causes in source files, not symptoms in generated outputs

**Acceptance Criteria (EARS):**
<!-- WHEN a PR is opened that modifies core/*.md THE SYSTEM SHALL NOT produce CodeRabbit inline comments on platforms/*/SKILL.md, platforms/*/specops.mdc, platforms/*/specops.instructions.md, skills/specops/SKILL.md, .claude-plugin/*.json, or CHECKSUMS.sha256 -->
- WHEN a PR modifies source files THE SYSTEM SHALL suppress bot inline reviews on generated files via `.coderabbit.yml` path filters
- WHEN CodeRabbit reviews `core/*.md` files THE SYSTEM SHALL provide context-aware instructions about abstract tool operations so the bot does not flag them as broken function calls

**Progress Checklist:**
- [ ] `.coderabbit.yml` created with path_filters excluding all generated files
- [ ] path_instructions added for `core/*.md`, `generator/templates/*.j2`, and `generator/validate.py`

### Requirement 2: Markdown Lint in CI
**As a** contributor
**I want** markdown formatting issues (MD040 missing fence language, MD058 table spacing) caught in CI
**So that** the 50+ markdown lint comments across 16 PRs are eliminated before review

**Acceptance Criteria (EARS):**
- WHEN a PR contains a fenced code block without a language specifier in a source `.md` file THE SYSTEM SHALL fail the CI markdownlint job
- WHEN a PR modifies only generated `.md` files THE SYSTEM SHALL NOT lint those files (they inherit quality from source)

**Progress Checklist:**
- [ ] `.markdownlint.json` config created with MD040 and MD058 enabled, MD013/MD033/MD041 disabled
- [ ] CI job added to `.github/workflows/ci.yml` linting source markdown only

### Requirement 3: FILE_EXISTS Tool Mapping Fix
**As a** platform user
**I want** `FILE_EXISTS` abstract operations to be properly substituted in generated output
**So that** platform instructions don't contain raw `FILE_EXISTS(` text

**Acceptance Criteria (EARS):**
- THE SYSTEM SHALL include `FILE_EXISTS` in the `toolMapping` of all 4 platform.json files
- THE SYSTEM SHALL include `"FILE_EXISTS("` in the `ABSTRACT_OPERATIONS` list in `generator/validate.py`
- WHEN platform outputs are regenerated THE SYSTEM SHALL NOT contain any raw `FILE_EXISTS(` text

**Progress Checklist:**
- [ ] All 4 platform.json files have FILE_EXISTS mapping
- [ ] validate.py ABSTRACT_OPERATIONS includes FILE_EXISTS
- [ ] Regenerated outputs pass validation

### Requirement 4: Source-Level Abstract Op Validation
**As a** contributor editing `core/*.md`
**I want** malformed abstract operation usage caught at validation time
**So that** broken tool substitutions (bare ops without args, ops used as nouns) are detected before generation

**Acceptance Criteria (EARS):**
- WHEN `validate.py` runs THE SYSTEM SHALL scan each `core/*.md` file for abstract operations used without proper call syntax
- WHEN an abstract operation is used as a bare noun (without parentheses and arguments) THE SYSTEM SHALL report it as a validation error
- WHEN a `platform.json` is missing a `toolMapping` entry for a defined abstract operation THE SYSTEM SHALL report it as a validation error

**Progress Checklist:**
- [ ] `validate_source_syntax()` function added to validate.py
- [ ] Function checks core/*.md for bare abstract ops
- [ ] Function checks platform.json for complete toolMapping coverage

### Requirement 5: Checkbox Staleness in Pre-commit
**As a** contributor committing spec artifacts
**I want** checkbox staleness caught at commit time
**So that** the 40+ "Completed task with unchecked criteria" comments are eliminated

**Acceptance Criteria (EARS):**
- WHEN `.specops/` files are staged for commit AND `scripts/lint-specs.sh` exists THE SYSTEM SHALL run the spec linter as a pre-commit check
- IF the spec linter finds unchecked checkboxes in completed tasks THEN THE SYSTEM SHALL block the commit

**Progress Checklist:**
- [ ] Check 6 added to `hooks/pre-commit` running `lint-specs.sh` on staged spec files

### Requirement 6: Step Reference Validation
**As a** contributor
**I want** dangling step references (e.g., "see Step 5" when only 4 steps exist) caught by validation
**So that** the 30+ step reference staleness comments across 6 PRs are eliminated

**Acceptance Criteria (EARS):**
- WHEN `validate.py` runs THE SYSTEM SHALL detect all "Step N" references in generated outputs and verify the referenced step exists in the document

**Progress Checklist:**
- [ ] `validate_step_references()` function added to validate.py

### Requirement 7: Strengthened Validation Markers
**As a** contributor
**I want** validation markers to be specific enough to avoid incidental matches
**So that** false positive marker matches are reduced

**Acceptance Criteria (EARS):**
- WHEN `*_MARKERS` lists contain single-word or generic markers THE SYSTEM SHALL replace them with more specific multi-word or heading-prefixed strings
- THE SYSTEM SHALL keep `validate.py` and `test_platform_consistency.py` marker lists in sync

**Progress Checklist:**
- [ ] Generic markers identified and replaced in validate.py
- [ ] Same changes applied to test_platform_consistency.py

### Requirement 8: Pre-PR Quality Gate Command
**As a** contributor preparing to ship a PR
**I want** a single `/pre-pr` command that chains `/core-review`, validation, lint, checksums, tests, and `/docs-sync`
**So that** issues bots would flag are caught before the PR is opened

**Acceptance Criteria (EARS):**
- WHEN `/pre-pr` is invoked THE SYSTEM SHALL run `/core-review current`, `validate.py`, `lint-specs.sh`, checksum verification, full test suite, and `/docs-sync` in sequence
- WHEN all checks pass THE SYSTEM SHALL display a summary dashboard with pass/fail status for each check
- IF any P0/P1 findings exist in `/core-review` THEN THE SYSTEM SHALL offer auto-fix before continuing
- WHEN security-sensitive files are in the diff THE SYSTEM SHALL display an advisory suggesting `/full-review-gate`

**Progress Checklist:**
- [ ] `.claude/commands/pre-pr.md` created with 5-step workflow
- [ ] Dashboard format displays all check results

### Requirement 9: Ship-PR Advisory
**As a** contributor using `/ship-pr`
**I want** a tip suggesting `/pre-pr` before shipping
**So that** the pre-PR gate becomes part of the workflow

**Acceptance Criteria (EARS):**
- WHEN `/ship-pr` reaches Step 5 (Review changes) THE SYSTEM SHALL display a tip: "Run `/pre-pr` before `/ship-pr` to catch issues that bots would flag in review."

**Progress Checklist:**
- [ ] Tip added to `.claude/commands/ship-pr.md` after Step 5

## Scope Boundary

**Ships in v1:**
- Bot configuration (.coderabbit.yml)
- Markdown lint in CI
- FILE_EXISTS fix
- Source-level abstract op validation
- Checkbox staleness in pre-commit
- Step reference validation
- Marker strengthening
- /pre-pr command
- /ship-pr advisory

**Deferred:**
- Greptile configuration (high signal already, filtering not needed)
- Copilot review config (no granular path exclusion support)
- Shell injection scanning in markdown prose (design-level concern, not lintable)
- Spec artifact drift detection (v2 backlog — requires pivot detection)
- Workflow contradiction detection (complex NLP, deferred to v2)

## Deferred Criteria
- Requirement 7 (Strengthen validation markers) *(deferred — requires careful audit of 27 marker lists across validate.py and test_platform_consistency.py; lower priority than the other tasks which deliver 60%+ of the noise reduction)*

## Non-Functional Requirements
- Pre-commit hook must remain under 5 seconds execution time
- No new Python dependencies beyond jsonschema and jinja2
- Markdownlint runs via `npx` in CI only (no local Node.js dependency)

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
