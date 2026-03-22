# Design: From-Plan Enforcement Checklist Integration

## Architecture Overview

Add a new step 6.5 ("Post-Conversion Enforcement Pass") to `core/from-plan.md` between the gap-fill rule (step 6) and completion (step 7). This step runs the same 8 checks the dispatcher's Pre-Phase-3 Enforcement Checklist defines, adapted for the from-plan context where artifacts were just created rather than already existing. The pass is auto-remediation-first: it creates missing directories and writes missing context summaries rather than just failing.

## Technical Decisions

### Decision 1: Inline Enforcement in from-plan.md (Not Shared Function)

**Context:** Should the 8 checks be factored into a shared module that both dispatcher.md and from-plan.md reference?
**Options Considered:**

1. Shared enforcement module (`core/enforcement-checklist.md`) referenced by both
2. Inline the checks directly in `core/from-plan.md` step 6.5

**Decision:** Option 2 -- Inline in from-plan.md
**Rationale:** The dispatcher checks are pre-Phase-3 guards (verify artifacts exist before spawning implementation). The from-plan checks are post-conversion guards (verify the just-created artifacts meet standards). They share the same 8 check categories but have different remediation behavior: dispatcher STOPs, from-plan auto-remediates. Creating a shared module for 8 checks with divergent behavior adds abstraction without reducing duplication. The simplicity principle applies -- the shared module would be an abstraction used twice with different behavior at each call site.

### Decision 2: Auto-Remediation-First Strategy

**Context:** When a check fails (e.g., steering directory missing), should from-plan stop or fix it?
**Options Considered:**

1. Stop and notify (matching dispatcher behavior)
2. Auto-remediate, then verify, then stop only if remediation failed

**Decision:** Option 2 -- Auto-remediate first
**Rationale:** The dispatcher stops because it expects these artifacts to already exist (they should have been created in Phase 1/2). From-plan skips Phase 1 entirely -- these artifacts were never created. Stopping would always fail for the first from-plan conversion in a project. Auto-remediation matches what Phase 1 does: create steering directory with templates, create memory directory, write context summary.

### Decision 3: Context Summary Content for From-Plan Conversions

**Context:** What goes in the Phase 1 Context Summary when from-plan creates it? There was no Phase 1.
**Decision:** Write a from-plan-specific context summary that records: config status, conversion source (inline/file/auto-discovered), steering directory status, memory directory status, detected vertical, and affected files from the plan.
**Rationale:** The context summary's purpose is to provide the Phase 3 implementer with the setup context. For from-plan, the relevant context is the conversion source and what the enforcement pass verified/created.

### Decision 4: Step Numbering as 6.5

**Context:** Where to insert the enforcement pass in the from-plan workflow?
**Decision:** New step 6.5 between step 6 (gap-fill) and step 7 (complete)
**Rationale:** Follows the project convention of sub-step notation (N.5) to avoid renumbering existing steps. Step 6 completes artifact generation; step 6.5 verifies artifacts; step 7 declares completion. The enforcement pass is a gate between generation and completion.

## Component Design

### Component 1: Post-Conversion Enforcement Pass

**File:** `core/from-plan.md`
**Location:** New step 6.5 between step 6 and step 7

