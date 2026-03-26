# Requirements: Auto-Close GitHub Issues on Task Completion

## Overview

When taskTracking is configured and tasks have valid IssueIDs, completing a task in `tasks.md` should automatically close the corresponding external issue. Currently, the Status Sync protocol in `core/config-handling.md` already specifies that issues should be closed on the `In Progress -> Completed` transition, and `core/task-tracking.md` references this via the External Tracker Sync section. However, during the antigravity-platform spec (15 tasks, 15 issues #184-#198), all GitHub issues remained open after all tasks were marked Done. This indicates the auto-close behavior is documented but not enforced deterministically -- the agent skips it because it lacks imperative step-by-step instructions integrated into the task completion flow itself.

This spec adds deterministic auto-close enforcement to `core/task-tracking.md` so that issue closure happens as a mandatory step in the task completion procedure, not as an optional cross-reference to another module.

**Related Issue:** [#199](https://github.com/sanmak/specops/issues/199)

## Functional Requirements

### FR-1: Auto-Close on Task Completion

<!-- EARS: Event-Driven -->
WHEN a task's status transitions from `In Progress` to `Completed` in `tasks.md` AND `config.team.taskTracking` is not `"none"` AND the task has a valid `**IssueID:**` (neither `None` nor prefixed with `FAILED`) AND `canExecuteCode` is true, THE SYSTEM SHALL close the corresponding external issue using the platform-appropriate close command.

**Progress Checklist:**

- [x] Auto-close step added to task-tracking.md completion flow
- [x] Uses abstract operations (RUN_COMMAND)
- [x] Platform-specific commands for GitHub, Jira, Linear

### FR-2: Graceful Failure Handling

<!-- EARS: Unwanted Behavior -->
IF the external issue close command fails (network error, permissions, CLI not installed), THEN THE SYSTEM SHALL warn the user with the error details and continue without blocking the task completion in `tasks.md`.

**Progress Checklist:**

- [x] Failure handling uses NOTIFY_USER
- [x] Task completion in tasks.md is never blocked by close failure

### FR-3: Phase 4 Sweep for Missed Closures

<!-- EARS: Event-Driven -->
WHEN the spec status transitions to `completed` in Phase 4 AND `config.team.taskTracking` is not `"none"` AND `canExecuteCode` is true, THE SYSTEM SHALL scan all tasks in `tasks.md` for any with status `Completed` and a valid `**IssueID:**` whose external issue is still open, and close them.

**Progress Checklist:**

- [x] Phase 4 sweep step added to workflow.md
- [x] Only runs when taskTracking is configured
- [x] Handles partial failures gracefully

### FR-4: Capability Guard

<!-- EARS: Optional Feature -->
WHERE `canExecuteCode` is false, THE SYSTEM SHALL skip the auto-close command and instead suggest the close command to the user via NOTIFY_USER.

**Progress Checklist:**

- [x] canExecuteCode guard present in auto-close logic

## Non-Functional Requirements

### NFR-1: No New Module

The auto-close behavior is added to existing modules (`core/task-tracking.md` and `core/workflow.md`), not as a new core module. This avoids generator pipeline changes.

### NFR-2: Abstract Operations Only

All commands in `core/task-tracking.md` must use abstract operations (`RUN_COMMAND`, `NOTIFY_USER`, `READ_FILE`) per the three-tier architecture rules.

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false

## Scope Boundary

### In Scope

- Adding deterministic auto-close step to `core/task-tracking.md`
- Adding Phase 4 sweep to `core/workflow.md`
- Regenerating all platform outputs
- Updating validator and tests if new markers are added

### Out of Scope

- Reopening closed issues when a task moves back from Completed (Completed is terminal)
- Auto-close for Low-priority tasks without IssueIDs (they have no external issues)
- New configuration options (uses existing `taskTracking` config)
