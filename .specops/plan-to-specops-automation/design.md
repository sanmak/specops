# Design: Plan Mode → SpecOps Workflow Automation

## Architecture Overview
A 3-layer enforcement approach that bridges Claude Code's plan mode and SpecOps's from-plan workflow. Layer 1 enhances the core from-plan module to accept file paths. Layer 2 adds a behavioral enforcement gate in the workflow. Layer 3 adds a convenience bridge in the `/resume-plan` command. A platform config update enables auto-discovery.

## Architecture Decisions

### Decision 1: Universal Enforcement (No Config Flag)
**Context:** Should plan-to-spec routing be opt-in via `.specops.json`?
**Decision:** Universal enforcement — any SpecOps-configured project automatically enforces plan→spec conversion
**Rationale:** Prior feedback: "config flags without deterministic workflow instructions are dead features." The enforcement is in workflow instructions, not a boolean toggle.

### Decision 2: 3-Layer Defense-in-Depth
**Context:** How to enforce plan→spec routing when no plan-mode-exit hook exists?
**Options Considered:**
1. CLAUDE.md instruction only — simple but not deterministic (agents skip advisory steps)
2. `/resume-plan` enhancement only — only works when explicitly invoked
3. 3-layer approach (core module + workflow gate + command bridge)

**Decision:** Option 3 — 3-layer approach
**Rationale:** Each layer catches a different entry path: (1) explicit from-plan invocation with file path, (2) implicit post-plan acceptance detection, (3) `/resume-plan` command auto-handoff. No single layer is sufficient.

### Decision 3: Platform-Specific `planFileDirectory`
**Context:** How to make auto-discovery platform-agnostic?
**Decision:** Add `planFileDirectory` field to `platform.json`. Only Claude Code sets it (`~/.claude/plans`). Core module checks if the field exists and skips auto-discovery if absent.
**Rationale:** Keeps `core/from-plan.md` platform-agnostic while enabling Claude-specific plan file discovery.

### Decision 4: Protocol Breach Language
**Context:** What enforcement mechanism to use?
**Decision:** "Implementing a plan without converting it to a SpecOps spec first in a SpecOps-configured project is a protocol breach."
**Rationale:** Protocol breach is the strongest enforcement pattern in the codebase — used for Phase 1 pre-flight, task tracking, memory write gates.

## Component Design

### Component 1: Enhanced From-Plan Module
**File:** `core/from-plan.md`
**Changes:**
- Detection section: add new trigger patterns
- Step 1: restructure into 4 input branches (inline → file path → auto-discover → ask user)
- Path validation: reject `../`, require `.md`, check FILE_EXISTS
- Auto-discovery: use platform `planFileDirectory` if available

### Component 2: Post-Plan-Acceptance Gate
**File:** `core/workflow.md`
**Changes:**
- New step 10.5 in Getting Started between from-plan check (step 10) and interview check (step 11)
- Three-condition AND gate: acceptance phrase + plan context + .specops.json exists
- Protocol breach for ad-hoc implementation when conditions met

### Component 3: Resume-Plan SpecOps Bridge
**File:** `.claude/commands/resume-plan.md`
**Changes:**
- New Step 8 after plan presentation (Step 7)
- Check `.specops.json` existence → invoke `/specops from-plan` with plan content
- Graceful fallback when SpecOps not configured

### Component 4: Platform Config
**File:** `platforms/claude/platform.json`
**Changes:**
- Add `"planFileDirectory": "~/.claude/plans"` field

## Testing Strategy
- **Generator validation:** `python3 generator/validate.py` (ensures from-plan markers propagate)
- **Platform consistency:** `python3 tests/test_platform_consistency.py`
- **Build test:** `python3 tests/test_build.py`
- **Full suite:** `bash scripts/run-tests.sh`
