"""Validate spec-schema.json and index-schema.json are well-formed and test examples against them."""

import glob
import json
import sys
from datetime import datetime

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

    # Valid minimal spec.json (no email — new default)
    check(expect_valid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Minimal valid spec.json (no email)"))

    # Valid full spec.json (no email)
    check(expect_valid(spec_schema, {
        "id": "user-auth",
        "type": "feature",
        "status": "approved",
        "version": 2,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-02T14:30:00Z",
        "author": {"name": "Alice"},
        "reviewers": [
            {
                "name": "Bob",
                "status": "approved",
                "reviewedAt": "2026-03-02T12:00:00Z",
                "round": 2
            },
            {
                "name": "Carol",
                "status": "approved",
                "reviewedAt": "2026-03-02T14:00:00Z",
                "round": 2
            }
        ],
        "reviewRounds": 2,
        "approvals": 2,
        "requiredApprovals": 2
    }, "Full valid spec.json with reviewers"))

    # Valid: requiredApprovals 0 for review-disabled projects
    check(expect_valid(spec_schema, {
        "id": "no-review",
        "type": "feature",
        "status": "completed",
        "version": 1,
        "created": "2026-03-07T10:00:00Z",
        "updated": "2026-03-07T12:00:00Z",
        "author": {"name": "Solo Dev"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 0
    }, "Valid spec.json with requiredApprovals 0 (review disabled)"))

    # Invalid: email field in author (PII prevention — email property removed from schema)
    # Payload is otherwise valid so rejection is clearly due to the email field
    check(expect_invalid(spec_schema, {
        "id": "email-leak",
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
    }, "Rejects author with email field (PII prevention)"))

    # Invalid: email field in reviewer (PII prevention)
    # Payload is otherwise valid so rejection is clearly due to the email field
    check(expect_invalid(spec_schema, {
        "id": "email-leak-reviewer",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice"},
        "reviewers": [{"name": "Bob", "email": "bob@acme.com", "status": "approved"}],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 1
    }, "Rejects reviewer with email field (PII prevention)"))

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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
        "reviewers": [{"name": "Bob", "status": "pending", "reviewedAt": "", "round": 1, "extra": "bad"}],
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
        "author": {"name": "Solo Dev"},
        "reviewers": [
            {
                "name": "Solo Dev",
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
        "author": {"name": "Alice"},
        "reviewers": [
            {
                "name": "Bob",
                "status": "approved",
                "reviewedAt": "2026-03-05T11:30:00Z",
                "round": 1
            }
        ],
        "reviewRounds": 1,
        "approvals": 1,
        "requiredApprovals": 1
    }, "Valid peer-approved spec without selfApproval flag"))

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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"},
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
        "author": {"name": "Alice"}
    }, "Rejects malformed timestamp in created"))

    # Invalid: date-only (missing time component)
    check(expect_invalid(spec_schema, {
        "id": "bad-ts2",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01",
        "updated": "2026-03-01T10:00:00Z",
        "author": {"name": "Alice"}
    }, "Rejects date-only timestamp (missing time component)"))

    # Valid: timestamp with timezone offset
    check(expect_valid(spec_schema, {
        "id": "tz-offset",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-01T10:00:00+05:30",
        "updated": "2026-03-01T10:00:00-04:00",
        "author": {"name": "Alice"}
    }, "Valid timestamps with timezone offsets"))

    # --- Metrics object tests ---
    print("\n--- Metrics Object Validation ---")

    # Valid: spec with full metrics object
    check(expect_valid(spec_schema, {
        "id": "metrics-full",
        "type": "feature",
        "status": "completed",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "author": {"name": "Alice"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 0,
        "metrics": {
            "specArtifactTokensEstimate": 4200,
            "filesChanged": 12,
            "linesAdded": 340,
            "linesRemoved": 45,
            "tasksCompleted": 5,
            "acceptanceCriteriaVerified": 18,
            "specDurationMinutes": 120
        }
    }, "Valid spec.json with full metrics object"))

    # Valid: spec without metrics (backward compat)
    check(expect_valid(spec_schema, {
        "id": "no-metrics",
        "type": "feature",
        "status": "completed",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "author": {"name": "Alice"},
        "reviewers": [],
        "reviewRounds": 0,
        "approvals": 0,
        "requiredApprovals": 0
    }, "Valid spec.json without metrics (backward compat)"))

    # Invalid: extra property in metrics object
    check(expect_invalid(spec_schema, {
        "id": "metrics-extra",
        "type": "feature",
        "status": "completed",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "author": {"name": "Alice"},
        "metrics": {
            "specArtifactTokensEstimate": 4200,
            "unknownMetric": 99
        }
    }, "Rejects additional properties in metrics object"))

    # Invalid: negative metric value
    check(expect_invalid(spec_schema, {
        "id": "metrics-negative",
        "type": "feature",
        "status": "completed",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "author": {"name": "Alice"},
        "metrics": {
            "filesChanged": -1
        }
    }, "Rejects negative metric value"))

    # --- Timestamp ordering tests ---
    print("\n--- Timestamp Ordering Validation ---")

    def parse_ts(ts_str):
        """Parse ISO 8601 timestamp to datetime for comparison."""
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)

    def check_timestamp_ordering(spec_path):
        """Verify timestamp ordering invariants in a spec.json."""
        with open(spec_path) as f:
            spec = json.load(f)
        created = spec.get("created")
        updated = spec.get("updated")
        try:
            created_ts = parse_ts(created) if created else None
            updated_ts = parse_ts(updated) if updated else None
        except ValueError as e:
            print(f"FAIL: {spec_path} - invalid timestamp ({e})")
            return False
        if created_ts and updated_ts:
            if updated_ts < created_ts:
                print(f"FAIL: {spec_path} - updated < created ({updated} < {created})")
                return False
        for reviewer in spec.get("reviewers", []):
            reviewed_at = reviewer.get("reviewedAt")
            try:
                reviewed_at_ts = parse_ts(reviewed_at) if reviewed_at else None
            except ValueError as e:
                print(f"FAIL: {spec_path} - invalid reviewedAt ({e})")
                return False
            if reviewed_at_ts and created_ts:
                if reviewed_at_ts < created_ts:
                    print(f"FAIL: {spec_path} - reviewedAt < created ({reviewed_at} < {created})")
                    return False
            if reviewed_at_ts and updated_ts:
                if updated_ts < reviewed_at_ts:
                    print(f"FAIL: {spec_path} - updated < reviewedAt ({updated} < {reviewed_at})")
                    return False
        print(f"PASS: {spec_path} - timestamp ordering valid")
        return True

    for spec_file in sorted(glob.glob("examples/specs/*/spec.json")):
        check(check_timestamp_ordering(spec_file))

    for spec_file in sorted(glob.glob(".specops/**/spec.json", recursive=True)):
        check(check_timestamp_ordering(spec_file))

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

    # --- partOf field tests ---
    print("\n--- partOf Field Validation ---")

    # Valid: spec with partOf
    check(expect_valid(spec_schema, {
        "id": "child-spec",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "partOf": "my-initiative"
    }, "Valid spec.json with partOf"))

    # Valid: partOf with dots and numbers
    check(expect_valid(spec_schema, {
        "id": "child-spec-2",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "partOf": "init.1"
    }, "Valid spec.json with partOf using dots and numbers"))

    # Invalid: partOf with path traversal
    check(expect_invalid(spec_schema, {
        "id": "hack-spec",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "partOf": "../hack"
    }, "Rejects partOf with path traversal"))

    # Invalid: partOf empty string
    check(expect_invalid(spec_schema, {
        "id": "empty-partof",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "partOf": ""
    }, "Rejects partOf with empty string"))

    # Invalid: partOf too long
    check(expect_invalid(spec_schema, {
        "id": "long-partof",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "partOf": "a" * 101
    }, "Rejects partOf exceeding maxLength"))

    # --- relatedSpecs field tests ---
    print("\n--- relatedSpecs Field Validation ---")

    # Valid: spec with relatedSpecs
    check(expect_valid(spec_schema, {
        "id": "related-spec",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "relatedSpecs": ["spec-a", "spec-b", "spec.c"]
    }, "Valid spec.json with relatedSpecs"))

    # Valid: empty relatedSpecs array
    check(expect_valid(spec_schema, {
        "id": "no-related",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "relatedSpecs": []
    }, "Valid spec.json with empty relatedSpecs"))

    # Invalid: relatedSpecs exceeds maxItems (>20)
    check(expect_invalid(spec_schema, {
        "id": "too-many-related",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "relatedSpecs": [f"spec-{i}" for i in range(21)]
    }, "Rejects relatedSpecs exceeding maxItems (>20)"))

    # Invalid: relatedSpecs with bad pattern
    check(expect_invalid(spec_schema, {
        "id": "bad-related",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "relatedSpecs": ["../hack"]
    }, "Rejects relatedSpecs with path traversal pattern"))

    # --- specDependencies field tests ---
    print("\n--- specDependencies Field Validation ---")

    # Valid: specDependencies with required field
    check(expect_valid(spec_schema, {
        "id": "dep-spec",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": [
            {
                "specId": "auth-service",
                "reason": "Needs auth API contract",
                "required": True,
                "contractRef": "docs/auth-api.md"
            }
        ]
    }, "Valid spec.json with specDependencies (all fields)"))

    # Valid: specDependencies without optional required field
    check(expect_valid(spec_schema, {
        "id": "dep-spec-minimal",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": [
            {
                "specId": "data-layer",
                "reason": "Depends on data model"
            }
        ]
    }, "Valid spec.json with specDependencies (required fields only)"))

    # Valid: empty specDependencies array
    check(expect_valid(spec_schema, {
        "id": "no-deps",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": []
    }, "Valid spec.json with empty specDependencies"))

    # Invalid: specDependencies with bad specId pattern
    check(expect_invalid(spec_schema, {
        "id": "bad-dep-id",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": [
            {
                "specId": "../hack",
                "reason": "Malicious dependency"
            }
        ]
    }, "Rejects specDependencies with bad specId pattern"))

    # Invalid: specDependencies exceeds maxItems (>50)
    check(expect_invalid(spec_schema, {
        "id": "too-many-deps",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": [
            {"specId": f"dep-{i}", "reason": f"Reason {i}"} for i in range(51)
        ]
    }, "Rejects specDependencies exceeding maxItems (>50)"))

    # Invalid: specDependencies with extra properties (additionalProperties: false)
    check(expect_invalid(spec_schema, {
        "id": "extra-dep-props",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": [
            {
                "specId": "auth-service",
                "reason": "Needs auth API",
                "extraField": "should fail"
            }
        ]
    }, "Rejects specDependencies with additional properties"))

    # Invalid: specDependencies missing required specId
    check(expect_invalid(spec_schema, {
        "id": "missing-specid",
        "type": "feature",
        "status": "draft",
        "version": 1,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": {"name": "Alice"},
        "specDependencies": [
            {
                "reason": "Missing specId"
            }
        ]
    }, "Rejects specDependencies missing required specId"))

    # --- Backward compatibility ---
    print("\n--- Decomposition Backward Compatibility ---")

    # Valid: existing spec without any new fields still validates
    check(expect_valid(spec_schema, {
        "id": "legacy-spec",
        "type": "bugfix",
        "status": "implementing",
        "version": 3,
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-15T14:00:00Z",
        "author": {"name": "Bob"},
        "reviewers": [
            {
                "name": "Carol",
                "status": "approved",
                "reviewedAt": "2026-03-10T12:00:00Z",
                "round": 1
            }
        ],
        "reviewRounds": 1,
        "approvals": 1,
        "requiredApprovals": 1
    }, "Existing spec without new fields still validates (backward compat)"))

    # Valid: spec with all three new fields combined
    check(expect_valid(spec_schema, {
        "id": "full-decomp",
        "type": "feature",
        "status": "implementing",
        "version": 2,
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "author": {"name": "Alice"},
        "partOf": "my-initiative",
        "relatedSpecs": ["sibling-spec-a", "sibling-spec-b"],
        "specDependencies": [
            {
                "specId": "auth-service",
                "reason": "Needs auth API contract",
                "required": True
            }
        ]
    }, "Valid spec.json with all three decomposition fields"))

    # --- Index partOf field tests ---
    print("\n--- Index partOf Field Validation ---")

    # Valid: index entry with partOf
    check(expect_valid(index_schema, [
        {
            "id": "child-spec",
            "type": "feature",
            "status": "implementing",
            "version": 1,
            "author": "Alice",
            "updated": "2026-03-20T10:00:00Z",
            "partOf": "my-initiative"
        }
    ], "Valid index entry with partOf"))

    # Valid: index entry without partOf (backward compat)
    check(expect_valid(index_schema, [
        {
            "id": "standalone-spec",
            "type": "feature",
            "status": "draft",
            "version": 1,
            "author": "Alice",
            "updated": "2026-03-20T10:00:00Z"
        }
    ], "Valid index entry without partOf (backward compat)"))

    # Invalid: index entry with bad partOf pattern
    check(expect_invalid(index_schema, [
        {
            "id": "bad-index-partof",
            "type": "feature",
            "status": "draft",
            "version": 1,
            "author": "Alice",
            "updated": "2026-03-20T10:00:00Z",
            "partOf": "../hack"
        }
    ], "Rejects index entry with bad partOf pattern"))

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"{passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
