# Design: Plan Mode Blocking Enforcement

## Overview

This feature upgrades the ExitPlanMode hook enforcement from advisory to blocking using a marker file state machine. When a plan is approved, the PostToolUse hook creates a `.plan-pending-conversion` marker. A PreToolUse guard then blocks Write/Edit operations on non-spec files until `/specops from-plan` converts the plan and removes the marker.

## Architecture

### State Machine

```text
ExitPlanMode called
    |
    v
PostToolUse hook fires
    |-- .specops.json exists? No --> exit 0 (not a SpecOps project)
    |-- Yes --> create .specops/.plan-pending-conversion marker
    |           echo enforcement message
    v
Agent tries Write/Edit on a file
    |
    v
PreToolUse hook fires
    |-- marker exists? No --> exit 0 (allow)
    |-- Yes --> is target path in specsDir or .claude/plans/ or .claude/memory/?
    |     |-- Yes --> exit 0 (allow -- from-plan creates spec files)
    |     |-- No --> exit 2 (BLOCK with message: "Run /specops from-plan first")
    v
/specops from-plan runs
    |-- converts plan to spec
    |-- enforcement pass (step 6.5) succeeds
    |-- removes marker: rm -f .specops/.plan-pending-conversion
    v
Write/Edit now unblocked -- implementation proceeds through spec
```

### PostToolUse Hook (Upgraded)

Current (advisory):
```bash
test -f .specops.json && echo "SPECOPS HOOK: ..." # specops-hook
```

New (creates marker + advisory):
```bash
if [ -f .specops.json ]; then SPECS_DIR=$(python3 -c "import json; print(json.load(open('.specops.json')).get('specsDir','.specops'))" 2>/dev/null || echo ".specops"); mkdir -p "$SPECS_DIR"; touch "$SPECS_DIR/.plan-pending-conversion"; echo "SPECOPS ENFORCEMENT: Plan approved. Marker set at $SPECS_DIR/.plan-pending-conversion. Write/Edit on non-spec files is blocked until /specops from-plan converts the plan into a structured spec."; fi # specops-hook
```

Key elements:
- Reads `specsDir` from `.specops.json` (defaults to `.specops`)
- Creates the directory if needed (`mkdir -p`)
- Creates the marker file (`touch`)
- Emits a user-visible enforcement message
- `# specops-hook` marker preserved for idempotent detection

### PreToolUse Guard (New)

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "python3 -c \"\nimport json, sys, os\nif not os.path.isfile('.specops.json'):\n    sys.exit(0)\nspecs = json.load(open('.specops.json')).get('specsDir', '.specops')\nmarker = os.path.join(specs, '.plan-pending-conversion')\nif not os.path.isfile(marker):\n    sys.exit(0)\ntry:\n    data = json.load(sys.stdin)\n    fp = data.get('file_path', '')\nexcept Exception:\n    sys.exit(0)\nallowed = [specs + '/', '.claude/plans/', '.claude/memory/']\nif any(a in fp for a in allowed):\n    sys.exit(0)\nprint('SPECOPS ENFORCEMENT: A plan was approved but not yet converted to a spec.', file=sys.stderr)\nprint('Run /specops from-plan to convert the plan before implementing.', file=sys.stderr)\nprint(f'Blocked write to: {fp}', file=sys.stderr)\nsys.exit(2)\n\" # specops-plan-guard"
    }
  ]
}
```

This Python script:
1. Checks `.specops.json` exists (not a SpecOps project = allow)
2. Reads `specsDir` from config
3. Checks marker file exists (no marker = allow)
4. Reads `file_path` from tool input (stdin JSON)
5. Allows writes to specsDir, `.claude/plans/`, `.claude/memory/`
6. Blocks everything else with exit code 2

### Marker File Lifecycle in from-plan.md

Two integration points:
- **After step 1** (plan content received): Detect marker, notify user that writes will be unblocked after conversion
- **After step 6.5** (enforcement pass succeeds): Remove marker with `rm -f`, notify user that Write/Edit is unblocked

If from-plan fails before step 6.5, the marker stays, keeping writes blocked until conversion succeeds.

### Dispatcher Step 10.5 Update

Reference the hook-created marker in the post-plan acceptance gate:

> The ExitPlanMode hook creates a `.plan-pending-conversion` marker that blocks Write/Edit on non-spec files. If the marker exists when the dispatcher runs, it indicates a plan was approved but not yet converted. Route to from-plan mode.

## Architecture Decisions

### AD-1: Marker File vs In-Memory State
**Decision:** Use a marker file (`.plan-pending-conversion`) rather than in-memory state.
**Rationale:** Claude Code hooks run as separate processes; they cannot share in-memory state. A marker file persists across tool invocations, is visible to both PostToolUse and PreToolUse hooks, and survives context resets.

### AD-2: PreToolUse Exit Code 2 for Blocking
**Decision:** Use exit code 2 to block Write/Edit operations.
**Rationale:** Claude Code's PreToolUse hook protocol treats exit code 2 as a blocking signal that prevents the tool from executing. Exit code 0 allows, exit code 1 is a warning. This is the correct mechanism for enforcement.

### AD-3: Python3 for PreToolUse Guard
**Decision:** Use Python3 inline script for the PreToolUse guard.
**Rationale:** The guard needs to parse JSON from stdin (tool input), read `.specops.json` config, and perform path matching. Python3 handles all of these natively. This matches the existing installer pattern for PostToolUse hook injection.

### AD-4: Allowed Path Prefixes
**Decision:** Allow writes to `specsDir/`, `.claude/plans/`, and `.claude/memory/` when the marker is active.
**Rationale:** `/specops from-plan` creates spec files in specsDir. Plan files live in `.claude/plans/`. Memory files live in `.claude/memory/`. All three must be writable during the conversion process.

### AD-5: Upgrade Existing PostToolUse Hook In-Place
**Decision:** Replace the existing advisory PostToolUse command rather than adding a second hook.
**Rationale:** The existing advisory hook and the new marker-creating hook serve the same purpose (ExitPlanMode interception). Having both would create confusion and duplicate output. The `# specops-hook` marker enables the installer to find and replace the existing command.

## Component Interactions

```text
.claude/settings.local.json (or settings.json)
  |
  |-- hooks.PostToolUse[ExitPlanMode] --> creates marker, emits message
  |-- hooks.PreToolUse[Write|Edit]    --> checks marker, blocks or allows
  |
.specops/.plan-pending-conversion (marker file)
  |
  |-- created by: PostToolUse hook
  |-- checked by: PreToolUse hook
  |-- removed by: from-plan mode (after step 6.5)
  |
core/from-plan.md
  |-- step 1: detects marker, notifies user
  |-- after step 6.5: removes marker, notifies user
  |
core/dispatcher.md
  |-- step 10.5: references marker in post-plan acceptance gate
```

## Files to Modify

| File | Change |
|---|---|
| `.claude/settings.local.json` | Update PostToolUse command + add PreToolUse hook |
| `platforms/claude/install.sh` | Update PostToolUse command + add PreToolUse installation |
| `scripts/remote-install.sh` | Mirror installer changes |
| `core/from-plan.md` | Add marker detection at start + removal after step 6.5 |
| `core/dispatcher.md` | Reference marker in step 10.5 |
| `.gitignore` | Add `.plan-pending-conversion` |
| `core/dependency-introduction.md` | DELETE (created outside SpecOps workflow) |
| `CLAUDE.md` | Document enforcement hooks |
| `docs/REFERENCE.md` | Document marker file and hooks behavior |
| `CHANGELOG.md` | Note enforcement upgrade |
