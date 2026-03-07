# SpecOps Quick Reference

A one-page reference for daily use of SpecOps.

## Invocation

**Claude Code:**
```
/specops [description]
```

**Cursor / Codex:**
```
Use specops to [description]
```

## Common Usage Patterns

```
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
    "createPR": true,
    "testing": "auto"
  }
}
```

## Spec Structure

```
.specops/
  index.json             # Auto-generated spec dashboard
  feature-name/
    spec.json            # Lifecycle metadata (always created)
    requirements.md      # What (user stories, acceptance criteria)
    design.md            # How (architecture, decisions, diagrams)
    tasks.md             # Steps (implementation tasks)
    implementation.md    # (optional) Decisions, deviations, blockers
    reviews.md           # (optional) Review feedback
```

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
|--------|--------|---------|-------------|-------------|
| `specsDir` | string | `.specops` | max 200 chars, no `../` or absolute paths | Where to store specs |
| `vertical` | `backend`/`frontend`/`fullstack`/`infrastructure`/`data`/`library`/`builder` | (auto-detect) | enum | Project vertical for template adaptation |
| `templates.design` | string | `default` | max 100 chars | Custom template for design.md |
| `templates.tasks` | string | `default` | max 100 chars | Custom template for tasks.md |
| `team.conventions` | string[] | `[]` | max 30 items, each max 500 chars | Team-specific development conventions |
| `team.reviewRequired` | boolean | `false` | | Require approval before implementing |
| `team.specReview.enabled` | boolean | `false` | | Enable collaborative spec review workflow |
| `team.specReview.minApprovals` | integer | `1` | min 1, max 10 | Approvals required before implementation |
| `team.specReview.allowSelfApproval` | boolean | `false` | | Allow authors to self-review and self-approve (produces `self-approved` status) |
| `team.taskTracking` | `github`/`jira`/`linear`/`none` | `none` | enum | Task tracking integration |
| `team.taskPrefix` | string | | max 20 chars | Task/ticket prefix (e.g., `PROJ-`) |
| `implementation.autoCommit` | boolean | `false` | | Auto-commit after tasks |
| `implementation.createPR` | boolean | `false` | | Auto-create PR when done |
| `implementation.testing` | `auto`/`manual`/`skip` | `auto` | enum | Testing strategy |
| `implementation.testFramework` | string | (auto-detect) | max 50 chars | Test framework (jest, pytest, etc.) |
| `implementation.linting.enabled` | boolean | `true` | | Run linter after tasks |
| `implementation.formatting.enabled` | boolean | `true` | | Run formatter before commits |
| `implementation.formatting.tool` | `prettier`/`black`/`rustfmt`/`gofmt` | (auto-detect) | enum | Formatting tool |
| `team.codeReview.required` | boolean | `false` | | Require code review |
| `team.codeReview.minApprovals` | integer | `1` | min 1 | Minimum approvals needed |
| `team.codeReview.requireTests` | boolean | `true` | | Require tests in implementation |
| `team.codeReview.requireDocs` | boolean | `false` | | Require docs for public APIs |

> **Note:** All configuration objects enforce `additionalProperties: false` — unknown keys will be rejected during schema validation.

## Spec Templates

> **Vertical adaptation:** When a vertical is configured or detected, default template sections are adapted. For example, with `"vertical": "infrastructure"`, "User Stories" becomes "Infrastructure Requirements" and "Component Design" becomes "Infrastructure Topology".

### requirements.md
```markdown
# Feature: [Title]

## User Stories
**As a** [role]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
```

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
```
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
    "taskTracking": "jira",
    "taskPrefix": "PROJ-"
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
|-------|----------|
| Skill not found | Verify installation path, restart Claude Code |
| Config not loading | Check JSON validity, verify file location |
| Can't create specs | Check directory permissions |
| Tests failing | Review test output, check dependencies |

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

```
# Claude Code
~/.claude/skills/specops/           # User installation
<project>/.claude/skills/specops/   # Project installation

# Cursor
<project>/.cursor/rules/specops.mdc # Project rules

# Codex
<project>/.codex/skills/specops/    # Skill installation

# Copilot
<project>/.github/instructions/     # Scoped instructions

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

```
/specops                        # Launch SpecOps agent
/specops view <spec-name>       # View a spec
/specops list                   # List all specs
Ctrl+C                          # Cancel current operation
```

## Example Session Flow

```
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
    "autoCommit": true,
    "testing": "auto"
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
    "createPR": true,
    "testing": "auto"
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

**Version**: 1.2.0
**Keep this reference handy for daily development!**
