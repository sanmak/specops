#!/usr/bin/env python3
"""
SpecOps Spec Artifact Linter

Validates spec artifacts in <specsDir>/ for:
1. Checkbox staleness: completed tasks with unchecked items (excluding Deferred Criteria)
2. Documentation Review: completed specs must have ## Documentation Review in implementation.md
3. Task tracking: when taskTracking is configured, High/Medium tasks must have valid IssueIDs
4. Version validation: specopsCreatedWith/specopsUpdatedWith must be valid semver, absent, or "unknown"

Usage:
    python3 scripts/lint-spec-artifacts.py [specsDir]
    python3 scripts/lint-spec-artifacts.py .specops
"""

import json
import os
import re
import sys


def parse_tasks(content):
    """Parse tasks.md into a list of task dicts with status and checkbox info."""
    tasks = []
    current_task = None
    in_deferred = False
    in_acceptance = False
    in_tests = False

    for line in content.split("\n"):
        # Detect task headers (### Task N: ...)
        if re.match(r"^### Task \d+:", line):
            if current_task:
                tasks.append(current_task)
            current_task = {
                "name": line.strip("# ").strip(),
                "status": None,
                "unchecked": [],
            }
            in_deferred = False
            in_acceptance = False
            in_tests = False
            continue

        if current_task is None:
            continue

        # Detect status line
        status_match = re.match(r"\*\*Status:\*\*\s*(.+)", line)
        if status_match:
            current_task["status"] = status_match.group(1).strip()
            continue

        # Detect section boundaries
        if line.strip().startswith("**Acceptance Criteria:**"):
            in_acceptance = True
            in_deferred = False
            in_tests = False
            continue
        if line.strip().startswith("**Tests Required:**"):
            in_tests = True
            in_acceptance = False
            in_deferred = False
            continue
        if line.strip().startswith("**Deferred Criteria:**") or line.strip().startswith(
            "**Deferred Criteria**"
        ):
            in_deferred = True
            in_acceptance = False
            in_tests = False
            continue

        # Detect other bold sections that end acceptance/tests/deferred
        if re.match(r"^\*\*[A-Z].*:\*\*", line) and not any(
            kw in line
            for kw in ["Acceptance Criteria", "Tests Required", "Deferred Criteria"]
        ):
            in_acceptance = False
            in_tests = False
            in_deferred = False
            continue

        # Detect next task header or horizontal rule
        if line.strip() == "---":
            in_acceptance = False
            in_tests = False
            in_deferred = False
            continue

        # Check for unchecked items (only in acceptance/tests, not in deferred)
        if (in_acceptance or in_tests) and not in_deferred:
            if re.match(r"^\s*- \[ \]", line):
                current_task["unchecked"].append(line.strip())

    if current_task:
        tasks.append(current_task)

    return tasks


