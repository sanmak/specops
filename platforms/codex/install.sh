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

# Check for .gitignore conflicts on project-level installs
if [[ "$INSTALL_DIR" == "." ]] && [[ -f ".gitignore" ]]; then
  if grep -q -E "^\.codex/?$|^\.codex/\*" ".gitignore"; then
    echo ""
    echo "⚠️  WARNING: Project .gitignore blocks tracking of .codex/"
    echo ""
    echo "Your .gitignore excludes .codex/ or .codex/*, which means the installed"
    echo "SKILL.md will not be tracked by git. Team members cloning this repo won't"
    echo "have SpecOps available unless they install it individually."
    echo ""
    echo "Two options to fix this:"
    echo ""
    echo "Option 1 (Recommended): Use user-level installation instead"
    echo "  → Installs to ~/.codex/skills/specops/SKILL.md (not project-specific)"
    echo "  → Unaffected by .gitignore"
    echo ""
    echo "Option 2: Selectively un-ignore .codex/skills/ in your .gitignore"
    echo "  → Add this line to .gitignore:  !.codex/skills/"
    echo "  → Tracks SpecOps but keeps other .codex/ config local"
    echo ""
    read -rp "Proceed with project-level install anyway? [y/N]: " proceed
    if [[ ! $proceed =~ ^[Yy]$ ]]; then
      echo "Aborted. Consider using user-level installation instead."
      exit 1
    fi
  fi
fi

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

# Update .specops.json with version metadata if it exists
if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
  SPECOPS_VER="$(grep '^version:' "$SCRIPT_DIR/SKILL.md" | head -1 | sed 's/version: *"//;s/"//')"
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

echo ""
echo "Next steps:"
echo "1. Run Codex in your project"
echo "2. Ask it to 'use specops' or 'create a spec' for your feature"
echo "3. Create a .specops.json in your project (see examples/)"
echo ""
