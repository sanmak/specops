"""Verify that all generated platform outputs contain consistent content.

Checks that all platforms include the same:
- Workflow phases (Understand, Spec, Implement, Complete)
- Safety rules (convention sanitization, template safety, path containment)
- Spec templates (feature, bugfix, refactor, design, tasks)
- Vertical adaptation rules (infrastructure, data, library, frontend)
- Data handling rules
- Simplicity principle
"""

import os
import sys

PLATFORMS_DIR = "platforms"

# Map of platform name -> generated output file
PLATFORM_FILES = {
    "claude": "SKILL.md",
    "cursor": "specops.mdc",
    "codex": "SKILL.md",
    "copilot": "specops.instructions.md",
}

# Markers that MUST be present in every platform output
REQUIRED_MARKERS = {
    "workflow": [
        "Phase 1: Understand Context",
        "Phase 2: Create Specification",
        "Phase 3: Implement",
        "Phase 4: Complete",
        "Version Display",
        "Version Extraction Protocol",
    ],
    "safety": [
        "Convention Sanitization",
        "meta-instructions",
        "Template File Safety",
        "fall back to the default template",
        "Path Containment",
        "path traversal",
    ],
    "templates": [
        "Feature: [Title]",
        "Bug Fix: [Title]",
        "Refactor: [Title]",
        "Design: [Title]",
        "Implementation Tasks: [Title]",
        "Implementation Journal: [Title]",
    ],
    "verticals": [
        "### infrastructure",
        "### data",
        "### library",
        "### frontend",
        "### builder",
    ],
    "simplicity": [
        "Simplicity Principle",
        "No premature abstractions",
        "Over-Engineering",
    ],
    "data_handling": [
        "Secrets and Credentials",
        "Personal Data (PII)",
        "Data Classification",
    ],
    "review_workflow": [
        "spec.json",
        "reviews.md",
        "review mode",
        "revision mode",
        "Self-review mode",
        "Implementation gate",
        "Status Dashboard",
    ],
    "view": [
        "Spec Viewing",
        "View/List Mode Detection",
        "List Specs",
        "View: Summary",
        "View: Full",
        "View: Walkthrough",
        "View: Status",
    ],
    "update": [
        "Update Mode",
        "Update Mode Detection",
        "Detect Current Version",
        "Check Latest Available Version",
        "Detect Installation Method",
    ],
    "steering": [
        "## Steering Files",
        "Steering File Format",
        "Inclusion Modes",
        "fileMatch",
        "Loading Procedure",
        "Foundation File Templates",
        "product.md",
        "tech.md",
        "structure.md",
    ],
    "reconciliation": [
        "## Audit Mode",
        "## Reconcile Mode",
        "### File Drift",
        "### Post-Completion Modification",
        "### Task Status Inconsistency",
        "### Staleness",
        "### Cross-Spec Conflicts",
        "### Health Summary",
        "### Audit Report",
    ],
    "from_plan": [
        "# From Plan Mode",
        "From Plan mode",
        "Faithful Conversion",
        "from-plan",
        "Parse the plan",
    ],
    "memory": [
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
    ],
    "external_tracking": [
        "Issue Creation Timing",
        "Issue Creation Protocol",
        "Graceful Degradation",
        "Status Sync",
        "Commit Linking",
        "IssueID",
        "Task tracking gate",
        "attempted creation",
    ],
    "repo_map": [
        "## Repo Map",
        "### Repo Map Format",
        "### Repo Map Generation",
        "### Language Tier Extraction",
        "### Staleness Detection",
        "### Scope Control",
        "### Map Subcommand",
        "### Repo Map Safety",
        "### Platform Adaptation",
    ],
    "writing_quality": [
        "## Writing Quality",
        "### Structure and Order",
        "### Precision and Testability",
        "### Clarity and Conciseness",
        "### Audience Awareness",
        "### Collaborative Voice",
        "### Self-Check",
        "### Sources",
        "ANT test",
        "active voice",
    ],
    "feedback": [
        "## Feedback Mode",
        "Feedback Mode Detection",
        "Interactive Feedback Workflow",
        "Non-Interactive Feedback Workflow",
        "Issue Composition",
        "Privacy Safety Rules",
        "### Submission",
        "Feedback Graceful Degradation",
        "sanmak/specops",
    ],
}


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    errors = 0

    # Load all platform outputs
    platform_contents = {}
    for platform, filename in PLATFORM_FILES.items():
        filepath = os.path.join(PLATFORMS_DIR, platform, filename)
        if not os.path.exists(filepath):
            print(f"SKIP: {filepath} not found (run generator/generate.py --all first)")
            continue
        platform_contents[platform] = read_file(filepath)

    if len(platform_contents) < 2:
        print("Need at least 2 platform outputs to check consistency")
        sys.exit(1)

    # Check required markers in each platform
    for category, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            present_in = []
            missing_from = []
            for platform, content in platform_contents.items():
                if marker in content:
                    present_in.append(platform)
                else:
                    missing_from.append(platform)

            if missing_from:
                print(f"FAIL: [{category}] '{marker}' missing from: {', '.join(missing_from)}")
                errors += 1

    # Cross-platform consistency: check that no platform is missing an entire category
    for category, markers in REQUIRED_MARKERS.items():
        for platform, content in platform_contents.items():
            found = sum(1 for m in markers if m in content)
            if found == 0:
                print(f"FAIL: Platform '{platform}' has no markers from category '{category}'")
                errors += 1
            elif found < len(markers):
                missing = [m for m in markers if m not in content]
                print(f"WARN: Platform '{platform}' missing {len(missing)}/{len(markers)} markers from '{category}'")

    if errors > 0:
        print(f"\n{errors} consistency error(s) found")
        sys.exit(1)
    else:
        print(f"\nPASS: All {len(platform_contents)} platform outputs are consistent")


if __name__ == "__main__":
    main()
