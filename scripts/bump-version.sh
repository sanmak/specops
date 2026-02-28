#!/bin/bash
# scripts/bump-version.sh -- Update version across all SpecOps JSON files
#
# Usage:
#   bash scripts/bump-version.sh <version>
#   bash scripts/bump-version.sh 1.0.0
#   bash scripts/bump-version.sh 2.1.3 --checksums
#
# The version must be valid semver (MAJOR.MINOR.PATCH).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Argument parsing ---
VERSION="${1:-}"
REGEN_CHECKSUMS=false

if [ -z "$VERSION" ]; then
  echo "Usage: bash scripts/bump-version.sh <version> [--checksums]"
  echo "Example: bash scripts/bump-version.sh 1.0.0"
  exit 1
fi

shift
for arg in "$@"; do
  case "$arg" in
    --checksums) REGEN_CHECKSUMS=true ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

# --- Validate semver format ---
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Error: '$VERSION' is not valid semver (expected MAJOR.MINOR.PATCH)"
  exit 1
fi

echo "Bumping version to $VERSION"

# --- List of JSON files to update ---
FILES=(
  "skills/specops/skill.json"
  "platforms/claude/skill.json"
  "platforms/claude/platform.json"
  "platforms/cursor/platform.json"
  "platforms/codex/platform.json"
  "platforms/copilot/platform.json"
)

# --- Update each file using Python (preserves JSON structure) ---
for file in "${FILES[@]}"; do
  filepath="$ROOT_DIR/$file"
  if [ ! -f "$filepath" ]; then
    echo "  SKIP: $file (not found)"
    continue
  fi

  python3 -c "
import json, sys
path = sys.argv[1]
version = sys.argv[2]
with open(path, 'r') as f:
    data = json.load(f)
data['version'] = version
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" "$filepath" "$VERSION"

  echo "  Updated: $file -> $VERSION"
done

# --- Optionally regenerate checksums ---
if [ "$REGEN_CHECKSUMS" = true ]; then
  echo ""
  echo "Regenerating CHECKSUMS.sha256..."
  cd "$ROOT_DIR"
  shasum -a 256 \
    skills/specops/skill.json \
    skills/specops/prompt.md \
    schema.json \
    platforms/claude/skill.json \
    platforms/claude/prompt.md \
    platforms/claude/platform.json \
    platforms/cursor/specops.mdc \
    platforms/cursor/platform.json \
    platforms/codex/AGENTS.md \
    platforms/codex/platform.json \
    platforms/copilot/copilot-instructions.md \
    platforms/copilot/platform.json \
    core/workflow.md \
    core/safety.md \
    > CHECKSUMS.sha256
  echo "  Updated: CHECKSUMS.sha256"
fi

echo ""
echo "Done! Version bumped to $VERSION across ${#FILES[@]} files."
