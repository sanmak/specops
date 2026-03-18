#!/usr/bin/env python3
"""
SpecOps Platform Validator

Validates that generated platform outputs are complete and correct:
1. All safety rules from core/safety.md are present in every output
2. All spec templates from core/templates/ are present in every output
3. No raw abstract tool operations remain (e.g., READ_FILE should be substituted)
4. Platform-specific format validation
"""

import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(ROOT_DIR, "core")
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")
PLUGIN_DIR = os.path.join(ROOT_DIR, ".claude-plugin")
SKILLS_DIR = os.path.join(ROOT_DIR, "skills")

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
    "GET_SPECOPS_VERSION",
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
    "Implementation Journal: [Title]",
]

# Key workflow markers that MUST appear in every output
WORKFLOW_MARKERS = [
    "Phase 1: Understand Context",
    "Phase 2: Create Specification",
    "Phase 3: Implement",
    "Phase 4: Complete",
    "Version Extraction Protocol",
]

# Review workflow markers that MUST appear
REVIEW_MARKERS = [
    "spec.json",
    "reviews.md",
    "review mode",
    "revision mode",
    "Self-review mode",
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

# Task tracking markers that MUST appear in every output
TASK_TRACKING_MARKERS = [
    "Task State Machine",
    "Write Ordering Protocol",
    "Single Active Task",
    "Blocker Handling",
    "protocol breach",
    "Blocked",
]

# Update workflow markers that MUST appear in every output
UPDATE_MARKERS = [
    "Update Mode",
    "Update Mode Detection",
    "Detect Current Version",
    "Check Latest Available Version",
    "Detect Installation Method",
]

# Regression risk analysis markers that MUST appear in every output (bugfix template)
REGRESSION_MARKERS = [
    "## Regression Risk Analysis",
    "### Blast Radius",
    "### Behavior Inventory",
    "### Test Coverage Assessment",
    "### Risk Tier",
    "### Scope Escalation Check",
]

# Reconciliation (audit/reconcile) markers that MUST appear in every output
RECONCILIATION_MARKERS = [
    "## Audit Mode",
    "## Reconcile Mode",
    "### File Drift",
    "### Post-Completion Modification",
    "### Task Status Inconsistency",
    "### Staleness",
    "### Cross-Spec Conflicts",
    "### Health Summary",
    "### Audit Report",
]

# Steering files markers that MUST appear in every output
STEERING_MARKERS = [
    "## Steering Files",
    "Steering File Format",
    "Inclusion Modes",
    "fileMatch",
    "Loading Procedure",
    "Foundation File Templates",
    "product.md",
    "tech.md",
    "structure.md",
]

# From Plan mode markers that MUST appear in every output
FROM_PLAN_MARKERS = [
    "# From Plan Mode",
    "From Plan mode",
    "Faithful Conversion",
    "from-plan",
    "Parse the plan",
]

# Repo Map markers that MUST appear in every output
REPO_MAP_MARKERS = [
    "## Repo Map",
    "### Repo Map Format",
    "### Repo Map Generation",
    "### Language Tier Extraction",
    "### Staleness Detection",
    "### Scope Control",
    "### Map Subcommand",
    "### Repo Map Safety",
    "### Platform Adaptation",
]

# Local Memory Layer markers that MUST appear in every output
MEMORY_MARKERS = [
    "## Local Memory Layer",
    "### Memory Storage Format",
    "### Memory Loading",
    "### Memory Writing",
    "### Pattern Detection",
    "### Memory Subcommand",
    "### Memory Safety",
    "decisions.json",
    "context.md",
    "patterns.json",
]


# Task delegation markers that MUST appear in every output
DELEGATION_MARKERS = [
    "## Task Delegation",
    "### Delegation Decision",
    "Handoff Bundle",
    "### Strategy A",
    "### Strategy B",
    "### Strategy C",
    "### Delegation Safety",
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

    # Check task tracking present
    errors.extend(check_markers_present(platform, content, TASK_TRACKING_MARKERS, "task-tracking"))

    # Check update workflow present
    errors.extend(check_markers_present(platform, content, UPDATE_MARKERS, "update"))

    # Check regression risk analysis present
    errors.extend(check_markers_present(platform, content, REGRESSION_MARKERS, "regression"))

    # Check steering files present
    errors.extend(check_markers_present(platform, content, STEERING_MARKERS, "steering"))

    # Check reconciliation (audit/reconcile) present
    errors.extend(check_markers_present(platform, content, RECONCILIATION_MARKERS, "reconciliation"))

    # Check from-plan mode present
    errors.extend(check_markers_present(platform, content, FROM_PLAN_MARKERS, "from-plan"))

    # Check memory layer present
    errors.extend(check_markers_present(platform, content, MEMORY_MARKERS, "memory"))

    # Check repo map present
    errors.extend(check_markers_present(platform, content, REPO_MAP_MARKERS, "repo-map"))

    # Check task delegation present
    errors.extend(check_markers_present(platform, content, DELEGATION_MARKERS, "delegation"))

    # Platform-specific format validation
    if platform == "cursor":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Cursor .mdc", ["description", "version"]
        )
        errors.extend(fmt_errors)
    elif platform == "claude":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Claude SKILL.md", ["name", "description", "version"]
        )
        errors.extend(fmt_errors)
    elif platform == "codex":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Codex SKILL.md", ["name", "description", "version"]
        )
        errors.extend(fmt_errors)
    elif platform == "copilot":
        fmt_errors, _ = validate_frontmatter_format(
            content, "Copilot specops.instructions.md", ["applyTo", "version"]
        )
        errors.extend(fmt_errors)

    return errors


