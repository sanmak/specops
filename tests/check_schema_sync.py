"""Validate that schema.json is well-formed and follows SpecOps conventions.

Checks:
- Valid JSON Schema structure
- All objects use "additionalProperties": false
- All strings have maxLength
- All arrays have maxItems
- Required top-level properties exist
"""

import json
import sys


def check_constraints(obj, path=""):
    """Recursively check schema constraints."""
    errors = []

    if "properties" in obj:
        for key, value in obj["properties"].items():
            full_path = f"{path}.{key}" if path else key

            # Skip $schema key
            if key == "$schema":
                continue

            prop_type = value.get("type")

            # Strings must have maxLength
            if prop_type == "string" and "maxLength" not in value and "enum" not in value:
                errors.append(f"  Missing maxLength on string: {full_path}")

            # Arrays must have maxItems
            if prop_type == "array" and "maxItems" not in value:
                errors.append(f"  Missing maxItems on array: {full_path}")

            # Recurse into objects
            if prop_type == "object":
                errors.extend(check_constraints(value, full_path))

    # Objects must have additionalProperties: false
    if obj.get("type") == "object" and "additionalProperties" not in obj:
        errors.append(f"  Missing additionalProperties on object: {path or 'root'}")
    elif obj.get("type") == "object" and obj.get("additionalProperties") is not False:
        errors.append(f"  additionalProperties must be false on: {path or 'root'}")

    # Check patternProperties objects
    if "patternProperties" in obj:
        for pattern, value in obj["patternProperties"].items():
            pp_path = f"{path}[{pattern}]" if path else f"[{pattern}]"
            if value.get("type") == "object":
                errors.extend(check_constraints(value, pp_path))

    return errors


def main():
    try:
        with open("schema.json") as f:
            schema = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot load schema.json: {e}")
        sys.exit(1)

    errors = []

    # Check it's a valid JSON Schema
    if schema.get("type") != "object":
        errors.append("  schema.json root must be type 'object'")

    if "properties" not in schema:
        errors.append("  schema.json must have 'properties'")

    # Check required top-level properties exist
    required_props = ["specsDir", "vertical", "templates", "team", "implementation"]
    for prop in required_props:
        if prop not in schema.get("properties", {}):
            errors.append(f"  Missing required property: {prop}")

    # Check constraints recursively
    errors.extend(check_constraints(schema))

    if errors:
        print("Schema validation FAILED:")
        for err in errors:
            print(f"  {err}")
        print(f"\n{len(errors)} error(s) found")
        sys.exit(1)
    else:
        print("PASS: schema.json is well-formed and follows conventions")


if __name__ == "__main__":
    main()