def lint_checkbox_staleness(specs_dir):
    """Check completed tasks for unchecked items."""
    errors = []

    for spec_name in sorted(os.listdir(specs_dir)):
        spec_dir = os.path.join(specs_dir, spec_name)
        if not os.path.isdir(spec_dir):
            continue

        tasks_path = os.path.join(spec_dir, "tasks.md")
        if not os.path.exists(tasks_path):
            continue

        try:
            with open(tasks_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            errors.append(f"  {spec_name}: cannot read tasks.md: {e}")
            continue

        tasks = parse_tasks(content)
        for task in tasks:
            if task["status"] and task["status"].lower() == "completed":
                for item in task["unchecked"]:
                    errors.append(
                        f"  {spec_name} > {task['name']}: unchecked item in completed task: {item}"
                    )

    return errors


def lint_docs_review(specs_dir):
    """Check that completed specs have Documentation Review in implementation.md.

    Legacy specs (completed before this gate was introduced, identified by
    specopsCreatedWith <= 1.3.0 or absent) are skipped. The gate was introduced
    at 1.3.0 but specs created at that version predate enforcement.
    """
    errors = []

    for spec_name in sorted(os.listdir(specs_dir)):
        spec_dir = os.path.join(specs_dir, spec_name)
        if not os.path.isdir(spec_dir):
            continue

        spec_json_path = os.path.join(spec_dir, "spec.json")
        if not os.path.exists(spec_json_path):
            continue

        try:
            with open(spec_json_path, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if spec.get("status") != "completed":
            continue

        # Skip legacy specs (created before this gate existed)
        created_with = spec.get("specopsCreatedWith", "")
        if not created_with or created_with == "unknown":
            continue
        if not isinstance(created_with, str):
            continue
        # Parse version — skip if < 1.3.0 (gate introduced at 1.3.0)
        try:
            parts = [int(x) for x in created_with.split(".")]
            if len(parts) == 3 and (
                parts[0] < 1
                or (parts[0] == 1 and parts[1] < 3)
            ):
                continue
        except (ValueError, IndexError):
            continue

        impl_path = os.path.join(spec_dir, "implementation.md")
        if not os.path.exists(impl_path):
            errors.append(
                f"  {spec_name}: completed spec missing implementation.md"
            )
            continue

        try:
            with open(impl_path, "r", encoding="utf-8") as f:
                impl_content = f.read()
        except OSError as e:
            errors.append(f"  {spec_name}: cannot read implementation.md: {e}")
            continue

        if "## Documentation Review" not in impl_content:
            errors.append(
                f"  {spec_name}: completed spec missing '## Documentation Review' section in implementation.md"
            )

    return errors


def lint_version_fields(specs_dir):
    """Validate specopsCreatedWith and specopsUpdatedWith in spec.json."""
    semver_re = re.compile(r"^\d+\.\d+\.\d+$")
    errors = []

    for spec_name in sorted(os.listdir(specs_dir)):
        spec_dir = os.path.join(specs_dir, spec_name)
        if not os.path.isdir(spec_dir):
            continue

        spec_json_path = os.path.join(spec_dir, "spec.json")
        if not os.path.exists(spec_json_path):
            continue

        try:
            with open(spec_json_path, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except (json.JSONDecodeError, OSError):
            errors.append(f"  {spec_name}: spec.json is not valid JSON")
            continue

        for field in ["specopsCreatedWith", "specopsUpdatedWith"]:
            value = spec.get(field)
            if value is None:
                # Absent is OK (legacy spec)
                continue
            if value == "unknown":
                # Acceptable fallback
                continue
            if not semver_re.match(value):
                errors.append(
                    f"  {spec_name}: {field} has invalid version format: '{value}'"
                )

    return errors


def load_specops_config(specs_dir):
    """Load .specops.json from the project root (parent of specsDir) or cwd."""
    # Try project root (assume specsDir is relative to project root)
    for candidate in [".specops.json", os.path.join(os.path.dirname(specs_dir) or ".", ".specops.json")]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
    return {}


def lint_task_tracking(specs_dir):
    """Check that completed specs with taskTracking configured have valid IssueIDs.

    When taskTracking is not "none", High/Medium priority tasks in completed
    specs must have IssueID set to a valid tracker identifier (e.g., #42,
    PROJ-123) or FAILED — <reason>. Values like None, TBD, or N/A indicate
    the task tracking gate was skipped — a protocol breach.

    Specs created before 1.3.0 (or with no specopsCreatedWith) are
    skipped since task tracking enforcement was introduced at 1.3.0.
    """
    config = load_specops_config(specs_dir)
    task_tracking = config.get("team", {}).get("taskTracking", "none")

    if task_tracking == "none":
        return []

    errors = []
    valid_issue_re = re.compile(r"^(#\d+|[A-Z]+-\d+|FAILED\s*[—–-])")

    for spec_name in sorted(os.listdir(specs_dir)):
        spec_dir = os.path.join(specs_dir, spec_name)
        if not os.path.isdir(spec_dir):
            continue

        spec_json_path = os.path.join(spec_dir, "spec.json")
        if not os.path.exists(spec_json_path):
            continue

        try:
            with open(spec_json_path, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if spec.get("status") != "completed":
            continue

        # Skip legacy specs (created before 1.3.0, when task tracking
        # enforcement was introduced)
        created_with = spec.get("specopsCreatedWith", "")
        if not created_with or created_with == "unknown":
            continue
        if not isinstance(created_with, str):
            continue
        try:
            parts = [int(x) for x in created_with.split(".")]
            if len(parts) == 3 and (
                parts[0] < 1
                or (parts[0] == 1 and parts[1] < 3)
            ):
                continue
        except (ValueError, IndexError):
            continue

        tasks_path = os.path.join(spec_dir, "tasks.md")
        if not os.path.exists(tasks_path):
            continue

        try:
            with open(tasks_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            errors.append(f"  {spec_name}: cannot read tasks.md: {e}")
            continue

        # First pass: collect all tasks with their priority, status, and IssueID
        task_entries = []
        current_task_name = None
        current_priority = None
        current_issue_id = None
        current_status = None

        for line in content.split("\n"):
            task_match = re.match(r"^### Task \d+:\s*(.+)", line)
            if task_match:
                if current_task_name:
                    task_entries.append((current_task_name, current_priority, current_issue_id, current_status))
                current_task_name = task_match.group(1).strip()
                current_priority = None
                current_issue_id = None
                current_status = None
                continue

            status_match = re.match(r"\*\*Status:\*\*\s*(.+)", line)
            if status_match:
                current_status = status_match.group(1).strip()
                continue

            priority_match = re.match(r"\*\*Priority:\*\*\s*(.+)", line)
            if priority_match:
                current_priority = priority_match.group(1).strip()
                continue

            issue_match = re.match(r"\*\*IssueID:\*\*\s*(.+)", line)
            if issue_match:
                current_issue_id = issue_match.group(1).strip()
                continue

        if current_task_name:
            task_entries.append((current_task_name, current_priority, current_issue_id, current_status))

        # Filter to eligible tasks (High/Medium priority, completed status)
        eligible = [
            (n, p, i)
            for n, p, i, s in task_entries
            if p in ("High", "Medium") and (s or "").lower() == "completed"
        ]
        if not eligible:
            continue

        # Flag tasks with missing/invalid IssueIDs
        for task_name, priority, issue_id in eligible:
            if not issue_id or not valid_issue_re.match(issue_id):
                errors.append(
                    f"  {spec_name} > {task_name}: "
                    f"{priority}-priority task missing valid IssueID "
                    f"(got '{issue_id or 'None'}', "
                    f"taskTracking={task_tracking})"
                )

    return errors


def main():
    specs_dir = sys.argv[1] if len(sys.argv) > 1 else ".specops"

    if not os.path.isdir(specs_dir):
        print(f"Specs directory not found: {specs_dir}")
        print("Skipping spec artifact linting (no specs to lint).")
        return 0

    print("SpecOps Spec Artifact Linter")
    print("=" * 40)
    print(f"Scanning: {specs_dir}/")

    all_errors = []

    # Check 1: Checkbox staleness
    print("\nCheck 1: Checkbox staleness")
    checkbox_errors = lint_checkbox_staleness(specs_dir)
    if checkbox_errors:
        for err in checkbox_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(checkbox_errors)
    else:
        print("  PASS: No stale checkboxes in completed tasks")

    # Check 2: Documentation Review section
    print("\nCheck 2: Documentation Review section")
    docs_errors = lint_docs_review(specs_dir)
    if docs_errors:
        for err in docs_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(docs_errors)
    else:
        print("  PASS: All applicable completed specs have Documentation Review")

    # Check 3: Task tracking IssueID validation
    print("\nCheck 3: Task tracking IssueID validation")
    tracking_errors = lint_task_tracking(specs_dir)
    if tracking_errors:
        for err in tracking_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(tracking_errors)
    else:
        print("  PASS: All eligible tasks have valid IssueIDs (or taskTracking is none)")

    # Check 4: Version field validation
    print("\nCheck 4: Version field validation")
    version_errors = lint_version_fields(specs_dir)
    if version_errors:
        for err in version_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(version_errors)
    else:
        print("  PASS: All version fields are valid")

    print(f"\n{'=' * 40}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found")
        return 1
    else:
        print("PASSED: All checks clean")
        return 0


if __name__ == "__main__":
    sys.exit(main())
