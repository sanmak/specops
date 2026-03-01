#!/bin/bash

# SpecOps Universal Setup Script
# Detects installed AI coding tools and installs SpecOps for selected platforms

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "SpecOps Setup"
echo "===================="
echo ""

# Detect available platforms
detect_platforms() {
  DETECTED=""

  # Claude Code
  if [ -d "$HOME/.claude" ] || command -v claude &>/dev/null; then
    DETECTED="$DETECTED claude"
  fi

  # Cursor
  if [ -d ".cursor" ] || command -v cursor &>/dev/null || \
     [ -d "/Applications/Cursor.app" ] || [ -d "$HOME/Applications/Cursor.app" ]; then
    DETECTED="$DETECTED cursor"
  fi

  # OpenAI Codex
  if command -v codex &>/dev/null; then
    DETECTED="$DETECTED codex"
  fi

  # GitHub Copilot
  if command -v gh &>/dev/null && gh copilot --help &>/dev/null 2>&1 || \
     [ -f ".github/copilot-instructions.md" ] || [ -d ".github/instructions" ]; then
    DETECTED="$DETECTED copilot"
  fi

  echo "$DETECTED"
}

echo "Detecting installed AI coding tools..."
DETECTED=$(detect_platforms)

if [ -z "$DETECTED" ]; then
  echo "No AI coding tools detected automatically."
  echo ""
fi

echo ""
echo "Which platform(s) would you like to install SpecOps for?"
echo ""
echo "1) Claude Code"
echo "2) Cursor"
echo "3) OpenAI Codex"
echo "4) GitHub Copilot"
echo "5) All detected platforms"
echo "6) All platforms"
echo ""

# Show detected platforms
if [ -n "$DETECTED" ]; then
  echo "Detected:$DETECTED"
  echo ""
fi

read -rp "Select option(s) [comma-separated, e.g. 1,2]: " platform_choice

SELECTED=""
IFS=',' read -ra CHOICES <<< "$platform_choice"
for choice in "${CHOICES[@]}"; do
  choice=$(echo "$choice" | tr -d ' ')
  case $choice in
    1) SELECTED="$SELECTED claude" ;;
    2) SELECTED="$SELECTED cursor" ;;
    3) SELECTED="$SELECTED codex" ;;
    4) SELECTED="$SELECTED copilot" ;;
    5) SELECTED="$DETECTED" ;;
    6) SELECTED=" claude cursor codex copilot" ;;
    *)
      echo "Invalid option: $choice"
      exit 1
      ;;
  esac
done

if [ -z "$SELECTED" ]; then
  echo "No platforms selected. Exiting."
  exit 1
fi

echo ""

# Install for each selected platform
for platform in $SELECTED; do
  platform=$(echo "$platform" | tr -d ' ')
  installer="$SCRIPT_DIR/platforms/$platform/install.sh"

  if [ -f "$installer" ]; then
    echo "----------------------------------------"
    echo "Installing for: $platform"
    echo "----------------------------------------"
    bash "$installer"
    echo ""
  else
    echo "WARNING: No installer found for $platform at $installer"
  fi
done

# Setup project configuration
echo "----------------------------------------"
read -rp "Would you like to create a .specops.json config in the current directory? [y/N]: " config_choice

if [[ $config_choice =~ ^[Yy]$ ]]; then
  if [ -f ".specops.json" ]; then
    echo ".specops.json already exists. Skipping."
  else
    echo ""
    echo "Select a configuration template:"
    echo "1) Minimal (just specsDir)"
    echo "2) Standard (team conventions, review required)"
    echo "3) Full (all options configured)"
    read -rp "Select option [1-3]: " config_template

    case $config_template in
      1)
        cp "$SCRIPT_DIR/examples/.specops.minimal.json" .specops.json
        ;;
      2)
        cp "$SCRIPT_DIR/examples/.specops.json" .specops.json
        ;;
      3)
        cp "$SCRIPT_DIR/examples/.specops.full.json" .specops.json
        ;;
      *)
        echo "Invalid option. Skipping config creation."
        ;;
    esac

    if [ -f ".specops.json" ]; then
      echo "Created .specops.json"
      echo "Edit .specops.json to customize for your project"
    fi
  fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. See platform-specific README for usage instructions:"
for platform in $SELECTED; do
  platform=$(echo "$platform" | tr -d ' ')
  echo "   - platforms/$platform/README.md"
done
echo "2. Customize .specops.json for your team"
echo "3. Read README.md for full documentation"
echo ""
echo "For team sharing:"
echo "- Share this repository URL: https://github.com/sanmak/specops.git"
echo "- Team members run: bash setup.sh"
echo ""
