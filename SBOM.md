# Software Bill of Materials (SBOM)

## Runtime Dependencies

**None.** SpecOps has zero runtime dependencies. It consists entirely of:
- Markdown files (agent prompt, documentation)
- JSON files (configuration schema, skill metadata, examples)
- Shell scripts (installation, verification)

This zero-dependency design minimizes supply chain attack surface.

## Development / CI Dependencies

These are used only in the CI pipeline and test suite, not at runtime:

| Dependency | Purpose | Required |
|-----------|---------|----------|
| Python 3 | JSON validation, schema testing | Yes (CI) |
| [jsonschema](https://pypi.org/project/jsonschema/) | Validate configs against JSON Schema | Yes (CI) |
| [ShellCheck](https://www.shellcheck.net/) | Shell script static analysis | Yes (CI) |
| jq | JSON validation in verify.sh | Optional |

## Installed File Inventory

When SpecOps is installed, only these files are copied to the target directory:

| File | Purpose |
|------|---------|
| `skill.json` | Skill metadata, command definitions, configuration schema |
| `prompt.md` | Agent instructions defining the spec-driven workflow |

## Integrity Verification

After installation, verify file integrity:

```bash
# Run the verification script
bash verify.sh

# Or manually validate JSON
python3 -c "import json; json.load(open('skills/specops/skill.json'))"

# Check installed files against checksums
shasum -a 256 -c CHECKSUMS.sha256 --ignore-missing
```

## Supply Chain Transparency

- **Source**: All code is available in this repository
- **No binary artifacts**: Everything is human-readable text
- **No post-install scripts**: Installation is a simple file copy (`cp`)
- **No network access**: Installation does not fetch anything from the internet
- **No package registry**: Not distributed via npm, pip, or similar registries
