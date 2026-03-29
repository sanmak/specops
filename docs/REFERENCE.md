# SpecOps Quick Reference

A one-page reference for daily use of SpecOps.

## Invocation

**Claude Code:**

```text
/specops [description]
```

**Cursor / Codex / Copilot / Antigravity:**

```text
Use specops to [description]
```

## Common Usage Patterns

```text
# Feature development
Add user authentication with OAuth

# Bug fix
Fix: Users seeing 500 errors on checkout

# Refactoring
Refactor payment service to use repository pattern

# Interview mode (explicit)
interview I want to build a SaaS platform for restaurants

# Interview mode (auto-triggered by vague request)
I have an idea

# Implement existing spec
implement auth-feature

# View an initiative
view initiative oauth-payments

# List all initiatives
list initiatives

# Execute all specs in an initiative
initiative oauth-payments

# Review a teammate's spec
review user-auth

# Revise spec after feedback
revise user-auth

# Show all specs and their status
status

# Show only specs needing review
status in-review

# View a spec (executive summary)
view auth-feature

# View specific sections
view auth-feature design
view auth-feature requirements design

# View full spec content
view auth-feature full

# Interactive walkthrough
view auth-feature walkthrough

# Quick status/progress check
view auth-feature status

# List all specs
list
```

## Configuration File (.specops.json)

```json
{
  "specsDir": ".specops",
  "team": {
    "conventions": ["Your team conventions"],
    "reviewRequired": true,
    "taskTracking": "github"
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true
  }
}
```

## Spec Structure

```text
.specops/
  index.json             # Auto-generated spec dashboard
  initiatives/           # Multi-spec feature tracking
    <initiative-id>.json       # Member specs, execution waves, status
    <initiative-id>-log.md     # Chronological execution trace
  feature-name/
    spec.json            # Lifecycle metadata (always created)
    requirements.md      # What (user stories, acceptance criteria)
    design.md            # How (architecture, decisions, diagrams)
    tasks.md             # Steps (implementation tasks)
    implementation.md    # (optional) Decisions, deviations, blockers
    reviews.md           # (optional) Review feedback
```

## Usage Metrics

Completed specs include an optional `metrics` object in `spec.json` with proxy productivity data:

| Field | Description |
| ------- | ------------- |
| `specArtifactTokensEstimate` | Estimated tokens of spec artifacts (total chars / 4) |
| `filesChanged` | Files changed during implementation |
| `linesAdded` | Lines added during implementation |
| `linesRemoved` | Lines removed during implementation |
| `tasksCompleted` | Count of completed tasks |
| `acceptanceCriteriaVerified` | Count of checked acceptance criteria |
| `specDurationMinutes` | Wall-clock minutes from creation to completion |

Metrics are captured automatically at Phase 4 completion. See [TOKEN-USAGE.md](TOKEN-USAGE.md) for benchmark data and ROI analysis guidance.

## Workflow Phases

**Optional pre-phase:**
0. **Interview** (optional) - Structured Q&A to gather requirements for vague or exploratory ideas

- Triggered by: explicit `/specops interview` or auto-detected vague requests
- Asks 5 questions: Problem, Users, Features, Constraints, Done Criteria
- Collects answers with smart follow-ups for clarification
- Proceeds to Phase 1 with enriched context

**Core workflow:**

1. **Understand** - Agent analyzes request and codebase
2. **Spec** - Creates structured specification (always creates spec.json)
2.5. **Review** - Team reviews spec, provides feedback, approves (if specReview enabled). Solo developers can self-review (if allowSelfApproval enabled)
3. **Implement** - Executes tasks following spec (gate checks approvals)
4. **Complete** - Verifies, commits, creates PR

## Configuration Options

