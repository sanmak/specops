## Multi-Persona Review

The multi-persona review system adds structurally separated, focused reviewer personas that run alongside the adversarial evaluator at Phase 4A. Each persona has a narrow focus area, produces findings with severity (P0-P3) and confidence (HIGH/MODERATE/LOW from the confidence-gating system), and operates as a structurally separate evaluation pass. Findings from all personas are aggregated, deduplicated, and the most conservative classification wins on disagreement.

### Persona Registry

Four reviewer personas are defined as a static registry. Prompts are hardcoded in this module and MUST NOT be overridden via `.specops.json` or any other configuration mechanism.

| Persona | Prefix | Activation | Focus |
| --- | --- | --- | --- |
| Correctness Reviewer | CORR | Always (activationMode: always) | Code-vs-spec fidelity: every acceptance criterion has corresponding code, edge cases handled, error paths implemented |
| Testing Reviewer | TEST | Always (activationMode: always) | Test coverage adequacy: test existence, test quality, missing test categories, test isolation |
| Standards Reviewer | STD | Always (activationMode: always) | Convention adherence: naming conventions, architectural patterns, code organization rules, commit conventions |
| Security Reviewer | SEC | Conditional (activationMode: conditional, filePatterns) | Security concerns: input validation, authentication/authorization, secrets handling, injection vulnerabilities |

### Triggering Conditions

Each persona has triggering conditions that determine when it activates during the multi-persona review. Triggering conditions are hardcoded in this module and MUST NOT be overridden via `.specops.json` or any other configuration mechanism.

**activationMode**: Determines the persona's activation behavior.

- `"always"`: The persona fires on every review regardless of which files changed. Used by Correctness, Testing, and Standards.
- `"conditional"`: The persona fires only when its trigger patterns match changed files. Used by Security.

**filePatterns**: Array of glob patterns matched against changed file paths. A conditional persona activates if any changed file matches any of its filePatterns. Always-on personas do not need filePatterns (they activate regardless). See the Persona Trigger Patterns section below for the default patterns.

**contentPatterns**: Array of regex patterns matched against changed file content. Content pattern matching is a secondary fallback -- it only runs when no filePattern matched. This avoids unnecessary file reads (READ_FILE per changed file). Content patterns exist as an extension point for future conditional personas (e.g., a Data Migration reviewer triggering on SQL migration statements). The existing 4 personas do not use contentPatterns.

**Manual override**: Users can force-activate any persona regardless of its triggering conditions by including `--with-<persona-name>-review` in their request (e.g., `--with-security-review`). The override is detected by checking the user's original request text for the pattern `--with-<name>-review` where name maps to a persona: `security` -> SEC, `correctness` -> CORR, `testing` -> TEST, `standards` -> STD. A force-activated persona shows activation reason "manual override (--with-<name>-review)". Force-activating an always-on persona is valid but a no-op (it would activate anyway).

### Persona Prompts

Each persona prompt includes the structural rules from the adversarial evaluation system (evidence-first, mandatory finding, confidence classification). These prompts are hardcoded and not configurable.

#### Correctness Reviewer

```text
You are a Correctness Reviewer. Your sole focus is whether the implementation matches
the specification. For every acceptance criterion, find the corresponding code. If code
is missing, the criterion is unmet. If code exists but handles only the happy path, the
criterion is partially met.

STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each criterion, cite the specific file:line where it is implemented.
   If you cannot find it, that is a finding.
2. Mandatory finding: You MUST identify at least one gap or risk. If the implementation
   perfectly matches the spec, identify the weakest point (least robust error handling,
   most fragile assumption).
3. Confidence classification: HIGH (>= 0.80) requires file:line + code quote + consequence.
   MODERATE (0.60-0.79) requires file/pattern + impact. LOW (< 0.60) is [Advisory] only.
```

#### Testing Reviewer

```text
You are a Testing Reviewer. Your sole focus is test adequacy. Existence of tests is
necessary but not sufficient -- tests must exercise meaningful behavior, not just exist
for coverage metrics.

STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each test file, cite what it tests and what it misses.
2. Mandatory finding: You MUST identify at least one testing gap. Common gaps: missing
   edge case tests, missing error path tests, tests that assert on implementation details
   rather than behavior, tests that pass trivially.
3. Confidence classification: HIGH (>= 0.80) requires file:line + test code quote +
   consequence of missing coverage. MODERATE (0.60-0.79) requires test pattern reference
   + likely impact. LOW (< 0.60) is [Advisory] only.
```

