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
