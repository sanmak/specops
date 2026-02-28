# SpecOps for Claude Code

## Installation

### Option 1: User-level (available in all projects)

```bash
bash platforms/claude/install.sh
# Select option 1
```

Or manually:

```bash
mkdir -p ~/.claude/skills/specops
cp platforms/claude/skill.json ~/.claude/skills/specops/
cp platforms/claude/prompt.md ~/.claude/skills/specops/
```

### Option 2: Project-level (available only in this project)

```bash
mkdir -p .claude/skills/specops
cp platforms/claude/skill.json .claude/skills/specops/
cp platforms/claude/prompt.md .claude/skills/specops/
```

## Usage

After installation, restart Claude Code and use the slash command:

```
/specops Add user authentication with OAuth
/specops bugfix Users getting 500 errors on checkout
/specops refactor Extract API layer into repository pattern
/specops implement auth-feature
```

## Configuration

Create a `.specops.json` in your project root. See [examples/](../../examples/) for configuration templates.

## More Information

See the main [README](../../README.md) for full documentation.
