#!/bin/bash

# SpecOps Installer — Cursor
# Installs SpecOps rules for Cursor IDE

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Installer — Cursor"
echo "==========================="
echo ""

# Default to current directory (project-level install)
INSTALL_DIR="${1:-.}"

RULES_DIR="$INSTALL_DIR/.cursor/rules"

# Check for .gitignore conflicts on project-level installs
if [[ "$INSTALL_DIR" == "." ]] && [[ -f ".gitignore" ]]; then
  if grep -q -E "^\.cursor/?$|^\.cursor/\*" ".gitignore"; then
    echo ""
    echo "⚠️  WARNING: Project .gitignore blocks tracking of .cursor/"
    echo ""
    echo "Your .gitignore excludes .cursor/ or .cursor/*, which means the installed"
    echo "specops.mdc will not be tracked by git. Team members cloning this repo won't"
    echo "have SpecOps available unless they install it individually."
    echo ""
    echo "Two options to fix this:"
    echo ""
    echo "Option 1 (Recommended): Use user-level installation instead"
    echo "  → Installs to ~/.cursor/rules/specops.mdc (not project-specific)"
    echo "  → Unaffected by .gitignore"
    echo ""
    echo "Option 2: Selectively un-ignore .cursor/rules/ in your .gitignore"
    echo "  → Add this line to .gitignore:  !.cursor/rules/"
    echo "  → Tracks SpecOps but keeps other .cursor/ config local"
    echo ""
    read -rp "Proceed with project-level install anyway? [y/N]: " proceed
    if [[ ! $proceed =~ ^[Yy]$ ]]; then
      echo "Aborted. Consider using user-level installation instead."
      exit 1
    fi
  fi
fi

echo ""
echo "Installing to: $RULES_DIR/specops.mdc"
mkdir -p "$RULES_DIR"
cp "$SCRIPT_DIR/specops.mdc" "$RULES_DIR/specops.mdc"

echo "Installed successfully!"
echo ""

# Update .specops.json with version metadata if it exists
if [ -f ".specops.json" ]; then
  SPECOPS_VER="$(grep '^version:' "$SCRIPT_DIR/specops.mdc" | head -1 | sed 's/version: *"//;s/"//')"
  INSTALL_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  if [ -n "$SPECOPS_VER" ]; then
    python3 -c "
import json
with open('.specops.json', 'r') as f:
    d = json.load(f)
d['_installedVersion'] = '${SPECOPS_VER}'
d['_installedAt'] = '${INSTALL_TS}'
with open('.specops.json', 'w') as f:
    json.dump(d, f, indent=2)
    f.write('\n')
" && echo "Updated .specops.json with version metadata"
  fi
fi

echo "Next steps:"
echo "1. Open the project in Cursor"
echo "2. The SpecOps rules will activate when you mention 'specops' or 'spec-driven development'"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
