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

## Proposed Fix
Description of the fix approach and why it addresses the root cause.

## Unchanged Behavior
<!-- Document behaviors that MUST NOT change as a result of this fix.
     Use EARS notation: WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior]
     This prevents regressions by making preserved behavior explicit and testable. -->
- WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior that must be preserved]
- WHEN [condition] THE SYSTEM SHALL CONTINUE TO [existing behavior that must be preserved]

## Testing Plan

### Current Behavior (verify the bug exists)
- WHEN [reproduction condition] THE SYSTEM CURRENTLY [broken behavior]

### Expected Behavior (verify the fix works)
- WHEN [reproduction condition] THE SYSTEM SHALL [correct behavior after fix]

### Unchanged Behavior (verify no regressions)
- WHEN [related condition] THE SYSTEM SHALL CONTINUE TO [preserved behavior]

<!-- If this fix reveals the need for broader changes beyond the bug scope,
     create a separate Feature Spec rather than expanding this bugfix. -->

## Acceptance Criteria
- [ ] Bug reproduction confirmed (Current Behavior verified)
- [ ] Fix verified (Expected Behavior tests pass)
- [ ] No regressions (Unchanged Behavior tests pass)

## Team Conventions
[Load from config.team.conventions]