#### Standards Reviewer

```text
You are a Standards Reviewer. Your sole focus is adherence to the project's documented
conventions. Read the steering files and team conventions. Every deviation from a stated
convention is a finding.

STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each convention violation, cite the convention source (steering
   file or .specops.json) and the violating code location.
2. Mandatory finding: You MUST identify at least one convention deviation. If all
   conventions are followed, identify the convention with the weakest adherence.
3. Confidence classification: HIGH (>= 0.80) requires convention source + violating
   file:line + consequence. MODERATE (0.60-0.79) requires convention reference + likely
   impact. LOW (< 0.60) is [Advisory] only.
```

#### Security Reviewer

```text
You are a Security Reviewer. Your sole focus is security concerns in the changed files.
You are activated only when security-sensitive files are modified. Assume the code has
vulnerabilities until proven otherwise.

STRUCTURAL RULES (mandatory, not guidelines):
1. Evidence-first: For each security concern, cite the specific file:line and the
   vulnerability class (OWASP category or CWE where applicable).
2. Mandatory finding: You MUST identify at least one security concern. If the code
   appears secure, identify the weakest security assumption or the most likely attack
   vector.
3. Confidence classification: HIGH (>= 0.80) requires file:line + code quote +
   exploit scenario. MODERATE (0.60-0.79) requires code pattern + likely attack vector.
   LOW (< 0.60) is [Advisory] only.
```

### Persona Trigger Patterns

Trigger patterns are per-persona. Always-on personas (Correctness, Testing, Standards) do not have trigger patterns -- they activate on every review regardless of changed files.

**Security Reviewer default filePatterns** (hardcoded):

```text
**/auth*
**/security*
**/crypto*
**/password*
**/token*
**/secret*
**/permission*
**/acl*
**/*.env*
**/middleware/auth*
```

**Security Reviewer extended patterns** are loaded at runtime and appended to the default filePatterns:

1. **Steering files**: If FILE_EXISTS(`<specsDir>/steering/`), scan steering files for a "Security-Sensitive Files" heading and extract the file list.
2. **Project documentation**: If FILE_EXISTS(`CLAUDE.md`), READ_FILE it and extract paths listed under a "Security-Sensitive Files" heading.

The combined pattern set (defaults + extended) is the Security persona's effective filePatterns. If any file modified during Phase 3 (from `implementation.md` session log "Files to Modify" entries) matches any pattern, the Security Reviewer activates.

**Future conditional personas**: New conditional personas added to the registry follow the same pattern -- define their filePatterns and optionally contentPatterns in this section. The activation logic in the Review Execution Protocol handles all conditional personas uniformly.

### Review Execution Protocol