**The 8 checks (mapped from dispatcher's Pre-Phase-3 Enforcement Checklist):**

1. **spec.json exists and status is valid**: FILE_EXISTS(`<specsDir>/<specName>/spec.json`). Since from-plan just created it in step 5, this is a sanity check. Verify status is `draft`. If missing, this is an internal error -- NOTIFY_USER and STOP.

2. **implementation.md exists with context summary**: FILE_EXISTS(`<specsDir>/<specName>/implementation.md`). If it exists but lacks `## Phase 1 Context Summary`, write the from-plan context summary (see Decision 3). If the file does not exist, create it with template headers and the context summary.

3. **tasks.md exists**: FILE_EXISTS(`<specsDir>/<specName>/tasks.md`). Since from-plan just created it, this is a sanity check. If missing, NOTIFY_USER and STOP.

4. **design.md exists**: FILE_EXISTS(`<specsDir>/<specName>/design.md`). Sanity check. If missing, NOTIFY_USER and STOP.

5. **IssueID population**: READ_FILE(`.specops.json`) and check `team.taskTracking`. If taskTracking is not `"none"`, READ_FILE(`<specsDir>/<specName>/tasks.md`) and find all tasks with `**Priority:** High` or `**Priority:** Medium`. For each, verify `**IssueID:**` is set to a valid identifier. If any High/Medium task has IssueID `None`, create external issues following the Task Tracking Integration protocol, then write IssueIDs back to `tasks.md`. If issue creation fails, NOTIFY_USER with the list of tasks needing IssueIDs and STOP.

6. **Steering directory exists**: FILE_EXISTS(`<specsDir>/steering/`). If false, create it with foundation templates (product.md, tech.md, structure.md) following the Steering Files module. NOTIFY_USER that steering files were created.

7. **Memory directory exists**: FILE_EXISTS(`<specsDir>/memory/`). If false, RUN_COMMAND(`mkdir -p <specsDir>/memory`).

8. **Spec dependency gate**: READ_FILE(`<specsDir>/<specName>/spec.json`) and check `specDependencies`. For each entry with `required: true`, verify the dependency spec has `status == "completed"`. If any required dependency is not met, NOTIFY_USER and STOP. If `specDependencies` is absent or empty, pass trivially.

**After all 8 checks pass:** Proceed to step 7 (complete).

**Protocol breach language:** "Skipping the post-conversion enforcement pass is a protocol breach -- from-plan specs must pass the same structural checks as dispatcher-routed specs before being declared ready for implementation."

### Component 2: Validator Marker Update

**File:** `generator/validate.py`
**Changes:** Add "post-conversion enforcement" or "enforcement pass" to `FROM_PLAN_MARKERS` to verify the enforcement section appears in all generated platform outputs.

### Component 3: Generator Pipeline (No Changes Expected)

The generator already includes `core/from-plan.md` in the from-plan mode's module list (via `core/mode-manifest.json`). Adding step 6.5 to `core/from-plan.md` will automatically flow through the existing pipeline. No generator changes needed.

## Sequence Diagram

```text
User -> SpecOps: "from-plan" with plan content
SpecOps -> SpecOps: Steps 1-6 (parse, generate artifacts)
SpecOps -> SpecOps: Step 6.5 Enforcement Pass
  SpecOps -> FileSystem: Check spec.json exists, status=draft
  SpecOps -> FileSystem: Check implementation.md, write context summary
  SpecOps -> FileSystem: Check tasks.md exists
  SpecOps -> FileSystem: Check design.md exists
  SpecOps -> Config: Check taskTracking
  [if taskTracking != "none"]
    SpecOps -> Tracker: Create issues for High/Medium tasks
    SpecOps -> FileSystem: Write IssueIDs to tasks.md
  SpecOps -> FileSystem: Check/create steering directory
  SpecOps -> FileSystem: Check/create memory directory
  SpecOps -> FileSystem: Check spec dependencies
SpecOps -> User: "Spec ready for implementation" (step 7)
```

## Testing Strategy

- **Generator validation:** `python3 generator/validate.py` (ensures from-plan markers include enforcement)
- **Platform consistency:** `python3 tests/test_platform_consistency.py`
- **Build test:** `python3 tests/test_build.py`
- **Full suite:** `bash scripts/run-tests.sh`
- **Manual verification:** Run from-plan conversion in a project with `taskTracking: "github"` and verify IssueIDs are created

## Risks & Mitigations

- **Risk 1:** Enforcement checks duplicate code from dispatcher.md -- future changes to one might miss the other. **Mitigation:** The checks reference the dispatcher's checklist by name in comments, making the relationship discoverable. A future spec could extract a shared module if duplication becomes a maintenance burden.
- **Risk 2:** Auto-remediation of steering/memory directories during from-plan might create empty steering files that the user doesn't expect. **Mitigation:** NOTIFY_USER when directories are created, consistent with Phase 1 behavior.

## Dependencies & Blockers

### Spec Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| workflow-enforcement-gates | Established enforcement pattern | No | Completed |
| plan-to-specops-automation | Current from-plan workflow | No | Completed |

### Cross-Spec Blockers

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| ------- | ------------- | --------------- | ----------------- | ------ |
| ---     | ---           | ---             | ---               | ---    |

## Future Enhancements

- Extract enforcement checks into a shared module if the pattern is needed by a third caller
- Add enforcement pass to pipeline mode if it also bypasses the dispatcher checks
