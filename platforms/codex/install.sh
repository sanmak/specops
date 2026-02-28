#!/bin/bash

# SpecOps Installer — OpenAI Codex
# Installs SpecOps agent instructions for OpenAI Codex

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Installer — OpenAI Codex"
echo "================================="
echo ""

# Default to current directory (project-level install)
INSTALL_DIR="${1:-.}"
TARGET="$INSTALL_DIR/AGENTS.md"

if [ -f "$TARGET" ]; then
  echo "AGENTS.md already exists at $TARGET"
  echo ""
  echo "Options:"
  echo "1) Append SpecOps instructions to existing AGENTS.md"
  echo "2) Replace AGENTS.md with SpecOps instructions"
  echo "3) Cancel"
  read -rp "Select option [1-3]: " choice

  case $choice in
    1)
      echo "" >> "$TARGET"
      echo "---" >> "$TARGET"
      echo "" >> "$TARGET"
      cat "$SCRIPT_DIR/AGENTS.md" >> "$TARGET"
      echo "Appended SpecOps instructions to $TARGET"
      ;;
    2)
      cp "$SCRIPT_DIR/AGENTS.md" "$TARGET"
      echo "Replaced $TARGET with SpecOps instructions"
      ;;
    3)
      echo "Cancelled."
      exit 0
      ;;
    *)
      echo "Invalid option. Exiting."
      exit 1
      ;;
  esac
else
  cp "$SCRIPT_DIR/AGENTS.md" "$TARGET"
  echo "Created $TARGET"
fi

echo ""
echo "Installed successfully!"
echo ""
echo "Next steps:"
echo "1. Run Codex in your project"
echo "2. Ask it to 'use specops' or 'create a spec' for your feature"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
