# Quick Start Guide

Get up and running with SpecOps in 5 minutes.

## Installation (1 minute)

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
cp platforms/claude/skill.json ~/.claude/skills/specops/
cp platforms/claude/prompt.md ~/.claude/skills/specops/
```

**Cursor:**
```bash
mkdir -p /path/to/your/project/.cursor/rules
cp platforms/cursor/specops.mdc /path/to/your/project/.cursor/rules/
```

**OpenAI Codex:**
```bash
cp platforms/codex/AGENTS.md /path/to/your/project/AGENTS.md
```

## First Use (2 minutes)

### 1. Create a project config

```bash
cp examples/.specops.json .specops.json
# Edit to customize for your project
```

### 2. Run SpecOps

**Claude Code:**
```
/specops Add a login page with email and password
```

**Cursor / Codex:**
```
Use specops to add a login page with email and password
```

The agent will:
- Create `.specops/login-page/` directory
- Generate `requirements.md` with user stories
- Create `design.md` with component structure
- Build `tasks.md` with implementation steps
- Implement if you approve

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

> **Tip:** Set `"vertical"` to match your project type (`backend`, `frontend`, `fullstack`, `infrastructure`, `data`, `library`) for domain-adapted specs.

## Example Workflows

### Feature Development
```
Add user authentication with OAuth
```
Agent creates complete spec, reviews with you, implements, creates PR.

### Bug Fix
```
Fix: Users can't submit form with special characters
```
Agent investigates, documents root cause, proposes fix, implements with tests.

### Refactoring
```
Refactor API layer to use repository pattern
```
Agent analyzes current code, designs refactoring approach, implements incrementally.

## What Gets Created

```
your-project/
  .specops.json                         (config)
  .specops/                             (specs directory)
    feature-user-auth/
      requirements.md                   (user stories, acceptance criteria)
      design.md                         (architecture, decisions, diagrams)
      tasks.md                          (implementation task breakdown)
      implementation.md                 (optional: notes during implementation)
```

## Next Steps

1. **Installed?** Try creating a real feature spec.
2. **Learn more**: Read [README.md](README.md) for full documentation
3. **Team setup**: See [TEAM_GUIDE.md](TEAM_GUIDE.md) for team collaboration
4. **Customize**: Check [examples/](examples/) for configuration options
5. **Add platforms**: See [platforms/](platforms/) for platform-specific guides
