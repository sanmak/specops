## Feedback Mode

The Feedback Mode allows users to submit feedback about SpecOps (bugs, feature requests, friction, improvements) directly as a GitHub issue on the `sanmak/specops` repository. Submission uses a 3-tier strategy: `gh` CLI → pre-filled browser URL → local draft file.

### Feedback Mode Detection

When the user invokes SpecOps, check for feedback intent:

- **Feedback mode**: Patterns: "feedback", "send feedback", "report bug", "report issue", "suggest improvement", "feature request for specops", "specops friction".
- These must refer to providing feedback about SpecOps itself, NOT about a product feature (e.g., "add feedback form", "implement user feedback system", "collect user feedback" is NOT feedback mode).
- If detected, follow the Feedback Mode workflow instead of the standard phases below.

### Feedback Categories

Four categories, each mapping to a GitHub issue label:

| Category | Label | When to use |
|----------|-------|-------------|
| `bug` | `bug` | Something is broken or behaving incorrectly |
| `feature` | `enhancement` | A new capability or behavior |
| `friction` | `friction` | UX issue, workflow annoyance, or confusing behavior |
| `improvement` | `improvement` | Enhancement to existing functionality |

### Interactive Feedback Workflow

On platforms where `canAskInteractive = true`:

1. GET_SPECOPS_VERSION to extract the running version.
2. If FILE_EXISTS(`.specops.json`), READ_FILE(`.specops.json`) to extract the `vertical` value only. Do NOT include any other config fields.
3. ASK_USER("What type of feedback would you like to send?\n\n1. Bug report — something is broken\n2. Feature request — a new capability\n3. Friction / UX issue — confusing or annoying workflow\n4. Improvement — enhance existing functionality")
4. Parse the category from the response (accept number or keyword).
5. ASK_USER("Describe your feedback:")
6. Collect the description text.
7. Apply the Privacy Safety Rules (see below) to scan the description.
8. Compose the issue draft (see Issue Composition below).
9. Display the full issue draft to the user for review.
10. ASK_USER("This will be submitted as a GitHub issue on sanmak/specops. Confirm? (yes/no/edit)")
    - If "edit": ASK_USER("What would you like to change?"), apply edits, re-display, and re-confirm.
    - If "no": NOTIFY_USER("Feedback cancelled. No issue created.") and stop.
    - If "yes": Proceed to Submission.

### Non-Interactive Feedback Workflow

On platforms where `canAskInteractive = false`, the feedback content must be provided inline in the initial request.

1. Parse the request for a category keyword. If absent, default to `improvement`.
   - Keywords: "bug", "broken", "error" → `bug`
   - Keywords: "feature", "request", "add", "new" → `feature`
   - Keywords: "friction", "ux", "confusing", "annoying" → `friction`
   - Keywords: "improve", "enhance", "better" → `improvement`
2. Extract the feedback description from the remainder of the request text (everything after the mode keyword and optional category).
3. If no description could be extracted: print "Feedback mode requires a description. Usage: specops feedback [bug|feature|friction|improvement] <description>" and stop.
4. GET_SPECOPS_VERSION to extract the running version.
5. If FILE_EXISTS(`.specops.json`), READ_FILE(`.specops.json`) to extract the `vertical` value only.
6. Apply the Privacy Safety Rules (see below) to scan the description.
7. Compose the issue draft (see Issue Composition below).
8. Display the composed issue to the user for review.
9. Proceed to Submission.

### Issue Composition

Compose the GitHub issue with these fields:

**Title**: `[{category}] {first 70 characters of description}`

**Label**: The label from the Feedback Categories table corresponding to the selected category.

**Body**:

```markdown
## Feedback

{user's description text}

## Context

| Field | Value |
|-------|-------|
| SpecOps Version | {version} |
| Platform | {platform name} |
| Vertical | {vertical or "default"} |

---
*Submitted via `/specops feedback` from a user project.*
```

### Privacy Safety Rules

