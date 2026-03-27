"""Verify that all generated platform outputs contain consistent content.

Checks that all platforms include the same:
- Workflow phases (Understand, Spec, Implement, Complete)
- Safety rules (convention sanitization, template safety, path containment)
- Spec templates (feature, bugfix, refactor, design, tasks)
- Vertical adaptation rules (infrastructure, data, library, frontend)
- Data handling rules
- Simplicity principle

NOTE: Marker lists are imported from generator/validate.py (single source of truth).
Do NOT duplicate marker definitions here — add new markers to validate.py only.
"""

import os
import sys

# Import marker constants from validate.py (single source of truth)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generator"))
from validate import (  # noqa: E402
    COHERENCE_MARKERS,
    DATA_HANDLING_MARKERS,
    DECOMPOSITION_MARKERS,
    DELEGATION_MARKERS,
    DEPENDENCY_SAFETY_MARKERS,
    ENGINEERING_DISCIPLINE_MARKERS,
    EXTERNAL_TRACKING_MARKERS,
    FEEDBACK_MARKERS,
    FROM_PLAN_MARKERS,
    GIT_CHECKPOINT_MARKERS,
    INTERVIEW_MARKERS,
    ISSUE_BODY_MARKERS,
    LEARNINGS_MARKERS,
    MEMORY_MARKERS,
    METRICS_MARKERS,
    PIPELINE_MARKERS,
    PLAN_VALIDATION_MARKERS,
    RECONCILIATION_MARKERS,
    REGRESSION_MARKERS,
    REPO_MAP_MARKERS,
    REVIEW_MARKERS,
    RUN_LOGGING_MARKERS,
    SAFETY_MARKERS,
    SIMPLICITY_MARKERS,
    STEERING_MARKERS,
    TASK_TRACKING_MARKERS,
    TEMPLATE_MARKERS,
    UPDATE_MARKERS,
    VERTICAL_MARKERS,
    VIEW_MARKERS,
    WORKFLOW_MARKERS,
    WRITING_QUALITY_MARKERS,
)

PLATFORMS_DIR = "platforms"

# Map of platform name -> generated output file
PLATFORM_FILES = {
    "claude": "SKILL.md",
    "cursor": "specops.mdc",
    "codex": "SKILL.md",
    "copilot": "specops.instructions.md",
    "antigravity": "specops.md",
}

# All marker sets to check, keyed by category name.
# Imported from validate.py to maintain single source of truth.
REQUIRED_MARKERS = {
    "workflow": WORKFLOW_MARKERS,
    "safety": SAFETY_MARKERS,
    "templates": TEMPLATE_MARKERS,
    "verticals": VERTICAL_MARKERS,
    "simplicity": SIMPLICITY_MARKERS,
    "data_handling": DATA_HANDLING_MARKERS,
    "review_workflow": REVIEW_MARKERS,
    "view": VIEW_MARKERS,
    "update": UPDATE_MARKERS,
    "steering": STEERING_MARKERS,
    "reconciliation": RECONCILIATION_MARKERS,
    "from_plan": FROM_PLAN_MARKERS,
    "memory": MEMORY_MARKERS,
    "external_tracking": EXTERNAL_TRACKING_MARKERS,
    "repo_map": REPO_MAP_MARKERS,
    "writing_quality": WRITING_QUALITY_MARKERS,
    "feedback": FEEDBACK_MARKERS,
    "metrics": METRICS_MARKERS,
    "run_logging": RUN_LOGGING_MARKERS,
    "plan_validation": PLAN_VALIDATION_MARKERS,
    "git_checkpointing": GIT_CHECKPOINT_MARKERS,
    "pipeline": PIPELINE_MARKERS,
    "issue_body": ISSUE_BODY_MARKERS,
    "decomposition": DECOMPOSITION_MARKERS,
    "learnings": LEARNINGS_MARKERS,
    "interview": INTERVIEW_MARKERS,
    "task_tracking": TASK_TRACKING_MARKERS,
    "regression": REGRESSION_MARKERS,
    "coherence": COHERENCE_MARKERS,
    "delegation": DELEGATION_MARKERS,
    "engineering_discipline": ENGINEERING_DISCIPLINE_MARKERS,
    "dependency_safety": DEPENDENCY_SAFETY_MARKERS,
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
        if platform == "claude":
            # Load dispatcher + all mode files as combined content
            combined_parts = [read_file(filepath)]
            modes_dir = os.path.join(PLATFORMS_DIR, "claude", "modes")
            if os.path.isdir(modes_dir):
                for mode_file in sorted(os.listdir(modes_dir)):
                    if mode_file.endswith(".md"):
                        mode_path = os.path.join(modes_dir, mode_file)
                        combined_parts.append(read_file(mode_path))
            platform_contents[platform] = "\n".join(combined_parts)
        else:
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