| Option | Values | Default | Constraints | Description |
| -------- | -------- | --------- | ------------- | ------------- |
| `specsDir` | string | `.specops` | max 200 chars, no `../` or absolute paths | Where to store specs |
| `vertical` | `backend`/`frontend`/`fullstack`/`infrastructure`/`data`/`library`/`builder`/`migration` | (auto-detect) | enum | Project vertical for template adaptation |
| `templates.feature` | string | `default` | max 100 chars | Custom template for feature specifications |
| `templates.bugfix` | string | `default` | max 100 chars | Custom template for bugfix specifications |
| `templates.refactor` | string | `default` | max 100 chars | Custom template for refactoring specifications |
| `templates.design` | string | `default` | max 100 chars | Custom template for design.md |
| `templates.tasks` | string | `default` | max 100 chars | Custom template for tasks.md |
| `team.conventions` | string[] | `[]` | max 30 items, each max 500 chars | Team-specific development conventions |
| `team.reviewRequired` | boolean | `false` | | Require approval before implementing |
| `team.specReview.enabled` | boolean | `false` | | Enable collaborative spec review workflow |
| `team.specReview.minApprovals` | integer | `1` | min 1, max 10 | Approvals required before implementation |
| `team.specReview.allowSelfApproval` | boolean | `false` | | Allow authors to self-review and self-approve (produces `self-approved` status) |
| `team.taskTracking` | `github`/`jira`/`linear`/`none` | `none` | enum | Task tracking integration |
| `implementation.autoCommit` | boolean | `false` | | Auto-commit after tasks |
| `implementation.createPR` | boolean | `false` | | Auto-create PR when done |
| `implementation.delegationThreshold` | integer | `4` | min 1, max 20 | Complexity score threshold for auto task delegation. Lower values delegate more aggressively. |
| `implementation.validateReferences` | `off`/`warn`/`strict` | `warn` | enum | Validate file paths and code references in spec against codebase before implementation. `off`: skip. `warn`: notify and continue. `strict`: block on unresolved. |
| `implementation.gitCheckpointing` | boolean | `false` | | Commit at phase boundaries (spec-created, implemented, completed). Three commits max per run. Complements `autoCommit` (per-task). |
| `implementation.taskDelegation` | `auto`/`always`/`never` | `auto` | enum | Phase 3 task execution strategy. `auto`: delegate when complexity score >= threshold. `always`: always delegate. `never`: sequential in current context. |
| `implementation.runLogging` | boolean | `false` | | Log per-step execution traces to `<specsDir>/runs/`. Complements proxy metrics with process data. |
| `implementation.pipelineMaxCycles` | integer | `3` | min 1, max 10 | Maximum Phase 3→4 iteration cycles in pipeline mode. |
| `implementation.evaluation` | object | | | Adversarial evaluation configuration. When enabled, Phase 2 exit gate scores spec quality and Phase 4A scores implementation quality using scored dimensions with hard thresholds and feedback loops. |
| `implementation.evaluation.enabled` | boolean | `true` | | Enable adversarial evaluation. When false, skip both evaluation touchpoints and use legacy Phase 4 checkbox verification. |
| `implementation.evaluation.minScore` | integer | `7` | min 1, max 10 | Minimum quality dimension score (1-10) required to pass evaluation. |
| `implementation.evaluation.maxIterations` | integer | `2` | min 1, max 5 | Maximum evaluation-remediation iterations before proceeding to next phase. |
| `implementation.evaluation.perTask` | boolean | `false` | | Run implementation evaluation after each task instead of after all tasks. |
| `implementation.evaluation.exerciseTests` | boolean | `true` | | Whether the implementation evaluator should run the project test suite. |
| `implementation.learnings` | object | | | Production learnings configuration. Controls capture and surfacing of post-deployment discoveries. |
| `implementation.learnings.maxSurfaced` | integer | `3` | min 1, max 10 | Maximum number of learnings surfaced during Phase 1 loading. |
| `implementation.learnings.severityThreshold` | string | `"medium"` | `all`, `medium`, `high`, `critical` | Minimum severity level to surface learnings. Critical/high always surface regardless. |
| `implementation.learnings.capturePrompt` | string | `"auto"` | `auto`, `manual`, `off` | When to prompt for learning capture. auto: Phase 4 + bugfix. manual: only /specops learn. off: disabled. |
| `dependencySafety.enabled` | boolean | `true` | | Enable dependency safety gate in Phase 2 step 6.7. Scans for CVEs, EOL status, and best practices. |
| `dependencySafety.severityThreshold` | `strict`/`medium`/`low` | `medium` | enum, max 10 chars | Severity that blocks implementation. strict: any finding. medium: Critical/High. low: warn only. |
| `dependencySafety.autoFix` | boolean | `false` | | Attempt automatic remediation (npm audit fix, cargo update) before re-evaluating. |
| `dependencySafety.allowedAdvisories` | string[] | `[]` | max 50 items, each max 100 chars | CVE IDs acknowledged and excluded from blocking (still recorded in audit). |
| `dependencySafety.scanScope` | `spec`/`project` | `spec` | enum, max 10 chars | Scope of scan. spec: ecosystems relevant to current spec. project: all detected ecosystems. |
| `team.codeReview.required` | boolean | `false` | | Require code review |
| `team.codeReview.minApprovals` | integer | `1` | min 1 | Minimum approvals needed |
| `team.codeReview.requireTests` | boolean | `true` | | Require tests in implementation |
| `modules` | object | | pattern-keyed | Module-specific configuration for monorepo/multi-module projects |

