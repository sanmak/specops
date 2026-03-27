# Writing Philosophy

SpecOps specs are written for two audiences: the implementing agent (needs precise, unambiguous instructions) and the human reviewer (needs to understand intent and rationale). These rules govern every spec artifact generated during Phase 2.

## Core Tests

**ANT test (Arguably Not True)**: Every requirement and acceptance criterion must be falsifiable. If a statement cannot be false, it carries no information.

| Fails ANT | Passes ANT |
| --- | --- |
| "The system handles errors gracefully" | "The API returns a 4xx status with a JSON body containing an `error` field" |
| "Performance should be acceptable" | "Completes within 200ms at p95 under 100 concurrent requests" |

**OAT test (Opposite Also True)**: Every design rationale must be specific enough that its opposite is clearly wrong. If the opposite is equally defensible, the rationale is vacuous.

| Fails OAT | Passes OAT |
| --- | --- |
| "We chose this for simplicity" | "We chose X because it eliminates the cross-service coordination Y requires, reducing failure modes from 3 to 1" |

## Structure Rules

- Lead every section with the most important information first. State the core idea in the first sentence.
- Place the conclusion before the supporting evidence. Readers scan top-down.
- Use causal narrative in design sections: what exists, why it is insufficient, what changes, what outcome it produces.

## Precision Rules

- Write fewer, precise requirements rather than many vague ones.
- Remove any requirement that hedges with "should ideally", "where possible", or "as appropriate." Either it is required or it is not.
- Use concrete nouns and measurable values. Replace "fast" with "completes within 200ms at p95." Replace "secure" with "validates JWT signatures using RS256."

## Clarity Rules

- Cut every word that does not change the meaning. Eliminate: "It is worth noting that", "In order to", "Essentially", "Basically."
- Use active voice. "The API validates the token" not "The token is validated by the API."
- Choose short, common words. "Use" not "utilize." "Start" not "initialize." "End" not "terminate."
- Use declarative language. "Requires", "creates", "prevents." Not "would need", "could potentially", "might cause."

## Audience Rules

- Define domain-specific terms at first use. Budget: at most 3 new terms per spec section.
- Prefer concrete examples over abstract descriptions. Include one representative example with realistic values.
- When precision and readability conflict, add a brief rationale parenthetical rather than making the instruction vague.

## Sources

Distilled from: Rich Sutton (importance ordering, ANT/OAT tests, jargon budget), George Orwell ("Politics and the English Language"), Jeff Bezos (narrative structure over bullet-point catalogs), Leslie Lamport (precision over completeness), Paul Graham ("Write Like You Talk"), Steven Pinker ("The Sense of Style"), William Zinsser ("On Writing Well").