def validate_plugin_manifests():
    """Validate plugin.json and marketplace.json manifests."""
    errors = []

    # Check plugin.json
    plugin_path = os.path.join(PLUGIN_DIR, "plugin.json")
    if not os.path.exists(plugin_path):
        errors.append("  Missing .claude-plugin/plugin.json")
    else:
        try:
            with open(plugin_path, "r", encoding="utf-8") as f:
                plugin = json.load(f)
            for field in ["name", "description", "version", "author", "repository"]:
                if field not in plugin:
                    errors.append(f"  plugin.json missing required field '{field}'")
        except json.JSONDecodeError as e:
            errors.append(f"  plugin.json is not valid JSON: {e}")

    # Check marketplace.json
    marketplace_path = os.path.join(PLUGIN_DIR, "marketplace.json")
    if not os.path.exists(marketplace_path):
        errors.append("  Missing .claude-plugin/marketplace.json")
    else:
        try:
            with open(marketplace_path, "r", encoding="utf-8") as f:
                marketplace = json.load(f)
            for field in ["name", "owner", "plugins"]:
                if field not in marketplace:
                    errors.append(f"  marketplace.json missing required field '{field}'")
            if "plugins" in marketplace and len(marketplace["plugins"]) == 0:
                errors.append("  marketplace.json has empty plugins array")
        except json.JSONDecodeError as e:
            errors.append(f"  marketplace.json is not valid JSON: {e}")

    # Check version consistency
    if not errors:
        with open(plugin_path, "r", encoding="utf-8") as f:
            plugin = json.load(f)
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)

        plugin_version = plugin.get("version")
        marketplace_version = marketplace.get("metadata", {}).get("version")
        marketplace_plugin_version = (
            marketplace.get("plugins", [{}])[0].get("version")
            if marketplace.get("plugins")
            else None
        )

        # Check against platform.json version
        claude_config_path = os.path.join(PLATFORMS_DIR, "claude", "platform.json")
        if os.path.exists(claude_config_path):
            with open(claude_config_path, "r", encoding="utf-8") as f:
                claude_config = json.load(f)
            platform_version = claude_config.get("version")

            if plugin_version != platform_version:
                errors.append(
                    f"  Version mismatch: plugin.json ({plugin_version})"
                    f" != platform.json ({platform_version})"
                )
            if marketplace_version and marketplace_version != platform_version:
                errors.append(
                    f"  Version mismatch: marketplace.json metadata ({marketplace_version})"
                    f" != platform.json ({platform_version})"
                )
            if marketplace_plugin_version and marketplace_plugin_version != platform_version:
                errors.append(
                    f"  Version mismatch: marketplace.json plugin ({marketplace_plugin_version})"
                    f" != platform.json ({platform_version})"
                )

    return errors


