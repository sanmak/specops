# SpecOps Sequence Diagrams

Interactive sequence diagrams showing actor interactions across SpecOps workflows. These complement the high-level SVG diagrams in [`assets/`](../assets/) with detailed message-passing views.

> **Rendering:** GitHub renders these Mermaid diagrams natively. In VS Code, use the [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension.

---

## Overall 4-Phase Workflow

The core SpecOps workflow: understand context, generate a spec, implement tasks, and verify completion.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant S as .specops/
    participant C as Codebase

    Note over A: Phase 1 — Understand Context
    A->>S: Read .specops.json
    S-->>A: Config (specsDir, vertical, review settings)
    A->>S: Read index.json (context recovery)
    S-->>A: Existing specs & statuses

    alt Incomplete spec found
        A-->>U: "Found incomplete spec. Continue?"
        U->>A: Yes / No
    end

    A->>S: Load steering files (always-included)
    S-->>A: Product context, tech stack, structure
    A->>C: Explore codebase patterns
    C-->>A: Architecture, affected files, dependencies
    A->>S: Evaluate fileMatch steering files
    S-->>A: Domain-specific context (if globs match)

    Note over A: Phase 2 — Create Specification
    A->>A: Detect type (feature / bugfix / refactor)
    A->>A: Detect vertical (backend, frontend, infra, etc.)
    A->>S: Write requirements.md (EARS acceptance criteria)
    A->>S: Write design.md (architecture decisions)
    A->>S: Write tasks.md (implementation checklist)
    A->>S: Write implementation.md (empty template)
    A->>S: Write spec.json (draft status)
    A->>S: Regenerate index.json

    alt Review enabled
        A->>S: Set status → in-review
        A-->>U: "Spec ready for review. Pausing for approval."
        Note over A: Phase 2.5 — Review Cycle
        U->>A: Review feedback & approval
        A->>S: Update spec.json (approved)
    end

    Note over A: Phase 3 — Implement
    A->>S: Read spec.json (implementation gate)
    A->>S: Set status → implementing

    loop For each task in tasks.md
        A->>S: Write "In Progress" to tasks.md
        A->>C: Implement code changes
        A->>C: Run tests
        A->>S: Update acceptance criteria checkboxes
        A->>S: Write "Completed" to tasks.md
        A-->>U: Progress update (e.g., "Task 3/8 done")
    end

    Note over A: Phase 4 — Complete
    A->>S: Read requirements.md — verify all criteria checked
    A->>S: Finalize implementation.md (summary)
    A->>C: Scan for stale documentation
    A->>S: Set status → completed
    A->>S: Regenerate index.json
    A-->>U: Completion summary
```

**Source:** [`core/workflow.md`](../core/workflow.md)

---

## Interview Mode

Structured Q&A for vague or high-level ideas. Transforms "I want to build a SaaS" into a spec-ready problem statement.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent

    U->>A: Vague request (e.g., "Something for restaurants")
    A->>A: Detect vague input (≤5 words, no tech keywords)

    Note over A,U: Phase: Gathering (5 fixed questions)

    A-->>U: Q1: "What problem are you solving?"
    U->>A: Answer
    opt Answer < 15 words or generic
        A-->>U: Follow-up: "Who encounters this? Current workaround?"
        U->>A: Clarification
    end

    A-->>U: Q2: "Who are the primary users?"
    U->>A: Answer
    opt Answer ≤ 2 words or too generic
        A-->>U: Follow-up: "What's their workflow? Are they technical?"
        U->>A: Clarification
    end

    A-->>U: Q3: "What are the 2-3 core features?"
    U->>A: Answer
    opt Fewer than 2 features mentioned
        A-->>U: Follow-up: "What happens after [primary feature]?"
        U->>A: Clarification
    end

    A-->>U: Q4: "Any hard constraints?"
    U->>A: Answer
    opt Answer is "none" or too generic
        A-->>U: Follow-up: "Any existing system integrations?"
        U->>A: Clarification
    end

    A-->>U: Q5: "How will you know this is done?"
    U->>A: Answer
    opt Answer < 10 words or no measurable outcome
        A-->>U: Follow-up: "What's the minimum shippable version?"
        U->>A: Clarification
    end

    Note over A,U: Phase: Confirming

    A-->>U: Display interview summary (Problem, Users, Features, Constraints, Done)
    A-->>U: "Does this capture your idea? Corrections?"

    alt User provides corrections
        U->>A: Corrections
        A-->>U: Updated summary
        A-->>U: "Confirmed now?"
    end

    U->>A: Confirmed

    Note over A,U: Phase: Complete
    A->>A: Synthesize enriched request
    A-->>U: "Now generating your spec from this foundation..."
    Note over A: → Proceeds to Phase 1 with enriched context
```

**Source:** [`core/interview.md`](../core/interview.md)

---

## Collaborative Review

Team-based spec review cycle between spec creation (Phase 2) and implementation (Phase 3).

```mermaid
sequenceDiagram
    participant Author
    participant A as Agent
    participant S as .specops/<spec-name>/
    participant Reviewer

    Note over Author,Reviewer: Phase 2 completes — spec auto-set to in-review, reviewRounds → 1

    Note over Reviewer: Review Mode

    Reviewer->>A: Open spec (detected as non-author)
    A->>S: Read spec files (requirements, design, tasks)
    A-->>Reviewer: Present structured summary
    A-->>Reviewer: "Section-by-section or overall feedback?"
    Reviewer->>A: Feedback preference

    alt Section-by-section
        loop Each spec section
            A-->>Reviewer: Present section
            Reviewer->>A: Comments on section
        end
    else Overall
        Reviewer->>A: General feedback
    end

    A-->>Reviewer: "Verdict: Approve / Approve with suggestions / Request changes?"
    Reviewer->>A: Verdict

    A->>S: Write reviews.md (feedback + verdict)
    A->>S: Update spec.json (reviewer entry, approvals)

    alt Changes requested
        Note over Author: Revision Mode
        Author->>A: Return to spec
        A->>S: Read reviews.md
        A-->>Author: Summary of requested changes
        Author->>A: Address feedback
        A->>S: Revise spec files
        A->>S: Increment version & reviewRounds, reset approvals
        A->>S: Regenerate index.json
        A-->>Author: "Spec revised. Notify reviewers for re-review."
        Note over Reviewer: Another review round...
    else Approved or Approve with suggestions (approvals >= requiredApprovals)
        A->>S: Set status → approved
        A->>S: Regenerate index.json
        Note over A: → Implementation gate passes, proceed to Phase 3
    else Self-approved (approvals >= requiredApprovals AND all reviewers have selfApproval: true)
        A->>S: Set status → self-approved
        A->>S: Regenerate index.json
        Note over A: → Implementation gate passes, proceed to Phase 3
    end
```

**Source:** [`core/review-workflow.md`](../core/review-workflow.md)

---

## From-Plan Conversion

Converts an existing AI plan into a persistent SpecOps spec. Faithful mapping — no re-derivation.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant C as Codebase
    participant S as .specops/<spec-name>/

    U->>A: "from-plan" + plan content
    alt No plan content provided (interactive)
        A-->>U: "Please paste your plan below."
        U->>A: Plan content
    end

    Note over A: Parse plan content

    A->>A: Identify goal/objective
    A->>A: Identify approach/decisions
    A->>A: Identify implementation steps
    A->>A: Identify acceptance criteria
    A->>A: Identify constraints
    A->>A: Extract file paths

    Note over A: Validate & scan codebase

    loop For each file path in plan
        A->>A: Validate path (reject absolute, reject ../)
        alt Valid relative path
            A->>C: Check FILE_EXISTS(path)
            alt File exists
                A->>C: READ_FILE(path)
                C-->>A: Current content + additional affected files
            else File missing
                A->>A: Note in mapping summary
            end
        else Invalid path
            A->>A: Skip with warning
        end
    end

    A->>A: Detect vertical from keywords & paths

    Note over A: Show mapping summary

    A-->>U: "Goals → requirements.md, Decisions → design.md, Steps → tasks.md (N tasks), Gaps: [...]"

    Note over A: Generate spec files (faithful conversion)

    A->>S: Write requirements.md (EARS from plan criteria, placeholders for gaps)
    A->>S: Write design.md (decisions verbatim from plan)
    A->>S: Write tasks.md (plan step order preserved)
    A->>S: Write implementation.md (empty template)
    A->>S: Write spec.json (draft, type inferred)
    A->>S: Regenerate index.json

    A-->>U: "Spec created from plan. Ready for review or implementation."
```

**Source:** [`core/from-plan.md`](../core/from-plan.md)

---

## Task Execution (Phase 3)

Write-ordering protocol and task state machine during implementation.

```mermaid
sequenceDiagram
    participant A as Agent
    participant T as tasks.md
    participant C as Codebase
    participant I as implementation.md

    Note over A: Implementation gate passed

    A->>T: Read tasks.md
    T-->>A: Task list with statuses

    loop For each pending task (sequential)
        A->>T: Verify no other task is "In Progress"

        Note over A,T: Write Ordering: update file BEFORE doing work

        A->>T: Set task status → "In Progress"
        A->>C: Implement code changes
        A->>C: Run tests

        alt Design decision made
            A->>I: Append to Decision Log
        end

        alt Deviated from design.md
            A->>I: Append to Deviations table
        end

        A->>T: Check off acceptance criteria ([ ] → [x])
        A->>T: Check off test items ([ ] → [x])

        alt All criteria satisfied
            A->>T: Set task status → "Completed"
        else Blocker encountered
            A->>T: Set task status → "Blocked"
            A->>T: Add Blocker: line with details
            A->>I: Add entry to Blockers Encountered
            Note over A: Resolve blocker...
            A->>T: Clear Blocker: line
            A->>T: Set task status → "In Progress"
        end
    end

    Note over A: All tasks completed → proceed to Phase 4
```

**Valid state transitions:**

```text
Pending ──────► In Progress
In Progress ──► Completed
In Progress ──► Blocked
Blocked ──────► In Progress
```

**Source:** [`core/task-tracking.md`](../core/task-tracking.md)

---

## Audit & Reconcile

Drift detection between spec artifacts and the live codebase, with interactive repair.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant S as .specops/
    participant G as Git History

    U->>A: /specops audit <spec-name>
    A->>S: Read .specops.json (get specsDir)

    alt Specific spec named
        A->>S: Read <spec-name>/spec.json
        A->>S: Read <spec-name>/tasks.md
    else Audit all
        A->>S: List spec directories
        A->>S: Read each spec.json (filter: status ≠ completed)
    end

    Note over A: Run 5 drift checks

    par Check 1: File Drift
        A->>S: Parse "Files to Modify" paths from tasks.md
        loop Each file path
            A->>A: FILE_EXISTS(path)?
            alt Missing
                A->>G: git log --diff-filter=R (renamed?)
                A->>G: git log --diff-filter=D (deleted?)
            end
        end
    and Check 2: Post-Completion Modification
        alt Status = completed
            loop Each file path
                A->>G: git log --after="<spec.json.updated>" -- "<path>"
                G-->>A: Commits after completion (if any)
            end
        end
    and Check 3: Task Status Inconsistency
        A->>A: Completed tasks with missing files?
        A->>G: Pending tasks with early commits?
    and Check 4: Staleness
        A->>A: Compare spec.json.updated vs current date
        A->>A: Apply thresholds (7d/14d/30d by status)
    and Check 5: Cross-Spec Conflicts
        A->>S: Collect "Files to Modify" from all active specs
        A->>A: Detect files referenced by 2+ specs
    end

    A-->>U: Health Report (Healthy / Warning / Drift per check)

    opt User requests reconcile
        U->>A: /specops reconcile <spec-name>
        A-->>U: Numbered findings list
        A-->>U: "Which findings to fix? (all / 1,3 / skip)"
        U->>A: Selection

        loop Selected findings
            A-->>U: Repair options (update path / remove / skip)
            U->>A: Choice
            A->>S: Apply repair to tasks.md
        end

        A->>S: Update spec.json (timestamp)
        A->>S: Regenerate index.json
        A-->>U: "Reconciliation complete. Applied N fix(es)."
    end
```

**Source:** [`core/reconciliation.md`](../core/reconciliation.md)

---

## Steering File Loading

How persistent project context is loaded during Phase 1.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant SD as .specops/steering/
    participant Ctx as Agent Context

    Note over A: Phase 1, Step 3 — Load steering files

    A->>SD: FILE_EXISTS(steering/)?

    alt Directory does not exist
        A-->>U: "No steering directory — run /specops steering to set up"
    else Directory exists
        A->>SD: LIST_DIR — find all .md files
        SD-->>A: File list (sorted alphabetically, max 20)

        loop Each .md file
            A->>SD: READ_FILE(filename)
            SD-->>A: Content with YAML frontmatter
            A->>A: Parse frontmatter (name, description, inclusion, globs)

            alt Invalid frontmatter
                A-->>U: "Skipping file — invalid frontmatter"
            else inclusion = "always"
                A->>Ctx: Store content as loaded project context
            else inclusion = "fileMatch"
                A->>A: Validate globs array
                A->>Ctx: Store with globs (deferred evaluation)
            else inclusion = "manual"
                A->>A: Skip (not auto-loaded)
            end
        end

        A-->>U: "Loaded N always-included steering files"

        Note over A: Phase 1 continues... affected files identified

        A->>A: Evaluate deferred fileMatch files
        loop Each fileMatch steering file
            A->>A: Match globs against affected file paths
            alt Globs match
                A->>Ctx: Load file content into project context
            end
        end
    end
```

**Source:** [`core/steering.md`](../core/steering.md)

---

## Init

Initialize SpecOps configuration in a project.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant FS as Project Root
    participant SD as .specops/steering/

    U->>A: /specops init

    A->>FS: Read .specops.json
    alt Config already exists
        A-->>U: Display existing config
        A-->>U: "Replace or keep current?"
        U->>A: Decision
        alt Keep
            A-->>U: "Keeping existing config."
            Note over A: Workflow ends here — no further steps
        else Replace
            Note over A: Continue to Template Selection below
        end
    end

    Note over A,U: Template Selection

    A-->>U: "Which template? Minimal / Standard / Full / Review / Builder"
    U->>A: Template choice
    A->>FS: Write .specops.json with template

    alt Template has specReview.enabled = true
        A-->>U: "Solo or team?"
        alt Solo
            A->>FS: Set allowSelfApproval → true, minApprovals → 1
        end
    end

    A-->>U: "Customize any fields? (specsDir, vertical, conventions)"
    U->>A: Optional customizations
    opt Customizations provided
        A->>FS: Edit .specops.json
    end

    Note over A,SD: Create steering files (skip existing)
    A->>SD: Write product.md (if not exists)
    A->>SD: Write tech.md (if not exists)
    A->>SD: Write structure.md (if not exists)

    Note over A: Create memory scaffold (skip existing)
    A->>FS: mkdir -p .specops/memory/
    A->>FS: Write decisions.json, context.md, patterns.json (if not exists)

    alt All files newly created
        A-->>U: "SpecOps initialized! Steering files created in .specops/steering/, memory scaffold created in .specops/memory/"
    else All files already existed
        A-->>U: "SpecOps initialized! Steering files verified existing in .specops/steering/, memory scaffold verified existing in .specops/memory/"
    else Some files created, some already existed
        A-->>U: "SpecOps initialized! Steering files set up in .specops/steering/, memory scaffold set up in .specops/memory/"
    end
```

**Source:** [`core/init.md`](../core/init.md)

---

## Spec Decomposition Workflow

Automatic scope assessment, split detection, and initiative orchestration for large features.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant S as .specops/
    participant I as .specops/initiatives/

    U->>A: /specops Add OAuth + payment processing

    Note over A: Phase 1 — Understand Context
    A->>S: Read config, steering files, memory
    A->>A: Analyze codebase and request scope

    Note over A: Phase 1.5 — Scope Assessment
    A->>A: Evaluate complexity signals
    A->>A: Detect multiple bounded contexts (auth, payments)
    A->>A: Estimate task count exceeds threshold

    alt Interactive platform
        A-->>U: "This feature spans 2 bounded contexts. Split into 2 specs?"
        A-->>U: "Spec 1: oauth-auth, Spec 2: payment-processing"
        U->>A: Approve split
    else Non-interactive platform
        A->>A: Continue as single spec with summary
    end

    Note over A: Create initiative
    A->>I: Write initiative.json (specs, waves, skeleton)

    Note over A: Phase 2 — Create Specs (for each member spec)

    loop For each spec in initiative
        A->>S: Write requirements.md, design.md, tasks.md
        A->>S: Write spec.json (partOf, specDependencies)
    end

    A->>A: Run cycle detection (DFS with coloring)
    A->>A: Derive execution waves (topological sort)
    A->>I: Update initiative.json with order

    Note over A: Initiative Orchestration

    loop For each wave
        loop For each spec in wave
            Note over A: Phase 3 — Dependency Gate
            A->>S: Read spec.json.specDependencies
            A->>A: Verify required deps completed

            alt Required dep incomplete
                A-->>U: "Blocked: <dep-spec> not completed"
                A->>A: Scope hammering options
            else All deps satisfied
                Note over A: Phase 3 — Implement
                A->>A: Dispatch spec to fresh sub-agent
                A->>S: Execute tasks, update status
            end

            Note over A: Phase 4 — Complete
            A->>S: Verify criteria, set completed
            A->>I: Update initiative status
        end
    end

    A->>I: All specs completed → initiative status = completed
    A->>I: Write initiative-log.md
    A-->>U: "Initiative complete. All specs implemented."
```

**Source:** [`core/decomposition.md`](../core/decomposition.md), [`core/initiative-orchestration.md`](../core/initiative-orchestration.md)

---

## Adversarial Evaluation

Two-touchpoint quality scoring: spec evaluation at Phase 2 exit and implementation evaluation at Phase 4A.

```mermaid
sequenceDiagram
    participant A as Agent
    participant E as Evaluator
    participant S as .specops/<spec-name>/

    Note over A,E: Phase 2 Exit — Spec Evaluation

    A->>S: Write requirements.md, design.md, tasks.md
    A->>E: Dispatch evaluator with spec artifacts

    E->>S: Read requirements.md
    E->>S: Read design.md
    E->>S: Read tasks.md
    E->>E: Score 4 dimensions (1-10 each)
    Note over E: Criteria Testability, Criteria Completeness,<br/>Design Coherence, Task Coverage

    alt All scores >= minScore (default 7)
        E->>S: Write evaluation.md (verdict: pass)
        Note over A: Proceed to Phase 3
    else Any score < minScore
        E->>S: Write evaluation.md (verdict: fail, findings)
        E-->>A: Remediation guidance per failing dimension
        A->>S: Revise spec artifacts
        Note over A,E: Re-evaluate (up to maxIterations)
    end

    Note over A,E: Phase 4A — Implementation Evaluation

    A->>S: Phase 3 implementation complete
    A->>E: Dispatch evaluator with code + spec artifacts

    E->>E: Score spec-type-specific dimensions (1-10 each)
    Note over E: Feature: Functionality Depth, Design Fidelity,<br/>Code Quality, Test Verification

    alt All scores >= minScore
        E->>S: Append to evaluation.md (verdict: pass)
        Note over A: Proceed to Phase 4B/4C (complete)
    else Any score < minScore
        E->>S: Append to evaluation.md (verdict: fail, findings)
        Note over A: Phase 4B remediation → re-implement failing tasks
    end
```

**Source:** [`core/evaluation.md`](../core/evaluation.md)

---

## Production Learnings Lifecycle

Capture, store, and surface post-deployment discoveries across spec sessions.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant M as .specops/memory/
    participant S as .specops/<spec-name>/

    Note over U,A: Capture — Three Mechanisms

    alt Explicit capture
        U->>A: /specops learn <spec-name>
        A-->>U: "What was discovered?"
        U->>A: Discovery details
        A-->>U: "Severity? Category? Root cause?"
        U->>A: Metadata
    else Agent-proposed (during bugfix)
        A->>A: Detect production issue pattern
        A-->>U: "Should I capture this as a learning?"
        U->>A: Approve
    else Reconciliation-based
        A->>A: Detect hotfix commits post-completion
        A->>A: Extract learning from fix context
    end

    A->>M: Append to learnings.json (immutable record)
    Note over M: {specId, category, severity,<br/>discovery, prevention, reconsiderWhen}

    Note over U,A: Retrieval — During Phase 1

    U->>A: /specops Add feature touching same files
    A->>M: Read learnings.json
    A->>A: Filter by 5 layers
    Note over A: 1. Proximity (file overlap)<br/>2. Recurrence (pattern count)<br/>3. Severity (critical/high always)<br/>4. Decay/validity (reconsiderWhen)<br/>5. Category match

    A->>A: Surface top N learnings (maxSurfaced: 3)
    A-->>U: "Relevant learnings from prior specs: ..."

    Note over U,A: Supersession — Newer replaces older

    U->>A: /specops learn <spec-name>
    A->>M: Read existing learnings for same topic
    A->>M: Write new learning (supersedes: <old-id>)
    Note over M: Old learning preserved, marked superseded
```

**Source:** [`core/learnings.md`](../core/learnings.md)
