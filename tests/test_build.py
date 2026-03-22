"""Test the build system generates valid platform outputs.

Validates:
1. All expected output files are generated
2. No raw abstract tool operations remain in outputs
3. Platform-specific format requirements are met
4. Generated files are non-empty
5. Claude split output: dispatcher + monolithic backup + 15 mode files
6. Skills directory synced with platform output
"""

import filecmp
import json
import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")
SKILLS_DIR = os.path.join(ROOT_DIR, "skills", "specops")

EXPECTED_OUTPUTS = {
    "claude": "SKILL.md",
    "cursor": "specops.mdc",
    "codex": "SKILL.md",
    "copilot": "specops.instructions.md",
}

# Claude split output: 15 mode files (from core/mode-manifest.json)
EXPECTED_CLAUDE_MODES = [
    "audit.md",
    "feedback.md",
    "from-plan.md",
    "init.md",
    "initiative.md",
    "interview.md",
    "learn.md",
    "map.md",
    "memory.md",
    "pipeline.md",
    "spec.md",
    "steering.md",
    "update.md",
    "version.md",
    "view.md",
]

# Modes that have no core modules and are expected to be empty
EMPTY_MODE_FILES = ["version.md"]

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


def test_claude_split_output():
    """Verify Claude generates dispatcher + monolithic backup + 14 mode files."""
    errors = 0
    claude_dir = os.path.join(PLATFORMS_DIR, "claude")
    modes_dir = os.path.join(claude_dir, "modes")

    # 1. Dispatcher SKILL.md exists and is non-empty
    dispatcher_path = os.path.join(claude_dir, "SKILL.md")
    if not os.path.exists(dispatcher_path):
        print("FAIL: Claude dispatcher SKILL.md not found")
        errors += 1
    else:
        content = read_file(dispatcher_path)
        if len(content.strip()) == 0:
            print("FAIL: Claude dispatcher SKILL.md is empty")
            errors += 1
        else:
            print(f"PASS: Claude dispatcher SKILL.md exists ({len(content)} chars)")

    # 2. Monolithic backup exists and is non-empty
    monolithic_path = os.path.join(claude_dir, "SKILL.monolithic.md")
    if not os.path.exists(monolithic_path):
        print("FAIL: Claude monolithic backup SKILL.monolithic.md not found")
        errors += 1
    else:
        content = read_file(monolithic_path)
        if len(content.strip()) == 0:
            print("FAIL: Claude SKILL.monolithic.md is empty")
            errors += 1
        else:
            print(f"PASS: Claude SKILL.monolithic.md exists ({len(content)} chars)")

    # 3. modes/ directory exists with exactly 13 .md files
    if not os.path.isdir(modes_dir):
        print("FAIL: Claude modes/ directory not found")
        errors += 1
        return errors

    mode_files = sorted(f for f in os.listdir(modes_dir) if f.endswith(".md"))
    if mode_files != sorted(EXPECTED_CLAUDE_MODES):
        missing = set(EXPECTED_CLAUDE_MODES) - set(mode_files)
        extra = set(mode_files) - set(EXPECTED_CLAUDE_MODES)
        if missing:
            print(f"FAIL: Missing mode files: {', '.join(sorted(missing))}")
        if extra:
            print(f"FAIL: Unexpected mode files: {', '.join(sorted(extra))}")
        errors += 1
    else:
        print(f"PASS: Claude modes/ has exactly {len(EXPECTED_CLAUDE_MODES)} mode files")

    # 4. Each mode file has content (except known empty modes like version)
    for mode_file in EXPECTED_CLAUDE_MODES:
        mode_path = os.path.join(modes_dir, mode_file)
        if not os.path.exists(mode_path):
            continue
        content = read_file(mode_path)
        if mode_file in EMPTY_MODE_FILES:
            # Known empty modes (no core modules) — just verify file exists
            print(f"PASS: Claude modes/{mode_file} exists (empty mode, expected)")
        elif len(content.strip()) == 0:
            print(f"FAIL: Claude modes/{mode_file} is empty (expected content)")
            errors += 1
        else:
            print(f"PASS: Claude modes/{mode_file} has content ({len(content)} chars)")

    return errors


