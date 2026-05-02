# Conditional Reviewer Triggering

## Overview

The multi-persona review system (core/review-agents.md) currently hardcodes activation logic: Correctness, Testing, and Standards are always-on, while Security is conditionally triggered by a hardcoded list of security-sensitive file patterns. This works for Security but does not scale to new conditional personas or allow existing always-on personas to become conditional based on project context.

Conditional reviewer triggering generalizes the activation logic. Each persona in the registry gains a triggering conditions definition (file glob patterns, content patterns, or always-on). The review orchestrator (step 4A.2.5, step 1) matches changed files from the implementation session log against each persona's triggers and activates only the relevant reviewers. An activation reason is recorded in the evaluation report for every persona (active with reason, or skipped with reason).

Developer problem: "Every review runs all reviewers including security even when I am just updating a README. When I do touch auth code I have to remember to ask for security review."

## Product Requirements

### FR-1: Triggering Conditions in Persona Registry

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL extend each persona entry in the Persona Registry (core/review-agents.md Section 1) with a triggering conditions definition containing:

1. **activationMode**: One of `"always"` or `"conditional"`. Always-on personas fire on every review. Conditional personas fire only when their trigger patterns match.
2. **filePatterns**: Array of glob patterns (e.g., `**/auth*`, `**/*.test.*`). A conditional persona activates if any changed file matches any of its file patterns.
3. **contentPatterns**: Array of regex patterns matched against the content of changed files. A conditional persona activates if any changed file content matches any of its content patterns.

Default triggering conditions for the existing 4 personas:
- Correctness: `activationMode: "always"`, no patterns needed
- Testing: `activationMode: "always"`, no patterns needed
- Standards: `activationMode: "always"`, no patterns needed
- Security: `activationMode: "conditional"`, filePatterns = the existing security-sensitive file patterns list

**Acceptance Criteria:**
- [x] Each persona in the registry table has an Activation column showing activationMode
- [x] Security persona's filePatterns match the existing security-sensitive patterns
- [x] Triggering conditions are hardcoded (not configurable via .specops.json)
- [x] Persona prompts are NOT modified (cross-spec boundary)

### FR-2: Generalized Activation Logic in Review Execution Protocol

<!-- EARS: Event-driven -->
WHEN the review orchestrator runs step 4A.2.5 step 1 ("Determine active personas"), THE SYSTEM SHALL use the triggering conditions from the persona registry to determine activation instead of the current hardcoded logic.

For each persona:
1. If `activationMode` is `"always"`: persona is active.
2. If `activationMode` is `"conditional"`:
   a. Collect changed files from implementation.md session log "Files to Modify" entries.
   b. Match changed files against the persona's `filePatterns` using glob matching.
   c. If `contentPatterns` is non-empty and no filePattern matched: READ_FILE each changed file and match content against `contentPatterns`.
   d. If any pattern matches: persona is active with reason "matched pattern: <pattern> on file: <file>".
   e. If no pattern matches: persona is skipped with reason "no matching files".

**Acceptance Criteria:**
- [x] Step 1 uses triggering conditions instead of hardcoded "CORR/TEST/STD always, SEC conditional" logic
- [x] File pattern matching uses glob semantics
- [x] Content pattern matching uses regex semantics
- [x] Content pattern matching only runs when no file pattern matched (performance optimization)
- [x] The existing Security-Sensitive File Patterns section is absorbed into the Security persona's filePatterns
- [x] Extended patterns from steering files and CLAUDE.md are still loaded and appended to Security's filePatterns

### FR-3: Activation Reason in Evaluation Report

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL record an activation reason for every persona in the Multi-Persona Review section of the evaluation report.

The Active Personas subsection changes from a simple active/skipped list to include the reason:
```
### Active Personas
- Correctness: active (always-on)
- Testing: active (always-on)
- Standards: active (always-on)
- Security: active (matched pattern: **/auth* on file: src/auth/login.ts)
```

Or when skipped:
```
- Security: skipped (no changed files match security-sensitive patterns)
```

**Acceptance Criteria:**
- [x] Each persona entry in Active Personas includes a reason
- [x] Always-on personas show "always-on" as reason
- [x] Conditional personas show the matched pattern and file when active
- [x] Conditional personas show "no changed files match [persona] patterns" when skipped

### FR-4: Manual Override for Conditional Personas

<!-- EARS: Event-driven -->
WHEN a user includes `--with-<persona-name>-review` in the spec invocation (e.g., `--with-security-review`), THE SYSTEM SHALL force-activate that persona regardless of whether its trigger patterns match.

The manual override is detected by checking the user's original request text for the pattern `--with-<prefix>-review` where prefix maps to a persona name (e.g., `security` maps to SEC, `correctness` maps to CORR).

**Acceptance Criteria:**
- [x] Manual override syntax documented in core/review-agents.md
- [x] Override detected from user request text
- [x] Force-activated personas show reason "manual override (--with-<name>-review)"
- [x] Override does not require the persona to have conditional activation mode (can force-activate an always-on persona -- this is a no-op but valid)

### FR-5: Evaluation Template Update

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL update the evaluation report template (core/templates/evaluation.md) to include activation reasons in the Active Personas subsection.

**Acceptance Criteria:**
- [x] Template Active Personas section updated with reason format
- [x] Template shows both always-on and conditional examples

### FR-6: Validation Pipeline Integration

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL add validation markers for conditional reviewer triggering content in the generated platform outputs.

**Acceptance Criteria:**
- [x] TRIGGERING_MARKERS constant added to generator/validate.py
- [x] Markers added to validate_platform() checks
- [x] Markers added to cross-platform consistency check loop
- [x] Markers imported in tests/test_platform_consistency.py
- [x] All 5 platforms pass validation after regeneration
