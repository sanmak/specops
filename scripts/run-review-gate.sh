#!/usr/bin/env bash

# Baseline review gate checks for this repository.

# Note: set -e is intentionally omitted. This script runs multiple checks
# and tallies pass/fail results. Early exit would prevent subsequent checks.
set -u
set -o pipefail

FAILURES=0
WARNINGS=0

pass() {
  printf 'PASS: %s\n' "$1"
}

warn() {
  printf 'WARN: %s\n' "$1"
  WARNINGS=$((WARNINGS + 1))
}

fail() {
  printf 'FAIL: %s\n' "$1"
  FAILURES=$((FAILURES + 1))
}

run_check() {
  local name="$1"
  shift
  printf '\n== %s ==\n' "$name"
  if "$@"; then
    pass "$name"
  else
    fail "$name"
  fi
}

run_negative_rg_check() {
  local name="$1"
  local pattern="$2"
  shift 2

  if ! command -v rg >/dev/null 2>&1; then
    warn "$name skipped because rg is not installed"
    return
  fi

  printf '\n== %s ==\n' "$name"
  # Use --files-with-matches to avoid printing sensitive content to stdout.
  # Capture exit code explicitly (not via $? inside if/else which is always 0).
  local code
  rg --files-with-matches --hidden --color=never -P "$pattern" "$@" . >/dev/null 2>&1
  code=$?
  if [ "$code" -eq 0 ]; then
    fail "$name (potential matches found — run rg manually to inspect)"
  elif [ "$code" -eq 1 ]; then
    pass "$name"
  else
    fail "$name (rg execution error)"
  fi
}

printf 'Full Review Gate Baseline\n'
printf '=========================\n'

run_check "Repository integrity checks" bash verify.sh
run_check "Checksum verification" shasum -a 256 -c CHECKSUMS.sha256
run_check "Test suite" bash scripts/run-tests.sh

if command -v shellcheck >/dev/null 2>&1; then
  shell_targets=(
    setup.sh
    verify.sh
    scripts/*.sh
    platforms/*/install.sh
    hooks/pre-commit
    hooks/pre-push
  )
  run_check "Shell static analysis" shellcheck "${shell_targets[@]}"
else
  warn "Shell static analysis skipped because shellcheck is not installed"
fi

if command -v gitleaks >/dev/null 2>&1; then
  run_check "Secret scan (gitleaks)" gitleaks detect --no-banner --source .
else
  # Fallback heuristic scan for obvious hardcoded secrets.
  run_negative_rg_check \
    "Secret scan fallback (regex heuristics)" \
    '(AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[^\s]{8,})' \
    --glob '!.git/**' \
    --glob '!docs/**' \
    --glob '!**/*.md'
fi

# Heuristic scan for common PII-like literals.
run_negative_rg_check \
  "PII scan fallback (regex heuristics)" \
  '(\b\d{3}-\d{2}-\d{4}\b|\b(?:\d[ -]*?){13,16}\b)' \
  --glob '!.git/**' \
  --glob '!docs/**' \
  --glob '!**/*.md'

if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    run_check "Dependency vulnerability audit (npm)" npm audit --audit-level=high
  else
    warn "Dependency audit skipped because npm is not installed"
  fi
fi

if [ -f requirements.txt ] || [ -f requirements-dev.txt ]; then
  if command -v pip-audit >/dev/null 2>&1; then
    if [ -f requirements.txt ]; then
      run_check "Dependency vulnerability audit (pip requirements.txt)" pip-audit -r requirements.txt
    fi
    if [ -f requirements-dev.txt ]; then
      run_check "Dependency vulnerability audit (pip requirements-dev.txt)" pip-audit -r requirements-dev.txt
    fi
  else
    warn "Dependency audit skipped because pip-audit is not installed"
  fi
fi

if [ -f go.mod ]; then
  if command -v govulncheck >/dev/null 2>&1; then
    run_check "Dependency vulnerability audit (Go)" govulncheck ./...
  else
    warn "Dependency audit skipped because govulncheck is not installed"
  fi
fi

printf '\nSummary:\n'
printf '  Failures: %s\n' "$FAILURES"
printf '  Warnings: %s\n' "$WARNINGS"

if [ "$FAILURES" -gt 0 ]; then
  exit 1
fi

exit 0
