# Design: Bugfix Regression Risk Analysis

## Architecture Overview

This feature enhances the existing bugfix workflow by adding a discovery methodology layer. No new core modules or files are created — all changes go into `core/templates/bugfix.md`, `core/workflow.md`, and `generator/validate.py`. The three-layer architecture (core → generator → platforms) remains unchanged; template content flows through the existing build pipeline automatically.

## Technical Decisions

### Decision 1: Section Placement in Bugfix Template
**Context:** Where should the Regression Risk Analysis section go in the bugfix template?
**Options Considered:**
1. After Proposed Fix (current Unchanged Behavior position) — Cons: agent writes fix before analyzing risks
2. Between Reproduction Steps and Proposed Fix — Pros: analysis constrains fix design; follows natural workflow (understand → analyze → fix)

**Decision:** Between Reproduction Steps and Proposed Fix
**Rationale:** The agent needs to understand the blast radius before designing a fix. Placing analysis after the fix would mean the agent commits to an approach without knowing what it might break.

### Decision 2: Proportionality Mechanism
**Context:** How to scale analysis depth with severity without adding new configuration.
**Options Considered:**
1. New config field in `.specops.json` — Cons: adds schema complexity
2. Leverage existing Severity field in Impact Assessment — Pros: zero new config, already present in template

**Decision:** Use the existing Severity field from Impact Assessment
**Rationale:** The Severity field is already filled in before the Regression Risk Analysis section. HTML comments in the template guide the agent to select the appropriate depth level. No schema changes needed.

### Decision 3: Scope Escalation Placement
**Context:** The current scope escalation guidance is an HTML comment at the bottom of Testing Plan — too late and too invisible.
**Options Considered:**
1. Keep as HTML comment — Cons: produces nothing actionable
2. Move to a subsection of Regression Risk Analysis with explicit signal format — Pros: agent produces a visible "Contained" or "Escalation needed" signal before writing the fix

**Decision:** Move to Scope Escalation Check subsection within Regression Risk Analysis
**Rationale:** Explicit signal format is reviewable and occurs before fix design. The old HTML comment in Testing Plan is removed to avoid duplication.

## Product Module Design

### Module: Bugfix Template Enhancement
**Responsibility:** Provides the structural template for regression analysis
**Interface:** HTML comments guide agent behavior; subsection headings provide structure
**Dependencies:** Existing bugfix.md template sections (Impact Assessment provides Severity input)

### Module: Workflow Guidance Enhancement
**Responsibility:** Provides step-by-step discovery procedure using abstract operations
**Interface:** Integrated into Phase 2 bugfix-specific guidance in core/workflow.md
**Dependencies:** Abstract operations from core/tool-abstraction.md (LIST_DIR, READ_FILE, RUN_COMMAND)

### Module: Validation Markers
**Responsibility:** Ensures regression analysis content survives platform generation
**Interface:** REGRESSION_MARKERS list in validate.py, checked per-platform and cross-platform
**Dependencies:** Existing validate.py marker-checking infrastructure (check_markers_present function)

## System Flow

```
Impact Assessment (Severity field)
       ↓
Regression Risk Analysis
  ├── Blast Radius (LIST_DIR, READ_FILE callers/dependents)
  ├── Behavior Inventory (document existing correct behaviors)
  ├── Test Coverage Assessment (READ_FILE test files, identify gaps)
  ├── Risk Tier (Must-Test / Nice-To-Test / Low-Risk)
  └── Scope Escalation Check (Contained / Escalation needed)
       ↓
Proposed Fix (constrained by analysis findings)
       ↓
Unchanged Behavior (populated from Must-Test behaviors)
       ↓
Testing Plan (gaps from Coverage Assessment become new tests)
```

## Ship Plan
1. Implement template changes (bugfix.md) and workflow guidance (workflow.md) — these are independent
2. Add validation markers (validate.py) — depends on template content being final
3. Regenerate all platform outputs and validate
4. Run full test suite

## Risks & Mitigations
- **Risk:** Regression analysis adds overhead to simple bugs → **Mitigation:** Low-severity bugs require only a brief blast radius scan (1-2 lines)
- **Risk:** Abstract operations in workflow guidance may not map cleanly to all platforms → **Mitigation:** Operations used (LIST_DIR, READ_FILE, RUN_COMMAND) already have mappings in all 4 platform.json files
