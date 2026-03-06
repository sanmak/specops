# SpecOps for GitHub Copilot

## Installation

### Quick Install (no clone needed)

```bash
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform copilot
```

### Option 1: Using the installer

```bash
bash platforms/copilot/install.sh /path/to/your/project
```

### Option 2: Manual

```bash
mkdir -p /path/to/your/project/.github/instructions
cp platforms/copilot/specops.instructions.md /path/to/your/project/.github/instructions/
```

## Usage

When using GitHub Copilot, trigger SpecOps with natural language:

```
Use specops to add user authentication with OAuth
Create a spec for fixing the 500 errors on checkout
Spec-driven refactor of the API layer to use repository pattern
Implement the auth-feature spec
Review the oauth-auth spec
Approve the oauth-auth spec with suggestion: add load testing
Show specops status
View the auth-feature spec
Show me the auth-feature design
Walk me through the auth-feature spec
List all specops specs
```

## Notes

- GitHub Copilot supports interactive questions via the chat interface. SpecOps will ask for clarification when needed.
- Progress is noted in chat responses as tasks complete.
- SpecOps installs as a scoped instruction file (`.github/instructions/`), so it won't conflict with your project's `copilot-instructions.md`.

## Configuration

Create a `.specops.json` in your project root. See [examples/](../../examples/) for configuration templates.

## More Information

- [Quick Start & Troubleshooting](../../QUICKSTART.md)
- [Configuration Reference](../../docs/REFERENCE.md)
- [Team Review Workflow](../../docs/TEAM_GUIDE.md)
