# Production Learnings — Tasks

## Task 1: Create `core/learnings.md` module

- [ ] Define learning storage format (learnings.json schema with version field)
- [ ] Define learning loading procedure (Phase 1, five-layer filtering)
- [ ] Define learning capture workflow (explicit, agent-proposed, reconciliation-based)
- [ ] Define "Reconsider When" evaluation protocol
- [ ] Define supersession chain mechanics
- [ ] Define `/specops learn` subcommand workflow
- [ ] Define `/specops reconcile --learnings` extension
- [ ] Define learning pattern detection (extends patterns.json)
- [ ] Define safety rules (no secrets, path containment, convention sanitization)
- [ ] Use abstract operations only

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Large
**Files:** `core/learnings.md` (new)

---

## Task 2: Integrate into workflow phases

- [ ] Phase 1 step 4: Add learnings loading after memory loading
- [ ] Phase 4 step 3: Add learning capture prompt after memory update
- [ ] Bugfix workflow: Add agent-proposed learning extraction
- [ ] Add `/specops learn` mode to dispatcher route table
- [ ] Add `/specops reconcile --learnings` extension to reconciliation module

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Medium
**Files:** `core/workflow.md`, `core/dispatcher.md`, `core/reconciliation.md`

---

## Task 3: Extend spec-schema.json and schema.json

- [ ] Add optional `productionLearnings` array to spec.json schema
- [ ] Add `learnings` config object to `.specops.json` schema (under `implementation`)
- [ ] Ensure `additionalProperties: false`, `maxLength` on strings, `maxItems` on arrays
- [ ] Run `python3 tests/check_schema_sync.py` to verify

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Medium
**Files:** `spec-schema.json`, `schema.json`

---

## Task 4: Wire into generator pipeline

- [ ] Add `"learnings": core["learnings"]` to `build_common_context()` in `generate.py`
- [ ] Add `{{ learnings }}` placeholder to all 4 Jinja2 templates
- [ ] Add `"learnings"` to relevant modes in `core/mode-manifest.json`

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Small
**Files:** `generator/generate.py`, `generator/templates/*.j2`, `core/mode-manifest.json`

---

## Task 5: Create learn mode file

- [ ] Create standalone capture workflow for `/specops learn`
- [ ] Handle both interactive and non-interactive platforms
- [ ] Validate inputs (spec-name exists, category valid, no secrets in description)
- [ ] Write to learnings.json and run pattern detection

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Medium
**Files:** New mode file, `core/dispatcher.md`

---

## Task 6: Add validation markers

- [ ] Define `LEARNINGS_MARKERS` in `generator/validate.py` (~8-10 markers)
- [ ] Add `check_markers_present()` call in `validate_platform()`
- [ ] Add same markers to cross-platform consistency check (Gap 31 — same commit)

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Small
**Files:** `generator/validate.py`, `tests/test_platform_consistency.py`

---

## Task 7: Extend memory pattern detection

- [ ] Add `learningPatterns` array to `patterns.json` format
- [ ] Cross-spec learning category grouping (2+ specs = pattern)
- [ ] Update `core/memory.md` to reference learnings pattern detection

**Status:** Pending
**Priority:** Medium
**IssueID:** None
**Estimated effort:** Small
**Files:** `core/memory.md`, `core/learnings.md`

---

## Task 8: Regenerate, validate, test

- [ ] Run `python3 generator/generate.py --all`
- [ ] Run `python3 generator/validate.py`
- [ ] Run `bash scripts/run-tests.sh`
- [ ] Verify all 4 platform outputs include learnings content

**Status:** Pending
**Priority:** High
**IssueID:** None
**Estimated effort:** Small
**Files:** All generated platform outputs

---

## Task 9: Update documentation and CLAUDE.md

- [ ] Add learnings to CLAUDE.md (new core module, config option)
- [ ] Update CHANGELOG.md with unreleased entry
- [ ] Update docs/REFERENCE.md with `/specops learn` command
- [ ] Update docs/STRUCTURE.md with learnings.json file

**Status:** Pending
**Priority:** Medium
**IssueID:** None
**Estimated effort:** Small
**Files:** `CLAUDE.md`, `CHANGELOG.md`, `docs/REFERENCE.md`, `docs/STRUCTURE.md`

---

## Task 10: Dogfood — seed learnings from project history

- [ ] Scan completed specs and git history for production-relevant insights
- [ ] Seed `learnings.json` with 3-5 learnings from SpecOps project itself
- [ ] Verify Phase 1 loading surfaces relevant learnings correctly

**Status:** Pending
**Priority:** Medium
**IssueID:** None
**Estimated effort:** Small
**Files:** `.specops/memory/learnings.json` (new)
