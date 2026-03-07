#!/bin/bash

# SpecOps Remote Installer
# Install SpecOps without cloning the repository.
#
# Interactive (preserves stdin for prompts):
#   bash <(curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh)
#
# Non-interactive:
#   curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform claude --scope user
#   curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform cursor
#   curl -fsSL https://raw.githubusercontent.com/sanmak/specops/main/scripts/remote-install.sh | bash -s -- --platform all

set -euo pipefail

SPECOPS_REPO="sanmak/specops"
SPECOPS_VERSION="${SPECOPS_VERSION:-main}"

# --- Argument parsing ---
PLATFORM=""
SCOPE=""
CONFIG=""
FORCE=false

usage() {
  echo "Usage: remote-install.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --platform <name>   Platform to install: claude, cursor, codex, copilot, all"
  echo "  --scope <scope>     Claude Code only: user or project (default: user)"
  echo "  --version <ref>     Git ref to install from (default: main)"
  echo "  --config <template> Create .specops.json: minimal, standard, full"
  echo "  --force             Overwrite existing files without prompting"
  echo "  --help              Show this help message"
  echo ""
  echo "Interactive mode:"
  echo "  bash <(curl -fsSL https://raw.githubusercontent.com/${SPECOPS_REPO}/main/scripts/remote-install.sh)"
  echo ""
  echo "Non-interactive examples:"
  echo "  ... | bash -s -- --platform claude --scope user"
  echo "  ... | bash -s -- --platform cursor"
  echo "  ... | bash -s -- --platform all --config minimal"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    --scope)    SCOPE="$2"; shift 2 ;;
    --version)  SPECOPS_VERSION="$2"; shift 2 ;;
    --config)   CONFIG="$2"; shift 2 ;;
    --force)    FORCE=true; shift ;;
    --help)     usage; exit 0 ;;
    *)          echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

SPECOPS_BASE_URL="https://raw.githubusercontent.com/${SPECOPS_REPO}/${SPECOPS_VERSION}"

# --- Prerequisites ---
DOWNLOAD_CMD=""
if command -v curl &>/dev/null; then
  DOWNLOAD_CMD="curl"
elif command -v wget &>/dev/null; then
  DOWNLOAD_CMD="wget"
else
  echo "Error: curl or wget is required."
  exit 1
fi

# --- Helpers ---
download_file() {
  local url="$1"
  local dest="$2"
  local dest_dir
  dest_dir="$(dirname "$dest")"
  mkdir -p "$dest_dir"

  local tmp_file
  tmp_file="$(mktemp)"

  if [[ "$DOWNLOAD_CMD" == "curl" ]]; then
    if ! curl -fsSL "$url" -o "$tmp_file"; then
      rm -f "$tmp_file"
      echo "Error: Failed to download $url"
      exit 1
    fi
  else
    if ! wget -qO "$tmp_file" "$url"; then
      rm -f "$tmp_file"
      echo "Error: Failed to download $url"
      exit 1
    fi
  fi

  if [[ ! -s "$tmp_file" ]]; then
    rm -f "$tmp_file"
    echo "Error: Downloaded file is empty: $url"
    exit 1
  fi

  mv "$tmp_file" "$dest"
}

is_interactive() {
  [[ -t 0 ]]
}

# --- Banner ---
echo "SpecOps Remote Installer"
echo "========================"
echo "Version: ${SPECOPS_VERSION}"
echo "Source:  https://github.com/${SPECOPS_REPO}"
echo ""

# --- Platform detection ---
detect_platforms() {
  local detected=""

  # Claude Code
  if [ -d "$HOME/.claude" ] || command -v claude &>/dev/null; then
    detected="$detected claude"
  fi

  # Cursor
  if [ -d ".cursor" ] || command -v cursor &>/dev/null || \
     [ -d "/Applications/Cursor.app" ] || [ -d "$HOME/Applications/Cursor.app" ]; then
    detected="$detected cursor"
  fi

  # OpenAI Codex
  if command -v codex &>/dev/null; then
    detected="$detected codex"
  fi

  # GitHub Copilot
  if command -v gh &>/dev/null && gh copilot --help &>/dev/null 2>&1 || \
     [ -f ".github/copilot-instructions.md" ] || [ -d ".github/instructions" ]; then
    detected="$detected copilot"
  fi

  echo "$detected"
}

# --- Platform selection ---
SELECTED=""

if [[ -n "$PLATFORM" ]]; then
  # Non-interactive: use --platform flag
  case "$PLATFORM" in
    claude|cursor|codex|copilot) SELECTED="$PLATFORM" ;;
    all) SELECTED="claude cursor codex copilot" ;;
    *) echo "Error: Invalid platform '$PLATFORM'. Use: claude, cursor, codex, copilot, all"; exit 1 ;;
  esac
elif is_interactive; then
  # Interactive: detect and prompt
  echo "Detecting installed AI coding tools..."
  DETECTED=$(detect_platforms)

  if [ -n "$DETECTED" ]; then
    echo "Detected:$DETECTED"
  else
    echo "No AI coding tools detected automatically."
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
  read -rp "Select option(s) [comma-separated, e.g. 1,2]: " platform_choice

  IFS=',' read -ra CHOICES <<< "$platform_choice"
  for choice in "${CHOICES[@]}"; do
    choice=$(echo "$choice" | tr -d ' ')
    case $choice in
      1) SELECTED="$SELECTED claude" ;;
      2) SELECTED="$SELECTED cursor" ;;
      3) SELECTED="$SELECTED codex" ;;
      4) SELECTED="$SELECTED copilot" ;;
      5) SELECTED="$DETECTED" ;;
      6) SELECTED="claude cursor codex copilot" ;;
      *) echo "Invalid option: $choice"; exit 1 ;;
    esac
  done
