#!/bin/bash

# SpecOps Installer — GitHub Copilot
# Installs SpecOps instructions for GitHub Copilot

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Installer — GitHub Copilot"
echo "===================================="
echo ""

# Default to current directory (project-level install)
INSTALL_DIR="${1:-.}"
TARGET_DIR="$INSTALL_DIR/.github/instructions"
TARGET="$TARGET_DIR/specops.instructions.md"

# Check for .gitignore conflicts on project-level installs
if [[ "$INSTALL_DIR" == "." ]] && [[ -f ".gitignore" ]]; then
  if grep -q -E "^\.github/?$|^\.github/\*|^\.github/instructions" ".gitignore"; then
    echo ""
    echo "⚠️  WARNING: Project .gitignore blocks tracking of .github/instructions/"
    echo ""
    echo "Your .gitignore excludes .github or .github/instructions, which means the installed"
    echo "specops.instructions.md will not be tracked by git. Team members cloning this repo won't"
    echo "have SpecOps available unless they install it individually."
    echo ""
    echo "Two options to fix this:"
    echo ""
    echo "Option 1 (Recommended): Use user-level installation"
    echo "  → GitHub Copilot reads from .github/instructions/ in the current project"
    echo "  → For user-level, you'll need to configure it in VS Code settings"
    echo ""
    echo "Option 2: Selectively un-ignore .github/instructions/ in your .gitignore"
    echo "  → Add this line to .gitignore:  !.github/instructions/"
    echo "  → Tracks SpecOps but keeps other .github/ content as configured"
    echo ""
    read -rp "Proceed with project-level install anyway? [y/N]: " proceed
    if [[ ! $proceed =~ ^[Yy]$ ]]; then
      echo "Aborted."
      exit 1
    fi
  fi
fi

echo "Installing to: $TARGET"
mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/specops.instructions.md" "$TARGET"

echo ""
echo "Installed successfully!"
echo ""

if [ -f "$TARGET" ]; then
  echo "Installed files verified at $TARGET"
else
  echo "WARNING: Installation may be incomplete — missing files"
fi

echo ""
echo "Next steps:"
echo "1. Open the project in VS Code with GitHub Copilot enabled"
echo "2. Ask Copilot to 'use specops' or 'create a spec' for your feature"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
