"""Test the build system generates valid platform outputs.

Validates:
1. All expected output files are generated
2. No raw abstract tool operations remain in outputs
3. Platform-specific format requirements are met
4. Generated files are non-empty
"""

import json
import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")

EXPECTED_OUTPUTS = {
    "claude": "prompt.md",
    "cursor": "specops.mdc",
    "codex": "AGENTS.md",
    "copilot": "copilot-instructions.md",
}

# Abstract operations that should NOT appear in generated outputs
ABSTRACT_OPERATIONS = [
    "READ_FILE(",
    "WRITE_FILE(",
    "EDIT_FILE(",
    "LIST_DIR(",
    "RUN_COMMAND(",
    "UPDATE_PROGRESS(",
]


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_generation():
    """Run the generator and check that all outputs are created."""
    errors = 0

    # Run the generator
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT_DIR, "generator", "generate.py"), "--all"],
        capture_output=True,
        text=True,
        cwd=ROOT_DIR,
    )

    if result.returncode != 0:
        print(f"FAIL: Generator exited with code {result.returncode}")
        print(f"  stdout: {result.stdout}")
        print(f"  stderr: {result.stderr}")
        return 1

    print("PASS: Generator ran successfully")

    # Check all expected files exist and are non-empty
    for platform, filename in EXPECTED_OUTPUTS.items():
        filepath = os.path.join(PLATFORMS_DIR, platform, filename)
        if not os.path.exists(filepath):
            print(f"FAIL: Expected output not found: {filepath}")
            errors += 1
            continue

        content = read_file(filepath)
        if len(content.strip()) == 0:
            print(f"FAIL: Generated file is empty: {filepath}")
            errors += 1
            continue

        print(f"PASS: {platform}/{filename} exists ({len(content)} chars)")

    return errors


def test_no_abstract_operations():
    """Check that no raw abstract tool operations remain in generated outputs."""
    errors = 0

    for platform, filename in EXPECTED_OUTPUTS.items():
        filepath = os.path.join(PLATFORMS_DIR, platform, filename)
        if not os.path.exists(filepath):
            continue

        content = read_file(filepath)
        for op in ABSTRACT_OPERATIONS:
            if op in content:
                # Check it's not in a documentation/description context
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if op in line and not line.strip().startswith("#") and "abstraction" not in line.lower():
                        print(f"FAIL: Raw abstract operation '{op}' found in {platform}/{filename} line {i}")
                        errors += 1

    if errors == 0:
        print("PASS: No raw abstract operations in generated outputs")

    return errors


def test_cursor_mdc_format():
    """Validate Cursor MDC format."""
    filepath = os.path.join(PLATFORMS_DIR, "cursor", "specops.mdc")
    if not os.path.exists(filepath):
        print("SKIP: Cursor output not found")
        return 0

    content = read_file(filepath)
    errors = 0

    if not content.startswith("---\n"):
        print("FAIL: Cursor .mdc must start with YAML frontmatter (---)")
        errors += 1

    if "description:" not in content[:500]:
        print("FAIL: Cursor .mdc frontmatter missing 'description'")
        errors += 1

    if errors == 0:
        print("PASS: Cursor MDC format is valid")

    return errors


def test_platform_json_valid():
    """Validate all platform.json files are valid JSON."""
    errors = 0

    for platform in EXPECTED_OUTPUTS:
        filepath = os.path.join(PLATFORMS_DIR, platform, "platform.json")
        if not os.path.exists(filepath):
            print(f"FAIL: Missing platform.json for {platform}")
            errors += 1
            continue

        try:
            with open(filepath) as f:
                config = json.load(f)

            # Check required fields
            for field in ["name", "displayName", "capabilities", "toolMapping"]:
                if field not in config:
                    print(f"FAIL: {platform}/platform.json missing required field '{field}'")
                    errors += 1

            print(f"PASS: {platform}/platform.json is valid")
        except json.JSONDecodeError as e:
            print(f"FAIL: {platform}/platform.json is invalid JSON: {e}")
            errors += 1

    return errors


def main():
    print("SpecOps Build Tests")
    print("=" * 40)

    total_errors = 0

    print("\n--- Test: Generation ---")
    total_errors += test_generation()

    print("\n--- Test: No Abstract Operations ---")
    total_errors += test_no_abstract_operations()

    print("\n--- Test: Cursor MDC Format ---")
    total_errors += test_cursor_mdc_format()

    print("\n--- Test: Platform JSON Validity ---")
    total_errors += test_platform_json_valid()

    print(f"\n{'=' * 40}")
    if total_errors > 0:
        print(f"FAILED: {total_errors} error(s) found")
        sys.exit(1)
    else:
        print("PASSED: All build tests successful")


if __name__ == "__main__":
    main()
