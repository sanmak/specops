## Writing Quality

Apply these writing rules when generating spec artifacts (requirements.md, bugfix.md, refactor.md, design.md, tasks.md) during Phase 2. These rules govern how to express content — not what to include (see the Simplicity Principle for scope guidance). These are mandatory, not suggestions.

### Structure and Order

- Lead every section with the most important information first. State the core idea or problem in the first sentence — do not bury it after context-setting paragraphs.
- Open each spec's Overview with one sentence answering "what problem does this solve and why does it matter now." Do not start with a feature description.
- Use causal narrative in Architecture Overview and design rationale sections: state what exists, why it is insufficient, what the change does, and what outcome it produces. Do not present disconnected bullet points where a causal thread exists.
- Place the conclusion or decision before the supporting evidence. Readers scan top-down — put the answer first, then the reasoning.

### Precision and Testability

- Apply the ANT test (Arguably Not True) to every requirement and acceptance criterion. If a statement cannot be false, it carries no information — rewrite it to make a specific, falsifiable claim. Example: "The system handles errors gracefully" fails the ANT test. "The API returns a 4xx status with a JSON body containing an `error` field" passes.
- Apply the OAT test (Opposite Also True) to design rationales. If the opposite statement is equally defensible, the rationale is vacuous — make it specific. Example: "We chose this for simplicity" fails if the alternative is also simple.
- Write fewer, precise requirements rather than many vague ones. Remove any requirement that hedges with "should ideally", "where possible", or "as appropriate" — either it is required or it is not.
- Use concrete nouns and measurable values. Replace adjectives ("fast", "secure", "robust") with specifications ("completes within 200ms at p95", "validates JWT signatures using RS256").

### Clarity and Conciseness

- Cut every word that does not change the meaning. Eliminate filler phrases: "It is worth noting that", "In order to", "It should be noted that", "As a matter of fact", "Essentially", "Basically."
- Use active voice. Write "The API validates the token" not "The token is validated by the API." Passive voice is permitted only when the actor is genuinely unknown or irrelevant.
- Choose short, common words over long ones. Write "use" not "utilize", "start" not "initialize", "end" not "terminate", "show" not "facilitate the display of" — unless the technical term carries precision the plain word lacks.
- Use declarative language in rationales. Write "requires", "creates", "prevents" — not "would need", "could potentially", "might cause." Modal hedging (would, could, might, should) weakens rationales — state trade-offs as facts.
- Use present tense for system behavior and design concepts. Use past tense for decisions already made. Reserve future tense for actions that have not yet occurred.
- Do not restate what the section heading already implies. If the heading says "Design: Feature X", do not open with "This section describes the design for Feature X."

### Audience Awareness

- Write for two audiences: the implementing agent (needs precise, unambiguous instructions) and the human reviewer (needs to understand intent and rationale). When these needs conflict, add a brief rationale parenthetical rather than making the instruction vague.
- Define domain-specific terms at first use in each spec. Do not assume the reader knows project-internal jargon, acronyms, or shorthand from prior specs. Budget jargon: introduce at most 3 new terms per spec section; beyond that, simplify or use plain language.
- Prefer concrete examples over abstract descriptions. When describing a data flow, API contract, or configuration format, include one representative example with realistic (but synthetic) values.

### Collaborative Voice

- Use "we" when describing collaborative design decisions and trade-offs ("We chose X because..."). Use imperative mood for task instructions ("Create the file...", "Add validation for...").
- Attribute constraints to their source. Write "The database schema requires a unique index on email" not "There needs to be a unique index." Name the actor or system imposing the constraint.

### Self-Check

Before finalizing any spec artifact in Phase 2, silently verify:

1. Read the Overview or Summary — does it sound like natural speech? If it reads like a legal document, simplify.
2. Read the first sentence of each section. Those sentences alone should convey the spec's key insights. If they are generic or descriptive ("This section covers..."), rewrite them as topic sentences.
3. Confirm no section is a wall of bullet points without at least one connecting narrative sentence explaining how the points relate.

### Sources

Distilled from: Rich Sutton (ordering, precision, ANT/OAT test, jargon budget, topic sentences), George Orwell ("Politics and the English Language" — cut words, active voice, plain language), Simon Peyton Jones (identify the one key idea, tell a story), Jeff Bezos (narrative structure over bullet-point catalogs), Leslie Lamport (precision over completeness in specifications), Donald Knuth (tense conventions, collaborative "we" voice), Paul Graham ("Write Like You Talk"), Steven Pinker ("The Sense of Style" — curse of knowledge, concrete over abstract), William Zinsser ("On Writing Well" — clarity, simplicity, brevity, humanity).
