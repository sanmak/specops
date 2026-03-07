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
        "examples/.specops.builder.json",
        "examples/.specops.solo-review.json",
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

    # Test _installedVersion and _installedAt fields
    print("\n--- Version Metadata Fields ---")
    config_with_version = {
        "specsDir": ".specops",
        "_installedVersion": "1.2.0",
        "_installedAt": "2026-03-07T10:00:00Z"
    }
    try:
        validate(instance=config_with_version, schema=schema)
        print("PASS: Config with _installedVersion and _installedAt validates")
    except ValidationError as e:
        print(f"FAIL: Config with version metadata rejected - {e.message}")
        errors += 1

    # Bad semver format
    config_bad_version = {
        "specsDir": ".specops",
        "_installedVersion": "v1.2.0"
    }
    try:
        validate(instance=config_bad_version, schema=schema)
        print("FAIL: Config with 'v' prefix in _installedVersion should be rejected")
        errors += 1
    except ValidationError:
        print("PASS: Config with bad _installedVersion format rejected")

    if errors > 0:
        print(f"\n{errors} validation error(s) found")
        sys.exit(1)
    else:
        print("\nAll example configs validate successfully")


if __name__ == "__main__":
    main()
