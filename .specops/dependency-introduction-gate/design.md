# Design: Dependency Introduction Gate

## Architecture Overview

The Dependency Introduction Gate adds a new core module (`core/dependency-introduction.md`) that governs *which* dependencies enter a project, complementing the existing `core/dependency-safety.md` which audits *whether* existing dependencies are safe. The gate operates at three workflow touchpoints: Phase 2 (decision-making), Phase 3 (enforcement), and audit mode (drift detection). It also extends adversarial evaluation scoring and the dependencies.md steering file.

## Technical Decisions

### Decision 1: Always-Active Gate with No Config Knobs

**Context:** The existing dependency-safety gate has `config.dependencySafety.enabled`, `severityThreshold`, and other config options. Should the introduction gate follow the same pattern?
**Options Considered:**

1. Add `config.dependencyIntroduction` section with enabled/threshold/bypass options -- Pros: consistency with dependency-safety; Cons: config knobs become dead features when agents skip non-mandatory steps
2. Always active, no bypass, deterministic -- Pros: no way to circumvent, simpler implementation, aligns with the "deterministic workflow execution" feedback pattern; Cons: less flexible

**Decision:** Option 2 -- always active, no config knobs
**Rationale:** The feedback memory documents that config flags without deterministic workflow instructions are dead features. The gate should always run. If a spec has no new dependencies, it passes trivially. There is no legitimate reason to bypass dependency governance.

### Decision 2: Separate Core Module vs. Extending dependency-safety.md

**Context:** Should the introduction gate be added to the existing dependency-safety.md or be a new module?
**Options Considered:**

1. Extend `core/dependency-safety.md` with introduction gate sections -- Pros: single dependency module; Cons: module becomes very large, mixes two concerns (auditing existing vs. governing new)
2. New `core/dependency-introduction.md` module -- Pros: separation of concerns, each module has a clear purpose; Cons: one more module in the system

**Decision:** Option 2 -- new `core/dependency-introduction.md`
**Rationale:** The two modules have different trigger points (safety gate runs once at Phase 2 step 6.5; introduction gate runs at step 5.8 and throughout Phase 3), different data flows, and different purposes. Combining them would create an oversized module that is harder to maintain.

### Decision 3: Phase 2 Step Numbering

**Context:** Where in Phase 2 does the dependency introduction gate run?
**Options Considered:**

1. New step 5.8 -- between coherence verification (5.5) and vocabulary verification (5.6) -- Pros: early enough to inform design; Cons: requires renumbering
2. New step 5.8 -- after code-grounded plan validation (5.7) -- Pros: has access to validated file paths; Cons: late in Phase 2
3. New step 6.3 -- after external issue creation (6) -- Pros: no renumbering; Cons: too late, dependencies should be decided before issues are created

**Decision:** Option 2 -- step 5.8, after code-grounded plan validation
**Rationale:** At step 5.8 the design.md is finalized and file paths are validated. This is the right moment to scan for dependency references and evaluate them before issue creation and the dependency safety gate (6.5). The numbering follows the existing fractional step pattern (5.5, 5.6, 5.7, 5.8).

### Decision 4: Install Command Pattern Detection

**Context:** How does the gate detect when Phase 3 attempts to install a dependency?
**Options Considered:**

1. Pre-scan task implementation steps for install commands before executing -- Pros: catches before execution; Cons: tasks may not list exact commands
2. Hook into RUN_COMMAND calls and intercept install patterns -- Pros: catches all installs; Cons: requires changes to the abstract operation layer
3. Pattern-match in the core module instructions -- the agent is instructed to check before running any install command -- Pros: works within existing architecture; Cons: relies on agent compliance

**Decision:** Option 3 -- instruct the agent to verify before executing install commands
**Rationale:** SpecOps operates at the instruction/prompt level, not at a code execution interception layer. The agent is told "WHEN you are about to run an install command, verify the package is in ### Dependency Decisions first." This is the same enforcement pattern used by all other SpecOps gates (task state machine, dependency gate, etc.). Adversarial evaluation catches violations that slip through.

### Decision 5: Maintenance Profile Intelligence Layers

**Context:** How does the gate assess whether a dependency is well-maintained?
**Options Considered:**

1. Registry APIs only (npmjs.com, pypi.org) -- Pros: standardized, fast; Cons: limited data
2. 3-layer approach: registry API, source repo (GitHub API), LLM fallback -- Pros: comprehensive; Cons: more network calls
3. LLM-only assessment -- Pros: no network dependency; Cons: training data is stale

