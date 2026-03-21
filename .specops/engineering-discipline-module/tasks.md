# Implementation Tasks: Engineering Discipline Module

## Task 1: Create core/engineering-discipline.md

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #136
**Dependencies:** None

**Description:**
Create the engineering discipline module as a new core file following the exact structure of `core/writing-quality.md`. The module maps 11 named thinkers across 4 domains to 14 concrete, testable rules. Rules that reinforce existing modules include `(reinforces: <module>)` cross-references. The module includes a 3-item silent self-check and a sources section attributing each rule.

**Implementation Steps:**

1. Create `core/engineering-discipline.md` with the `## Engineering Discipline` heading
2. Add introductory paragraph explaining when these rules apply (Phase 2 design, Phase 3 implementation)
3. Add `### Architecture & Design Integrity` section with 4 rules (Brooks, Liskov, Hohpe)
4. Add `### Testing & Validation Philosophy` section with 4 rules (Beck, Dijkstra, Feathers)
5. Add `### Reliability & Failure Reasoning` section with 3 rules (Leveson, Taleb)
6. Add `### Constraints & Quality Gates` section with 3 rules (Goldratt, Deming, Humble)
7. Add `### Self-Check` section with 3 silent verification items
8. Add `### Sources` section attributing all 11 leaders to specific rules
9. Verify total line count is under 60 lines

**Files to Modify:**

- `core/engineering-discipline.md` (new file)

**Acceptance Criteria:**

- [x] File exists at `core/engineering-discipline.md`
- [x] Contains 4 domain sections with 14 rules total
- [x] Contains `### Self-Check` with 3 items
- [x] Contains `### Sources` with 11 named leaders
- [x] Cross-references use `(reinforces: <module>)` pattern
- [x] File is under 60 lines
- [x] Passes `npx markdownlint-cli2 "core/engineering-discipline.md"`

## Task 2: Wire into generator — build_common_context()

**Status:** Completed
**Priority:** High
**Effort:** Small
**IssueID:** #137
**Dependencies:** Task 1

**Description:**
Add the engineering discipline module to the shared render context in `generator/generate.py` so all platform generators can access it. Add `"engineering_discipline": core["engineering-discipline"]` to the `build_common_context()` function after the `writing_quality` entry.

**Implementation Steps:**

1. Open `generator/generate.py`
2. Locate `build_common_context()` function (around line 326)
3. Find the `"writing_quality": core["writing-quality"],` line (around line 349)
4. Add `"engineering_discipline": core["engineering-discipline"],` on the next line
5. Verify no syntax errors by running `python3 -c "import generator.generate"`

**Files to Modify:**

- `generator/generate.py`

**Acceptance Criteria:**

- [x] `build_common_context()` includes `"engineering_discipline"` key
- [x] Key is placed after `"writing_quality"` for consistency
- [x] `python3 generator/generate.py --all` runs without import errors

## Task 3: Add template placeholder to all 4 Jinja2 templates

**Status:** Completed
**Priority:** High
**Effort:** Small
**IssueID:** #138
**Dependencies:** Task 2

**Description:**
Add `{{ engineering_discipline }}` to all 4 Jinja2 templates immediately after `{{ writing_quality }}`. This ensures the engineering discipline content appears in all generated platform outputs, grouped with the writing quality module.

**Implementation Steps:**

1. Edit `generator/templates/claude.j2` — add `{{ engineering_discipline }}` on a new line after `{{ writing_quality }}`
2. Edit `generator/templates/codex.j2` — add `{{ engineering_discipline }}` on a new line after `{{ writing_quality }}`
3. Edit `generator/templates/cursor.j2` — add `{{ engineering_discipline }}` on a new line after `{{ writing_quality }}`
4. Edit `generator/templates/copilot.j2` — add `{{ engineering_discipline }}` on a new line after `{{ writing_quality }}`

**Files to Modify:**

- `generator/templates/claude.j2`
- `generator/templates/codex.j2`
- `generator/templates/cursor.j2`
- `generator/templates/copilot.j2`

**Acceptance Criteria:**

- [x] All 4 templates contain `{{ engineering_discipline }}` after `{{ writing_quality }}`
- [x] Templates have blank lines separating the two placeholders (matching existing style)

## Task 4: Add to mode manifest

**Status:** Completed
**Priority:** High
**Effort:** Small
**IssueID:** #139
**Dependencies:** Task 1

**Description:**
Add `"engineering-discipline"` to the module lists for `spec` and `from-plan` modes in `core/mode-manifest.json`. This ensures the Claude dispatcher loads the engineering discipline module when entering these modes.

**Implementation Steps:**

1. Open `core/mode-manifest.json`
2. In the `from-plan` mode `modules` array, add `"engineering-discipline"` after `"writing-quality"`
3. In the `spec` mode `modules` array, add `"engineering-discipline"` after `"writing-quality"`
4. Validate JSON syntax: `python3 -c "import json; json.load(open('core/mode-manifest.json'))"`

**Files to Modify:**

- `core/mode-manifest.json`

**Acceptance Criteria:**

- [x] `from-plan` mode modules array includes `"engineering-discipline"` after `"writing-quality"`
- [x] `spec` mode modules array includes `"engineering-discipline"` after `"writing-quality"`
- [x] JSON is valid (no syntax errors)

## Task 5: Add validation markers to validate.py