> **Note:** All configuration objects enforce `additionalProperties: false` — unknown keys will be rejected during schema validation.
>
> **Project context beyond conventions:** For rich, multi-paragraph context (product overview, tech stack, directory structure), use [Steering Files](STEERING_GUIDE.md) instead of cramming it into `team.conventions` strings.

## Spec Templates

> **Vertical adaptation:** When a vertical is configured or detected, default template sections are adapted. For example, with `"vertical": "infrastructure"`, "User Stories" becomes "Infrastructure Requirements" and "Component Design" becomes "Infrastructure Topology".

### requirements.md

```markdown
# Feature: [Title]

## User Stories
**As a** [role]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria (EARS):**
<!-- EARS patterns: Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted -->
- WHEN [condition/event] THE SYSTEM SHALL [expected behavior]
- WHEN [condition/event] THE SYSTEM SHALL [expected behavior]

**Progress Checklist:**
- [ ] [derived from EARS criterion 1]
- [ ] [derived from EARS criterion 2]
```

> **EARS Notation:** Acceptance criteria use [EARS (Easy Approach to Requirements Syntax)](https://alistairmavin.com/ears/) for precision and testability. Five patterns: **Ubiquitous** (`THE SYSTEM SHALL`), **Event-Driven** (`WHEN ... THE SYSTEM SHALL`), **State-Driven** (`WHILE ... THE SYSTEM SHALL`), **Optional** (`WHERE ... THE SYSTEM SHALL`), **Unwanted** (`IF ... THEN THE SYSTEM SHALL`). Checkboxes are an optional progress checklist derived from EARS statements.

### design.md

```markdown
# Design: [Title]

## Technical Decisions
**Decision:** [Choice made]
**Rationale:** [Why]

## Component Design
**Component:** [Name]
**Responsibility:** [What it does]
**Interface:** [API]

## Sequence Diagram
```

User -> Frontend: Action
Frontend -> API: Request

```text
```

### tasks.md

```markdown
# Tasks: [Title]

## Task 1: [Title]
**Status:** Pending
**Dependencies:** None
**Priority:** High

**Steps:**
1. Step 1
2. Step 2

**Acceptance Criteria:**
- [ ] Done when X
```

## Team Conventions Template

```json
{
  "team": {
    "conventions": [
      "Use TypeScript for all new code",
      "Write unit tests with 80% coverage",
      "Follow existing patterns",
      "Document public APIs",
      "Keep functions under 50 lines",
      "Handle errors explicitly"
    ]
  }
}
```

## Integration with Git

### Manual Workflow

```bash
# After spec creation
git add .specops/
git commit -m "Add spec for feature X"

# After implementation
git add .
git commit -m "Implement feature X"
git push
```

### Automatic Workflow

```json
{
  "implementation": {
    "autoCommit": true,
    "createPR": true
  }
}
```

## Task Tracking Integration

### GitHub

```json
{
  "team": {
    "taskTracking": "github"
  }
}
```

- Creates GitHub issues for tasks
- Links commits to issues
- Updates issue status

### Jira

```json
{
  "team": {
    "taskTracking": "jira"
  }
}
```

- References Jira tickets
- Updates ticket status
- Links in commits

## Module-Specific Configuration

```json
{
  "modules": {
    "backend": {
      "specsDir": "backend/specs",
      "conventions": ["Backend conventions"]
    },
    "frontend": {
      "specsDir": "frontend/specs",
      "conventions": ["Frontend conventions"]
    }
  }
}
```

## Troubleshooting

| Issue | Solution |
| ------- | ---------- |
| Skill not found | Verify installation path, restart Claude Code |
| Config not loading | Check JSON validity, verify file location |
| Can't create specs | Check directory permissions |
| Tests failing | Review test output, check dependencies |

## Plan Enforcement (Claude Code)

When a plan is approved in Claude Code, SpecOps enforces the spec-driven workflow using a marker file state machine:

1. **ExitPlanMode fires**: The PostToolUse hook creates `.plan-pending-conversion` in the specsDir
2. **Write/Edit blocked**: The PreToolUse guard blocks writes to non-spec files while the marker exists
3. **Allowed paths**: Writes to specsDir, `.claude/plans/`, and `.claude/memory/` are always allowed
4. **`/specops from-plan` runs**: Converts the plan to a spec, then removes the marker
5. **Writes unblocked**: All Write/Edit operations resume normally

The marker file is:

- Created by the PostToolUse ExitPlanMode hook
- Checked by the PreToolUse Write|Edit guard
- Removed by from-plan mode after the enforcement pass (step 7) succeeds
- Gitignored (ephemeral, not committed)

If from-plan fails before the enforcement pass, the marker persists and writes remain blocked until conversion succeeds.

## Best Practices

✅ **DO:**

- Review specs before implementing
- Commit specs to git
- Use team conventions
- Keep specs updated
- Start small and iterate
- Keep specs proportional to the task

❌ **DON'T:**

- Skip spec review
- Ignore test failures
- Mix unrelated changes
- Skip documentation
- Rush to implementation
- Over-engineer specs or implementations
- Add speculative features not in requirements

## File Locations

```text
# Claude Code
~/.claude/skills/specops/           # User installation
<project>/.claude/skills/specops/   # Project installation

# Cursor
<project>/.cursor/rules/specops.mdc # Project rules

# Codex
<project>/.codex/skills/specops/    # Skill installation

# Copilot
<project>/.github/instructions/     # Scoped instructions

# Antigravity
<project>/.agents/rules/specops.md  # Agent rules

# All platforms
<project>/.specops.json             # Project configuration
<project>/.specops/                 # Specs directory
```

## Getting Help

1. **Quick Start**: `QUICKSTART.md`
2. **Full Docs**: `README.md`
3. **Team Setup**: `TEAM_GUIDE.md`
4. **Examples**: `examples/` directory
5. **Structure**: `STRUCTURE.md`
6. **Security**: `SECURITY.md`
7. **Contributing**: `CONTRIBUTING.md`

## Keyboard Shortcuts (in Claude Code)

```text
/specops                        # Launch SpecOps agent
/specops view <spec-name>       # View a spec
/specops list                   # List all specs
Ctrl+C                          # Cancel current operation
```

## Example Session Flow

```text
You: /specops Add payment processing

Agent:
🎯 SpecOps Agent Activated
📋 Creating spec...
✅ Spec created in .specops/payment-processing/
📊 3 user stories, 8 components, 12 tasks
🔍 Ready for review

You: /specops view payment-processing

Agent:
# payment-processing
Type: Feature | Status: Draft | Version: v1
## What
Add Stripe-based payment processing with checkout flow...
## Key Decisions
- Payment provider: Stripe (chosen over Braintree)
- Checkout flow: Server-side sessions
## Progress
Completed: 0/12 tasks (0%)

You: Looks good, proceed

Agent:
✅ Task 1/12: Create PaymentService
✅ Task 2/12: Add Stripe integration
...
✅ Task 12/12: Update documentation
🎉 Implementation complete!
🔗 PR created: #456
```

## Quick Configuration Examples

### Minimal

```json
{
  "specsDir": ".specops"
}
```

### Solo Developer

```json
{
  "specsDir": ".specops",
  "implementation": {
    "autoCommit": true
  }
}
```

### Team Project

```json
{
  "specsDir": ".specops",
  "team": {
    "conventions": ["Team standards"],
    "reviewRequired": true,
    "taskTracking": "github"
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true
  }
}
```

### Team Review

```json
{
  "team": {
    "specReview": { "enabled": true, "minApprovals": 2 }
  }
```

---

**Version**: 1.7.0
**Keep this reference handy for daily development!**
