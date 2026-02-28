"""Test that schema.json correctly rejects invalid configuration values.

These tests verify the hardening constraints: path validation, maxLength,
maxItems, and additionalProperties enforcement.
"""

import json
import sys

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


def load_schema():
    with open("schema.json") as f:
        return json.load(f)


def expect_valid(schema, config, description):
    """Assert that config validates successfully."""
    try:
        validate(instance=config, schema=schema)
        print(f"PASS: {description}")
        return True
    except ValidationError as e:
        print(f"FAIL: {description} - expected valid but got: {e.message}")
        return False


def expect_invalid(schema, config, description):
    """Assert that config fails validation."""
    try:
        validate(instance=config, schema=schema)
        print(f"FAIL: {description} - expected rejection but config was accepted")
        return False
    except ValidationError:
        print(f"PASS: {description}")
        return True


def main():
    schema = load_schema()
    passed = 0
    failed = 0

    def check(result):
        nonlocal passed, failed
        if result:
            passed += 1
        else:
            failed += 1

    # --- Valid configs ---
    check(expect_valid(schema, {"specsDir": ".specops"}, "Minimal config is valid"))
    check(expect_valid(schema, {"specsDir": "specs/output"}, "specsDir with subdirectory is valid"))
    check(expect_valid(schema, {
        "specsDir": ".specops",
        "team": {"conventions": ["Use camelCase", "All APIs need input validation"]}
    }, "Config with conventions is valid"))

    # --- specsDir path validation ---
    check(expect_invalid(schema, {"specsDir": "/etc/passwd"}, "Rejects absolute path in specsDir"))
    check(expect_invalid(schema, {"specsDir": "../../../etc"}, "Rejects path traversal in specsDir"))
    check(expect_invalid(schema, {"specsDir": "a" * 201}, "Rejects specsDir exceeding maxLength"))
    check(expect_invalid(schema, {"specsDir": "path with spaces"}, "Rejects specsDir with spaces"))

    # --- String maxLength ---
    check(expect_invalid(schema, {
        "templates": {"feature": "a" * 101}
    }, "Rejects template name exceeding maxLength"))
    check(expect_invalid(schema, {
        "team": {"taskPrefix": "a" * 21}
    }, "Rejects taskPrefix exceeding maxLength"))
    check(expect_invalid(schema, {
        "implementation": {"testFramework": "a" * 51}
    }, "Rejects testFramework exceeding maxLength"))
    check(expect_invalid(schema, {
        "integrations": {"ci": "a" * 51}
    }, "Rejects integration string exceeding maxLength"))

    # --- Convention constraints ---
    check(expect_invalid(schema, {
        "team": {"conventions": ["a" * 501]}
    }, "Rejects convention string exceeding maxLength"))
    check(expect_invalid(schema, {
        "team": {"conventions": ["convention"] * 31}
    }, "Rejects conventions array exceeding maxItems"))

    # --- additionalProperties enforcement ---
    check(expect_invalid(schema, {
        "unknownField": "value"
    }, "Rejects unknown root-level property"))
    check(expect_invalid(schema, {
        "templates": {"feature": "default", "unknownTemplate": "value"}
    }, "Rejects unknown property in templates"))
    check(expect_invalid(schema, {
        "team": {"conventions": [], "unknownField": "value"}
    }, "Rejects unknown property in team"))
    check(expect_invalid(schema, {
        "team": {"codeReview": {"required": True, "unknownField": "value"}}
    }, "Rejects unknown property in team.codeReview"))
    check(expect_invalid(schema, {
        "implementation": {"autoCommit": False, "unknownField": "value"}
    }, "Rejects unknown property in implementation"))
    check(expect_invalid(schema, {
        "implementation": {"linting": {"enabled": True, "unknownField": "value"}}
    }, "Rejects unknown property in implementation.linting"))
    check(expect_invalid(schema, {
        "implementation": {"formatting": {"enabled": True, "unknownField": "value"}}
    }, "Rejects unknown property in implementation.formatting"))
    check(expect_invalid(schema, {
        "integrations": {"ci": "github-actions", "unknownField": "value"}
    }, "Rejects unknown property in integrations"))

    # --- Module constraints ---
    check(expect_invalid(schema, {
        "modules": {"frontend": {"specsDir": "../../../etc"}}
    }, "Rejects path traversal in module specsDir"))
    check(expect_invalid(schema, {
        "modules": {"frontend": {"conventions": ["a" * 501]}}
    }, "Rejects module convention exceeding maxLength"))
    check(expect_invalid(schema, {
        "modules": {"frontend": {"conventions": ["c"] * 31}}
    }, "Rejects module conventions exceeding maxItems"))
    check(expect_invalid(schema, {
        "modules": {"frontend": {"unknownField": "value"}}
    }, "Rejects unknown property in module"))

    # --- Summary ---
    print(f"\n{passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
