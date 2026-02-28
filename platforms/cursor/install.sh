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

echo "Installing to: $RULES_DIR/specops.mdc"
mkdir -p "$RULES_DIR"
cp "$SCRIPT_DIR/specops.mdc" "$RULES_DIR/specops.mdc"

echo "Installed successfully!"
echo ""
echo "Next steps:"
echo "1. Open the project in Cursor"
echo "2. The SpecOps rules will activate when you mention 'specops' or 'spec-driven development'"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
