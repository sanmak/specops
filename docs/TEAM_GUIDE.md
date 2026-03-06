# Team Collaboration Guide

SpecOps includes a built-in spec review workflow designed for teams — structured review cycles, configurable approval gates, and section-by-section feedback before implementation begins. This guide covers setup, the review cycle, configuration, and platform-specific behavior.

## Getting Started as a Team

### 1. Designate a Team Champion

Choose someone to:
- Set up the initial configuration
- Define team conventions
- Train other team members
- Maintain and update the skill

### 2. Define Team Conventions

Create a shared `.specops.json` template with your team's conventions:

```json
{
  "team": {
    "conventions": [
      "Your team's coding standards",
      "Testing requirements",
      "Documentation expectations",
      "Code review process"
    ]
  }
}
```

**Example Team Conventions:**
- "Use TypeScript for all new code"
- "Write unit tests with minimum 80% coverage"
- "Document all public APIs"
- "Follow existing architectural patterns"
- "Keep functions under 50 lines"
- "Use meaningful names (no abbreviations)"
- "Handle errors explicitly"

### 3. Choose a Distribution Method

#### Option A: Git Repository (Recommended)
1. Fork or clone this repository
2. Customize for your team
3. Share repository URL with team
4. Team members clone and run `./setup.sh`

**Pros:** Version controlled, easy updates, trackable changes
**Cons:** Requires git access

#### Option B: Shared Network Drive
1. Copy `skills/specops/` to shared drive
2. Team members copy from shared location
3. Update centrally

**Pros:** Simple, no git required
**Cons:** Manual updates, no version control

#### Option C: Package Distribution
1. Package as npm/pip package
2. Publish to private registry
3. Team installs via package manager

**Pros:** Professional, versioned, easy updates
**Cons:** Requires package infrastructure

### 4. Standardize Configuration

Create a **team configuration template** that all projects use:

**`team-specops-config.json`**
```json
{
  "specsDir": ".specops",
  "team": {
    "conventions": [
      "Load from team standards doc"
    ],
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

Add to project setup:
```bash
cp team-specops-config.json .specops.json
```

### 5. Integrate with Project Templates

Add SpecOps config to your project templates:

**Project scaffold:**
```
new-project/
  .specops.json          (from team template)
  .specops/              (empty, ready for specs)
    templates/        (custom templates)
  CLAUDE.md           (reference SpecOps in AI instructions)