**Decision:** Option 2 -- 3-layer approach matching the dependency-safety.md pattern
**Rationale:** Consistent with the existing 3-layer verification pattern in dependency-safety.md. Each layer compensates for the previous layer's failures: registry APIs provide download stats and last-publish dates; GitHub API provides star count, last commit, and open issue count; LLM fallback provides knowledge when APIs are unavailable.

## Component Design

### Component 1: Install Command Patterns Table

**Responsibility:** Define ecosystem-specific install command patterns that the gate recognizes
**Interface:** Markdown table mapping ecosystems to command patterns (npm install, pip install, cargo add, etc.)
**Dependencies:** Ecosystem list from `core/dependency-safety.md` Dependency Detection Protocol

### Component 2: Build-vs-Install Evaluation Framework

**Responsibility:** Provide 5 criteria for evaluating whether to install a package or build the functionality in-house
**Interface:** 5-criteria scoring table: scope match, maintenance health, size proportionality, security surface, license compatibility
**Dependencies:** Maintenance Profile Intelligence (Component 3)

### Component 3: Maintenance Profile Intelligence

**Responsibility:** Assess dependency maintenance health using a 3-layer approach
**Interface:** 3 layers: (1) registry APIs for download stats and publish dates, (2) source repo APIs for activity metrics, (3) LLM fallback for training data knowledge
**Dependencies:** Network access for layers 1-2; graceful fallback to layer 3

### Component 4: Phase 2 Step 5.8 Gate Procedure

**Responsibility:** Scan design.md for dependency references, evaluate new dependencies, surface to user, record decisions
**Interface:** Integrated into Phase 2 workflow after step 5.7
**Dependencies:** Components 1-3, dependencies.md steering file

### Component 5: Phase 3 Spec Adherence Enforcement

**Responsibility:** Verify all install commands target approved dependencies; flag unapproved installs as protocol breach
**Interface:** Enforcement rule in Phase 3 implementation gates section
**Dependencies:** design.md ### Dependency Decisions section

### Component 6: Auto-Intelligence Policy Generation

**Responsibility:** Create and maintain ## Dependency Introduction Policy in dependencies.md
**Interface:** Writes to dependencies.md steering file, preserving team-maintained sections
**Dependencies:** Component 4 decisions, vertical detection

### Component 7: Adversarial Evaluation Updates

**Responsibility:** Add dependency-aware scoring guidance to Design Coherence and Design Fidelity dimensions
**Interface:** Additional guidance text in existing evaluation dimension tables
**Dependencies:** `core/evaluation.md` existing scoring tables

### Component 8: Audit Mode Dependency Drift Check

**Responsibility:** 7th drift check comparing installed packages against approved dependencies
**Interface:** New check in the Six Drift Checks section of `core/reconciliation.md`
**Dependencies:** Ecosystem detection from `core/dependency-safety.md`, lock file parsing

### Component 9: Generator Pipeline Integration

**Responsibility:** Wire the new module into build_common_context(), Jinja2 templates, mode-manifest.json, validate.py, and test_platform_consistency.py
**Interface:** Standard generator pipeline integration pattern
**Dependencies:** Existing generator infrastructure

### Dependency Decisions

No external dependencies required. This feature is pure markdown/workflow logic with optional network calls to public registry APIs (npmjs.com, pypi.org, registry.npmjs.org, api.github.com) that use graceful fallback when unavailable.

## Sequence Diagrams

### Flow 1: Phase 2 Dependency Introduction Gate (Step 5.8)

```text
Agent -> design.md: READ_FILE to scan for install commands and package references
Agent -> dependencies.md: READ_FILE to get Detected Dependencies
Agent -> Agent: Compare design.md packages against Detected Dependencies
Agent -> Agent: Identify net-new dependencies
[For each new dependency:]
Agent -> Registry API: Query download stats, last publish (Layer 1)
Agent -> GitHub API: Query stars, last commit, issues (Layer 2)
Agent -> Agent: LLM fallback if APIs fail (Layer 3)
Agent -> Agent: Run Build-vs-Install 5-criteria evaluation
Agent -> User: ASK_USER with evaluation summary and recommendation
User -> Agent: Approve or reject
Agent -> design.md: EDIT_FILE to add ### Dependency Decisions with outcomes
Agent -> dependencies.md: EDIT_FILE to update ## Dependency Introduction Policy
```

### Flow 2: Phase 3 Install Command Enforcement

```text
Agent -> tasks.md: READ_FILE to get implementation steps
[For each task with install commands:]
Agent -> design.md: READ_FILE ### Dependency Decisions
Agent -> Agent: Verify target package is in approved list
[If approved:]
Agent -> Shell: RUN_COMMAND install command
[If NOT approved:]
Agent -> User: NOTIFY_USER protocol breach -- unapproved dependency
Agent -> Agent: HALT until user approves or removes the install
```

