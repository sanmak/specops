# Quick Start Guide

Get up and running with SpecOps in 5 minutes.

## Installation (1 minute)

### Option 0: Plugin Marketplace (Recommended)

**Claude Code:**

```text
/plugin marketplace add sanmak/specops
/plugin install specops@specops-marketplace
/reload-plugins
```

**Cursor:** Search "specops" in Cursor Settings > Extensions, or visit [cursor.com/marketplace](https://cursor.com/marketplace)

**OpenAI Codex:** Search "specops" in the Codex skills catalog

**GitHub Copilot:** Search "specops" in Copilot Extensions marketplace

### Option 1: One-Line Install (no clone needed)

```bash
# Interactive — detects your tools and prompts for choices
bash <(curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh)

# Non-interactive — specify platform directly
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform claude --scope user
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform cursor
```

### Option 2: Clone and Run Setup

```bash
git clone https://github.com/sanmak/specops.git
cd specops
bash setup.sh
```

The setup script detects your installed AI coding tools and installs SpecOps for each.

### Option 3: Platform-Specific Setup

**Claude Code:**

```bash
mkdir -p ~/.claude/skills/specops
cp platforms/claude/SKILL.md ~/.claude/skills/specops/
```

**Cursor:**

```bash
mkdir -p /path/to/your/project/.cursor/rules
cp platforms/cursor/specops.mdc /path/to/your/project/.cursor/rules/
```

**OpenAI Codex:**

```bash
mkdir -p /path/to/your/project/.codex/skills/specops
cp platforms/codex/SKILL.md /path/to/your/project/.codex/skills/specops/
```

**GitHub Copilot:**

```bash
mkdir -p /path/to/your/project/.github/instructions
cp platforms/copilot/specops.instructions.md /path/to/your/project/.github/instructions/
```

**Google Antigravity:**

```bash
mkdir -p /path/to/your/project/.agents/rules
cp platforms/antigravity/specops.md /path/to/your/project/.agents/rules/
```

## First Use (2 minutes)

### 1. Create a project config

```bash
cp examples/.specops.json .specops.json
# Edit to customize for your project
```

### 2. Run SpecOps

**Claude Code:**

```text
/specops Add a login page with email and password
```

**Cursor / Codex:**

```text
Use specops to add a login page with email and password
```

The agent will:

- Create `.specops/login-page/` directory
- Generate `requirements.md` with user stories
- Create `design.md` with component structure
- Build `tasks.md` with implementation steps
- Implement if you approve

### 3. View Your Specs

Once a spec exists, view it directly through the assistant instead of opening raw files:

**Claude Code:**

```text
/specops view login-page                   # Executive summary
/specops view login-page design            # Design section only
/specops view login-page full              # All sections
/specops view login-page walkthrough       # Interactive guided tour
/specops list                              # Overview of all specs
/specops view initiative oauth-payments    # Initiative progress
/specops list initiatives                  # All initiatives
```

**Cursor / Codex:**

```text
View the login-page spec
Show me the login-page design
Walk me through the login-page spec
List all specops specs
```

View modes: `summary` (default), `full`, `status`, `walkthrough`, or specific sections (`requirements`, `design`, `tasks`, `implementation`, `reviews`). Combine sections: `view login-page requirements design`.

> **Full command reference:** See [docs/COMMANDS.md](docs/COMMANDS.md) for the exhaustive list of all commands, triggers, and platform differences.

## Configuration

### Minimal

```json
{
  "specsDir": ".specops"
}
```

### Recommended

```json
{
  "specsDir": ".specops",
  "vertical": "backend",
  "team": {
    "conventions": [
      "Use TypeScript",
      "Write tests",
      "Follow existing patterns"
    ],
    "reviewRequired": true
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto"
  }
}
```

Save as `.specops.json` in your project root.

> **Tip:** Set `"vertical"` to match your project type (`backend`, `frontend`, `fullstack`, `infrastructure`, `data`, `library`, `builder`) for domain-adapted specs.

## Example Workflows

### Feature Development

```text
Add user authentication with OAuth
```

Agent creates complete spec, reviews with you, implements, creates PR.

### Bug Fix

```text
Fix: Users can't submit form with special characters
```

Agent investigates, documents root cause, proposes fix, implements with tests.

### Refactoring

```text
Refactor API layer to use repository pattern
```

Agent analyzes current code, designs refactoring approach, implements incrementally.

### Example: Large Feature

```text
Add OAuth authentication and payment processing
```

If the feature spans multiple bounded contexts, SpecOps automatically detects this during scope assessment (Phase 1.5) and proposes splitting it into coordinated specs:

```text
Agent:
  Scope assessment → 2 bounded contexts detected
  Proposed split:
    Spec 1: oauth-authentication (wave 1)
    Spec 2: payment-processing (wave 2, depends on auth)
  Initiative created: oauth-payments

You approve → 2 specs created with cross-spec dependencies
/specops initiative oauth-payments → executes both in wave order
/specops view initiative oauth-payments → see progress across all specs
```

## What Gets Created

```text
your-project/
  .specops.json                         (config)
  .specops/                             (specs directory)
    index.json                          (auto-generated spec dashboard)
    feature-user-auth/
      spec.json                         (lifecycle metadata)
      requirements.md                   (user stories, acceptance criteria)
      design.md                         (architecture, decisions, diagrams)
      tasks.md                          (implementation task breakdown)
      implementation.md                 (optional: notes during implementation)
    initiatives/                        (created for multi-spec features)
      oauth-payments.json               (member specs, execution waves, status)
      oauth-payments-log.md             (execution trace)
```

## Team Review

Enable collaborative spec review so teammates approve specs before implementation:

1. **Enable** — add `"specReview": { "enabled": true, "minApprovals": 2 }` to `team` in `.specops.json`
2. **Create spec** — spec gets `spec.json` with status `in-review`, commit and push
3. **Review** — teammates pull and run `review <spec-name>` to provide feedback
4. **Approve** — once approvals meet threshold, status becomes `approved`
5. **Implement** — implementation gate passes, coding begins

**Solo developer?** Add `"allowSelfApproval": true` to `specReview` to enable self-review. You'll go through the same review ritual but can approve your own specs (recorded as `self-approved` for audit trail).

See [TEAM_GUIDE.md](docs/TEAM_GUIDE.md) for the full team review workflow.

## Next Steps

1. **Installed?** Try creating a real feature spec.
2. **Learn more**: Read [README.md](README.md) for full documentation
3. **Team setup**: See [TEAM_GUIDE.md](docs/TEAM_GUIDE.md) for team collaboration
4. **Customize**: Check [examples/](examples/) for configuration options
5. **Add platforms**: See [platforms/](platforms/) for platform-specific guides
