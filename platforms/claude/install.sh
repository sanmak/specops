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

# Check for .gitignore conflicts on project-level installs
if [[ "$INSTALL_DIR" == "./.claude/skills/specops" ]] && [[ -f ".gitignore" ]]; then
  if grep -q -E "^\.claude/?$|^\.claude/\*" ".gitignore"; then
    echo ""
    echo "⚠️  WARNING: Project .gitignore blocks tracking of .claude/"
    echo ""
    echo "Your .gitignore excludes .claude/ or .claude/*, which means the installed"
    echo "SKILL.md will not be tracked by git. Team members cloning this repo won't"
    echo "have SpecOps available unless they install it individually."
    echo ""
    echo "Two options to fix this:"
    echo ""
    echo "Option 1 (Recommended): Use user-level installation instead"
    echo "  → Installs to ~/.claude/skills/specops (not project-specific)"
    echo "  → Unaffected by .gitignore"
    echo ""
    echo "Option 2: Selectively un-ignore .claude/skills/ in your .gitignore"
    echo "  → Add this line to .gitignore:  !.claude/skills/"
    echo "  → Tracks SpecOps but keeps other .claude/ config local"
    echo ""
    read -rp "Proceed with project-level install anyway? [y/N]: " proceed
    if [[ ! $proceed =~ ^[Yy]$ ]]; then
      echo "Aborted. Consider running: bash setup.sh  (and choose user installation)"
      exit 1
    fi
  fi
fi

echo ""
echo "Installing to: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$INSTALL_DIR/"

echo "Installed successfully!"
echo ""

if [ -f "$INSTALL_DIR/SKILL.md" ]; then
  echo "Installed files verified at $INSTALL_DIR"
else
  echo "WARNING: Installation may be incomplete - missing files in $INSTALL_DIR"
fi

# Update .specops.json with version metadata if it exists
if [ -f ".specops.json" ]; then
  SPECOPS_VER="$(grep '^version:' "$SCRIPT_DIR/SKILL.md" | head -1 | sed 's/version: *"//;s/"//')"
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

echo ""
echo "Next steps:"
echo "1. Restart Claude Code (if running)"
echo "2. Verify skill is available: /specops"
echo "3. Initialize config: /specops init"
echo ""