```

## Developer Setup (Contributors)

After cloning the SpecOps repository, install git hooks to catch CI failures locally:

```bash
bash scripts/install-hooks.sh
```

This installs two hooks:
- **Pre-commit** (~1-2s): JSON syntax validation, ShellCheck on staged `.sh` files, stale generated files detection, stale checksums detection
- **Pre-push** (~5-8s): Full platform validation, checksum verification, generated file freshness, schema checks, full test suite, ShellCheck on all scripts

Bypass when needed: `git commit --no-verify` / `git push --no-verify`

## Team Workflows

### Feature Development Workflow

1. **Product Manager** creates feature brief
2. **Developer** runs `/specops` to create spec (creates `spec.json` with status `draft`)
3. **Spec Review** (if `specReview.enabled` or `reviewRequired: true`)
   - Developer commits spec and pushes — status becomes `in-review`
   - Reviewers pull and run `review <spec-name>` to provide structured feedback
   - Author runs `revise <spec-name>` to address feedback (version increments, approvals reset)
   - Reviewers approve — once `minApprovals` met, status becomes `approved`
4. **Implementation** proceeds after approval (implementation gate checks `spec.json`)
5. **Implementation Notes** tracked in `implementation.md` (decisions, deviations, blockers)
6. **Code Review** follows normal process
7. **Spec Update** if implementation deviates

### Bug Fix Workflow

1. **QA/User** reports bug
2. **Developer** runs `/specops bugfix [description]`
3. **Root Cause Analysis** in `bugfix.md`
4. **Fix Review** (quick approval)
5. **Implementation** with tests
6. **Verification** by QA

### Refactoring Workflow

1. **Developer** identifies refactoring need
2. **Spec Creation** with `/specops`
3. **Team Review** of refactoring scope
4. **Incremental Implementation**
5. **Continuous Testing** during refactor
6. **Documentation Update**

## Collaborative Spec Review

<p align="center">
  <img src="assets/review-workflow.svg" alt="SpecOps review workflow" width="800"/>
</p>

### Overview

The collaborative review workflow adds structured team review between spec creation and implementation. Specs move through a lifecycle: `draft` → `in-review` → `approved` → `implementing` → `completed`.

### Enable Review

Add `specReview` to your `.specops.json`:

```json
{
  "team": {
    "specReview": { "enabled": true, "minApprovals": 2 }
  }
}
```

### Files Created

- **`spec.json`** — Per-spec lifecycle metadata (always created, even without review enabled). Tracks status, version, author, reviewers, and approvals.
- **`reviews.md`** — Structured review feedback organized by review rounds. Created during the first review.
- **`index.json`** — Auto-generated global index at `<specsDir>/index.json`. Rebuilt whenever any `spec.json` changes.

### How Identity Detection Works

The agent runs `git config user.email` to identify the current user:
- If the current user is **not** the spec author → **Review mode** (provide feedback and verdict)
- If the current user **is** the author and changes were requested → **Revision mode** (address feedback)

### Implementation Gate

When review is enabled, Phase 3 (Implementation) checks `spec.json` before proceeding:
- If status is `approved` → proceed to implementation
- If not approved → warn the user and ask whether to override (interactive) or stop (non-interactive)

### Status Dashboard

View all specs and their review status:

```
/specops status              # Show all specs
/specops status in-review    # Filter by status
```

```
Spec Status Dashboard
═══════════════════════════════════════════════════════════
Spec                   Status         Approvals  Version
───────────────────────────────────────────────────────────
user-auth              approved       2/2        v2
payment-gateway        in-review      1/2        v1
refactor-api           draft          0/1        v1
bugfix-checkout        implementing   2/2        v1
═══════════════════════════════════════════════════════════
Total: 4 specs | 1 approved | 1 in-review | 1 draft | 1 implementing
```

## Platform Review Behavior

Review works across all platforms, with behavior adapted to each platform's capabilities.

| Capability | Claude Code | Cursor | Codex | Copilot |
|---|---|---|---|---|
| Spec creation + spec.json | Full | Full | Full | Full |
| Interactive review (ask questions) | Yes | Yes | No | Yes |
| Review feedback collection | Section-by-section | Section-by-section | All-in-prompt | Section-by-section |
| Verdict selection | Interactive choice | Interactive choice | Parsed from prompt | Interactive choice |
| Revision mode | Interactive guidance | Interactive guidance | Prompt-directed | Interactive guidance |
| Implementation gate override | Ask user | Ask user | Hard stop | Ask user |
| Progress tracking | TodoWrite tool | Chat responses | stdout | Chat responses |

### Claude Code Examples

```
/specops Add OAuth authentication          # Create spec
/specops review oauth-auth                 # Review someone's spec
/specops revise oauth-auth                 # Revise after feedback
/specops implement oauth-auth              # Implement approved spec
/specops status                            # Show all specs dashboard
/specops status in-review                  # Show only specs needing review
/specops view oauth-auth                   # View spec summary
/specops view oauth-auth design            # View design section
/specops view oauth-auth walkthrough       # Interactive guided tour
/specops list                              # List all specs with status
```

### Cursor Examples

```
"Use specops to add OAuth authentication"
"Review the oauth-auth spec"
"Revise the oauth-auth spec based on feedback"
"Implement the oauth-auth spec"
"Show specops status"
"View the oauth-auth spec"
"Show me the oauth-auth design"
"Walk me through the oauth-auth spec"
"List all specops specs"
```

### Codex Examples

```
"Use specops to add OAuth authentication"
"Review the oauth-auth spec — token refresh is missing from Story 3,
 increase session limit to 50k. Request changes."