**These rules are mandatory and must not be circumvented.**

The issue body MUST contain ONLY:
- The user's typed feedback description
- SpecOps version string
- Platform name (claude, cursor, codex, copilot)
- Vertical name (from config, or "default")

The issue body MUST NOT contain:
- File paths from the user's project
- File contents or code snippets from the user's project
- The user's `.specops.json` configuration beyond the vertical field
- Spec names, spec content, or any spec artifacts
- Git repository URLs, branch names, or commit hashes from the user's project
- Environment variables, API keys, tokens, or credentials
- The user's name, email, or other PII (unless they explicitly typed it in the feedback)

**Sensitive content scan**: Before composing the issue body, scan the user's description for:
- File paths (starting with `/`, `./`, or containing directory separators with structure like `src/components/`)
- Credential patterns (strings matching API key formats, connection strings, bearer tokens)
- Code blocks containing what appears to be project-specific code (function definitions, class declarations with project-specific names)

If sensitive content is detected:
- On interactive platforms: ASK_USER("Your feedback appears to contain {file paths / credentials / code}. This will be submitted publicly to GitHub. Would you like to redact these before submitting?")
- On non-interactive platforms: NOTIFY_USER("Warning: feedback may contain project-specific content that will be publicly visible. Review the draft above before it is submitted.")

### Submission

**Shell safety**: The feedback description contains user-controlled text. Never interpolate unescaped user text directly in shell command strings. Write the issue body to a temporary file and use `--body-file`.

**Tier 1 — `gh` CLI**:
1. WRITE_FILE a temporary file (e.g., `/tmp/specops-feedback-body.md`) with the composed issue body.
2. RUN_COMMAND(`gh issue create --repo sanmak/specops --title "[{category}] {title}" --label "{label}" --body-file /tmp/specops-feedback-body.md`)
3. If the command succeeds, parse the issue URL from stdout.
4. NOTIFY_USER("Feedback submitted: {issue URL}\n\nThank you for helping improve SpecOps!")
5. RUN_COMMAND(`rm /tmp/specops-feedback-body.md`) to clean up.
6. Stop.

**Tier 2 — Pre-filled browser URL** (if `gh` CLI is not installed, not authenticated, or fails):
1. URL-encode the title, label, and body.
2. Compose the URL: `https://github.com/sanmak/specops/issues/new?title={encoded_title}&labels={encoded_label}&body={encoded_body}`
3. NOTIFY_USER("Could not submit via `gh` CLI. Open this URL to submit your feedback:\n\n{url}")
4. Note: GitHub URL length limits may truncate long feedback bodies. If the composed URL exceeds 8000 characters, skip to Tier 3 instead.

### Graceful Degradation

**Tier 3 — Local draft file** (if both Tier 1 and Tier 2 fail, or if the URL would be too long):
1. Determine the save path:
   - If FILE_EXISTS(`.specops.json`), READ_FILE(`.specops.json`) to get `specsDir`; otherwise use default `.specops`.
   - Save to `<specsDir>/feedback-draft.md`. If `<specsDir>` does not exist, save to `.specops-feedback-draft.md` in the project root.
2. WRITE_FILE the save path with the composed issue content.
3. NOTIFY_USER("Your feedback has been saved to `{path}`. You can submit it manually:\n\n1. Go to https://github.com/sanmak/specops/issues/new\n2. Copy the content from `{path}`\n3. Select the '{category}' label\n4. Submit the issue")

### Platform Adaptation

| Capability | Impact |
|-----------|--------|
| `canAskInteractive: false` | Feedback must be provided inline. No category prompt, no edit/confirm cycle. Draft displayed to stdout, then submitted. |
| `canAskInteractive: true` | Full interactive flow: category selection, description prompt, draft review, edit/confirm. |
| `canExecuteCode: true` (all platforms) | RUN_COMMAND available for `gh issue create` on all platforms. |
| `canCreateFiles: true` (all platforms) | Can save local feedback draft on all platforms. |