def validate_version_in_frontmatter(generated):
    """Check that all generated outputs have a version field in frontmatter."""
    errors = []
    for platform, info in generated.items():
        content = info["content"]
        if not content.startswith("---\n"):
            continue
        second_dash = content.find("---\n", 4)
        if second_dash == -1:
            continue
        frontmatter = content[4:second_dash]
        if "version:" not in frontmatter:
            errors.append(f"  {platform} frontmatter missing 'version' field")
        else:
            # Verify version matches platform.json
            config_path = os.path.join(PLATFORMS_DIR, platform, "platform.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                expected_version = config.get("version", "")
                for line in frontmatter.splitlines():
                    if line.startswith("version:"):
                        actual_version = line.split(":", 1)[1].strip().strip('"')
                        if actual_version != expected_version:
                            errors.append(
                                f"  {platform} frontmatter version ({actual_version})"
                                f" != platform.json ({expected_version})"
                            )
                        break
    return errors


def validate_init_skill():
    """Validate init mode content is present in Claude SKILL.md."""
    errors = []

    claude_skill_path = os.path.join(PLATFORMS_DIR, "claude", "SKILL.md")
    if not os.path.exists(claude_skill_path):
        errors.append("  Missing platforms/claude/SKILL.md (needed for init validation)")
        return errors

    content = read_file(claude_skill_path)

    # Check init mode markers
    init_markers = ["Init Mode", "Init Workflow", "Init Mode Detection"]
    for marker in init_markers:
        if marker not in content:
            errors.append(f"  Claude SKILL.md missing init marker: '{marker}'")

    # Check all 5 config templates are present
    template_names = ["Minimal", "Standard", "Full", "Review", "Builder"]
    for name in template_names:
        if f"Template: {name}" not in content:
            errors.append(f"  Claude SKILL.md missing init config template: {name}")

    return errors


def validate_docs_coverage():
    """Validate that documentation files reference all core modules and config options."""
    errors = []

    # Check 1: all schema.json properties → docs/REFERENCE.md
    schema_path = os.path.join(ROOT_DIR, "schema.json")
    reference_path = os.path.join(ROOT_DIR, "docs", "REFERENCE.md")
    if not os.path.exists(reference_path):
        errors.append(
            "  docs/REFERENCE.md is missing — cannot verify schema property coverage"
        )
    elif os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        reference_content = read_file(reference_path)

        def check_props(props, prefix):
            """Recursively check schema properties against REFERENCE.md."""
            for prop_name in props:
                # Skip $schema and private properties
                if prop_name.startswith("$") or prop_name.startswith("_"):
                    continue
                full_name = f"{prefix}.{prop_name}" if prefix else prop_name
                if full_name not in reference_content:
                    errors.append(
                        f"  schema.json property '{full_name}' not found"
                        f" in docs/REFERENCE.md"
                    )
                sub_props = props[prop_name].get("properties")
                if sub_props:
                    check_props(sub_props, full_name)

        top_props = schema.get("properties", {})
        check_props(top_props, "")

    # Check 2: core/*.md modules → docs/STRUCTURE.md
    structure_path = os.path.join(ROOT_DIR, "docs", "STRUCTURE.md")
    if not os.path.exists(structure_path):
        errors.append(
            "  docs/STRUCTURE.md is missing — cannot verify core module coverage"
        )
    else:
        structure_content = read_file(structure_path)
        for filename in sorted(os.listdir(CORE_DIR)):
            if filename.endswith(".md") and os.path.isfile(
                os.path.join(CORE_DIR, filename)
            ):
                if filename not in structure_content:
                    errors.append(
                        f"  core module '{filename}' not found in docs/STRUCTURE.md"
                    )

    # Check 3: core/*.md modules → .claude/commands/docs-sync.md
    docs_sync_path = os.path.join(
        ROOT_DIR, ".claude", "commands", "docs-sync.md"
    )
    if not os.path.exists(docs_sync_path):
        errors.append(
            "  .claude/commands/docs-sync.md is missing —"
            " cannot verify docs-sync mappings"
        )
    else:
        docs_sync_content = read_file(docs_sync_path)
        for filename in sorted(os.listdir(CORE_DIR)):
            if filename.endswith(".md") and os.path.isfile(
                os.path.join(CORE_DIR, filename)
            ):
                # Check for core/filename in the docs-sync dependency map
                core_ref = f"core/{filename}"
                if core_ref not in docs_sync_content:
                    errors.append(
                        f"  core module '{filename}' has no mapping in"
                        f" .claude/commands/docs-sync.md"
                    )

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

    # Version in frontmatter validation
    print("\nValidating: version in frontmatter")
    version_errors = validate_version_in_frontmatter(generated)
    if version_errors:
        for err in version_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(version_errors)
    else:
        print("  PASS: All platforms have version in frontmatter")

    # Plugin manifest validation
    print("\nValidating: plugin manifests")
    plugin_errors = validate_plugin_manifests()
    if plugin_errors:
        for err in plugin_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(plugin_errors)
    else:
        print("  PASS: All plugin manifest checks passed")

    # Init mode validation
    print("\nValidating: init mode")
    init_errors = validate_init_skill()
    if init_errors:
        for err in init_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(init_errors)
    else:
        print("  PASS: Init mode checks passed")

    # Docs coverage validation
    print("\nValidating: docs coverage")
    docs_errors = validate_docs_coverage()
    if docs_errors:
        for err in docs_errors:
            print(f"  FAIL: {err}")
        all_errors.extend(docs_errors)
    else:
        print("  PASS: All docs coverage checks passed")

    # Cross-platform consistency check
    print("\nCross-platform consistency:")
    if len(generated) >= 2:
        platforms = list(generated.keys())
        consistency_errors = []
        for marker in WORKFLOW_MARKERS + SAFETY_MARKERS + REVIEW_MARKERS + VIEW_MARKERS + UPDATE_MARKERS + TASK_TRACKING_MARKERS + REGRESSION_MARKERS + RECONCILIATION_MARKERS + FROM_PLAN_MARKERS + MEMORY_MARKERS + REPO_MAP_MARKERS + DELEGATION_MARKERS:
            present_in = [p for p in platforms if marker in generated[p]["content"]]
            if len(present_in) != len(platforms):
                missing = set(platforms) - set(present_in)
                err = f"  '{marker}' missing from: {', '.join(missing)}"
                print(f"  FAIL: {err}")
                consistency_errors.append(err)

        all_errors.extend(consistency_errors)
        if not consistency_errors:
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
