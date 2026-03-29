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

# Copy modes/ directory for context-aware dispatch
if [ -d "$SCRIPT_DIR/modes" ]; then
  mkdir -p "$INSTALL_DIR/modes"
  # shellcheck disable=SC2039
  if compgen -G "$SCRIPT_DIR/modes/*.md" > /dev/null 2>&1; then
    cp "$SCRIPT_DIR/modes/"*.md "$INSTALL_DIR/modes/"
  else
    echo "WARNING: modes/ directory exists but contains no .md files"
  fi
  echo "Installed dispatcher + $(find "$SCRIPT_DIR/modes" -name '*.md' 2>/dev/null | wc -l | tr -d ' ') mode files"
else
  echo "Installed SKILL.md (modes/ directory not found — monolithic mode)"
fi

echo "Installed successfully!"
echo ""

if [ -f "$INSTALL_DIR/SKILL.md" ]; then
  echo "Installed files verified at $INSTALL_DIR"
else
  echo "WARNING: Installation may be incomplete - missing files in $INSTALL_DIR"
fi

# Install PostToolUse ExitPlanMode hook and PreToolUse Write/Edit guard
install_hooks() {
  local settings_file

  # Determine settings file based on installation scope
  case "$INSTALL_DIR" in
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

  if ! command -v python3 >/dev/null 2>&1; then
    echo ""
    echo "WARNING: python3 not found — cannot install hooks automatically."
    echo "To install manually, add PostToolUse and PreToolUse hooks to $settings_file."
    return 0
  fi

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
}

install_hooks

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
echo "1. Restart Claude Code (if running)"
echo "2. Verify skill is available: /specops"
echo "3. Initialize config: /specops init"
echo ""
