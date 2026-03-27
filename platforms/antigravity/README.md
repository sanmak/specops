# SpecOps for Google Antigravity

Spec-driven development workflow for Google Antigravity.

## Installation

### Option 1: Run the installer

```bash
# From the SpecOps repository root
bash platforms/antigravity/install.sh
```

### Option 2: Manual install

```bash
mkdir -p /path/to/your/project/.agents/rules
cp platforms/antigravity/specops.md /path/to/your/project/.agents/rules/
```

### Option 3: Remote install (no clone needed)

```bash
curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform antigravity
```

## Usage

In Google Antigravity, trigger SpecOps by mentioning it:

```text
Use specops to add user authentication with OAuth
```

Other triggers:

```text
Create a spec for adding user authentication
Implement the auth-feature spec
View the auth-feature spec
List all specops specs
Use specops init to set up the project config
Use specops interview to explore a vague idea
Use specops update to check for updates
Use specops feedback to report an issue
```

## Configuration

Create a `.specops.json` in your project root:

```json
{
  "specsDir": ".specops",
  "vertical": "backend",
  "team": {
    "conventions": ["Use TypeScript", "Write tests"],
    "reviewRequired": false
  }
}
```

## Antigravity-Specific Notes

- SpecOps installs to `.agents/rules/specops.md`, which is the standard location for Antigravity agent rules
- The version is stored as an HTML comment (`<!-- specops-version: "X.Y.Z" -->`) at the top of the file
- Task delegation is supported via the Manager View when available
- Progress tracking is noted in chat responses since native progress tracking is not available

## Files

| File | Description |
| --- | --- |
| `platform.json` | Platform adapter (capabilities, tool mapping) |
| `specops.md` | Generated rules file (do not edit directly) |
| `install.sh` | Platform installer script |

## More Information

- [Full documentation](../../README.md)
- [Quick start guide](../../QUICKSTART.md)
- [Configuration reference](../../docs/REFERENCE.md)
