#!/usr/bin/env python3
"""
SpecOps Spec Artifact Linter

Validates spec artifacts in <specsDir>/ for:
1. Checkbox staleness: completed tasks with unchecked items (excluding Deferred Criteria)
2. Documentation Review: completed specs must have ## Documentation Review in implementation.md
3. Version validation: specopsCreatedWith/specopsUpdatedWith must be valid semver, absent, or "unknown"

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

        with open(tasks_path, "r", encoding="utf-8") as f:
            content = f.read()

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
    specopsCreatedWith < 1.4.0 or absent) are skipped.
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
        # Parse version — skip if < 1.4.0
        try:
            parts = [int(x) for x in created_with.split(".")]
            if len(parts) == 3 and (
                parts[0] < 1 or (parts[0] == 1 and parts[1] < 4)
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

        with open(impl_path, "r", encoding="utf-8") as f:
            impl_content = f.read()

        if "## Documentation Review" not in impl_content:
            errors.append(
                f"  {spec_name}: completed spec missing '## Documentation Review' section in implementation.md"
            )

    return errors


def lint_version_fields(specs_dir):
    """Validate specopsCreatedWith and specopsUpdatedWith in spec.json."""
    semver_re = re.compile(r"^\d+\.\d+\.\d+$")
    warnings = []

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
            warnings.append(f"  {spec_name}: spec.json is not valid JSON")
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
                warnings.append(
                    f"  {spec_name}: {field} has invalid version format: '{value}'"
                )

    return warnings


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

    # Check 3: Version field validation
    print("\nCheck 3: Version field validation")
    version_warnings = lint_version_fields(specs_dir)
    if version_warnings:
        for warn in version_warnings:
            print(f"  WARN: {warn}")
        # Version issues are warnings, not errors
    else:
        print("  PASS: All version fields are valid")

    print(f"\n{'=' * 40}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found")
        return 1
    else:
        if version_warnings:
            print(f"PASSED with {len(version_warnings)} warning(s)")
        else:
            print("PASSED: All checks clean")
        return 0


if __name__ == "__main__":
    sys.exit(main())
