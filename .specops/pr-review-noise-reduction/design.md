# Design: PR Review Noise Reduction

## Architecture Overview
This feature operates across 4 layers of the existing quality infrastructure: bot configuration (new), CI pipeline (extended), generator validation (extended), git hooks (extended), and slash commands (new + modified). No new architectural patterns are introduced — every change extends an existing mechanism.

## Technical Decisions

### Decision 1: Bot Configuration Over Bot-Specific APIs
**Context:** 33.6% of review comments target generated files. Need to suppress them.
**Options Considered:**
1. `.coderabbit.yml` path filters — declarative, no code, immediate effect
2. GitHub API to auto-dismiss comments — requires auth, fragile, reactive not preventive

**Decision:** Option 1 — `.coderabbit.yml`
**Rationale:** Zero maintenance, declarative, takes effect on next PR. CodeRabbit's path filtering is well-documented. Greptile and Copilot lack equivalent granularity so are not configured.

### Decision 2: CI-Only Markdownlint (No Local Dependency)
**Context:** MD040 is the single highest-volume comment category (50+ across 16 PRs).
**Options Considered:**
1. Add markdownlint to pre-commit hook — fast feedback but requires Node.js locally
2. CI job with `npx markdownlint-cli2` — slightly slower feedback but no local dependency

**Decision:** Option 2 — CI only
**Rationale:** The project has no Node.js dependency. Adding it to pre-commit would require all contributors to install Node. CI feedback is fast enough for formatting issues.

### Decision 3: Source Validation in validate.py (Not Pre-commit)
**Context:** Tool abstraction misuse (50+ comments) needs source-level detection.
**Options Considered:**
1. Shell-based check in pre-commit — fast but limited regex capability
2. Python validation in validate.py — richer parsing, already part of CI and pre-push

**Decision:** Option 2 — validate.py
**Rationale:** validate.py already has the infrastructure (ROOT_DIR, file loading, error reporting). Source syntax validation is a natural extension. It runs in pre-push and CI automatically.

## Product Module Design

### Module 1: Bot Configuration (`.coderabbit.yml`)
**Responsibility:** Suppress generated file reviews, provide architectural context to CodeRabbit
**Interface:** Declarative YAML, no runtime interface
**Dependencies:** None — consumed by CodeRabbit's GitHub App

### Module 2: Markdown Lint CI Job
**Responsibility:** Catch MD040/MD058 violations in source markdown
**Interface:** CI job exit code (0 = pass, non-zero = fail)
**Dependencies:** `npx markdownlint-cli2`, `.markdownlint.json` config

### Module 3: Source Syntax Validation (`validate.py` extension)
**Responsibility:** Detect malformed abstract operations in `core/*.md` and missing `toolMapping` entries
**Interface:** `validate_source_syntax()` function called from main validation flow
**Dependencies:** `core/tool-abstraction.md` (defines the canonical operation list)

### Module 4: Checkbox Staleness Gate (`hooks/pre-commit` extension)
**Responsibility:** Block commits with unchecked checkboxes in completed spec tasks
**Interface:** Pre-commit Check 6, uses existing `scripts/lint-specs.sh`
**Dependencies:** `scripts/lint-specs.sh` must exist

### Module 5: Step Reference Validation (`validate.py` extension)
**Responsibility:** Detect dangling step references in generated outputs
**Interface:** `validate_step_references()` function called from main validation flow
**Dependencies:** None beyond existing generated output files

### Module 6: Pre-PR Quality Gate (`.claude/commands/pre-pr.md`)
**Responsibility:** Chain existing quality tools into a single pre-PR workflow
**Interface:** `/pre-pr` slash command
**Dependencies:** `/core-review`, `validate.py`, `lint-specs.sh`, CHECKSUMS.sha256, test suite, `/docs-sync`

## System Flow

```
Contributor edits core/*.md or other source files
    │
    ├─── git commit ──► pre-commit hook
    │                    ├── Check 1-5 (existing)
    │                    └── Check 6: lint-specs.sh (NEW)
    │
    ├─── /pre-pr ──► Step 1: /core-review current (40% of issues)
    │                Step 2: validate.py + lint-specs + checksums + tests
    │                Step 3: /docs-sync (if source changed)
    │                Step 4: Summary dashboard
    │                Step 5: Security advisory (if needed)
    │
    ├─── /ship-pr ──► (existing flow + tip suggesting /pre-pr)
    │
    └─── PR opened ──► CodeRabbit reviews SOURCE files only
                        (generated files excluded via .coderabbit.yml)
```

## Integration Points
- `.coderabbit.yml` integrates with CodeRabbit's GitHub App (external)
- `markdownlint` CI job integrates with `.github/workflows/ci.yml`
- `validate_source_syntax()` integrates with existing `validate.py` main flow
- Check 6 integrates with existing `hooks/pre-commit` check sequence
- `/pre-pr` integrates with existing `/core-review`, `/docs-sync` commands

## Ship Plan
1. Tasks 1-3, 5 are independent — can be implemented in parallel
2. Task 4 depends on Task 3 (FILE_EXISTS must be fixed first)
3. Tasks 6-7 are independent validate.py extensions
4. Task 8 (/pre-pr) depends on Tasks 3-7 (chains the tools they create)
5. Task 9 is a trivial follow-up to Task 8

## Risks & Mitigations
- **Risk:** `.coderabbit.yml` path filters may have syntax issues → **Mitigation:** Test with a small PR before the full rollout
- **Risk:** markdownlint may flag legitimate markdown patterns → **Mitigation:** `.markdownlint.json` disables MD013/MD033/MD041 which conflict with repo patterns
- **Risk:** Source syntax validation false positives on prose mentions of abstract ops → **Mitigation:** Only flag operations followed by `(` without arguments, not bare mentions in documentation text
