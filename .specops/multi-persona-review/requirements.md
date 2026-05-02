# Multi-Persona Review System

## Overview

The current adversarial evaluation system uses a single monolithic evaluator at Phase 4A. This evaluator scores 4 dimensions but operates from a single perspective, creating blind spots. A race condition, a security vulnerability, or a convention violation may pass because the generalist evaluator lacks focused expertise in those domains.

The multi-persona review system adds 3-4 specialized reviewer personas that run alongside the existing adversarial evaluator at Phase 4A. Each persona has a narrow focus area, produces findings with severity (P0-P3) and confidence (HIGH/MODERATE/LOW from the confidence-gating system), and operates as a structurally separate evaluation pass. Findings from all personas are aggregated, deduplicated, and the most conservative classification wins on disagreement.

Developer problem: "The evaluation scored 8/10 but production broke because of a race condition nobody caught."

## Product Requirements

### FR-1: Reviewer Persona Definitions

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL define four reviewer personas, each with a name, focus area, hardcoded prompt, and output format:

1. **Correctness Reviewer**: Verifies implementation matches spec requirements. Focus: every acceptance criterion has corresponding code, edge cases handled, error paths implemented.
2. **Testing Reviewer**: Assesses test coverage adequacy. Focus: test existence, test quality (not just line count), missing test categories (unit, integration, edge case), test isolation.
3. **Standards Reviewer**: Checks adherence to team conventions from steering files. Focus: naming conventions, architectural patterns, code organization rules, commit conventions.
4. **Security Reviewer**: Identifies security concerns in changed files. Focus: input validation, authentication/authorization, secrets handling, injection vulnerabilities, unsafe deserialization.

**Acceptance Criteria:**
- [ ] Four reviewer personas defined with distinct focus areas
- [ ] Each persona has a hardcoded prompt (not configurable via `.specops.json`)
- [ ] Each persona's prompt includes the structural rules from the adversarial evaluation system (evidence-first, mandatory finding, score variance, confidence classification)
- [ ] Persona definitions live in a new `core/review-agents.md` module

### FR-2: Conditional Reviewer Triggering (Security Persona)

<!-- EARS: State-Driven -->
WHILE the changed files include files matching security-sensitive patterns, THE SYSTEM SHALL activate the Security Reviewer persona.

<!-- EARS: State-Driven -->
WHILE no changed files match security-sensitive patterns, THE SYSTEM SHALL skip the Security Reviewer and note "Security review skipped -- no security-sensitive files changed" in the evaluation report.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL use the following default security-sensitive file patterns: `**/auth*`, `**/security*`, `**/crypto*`, `**/password*`, `**/token*`, `**/secret*`, `**/permission*`, `**/acl*`, `**/*.env*`, `**/middleware/auth*`, files listed in `.specops.json` `securitySensitiveFiles` (if configured), and files listed in the project's `CLAUDE.md` or steering files under "Security-Sensitive Files".

**Acceptance Criteria:**
- [ ] Security Reviewer activates only when changed files match security-sensitive patterns
- [ ] Default security-sensitive patterns cover common auth/crypto/secret file paths
- [ ] Security-sensitive patterns are extensible via steering files
- [ ] Evaluation report notes when Security Reviewer is skipped with reason
- [ ] Correctness, Testing, and Standards reviewers always run (unconditional)

### FR-3: Reviewer Output Format

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL require each reviewer persona to produce findings in the following format:

- **Finding ID**: `<persona-prefix>-<sequence>` (e.g., `CORR-1`, `TEST-2`, `STD-3`, `SEC-1`)
- **Severity**: P0 (critical, blocks release), P1 (high, should fix before merge), P2 (medium, fix soon), P3 (low, advisory)
- **Confidence**: HIGH (>= 0.80), MODERATE (0.60-0.79), or LOW (< 0.60) -- following the confidence tier definitions from the confidence-gating system
- **Evidence**: Required per confidence tier (HIGH needs file:line + code + consequence; MODERATE needs file/pattern + impact; LOW has no minimum)
- **Description**: Concise finding description
- **Remediation**: Specific fix suggestion (for P0-P2 findings)

**Acceptance Criteria:**
- [ ] Each finding has a unique ID with persona prefix
- [ ] Severity uses P0-P3 scale orthogonal to confidence tier
- [ ] Confidence classification follows the confidence-gating evidence requirements
- [ ] HIGH confidence findings include all three evidence elements or are auto-downgraded to MODERATE
- [ ] LOW confidence findings are prefixed with `[Advisory]` and excluded from pass/fail scoring
- [ ] P0-P2 findings include remediation instructions

### FR-4: Finding Aggregation and Deduplication

<!-- EARS: Event-Driven -->
WHEN all active reviewer personas have completed their review, THE SYSTEM SHALL aggregate all findings into a unified report.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL deduplicate findings that reference the same file and line range across personas. When two or more findings overlap:
- The more conservative (higher) severity wins
- The more conservative (higher) confidence classification wins
- Evidence from all personas is preserved (merged)
- The finding ID reflects the primary persona (first to report)

