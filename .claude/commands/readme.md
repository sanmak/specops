Audit and rewrite a project README for maximum clarity, value proposition, and developer conversion, using principles from Steve Jobs, David Ogilvy, Seth Godin, Simon Sinek, Paul Graham, George Orwell, and Jeff Bezos.

## Instructions

Follow these steps precisely. This command evaluates a README against 8 dimensions drawn from marketing, writing, and open-source best practices, then generates a rewritten version optimized for the "star-or-bounce" moment.

### Step 1: Read current README

Read `README.md` in the project root. If none exists, note "No README found" and switch to create mode (skip the scorecard, go directly to Step 4).

Also read any available project context: package.json, pyproject.toml, Cargo.toml, CLAUDE.md, or similar config files that reveal what the project does, its dependencies, and its target audience.

### Step 2: Score against the README scorecard

Evaluate the current README on 8 dimensions. Each dimension is informed by a specific leader or pattern:

1. **Hook** (Steve Jobs, David Ogilvy): Does the first visible line name a problem or benefit? Not a feature description, not "A framework for X." The headline does 80% of the work. One big idea, not ten features.

2. **Tagline** (Steve Jobs): Is there a single sentence under 10 words that captures the core value? "1000 songs in your pocket" not "5GB hard drive with FireWire."

3. **Problem statement** (Simon Sinek): Does it articulate WHY this exists before WHAT it does? People don't care what you built until they feel the pain it solves. No product name in the first sentence of the problem.

4. **Proof** (Seth Godin): Is there a before/after, demo, screenshot, dogfood section, or usage example? Claims cost nothing. Evidence costs credibility. If it's remarkable, show it.

5. **Getting started** (Supabase/shadcn pattern): Can someone install and try it in under 5 minutes with 3 or fewer commands? If getting started requires reading docs first, it's too long.

6. **Scanability** (Paul Graham, George Orwell): Short sentences, tables over paragraphs, no jargon in the first 200 words. Write like you talk. Cut every word that does not change the meaning. Never use a long word where a short one will do.

7. **Positioning** (David Ogilvy): Does it say what only THIS project does, not what the category does? Lead with the benefit, not the feature. "Firebase features on open source tools" not "A backend platform."

8. **Conciseness** (George Orwell, Jeff Bezos): Is architecture/contributor content in docs, not README? Is it under 200 lines? Narrative structure over bullet-point catalogs. If you can cut a section without losing user value, cut it.

Score each dimension as: **Strong**, **Weak**, or **Missing**.

### Step 3: Present the scorecard

Show the findings as a table:

```text
README Scorecard
================

| #  | Dimension         | Principle (source)          | Score   | Finding                                      |
|----|-------------------|-----------------------------|---------|----------------------------------------------|
| 1  | Hook              | Jobs/Ogilvy                 | Weak    | Opens with feature description, not problem  |
| 2  | Tagline           | Jobs                        | Missing | No one-liner tagline                         |
| 3  | Problem statement | Sinek                       | Missing | Jumps to features without explaining the pain|
| 4  | Proof             | Godin                       | Weak    | Has a diagram but no before/after contrast   |
| 5  | Getting started   | Supabase/shadcn             | Strong  | 3 commands, clean                            |
| 6  | Scanability       | Graham/Orwell               | Weak    | Long paragraphs, jargon in first 200 words   |
| 7  | Positioning       | Ogilvy                      | Weak    | Lists category features, not unique value    |
| 8  | Conciseness       | Orwell/Bezos                | Weak    | Architecture internals in README (move to docs)|

Overall: 1/8 Strong, 5/8 Weak, 2/8 Missing
```

### Step 4: Identify the one big idea

Read the project's source code, config files, and any existing documentation. Understand what problem it solves and for whom.

Propose 3 tagline candidates, each under 10 words:

```text
Tagline candidates:
1. "Make your AI agent think before it codes."
2. "Structured specs for AI agents. Think first, code right."
3. "Stop correcting your AI. Start directing it."
```

Ask the user to pick one or suggest their own.

### Step 5: Draft the problem statement

Write 2-3 sentences that articulate the pain. Rules:

- First sentence: describe the frustration without naming the product
- Second sentence: make it concrete and visceral (a scenario the reader recognizes)
- Third sentence (optional): the reframe. "The problem isn't X. It's Y."

### Step 6: Draft the solution statement

Write the solution block:

- One sentence: what the project does (verb-first, active voice)
- Numbered list: key phases or capabilities (max 5 items)
- One line: platform/compatibility/reach

### Step 7: Draft the before/after

Create a concrete before/after comparison:

- Pick a realistic scenario from the project's domain
- "Without [project]:" shows the pain (3-4 lines)
- "With [project]:" shows the transformation (4-5 lines)
- Use code blocks for both sides

### Step 8: Build the capabilities table

Convert features into a problem-solution table. Format:

```text
| Problem | How [project] handles it |
|---|---|
| [Reader's pain point] | [Feature framed as solution] |
```

Every row must start with the reader's pain, never the tool's feature. Maximum 7 rows. If a feature cannot be tied to a user pain point, leave it out of the README (it belongs in docs).

### Step 9: Assemble and present the full draft

Compose the complete README following this structure:

1. Logo/title + tagline (centered)
2. Badges (keep only user-facing: CI, release, stars, license)
3. Problem statement (2-3 sentences, no product name first)
4. Solution statement (what it does + key phases)
5. Quick Start with installation (under 3 commands to try it)
6. Before/After comparison
7. Capabilities table (problems solved)
8. Dogfood/proof section (if applicable)
9. Unique positioning ("What only [project] does")
10. Platforms/compatibility (if multi-platform)
11. Configuration (brief, link to docs for details)
12. Contributing + License

Re-evaluate the scorecard against the new draft and present both side by side.

Style rules for the draft:

- No em dashes. Use periods, colons, or restructured sentences.
- No jargon in the first 200 words.
- Every feature mention must be anchored to a problem it solves.
- Architecture and contributor docs belong in linked pages, not README.
- Tables over bullet lists for scanability.
- Proof over promise: show real output, not claims.
- Target under 200 lines total.

### Step 10: Apply on approval

Ask the user using AskUserQuestion:

**Question**: "How would you like to apply the README update?"

**Options**:

- **Apply the full rewrite** — Replace README.md with the new version
- **Iterate on specific sections** — Tell me which sections to adjust
- **Skip** — Keep the current README unchanged

On approval, write the new README.md. After writing, report the before/after line count and scorecard improvement.