### Flow 3: Audit Mode Dependency Drift

```text
Agent -> Lock files: READ_FILE to get installed packages
Agent -> index.json: READ_FILE to enumerate completed specs
[For each completed spec:]
Agent -> design.md: READ_FILE ### Dependency Decisions to collect approved packages
Agent -> Agent: Compare installed vs approved union
Agent -> Agent: Flag unapproved packages as Warning
Agent -> Report: Include in Dependency Drift check
```

## Data Model Changes

No database or data model changes. The feature uses existing spec artifact files (design.md, dependencies.md, spec.json) and adds new sections within them.

### New Sections in Existing Files

**design.md** -- new section added during Phase 2 step 5.8:

```markdown
### Dependency Decisions

| Package | Version | Ecosystem | Decision | Rationale |
| ------- | ------- | --------- | -------- | --------- |
| express | ^4.18   | Node.js   | Approved | Scope match: HTTP server framework needed; Health: 59M weekly downloads, active maintenance |
| lodash  | ^4.17   | Node.js   | Rejected | Size proportionality: only need _.get -- use optional chaining instead |
```

**dependencies.md** steering file -- new section:

```markdown
## Dependency Introduction Policy

**Default stance:** conservative (builder vertical)
**Ecosystem:** Node.js (detected from package-lock.json)

### Approved Patterns
- [accumulated from dependency decisions across specs]

### Rejected Patterns
- [accumulated from rejected dependencies with reasons]
```

## API Changes

No API changes. This is a workflow/prompt-level feature.

## Security Considerations

- Authentication: N/A -- registry API calls are public, no auth needed
- Authorization: N/A -- no new permissions required
- Data protection: Registry API responses are ephemeral, not stored beyond the evaluation
- Input validation: Package names from design.md are treated as data, not commands -- no shell injection risk because they are used for string comparison, not interpolated into commands

## Performance Considerations

- Registry API calls use 10-second timeout (matching dependency-safety.md pattern)
- Maximum 10 dependencies evaluated per gate run (matching dependency-safety.md top-10 limit)
- Layer fallback ensures the gate completes even without network access

## Testing Strategy

- Unit tests: Validation markers in test_platform_consistency.py (DEPENDENCY_INTRODUCTION_MARKERS)
- Integration tests: `python3 generator/validate.py` verifies markers present in all 5 platform outputs
- E2E tests: `bash scripts/run-tests.sh` runs full test suite

## Rollout Plan

1. Create `core/dependency-introduction.md` with all gate logic
2. Update `core/workflow.md` with Phase 2 step 5.8 and Phase 3 enforcement
3. Update `core/evaluation.md` with scoring guidance
4. Update `core/reconciliation.md` with 7th drift check
5. Update `core/steering.md` with Dependency Introduction Policy section in dependencies.md template
6. Update generator pipeline (generate.py, templates, mode-manifest.json, validate.py, test)
7. Regenerate all platform outputs
8. Run full test suite

## Risks & Mitigations

- **Risk 1:** Registry API rate limiting or downtime could slow Phase 2 -- **Mitigation:** 3-layer fallback ensures the gate always completes; 10-second timeouts prevent hanging
- **Risk 2:** Agents may not reliably self-enforce install command checking in Phase 3 -- **Mitigation:** Adversarial evaluation catches violations in Phase 4A; audit mode catches drift post-completion
- **Risk 3:** Lock file parsing may miss edge cases (workspaces, monorepos) -- **Mitigation:** Audit drift check flags as Warning (not Drift), acknowledging pre-existing dependencies

## Dependencies & Blockers

### Spec Dependencies

| Dependent Spec | Reason | Required | Status |
| -------------- | ------ | -------- | ------ |
| dependency-safety-gate | Shares ecosystem detection and dependencies.md | No | Completed |
| adversarial-evaluation | Scoring dimensions to extend | No | Completed |

### Cross-Spec Blockers

<!-- Resolution types: scope_cut, interface_defined, completed, escalated, deferred -->

| Blocker | Blocking Spec | Resolution Type | Resolution Detail | Status |
| ------- | ------------- | --------------- | ----------------- | ------ |
| -- | -- | -- | -- | -- |

## Future Enhancements

- Dependency version range policy enforcement (e.g., "must pin major versions")
- Monorepo per-workspace dependency scoping
- Dependency graph visualization in audit reports
- Integration with Dependabot/Renovate for automated upgrade tracking
