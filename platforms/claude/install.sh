#!/bin/bash

# SpecOps Installer — Claude Code
# Installs SpecOps skill for Claude Code

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Installer — Claude Code"
echo "================================"
echo ""

echo "How would you like to install SpecOps?"
echo "1) User installation (~/.claude/skills/specops)"
echo "2) Project installation (./.claude/skills/specops)"
echo "3) Custom location"
read -rp "Select option [1-3]: " choice

case $choice in
  1)
    INSTALL_DIR="$HOME/.claude/skills/specops"
    ;;
  2)
    INSTALL_DIR="./.claude/skills/specops"
    ;;
  3)
    read -rp "Enter custom path: " INSTALL_DIR

    if [[ -z "$INSTALL_DIR" ]]; then
      echo "Error: Empty path provided. Exiting."
      exit 1
    fi

    if [[ "$INSTALL_DIR" =~ [[:cntrl:]] ]] || [[ "$INSTALL_DIR" == *".."* ]]; then
      echo "Error: Invalid path (contains control characters or path traversal). Exiting."
      exit 1
    fi

    case "$INSTALL_DIR" in
      "$HOME"/*)
        ;;
      ./*)
        ;;
      [^/]*)
        ;;
      *)
        echo "Warning: Installing to system path '$INSTALL_DIR'."
        read -rp "Are you sure? [y/N]: " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
          echo "Aborted."
          exit 1
        fi
        ;;
    esac
    ;;
  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac

echo ""
echo "Installing to: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/skill.json" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/prompt.md" "$INSTALL_DIR/"

echo "Installed successfully!"
echo ""

if [ -f "$INSTALL_DIR/skill.json" ] && [ -f "$INSTALL_DIR/prompt.md" ]; then
  echo "Installed files verified at $INSTALL_DIR"
else
  echo "WARNING: Installation may be incomplete - missing files in $INSTALL_DIR"
fi

echo ""
echo "Next steps:"
echo "1. Restart Claude Code (if running)"
echo "2. Verify skill is available: /specops"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
