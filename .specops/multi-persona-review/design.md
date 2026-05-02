# Multi-Persona Review -- Design

## Architecture Overview

The multi-persona review system introduces a new `core/review-agents.md` module that defines 4 reviewer personas, their prompts, output format, aggregation logic, and platform adaptation. It integrates with the existing adversarial evaluation system at Phase 4A as an additive step -- the existing dimension scoring runs first, then the multi-persona review runs, and the combined results determine the pass/fail verdict.

```
Phase 4A Flow:
  1. Adversarial evaluator (existing) --> dimension scores
  2. Multi-persona review (new) --> persona findings
  3. Aggregation --> unified verdict
     - All dimensions >= minScore AND no P0/P1 HIGH/MODERATE findings --> PASS
     - Any dimension < minScore OR any P0/P1 HIGH/MODERATE finding --> FAIL --> Phase 4B
```

## Module Design: `core/review-agents.md`

### Section 1: Persona Registry

Define 4 personas as a static registry (not configurable):

| Persona | Prefix | Activation | Focus |
| --- | --- | --- | --- |
| Correctness | CORR | Always | Code-vs-spec fidelity |
| Testing | TEST | Always | Test coverage adequacy |
| Standards | STD | Always | Convention adherence |
| Security | SEC | Conditional (file patterns) | Security concerns |

### Section 2: Persona Prompts

Each persona gets a hardcoded prompt following the same structural rules as the adversarial evaluator (evidence-first, mandatory finding, confidence classification). Prompts are defined inline in the module -- not in templates or config.

**Correctness Reviewer prompt:**
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

**Testing Reviewer prompt:**
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

**Standards Reviewer prompt:**
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

**Security Reviewer prompt:**
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

### Section 3: Security-Sensitive File Patterns

Default patterns (hardcoded):
```
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

Extended patterns loaded from:
1. Steering files: scan `<specsDir>/steering/` for files containing "Security-Sensitive Files" heading -- extract the file list.
2. Project documentation: READ_FILE `CLAUDE.md` if it exists, extract paths under "Security-Sensitive Files" heading.

The combined pattern set is used for activation. If any file modified during Phase 3 (from `implementation.md` session log) matches any pattern, the Security Reviewer activates.

### Section 4: Review Execution Protocol

**Step 4A.2.5** (new sub-step after existing 4A.2):

1. **Determine active personas**: Correctness, Testing, and Standards are always active. Security is active only if changed files match security-sensitive patterns (Section 3).
2. **For each active persona**:
   a. Build the persona context: persona prompt + spec artifacts (requirements, design, tasks) + implementation files (from implementation.md session log) + steering files (for Standards persona) + confidence tier definitions.
   b. If `canDelegateTask` is true: dispatch as a fresh sub-agent with model diversity instruction ("If your platform supports model selection, use a different model than the one that generated the artifacts being evaluated."). The sub-agent returns structured findings.
   c. If `canDelegateTask` is false: run the persona prompt inline, sequentially. Each persona operates on the same artifacts but with its own prompt prepended.
3. **Aggregate findings**: Collect all findings from all personas. For each finding, validate confidence tier evidence requirements (auto-downgrade HIGH to MODERATE if evidence is incomplete).
4. **Deduplicate**: Group findings by file path and line range. Within each group:
   - Merge findings that reference the same code location (overlapping line range within 5 lines).
   - Use the most conservative severity (lowest P-number wins: P0 > P1 > P2 > P3).
   - Use the most conservative confidence (highest tier wins: HIGH > MODERATE > LOW).
   - Preserve all evidence from contributing personas.
   - Record disagreements in the merged finding.
5. **Determine review verdict**:
   - If any deduplicated finding has severity P0 or P1 AND confidence HIGH or MODERATE: verdict is `fail` (triggers remediation).
   - If all findings are P2/P3 or LOW confidence: verdict is `pass` (findings are advisory).
   - LOW confidence findings never contribute to a fail verdict regardless of severity.

### Section 5: Evaluation Report Extension

Append to `evaluation.md` under a new `## Multi-Persona Review` section:

