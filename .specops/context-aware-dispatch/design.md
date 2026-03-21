# Design: Context-Aware Dispatch

## Architecture Overview
The monolithic SKILL.md (4,596 lines) is split into a lightweight dispatcher + per-mode files. The dispatcher handles routing, enforcement gates, and sub-agent spawning. Mode files contain the actual workflow instructions. The generator assembles both from the same `core/*.md` modules, preserving the 3-layer architecture. Only Claude gets this treatment — other platforms keep monolithic output.

## Technical Decisions

### Decision 1: Two-File Architecture for Claude Only
**Context:** Need to reduce context load without breaking other platforms
**Options Considered:**
1. Split all platforms — requires sub-agent capability on all
2. Split Claude only — other platforms lack canDelegateTask

**Decision:** Option 2 — Claude-only split
**Rationale:** Only Claude has `canDelegateTask: true`. Other platforms have no sub-agent infrastructure. Splitting them would produce files they can't load on demand.

### Decision 2: File-Based Mode Loading (Not Inline Prompts)
**Context:** Sub-agents need mode-specific instructions
**Options Considered:**
1. Inline mode instructions in dispatcher — defeats the purpose (back to monolithic)
2. Read mode files at dispatch time — keeps dispatcher small, files are version-controlled

**Decision:** Option 2 — file-based mode loading
**Rationale:** Files can be validated independently, keep the dispatcher under 400 lines, and follow the existing pattern of generated files checked into git.

### Decision 3: Enforcement Gates in Dispatcher (Not Sub-Agent)
**Context:** Gates like task tracking IssueID check get skipped under context pressure
**Options Considered:**
1. Keep gates in sub-agent instructions — same failure mode as today
2. Move critical gates to dispatcher, run before spawning sub-agent

**Decision:** Option 2 — dispatcher-enforced gates
**Rationale:** The dispatcher has minimal context (~350 lines). Gates run as file reads before the sub-agent is spawned. The sub-agent literally cannot execute without gates passing. This is the key reliability improvement.

### Decision 4: Mode Manifest JSON for Module Grouping
**Context:** Generator needs to know which core modules go into each mode file
**Options Considered:**
1. Hardcode groupings in generate.py — fragile, not discoverable
2. JSON manifest file mapping modes to modules — declarative, testable

**Decision:** Option 2 — `core/mode-manifest.json`
**Rationale:** A manifest is self-documenting, can be validated in CI, and makes adding new modes a data change rather than a code change.

### Decision 5: Monolithic Backward Compatibility
**Context:** Existing Claude installs have a monolithic SKILL.md
**Options Considered:**
1. Break backward compatibility — old installs stop working
2. Generate both monolithic and split — old installs still work, new installs get split

**Decision:** Option 2 — generate both during transition
**Rationale:** Users who haven't updated their installation still get a working (monolithic) skill. The dispatcher replaces it on next install. The monolithic file can be deprecated after one release cycle.

## Product Module Design

### Module 1: Dispatcher (SKILL.md, ~350 lines)
**Responsibility:** Route invocations, enforce gates, spawn sub-agents
**Interface:** Claude Code skill entry point (`/specops`)
**Dependencies:** Mode files in `modes/` directory

### Module 2: Mode Files (modes/*.md, 13 files)
**Responsibility:** Contain mode-specific workflow instructions
**Interface:** Read by dispatcher, passed as sub-agent prompt
**Dependencies:** None (self-contained per mode)

### Module 3: Mode Manifest (core/mode-manifest.json)
**Responsibility:** Map mode names to core module lists
**Interface:** Read by generator during build
**Dependencies:** core/*.md modules

### Module 4: Generator Extension (generate.py)
**Responsibility:** Produce dispatcher + mode files from core modules
**Interface:** `python3 generator/generate.py --all`
**Dependencies:** core/mode-manifest.json, generator/templates/claude-dispatcher.j2

## System Flow

```
/specops invoked
    │
    ▼
Dispatcher loaded (~350 lines)
    │
    ├── Config loading
    ├── Safety rules
    ├── Mode detection (12 patterns)
    │
    ▼
Mode identified (e.g., "from-plan")
    │
    ├── Pre-dispatch gates (if Phase 3)
    │   └── 7-point checklist (file reads only)
    │
    ▼
Read modes/from-plan.md (~120 lines)
    │
    ▼
Spawn sub-agent with:
    [Shared context (~80 lines)] + [Mode instructions (~120 lines)]
    = ~200 lines total context (was 4,596)
    │
    ▼
Sub-agent executes autonomously
    │
    ▼
Dispatcher runs post-dispatch verification
```

## Integration Points
- Generator reads `core/mode-manifest.json` to assemble mode files
- Dispatcher reads `modes/*.md` at runtime via Read tool
- Dispatcher spawns sub-agents via Agent tool
- Validator checks markers across dispatcher + mode files (union)
- `install.sh` and `remote-install.sh` copy `modes/` directory

## Ship Plan
1. Phase A: Core layer (manifest + dispatcher module) — foundation
2. Phase B: Generator changes — produces the files
3. Phase C: Validator updates — CI catches regressions
4. Phase D: /pre-pr IssueID check — quick win
5. Phase E: Installation + testing — user-facing
6. Phase F: README + plugin — documentation

## Risks & Mitigations
- **Risk:** Sub-agent can't read mode files (wrong path) → **Mitigation:** Dispatcher includes fallback message if file not found; install.sh copies modes/ directory
- **Risk:** Validator regression from split-file checking → **Mitigation:** Run before/after comparison; keep monolithic check as secondary during transition
- **Risk:** Mode manifest drifts from core modules → **Mitigation:** CI test verifying manifest references all core/*.md files
