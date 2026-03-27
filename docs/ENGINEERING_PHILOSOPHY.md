# Engineering Philosophy

SpecOps specs follow engineering principles that govern architecture, testing, reliability, and quality. These rules apply during Phase 2 design and Phase 3 implementation.

## Architecture

- **One responsibility per component.** If a component description contains "and" joining two independent concerns, split it. A component that does two things is two components sharing a name.
- **Record every decision.** No architectural choice may exist only in code. Decisions made during implementation that were not in design.md must be logged in implementation.md's Decision Log.
- **Verify substitutability.** Any new implementation of an existing interface must pass the existing test suite unchanged. If existing tests must change, the interface contract is being violated.
- **Narrow the contract, not the implementation.** When a requirement is ambiguous, pick the interpretation that constrains the system more. Document the discarded interpretation.

## Testing

- **Derive tests from requirements.** Every test traces to a specific acceptance criterion or EARS statement. Tests without requirements are testing implementation details.
- **Test first.** Write the assertion before writing the production code. Existing passing tests must remain passing.
- **Characterize before changing.** When modifying code without tests, write a characterization test capturing current behavior before making changes.
- **Passing tests are necessary, not sufficient.** After tests pass, review each acceptance criterion and confirm it is covered. Untested criteria are not done.

## Reliability

- **Document every failure mode.** For every integration point (API call, file I/O, external service), document what happens when it fails. "What happens when this fails?" must have an explicit answer.
- **Evaluate interactions, not components.** When a change modifies shared state, a message format, or a timing assumption, trace through every consumer and verify each tolerates the new behavior.
- **Match risks to detection.** Every identified risk must have a corresponding test or monitoring check. A risk without detection is an unacknowledged blind spot.

## Constraints

- **Resolve the bottleneck first.** Identify the single constraint that most limits delivery. Execute that first. Do not parallelize work around an unresolved bottleneck.
- **Gates are structure, not ceremony.** Never produce workarounds that technically pass a gate while violating its intent. If a gate blocks progress incorrectly, flag it.
- **One verifiable increment per spec.** If a design requires completing a second spec to validate, the scope is too large.

## Sources

Distilled from: Fred Brooks (conceptual integrity), Barbara Liskov (substitutability), Kent Beck (test-driven development), Edsger Dijkstra (testing shows presence of bugs, not absence), Nancy Leveson (STAMP: failures from interactions), Eliyahu Goldratt (Theory of Constraints), W. Edwards Deming (build quality in), Jez Humble (continuous delivery).
