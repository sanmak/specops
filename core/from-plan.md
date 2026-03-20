# From Plan Mode

From Plan mode converts an existing AI coding assistant plan (from plan mode, a planning session, or any structured outline) into a persistent SpecOps spec. Instead of starting from scratch, SpecOps faithfully maps the plan's content into the standard spec structure: goals become requirements with EARS acceptance criteria, architectural decisions become design.md, and implementation steps become tasks.md.

## Detection

Patterns that trigger From Plan mode: "from-plan", "from plan", "import plan", "convert plan", "convert my plan", "from my plan", "use this plan", "turn this plan into a spec", "make a spec from this plan", "implement the plan", "implement my plan", "go ahead with the plan", "proceed with plan".

These must refer to converting an AI coding assistant plan into a SpecOps spec — NOT for product features like "import plan data from external system" or "convert pricing plan".

On non-interactive platforms (`canAskInteractive = false`), the plan content must be provided inline or as a file path. If neither is provided, NOTIFY_USER: "From Plan mode requires the plan to be pasted inline or provided as a file path. Re-invoke with your plan content or path included in the request." and stop.

## Workflow

1. **Receive plan content**: Resolve plan content using the first matching branch:

   **Branch A — Inline content**: If plan content was provided inline with the invocation, use it directly.

   **Branch B — File path**: If a file path was provided with the invocation (e.g., `from-plan <path>`), validate the path before reading:
   - Reject absolute paths (starting with `/`)
   - Reject paths containing `../` traversal sequences
   - Reject paths that do not end in `.md`
   - Reject paths outside the project root
   - Check FILE_EXISTS(`<path>`). If the file does not exist, NOTIFY_USER: "Plan file not found: `<path>`" and stop.
   - READ_FILE(`<path>`) to obtain plan content.

   **Branch C — Platform auto-discovery**: If no content and no path were provided, and the platform configuration includes a `planFileDirectory` field:
   - RUN_COMMAND(`ls -t "<planFileDirectory>"/*.md 2>/dev/null | head -5`) to find the 5 most recently modified plan files.
   - If no files found, fall through to Branch D.
   - If `canAskInteractive`: present the file list to the user with modification dates and ASK_USER: "Which plan would you like to convert? Enter a number, or paste a plan below."
   - If `canAskInteractive` is false: NOTIFY_USER with the list of discovered plan files and stop ("From Plan mode found these recent plans but requires interactive input to select one.").
   - Once the user selects a file, validate the path (must remain within `<planFileDirectory>`, no absolute path, no `../`, must be `.md`, FILE_EXISTS check) and READ_FILE it.

   **Branch D — Interactive paste (fallback)**: If `canAskInteractive`, ASK_USER: "Please paste your plan below."

   If none of the branches produced plan content (non-interactive platform, no inline content, no file path, no `planFileDirectory`): NOTIFY_USER: "From Plan mode requires the plan to be pasted inline or provided as a file path. Re-invoke with your plan content or path included in the request." and stop.

2. **Parse the plan**: Read through the plan content and identify sections using these keyword heuristics:

   | Plan signal | Keywords to look for |
   |---|---|
   | **Goal / objective** | "Goal", "Context", "Why", "Objective", "Outcome", "Problem", first paragraph |
   | **Approach / decisions** | "Approach", "Design", "Architecture", "Method", "How", "Solution", "Strategy" |
   | **Implementation steps** | Numbered lists, "Steps", "Implementation", "Tasks", "Phases", "What to create", "What to change" |
   | **Acceptance criteria** | "Verification", "Done when", "Success criteria", "Test plan", "How to test", "Acceptance" |
   | **Constraints** | "Constraints", "Trade-offs", "Risks", "Considerations", "Out of scope", "Do NOT touch", "Limitations" |
   | **Files / paths** | Any file paths mentioned (e.g., `src/auth.ts`, `core/workflow.md`) |

3. **Detect vertical and codebase context**: Use file paths and keywords in the plan to detect the project vertical (backend, frontend, infrastructure, etc.) using the same vertical detection rules as Phase 1. Do a lightweight codebase scan — for each file path mentioned in the plan, validate the path before reading: reject absolute paths (starting with `/`), paths containing `../` traversal sequences, and paths outside the project root. For each valid relative path, check FILE_EXISTS(`<path>`) and if it exists READ_FILE(`<path>`) to examine its current content and identify any additional affected files not already listed. Skip invalid or non-existent paths with a warning in the mapping summary.

4. **Show mapping summary**: NOTIFY_USER with a brief mapping summary before generating files:
   ```text
   From Plan → Spec mapping:
     Goals found → requirements.md (user stories + EARS criteria)
     Decisions found → design.md
     Steps found → tasks.md (N tasks)
     [Gap: no constraints detected — adding [To be defined] placeholder]
   ```

5. **Generate spec files using faithful mapping**:

   **requirements.md**:
   - Convert goal statements into user-story structure only when the plan already states the actor and benefit. When the plan omits actor or benefit, use `[role not specified]` or `[benefit not specified]` placeholders instead of inferring
   - Extract acceptance criteria / done criteria and rewrite in EARS notation (WHEN / THE SYSTEM SHALL patterns)
   - Add a Constraints section from any constraints/risks found in the plan. If none found, use `[To be defined]` placeholder
   - Faithfully preserve the intent — do NOT re-derive or expand beyond what the plan states

   **design.md**:
   - Extract approach, architectural decisions, and rationale from the plan
   - Preserve file paths and component names exactly as stated in the plan
   - Add an Architecture Decisions section listing each explicit decision from the plan
   - If the plan mentioned specific libraries, patterns, or approaches, include them verbatim

   **tasks.md**:
   - Extract implementation steps and convert to spec task format with `[ ]` checkboxes and `Status: Pending`
   - Preserve the plan's step order — do not re-sequence
   - If the codebase scan reveals missing prerequisite work not addressed in the plan, record it as a gap note in the mapping summary rather than adding tasks to `tasks.md`

   **implementation.md**: WRITE_FILE(`<specsDir>/<specName>/implementation.md`) with template headers only (empty — populated incrementally during Phase 3).

   **spec.json**: Create following the Spec Metadata protocol (see "Review Workflow" module) — run `RUN_COMMAND(\`git config user.name\`)` for author name, `RUN_COMMAND(\`date -u +"%Y-%m-%dT%H:%M:%SZ"\`)` for timestamps, set `status: draft`, infer `type` from plan content (feature/bugfix/refactor), and set `requiredApprovals` to 0 unless spec review is configured. Include all required fields: `id`, `type`, `status`, `version`, `created`, `updated`, `specopsCreatedWith`, `specopsUpdatedWith`, `author`, `reviewers`, `reviewRounds`, `approvals`, `requiredApprovals`. After writing `spec.json`, regenerate `<specsDir>/index.json` using the Global Index protocol.

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
- Apply user-story framing (As a / I want / So that) only when the plan states the actor and benefit; otherwise use `[role not specified]` or `[benefit not specified]` placeholders
- Fill structural gaps with `[To be defined]` placeholders
- Record codebase gaps in the mapping summary (noted as "Gap: not in original plan") rather than adding tasks to `tasks.md`

## Relationship to Interview Mode

From Plan mode and Interview mode serve opposite needs:

- **Interview mode**: vague idea → structured spec (SpecOps asks questions to build up requirements)
- **From Plan mode**: structured plan → persistent spec (SpecOps converts an existing plan faithfully)

If a user invokes From Plan mode but provides no plan content on a non-interactive platform, NOTIFY_USER and stop. Do not fall back to Interview mode.
