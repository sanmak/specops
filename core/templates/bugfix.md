# Bug Fix: [Title]

## Problem Statement
Clear description of the bug and its impact.

## Root Cause Analysis
Detailed analysis of what's causing the bug.

**Affected Components:**
- Component 1
- Component 2

**Error Symptoms:**
- Symptom 1
- Symptom 2

## Impact Assessment
- **Severity:** [Critical/High/Medium/Low]
- **Users Affected:** [Number/Percentage]
- **Frequency:** [Always/Often/Sometimes/Rarely]

## Reproduction Steps
1. Step 1
2. Step 2
3. Expected: [expected behavior]
4. Actual: [actual behavior]

## Regression Risk Analysis
<!-- Depth scales with Severity from Impact Assessment:
     Critical/High → complete all five subsections
     Medium        → complete Blast Radius + Behavior Inventory; brief Risk Tier
     Low           → brief Blast Radius scan; also record a lightweight Risk Tier entry for at least one caller-visible behavior, or explicitly note "No caller-visible unchanged behavior — isolated internal fix"; note "minimal regression risk" if confirmed -->

### Blast Radius
<!-- Survey what code paths are touched by the affected component(s).
     LIST_DIR and READ_FILE to find callers, importers, and dependents.
     RUN_COMMAND to search for usages if the platform supports code execution.
     List each affected entry point, module boundary, or API surface. -->
- [Affected code path or module 1]
- [Affected code path or module 2]

### Behavior Inventory
<!-- For each item in the Blast Radius, list the existing behaviors that interact
     with the affected area. Ask: "What does this code path do correctly today?"
     These are the candidate behaviors the fix must not disturb. -->
- [Existing behavior that touches the affected area]
- [Existing behavior that touches the affected area]

### Test Coverage Assessment
<!-- Identify which behaviors in the inventory are already covered by tests,
     and which are gaps. READ_FILE test files for the affected component(s).
     Gaps must be addressed in the Testing Plan below. -->
- **Covered:** [behavior] → [test file / test name]
- **Gap:** [behavior] → no existing test

### Risk Tier
<!-- Classify each inventoried behavior by regression likelihood:
     Must-Test    → close coupling to changed code; high mutation chance
     Nice-To-Test → indirect coupling; moderate risk
     Low-Risk     → separate module boundary; independent codepath
     Only Must-Test items are required gates for Unchanged Behavior verification. -->
| Behavior | Tier | Reason |
|----------|------|--------|
| [behavior] | Must-Test | [why] |
| [behavior] | Nice-To-Test | [why] |

### Scope Escalation Check
<!-- After surveying the blast radius: does the fix require changes beyond
     correcting the broken behavior? If yes, create a Feature Spec instead of
     (or in addition to) this bugfix. Common triggers:
     - The root cause is a missing feature, not a defect
     - Fixing correctly requires new abstractions used in multiple places
     - The correct behavior has never been implemented (not a regression) -->
**Scope:** [Contained | Escalation needed — reason]

## Proposed Fix
Description of the fix approach and why it addresses the root cause.

## Unchanged Behavior
<!-- Drawn from Must-Test behaviors in the Regression Risk Analysis above.
     Each item here is a formal commitment backed by discovery, not a guess.
     Use EARS notation: WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior] -->
- WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior that must be preserved]
- WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior that must be preserved]

## Testing Plan

### Current Behavior (verify the bug exists)
- WHEN [reproduction condition] THE SYSTEM CURRENTLY [broken behavior]

### Expected Behavior (verify the fix works)
- WHEN [reproduction condition] THE SYSTEM SHALL [correct behavior after fix]

### Unchanged Behavior (verify no regressions)
<!-- Must-Test behaviors from Regression Risk Analysis. Nice-To-Test items are optional.
     Gap behaviors (no existing test) from Coverage Assessment must have new tests here. -->
- WHEN [related condition] THE SYSTEM SHALL CONTINUE TO [preserved behavior]

## Acceptance Criteria
<!-- Keep or remove criteria based on Severity from Impact Assessment:
     Critical/High → all five criteria apply
     Medium        → keep criteria 1-4; criterion 5 only if coverage gaps were found
     Low           → keep criteria 1-3; omit 4 if no Must-Test items; omit 5 (no Coverage Assessment) -->
- [ ] Regression Risk Analysis completed (blast radius surveyed, behaviors inventoried)
- [ ] Bug reproduction confirmed (Current Behavior verified)
- [ ] Fix verified (Expected Behavior tests pass)
- [ ] No regressions (all Must-Test Unchanged Behavior tests pass)
- [ ] Test coverage gaps from Coverage Assessment addressed

## Team Conventions
[Load from config.team.conventions]
