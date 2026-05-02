# Evaluation Report: [Title]

## Spec Evaluation

### Iteration [N]

**Evaluated at:** [ISO 8601 timestamp]
**Threshold:** [minScore]/10

| Dimension | Evidence | Findings | Score | Threshold | Pass/Fail |
| ----------- | -------- | -------- | ------- | ----------- | ----------- |
| Criteria Testability | | | | | |
| Criteria Completeness | | | | | |
| Design Coherence | | | | | |
| Task Coverage | | | | | |

#### Findings Detail

<!-- For each dimension, list findings with confidence classification -->

**[Dimension Name]:**

| # | Finding | Confidence | Evidence | Impact |
| --- | --------- | ---------- | -------- | ------ |
| 1 | [description] | HIGH (0.85) | [file:line, code quote] | [consequence] |
| 2 | [description] | MODERATE (0.65) | [file or pattern] | [likely impact] |
| 3 | [Advisory] [description] | LOW (0.40) | [suspected pattern] | [suspected impact] |

**Verdict:** [PASS / FAIL -- N of M dimensions passed]

**Remediation** (if FAIL):
<!-- List specific, actionable instructions for each failing dimension. Reference artifact sections by name. Only HIGH and MODERATE findings trigger remediation. -->

---

## Implementation Evaluation

### Iteration [N]

**Evaluated at:** [ISO 8601 timestamp]
**Spec type:** [feature / bugfix / refactor]
**Threshold:** [minScore]/10

| Dimension | Evidence | Findings | Score | Threshold | Pass/Fail |
| ----------- | -------- | -------- | ------- | ----------- | ----------- |
| [Dimension 1] | | | | | |
| [Dimension 2] | | | | | |
| [Dimension 3] | | | | | |
| [Dimension 4] | | | | | |

#### Findings Detail

<!-- For each dimension, list findings with confidence classification -->

**[Dimension Name]:**

| # | Finding | Confidence | Evidence | Impact |
| --- | --------- | ---------- | -------- | ------ |
| 1 | [description] | HIGH (0.85) | [file:line, code quote] | [consequence] |
| 2 | [description] | MODERATE (0.65) | [file or pattern] | [likely impact] |
| 3 | [Advisory] [description] | LOW (0.40) | [suspected pattern] | [suspected impact] |

**Test Exercise Results:**

- Tests run: [yes / no / not applicable]
- Test command: [command executed, if any]
- Pass count: [N]
- Fail count: [N]
- Failures: [specific test failures, if any]

**Verdict:** [PASS / FAIL -- N of M dimensions passed]

**Remediation** (if FAIL):
<!-- List specific, actionable instructions scoped to tasks and files. Only HIGH and MODERATE findings trigger remediation. -->

---

## Multi-Persona Review

<!-- This section is additive. Specs evaluated before multi-persona review was introduced will not have this section, and that is valid. -->

### Active Personas
<!-- Each persona includes an activation reason. Always-on personas show "always-on". Conditional personas show the matched pattern or skip reason. Manual overrides show the override flag. -->
- Correctness: [active (always-on)]
- Testing: [active (always-on)]
- Standards: [active (always-on)]
- Security: [active (matched pattern: <pattern> on file: <file>) | active (manual override (--with-security-review)) | skipped (no changed files match security-sensitive trigger patterns)]

### Findings

| ID | Persona | Severity | Confidence | Fix Class | File | Description |
| --- | --- | --- | --- | --- | --- | --- |
| [PREFIX]-[N] | [Persona Name] | [P0-P3] | [HIGH/MODERATE/LOW (value)] | [auto_fix/gated_fix/manual/advisory] | [file:line] | [description] |

### Finding Details

#### [PREFIX]-[N]: [Description]

- **Severity**: [P0-P3]
- **Confidence**: [HIGH/MODERATE/LOW (value)]
- **Evidence**: [file:line, code quote, consequence]
- **Remediation**: [specific fix]

### Deduplication Notes
<!-- Any merged findings with disagreement records. Record severity/confidence disagreements between personas. -->

### Review Verdict
<!-- [pass | fail -- N P0/P1 findings with HIGH/MODERATE confidence] -->

---

## Action Routing Summary

<!-- This section is additive. Specs evaluated before action routing was introduced will not have this section, and that is valid. -->

| Fix Class | Count | Findings |
| --- | --- | --- |
| auto_fix | [N] | [finding IDs] |
| gated_fix | [N] | [finding IDs] |
| manual | [N] | [finding IDs] |
| advisory | [N] | [finding IDs] |

### Auto-Fix Results
<!-- For each auto_fix finding: applied successfully / failed and reclassified as gated_fix -->

### Gated Fix Batch
<!-- For each gated_fix finding: proposed change summary, approval status -->

### Manual Findings
<!-- For each manual finding: reported to developer, no fix attempted -->
