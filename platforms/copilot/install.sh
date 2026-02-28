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
TARGET_DIR="$INSTALL_DIR/.github"
TARGET="$TARGET_DIR/copilot-instructions.md"

if [ -f "$TARGET" ]; then
  echo "copilot-instructions.md already exists at $TARGET"
  echo ""
  echo "Options:"
  echo "1) Append SpecOps instructions to existing copilot-instructions.md"
  echo "2) Replace copilot-instructions.md with SpecOps instructions"
  echo "3) Cancel"
  read -rp "Select option [1-3]: " choice

  case $choice in
    1)
      echo "" >> "$TARGET"
      echo "---" >> "$TARGET"
      echo "" >> "$TARGET"
      cat "$SCRIPT_DIR/copilot-instructions.md" >> "$TARGET"
      echo "Appended SpecOps instructions to $TARGET"
      ;;
    2)
      cp "$SCRIPT_DIR/copilot-instructions.md" "$TARGET"
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
  mkdir -p "$TARGET_DIR"
  cp "$SCRIPT_DIR/copilot-instructions.md" "$TARGET"
  echo "Created $TARGET"
fi

echo ""
echo "Installed successfully!"
echo ""
echo "Next steps:"
echo "1. Open the project in VS Code with GitHub Copilot enabled"
echo "2. Ask Copilot to 'use specops' or 'create a spec' for your feature"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
