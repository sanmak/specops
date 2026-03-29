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
NO_VERIFY=false

usage() {
  echo "Usage: remote-install.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --platform <name>   Platform to install: claude, cursor, codex, copilot, antigravity, all"
  echo "  --scope <scope>     Claude Code only: user or project (default: user)"
  echo "  --version <ref>     Git ref to install from (default: main)"
  echo "  --config <template> Create .specops.json: minimal, standard, full"
  echo "  --no-verify         Skip checksum verification (not recommended)"
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
    --platform) [[ $# -ge 2 ]] || { echo "Error: $1 requires a value"; usage; exit 1; }; PLATFORM="$2"; shift 2 ;;
    --scope)    [[ $# -ge 2 ]] || { echo "Error: $1 requires a value"; usage; exit 1; }; SCOPE="$2"; shift 2 ;;
    --version)  [[ $# -ge 2 ]] || { echo "Error: $1 requires a value"; usage; exit 1; }; SPECOPS_VERSION="$2"; shift 2 ;;
    --config)   [[ $# -ge 2 ]] || { echo "Error: $1 requires a value"; usage; exit 1; }; CONFIG="$2"; shift 2 ;;
    --no-verify) NO_VERIFY=true; shift ;;
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
      echo "Error: Failed to download $url" >&2
      return 1
    fi
  else
    if ! wget -qO "$tmp_file" "$url"; then
      rm -f "$tmp_file"
      echo "Error: Failed to download $url" >&2
      return 1
    fi
  fi

  if [[ ! -s "$tmp_file" ]]; then
    rm -f "$tmp_file"
    echo "Error: Downloaded file is empty: $url" >&2
    return 1
  fi

  mv "$tmp_file" "$dest"
}

is_interactive() {
  [[ -t 0 ]]
}

# --- Checksum verification ---
HASH_CMD=()
CHECKSUMS_FILE=""

detect_hash_cmd() {
  if command -v sha256sum &>/dev/null; then
    HASH_CMD=(sha256sum)
  elif command -v shasum &>/dev/null; then
    HASH_CMD=(shasum -a 256)
  else
    echo "Warning: Neither sha256sum nor shasum found. Cannot verify checksums."
    return 1
  fi
}

fetch_checksums() {
  CHECKSUMS_FILE="$(mktemp)"
  local checksums_url="${SPECOPS_BASE_URL}/CHECKSUMS.sha256"

  if [[ "$DOWNLOAD_CMD" == "curl" ]]; then
    if ! curl -fsSL "$checksums_url" -o "$CHECKSUMS_FILE" 2>/dev/null; then
      rm -f "$CHECKSUMS_FILE"
      CHECKSUMS_FILE=""
      return 1
    fi
  else
    if ! wget -qO "$CHECKSUMS_FILE" "$checksums_url" 2>/dev/null; then
      rm -f "$CHECKSUMS_FILE"
      CHECKSUMS_FILE=""
      return 1
    fi
  fi

  if [[ ! -s "$CHECKSUMS_FILE" ]]; then
    rm -f "$CHECKSUMS_FILE"
    CHECKSUMS_FILE=""
    return 1
  fi
}

# verify_file <local_file> <repo_path>
# Verifies the SHA-256 hash of a local file against the CHECKSUMS.sha256 entry
# for the given repo path. Returns 0 on match or missing entry (with warning),
# 1 on mismatch (file is removed).
verify_file() {
  local local_file="$1"
  local repo_path="$2"

  if [[ -z "$CHECKSUMS_FILE" ]] || [[ ${#HASH_CMD[@]} -eq 0 ]]; then
    return 0  # no checksums available, skip silently
  fi

  local expected_hash
  expected_hash="$(grep -E "  ${repo_path}$" "$CHECKSUMS_FILE" | head -1 | awk '{print $1}' || true)"

  if [[ -z "$expected_hash" ]]; then
    echo "ERROR: No checksum entry for ${repo_path} in CHECKSUMS.sha256"
    echo "Cannot verify file integrity — aborting."
    rm -f "$local_file"
    return 1
  fi

  local actual_hash
  actual_hash="$("${HASH_CMD[@]}" "$local_file" | awk '{print $1}')"

  if [[ "$actual_hash" != "$expected_hash" ]]; then
    echo ""
    echo "ERROR: Checksum verification failed for ${repo_path}"
    echo "  Expected: ${expected_hash}"
    echo "  Actual:   ${actual_hash}"
    echo ""
    echo "The downloaded file may have been tampered with or corrupted."
    echo "Removing downloaded file and aborting."
    rm -f "$local_file"
    return 1
  fi

  echo "  Verified: ${repo_path} (SHA-256 OK)"
  return 0
}

cleanup_checksums() {
  if [[ -n "$CHECKSUMS_FILE" ]] && [[ -f "$CHECKSUMS_FILE" ]]; then
    rm -f "$CHECKSUMS_FILE"
  fi
}
trap cleanup_checksums EXIT

# --- Banner ---
echo "SpecOps Remote Installer"
echo "========================"
echo "Version: ${SPECOPS_VERSION}"
echo "Source:  https://github.com/${SPECOPS_REPO}"
echo ""

# --- Checksum setup ---
if [[ "$NO_VERIFY" == true ]]; then
  echo "Warning: Checksum verification disabled (--no-verify). File integrity will not be checked."
  echo ""
elif detect_hash_cmd; then
  if fetch_checksums; then
    echo "Checksums loaded for integrity verification."
  else
    echo "Warning: Could not fetch CHECKSUMS.sha256 from ${SPECOPS_BASE_URL}/CHECKSUMS.sha256"
    if is_interactive; then
      read -rp "Continue without checksum verification? [y/N]: " verify_choice
      if [[ ! $verify_choice =~ ^[Yy]$ ]]; then
        echo "Aborting. Use a release tag (--version v1.3.0) or verify files manually."
        exit 1
      fi
    else
      echo "Aborting: Cannot verify file integrity in non-interactive mode."
      echo "Use --no-verify to skip, or use a release tag (--version v1.3.0)."
      exit 1
    fi
  fi
  echo ""
else
  echo "Warning: No SHA-256 hash command available (sha256sum or shasum)."
  if is_interactive; then
    read -rp "Continue without checksum verification? [y/N]: " hash_choice
    if [[ ! $hash_choice =~ ^[Yy]$ ]]; then
      echo "Aborting. Install sha256sum or shasum and try again."
      exit 1
    fi
  else
    echo "Aborting: Cannot verify file integrity in non-interactive mode (no hash command)."
    echo "Use --no-verify to skip, or install sha256sum/shasum."
    exit 1
  fi
  echo ""
fi

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

  # Google Antigravity
  if command -v antigravity &>/dev/null || \
     [ -d "/Applications/Antigravity.app" ] || [ -d "$HOME/Applications/Antigravity.app" ] || \
     [ -d ".agents" ]; then
    detected="$detected antigravity"
  fi

  echo "$detected"
}

# --- Platform selection ---
SELECTED=""

if [[ -n "$PLATFORM" ]]; then
  # Non-interactive: use --platform flag
  case "$PLATFORM" in
    claude|cursor|codex|copilot|antigravity) SELECTED="$PLATFORM" ;;
    all) SELECTED="claude cursor codex copilot antigravity" ;;
    *) echo "Error: Invalid platform '$PLATFORM'. Use: claude, cursor, codex, copilot, antigravity, all"; exit 1 ;;
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
  echo "5) Google Antigravity"
  echo "6) All detected platforms"
  echo "7) All platforms"
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
      5) SELECTED="$SELECTED antigravity" ;;
      6) SELECTED="$DETECTED" ;;
      7) SELECTED="claude cursor codex copilot antigravity" ;;
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
  if ! verify_file "$install_dir/SKILL.md" "platforms/claude/SKILL.md"; then
    exit 1
  fi

  # Download mode files for context-aware dispatch
  local mode_names="audit feedback from-plan init interview map memory pipeline spec steering update version view"
  mkdir -p "$install_dir/modes"
  local mode_count=0
  for mode in $mode_names; do
    # Attempt download, continue on failure (download_file returns 1 on error, caught by || true)
    download_file "${SPECOPS_BASE_URL}/platforms/claude/modes/${mode}.md" "$install_dir/modes/${mode}.md" 2>/dev/null || true
    [ -f "$install_dir/modes/${mode}.md" ] && mode_count=$((mode_count + 1))
  done
  if [ "$mode_count" -gt 0 ]; then
    echo "  Installed dispatcher + ${mode_count} mode files"
  fi

  if [ -f "$install_dir/SKILL.md" ]; then
    echo "Installed files verified at $install_dir"
  else
    echo "WARNING: Installation may be incomplete — missing files in $install_dir"
  fi

  # Install PostToolUse ExitPlanMode hook and PreToolUse Write/Edit guard
  if command -v python3 >/dev/null 2>&1; then
    local settings_file
    case "$install_dir" in
      "$HOME"/.claude/skills/specops)
        settings_file="$HOME/.claude/settings.json"
        ;;
      ./.claude/skills/specops)
        settings_file="./.claude/settings.json"
        ;;
      *)
        settings_file="$HOME/.claude/settings.json"
        ;;
    esac

    SETTINGS_FILE="$settings_file" python3 - <<'HOOK_PY'
