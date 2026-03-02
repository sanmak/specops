"""Validate example configuration files against schema.json."""

import json
import sys

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


def main():
    with open("schema.json") as f:
        schema = json.load(f)

    example_files = [
        "examples/.specops.json",
        "examples/.specops.minimal.json",
        "examples/.specops.full.json",
        "examples/.specops.review.json",
    ]

    errors = 0
    for filepath in example_files:
        try:
            with open(filepath) as f:
                config = json.load(f)
            validate(instance=config, schema=schema)
            print(f"PASS: {filepath} validates against schema")
        except ValidationError as e:
            print(f"FAIL: {filepath} - {e.message}")
            errors += 1
        except FileNotFoundError:
            print(f"FAIL: {filepath} - file not found")
            errors += 1

    if errors > 0:
        print(f"\n{errors} validation error(s) found")
        sys.exit(1)
    else:
        print("\nAll example configs validate successfully")


if __name__ == "__main__":
    main()