def test_claude_modes_no_abstract_operations():
    """Check that no raw abstract operations remain in Claude mode files."""
    errors = 0
    modes_dir = os.path.join(PLATFORMS_DIR, "claude", "modes")

    if not os.path.isdir(modes_dir):
        print("SKIP: Claude modes/ directory not found")
        return 0

    for mode_file in sorted(os.listdir(modes_dir)):
        if not mode_file.endswith(".md"):
            continue
        mode_path = os.path.join(modes_dir, mode_file)
        content = read_file(mode_path)
        for op in ABSTRACT_OPERATIONS:
            if op in content:
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if op in line and not line.strip().startswith("#") and "abstraction" not in line.lower():
                        print(f"FAIL: Raw abstract operation '{op}' found in claude/modes/{mode_file} line {i}")
                        errors += 1

    if errors == 0:
        print("PASS: No raw abstract operations in Claude mode files")

    return errors


def test_claude_skills_sync():
    """Verify skills/specops/ is synced with platforms/claude/ for split output."""
    errors = 0
    claude_modes_dir = os.path.join(PLATFORMS_DIR, "claude", "modes")
    skills_modes_dir = os.path.join(SKILLS_DIR, "modes")

    # Check skills/specops/SKILL.md matches platforms/claude/SKILL.md
    claude_skill = os.path.join(PLATFORMS_DIR, "claude", "SKILL.md")
    skills_skill = os.path.join(SKILLS_DIR, "SKILL.md")
    if os.path.exists(claude_skill) and os.path.exists(skills_skill):
        if filecmp.cmp(claude_skill, skills_skill, shallow=False):
            print("PASS: skills/specops/SKILL.md matches platforms/claude/SKILL.md")
        else:
            print("FAIL: skills/specops/SKILL.md differs from platforms/claude/SKILL.md")
            errors += 1
    elif not os.path.exists(skills_skill):
        print("FAIL: skills/specops/SKILL.md not found")
        errors += 1

    # Check skills/specops/modes/ directory exists
    if not os.path.isdir(skills_modes_dir):
        print("FAIL: skills/specops/modes/ directory not found")
        errors += 1
        return errors

    if not os.path.isdir(claude_modes_dir):
        print("SKIP: platforms/claude/modes/ not found, cannot compare")
        return errors

    # Compare mode files
    claude_modes = sorted(f for f in os.listdir(claude_modes_dir) if f.endswith(".md"))
    skills_modes = sorted(f for f in os.listdir(skills_modes_dir) if f.endswith(".md"))

    if claude_modes != skills_modes:
        missing = set(claude_modes) - set(skills_modes)
        extra = set(skills_modes) - set(claude_modes)
        if missing:
            print(f"FAIL: skills/specops/modes/ missing: {', '.join(sorted(missing))}")
        if extra:
            print(f"FAIL: skills/specops/modes/ has extra: {', '.join(sorted(extra))}")
        errors += 1
    else:
        # Compare content of each file
        all_match = True
        for mode_file in claude_modes:
            claude_path = os.path.join(claude_modes_dir, mode_file)
            skills_path = os.path.join(skills_modes_dir, mode_file)
            if not filecmp.cmp(claude_path, skills_path, shallow=False):
                print(f"FAIL: skills/specops/modes/{mode_file} differs from platforms/claude/modes/{mode_file}")
                errors += 1
                all_match = False
        if all_match:
            print(f"PASS: skills/specops/modes/ synced with platforms/claude/modes/ ({len(claude_modes)} files)")

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


def test_claude_skill_md_format():
    """Validate Claude SKILL.md format."""
    filepath = os.path.join(PLATFORMS_DIR, "claude", "SKILL.md")
    if not os.path.exists(filepath):
        print("SKIP: Claude SKILL.md not found")
        return 0

    content = read_file(filepath)
    errors = 0

    if not content.startswith("---\n"):
        print("FAIL: Claude SKILL.md must start with YAML frontmatter (---)")
        errors += 1

    # Find closing frontmatter
    second_dash = content.find("---\n", 4)
    if second_dash == -1:
        print("FAIL: Claude SKILL.md has unclosed YAML frontmatter")
        errors += 1
    else:
        frontmatter = content[4:second_dash]
        if "name:" not in frontmatter:
            print("FAIL: Claude SKILL.md frontmatter missing 'name'")
            errors += 1
        if "description:" not in frontmatter:
            print("FAIL: Claude SKILL.md frontmatter missing 'description'")
            errors += 1

    if errors == 0:
        print("PASS: Claude SKILL.md format is valid")

    return errors