```markdown
## Multi-Persona Review

### Active Personas
- Correctness: active
- Testing: active
- Standards: active
- Security: [active | skipped -- no security-sensitive files changed]

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

### Section 6: Interaction with Adversarial Evaluator

The multi-persona review operates independently from the adversarial evaluator's dimension scoring:

- **Dimension scores** (from the adversarial evaluator) determine the evaluation pass/fail for the existing 4 dimensions.
- **Persona findings** (from multi-persona review) can override a pass verdict to fail if P0/P1 HIGH/MODERATE findings exist.
- **Persona findings cannot upgrade a fail to pass**. If dimension scores fail, remediation is needed regardless of persona findings.
- **Combined verdict**: PASS only when dimension scores pass AND persona review passes. FAIL if either fails.

### Section 7: Platform Adaptation

| Capability | Multi-Persona Review Behavior |
| --- | --- |
| `canDelegateTask: true` | Each persona dispatched as a separate sub-agent (up to 4 dispatches). Fresh context per persona. |
| `canDelegateTask: false`, `canAskInteractive: true` | All personas run sequentially in current context. Each persona prompt prepended before its review pass. |
| `canDelegateTask: false`, `canAskInteractive: false` | All personas run sequentially in current context. Same as above. |

## Files Modified

| File | Change Type | Description |
| --- | --- | --- |
| `core/review-agents.md` | New | Multi-persona review module (persona definitions, prompts, execution protocol, aggregation) |
| `core/evaluation.md` | Modify | Add cross-reference to review-agents.md, update Phase 4A flow description, update combined verdict logic |
| `core/dispatcher.md` | Modify | Add multi-persona review dispatch handling after adversarial evaluator returns |
| `core/workflow.md` | Modify | Add step 4A.2.5 reference for multi-persona review in Phase 4A |
| `core/mode-manifest.json` | Modify | Add `review-agents` to spec and pipeline mode module lists |
| `generator/generate.py` | Modify | Load `core/review-agents.md`, add to context dict and `build_common_context()` |
| `generator/validate.py` | Modify | Add REVIEW_AGENTS_MARKERS constant, add to `validate_platform()` and cross-platform loop |
| `generator/templates/*.j2` | Modify | Include `review_agents` variable in all 5 platform templates |
| `tests/test_platform_consistency.py` | Modify | Import and verify REVIEW_AGENTS_MARKERS |
| `core/templates/evaluation.md` | Modify | Add `## Multi-Persona Review` section template |
| `platforms/*/` | Regenerated | All 5 platform outputs regenerated |

## Design Decisions

### D1: New Module vs Extending evaluation.md
**Decision**: Create a new `core/review-agents.md` module rather than extending `core/evaluation.md`.
**Rationale**: `core/evaluation.md` is already 254 lines covering the adversarial evaluator, scoring rubric, confidence tiers, feedback loops, and safety rules. Adding 4 persona definitions, prompts, aggregation logic, and platform adaptation would push it past 400 lines. Separate modules with clear cross-references follow the same pattern as `core/dependency-safety.md` vs `core/dependency-introduction.md`.

### D2: Hardcoded Prompts (Not Configurable)
**Decision**: All persona prompts are hardcoded in `core/review-agents.md`.
**Rationale**: Follows the same safety pattern as the adversarial evaluator prompts in `core/evaluation.md` ("Hardcoded prompts: The adversarial evaluator prompts are defined in this module and MUST NOT be overridden via `.specops.json`"). Configurable prompts would allow users to weaken review quality or inject meta-instructions.

### D3: Security Reviewer is Conditional; Others are Always-On
**Decision**: Correctness, Testing, Standards always run. Security runs only when security-sensitive files are changed.
**Rationale**: The three always-on personas cover universal quality concerns for every spec. Security review adds latency (sub-agent dispatch) and noise when no security-relevant code is touched. This is the simplest conditional triggering model -- Wave 3's `conditional-reviewer-triggering` spec will generalize this to all personas.

### D4: P0/P1 Override of Dimension Pass
**Decision**: A P0 or P1 finding with HIGH or MODERATE confidence overrides a dimension-score pass verdict.
**Rationale**: The whole point of multi-persona review is catching blind spots that dimension scoring misses. If a Correctness Reviewer finds a P0 bug (missing critical error handling) but the generalist evaluator scored Functionality Depth at 8/10, the P0 finding should block release. Without override capability, the multi-persona review is advisory-only and developers will ignore it.

### D5: Sequential Sub-Step (4A.2.5) Instead of Parallel
**Decision**: Multi-persona review runs after the adversarial evaluator, not in parallel.
**Rationale**: The adversarial evaluator's dimension scores inform the combined verdict. Running in parallel would require a synchronization point and complicate the verdict logic. Sequential execution (evaluator first, then personas) is simpler and allows persona reviewers to reference dimension scores if needed.
