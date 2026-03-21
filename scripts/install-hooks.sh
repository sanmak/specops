#!/bin/bash
# scripts/install-hooks.sh -- Install SpecOps git hooks
#
# Usage:
#   bash scripts/install-hooks.sh
#
# Symlinks hooks from hooks/ into .git/hooks/ so they track with the repo.
# Running this script again is safe (overwrites existing symlinks).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$ROOT_DIR/hooks"
GIT_HOOKS_DIR="$ROOT_DIR/.git/hooks"

if [ ! -d "$GIT_HOOKS_DIR" ]; then
  echo "Error: .git/hooks directory not found. Are you in a git repository?"
  exit 1
fi

if [ ! -d "$HOOKS_DIR" ]; then
  echo "Error: hooks/ directory not found at $HOOKS_DIR"
  exit 1
fi

echo "Installing SpecOps git hooks..."

for hook in pre-commit pre-push; do
  src="$HOOKS_DIR/$hook"
  dst="$GIT_HOOKS_DIR/$hook"

  if [ ! -f "$src" ]; then
    echo "  SKIP: $hook (not found in hooks/)"
    continue
  fi

  # Back up existing non-symlink hooks
  if [ -f "$dst" ] && [ ! -L "$dst" ]; then
    backup="$dst.backup.$(date +%Y%m%d%H%M%S)"
    echo "  Backing up existing $hook to $(basename "$backup")"
    mv "$dst" "$backup"
  fi

  ln -sf "$src" "$dst"
  chmod +x "$src"
  echo "  Installed: $hook -> hooks/$hook"
done

echo ""
echo "Done! Git hooks installed."
echo "  Pre-commit: JSON validation, ShellCheck, markdown lint, staleness detection"
echo "  Pre-push:   Platform validation, checksums, freshness, tests, markdown lint"
echo ""
echo "Bypass hooks when needed:"
echo "  git commit --no-verify"
echo "  git push --no-verify"
