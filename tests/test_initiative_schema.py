"""Validate initiative-schema.json is well-formed and test examples against it."""

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

    # --- Validate schema is well-formed ---
    print("--- Schema Well-Formedness ---")
    try:
        schema = load_schema("initiative-schema.json")
        Draft7Validator.check_schema(schema)
        print("PASS: initiative-schema.json is a valid JSON Schema")
        passed += 1
    except Exception as e:
        print(f"FAIL: initiative-schema.json is not a valid JSON Schema - {e}")
        failed += 1

    # --- Valid initiative tests ---
    print("\n--- Valid Initiative Validation ---")
    initiative_schema = load_schema("initiative-schema.json")

    # Valid: initiative with all required fields
    check(expect_valid(initiative_schema, {
        "id": "auth-overhaul",
        "title": "Authentication System Overhaul",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["auth-api", "auth-ui", "auth-migration"],
        "order": [["auth-api"], ["auth-ui", "auth-migration"]],
        "status": "active"
    }, "Valid initiative with all required fields"))

    # Valid: initiative with optional description
    check(expect_valid(initiative_schema, {
        "id": "payment-v2",
        "title": "Payment System v2",
        "description": "Complete rewrite of the payment processing pipeline with PCI compliance",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T12:00:00Z",
        "author": "Bob",
        "specs": ["payment-api", "payment-ui"],
        "order": [["payment-api"], ["payment-ui"]],
        "status": "active"
    }, "Valid initiative with optional description"))

    # Valid: initiative with optional skeleton
    check(expect_valid(initiative_schema, {
        "id": "search-feature",
        "title": "Full-Text Search Feature",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Carol",
        "specs": ["search-index", "search-api", "search-ui"],
        "order": [["search-index"], ["search-api"], ["search-ui"]],
        "skeleton": "search-index",
        "status": "active"
    }, "Valid initiative with optional skeleton"))

    # Valid: initiative with all optional fields
    check(expect_valid(initiative_schema, {
        "id": "full-initiative",
        "title": "Complete Initiative Example",
        "description": "An initiative demonstrating all fields",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-21T14:30:00Z",
        "author": "Dave",
        "specs": ["spec-a", "spec-b", "spec-c"],
        "order": [["spec-a"], ["spec-b", "spec-c"]],
        "skeleton": "spec-a",
        "status": "completed"
    }, "Valid initiative with all optional fields"))

    # Valid: completed initiative
    check(expect_valid(initiative_schema, {
        "id": "done-initiative",
        "title": "Completed Initiative",
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-20T16:00:00Z",
        "author": "Eve",
        "specs": ["done-spec-1"],
        "order": [["done-spec-1"]],
        "status": "completed"
    }, "Valid completed initiative"))

    # Valid: ID with dots, underscores, and numbers
    check(expect_valid(initiative_schema, {
        "id": "init.v2_phase-1",
        "title": "Initiative with complex ID",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Valid initiative with dots, underscores, and numbers in ID"))

    # --- Edge case tests ---
    print("\n--- Edge Case Validation ---")

    # Invalid: empty specs array (minItems: 1 required)
    check(expect_invalid(initiative_schema, {
        "id": "empty-specs",
        "title": "Initiative with No Specs Yet",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": [],
        "order": [],
        "status": "active"
    }, "Invalid initiative with empty specs array"))

    # Valid: single spec in single wave
    check(expect_valid(initiative_schema, {
        "id": "single-spec",
        "title": "Minimal Initiative",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["only-spec"],
        "order": [["only-spec"]],
        "status": "active"
    }, "Valid initiative with single spec in single wave"))

    # --- Invalid initiative tests ---
    print("\n--- Invalid Initiative Validation ---")

    # Invalid: duplicate spec IDs (uniqueItems: true)
    check(expect_invalid(initiative_schema, {
        "id": "dup-specs",
        "title": "Duplicate Specs",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["auth-api", "auth-api"],
        "order": [["auth-api"]],
        "status": "active"
    }, "Rejects initiative with duplicate spec IDs"))

    # Invalid: duplicate spec IDs in order wave (uniqueItems: true)
    check(expect_invalid(initiative_schema, {
        "id": "dup-wave",
        "title": "Duplicate Wave Specs",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["auth-api"],
        "order": [["auth-api", "auth-api"]],
        "status": "active"
    }, "Rejects initiative with duplicate spec IDs in wave"))

    # Invalid: empty author string (minLength: 1)
    check(expect_invalid(initiative_schema, {
        "id": "empty-author",
        "title": "Empty Author",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative with empty author"))

    # Invalid: missing required field - id
    check(expect_invalid(initiative_schema, {
        "title": "Missing ID",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative missing id"))

    # Invalid: missing required field - title
    check(expect_invalid(initiative_schema, {
        "id": "no-title",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative missing title"))

    # Invalid: missing required field - created
    check(expect_invalid(initiative_schema, {
        "id": "no-created",
        "title": "Missing Created",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative missing created"))

    # Invalid: missing required field - updated
    check(expect_invalid(initiative_schema, {
        "id": "no-updated",
        "title": "Missing Updated",
        "created": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative missing updated"))

    # Invalid: missing required field - author
    check(expect_invalid(initiative_schema, {
        "id": "no-author",
        "title": "Missing Author",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative missing author"))

    # Invalid: missing required field - specs
    check(expect_invalid(initiative_schema, {
        "id": "no-specs",
        "title": "Missing Specs",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative missing specs"))

    # Invalid: missing required field - order
    check(expect_invalid(initiative_schema, {
        "id": "no-order",
        "title": "Missing Order",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "status": "active"
    }, "Rejects initiative missing order"))

    # Invalid: missing required field - status
    check(expect_invalid(initiative_schema, {
        "id": "no-status",
        "title": "Missing Status",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]]
    }, "Rejects initiative missing status"))

    # Invalid: bad ID pattern (path traversal)
    check(expect_invalid(initiative_schema, {
        "id": "../hack",
        "title": "Bad ID",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative with path traversal in ID"))

    # --- Planned Waves tests ---
    print("\n--- Planned Waves Validation ---")

    # Valid: initiative with plannedWaves
    check(expect_valid(initiative_schema, {
        "id": "multi-wave",
        "title": "Multi-Wave Initiative",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a", "spec-b", "spec-c"],
        "order": [["spec-a"], ["spec-b", "spec-c"]],
        "status": "active",
        "plannedWaves": [
            {
                "wave": 2,
                "description": "Wave 2 builds on spec-a foundation",
                "specs": [
                    {"id": "spec-b", "description": "Implement feature B"},
                    {"id": "spec-c", "description": "Implement feature C", "context": "Extended context for spec-c with file targets and constraints"}
                ]
            }
        ]
    }, "Valid initiative with plannedWaves"))

    # Valid: initiative with plannedWaves without optional context field
    check(expect_valid(initiative_schema, {
        "id": "planned-no-ctx",
        "title": "Planned Without Context",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a", "spec-b"],
        "order": [["spec-a"], ["spec-b"]],
        "status": "active",
        "plannedWaves": [
            {
                "wave": 2,
                "description": "Wave 2 description",
                "specs": [{"id": "spec-b", "description": "Build on spec-a"}]
            }
        ]
    }, "Valid plannedWaves without optional context field"))

    # Valid: initiative without plannedWaves (backward compatible)
    check(expect_valid(initiative_schema, {
        "id": "no-planned",
        "title": "No Planned Waves",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Valid initiative without plannedWaves (backward compatible)"))

    # Invalid: plannedWaves spec with additional properties
    check(expect_invalid(initiative_schema, {
        "id": "bad-planned",
        "title": "Bad Planned Wave",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a"],
        "order": [["spec-a"]],
        "status": "active",
        "plannedWaves": [
            {
                "wave": 1,
                "description": "Wave 1",
                "specs": [{"id": "spec-a", "description": "Do thing", "extraField": "bad"}]
            }
        ]
    }, "Rejects plannedWaves spec with additional properties"))

    # Invalid: plannedWaves entry missing required fields
    check(expect_invalid(initiative_schema, {
        "id": "missing-wave-desc",
        "title": "Missing Wave Desc",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a"],
        "order": [["spec-a"]],
        "status": "active",
        "plannedWaves": [
            {"wave": 1, "specs": [{"id": "spec-a", "description": "Do thing"}]}
        ]
    }, "Rejects plannedWaves entry missing description"))

    # Invalid: plannedWaves spec missing required id
    check(expect_invalid(initiative_schema, {
        "id": "missing-spec-id",
        "title": "Missing Spec ID",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a"],
        "order": [["spec-a"]],
        "status": "active",
        "plannedWaves": [
            {"wave": 1, "description": "Wave 1", "specs": [{"description": "No ID"}]}
        ]
    }, "Rejects plannedWaves spec missing id"))

    # Invalid: plannedWaves wave number out of range
    check(expect_invalid(initiative_schema, {
        "id": "bad-wave-num",
        "title": "Bad Wave Number",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a"],
        "order": [["spec-a"]],
        "status": "active",
        "plannedWaves": [
            {"wave": 0, "description": "Invalid wave 0", "specs": [{"id": "spec-a", "description": "Do thing"}]}
        ]
    }, "Rejects plannedWaves with wave number 0 (minimum is 1)"))

    # Invalid: plannedWaves with bad spec ID pattern
    check(expect_invalid(initiative_schema, {
        "id": "bad-planned-id",
        "title": "Bad Planned Spec ID",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-a"],
        "order": [["spec-a"]],
        "status": "active",
        "plannedWaves": [
            {"wave": 1, "description": "Wave 1", "specs": [{"id": "../hack", "description": "Bad ID"}]}
        ]
    }, "Rejects plannedWaves spec with bad ID pattern"))

    # --- Invalid initiative tests (continued) ---
    print("\n--- Invalid Initiative Validation ---")

    # Invalid: bad ID pattern (spaces)
    check(expect_invalid(initiative_schema, {
        "id": "bad initiative id",
        "title": "Bad ID with spaces",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative with spaces in ID"))

    # Invalid: status not in enum
    check(expect_invalid(initiative_schema, {
        "id": "bad-status",
        "title": "Bad Status",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "paused"
    }, "Rejects initiative with invalid status 'paused'"))

    # Invalid: status not in enum (draft)
    check(expect_invalid(initiative_schema, {
        "id": "bad-status-2",
        "title": "Bad Status Draft",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "draft"
    }, "Rejects initiative with invalid status 'draft'"))

    # Invalid: specs array exceeds maxItems (>50)
    check(expect_invalid(initiative_schema, {
        "id": "too-many-specs",
        "title": "Too Many Specs",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": [f"spec-{i}" for i in range(51)],
        "order": [],
        "status": "active"
    }, "Rejects initiative with specs exceeding maxItems (>50)"))

    # Invalid: additional properties (extra field)
    check(expect_invalid(initiative_schema, {
        "id": "extra-props",
        "title": "Extra Properties",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active",
        "unknownField": "should fail"
    }, "Rejects initiative with additional properties"))

    # Invalid: bad timestamp format
    check(expect_invalid(initiative_schema, {
        "id": "bad-timestamp",
        "title": "Bad Timestamp",
        "created": "not-a-date",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "status": "active"
    }, "Rejects initiative with malformed timestamp"))

    # Invalid: spec ID with bad pattern in specs array
    check(expect_invalid(initiative_schema, {
        "id": "bad-spec-ref",
        "title": "Bad Spec Reference",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["../malicious"],
        "order": [],
        "status": "active"
    }, "Rejects initiative with bad spec ID pattern in specs array"))

    # Invalid: skeleton with bad pattern
    check(expect_invalid(initiative_schema, {
        "id": "bad-skeleton",
        "title": "Bad Skeleton",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [["spec-1"]],
        "skeleton": "../hack",
        "status": "active"
    }, "Rejects initiative with bad skeleton pattern"))

    # Invalid: order waves exceeding maxItems (>20 waves)
    check(expect_invalid(initiative_schema, {
        "id": "too-many-waves",
        "title": "Too Many Waves",
        "created": "2026-03-20T10:00:00Z",
        "updated": "2026-03-20T10:00:00Z",
        "author": "Alice",
        "specs": ["spec-1"],
        "order": [[f"wave-{i}"] for i in range(21)],
        "status": "active"
    }, "Rejects initiative with order exceeding maxItems (>20 waves)"))

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"{passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
