# Team Collaboration Guide

This guide helps teams adopt and standardize SpecOps across projects and team members.

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

## Team Workflows

### Feature Development Workflow

1. **Product Manager** creates feature brief
2. **Developer** runs `/specops` to create spec
3. **Spec Review** (if `reviewRequired: true`)
   - PM reviews requirements
   - Tech lead reviews design
   - Team discusses in PR/meeting
4. **Implementation** proceeds after approval
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

## Best Practices for Teams

### 1. Commit Specs to Git
```bash
git add .specops/
git commit -m "Add spec for user authentication"
```

**Benefits:**
- Team visibility
- Change history
- Review in PRs
- Documentation

### 2. Review Specs in PRs

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

### 3. Use Consistent Naming

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

### 4. Maintain Spec Quality

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

### 5. Follow the Simplicity Principle

SpecOps specs and implementations should be proportional to the task:
- Small features get lean specs — skip irrelevant design.md sections
- Implementations use existing patterns rather than inventing new abstractions
- The agent avoids speculative features, unnecessary configuration, and premature optimization

When reviewing specs, watch for over-engineering: abstractions used once, error handling for impossible scenarios, configuration for values that won't change.

### 6. Track Metrics

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
- [ ] Review spec creation process

### Demo Workflow

**For new team members:**

1. **Show existing spec**
   ```bash
   cat .specops/existing-feature/requirements.md
   cat .specops/existing-feature/design.md
   ```

2. **Create sample spec together**
   ```
   /specops Add a simple feature (guided)
   ```

3. **Review generated spec**
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

See [SECURITY.md](SECURITY.md) for the full security policy, including:
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
