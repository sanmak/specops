# SpecOps for Cursor

## Installation

### Marketplace (Recommended)

Search "specops" in Cursor Settings > Extensions, or visit [cursor.com/marketplace](https://cursor.com/marketplace).

### Quick Install (no clone needed)

```bash
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform cursor
```

### Option 1: Using the installer

```bash
bash platforms/cursor/install.sh /path/to/your/project
```

### Option 2: Manual

```bash
mkdir -p /path/to/your/project/.cursor/rules
cp platforms/cursor/specops.mdc /path/to/your/project/.cursor/rules/specops.mdc
```

## Usage

In Cursor's AI chat, use natural language to trigger SpecOps:

```
Use specops to add user authentication with OAuth
Create a spec for fixing the 500 errors on checkout
Spec-driven refactor of the API layer to use repository pattern
Implement the auth-feature spec
Review the oauth-auth spec
Revise the oauth-auth spec based on feedback
Show specops status
View the auth-feature spec
Show me the auth-feature design
Walk me through the auth-feature spec
List all specops specs
```

The SpecOps rules activate when you mention "specops", "spec-driven development", or ask to "create a spec".

## Configuration

Create a `.specops.json` in your project root. See [examples/](../../examples/) for configuration templates.

## More Information

- [Command Reference](../../docs/COMMANDS.md)
- [Quick Start & Troubleshooting](../../QUICKSTART.md)
- [Configuration Reference](../../docs/REFERENCE.md)
- [Team Review Workflow](../../docs/TEAM_GUIDE.md)