**Status:** Completed
**Priority:** High
**Effort:** Medium
**IssueID:** #140
**Dependencies:** Task 1

**Description:**
Add `ENGINEERING_DISCIPLINE_MARKERS` constant and wire it into both `validate_platform()` and the cross-platform consistency check loop. All 3 additions must be in the same commit per the project rule documented in CLAUDE.md.

**Implementation Steps:**

1. Add `ENGINEERING_DISCIPLINE_MARKERS` constant after `WRITING_QUALITY_MARKERS` (around line 244) with section headings and content markers
2. Add `check_markers_present()` call in `validate_platform()` after the writing-quality check (around line 567)
3. Add `+ ENGINEERING_DISCIPLINE_MARKERS` to the cross-platform consistency marker concatenation (around line 1104)

**Files to Modify:**

- `generator/validate.py`

**Acceptance Criteria:**

- [x] `ENGINEERING_DISCIPLINE_MARKERS` constant exists with section headings (`## Engineering Discipline`, `### Architecture & Design Integrity`, etc.) and content markers (`substitutability`, `characterization test`)
- [x] `validate_platform()` calls `check_markers_present()` for engineering-discipline markers
- [x] Cross-platform consistency loop includes `ENGINEERING_DISCIPLINE_MARKERS`
- [x] All 3 changes are in the same commit

## Task 6: Regenerate and validate all platform outputs

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #141
**Dependencies:** Tasks 1-5

**Description:**
Run the generator to produce updated platform outputs, then validate them. This confirms the end-to-end pipeline works correctly with the new module.

**Implementation Steps:**

1. Run `python3 generator/generate.py --all`
2. Run `python3 generator/validate.py` — expect 0 errors
3. Run `bash scripts/run-tests.sh` — expect all tests pass
4. Verify presence: `grep "Engineering Discipline" platforms/claude/modes/spec.md`
5. Verify presence: `grep "Engineering Discipline" platforms/cursor/specops.mdc`
6. Verify presence: `grep "Engineering Discipline" platforms/codex/SKILL.md`
7. Verify presence: `grep "Engineering Discipline" platforms/copilot/specops.instructions.md`
8. Lint the new module: `npx markdownlint-cli2 "core/engineering-discipline.md"`

**Files to Modify:**

- `platforms/claude/SKILL.monolithic.md` (regenerated)
- `platforms/claude/modes/spec.md` (regenerated)
- `platforms/claude/modes/from-plan.md` (regenerated)
- `platforms/cursor/specops.mdc` (regenerated)
- `platforms/codex/SKILL.md` (regenerated)
- `platforms/copilot/specops.instructions.md` (regenerated)
- `skills/specops/SKILL.monolithic.md` (regenerated)
- `skills/specops/modes/spec.md` (regenerated)
- `skills/specops/modes/from-plan.md` (regenerated)

**Acceptance Criteria:**

- [x] `python3 generator/generate.py --all` exits 0
- [x] `python3 generator/validate.py` exits 0
- [x] `bash scripts/run-tests.sh` reports all tests pass
- [x] All 4 platform outputs contain "Engineering Discipline"
- [x] Markdown lint passes for `core/engineering-discipline.md`

## Task 7: Update checksums

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #142
**Dependencies:** Task 6

**Description:**
Regenerate `CHECKSUMS.sha256` to include the new `core/engineering-discipline.md` file and updated generated outputs. The pre-commit hook enforces checksum freshness.

**Implementation Steps:**

1. Run `shasum -a 256` on all checksummed files (follow existing `CHECKSUMS.sha256` file list plus the new core file)
2. Update `CHECKSUMS.sha256` with the new checksums
3. Verify: `shasum -a 256 -c CHECKSUMS.sha256`

**Files to Modify:**

- `CHECKSUMS.sha256`

**Acceptance Criteria:**

- [x] `CHECKSUMS.sha256` includes `core/engineering-discipline.md`
- [x] `shasum -a 256 -c CHECKSUMS.sha256` passes with no failures

## Task 8: Update documentation

**Status:** Completed
**Priority:** Medium
**Effort:** Small
**IssueID:** #143
**Dependencies:** Task 1

**Description:**
Update `docs/STRUCTURE.md` to list the new module in the core directory tree and update `README.md` to mention engineering discipline in the philosophy section alongside the existing writing quality reference.

**Implementation Steps:**

1. Edit `docs/STRUCTURE.md` — add `│   ├── engineering-discipline.md          # Engineering discipline rules for design and implementation` after the `dependency-safety.md` line in the directory tree
2. Edit `README.md` — add engineering discipline mention in the Writing Philosophy section (around line 139-141), renaming it to "Writing & Engineering Philosophy" or appending a sentence about engineering discipline
3. Add mapping to `.claude/commands/docs-sync.md` for the new core module

**Files to Modify:**

- `docs/STRUCTURE.md`
- `README.md`
- `.claude/commands/docs-sync.md`

**Acceptance Criteria:**

- [x] `docs/STRUCTURE.md` lists `engineering-discipline.md` in the core module tree
- [x] `README.md` references engineering discipline with a link to `core/engineering-discipline.md`
- [x] `.claude/commands/docs-sync.md` has a mapping row for `core/engineering-discipline.md`

**Tests Required:**

- [x] `python3 generator/validate.py` passes docs coverage check (validates all core modules appear in `docs/STRUCTURE.md` and `docs-sync.md`)
