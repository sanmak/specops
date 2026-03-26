#!/bin/bash

# SpecOps Installer -- Google Antigravity
# Installs SpecOps rules for Google Antigravity

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Installer -- Google Antigravity"
echo "========================================"
echo ""

# Default to current directory (project-level install)
INSTALL_DIR="${1:-.}"

RULES_DIR="$INSTALL_DIR/.agents/rules"

# Check for .gitignore conflicts on project-level installs
if [[ "$INSTALL_DIR" == "." ]] && [[ -f ".gitignore" ]]; then
  if grep -q -E "^\.agents/?$|^\.agents/\*" ".gitignore"; then
    echo ""
    echo "WARNING: Project .gitignore blocks tracking of .agents/"
    echo ""
    echo "Your .gitignore excludes .agents/ or .agents/*, which means the installed"
    echo "specops.md will not be tracked by git. Team members cloning this repo won't"
    echo "have SpecOps available unless they install it individually."
    echo ""
    echo "To fix this, selectively un-ignore .agents/rules/ in your .gitignore:"
    echo "  Add this line to .gitignore:  !.agents/rules/"
    echo ""
    read -rp "Proceed with project-level install anyway? [y/N]: " proceed
    if [[ ! $proceed =~ ^[Yy]$ ]]; then
      echo "Aborted."
      exit 1
    fi
  fi
fi

echo ""
echo "Installing to: $RULES_DIR/specops.md"
mkdir -p "$RULES_DIR"
cp "$SCRIPT_DIR/specops.md" "$RULES_DIR/specops.md"

echo "Installed successfully!"
echo ""

# Update .specops.json with version metadata if it exists
if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
  SPECOPS_VER="$(grep '<!-- specops-version:' "$SCRIPT_DIR/specops.md" | head -1 | sed 's/.*specops-version: *"//;s/".*//')"
  INSTALL_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  if [ -n "$SPECOPS_VER" ]; then
    SPECOPS_VER="$SPECOPS_VER" INSTALL_TS="$INSTALL_TS" python3 - <<'PY'
import json
import os

with open(".specops.json", "r") as f:
    d = json.load(f)
d["_installedVersion"] = os.environ["SPECOPS_VER"]
d["_installedAt"] = os.environ["INSTALL_TS"]
with open(".specops.json", "w") as f:
    json.dump(d, f, indent=2)
    f.write("\n")
PY
    echo "Updated .specops.json with version metadata"
  fi
fi

echo "Next steps:"
echo "1. Open the project in Google Antigravity"
echo "2. The SpecOps rules will activate when you mention 'specops' or 'spec-driven development'"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