"Revise oauth-auth — add token refresh to Story 3, update session limit to 50k"
"Implement the oauth-auth spec"
"View the oauth-auth spec"
"List all specops specs"
```

> **Note:** Codex requires all feedback and verdict in the initial prompt since it cannot ask interactive questions.

### Copilot Examples

```
"Use specops to add OAuth authentication"
"Review the oauth-auth spec"
"Approve the oauth-auth spec with suggestion: add load testing"
"Implement the oauth-auth spec"
"Show specops status"
"View the oauth-auth spec"
"Walk me through the oauth-auth spec"
"List all specops specs"
```

### Platform Shortfalls

- **Codex**: No interactive questions — reviewer must provide all feedback and verdict in prompt text. Cannot interactively override implementation gate. No section-by-section walkthrough.
- **Cursor / Copilot**: No built-in progress tracking — review progress shown in chat responses only.
- **All platforms**: No push notifications for review requests. Teams rely on git/PR/task-tracker notifications. Review is asynchronous via git commits.

## Practical Team Workflow Example

Three engineers collaborating on `feature-user-authentication`:

```
Timeline:
─────────────────────────────────────────────────────────

Day 1 - Alice (Claude Code):
  /specops Add user authentication with OAuth
  → Spec created in .specops/user-auth/
  → spec.json: { status: "in-review", author: "alice@acme.com", version: 1 }
  → git commit + push to branch spec/user-auth
  → Creates PR #42: "Spec: User Authentication with OAuth"

Day 1 - Bob (Cursor):
  "Review the user-auth spec"
  → Reads spec, provides feedback:
    - requirements.md: "Missing token refresh in Story 3"
    - design.md: "Session limit should be 50k not 10k"
  → Verdict: Changes Requested
  → reviews.md updated, spec.json: bob → changes-requested
  → git commit + push

Day 2 - Carol (Copilot):
  "Review the user-auth spec"
  → Reads spec, approves with suggestion:
    - design.md: "Consider adding load testing"
  → Verdict: Approved with suggestions
  → reviews.md updated, spec.json: carol → approved, approvals: 1/2

Day 2 - Alice (Claude Code):
  /specops revise user-auth
  → Agent shows Bob's feedback summary
  → Alice revises: adds token refresh, updates session limit
  → spec.json: { version: 2, reviewRounds: 2, approvals: 0 (reset) }
  → git commit + push

Day 2 - Bob (Cursor):
  "Approve the user-auth spec"
  → Reviews v2, approves
  → spec.json: { approvals: 1/2 }

Day 3 - Carol (Copilot):
  "Approve the user-auth spec"
  → spec.json: { status: "approved", approvals: 2/2 }

Day 3 - Alice (Claude Code):
  /specops implement user-auth
  → Gate check passes (2/2 approvals)
  → Implementation begins...
  → spec.json: { status: "completed" }
