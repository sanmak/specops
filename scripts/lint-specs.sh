#!/usr/bin/env bash
set -e

# Spec artifact linter — catches checkbox staleness in completed tasks.
# A completed task with unchecked checkboxes (- [ ]) is a protocol breach.
#
# Usage: bash scripts/lint-specs.sh [specs-dir]
# Default specs-dir: .specops

SPECS_DIR="${1:-.specops}"
EXIT_CODE=0

if [ ! -d "$SPECS_DIR" ]; then
  echo "No specs directory found at '$SPECS_DIR'"
  exit 0
fi

for tasks_file in "$SPECS_DIR"/*/tasks.md; do
  [ -f "$tasks_file" ] || continue

  spec_name="$(basename "$(dirname "$tasks_file")")"
  in_completed_task=false
  task_name=""
  line_num=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    line_num=$((line_num + 1))

    # Detect task heading (### Task N: ...)
    if echo "$line" | grep -qE '^### Task [0-9]'; then
      in_completed_task=false
      task_name="$line"
    elif echo "$line" | grep -qE '^### '; then
      # Any other h3 section also ends the current task context
      in_completed_task=false
    fi

    # Detect status line
    if echo "$line" | grep -qiE '^\*\*Status:\*\* Completed'; then
      in_completed_task=true
    fi

    # Check for unchecked checkboxes in completed tasks
    if "$in_completed_task" && echo "$line" | grep -qE '^[[:space:]]*- \[ \]'; then
      echo "FAIL: $spec_name/tasks.md:$line_num — unchecked checkbox in completed task"
      echo "  Task: $task_name"
      echo "  Line: $line"
      echo ""
      EXIT_CODE=1
    fi
  done < "$tasks_file"
done

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "PASS: No checkbox staleness found in $SPECS_DIR"
else
  echo "Checkbox staleness detected — completed tasks must have all checkboxes checked."
  echo "Fix: change '- [ ]' to '- [x]' for items that were verified, or add '— N/A' for items not applicable."
fi

exit "$EXIT_CODE"
