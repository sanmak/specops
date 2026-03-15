# Design: Workflow Enforcement Gates

## Architecture Overview
Surgical text edits to 2 core modules and 2 validation files. No new modules, no schema changes, no step renumbering. The changes apply the existing "protocol breach" enforcement pattern (proven in the Task State Machine module) to three weak workflow points.

## Technical Decisions

### Decision 1: Enforcement Language Pattern
**Context:** Need a pattern agents reliably follow. Multiple options exist in the codebase.
**Options Considered:**
1. "MUST" language (used in Phase 1 step 5 currently) — moderate compliance
2. "protocol breach" language (used in Task State Machine) — high compliance, agents trained on this

**Decision:** "protocol breach" language
**Rationale:** Already proven effective in task-tracking.md (3 occurrences). Agents with protocol breach training treat violations with maximum gravity. Consistent with existing enforcement infrastructure.

### Decision 2: Phase 1 Content-Level Check
**Context:** Current pre-flight check only verifies directory existence. An empty directory passes.
**Options Considered:**
1. Check directory exists only (current) — weak
2. Check at least one .md file exists (LIST_DIR) — catches empty directories
3. Check frontmatter validity of each steering file — too complex for a gate

**Decision:** LIST_DIR for at least one `.md` file
**Rationale:** The gate's job is to verify step 3 ran, not to re-validate its output. Frontmatter validation belongs to the loading procedure. One `.md` file proves the foundation templates were created.

### Decision 3: Task Tracking Gate — Attempt vs Success
**Context:** The gate was "advisory, not blocking" to avoid blocking implementation when external tools fail. Need to enforce without being fragile.
**Options Considered:**
1. Make gate fully blocking (100% success required) — too fragile, external CLI failures are common
2. Keep advisory (current) — agents skip it entirely
3. Enforce attempted creation, allow graceful degradation on failure — best of both

**Decision:** Enforce attempt, not success
**Rationale:** An IssueID of `FAILED — <reason>` proves the agent tried; `None` proves it did not. The existing Graceful Degradation section already handles CLI failures correctly. The protocol breach applies to not trying, not to external tool failures.

### Decision 4: Phase 3 Step 1 Structure
**Context:** Review gate and task tracking gate are crammed into one paragraph.
**Options Considered:**
1. Keep single paragraph (current) — task tracking gate buried
2. Split into sub-list with named gates — clear structure, agents parse sub-lists reliably

**Decision:** Structured sub-list with named gates
**Rationale:** Agents parse structure (headings, sub-lists) more reliably than inline bold labels. The review gate already has its own section in review-workflow.md; the task tracking gate deserves equal structural visibility.

## Component Design

### core/workflow.md Edits (3 locations)

**Phase 1 Step 5** (line 28-34):
- Replace current step 5 text with enforcement gate version
- Add LIST_DIR content check
- Add STOP consequence
- Separate .gitignore check visually

**Phase 3 Step 1** (line 112):
- Replace single paragraph with sub-list
- Named gates: Review gate, Task tracking gate
- Status update after "both gates pass"

**Phase 4 Step 3** (line 135):
- Add "(mandatory)" to heading
- Add "protocol breach" and forward reference to step 5

### core/config-handling.md Edit (1 location)

**Task Tracking Gate** (lines 134-141):
- Remove "advisory, not blocking"
- Add "protocol breach" for skipping
- Replace steps 4-5 with specific scenarios (partial/total failure)
- Add step 6 as enforcement principle anchor

### Validation Edits (2 files)

**generator/validate.py**: Add `"attempted creation"` to `EXTERNAL_TRACKING_MARKERS`
**tests/test_platform_consistency.py**: Add `"attempted creation"` to `REQUIRED_MARKERS["external_tracking"]`

## Testing Strategy
- Run `python3 generator/generate.py --all` to regenerate platform outputs
- Run `python3 generator/validate.py` to verify markers propagated
- Run `bash scripts/run-tests.sh` for full test suite
- Spot-check: `grep -c "protocol breach" platforms/claude/SKILL.md` >= 5
- Spot-check: `grep "advisory, not blocking" platforms/claude/SKILL.md` returns nothing

## Risks & Mitigations
- **Risk:** Phase 3 step 1 restructure breaks Jinja2 template rendering → **Mitigation:** Templates inject `{{ workflow }}` wholesale; markdown restructuring within the module is safe
- **Risk:** New marker fails validation for some platforms → **Mitigation:** The "attempted creation" text exists in config-handling.md which is included in all platform outputs