def test_codex_skill_md_format():
    """Validate Codex SKILL.md format."""
    filepath = os.path.join(PLATFORMS_DIR, "codex", "SKILL.md")
    if not os.path.exists(filepath):
        print("SKIP: Codex SKILL.md not found")
        return 0

    content = read_file(filepath)
    errors = 0

    if not content.startswith("---\n"):
        print("FAIL: Codex SKILL.md must start with YAML frontmatter (---)")
        errors += 1

    second_dash = content.find("---\n", 4)
    if second_dash == -1:
        print("FAIL: Codex SKILL.md has unclosed YAML frontmatter")
        errors += 1
    else:
        frontmatter = content[4:second_dash]
        if "name:" not in frontmatter:
            print("FAIL: Codex SKILL.md frontmatter missing 'name'")
            errors += 1
        if "description:" not in frontmatter:
            print("FAIL: Codex SKILL.md frontmatter missing 'description'")
            errors += 1

    if errors == 0:
        print("PASS: Codex SKILL.md format is valid")

    return errors


def test_copilot_instructions_format():
    """Validate Copilot specops.instructions.md format."""
    filepath = os.path.join(PLATFORMS_DIR, "copilot", "specops.instructions.md")
    if not os.path.exists(filepath):
        print("SKIP: Copilot specops.instructions.md not found")
        return 0

    content = read_file(filepath)
    errors = 0

    if not content.startswith("---\n"):
        print("FAIL: Copilot specops.instructions.md must start with YAML frontmatter (---)")
        errors += 1

    second_dash = content.find("---\n", 4)
    if second_dash == -1:
        print("FAIL: Copilot specops.instructions.md has unclosed YAML frontmatter")
        errors += 1
    else:
        frontmatter = content[4:second_dash]
        if "applyTo:" not in frontmatter:
            print("FAIL: Copilot specops.instructions.md frontmatter missing 'applyTo'")
            errors += 1

    if errors == 0:
        print("PASS: Copilot specops.instructions.md format is valid")

    return errors


def test_version_in_frontmatter():
    """Check all generated outputs have version in their frontmatter."""
    errors = 0

    for platform, filename in EXPECTED_OUTPUTS.items():
        filepath = os.path.join(PLATFORMS_DIR, platform, filename)
        if not os.path.exists(filepath):
            continue

        content = read_file(filepath)
        if not content.startswith("---\n"):
            continue

        second_dash = content.find("---\n", 4)
        if second_dash == -1:
            continue

        frontmatter = content[4:second_dash]
        if "version:" not in frontmatter:
            print(f"FAIL: {platform}/{filename} frontmatter missing 'version' field")
            errors += 1
        else:
            # Verify version matches platform.json
            config_path = os.path.join(PLATFORMS_DIR, platform, "platform.json")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                expected = config.get("version", "")
                for line in frontmatter.splitlines():
                    if line.startswith("version:"):
                        actual = line.split(":", 1)[1].strip().strip('"')
                        if actual != expected:
                            print(
                                f"FAIL: {platform}/{filename} frontmatter version"
                                f" ({actual}) != platform.json ({expected})"
                            )
                            errors += 1
                        break

    if errors == 0:
        print("PASS: All generated outputs have correct version in frontmatter")

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

    print("\n--- Test: Claude Split Output ---")
    total_errors += test_claude_split_output()

    print("\n--- Test: Claude Modes No Abstract Operations ---")
    total_errors += test_claude_modes_no_abstract_operations()

    print("\n--- Test: Claude Skills Sync ---")
    total_errors += test_claude_skills_sync()

    print("\n--- Test: Cursor MDC Format ---")
    total_errors += test_cursor_mdc_format()

    print("\n--- Test: Claude SKILL.md Format ---")
    total_errors += test_claude_skill_md_format()

    print("\n--- Test: Codex SKILL.md Format ---")
    total_errors += test_codex_skill_md_format()

    print("\n--- Test: Copilot Instructions Format ---")
    total_errors += test_copilot_instructions_format()

    print("\n--- Test: Version in Frontmatter ---")
    total_errors += test_version_in_frontmatter()

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