**Step 4A.2.5** (runs after the adversarial evaluator's dimension scoring at step 4A.2):

1. **Determine active personas**: For each persona in the registry, evaluate its triggering conditions to determine activation. Record an activation reason for every persona.
   a. Collect changed files from `implementation.md` session log "Files to Modify" entries.
   b. Check for manual overrides: scan the user's original request text for `--with-<persona-name>-review` patterns (e.g., `--with-security-review`).
   c. For each persona:
      - If a manual override is present for this persona: activate. Activation reason: "manual override (--with-<name>-review)".
      - Else if `activationMode` is `"always"`: activate. Activation reason: "always-on".
      - Else if `activationMode` is `"conditional"`:
        i. Match each changed file path against the persona's `filePatterns` (see Persona Trigger Patterns above) using glob matching.
        ii. If any file matches: activate. Activation reason: "matched pattern: <pattern> on file: <file>".
        iii. If no filePattern matched and the persona has `contentPatterns`: READ_FILE each changed file and match content against the `contentPatterns` regex patterns.
        iv. If any content matches: activate. Activation reason: "content matched pattern: <pattern> in file: <file>".
        v. If no pattern matches: skip. Activation reason: "no changed files match <persona> trigger patterns".
   d. Record activation results (persona name, active/skipped, activation reason) for inclusion in the Multi-Persona Review section of the evaluation report.

2. **For each active persona**:
   a. Build the persona context: persona prompt (from Persona Prompts above) + spec artifacts (requirements, design, tasks) + implementation files (from implementation.md session log) + steering files (for Standards persona) + confidence tier definitions.
   b. If `canDelegateTask` is true: dispatch as a fresh sub-agent with model diversity instruction ("If your platform supports model selection, use a different model than the one that generated the artifacts being evaluated."). The sub-agent returns structured findings.
   c. If `canDelegateTask` is false: run the persona prompt inline, sequentially. Each persona operates on the same artifacts but with its own prompt prepended.

3. **Aggregate findings**: Collect all findings from all personas. Each finding must include:
   - **Finding ID**: `<persona-prefix>-<sequence>` (e.g., CORR-1, TEST-2, STD-3, SEC-1)
   - **Severity**: P0 (critical, blocks release), P1 (high, should fix before merge), P2 (medium, fix soon), P3 (low, advisory)
   - **Confidence**: HIGH (>= 0.80), MODERATE (0.60-0.79), or LOW (< 0.60) following confidence tier definitions
   - **Evidence**: Required per confidence tier (HIGH needs file:line + code + consequence; MODERATE needs file/pattern + impact; LOW has no minimum)
   - **Description**: Concise finding description
   - **Remediation**: Specific fix suggestion (for P0-P2 findings)

   For each finding, validate confidence tier evidence requirements. If a HIGH confidence finding is missing any of the three required evidence elements, auto-downgrade to MODERATE and append: "Downgraded from HIGH -- missing [element]."

   LOW confidence findings are prefixed with `[Advisory]` and excluded from pass/fail scoring.

4. **Deduplicate**: Group findings by file path and line range. Within each group:
   - Merge findings that reference the same code location (overlapping line range within 5 lines).
   - Use the most conservative severity (lowest P-number wins: P0 > P1 > P2 > P3).
   - Use the most conservative confidence (highest tier wins: HIGH > MODERATE > LOW).
   - Preserve all evidence from contributing personas.
   - Record disagreements: if personas disagree on severity, note "Severity disagreement: [persona-A] classified P[X], [persona-B] classified P[Y]. Using P[min(X,Y)] (conservative)."

5. **Determine review verdict**:
   - If any deduplicated finding has severity P0 or P1 AND confidence HIGH or MODERATE: verdict is `fail` (triggers remediation).
   - If all findings are P2/P3 or LOW confidence: verdict is `pass` (findings are advisory).
   - LOW confidence findings never contribute to a fail verdict regardless of severity.

### Multi-Persona Review Report Template

Append to `evaluation.md` under a new `## Multi-Persona Review` section:

```markdown
## Multi-Persona Review

### Active Personas
- Correctness: active (always-on)
- Testing: active (always-on)
- Standards: active (always-on)
- Security: [active (matched pattern: <pattern> on file: <file>) | active (manual override (--with-security-review)) | skipped (no changed files match security-sensitive trigger patterns)]

### Findings

| ID | Persona | Severity | Confidence | File | Description |
| --- | --- | --- | --- | --- | --- |
| CORR-1 | Correctness | P1 | HIGH (0.85) | core/foo.md:42 | ... |
| TEST-1 | Testing | P2 | MODERATE (0.70) | tests/test_foo.py | ... |

### Finding Details

#### CORR-1: [Description]
- **Severity**: P1
- **Confidence**: HIGH (0.85)
- **Evidence**: [file:line, code quote, consequence]
- **Remediation**: [specific fix]

### Deduplication Notes
[Any merged findings with disagreement records]

### Review Verdict
[pass | fail -- N P0/P1 findings with HIGH/MODERATE confidence]
```

### Interaction with Adversarial Evaluator

The multi-persona review operates independently from the adversarial evaluator's dimension scoring:

- **Dimension scores** (from the adversarial evaluator) determine the evaluation pass/fail for the existing 4 dimensions.
- **Persona findings** (from multi-persona review) can override a pass verdict to fail if P0/P1 HIGH/MODERATE findings exist.
- **Persona findings cannot upgrade a fail to pass**. If dimension scores fail, remediation is needed regardless of persona findings.
- **Combined verdict**: PASS only when dimension scores pass AND persona review passes. FAIL if either fails.

When remediation is triggered by persona findings (not dimension score failures), the remediation context includes the specific persona findings -- not just dimension scores. The failing finding IDs, severities, and remediation instructions are included in the Phase 4B remediation dispatch.

### Platform Adaptation

| Capability | Multi-Persona Review Behavior |
| --- | --- |
| `canDelegateTask: true` | Each persona dispatched as a separate sub-agent (up to 4 dispatches). Fresh context per persona. |
| `canDelegateTask: false`, `canAskInteractive: true` | All personas run sequentially in current context. Each persona prompt prepended before its review pass. |
| `canDelegateTask: false`, `canAskInteractive: false` | All personas run sequentially in current context. Same as above. |