import json
import os

settings_file = os.environ["SETTINGS_FILE"]

# Load existing settings or create empty dict
if os.path.isfile(settings_file):
    try:
        with open(settings_file, "r") as f:
            settings = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(
            "WARNING: Could not parse {} ({}); skipping hook installation.".format(
                settings_file, e
            )
        )
        exit(0)
else:
    settings = {}

# Ensure hooks structure exists
if not isinstance(settings.get("hooks"), dict):
    settings["hooks"] = {}
if not isinstance(settings["hooks"].get("PostToolUse"), list):
    settings["hooks"]["PostToolUse"] = []
if not isinstance(settings["hooks"].get("PreToolUse"), list):
    settings["hooks"]["PreToolUse"] = []

# --- PostToolUse: marker-creating ExitPlanMode hook ---
NEW_POST_CMD = (
    'if [ -f .specops.json ]; then '
    'SPECS_DIR=$(python3 -c "import json; print(json.load(open(\'.specops.json\')).get(\'specsDir\',\'.specops\'))" 2>/dev/null || echo ".specops"); '
    'mkdir -p "$SPECS_DIR"; '
    'touch "$SPECS_DIR/.plan-pending-conversion"; '
    'echo "SPECOPS ENFORCEMENT: Plan approved. Marker set at $SPECS_DIR/.plan-pending-conversion. '
    'Write/Edit on non-spec files is blocked until /specops from-plan converts the plan into a structured spec."; '
    'fi # specops-hook'
)

