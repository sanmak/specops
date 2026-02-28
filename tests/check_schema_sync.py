"""Verify that schema.json and all platform skill.json files define the same configuration shape.

The configuration schema in skill.json must stay in sync with schema.json.
This script compares the property structures to detect drift across all platforms.
"""

import json
import os
import sys


def extract_properties(obj, path=""):
    """Recursively extract property names and their types from a schema object."""
    results = {}
    if "properties" in obj:
        for key, value in obj["properties"].items():
            full_path = f"{path}.{key}" if path else key
            results[full_path] = {
                "type": value.get("type"),
                "enum": value.get("enum"),
                "additionalProperties": value.get("additionalProperties"),
            }
            if value.get("type") == "object":
                results.update(extract_properties(value, full_path))
    if "patternProperties" in obj:
        for pattern, value in obj["patternProperties"].items():
            full_path = f"{path}[{pattern}]" if path else f"[{pattern}]"
            results[full_path] = {
                "type": value.get("type"),
                "additionalProperties": value.get("additionalProperties"),
            }
            if value.get("type") == "object":
                results.update(extract_properties(value, full_path))
    return results


def check_sync(schema_props, skill_path, skill_props):
    """Check sync between schema.json and a skill.json file."""
    errors = 0

    # Check for properties in schema.json but not in skill.json
    for key in sorted(schema_props.keys()):
        if key not in skill_props:
            print(f"DRIFT: '{key}' exists in schema.json but not in {skill_path}")
            errors += 1

    # Check for properties in skill.json but not in schema.json
    for key in sorted(skill_props.keys()):
        if key not in schema_props:
            print(f"DRIFT: '{key}' exists in {skill_path} but not in schema.json")
            errors += 1

    # Check matching properties have same type
    for key in sorted(set(schema_props.keys()) & set(skill_props.keys())):
        if schema_props[key].get("type") != skill_props[key].get("type"):
            print(f"DRIFT: '{key}' type mismatch - schema.json: {schema_props[key].get('type')}, {skill_path}: {skill_props[key].get('type')}")
            errors += 1

    return errors


def main():
    with open("schema.json") as f:
        schema = json.load(f)

    schema_props = extract_properties(schema)
    # Filter out $schema key from schema.json (not in skill.json)
    schema_props = {k: v for k, v in schema_props.items() if not k.startswith("$schema")}

    # All skill.json files to check (legacy + platform-specific)
    skill_files = [
        "skills/specops/skill.json",
        "platforms/claude/skill.json",
    ]

    total_errors = 0

    for skill_path in skill_files:
        if not os.path.exists(skill_path):
            print(f"SKIP: {skill_path} not found")
            continue

        with open(skill_path) as f:
            skill = json.load(f)

        skill_schema = skill.get("configuration", {}).get("schema", {})
        skill_props = extract_properties({"properties": skill_schema})

        errors = check_sync(schema_props, skill_path, skill_props)
        if errors == 0:
            print(f"PASS: schema.json and {skill_path} are in sync")
        total_errors += errors

    if total_errors > 0:
        print(f"\n{total_errors} sync error(s) found")
        sys.exit(1)
    else:
        print("\nAll schema files are in sync")


if __name__ == "__main__":
    main()
