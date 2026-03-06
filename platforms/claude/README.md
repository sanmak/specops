# SpecOps for Claude Code

## Installation

### Quick Install (no clone needed)

```bash
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform claude --scope user
```

### Option 1: User-level (available in all projects)

```bash
bash platforms/claude/install.sh
# Select option 1
```

Or manually:

```bash
mkdir -p ~/.claude/skills/specops
cp platforms/claude/SKILL.md ~/.claude/skills/specops/
```

### Option 2: Project-level (available only in this project)

```bash
mkdir -p .claude/skills/specops
cp platforms/claude/SKILL.md .claude/skills/specops/
```

## Usage

After installation, restart Claude Code and use the slash command:

```
/specops Add user authentication with OAuth
/specops bugfix Users getting 500 errors on checkout
/specops refactor Extract API layer into repository pattern
/specops implement auth-feature
/specops review oauth-auth
/specops revise oauth-auth
/specops status
/specops status in-review
/specops view auth-feature
/specops view auth-feature design
/specops view auth-feature full
/specops view auth-feature walkthrough
/specops list
```

## Configuration

Create a `.specops.json` in your project root. See [examples/](../../examples/) for configuration templates.

## More Information

- [Command Reference](../../docs/COMMANDS.md)
- [Quick Start & Troubleshooting](../../QUICKSTART.md)
- [Configuration Reference](../../docs/REFERENCE.md)
- [Team Review Workflow](../../docs/TEAM_GUIDE.md)
