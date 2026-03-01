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
mkdir -p /path/to/your/project/.github
cp platforms/copilot/copilot-instructions.md /path/to/your/project/.github/copilot-instructions.md
```

If you already have a `copilot-instructions.md`, append the SpecOps content to it.

## Usage

When using GitHub Copilot, trigger SpecOps with natural language:

```
Use specops to add user authentication with OAuth
Create a spec for fixing the 500 errors on checkout
Spec-driven refactor of the API layer to use repository pattern
Implement the auth-feature spec
```

## Notes

- GitHub Copilot supports interactive questions via the chat interface. SpecOps will ask for clarification when needed.
- Progress is noted in chat responses as tasks complete.

## Configuration

Create a `.specops.json` in your project root. See [examples/](../../examples/) for configuration templates.

## More Information

See the main [README](../../README.md) for full documentation.