```

## Best Practices for Teams

### 1. Review Specs Collaboratively Before Implementing

Enable `specReview` and require approvals from at least 2 team members before implementation begins. This catches design issues early and ensures team alignment.

### 2. Commit Specs to Git
```bash
git add .specops/
git commit -m "Add spec for user authentication"
```

**Benefits:**
- Team visibility
- Change history
- Review in PRs
- Documentation

### 3. Review Specs in PRs

Include spec files in PR:
```
PR: Add OAuth Authentication
Files:
  - .specops/oauth-auth/requirements.md
  - .specops/oauth-auth/design.md
  - .specops/oauth-auth/tasks.md
  - src/auth/*.ts (implementation)
```

**Review checklist:**
- [ ] Requirements are clear
- [ ] Design matches team architecture
- [ ] Tasks are well-scoped
- [ ] Implementation follows design
- [ ] Tests cover acceptance criteria

### 4. Use Consistent Naming

**Spec directory naming convention:**
```
.specops/
  feature-user-auth/
  feature-payment-gateway/
  bugfix-checkout-500/
  bugfix-login-timeout/
  refactor-api-layer/
```

Pattern: `<type>-<brief-description>`

### 5. Maintain Spec Quality

**Good spec characteristics:**
- Clear acceptance criteria
- Detailed design rationale
- Task breakdown with dependencies
- Security considerations
- Test coverage plan

**Review specs regularly:**
- Update as requirements change
- Archive completed specs
- Learn from past specs

### 6. Follow the Simplicity Principle

SpecOps specs and implementations should be proportional to the task:
- Small features get lean specs — skip irrelevant design.md sections
- Implementations use existing patterns rather than inventing new abstractions
- The agent avoids speculative features, unnecessary configuration, and premature optimization

When reviewing specs, watch for over-engineering: abstractions used once, error handling for impossible scenarios, configuration for values that won't change.

### 7. Track Metrics

Monitor team usage:
- Number of specs created per sprint
- Spec → implementation time
- Spec deviation rate
- Team satisfaction with process

## Integration with Development Process

### Jira/Linear Integration

Configure task tracking:
```json
{
  "team": {
    "taskTracking": "jira",
    "taskPrefix": "PROJ-"
  }
}
```

Agent will:
- Reference tickets in tasks
- Update ticket status
- Link commits to tickets

### GitHub Integration

```json
{
  "team": {
    "taskTracking": "github"
  },
  "implementation": {
    "createPR": true
  }
}
```

Agent will:
- Create issues for tasks
- Link commits to issues
- Auto-create PR with spec reference

### CI/CD Integration

Add spec validation to CI:
```yaml
# .github/workflows/validate-specs.yml
name: Validate Specs
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Specs
        run: |
          # Check all specs have required files
          find .specops -type d -mindepth 1 -maxdepth 1 | while read dir; do
            [ -f "$dir/requirements.md" ] || [ -f "$dir/bugfix.md" ] || exit 1
            [ -f "$dir/design.md" ] || exit 1
            [ -f "$dir/tasks.md" ] || exit 1
          done
```

## Training New Team Members

### Onboarding Checklist

- [ ] Install Claude Code
- [ ] Clone/install SpecOps
- [ ] Review team conventions
- [ ] Read example specs
- [ ] Walk through demo workflow
- [ ] Create first spec with mentor
- [ ] Review team review workflow process
- [ ] Review spec creation process

### Demo Workflow

**For new team members:**

1. **Show existing spec**
   ```
   /specops view existing-feature                # Summary overview
   /specops view existing-feature walkthrough     # Guided tour
   /specops list                                  # See all specs
   ```

2. **Create sample spec together**
   ```
   /specops Add a simple feature (guided)
   ```

3. **Review generated spec**
   ```
   /specops view simple-feature                  # Quick summary
   /specops view simple-feature design           # Dive into design
   ```
   - Discuss requirements clarity
   - Review design decisions
   - Understand task breakdown

4. **Walk through implementation**
   - Show task tracking
   - Demonstrate progress updates
   - Review completed work

### Training Materials

Create team-specific materials:
- **Video walkthrough** of SpecOps workflow
- **Example specs** from your projects
- **Common patterns** documentation
- **Troubleshooting guide** for your setup

## Customization for Your Team

### Custom Templates

Create team templates:
```
.specops/templates/
  feature-api.md       (API feature template)
  feature-ui.md        (UI feature template)
  bugfix-backend.md    (Backend bug template)
  bugfix-frontend.md   (Frontend bug template)
```

Custom templates support `{{variable}}` placeholders: `{{title}}`, `{{stories}}`, `{{criteria}}`, `{{conventions}}`, `{{date}}`, `{{type}}`. Any other `{{variable}}` is filled contextually.

Reference in config:
```json
{
  "templates": {
    "feature-api": "team-api-template",
    "feature-ui": "team-ui-template"
  }
}
```

### Module-Specific Configuration

For monorepo/multi-module projects:
```json
{
  "modules": {
    "backend": {
      "specsDir": "backend/specs",
      "conventions": ["Backend-specific conventions"]
    },
    "frontend": {
      "specsDir": "frontend/specs",
      "conventions": ["Frontend-specific conventions"]
    }
  }
}
```

Module conventions **merge with** root `team.conventions`. Module-specific conventions take priority on conflicts.

### Extend with Team Tools

Add team-specific integrations:
```json
{
  "integrations": {
    "ci": "github-actions",
    "deployment": "vercel",
    "monitoring": "sentry",
    "analytics": "mixpanel"
  }
}
```

## Vertical Support

SpecOps has first-class vertical support. Configure `"vertical"` in `.specops.json` to adapt templates:

```json
{
  "vertical": "infrastructure"
}
```

Or let the agent auto-detect from the request. Available verticals: `backend`, `frontend`, `fullstack`, `infrastructure`, `data`, `library`.

For maximum customization, combine `vertical` with custom templates:

```json
{
  "vertical": "infrastructure",
  "templates": {
    "feature": "infra-requirements",
    "design": "infra-design"
  }
}
```

Example templates are provided in `examples/templates/` for infrastructure, data pipelines, and library development.

## Troubleshooting Common Issues

### Specs inconsistent across team
**Solution:** Create and share team template config

### Too much/too little detail in specs
**Solution:** Review example specs as team, define standards

### Implementation deviates from specs
**Solution:** Enable `reviewRequired: true`, review specs in PRs

### Specs become stale
**Solution:** Include spec updates in definition of done

### Team finds process too slow
**Solution:** Reduce `reviewRequired` for small changes, use minimal config

## Security & Compliance for Enterprise Teams

### Security Posture

SpecOps includes security features designed for enterprise adoption:

- **Prompt injection defense**: The agent sanitizes `team.conventions` entries and custom template content, skipping any that contain meta-instructions
- **Data handling policy**: Secrets are never included in generated specs (replaced with placeholders like `$DATABASE_URL`). PII uses synthetic data.
- **Schema hardening**: All configuration fields enforce validation constraints — path patterns, length limits, and strict object schemas (`additionalProperties: false`)
- **Path containment**: `specsDir` values with absolute paths or `../` traversal are rejected
- **Config conflict detection**: Contradictory settings (e.g., `requireTests: true` + `testing: "skip"`) are flagged before implementation

### Vulnerability Reporting

See [SECURITY.md](../SECURITY.md) for the full security policy, including:
- How to report vulnerabilities (GitHub Security Advisories)
- Response timeline (48h acknowledgment, 7-day triage)
- Scope of security issues

### Supply Chain Transparency

- **Zero runtime dependencies** — see [SBOM.md](SBOM.md) for the complete Software Bill of Materials
- **File integrity verification** — use `CHECKSUMS.sha256` to verify installed files have not been tampered with:
  ```bash
  shasum -a 256 -c CHECKSUMS.sha256
  ```
- **Automated testing** — the CI pipeline validates all JSON files, runs schema constraint tests, and lints shell scripts

### Trust Model

Anyone with write access to a project's `.specops.json` can influence agent behavior. Treat `.specops.json` changes with the same scrutiny as code changes in PRs.

### Recommended Enterprise Settings

```json
{
  "team": {
    "reviewRequired": true,
    "specReview": { "enabled": true, "minApprovals": 2 },
    "codeReview": {
      "required": true,
      "requireTests": true
    }
  },
  "implementation": {
    "autoCommit": false,
    "createPR": false,
    "testing": "auto"
  }
}
```

## Measuring Success

Track these metrics:
- **Adoption rate:** % of features with specs
- **Quality:** Fewer bugs after spec-driven development
- **Speed:** Faster development with clear plans
- **Collaboration:** Better communication via specs
- **Satisfaction:** Developer happiness with process

## Getting Help

- **Documentation:** Read README.md
- **Quick Reference:** See REFERENCE.md
- **Security:** See SECURITY.md for vulnerability reporting
- **Contributing:** See CONTRIBUTING.md for contribution guidelines
- **Examples:** Review examples/ directory
- **Issues:** Check GitHub issues
- **Team Discussion:** Share experiences with team

---

**Remember:** SpecOps should enhance your process, not burden it. Customize to fit your team's workflow and adjust as you learn what works best.
