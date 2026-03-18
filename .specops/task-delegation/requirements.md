# Feature: Task Delegation for Phase 3

## Overview
During Phase 3 (Implement), SpecOps executes all tasks sequentially within a single agent context window. For specs with many tasks, accumulated file reads, implementation details, and conversation history exhaust the context window — causing hallucinations, lost task details, and quality degradation on later tasks. Task delegation solves this by executing each task in a fresh context using an orchestrator/worker pattern.

## Product Requirements

### Requirement 1: Fresh Context Per Task
**As a** developer using SpecOps
**I want** each implementation task to execute in a fresh context
**So that** later tasks get the same quality as earlier tasks without context window degradation

**Acceptance Criteria (EARS):**
- WHEN task delegation is active and a task is dispatched THE SYSTEM SHALL construct a focused handoff bundle containing only the task details, relevant design context, prior task summaries, and file paths
- WHEN a delegated task completes THE SYSTEM SHALL verify the task status in tasks.md before proceeding to the next task

**Progress Checklist:**
- [x] Handoff bundle construction implemented
- [x] Post-delegation verification implemented

### Requirement 2: Platform-Adaptive Strategies
**As a** developer using SpecOps on any supported platform
**I want** task delegation to adapt to my platform's capabilities
**So that** I get the best available context management regardless of platform

**Acceptance Criteria (EARS):**
- WHERE canDelegateTask is true THE SYSTEM SHALL spawn a fresh sub-agent for each task (Strategy A)
- WHERE canDelegateTask is false and canAskInteractive is true THE SYSTEM SHALL write a session checkpoint and prompt the user to start a fresh session (Strategy B)
- WHERE canDelegateTask is false and canAskInteractive is false THE SYSTEM SHALL execute tasks sequentially with enhanced checkpointing (Strategy C)

**Progress Checklist:**
- [x] Strategy A (sub-agent) defined
- [x] Strategy B (session checkpoint) defined
- [x] Strategy C (enhanced sequential) defined

### Requirement 3: Configurable Delegation
**As a** developer
**I want** to control when task delegation activates
**So that** I can opt in/out based on my workflow preferences

**Acceptance Criteria (EARS):**
- WHEN taskDelegation is "auto" and there are 4 or more pending tasks THE SYSTEM SHALL activate delegation
- WHEN taskDelegation is "always" THE SYSTEM SHALL activate delegation regardless of task count
- WHEN taskDelegation is "never" THE SYSTEM SHALL use standard sequential execution

**Progress Checklist:**
- [x] Config option added to schema.json
- [x] Delegation decision logic defined in core module

### Requirement 4: Per-Task Testing
**As a** developer
**I want** each delegated task to run its own tests before completion
**So that** regressions are caught early rather than cascading to later tasks

**Acceptance Criteria (EARS):**
- WHEN implementation.testing is "auto" THE SYSTEM SHALL run task-relevant tests before marking a delegated task Completed
- IF tests fail for a delegated task THEN THE SYSTEM SHALL keep the task In Progress or set it to Blocked

**Progress Checklist:**
- [x] Per-task testing defined in delegate responsibilities

## Non-Functional Requirements
- Backward compatible: specs created before this feature work without changes (default "auto" activates only when conditions met)
- No new file types: handoff uses existing tasks.md, design.md, implementation.md

## Constraints & Assumptions
- Sequential execution only — no parallel task execution (avoids merge conflicts in shared files)
- Sub-agent spawning (Strategy A) is Claude Code specific; other platforms use checkpoint/sequential fallbacks
- Delegates inherit all safety rules (convention sanitization, path containment)

## Scope Boundary
**Ships in v1:**
- Three delegation strategies (sub-agent, session checkpoint, enhanced sequential)
- `canDelegateTask` capability flag
- `taskDelegation` config option
- Handoff bundle construction
- Orchestrator verification loop

**Deferred:**
- Parallel task execution (future spec)
- Context usage estimation / adaptive splitting
- Sub-agent failure retry

## Team Conventions
- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
