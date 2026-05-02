# Conditional Reviewer Triggering -- Design

## Architecture Overview

Conditional reviewer triggering generalizes the persona activation system in `core/review-agents.md`. The change is contained to the existing review-agents module -- no new core module is needed. The Security-Sensitive File Patterns section is refactored into a per-persona triggering conditions system, and the Review Execution Protocol step 1 is updated to use this generalized system.

```
Current activation logic (hardcoded in step 1):
  CORR -> always active
  TEST -> always active
  STD  -> always active
  SEC  -> active if any changed file matches security-sensitive patterns

New activation logic (per-persona triggering conditions):
  For each persona:
    if activationMode == "always" -> active
    if activationMode == "conditional":
      match changed files against persona.filePatterns
      if no file match and contentPatterns defined:
        match changed file content against persona.contentPatterns
      if any match -> active (with reason)
      else -> skipped (with reason)
    if manual override present -> active (manual override)
```

## Design Decisions

### D1: Modify existing module, not create new one

The triggering system lives in `core/review-agents.md` as modifications to the existing Persona Registry and Review Execution Protocol sections. Rationale: triggering is an intrinsic property of persona activation, not a separate concern. Adding a new module would fragment the review system across two files. The multi-persona-review spec explicitly designed the activation logic in this module.

### D2: Triggering conditions are hardcoded, not configurable

Triggering conditions are hardcoded in the module, following the same safety pattern as persona prompts. Rationale: allowing `.specops.json` to override trigger patterns could deactivate security review on security-sensitive files, creating a security gap. This matches the existing decision from multi-persona-review: "Prompts are hardcoded in this module and MUST NOT be overridden via `.specops.json`."

### D3: Absorb Security-Sensitive File Patterns into Security persona filePatterns

The existing "### Security-Sensitive File Patterns" section in core/review-agents.md is refactored. The hardcoded patterns become the Security persona's filePatterns array. The extended patterns loading (from steering files and CLAUDE.md) remains and appends to Security's filePatterns at runtime. This eliminates the standalone section and moves all activation logic into the per-persona triggering system.

### D4: Content pattern matching is a secondary fallback

Content patterns are only evaluated when no file pattern matched. This is a performance optimization -- reading file content is expensive (requires READ_FILE per changed file). For the existing 4 personas, content patterns are not needed (Security uses file patterns only). Content patterns exist as an extension point for future conditional personas (e.g., a Data Migration reviewer might trigger on content containing SQL migration statements).

### D5: Validation markers extend REVIEW_AGENTS_MARKERS

Rather than creating a separate TRIGGERING_MARKERS constant, the new markers are added to the existing REVIEW_AGENTS_MARKERS. Rationale: triggering conditions are part of the review-agents module, not a separate feature. Adding to the existing marker set keeps the validation simple and avoids a separate import/registration in test_platform_consistency.py.

However, looking at project conventions (each feature gets its own marker set), a separate TRIGGERING_MARKERS constant is cleaner and follows the pattern of ACTION_ROUTING_MARKERS, HEADLESS_MARKERS, etc. **Decision: use a separate TRIGGERING_MARKERS constant** for consistency with the project pattern and to clearly track what this spec validates.

## Detailed Design

### Section 1: Persona Registry Update (core/review-agents.md)

Update the Persona Registry table to include triggering conditions. The table gains an Activation column with the mode and trigger description:

| Persona | Prefix | Activation | Triggering | Focus |
| --- | --- | --- | --- | --- |
| Correctness | CORR | Always | activationMode: always | ... |
| Testing | TEST | Always | activationMode: always | ... |
| Standards | STD | Always | activationMode: always | ... |
| Security | SEC | Conditional | activationMode: conditional, filePatterns: [security-sensitive patterns] | ... |

Below the table, add a "### Triggering Conditions" subsection documenting:
1. The activationMode field (always vs conditional)
2. The filePatterns field (array of glob patterns)
3. The contentPatterns field (array of regex patterns, secondary fallback)
4. Manual override syntax (`--with-<persona>-review`)
5. Extended pattern loading (steering files and CLAUDE.md, for Security only)

### Section 2: Refactor Security-Sensitive File Patterns

The existing "### Security-Sensitive File Patterns" section is renamed to "### Persona Trigger Patterns" and restructured:

1. The hardcoded security patterns become the Security persona's default filePatterns
2. The extended patterns loading (steering files, CLAUDE.md) remains as Security-specific extension logic
3. A note clarifies that always-on personas do not need patterns (they fire regardless)

### Section 3: Review Execution Protocol Step 1 Update

Replace step 1 in the Review Execution Protocol:

**Current:**
```
1. Determine active personas: Correctness, Testing, and Standards are always active.
   Security is active only if changed files match security-sensitive patterns.
```

**New:**
```
1. Determine active personas:
   a. Collect changed files from implementation.md session log "Files to Modify" entries.
   b. Check for manual overrides in the user's request text (--with-<persona>-review).
   c. For each persona in the registry:
      i.   If a manual override is present for this persona: activate. Reason: "manual override (--with-<prefix>-review)".
      ii.  If activationMode is "always": activate. Reason: "always-on".
      iii. If activationMode is "conditional":
           - Match each changed file path against the persona's filePatterns using glob matching.
           - If any match: activate. Reason: "matched pattern: <pattern> on file: <file>".
           - If no file match and contentPatterns is non-empty:
             READ_FILE each changed file and match content against contentPatterns.
           - If any content match: activate. Reason: "content matched pattern: <pattern> in file: <file>".
           - If no match: skip. Reason: "no changed files match <persona> trigger patterns".
   d. Record activation results (persona, status, reason) for the evaluation report.
```

### Section 4: Multi-Persona Review Report Template Update

Update the Active Personas subsection in the report template (both in core/review-agents.md and core/templates/evaluation.md):

```markdown
### Active Personas
- Correctness: [active (always-on) | skipped (manual override only)]
- Testing: [active (always-on) | skipped (manual override only)]
- Standards: [active (always-on) | skipped (manual override only)]
- Security: [active (always-on | matched pattern: <pattern> on file: <file> | manual override) | skipped (no changed files match security-sensitive patterns)]
```

### Section 5: Validation Markers

Add `TRIGGERING_MARKERS` to `generator/validate.py`:

```python
TRIGGERING_MARKERS = [
    "Triggering Conditions",
    "activationMode",
    "filePatterns",
    "contentPatterns",
    "Persona Trigger Patterns",
    "manual override",
    "always-on",
    "activation reason",
]
```

### Files Modified

| File | Change |
| --- | --- |
| `core/review-agents.md` | Add Triggering Conditions section, refactor Security-Sensitive File Patterns to Persona Trigger Patterns, update Review Execution Protocol step 1, update report template |
| `core/templates/evaluation.md` | Update Active Personas template with activation reasons |
| `generator/validate.py` | Add TRIGGERING_MARKERS, add to validate_platform(), add to consistency loop |
| `tests/test_platform_consistency.py` | Import TRIGGERING_MARKERS, add to REQUIRED_MARKERS |
| Generated platform outputs | Regenerate with `python3 generator/generate.py --all` |

### Dependency Decisions

No new dependencies introduced. This feature modifies only the existing review-agents module and the validation pipeline.
