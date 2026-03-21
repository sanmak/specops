# Interview Mode

Interview mode front-loads a structured Q&A session to gather clear requirements before spec generation. It's especially useful for vague or high-level ideas, transforming "I want to build a SaaS thing" into a spec-ready problem statement.

## When Interview Mode Triggers

### Explicit Trigger

User explicitly requests interview mode:

- `/specops interview I have this idea...`
- Request keyword contains "interview"

### Auto-Trigger (Interactive Platforms Only)

SpecOps automatically enters interview mode if the request is **vague**, detected by any of:

- ≤ 5 words in the request
- **No technical keywords** detected from any vertical (no matches against infrastructure/data/library/frontend/backend/builder keywords)
- **No action verb** (no add, build, fix, refactor, create, implement, set up, design, architect, etc.)
- Explicit signals: "help me think about", "idea:", "brainstorm", "need advice on"

**Example vague prompts triggering auto-interview:**

- "I want to build a SaaS" (5 words, no tech keywords, generic)
- "Something for restaurants" (3 words, no tech keywords)
- "Help me design a product" (auto-trigger keywords)

**Example clear prompts that skip interview:**

- "Add OAuth authentication to the API" (has action verb + tech keywords)
- "Refactor the database layer to use repository pattern" (explicit action + tech terms)
- "Fix 500 errors on checkout" (action verb + specific issue)

## Interview Workflow (State Machine)

The interview progresses through states: `gathering → clarifying → confirming → complete`.

### Phase: Gathering

Ask 5 fixed questions in order. Each question has a primary form and optional clarifying follow-up triggered by answer characteristics.

#### Question 1: Problem

```text
Primary:  "What problem are you solving or what gap are you filling?"
Trigger:  Answer < 15 words OR uses only generic words (thing, stuff, feature, tool)
Follow-up: "Who specifically encounters this problem? What's their current workaround or pain point?"
```

#### Question 2: Users

```text
Primary:  "Who are the primary users or beneficiaries? Describe them briefly."
Trigger:  Answer ≤ 2 words OR answer is exactly "developers", "users", "everyone", "anyone"
Follow-up: "What's their main workflow or context? Are they technical?"
```

#### Question 3: Core Features

```text
Primary:  "What are the 2–3 core things this needs to do? (Key features, not nice-to-haves)"
Trigger:  Fewer than 2 distinct features mentioned
Follow-up: "What happens after [primary feature]? Any secondary workflows or follow-on actions?"
```

#### Question 4: Constraints

```text
Primary:  "Any hard constraints? (Tech stack preferences, integrations, timeline, must-nots, dependencies)"
Trigger:  Answer is "none", empty/blank, or only very generic ("fast", "secure")
Follow-up: "Any existing systems this must integrate with or compatibility concerns?"
```

#### Question 5: Done Criteria

```text
Primary:  "How will you know this is done? (What does success look like?)"
Trigger:  Answer < 10 words OR no measurable/observable outcome mentioned
Follow-up: "What's the absolute minimum shippable version of this?"
```

### Phase: Clarifying

When a follow-up is triggered, Use the AskUserQuestion tool for the follow-up question. Record the follow-up answer. Then continue to the next primary question (or move to Confirming if all 5 are complete).

### Phase: Confirming

1. Display a formatted summary of all 5 gathered answers:

   ```text
   Interview Summary

   **Problem:** [answer 1]
   **Users:** [answer 2]
   **Core Features:** [answer 3]
   **Constraints:** [answer 4]
   **Done Criteria:** [answer 5]
   ```

2. Use the AskUserQuestion tool: "Does this capture your idea? Any corrections or clarifications?"

3. If the user provides corrections:
   - Update the affected answer
   - Re-display the updated summary
   - Re-confirm

4. Once confirmed: transition to `complete`

### Phase: Complete

- Synthesize gathered answers into a single enriched request description
- Transition back to Phase 1 (Understand Context) with this enriched description
- Display: "Now generating your spec from this foundation..."
- Continue with normal workflow (request type detection, vertical detection, spec generation)

## Platform Gating

- **Interactive platforms** (`canAskInteractive: true`): Full interview flow
- **Non-interactive platforms** (`canAskInteractive: false`, e.g., Codex):
  - Skip interview entirely
  - Note to user: "Interview mode requires interactive input. Proceeding with best-effort spec generation from your description."
  - Continue with Phase 1 using the original request

## Interview Mode in the Workflow

Interview mode runs after the from-plan check and before Phase 1 (Understand Context) in the main workflow:

1. User invokes specops
2. Check if request is view/list command → handle separately
3. Check if request is steering command → handle separately
4. Check if request is from-plan command → handle separately (see "From Plan Mode" module)
5. **Check if interview mode is triggered (explicit or auto)**
   - If yes: Run interview workflow above
   - Once complete: Proceed to Phase 1 with enriched context
6. If no interview: Continue to Phase 1 normally
