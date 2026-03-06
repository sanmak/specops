#!/usr/bin/env python3
"""
SpecOps Platform Validator

Validates that generated platform outputs are complete and correct:
1. All safety rules from core/safety.md are present in every output
2. All spec templates from core/templates/ are present in every output
3. No raw abstract tool operations remain (e.g., READ_FILE should be substituted)
4. Platform-specific format validation
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(ROOT_DIR, "core")
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")

# Abstract tool operations that should NOT appear in generated outputs
ABSTRACT_OPERATIONS = [
    "READ_FILE(",
    "WRITE_FILE(",
    "EDIT_FILE(",
    "LIST_DIR(",
    "RUN_COMMAND(",
    "ASK_USER(",
    "NOTIFY_USER(",
    "UPDATE_PROGRESS(",
]

# Key safety phrases that MUST appear in every generated output
SAFETY_MARKERS = [
    "Convention Sanitization",
    "meta-instructions",
    "Template File Safety",
    "fall back to the default template",
    "Path Containment",
    "specsDir",
    "path traversal",
]

# Key template markers that MUST appear in every generated output
TEMPLATE_MARKERS = [
    "Feature: [Title]",
    "Bug Fix: [Title]",
    "Refactor: [Title]",
    "Design: [Title]",
    "Implementation Tasks: [Title]",
]

# Key workflow markers that MUST appear in every output
WORKFLOW_MARKERS = [
    "Phase 1: Understand Context",
    "Phase 2: Create Specification",
    "Phase 3: Implement",
    "Phase 4: Complete",
]

# Review workflow markers that MUST appear
REVIEW_MARKERS = [
    "spec.json",
    "reviews.md",
    "review mode",
    "revision mode",
    "implementation gate",
    "Status Dashboard",
]

# Vertical markers that MUST appear
VERTICAL_MARKERS = [
    "### infrastructure",
    "### data",
    "### library",
    "### frontend",
    "### builder",
]

# View workflow markers that MUST appear
VIEW_MARKERS = [
    "Spec Viewing",
    "View/List Mode Detection",
    "List Specs",
    "View: Summary",
    "View: Full",
    "View: Walkthrough",
    "View: Status",
]

# Interview workflow markers that MUST appear
INTERVIEW_MARKERS = [
    "Interview Mode",
    "gathering",
    "clarifying",
    "confirming",
]


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_generated_files():
    """Find all generated platform output files."""
    generated = {}
    platform_outputs = {
        "claude": "SKILL.md",
        "cursor": "specops.mdc",
        "codex": "SKILL.md",
        "copilot": "specops.instructions.md",
    }

    for platform, filename in platform_outputs.items():
        filepath = os.path.join(PLATFORMS_DIR, platform, filename)
        if os.path.exists(filepath):
            generated[platform] = {
                "path": filepath,
                "content": read_file(filepath),
            }

    return generated


def check_no_abstract_operations(platform, content):
    """Ensure no raw abstract tool operations remain."""
    errors = []
    # Only check outside of the tool-abstraction documentation sections
    # Skip checking inside code blocks that document the abstraction
    lines = content.split("\n")
    in_code_block = False
    in_abstraction_section = False

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if "Tool Abstraction" in line or "Abstract Tool Operations" in line:
            in_abstraction_section = True
            continue
        if in_abstraction_section and line.startswith("## ") and "Tool" not in line:
            in_abstraction_section = False

        if not in_code_block and not in_abstraction_section:
            for op in ABSTRACT_OPERATIONS:
                if op in line:
                    errors.append(f"  Line {i}: Found raw abstract operation '{op}' in {platform}")

    return errors


def check_markers_present(platform, content, markers, category):
    """Check that all required markers are present in the content."""
    errors = []
    for marker in markers:
        if marker not in content:
            errors.append(f"  Missing {category} marker in {platform}: '{marker}'")
    return errors


def validate_frontmatter_format(content, platform, required_fields):
    """Validate YAML frontmatter format (--- delimited with required fields)."""
    errors = []
    if not content.startswith("---\n"):
        errors.append(f"  {platform} file must start with YAML frontmatter (---)")
        return errors, content

    # Find closing frontmatter
    second_dash = content.find("---\n", 4)
    if second_dash == -1:
        errors.append(f"  {platform} file has unclosed YAML frontmatter")
        return errors, content

    frontmatter = content[4:second_dash]
    for field in required_fields:
        if f"{field}:" not in frontmatter:
            errors.append(f"  {platform} frontmatter missing '{field}' field")

    # Return body content (after frontmatter) for further validation
    body = content[second_dash + 4:]
    return errors, body


def validate_platform(platform, info):
    """Run all validations for a single platform."""
    errors = []
    content = info["content"]

    # Check no abstract operations remain
    errors.extend(check_no_abstract_operations(platform, content))

    # Check safety rules present
    errors.extend(check_markers_present(platform, content, SAFETY_MARKERS, "safety"))

    # Check templates present
    errors.extend(check_markers_present(platform, content, TEMPLATE_MARKERS, "template"))

    # Check workflow present
    errors.extend(check_markers_present(platform, content, WORKFLOW_MARKERS, "workflow"))

    # Check review workflow present
    errors.extend(check_markers_present(platform, content, REVIEW_MARKERS, "review"))

    # Check verticals present
    errors.extend(check_markers_present(platform, content, VERTICAL_MARKERS, "vertical"))

    # Check view workflow present
    errors.extend(check_markers_present(platform, content, VIEW_MARKERS, "view"))

    # Check interview workflow present
    errors.extend(check_markers_present(platform, content, INTERVIEW_MARKERS, "interview"))

    # Platform-specific format validation
    if platform == "cursor":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Cursor .mdc", ["description"]
        )
        errors.extend(fmt_errors)
    elif platform == "claude":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Claude SKILL.md", ["name", "description"]
        )
        errors.extend(fmt_errors)
    elif platform == "codex":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Codex SKILL.md", ["name", "description"]
        )
        errors.extend(fmt_errors)
    elif platform == "copilot":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Copilot specops.instructions.md", ["applyTo"]
        )
        errors.extend(fmt_errors)

    return errors


def main():
    print("SpecOps Platform Validator")
    print("=" * 40)

    generated = get_generated_files()

    if not generated:
        print("\nERROR: No generated platform files found.")
        print("Run 'python3 generator/generate.py --all' first.")
        return 1

    print(f"\nFound {len(generated)} platform output(s): {', '.join(generated.keys())}")

    all_errors = []
    for platform, info in generated.items():
        print(f"\nValidating: {platform} ({os.path.relpath(info['path'], ROOT_DIR)})")
        errors = validate_platform(platform, info)
        if errors:
            for err in errors:
                print(f"  FAIL: {err}")
            all_errors.extend(errors)
        else:
            print("  PASS: All checks passed")

    # Cross-platform consistency check
    print("\nCross-platform consistency:")
    if len(generated) >= 2:
        platforms = list(generated.keys())
        for marker in WORKFLOW_MARKERS + SAFETY_MARKERS + REVIEW_MARKERS + VIEW_MARKERS:
            present_in = [p for p in platforms if marker in generated[p]["content"]]
            if len(present_in) != len(platforms):
                missing = set(platforms) - set(present_in)
                err = f"  '{marker}' missing from: {', '.join(missing)}"
                print(f"  FAIL: {err}")
                all_errors.append(err)

        if not any("FAIL" in str(e) for e in all_errors if "Cross" in str(e)):
            print("  PASS: All platforms have consistent content")
    else:
        print("  SKIP: Need at least 2 platforms for consistency check")

    print(f"\n{'=' * 40}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found")
        return 1
    else:
        print("PASSED: All validations successful")
        return 0


if __name__ == "__main__":
    sys.exit(main())
