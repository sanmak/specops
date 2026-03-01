# SpecOps for OpenAI Codex

## Installation

### Quick Install (no clone needed)

```bash
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform codex
```

### Option 1: Using the installer

```bash
bash platforms/codex/install.sh /path/to/your/project
```

### Option 2: Manual

```bash
cp platforms/codex/AGENTS.md /path/to/your/project/AGENTS.md
```

If you already have an `AGENTS.md`, append the SpecOps content to it.

## Usage

When using Codex, trigger SpecOps with natural language:

```
Use specops to add user authentication with OAuth
Create a spec for fixing the 500 errors on checkout
Spec-driven refactor of the API layer to use repository pattern
Implement the auth-feature spec
```

## Notes

- Codex runs autonomously without interactive questions. SpecOps will document any assumptions it makes in the spec files.
- Progress is printed to stdout as tasks complete.

## Configuration

Create a `.specops.json` in your project root. See [examples/](../../examples/) for configuration templates.

## More Information

See the main [README](../../README.md) for full documentation.
