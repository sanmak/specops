#!/bin/bash

# SpecOps Installer — OpenAI Codex
# Installs SpecOps skill for OpenAI Codex

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Installer — OpenAI Codex"
echo "================================="
echo ""

# Default to current directory (project-level install)
INSTALL_DIR="${1:-.}"
TARGET_DIR="$INSTALL_DIR/.codex/skills/specops"

echo "Installing to: $TARGET_DIR/SKILL.md"
mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$TARGET_DIR/"

echo ""
echo "Installed successfully!"
echo ""

if [ -f "$TARGET_DIR/SKILL.md" ]; then
  echo "Installed files verified at $TARGET_DIR"
else
  echo "WARNING: Installation may be incomplete — missing files in $TARGET_DIR"
fi

echo ""
echo "Next steps:"
echo "1. Run Codex in your project"
echo "2. Ask it to 'use specops' or 'create a spec' for your feature"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
