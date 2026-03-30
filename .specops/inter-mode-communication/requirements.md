# Inter-Mode Communication

## Overview

SpecOps modes currently produce human-readable markdown output exclusively. When modes need to chain (audit -> evaluation, pipeline -> evaluation -> review), each downstream mode must parse unstructured markdown to extract findings, scores, and verdicts. This is fragile and limits composability.

Inter-mode communication defines a JSON response schema for headless mode invocations. When a mode is invoked headlessly (by another mode, not directly by a user), it outputs structured JSON instead of markdown. This enables deterministic compound workflows where pipeline mode gets pass/fail JSON from evaluation, and audit results feed directly into evaluation without text parsing.

Developer problem: "I want to run audit then evaluation then pipeline but have to manually chain three commands."

## Product Requirements

### FR-1: Headless Response Schema

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL define a JSON response schema for headless mode output with the following top-level fields:

1. **status**: One of `"success"`, `"failure"`, `"partial"`. Indicates the overall outcome of the mode invocation.
2. **findings**: Array of finding objects. Each finding contains:
   - `id`: String identifier (e.g., `CORR-1`, `TEST-2`, `DIM-func-1`)
   - `severity`: One of `"P0"`, `"P1"`, `"P2"`, `"P3"`
   - `confidence`: One of `"HIGH"`, `"MODERATE"`, `"LOW"`
   - `confidenceValue`: Number (0.00-1.00)
   - `fixClass`: One of `"auto_fix"`, `"gated_fix"`, `"manual"`, `"advisory"`, `null` (null when action routing has not run)
   - `description`: String describing the finding
   - `remediation`: String with remediation instruction (empty for advisory)
   - `file`: String file path (optional, for file-specific findings)
   - `line`: Integer line number (optional)
3. **scores**: Object mapping dimension names to integer scores (1-10). Empty object when the mode does not produce scores.
4. **verdict**: One of `"pass"`, `"fail"`, `null`. Null when no verdict applies.
5. **actionItems**: Array of strings describing actions the caller should take.
6. **metadata**: Object containing:
   - `mode`: String name of the mode that produced this response
   - `specId`: String spec identifier (when applicable)
   - `timestamp`: ISO 8601 timestamp
   - `headless`: Boolean, always `true` for headless responses

**Acceptance Criteria:**
- [x] JSON response schema defined with all 6 top-level fields
- [x] Finding object schema matches existing evaluation finding format (severity P0-P3, confidence HIGH/MODERATE/LOW, fix class from action-routing)
- [x] Schema uses `additionalProperties: false` on all objects
- [x] String fields have `maxLength`, arrays have `maxItems`
- [x] Schema is documented in core/dispatcher.md (not a separate module)

### FR-2: Headless Dispatch Option

<!-- EARS: Event-driven -->
WHEN a mode is invoked with `headless: true` in the dispatch context, THE SYSTEM SHALL instruct the dispatched mode to output JSON conforming to the headless response schema instead of human-readable markdown.

The headless flag is set by:
- Pipeline mode when invoking evaluation
- The dispatcher when chaining modes in compound workflows
- Any caller mode that needs structured output from a callee mode

**Acceptance Criteria:**
- [x] Dispatch Protocol in core/dispatcher.md updated with headless option
- [x] Headless flag is passed through the Shared Context Block to the sub-agent
- [x] When headless is true, the dispatched mode produces JSON output only
- [x] When headless is false or absent, behavior is unchanged (markdown output)

### FR-3: Participating Modes

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL support headless output for the following modes:

1. **audit**: Produces structured health check results (findings array with drift, staleness, inconsistency findings)
2. **evaluation** (implicit in dispatcher step 6): Produces structured evaluation scores and findings
3. **pipeline**: Consumes structured evaluation responses; produces structured pipeline completion status

Modes that remain interactive-only (no headless support): explore, spec, interview, init, version, update, view, steering, memory, learn, feedback, map, from-plan, initiative.

**Acceptance Criteria:**
- [x] Audit mode updated to produce headless JSON when invoked headlessly
- [x] Evaluation produces headless JSON (dispatcher step 6 updated)
- [x] Pipeline mode consumes structured evaluation JSON instead of parsing markdown
- [x] Non-participating modes are unaffected

### FR-4: Pipeline Structured Consumption

<!-- EARS: Event-driven -->
WHEN pipeline mode runs evaluation within a cycle, THE SYSTEM SHALL invoke evaluation with `headless: true` and consume the structured JSON response directly, eliminating markdown parsing for score extraction and verdict determination.

**Acceptance Criteria:**
- [x] Pipeline cycle pseudocode updated to use headless evaluation invocation
- [x] Score extraction uses JSON field access instead of markdown parsing
- [x] Verdict determination uses JSON `verdict` field directly
- [x] Zero-progress detection compares structured score objects
- [x] Action routing classification reads from JSON `findings[].fixClass`

### FR-5: Validation Pipeline Integration

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL add validation markers for inter-mode communication content in the generated platform outputs.

**Acceptance Criteria:**
- [x] HEADLESS_MARKERS constant added to generator/validate.py
- [x] Markers added to validate_platform() checks
- [x] Markers added to cross-platform consistency check loop
- [x] Markers imported in tests/test_platform_consistency.py
- [x] All 5 platforms pass validation after regeneration

### FR-6: Backward Compatibility

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL preserve all existing markdown output behavior when headless mode is not active. The headless response schema is additive -- it does not replace or modify existing human-readable output.

**Acceptance Criteria:**
- [x] Existing mode output unchanged when headless is false/absent
- [x] All existing tests pass without modification
- [x] Pipeline mode falls back to markdown parsing when evaluation does not return JSON (backward compat)