# Find and replace existing specops-hook, or append
found_post = False
for entry in settings["hooks"]["PostToolUse"]:
    for hook in entry.get("hooks", []):
        if "specops-hook" in hook.get("command", ""):
            hook["command"] = NEW_POST_CMD
            found_post = True
            print("Updated ExitPlanMode hook (replaced advisory with marker-creating version)")
            break
    if found_post:
        break

if not found_post:
    settings["hooks"]["PostToolUse"].append({
        "matcher": "ExitPlanMode",
        "hooks": [{"type": "command", "command": NEW_POST_CMD}]
    })
    print("Installed ExitPlanMode hook (marker-creating version)")

# --- PreToolUse: Write/Edit guard ---
NEW_PRE_CMD = (
    "python3 -c \"\n"
    "import json, sys, os\n"
    "if not os.path.isfile('.specops.json'):\n"
    "    sys.exit(0)\n"
    "specs = json.load(open('.specops.json')).get('specsDir', '.specops')\n"
    "marker = os.path.join(os.path.abspath(specs), '.plan-pending-conversion')\n"
    "if not os.path.isfile(marker):\n"
    "    sys.exit(0)\n"
    "try:\n"
    "    data = json.load(sys.stdin)\n"
    "    fp = data.get('tool_input', {}).get('file_path', '')\n"
    "except Exception:\n"
    "    sys.exit(0)\n"
    "if not fp:\n"
    "    sys.exit(0)\n"
    "fp = os.path.normpath(os.path.abspath(fp))\n"
    "allowed = [os.path.abspath(specs), os.path.abspath('.claude/plans'), os.path.abspath('.claude/memory')]\n"
    "if any(os.path.commonpath([fp, a]) == a for a in allowed):\n"
    "    sys.exit(0)\n"
    "print('SPECOPS ENFORCEMENT: A plan was approved but not yet converted to a spec.', file=sys.stderr)\n"
    "print('Run /specops from-plan to convert the plan before implementing.', file=sys.stderr)\n"
    "print(f'Blocked write to: {fp}', file=sys.stderr)\n"
    "sys.exit(2)\n"
    "\" # specops-plan-guard"
)

# Check for existing specops-plan-guard marker (idempotent)
found_pre = False
for entry in settings["hooks"]["PreToolUse"]:
    for hook in entry.get("hooks", []):
        if "specops-plan-guard" in hook.get("command", ""):
            found_pre = True
            print("PreToolUse Write/Edit guard already installed (skipped)")
            break
    if found_pre:
        break