else
  # Piped mode without --platform flag
  echo "Error: --platform flag is required in non-interactive mode."
  echo ""
  usage
  exit 1
fi

if [[ -z "$SELECTED" ]]; then
  echo "No platforms selected. Exiting."
  exit 1
fi

echo ""

# --- Platform installers ---

install_claude() {
  echo "----------------------------------------"
  echo "Installing for: Claude Code"
  echo "----------------------------------------"

  local install_dir=""

  if [[ -n "$SCOPE" ]]; then
    case "$SCOPE" in
      user)    install_dir="$HOME/.claude/skills/specops" ;;
      project) install_dir="./.claude/skills/specops" ;;
      *) echo "Error: Invalid scope '$SCOPE'. Use: user, project"; exit 1 ;;
    esac
  elif is_interactive; then
    echo "How would you like to install SpecOps?"
    echo "1) User installation (~/.claude/skills/specops)"
    echo "2) Project installation (./.claude/skills/specops)"
    read -rp "Select option [1-2]: " choice

    case $choice in
      1) install_dir="$HOME/.claude/skills/specops" ;;
      2) install_dir="./.claude/skills/specops" ;;
      *) echo "Invalid option. Exiting."; exit 1 ;;
    esac
  else
    # Default to user-level in non-interactive mode
    install_dir="$HOME/.claude/skills/specops"
  fi

  echo "Installing to: $install_dir"
  mkdir -p "$install_dir"
  download_file "${SPECOPS_BASE_URL}/platforms/claude/SKILL.md" "$install_dir/SKILL.md"

  # Install init sub-skill (/specops:init)
  mkdir -p "$install_dir/init"
  download_file "${SPECOPS_BASE_URL}/platforms/claude/init/SKILL.md" "$install_dir/init/SKILL.md"

  if [ -f "$install_dir/SKILL.md" ] && [ -f "$install_dir/init/SKILL.md" ]; then
    echo "Installed files verified at $install_dir"
  else
    echo "WARNING: Installation may be incomplete — missing files in $install_dir"
  fi
  echo ""
}

install_cursor() {
  echo "----------------------------------------"
  echo "Installing for: Cursor"
  echo "----------------------------------------"

  local rules_dir=".cursor/rules"
  echo "Installing to: $rules_dir/specops.mdc"
  download_file "${SPECOPS_BASE_URL}/platforms/cursor/specops.mdc" "$rules_dir/specops.mdc"
  echo "Installed successfully!"
  echo ""
}

install_codex() {
  echo "----------------------------------------"
  echo "Installing for: OpenAI Codex"
  echo "----------------------------------------"

  local skill_dir=".codex/skills/specops"
  echo "Installing to: $skill_dir/SKILL.md"
  download_file "${SPECOPS_BASE_URL}/platforms/codex/SKILL.md" "$skill_dir/SKILL.md"
  echo "Installed successfully!"
  echo ""
}

install_copilot() {
  echo "----------------------------------------"
  echo "Installing for: GitHub Copilot"
  echo "----------------------------------------"

  local instructions_dir=".github/instructions"
  echo "Installing to: $instructions_dir/specops.instructions.md"
  download_file "${SPECOPS_BASE_URL}/platforms/copilot/specops.instructions.md" "$instructions_dir/specops.instructions.md"
  echo "Installed successfully!"
  echo ""
}

# --- Install selected platforms ---
for platform in $SELECTED; do
  platform=$(echo "$platform" | tr -d ' ')
  case "$platform" in
    claude)  install_claude ;;
    cursor)  install_cursor ;;
    codex)   install_codex ;;
    copilot) install_copilot ;;
  esac
done

# --- Optional config ---
install_config() {
  local template="$1"
  local source_file=""

  case "$template" in
    minimal)  source_file="examples/.specops.minimal.json" ;;
    standard) source_file="examples/.specops.json" ;;
    full)     source_file="examples/.specops.full.json" ;;
    *) echo "Error: Invalid config template '$template'. Use: minimal, standard, full"; exit 1 ;;
  esac

  if [ -f ".specops.json" ] && [[ "$FORCE" != true ]]; then
    echo ".specops.json already exists. Skipping."
  else
    download_file "${SPECOPS_BASE_URL}/${source_file}" ".specops.json"
    echo "Created .specops.json ($template template)"
    echo "Edit .specops.json to customize for your project."
  fi
}

if [[ -n "$CONFIG" ]]; then
  install_config "$CONFIG"
elif is_interactive; then
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
        1) install_config "minimal" ;;
        2) install_config "standard" ;;
        3) install_config "full" ;;
        *) echo "Invalid option. Skipping config creation." ;;
      esac
    fi
  fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create or edit .specops.json to customize for your project"
echo "2. Use SpecOps with your AI coding assistant:"
echo "   - Claude Code: /specops <your feature> (also: /specops:init)"
echo "   - Cursor/Codex/Copilot: 'Use specops to <your feature>'"
echo "3. Full docs: https://github.com/${SPECOPS_REPO}"
echo ""
