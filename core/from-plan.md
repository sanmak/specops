# From Plan Mode

From Plan mode converts an existing AI coding assistant plan (from plan mode, a planning session, or any structured outline) into a persistent SpecOps spec. Instead of starting from scratch, SpecOps faithfully maps the plan's content into the standard spec structure: goals become requirements with EARS acceptance criteria, architectural decisions become design.md, and implementation steps become tasks.md.

## Detection

Patterns that trigger From Plan mode: "from-plan", "from plan", "import plan", "convert plan", "convert my plan", "from my plan", "use this plan", "turn this plan into a spec", "make a spec from this plan".

These must refer to converting an AI coding assistant plan into a SpecOps spec — NOT for product features like "import plan data from external system" or "convert pricing plan".

On non-interactive platforms (`canAskInteractive = false`), the plan content must be provided inline. If not provided, NOTIFY_USER: "From Plan mode requires the plan to be pasted inline. Re-invoke with your plan content included in the request." and stop.

## Workflow

1. **Receive plan content**: If plan content was provided inline with the invocation, use it directly. Otherwise, ASK_USER: "Please paste your plan below."

2. **Parse the plan**: Read through the plan content and identify sections using these keyword heuristics:

   | Plan signal | Keywords to look for |
   |---|---|
   | **Goal / objective** | "Goal", "Context", "Why", "Objective", "Outcome", "Problem", first paragraph |
   | **Approach / decisions** | "Approach", "Design", "Architecture", "Method", "How", "Solution", "Strategy" |
   | **Implementation steps** | Numbered lists, "Steps", "Implementation", "Tasks", "Phases", "What to create", "What to change" |
   | **Acceptance criteria** | "Verification", "Done when", "Success criteria", "Test plan", "How to test", "Acceptance" |
   | **Constraints** | "Constraints", "Trade-offs", "Risks", "Considerations", "Out of scope", "Do NOT touch", "Limitations" |
   | **Files / paths** | Any file paths mentioned (e.g., `src/auth.ts`, `core/workflow.md`) |

3. **Detect vertical and codebase context**: Use file paths and keywords in the plan to detect the project vertical (backend, frontend, infrastructure, etc.) using the same vertical detection rules as Phase 1. Do a lightweight codebase scan — READ_FILE the files mentioned in the plan and identify any affected files not already listed.

4. **Show mapping summary**: NOTIFY_USER with a brief mapping summary before generating files:
   ```
   From Plan → Spec mapping:
     Goals found → requirements.md (user stories + EARS criteria)
     Decisions found → design.md
     Steps found → tasks.md (N tasks)
     [Gap: no constraints detected — adding [To be defined] placeholder]
   ```

5. **Generate spec files using faithful mapping**:

   **requirements.md**:
   - Extract goal statements and rephrase as user stories: "As a [inferred role], I want [goal], so that [benefit]"
   - Extract acceptance criteria / done criteria and rewrite in EARS notation (WHEN / THE SYSTEM SHALL patterns)
   - Add a Constraints section from any constraints/risks found in the plan. If none found, use `[To be defined]` placeholder
   - Faithfully preserve the intent — do NOT re-derive or expand beyond what the plan states

   **design.md**:
   - Extract approach, architectural decisions, and rationale from the plan
   - Preserve file paths and component names exactly as stated in the plan
   - Add an Architecture Decisions section listing each explicit decision from the plan
   - If the plan mentioned specific libraries, patterns, or approaches, include them verbatim

   **tasks.md**:
   - Extract implementation steps and convert to spec task format with `[ ]` checkboxes and `Status: Not Started`
   - Preserve the plan's step order — do not re-sequence
   - Add any gap tasks identified from the codebase scan that the plan omitted

   **implementation.md**: WRITE_FILE with template headers only (empty — populated incrementally during Phase 3).

   **spec.json**: Create with `status: draft`, `type` inferred from plan content (feature/bugfix/refactor).

6. **Gap-fill rule**: If a section could not be extracted (e.g., no acceptance criteria in the plan), add `[To be defined]` placeholder text rather than inventing content. Note the gap in the mapping summary.

7. **Complete**: Proceed to Phase 2 spec review gate (if `config.team.specReview.enabled` or `config.team.reviewRequired`) or NOTIFY_USER that the spec is ready and they can begin implementation.

## Faithful Conversion Principle

From Plan mode preserves the plan's intent. It does NOT:
- Re-derive requirements independently from the codebase
- Second-guess architectural decisions in the plan
- Add acceptance criteria not implied by the plan
- Reorder or merge implementation steps

It DOES:
- Reformat content into SpecOps spec structure
- Apply EARS notation to extracted acceptance criteria
- Enrich goal statements with user story framing (As a / I want / So that)
- Fill structural gaps with `[To be defined]` placeholders
- Add tasks for codebase gaps the plan omitted (noted as "Gap task: not in original plan")

## Relationship to Interview Mode

From Plan mode and Interview mode serve opposite needs:

- **Interview mode**: vague idea → structured spec (SpecOps asks questions to build up requirements)
- **From Plan mode**: structured plan → persistent spec (SpecOps converts an existing plan faithfully)

If a user invokes From Plan mode but provides no plan content on a non-interactive platform, NOTIFY_USER and stop. Do not fall back to Interview mode.