if not found_pre:
    settings["hooks"]["PreToolUse"].append({
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": NEW_PRE_CMD}]
    })
    print("Installed PreToolUse Write/Edit guard")

# Write back with indent=2
os.makedirs(os.path.dirname(settings_file) or ".", exist_ok=True)
with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print(f"Hooks installed in {settings_file}")
HOOK_PY
  else
    echo ""
    echo "WARNING: python3 not found — cannot install hooks automatically."
    echo "To install manually, add PostToolUse and PreToolUse hooks to your Claude Code settings."
  fi

  # Update .specops.json with version metadata if it exists
  if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
    SPECOPS_VER="$(grep '^version:' "$install_dir/SKILL.md" | head -1 | sed 's/version: *"//;s/"//')"
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
}

install_cursor() {
  echo "----------------------------------------"
  echo "Installing for: Cursor"
  echo "----------------------------------------"

  local rules_dir=".cursor/rules"
  echo "Installing to: $rules_dir/specops.mdc"
  download_file "${SPECOPS_BASE_URL}/platforms/cursor/specops.mdc" "$rules_dir/specops.mdc"
  if ! verify_file "$rules_dir/specops.mdc" "platforms/cursor/specops.mdc"; then
    exit 1
  fi
  echo "Installed successfully!"

  # Update .specops.json with version metadata if it exists
  if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
    SPECOPS_VER="$(grep '^version:' "$rules_dir/specops.mdc" | head -1 | sed 's/version: *"//;s/"//')"
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
}

install_codex() {
  echo "----------------------------------------"
  echo "Installing for: OpenAI Codex"
  echo "----------------------------------------"

  local skill_dir=".codex/skills/specops"
  echo "Installing to: $skill_dir/SKILL.md"
  download_file "${SPECOPS_BASE_URL}/platforms/codex/SKILL.md" "$skill_dir/SKILL.md"
  if ! verify_file "$skill_dir/SKILL.md" "platforms/codex/SKILL.md"; then
    exit 1
  fi
  echo "Installed successfully!"

  # Update .specops.json with version metadata if it exists
  if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
    SPECOPS_VER="$(grep '^version:' "$skill_dir/SKILL.md" | head -1 | sed 's/version: *"//;s/"//')"
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
}

install_copilot() {
  echo "----------------------------------------"
  echo "Installing for: GitHub Copilot"
  echo "----------------------------------------"

  local instructions_dir=".github/instructions"
  echo "Installing to: $instructions_dir/specops.instructions.md"
  download_file "${SPECOPS_BASE_URL}/platforms/copilot/specops.instructions.md" "$instructions_dir/specops.instructions.md"
  if ! verify_file "$instructions_dir/specops.instructions.md" "platforms/copilot/specops.instructions.md"; then
    exit 1
  fi
  echo "Installed successfully!"

  # Update .specops.json with version metadata if it exists
  if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
    SPECOPS_VER="$(grep '^version:' "$instructions_dir/specops.instructions.md" | head -1 | sed 's/version: *"//;s/"//')"
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
}

install_antigravity() {
  echo "----------------------------------------"
  echo "Installing for: Google Antigravity"
  echo "----------------------------------------"

  local rules_dir=".agents/rules"
  echo "Installing to: $rules_dir/specops.md"
  download_file "${SPECOPS_BASE_URL}/platforms/antigravity/specops.md" "$rules_dir/specops.md"
  if ! verify_file "$rules_dir/specops.md" "platforms/antigravity/specops.md"; then
    exit 1
  fi
  echo "Installed successfully!"

  # Update .specops.json with version metadata if it exists
  if [ -f ".specops.json" ] && command -v python3 >/dev/null 2>&1; then
    SPECOPS_VER="$(grep '<!-- specops-version:' "$rules_dir/specops.md" | head -1 | sed 's/.*specops-version: *"//;s/".*//')"
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
}

# --- Install selected platforms ---
for platform in $SELECTED; do
  platform=$(echo "$platform" | tr -d ' ')
  case "$platform" in
    claude)       install_claude ;;
    cursor)       install_cursor ;;
    codex)        install_codex ;;
    copilot)      install_copilot ;;
    antigravity)  install_antigravity ;;
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
echo "   - Claude Code: /specops <your feature> (also: /specops init)"
echo "   - Cursor/Codex/Copilot: 'Use specops to <your feature>'"
echo "3. Full docs: https://github.com/${SPECOPS_REPO}"
echo ""
