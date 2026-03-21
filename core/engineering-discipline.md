## Engineering Discipline

Apply these engineering rules when generating design artifacts (design.md) during Phase 2 and when making implementation decisions during Phase 3. These rules govern how to reason about architecture, testing, reliability, and quality — not what to write (see the Writing Quality module) or what to include (see the Simplicity Principle). These are mandatory, not suggestions. Rules marked *(reinforces: ...)* overlap with existing modules — they are restated here to ground the underlying principle.

### Architecture and Design Integrity

- Assign every component in design.md exactly one responsibility. If a component description contains "and" joining two independent concerns, split it into two components. A component that does two things is two components sharing a name.
- Record every technical decision in design.md's Technical Decisions section before implementing it. A decision made during Phase 3 that was not in design.md must be logged in implementation.md's Decision Log with the rationale. No architectural choice may exist only in code. *(reinforces: implementation.md template Decision Log)*
- Verify substitutability when extending existing components: any new implementation of an existing interface must pass the existing test suite unchanged. If the new code requires changing existing tests for reasons other than added coverage, the interface contract is being violated — redesign.
- Resolve ambiguity by narrowing the contract, not widening the implementation. When a requirement can be read two ways, pick the interpretation that constrains the system more. Document the discarded interpretation in the Technical Decisions section.

### Testing and Validation Philosophy

- Derive every test case from a specific acceptance criterion or EARS statement. If a test does not trace back to a requirement, it is either testing an undocumented requirement (add it) or testing an implementation detail (remove it).
- Write the test assertion before writing the production code that satisfies it. For each task in Phase 3, create or identify the failing test first, then implement until it passes. Existing passing tests must remain passing.
- When modifying code without tests, write a characterization test capturing the current behavior before making changes. The characterization test documents what the system does today — the new test documents what it should do after the change.
- Treat a passing test suite as necessary evidence, not sufficient proof. After tests pass, review each acceptance criterion in the spec and confirm it is covered. Untested criteria are not done. *(reinforces: Phase 4 acceptance criteria verification)*

### Reliability and Failure Reasoning

- For every new integration point (API call, file I/O, external service, inter-component message), document the failure mode and the system's response in design.md. "What happens when this fails?" must have an explicit answer — not silence.
- Evaluate changes as interactions, not isolated components. When a change modifies shared state, a message format, or a timing assumption, trace through every consumer of that shared resource and verify each one tolerates the new behavior. *(reinforces: bugfix blast radius analysis)*
- After completing blast radius analysis (bugfix specs) or risk assessment (feature specs), verify that every identified risk has a corresponding test or monitoring check. A risk without a detection mechanism is an unacknowledged blind spot.

### Constraints and Quality Gates

- Identify the single constraint that most limits delivery for each spec — the one task, dependency, or decision that every other task blocks on. Execute that constraint first. Do not parallelize work around an unresolved bottleneck.
- Treat quality gates (Phase 2 entry gate, implementation gates, completion gate) as load-bearing structure, not ceremony. Never produce workarounds that technically pass a gate while violating its intent. If a gate blocks progress incorrectly, flag it — do not route around it. *(reinforces: existing enforcement gates)*
- Scope each spec to deliver one verifiable increment. If design.md describes changes that cannot be validated without completing a second spec, the scope is too large — split it. *(reinforces: Simplicity Principle "scale specs to the task")*

### Self-Check

Before finalizing design.md in Phase 2 and before marking a task complete in Phase 3, silently verify:

1. Every component in design.md has exactly one stated responsibility.
2. Every acceptance criterion maps to at least one test case (or an explicit justification for why testing is deferred).
3. Every integration point documents its failure mode and recovery behavior.

### Sources

Distilled from: Fred Brooks (conceptual integrity — one mind or small group must control design), Barbara Liskov (substitutability — new implementations must honor existing contracts), Gregor Hohpe (architecture is decisions, not structure — record and justify every choice), Kent Beck (test-driven development — test first, then implement; tests derive from requirements), Edsger Dijkstra (testing shows the presence of bugs, never their absence — passing tests are necessary, not sufficient), Michael Feathers (characterization tests — capture existing behavior before changing legacy code), Nancy Leveson (STAMP — failures arise from interactions between components, not just component faults), Nassim Taleb (antifragility — systems improve under stress only when failure modes are explicit and monitored), Eliyahu Goldratt (Theory of Constraints — identify and resolve the bottleneck before optimizing elsewhere), W. Edwards Deming (build quality in — gates are structure, not inspection theater), Jez Humble (continuous delivery — every change must be independently deployable and verifiable).