<!-- EARS: Unwanted Behavior -->
IF a finding is classified P0 by one persona and P3 by another for the same code location, THEN THE SYSTEM SHALL use P0 (the more conservative severity) and note the disagreement: "Severity disagreement: [persona-A] classified P0, [persona-B] classified P3. Using P0 (conservative)."

**Acceptance Criteria:**
- [ ] Findings from all personas aggregated into a single report
- [ ] Duplicate findings (same file + overlapping line range) merged
- [ ] More conservative severity wins on disagreement
- [ ] More conservative confidence wins on disagreement
- [ ] Disagreements are recorded in the merged finding
- [ ] Deduplication preserves evidence from all contributing personas

### FR-5: Integration with Existing Evaluation System

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL run reviewer personas as part of Phase 4A, after the existing adversarial evaluator completes its dimension scoring.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL append reviewer findings to `evaluation.md` under a new `## Multi-Persona Review` section, separate from the adversarial evaluator's dimension scores.

<!-- EARS: Event-Driven -->
WHEN any reviewer finding has severity P0 or P1 with confidence HIGH or MODERATE, THE SYSTEM SHALL flag the evaluation as requiring remediation, regardless of the adversarial evaluator's dimension scores.

<!-- EARS: Unwanted Behavior -->
IF the adversarial evaluator passes all dimensions but a P0 finding exists from a reviewer persona, THEN THE SYSTEM SHALL override the pass verdict and trigger Phase 4B remediation.

**Acceptance Criteria:**
- [ ] Reviewer personas run after the adversarial evaluator in Phase 4A
- [ ] Findings appear in `evaluation.md` under `## Multi-Persona Review`
- [ ] P0/P1 HIGH/MODERATE findings trigger remediation even if dimension scores pass
- [ ] P2/P3 findings do not block the evaluation pass
- [ ] LOW confidence findings never trigger remediation regardless of severity
- [ ] Evaluation report shows both dimension scores and persona findings

### FR-6: Sub-Agent Dispatch for Reviewers

<!-- EARS: State-Driven -->
WHILE the platform capability `canDelegateTask` is true, THE SYSTEM SHALL dispatch each reviewer persona as a separate sub-agent with a fresh context containing only the persona's prompt, the spec artifacts, and the implementation files.

<!-- EARS: State-Driven -->
WHILE the platform capability `canDelegateTask` is false, THE SYSTEM SHALL run reviewer personas sequentially in the current context with the persona prompt prepended to each review pass.

**Acceptance Criteria:**
- [ ] Each reviewer persona runs in a fresh sub-agent context when `canDelegateTask` is true
- [ ] Reviewer personas run sequentially in the same context when `canDelegateTask` is false
- [ ] Sub-agent dispatch includes model diversity instruction (use different model if available)
- [ ] Each sub-agent receives only its persona prompt + relevant artifacts (not other personas' findings)

### FR-7: Dispatcher and Workflow Integration

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL update `core/dispatcher.md` to handle multi-persona review dispatch after the adversarial evaluator returns.

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL update `core/evaluation.md` to reference the multi-persona review system and define the interaction between dimension scores and persona findings.

**Acceptance Criteria:**
- [ ] `core/dispatcher.md` updated with multi-persona review dispatch logic
- [ ] `core/evaluation.md` updated with cross-reference to `core/review-agents.md`
- [ ] `core/workflow.md` Phase 4A references the multi-persona review step
- [ ] Generator pipeline wired (generate.py, validate.py, Jinja2 templates, mode-manifest.json)

## Non-Functional Requirements

- **NFR-1**: The multi-persona review adds no more than 4 sub-agent dispatches (one per active persona). The Security Reviewer may be skipped, reducing to 3.
- **NFR-2**: All reviewer prompts are hardcoded in `core/review-agents.md` and cannot be overridden by `.specops.json` or any configuration mechanism. This follows the same safety pattern as the adversarial evaluator prompts.
- **NFR-3**: All additions use abstract operations only in core modules (no platform-specific tool names).
- **NFR-4**: The multi-persona review system is always active when evaluation is enabled. There is no separate config switch to disable it independently of the evaluation system.
- **NFR-5**: Reviewer persona findings reuse the existing confidence tier infrastructure from the confidence-gating spec. No new tier definitions.
- **NFR-6**: The evaluation report remains backward compatible. Specs evaluated before this change render correctly (the `## Multi-Persona Review` section is additive).

## Deferred Criteria

- **Action routing for findings** (covered by separate `action-routing` spec in Wave 2): Classification of findings into auto_fix, gated_fix, manual, or advisory categories.
- **Conditional triggering for non-Security personas** (covered by separate `conditional-reviewer-triggering` spec in Wave 3): File-pattern-based activation for Correctness, Testing, and Standards reviewers.

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
