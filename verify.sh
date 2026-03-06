#!/bin/bash

# SpecOps Verification Script
# Checks that all required files are present and valid

set -e

echo "SpecOps Verification"
echo "==========================="
echo ""

ERRORS=0
WARNINGS=0

# Check function
check_file() {
  if [ -f "$1" ]; then
    echo "  OK: $1"
  else
    echo "  MISSING: $1"
    ERRORS=$((ERRORS + 1))
  fi
}

check_dir() {
  if [ -d "$1" ]; then
    echo "  OK: $1/"
  else
    echo "  MISSING: $1/"
    ERRORS=$((ERRORS + 1))
  fi
}

# Check core files
echo "Core Files:"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "docs/TEAM_GUIDE.md"
check_file "CHANGELOG.md"
check_file "docs/REFERENCE.md"
check_file "docs/STRUCTURE.md"
check_file "LICENSE"
check_file ".gitignore"
check_file "schema.json"
check_file "setup.sh"
check_file "verify.sh"
check_file "scripts/bump-version.sh"
check_file "scripts/remote-install.sh"
check_file "scripts/install-hooks.sh"
echo ""

# Check git hooks
echo "Git Hooks:"
check_dir "hooks"
check_file "hooks/pre-commit"
check_file "hooks/pre-push"
echo ""

# Check core modules
echo "Core Modules:"
check_dir "core"
check_file "core/workflow.md"
check_file "core/safety.md"
check_file "core/simplicity.md"
check_file "core/data-handling.md"
check_file "core/verticals.md"
check_file "core/custom-templates.md"
check_file "core/config-handling.md"
check_file "core/error-handling.md"
check_file "core/tool-abstraction.md"
check_dir "core/templates"
check_file "core/templates/feature-requirements.md"
check_file "core/templates/bugfix.md"
check_file "core/templates/refactor.md"
check_file "core/templates/design.md"
check_file "core/templates/tasks.md"
check_file "core/templates/implementation.md"
echo ""

# Check build system
echo "Build System:"
check_dir "generator"
check_file "generator/generate.py"
check_file "generator/validate.py"
check_dir "generator/templates"
check_file "generator/templates/claude.j2"
check_file "generator/templates/cursor.j2"
check_file "generator/templates/codex.j2"
check_file "generator/templates/copilot.j2"
echo ""

# Check platform adapters
echo "Platform Adapters:"
for platform in claude cursor codex copilot; do
  check_dir "platforms/$platform"
  check_file "platforms/$platform/platform.json"
  check_file "platforms/$platform/install.sh"
  check_file "platforms/$platform/README.md"
done
check_file "platforms/claude/SKILL.md"
check_file "platforms/cursor/specops.mdc"
check_file "platforms/codex/SKILL.md"
check_file "platforms/copilot/specops.instructions.md"
echo ""

# Check legacy skills directory (backward compat)
echo "Legacy Skills Directory:"
check_dir "skills"
check_dir "skills/specops"
check_file "skills/specops/SKILL.md"
echo ""

# Check examples directory
echo "Examples Directory:"
check_dir "examples"
check_file "examples/.specops.json"
check_file "examples/.specops.minimal.json"
check_file "examples/.specops.full.json"
check_dir "examples/specs"
check_dir "examples/specs/feature-user-authentication"
check_file "examples/specs/feature-user-authentication/requirements.md"
check_file "examples/specs/feature-user-authentication/design.md"
check_file "examples/specs/feature-user-authentication/tasks.md"
check_file "examples/specs/feature-user-authentication/implementation.md"
check_dir "examples/specs/feature-dark-mode-toggle"
check_dir "examples/specs/feature-k8s-autoscaling"
check_dir "examples/specs/feature-user-activity-pipeline"
check_dir "examples/specs/feature-date-utils-library"
echo ""

# Check example templates
echo "Example Templates:"
check_dir "examples/templates"
check_file "examples/templates/infra-requirements.md"
check_file "examples/templates/infra-design.md"
check_file "examples/templates/data-pipeline-requirements.md"
check_file "examples/templates/data-pipeline-design.md"
check_file "examples/templates/library-requirements.md"
check_file "examples/templates/library-design.md"
echo ""

# Validate JSON files
echo "JSON Validation:"
json_files=(
  schema.json
  "examples/.specops.json"
  "examples/.specops.minimal.json"
  "examples/.specops.full.json"
  platforms/claude/platform.json
  platforms/cursor/platform.json
  platforms/codex/platform.json
  platforms/copilot/platform.json
)
for json_file in "${json_files[@]}"; do
  if [ -f "$json_file" ]; then
    if python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
      echo "  OK: $json_file (valid JSON)"
    else
      echo "  FAIL: $json_file (invalid JSON)"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done
echo ""

# Check file permissions
echo "File Permissions:"
for script in setup.sh verify.sh scripts/bump-version.sh scripts/remote-install.sh platforms/claude/install.sh platforms/cursor/install.sh platforms/codex/install.sh platforms/copilot/install.sh; do
  if [ -f "$script" ]; then
    if [ -x "$script" ]; then
      echo "  OK: $script is executable"
    else
      echo "  WARN: $script is not executable (run: chmod +x $script)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done
echo ""

# Run build validation if generated files exist
echo "Build Validation:"
if [ -f "platforms/claude/SKILL.md" ] && [ -f "platforms/cursor/specops.mdc" ] && [ -f "platforms/codex/SKILL.md" ] && [ -f "platforms/copilot/specops.instructions.md" ]; then
  if python3 generator/validate.py 2>/dev/null; then
    echo "  OK: All platform outputs validated"
  else
    echo "  FAIL: Platform output validation failed"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "  SKIP: Generated platform files not found. Run: python3 generator/generate.py --all"
  WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "==========================="
echo "Summary:"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo "All checks passed!"
  echo ""
  echo "Next steps:"
  echo "1. Run ./setup.sh to install"
  echo "2. Read QUICKSTART.md to get started"
  echo "3. Review examples/ for reference"
  exit 0
else
  echo "Verification failed with $ERRORS error(s)"
  echo ""
  echo "Please ensure all files are present and try again."
  exit 1
fi
