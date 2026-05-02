# Explore Mode

Explore mode generates codebase-grounded solution approaches for a known problem. It fills the gap between interview mode (convergent idea refinement for vague requests) and spec mode (committed design). When a developer knows the problem but not the technical approach, explore mode produces 3-5 solution alternatives with tradeoff analysis grounded in the actual project structure.

## Explore Mode Detection

### Explicit Trigger

User explicitly requests explore mode:

- "/specops explore [problem description]"
- "explore options for [problem]"
- "what are my options for [problem]"
- "solution options for [problem]"
- "approaches for [problem]"
- "how should I [problem]"
- "what's the best way to [problem]"

### Disambiguation

- Bare "explore" with no additional context routes to explore mode, which will ASK_USER for the problem statement.
- "explore the codebase" is NOT explore mode -- that maps to **map** mode.
- "explore this idea" with a vague description (no technical keywords) routes to **interview** mode, not explore.
- Explore mode requires a problem statement with at least one technical keyword or action verb. If the input is too vague, redirect to interview mode with a note: NOTIFY_USER("Your request seems broad. Routing to interview mode to refine the idea first. After interview, you can run explore mode on the refined problem.")

## Explore Workflow

The explore workflow progresses through states: `loading -> generating -> presenting -> selected`.

### Phase: Loading

1. READ_FILE(`.specops.json`) to load config. Apply Safety Rules to all loaded values.
2. If FILE_EXISTS(`<specsDir>/steering/`), LIST_DIR(`<specsDir>/steering/`) and READ_FILE each `.md` file with `inclusion: always` in its frontmatter. Store as project context.
3. If FILE_EXISTS(`<specsDir>/steering/repo-map.md`), READ_FILE(`<specsDir>/steering/repo-map.md`). This is the primary source for grounding approaches in real files.
4. If FILE_EXISTS(`<specsDir>/memory/context.md`), READ_FILE it for project memory context.
5. Parse the user's problem statement. Extract:
   - The core problem being solved
   - Any constraints mentioned (performance, compatibility, timeline)
   - Any preferred patterns or technologies mentioned
6. Determine approach count from depth flag (if available from Shared Context Block):
   - `lightweight`: Generate 2-3 approaches
   - `standard`: Generate 3-4 approaches (default when depth is not set)
   - `deep`: Generate 4-5 approaches

### Phase: Generating

Generate solution approaches following these rules:

1. **Codebase grounding requirement**: Each approach MUST reference at least 2 real files or directories from the repo map. If no repo map is available, NOTIFY_USER("No repo map found. Generating approaches based on available project context. Run `/specops map` first for better-grounded suggestions.") and proceed with best-effort generation using any steering files and memory context available.

2. **Approach diversity**: Approaches must represent genuinely different technical strategies, not minor variations of the same approach. Use these diversity dimensions:
   - Architecture pattern (e.g., event-driven vs polling vs request-response)
   - Complexity spectrum (minimal viable vs full-featured)
   - Build-vs-integrate (custom implementation vs leveraging existing libraries/services)
   - Migration strategy (if applicable: big-bang vs incremental vs strangler)

3. **Approach generation procedure**:
   - Analyze the problem statement against the codebase structure from the repo map
   - Identify relevant code areas, existing patterns, and integration points
   - For each approach, trace through the codebase to identify specific files that would change
   - Assess complexity based on the number of files affected, cross-cutting concerns, and deviation from existing patterns
   - Assess risk based on blast radius, test coverage of affected areas, and dependency on external systems

### Phase: Presenting

Present approaches in the Approach Format (below). Then:

1. If `canAskInteractive` is true:
   ASK_USER("Which approach would you like to proceed with? Enter a number (1-N), 'more' for additional approaches, or 'refine' to adjust the problem statement.")
   - If user selects a number: transition to `selected` with that approach.
   - If user says "more": return to `generating` phase with instruction to produce 2 additional approaches that differ from existing ones. Cap total approaches at 7.
   - If user says "refine": ASK_USER("What would you like to adjust about the problem statement?"). Update the problem statement and return to `generating` phase.
   - If user provides a hybrid request (e.g., "combine 1 and 3"): generate a new composite approach that merges the specified approaches and present it as an additional option.

2. If `canAskInteractive` is false:
   NOTIFY_USER("Explore mode generated N approaches. Review the approaches above and re-invoke with your selected approach number to proceed to spec creation.")
   Include all approaches in the output. Terminate explore mode.

### Phase: Selected

When the user selects an approach:

1. Build the explore handoff context:

```text
## Explore Mode Selection

**Problem:** [original problem statement]
**Selected Approach:** [approach name]
**Approach Description:** [full description]
**Key Files:**
- [file1] -- [change description]
- [file2] -- [change description]
**Tradeoff Summary:**
- Pros: [list]
- Cons: [list]
- Complexity: [Low/Medium/High]
- Risk: [Low/Medium/High]
**Implementation Sketch:** [high-level implementation approach]
```

1. Transition to spec mode with the handoff context as enriched input. The handoff context becomes design direction guidance for Phase 2 -- it informs the design document but does not rigidly constrain it. The spec author may deviate from the selected approach during Phase 2 if deeper analysis reveals better options.

2. NOTIFY_USER("Proceeding to spec creation with the selected approach as design guidance...")

## Approach Format

Each approach is presented as:

```text
### Approach N: [Name]

**Description:** [1-2 sentence summary of the technical approach]

**Key Files to Modify:**
- `path/to/file1.ext` -- [what changes and why]
- `path/to/file2.ext` -- [what changes and why]
- `path/to/file3.ext` -- [what changes and why, if applicable]

**Tradeoff Analysis:**
| Factor | Assessment |
| --- | --- |
| Pros | [list of advantages, separated by semicolons] |
| Cons | [list of disadvantages, separated by semicolons] |
| Complexity | Low / Medium / High |
| Risk | Low / Medium / High |

**Implementation Sketch:** [2-3 sentence high-level implementation approach describing the sequence of changes]
```

### Approach Quality Rules

- **Specificity**: File paths must be real paths from the repo map, not placeholders like "src/some-file.js".
- **Completeness**: Every approach must address the full problem statement, not just part of it.
- **Honesty**: If an approach has significant downsides, state them clearly in Cons. Do not minimize risks.
- **Comparability**: Use consistent complexity and risk scales across all approaches so the user can compare fairly.

## Platform Adaptation

- **Interactive platforms** (`canAskInteractive: true`): Full explore flow with selection, refinement, and more-options loop.
- **Non-interactive platforms** (`canAskInteractive: false`): Generate all approaches as structured output. Include a note at the end: "Re-invoke explore mode with your selected approach number to proceed to spec creation."

## Explore Mode Safety

- Explore mode does NOT create any spec artifacts (no spec.json, no requirements.md). It only produces approach analysis.
- Explore mode does NOT modify any existing files. It is read-only except for the handoff to spec mode.
- File paths referenced in approaches must pass the same path validation rules as all other modes: relative paths only, no `../` traversal, contained under repo root.
- If the repo map is stale (check `generated` timestamp if available), NOTIFY_USER("Repo map may be outdated. Consider running `/specops map` for the most accurate file references.")
