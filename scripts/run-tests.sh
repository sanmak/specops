#!/bin/bash
# scripts/run-tests.sh -- Run all SpecOps tests and report a summary
#
# Usage:
#   bash scripts/run-tests.sh
#
# Requires: python3, pip (jsonschema will be installed if missing)

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PASS=0
FAIL=0
ERRORS=()

run_test() {
  local label="$1"
  local cmd="$2"

  printf "  %-50s " "$label"
  if (cd "$ROOT_DIR" && eval "$cmd" > /dev/null 2>&1); then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
    ERRORS+=("$label")
  fi
}

echo "SpecOps Test Suite"
echo "=================="

# Ensure jsonschema is available
if ! python3 -c "import jsonschema" 2>/dev/null; then
  echo "Installing jsonschema..."
  pip install --quiet jsonschema
fi

echo ""
echo "Running tests..."
run_test "JSON validity (schema.json)"      "python3 -c \"import json; json.load(open('schema.json'))\""
run_test "Schema validation (examples)"     "python3 tests/test_schema_validation.py"
run_test "Schema constraints"               "python3 tests/test_schema_constraints.py"
run_test "Schema sync (schema vs skill)"    "python3 tests/check_schema_sync.py"
run_test "Platform consistency"             "python3 tests/test_platform_consistency.py"
run_test "Build system"                     "python3 tests/test_build.py"

echo ""
echo "=================="
echo "Results: $PASS passed, $FAIL failed"

if [ "${#ERRORS[@]}" -gt 0 ]; then
  echo ""
  echo "Failed tests:"
  for err in "${ERRORS[@]}"; do
    echo "  - $err"
  done
  exit 1
fi
