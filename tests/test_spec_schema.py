"""Validate spec-schema.json and index-schema.json are well-formed and test examples against them."""

import json
import sys

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


def load_schema(path):
    with open(path) as f:
        return json.load(f)


def expect_valid(schema, instance, description):
    """Assert that instance validates successfully."""
    try:
        validate(instance=instance, schema=schema)
        print(f"PASS: {description}")
        return True
    except ValidationError as e:
        print(f"FAIL: {description} - {e.message}")
        return False


def expect_invalid(schema, instance, description):
    """Assert that instance fails validation."""
    try:
        validate(instance=instance, schema=schema)
        print(f"FAIL: {description} - expected rejection but was accepted")
        return False
    except ValidationError:
        print(f"PASS: {description}")
        return True


def main():
    passed = 0
    failed = 0

    def check(result):
        nonlocal passed, failed
        if result:
            passed += 1
        else:
            failed += 1

    # --- Validate schemas are well-formed ---
    print("--- Schema Well-Formedness ---")
    for schema_file in ["spec-schema.json", "index-schema.json"]:
        try:
            schema = load_schema(schema_file)
            Draft7Validator.check_schema(schema)
            print(f"PASS: {schema_file} is a valid JSON Schema")
            passed += 1
        except Exception as e:
            print(f"FAIL: {schema_file} is not a valid JSON Schema - {e}")
            failed += 1

    # --- spec-schema.json tests ---
    print("\n--- spec.json Validation ---")
    spec_schema = load_schema("spec-schema.json")

    # Valid minimal spec.json
    check(expect_valid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Minimal valid spec.json"))

    # Valid full spec.json
    check(expect_valid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "approved",
        "version": 2,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-02T14:30:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [
            {
                "name": "Bob",
                "email": "bob@acme.com",
                "status": "approved",
                "reviewedAt": "2026-03-02T12:00:00Z",
                "round": 2
            },
            {
                "name": "Carol",
                "email": "carol@acme.com",
                "status": "approved",
                "reviewedAt": "2026-03-02T14:00:00Z",
                "round": 2
            }
        ],
        "reviewRounds": 2,
        "approvals": 2,
        "requiredApprovals": 2
    }, "Full valid spec.json with reviewers"))

    # Invalid: missing required field
    check(expect_invalid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z"
    }, "Rejects spec.json missing author"))

    # Invalid: bad status enum
    check(expect_invalid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "pending",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects invalid status value"))

    # Invalid: bad type enum
    check(expect_invalid(spec_schema, {
        "id": "user-auth",
        "type": "hotfix",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects invalid type value"))

    # Invalid: version < 1
    check(expect_invalid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "draft",
        "version": 0,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects version < 1"))

    # Invalid: id with special characters
    check(expect_invalid(spec_schema, {
        "id": "user auth!@#",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects id with special characters"))

    # Invalid: additional properties
    check(expect_invalid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1,
        "unknownField": "value"
    }, "Rejects additional properties in spec.json"))

    # Invalid: reviewer with additional properties
    check(expect_invalid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [{"name": "Bob", "email": "bob@acme.com", "status": "pending", "reviewedAt": "", "round": 1, "extra": "bad"}],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects additional properties in reviewer"))

    # Valid: self-approved status with selfApproval reviewer flag
    check(expect_valid(spec_schema, {
        "id": "solo-feature",
        "type": "feature",
        "status": "self-approved",
        "version": 1,
        "created": "2026-03-05T10:00:00Z",
        "updated": "2026-03-05T11:30:00Z",
        "author": {"name": "Solo Dev", "email": "solo@dev.com"},
        "reviewers": [
            {
                "name": "Solo Dev",
                "email": "solo@dev.com",
                "status": "approved",
                "selfApproval": True,
                "reviewedAt": "2026-03-05T11:30:00Z",
                "round": 1
            }
        ],
        "reviewRounds": 1,
        "approvals": 1,
        "requiredApprovals": 1
    }, "Valid self-approved spec with selfApproval reviewer flag"))

    # Valid: peer-approved spec without selfApproval flag (backward compat)
    check(expect_valid(spec_schema, {
        "id": "team-feature",
        "type": "feature",
        "status": "approved",
        "version": 1,
        "created": "2026-03-05T10:00:00Z",
        "updated": "2026-03-05T11:30:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [
            {
                "name": "Bob",
                "email": "bob@acme.com",
                "status": "approved",
                "reviewedAt": "2026-03-05T11:30:00Z",
                "round": 1
            }
        ],
        "reviewRounds": 1,
        "approvals": 1,
        "requiredApprovals": 1
    }, "Valid peer-approved spec without selfApproval flag (backward compat)"))

    # --- Validate example spec.json ---
    print("\n--- Example spec.json Validation ---")
    try:
        with open("examples/specs/feature-user-authentication/spec.json") as f:
            example_spec = json.load(f)
        check(expect_valid(spec_schema, example_spec, "Example spec.json validates against spec-schema.json"))
    except FileNotFoundError:
        print("SKIP: Example spec.json not yet created")

    try:
        with open("examples/specs/feature-task-management-saas/spec.json") as f:
            builder_spec = json.load(f)
        check(expect_valid(spec_schema, builder_spec, "Builder example spec.json validates against spec-schema.json"))
    except FileNotFoundError:
        print("SKIP: Builder example spec.json not yet created")

    try:
        with open("examples/specs/feature-self-approved-example/spec.json") as f:
            self_approved_spec = json.load(f)
        check(expect_valid(spec_schema, self_approved_spec, "Self-approved example spec.json validates against spec-schema.json"))
    except FileNotFoundError:
        print("SKIP: Self-approved example spec.json not yet created")

    # Valid: spec with specopsCreatedWith and specopsUpdatedWith
    check(expect_valid(spec_schema, {
        "id": "versioned-feature",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-07T10:00:00Z",
        "updated": "2026-03-07T10:00:00Z",
        "specopsCreatedWith": "1.2.0",
        "specopsUpdatedWith": "1.2.0",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Valid spec.json with specopsCreatedWith and specopsUpdatedWith"))

    # Valid: spec without specopsCreatedWith (backward compat)
    check(expect_valid(spec_schema, {
        "id": "legacy-feature",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Valid spec.json without specops version fields (backward compat)"))

    # Invalid: bad semver format for specopsCreatedWith
    check(expect_invalid(spec_schema, {
        "id": "bad-version",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-07T10:00:00Z",
        "updated": "2026-03-07T10:00:00Z",
        "specopsCreatedWith": "v1.2.0",
        "author": {"name": "Alice", "email": "alice@acme.com"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects specopsCreatedWith with 'v' prefix"))

    # Invalid: malformed timestamp in created
    check(expect_invalid(spec_schema, {
        "id": "bad-ts",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "not-a-date",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"}
    }, "Rejects malformed timestamp in created"))

    # Invalid: date-only (missing time component)
    check(expect_invalid(spec_schema, {
        "id": "bad-ts2",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice", "email": "alice@acme.com"}
    }, "Rejects date-only timestamp (missing time component)"))

    # Valid: timestamp with timezone offset
    check(expect_valid(spec_schema, {
        "id": "tz-offset",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00+05:30",
        "updated": "2026-03-01T10:00:00-04:00",
        "author": {"name": "Alice", "email": "alice@acme.com"}
    }, "Valid timestamps with timezone offsets"))

    # --- index-schema.json tests ---
    print("\n--- index.json Validation ---")
    index_schema = load_schema("index-schema.json")

    # Valid index
    check(expect_valid(index_schema, [
        {
            "id": "user-auth",
            "type": "feature",
            "status": "approved",
            "version": 2,
            "author": "Alice",
            "updated": "2026-03-02T14:30:00Z"
        },
        {
            "id": "bugfix-checkout",
            "type": "bugfix",
            "status": "implementing",
            "version": 1,
            "author": "Bob",
            "updated": "2026-03-01T10:00:00Z"
        }
    ], "Valid index.json array"))

    # Valid: self-approved status in index
    check(expect_valid(index_schema, [
        {
            "id": "solo-feature",
            "type": "feature",
            "status": "self-approved",
            "version": 1,
            "author": "Solo Dev",
            "updated": "2026-03-05T11:30:00Z"
        }
    ], "Valid index with self-approved status"))

    # Valid empty index
    check(expect_valid(index_schema, [], "Empty index.json is valid"))

    # Invalid: malformed timestamp in index entry
    check(expect_invalid(index_schema, [
        {
            "id": "user-auth",
            "type": "feature",
            "status": "draft",
            "version": 1,
            "author": "Alice",
            "updated": "not-a-date"
        }
    ], "Rejects malformed timestamp in index entry"))

    # Invalid: bad status in index entry
    check(expect_invalid(index_schema, [
        {
            "id": "user-auth",
            "type": "feature",
            "status": "unknown",
            "version": 1,
            "author": "Alice",
            "updated": "2026-03-01"
        }
    ], "Rejects invalid status in index entry"))

    # Invalid: additional properties in index entry
    check(expect_invalid(index_schema, [
        {
            "id": "user-auth",
            "type": "feature",
            "status": "draft",
            "version": 1,
            "author": "Alice",
            "updated": "2026-03-01",
            "extra": "bad"
        }
    ], "Rejects additional properties in index entry"))

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"{passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
