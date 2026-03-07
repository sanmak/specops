## Collaborative Spec Review

### Overview

When `config.team.specReview.enabled` is true (or `config.team.reviewRequired` is true as a fallback), specs go through a collaborative review cycle before implementation. This enables team-based decision making where multiple engineers can review, provide feedback, and approve specs before any code is written.

### Spec Metadata (spec.json)

**Always create** a `spec.json` file in the spec directory at the end of Phase 2, regardless of whether review is enabled. This ensures consistent structure and enables retroactive review enablement.

After creating the spec files, create `spec.json`:

1. RUN_COMMAND(`git config user.name`) to get author name
2. If git config is unavailable, use "Unknown" for name
3. WRITE_FILE(`<specsDir>/<spec-name>/spec.json`) with:

```json
{
  "id": "<spec-name>",
  "type": "<feature|bugfix|refactor>",
  "status": "draft",
  "version": 1,
  "created": "<ISO 8601 timestamp>",
  "updated": "<ISO 8601 timestamp>",
  "specopsCreatedWith": "<version from this instruction file's frontmatter>",
  "specopsUpdatedWith": "<version from this instruction file's frontmatter>",
  "author": {
    "name": "<from git config>"
  },
  "reviewers": [],
  "reviewRounds": 0,
  "approvals": 0,
  "requiredApprovals": <from config.team.specReview.minApprovals or 1>
}
```

The `specopsCreatedWith` field is set once at creation and never modified. The `specopsUpdatedWith` field is updated every time `spec.json` is modified (reviews, revisions, status changes, completion). Both values come from reading this instruction file's own YAML frontmatter `version:` field.

If spec review is enabled, immediately set `status` to `"in-review"` and `reviewRounds` to `1`.

### Global Index (index.json)

After creating or updating any `spec.json`, regenerate the global index:

1. LIST_DIR(`<specsDir>`) to find all spec directories
2. For each directory, READ_FILE(`<specsDir>/<dir>/spec.json`) if it exists
3. Collect summary fields: `id`, `type`, `status`, `version`, `author` (name only), `updated`
4. WRITE_FILE(`<specsDir>/index.json`) with the collected summaries as a JSON array

The index is a **derived file** — per-spec `spec.json` files are the source of truth. If `index.json` has a merge conflict or is missing, regenerate it from per-spec files.

### Status Lifecycle

```
draft → in-review → approved       → implementing → completed
              ↑    ↘ self-approved ↗
              |          |
              └──────────┘ (revision cycle)
```

- **draft**: Spec just created, not yet submitted for review
- **in-review**: Spec submitted for team review, awaiting approvals
- **approved**: Required approvals met (at least one peer approval), ready for implementation
- **self-approved**: Author self-approved (via `allowSelfApproval: true`). Ready for implementation, but no peer review was performed
- **implementing**: Implementation in progress
- **completed**: Implementation done, all acceptance criteria met

### Mode Detection

When the user invokes SpecOps referencing an existing spec, detect the interaction mode. Rules are evaluated top-down — first match wins. Every combination of inputs maps to exactly one mode.

1. READ_FILE(`<specsDir>/<spec-name>/spec.json`)
2. **Validate spec.json**: If the file does not exist, or contains invalid JSON, or is missing required fields (`id`, `type`, `status`, `author`), or `status` is not a valid enum value (`draft`, `in-review`, `approved`, `self-approved`, `implementing`, `completed`) → treat as **legacy spec**, proceed with implementation. If the file existed but was invalid, NOTIFY_USER: "spec.json is invalid — proceeding without review tracking. Re-run `/specops` on this spec to regenerate it."
3. RUN_COMMAND(`git config user.name`) to get the current user's name
   **Limitation**: `user.name` is less unique than email — two users with the same git display name will be treated as the same identity. This trade-off was made to avoid storing PII (email addresses) in spec metadata. For teams where name collisions are a concern, use distinct display names in git config.
4. Determine mode:
   - If current user name ≠ `author.name` AND status is `"draft"` or `"in-review"` → **Review mode**
   - If current user name = `author.name` AND status is `"in-review"` AND any reviewer has `"changes-requested"` → **Revision mode**
   - If current user name = `author.name` AND status is `"draft"` or `"in-review"` AND `config.team.specReview.allowSelfApproval` is `true` → **Self-review mode**
   - If current user name = `author.name` AND status is `"draft"` or `"in-review"` → **Author waiting**. Message varies by status:
     - `"draft"`: "Your spec is in draft. Submit it for review to get team feedback, or enable `allowSelfApproval: true` in `.specops.json` for solo workflows."
     - `"in-review"`: "Your spec is awaiting review from teammates. Tip: enable `allowSelfApproval: true` in `.specops.json` for solo workflows."
   - If status is `"approved"` or `"self-approved"` → **Implement mode**
   - If status is `"implementing"` → **Continue implementation**
   - If status is `"completed"` → inform user that spec is already completed

### Review Mode

When entering review mode:

1. Read all spec files (requirements/bugfix/refactor, design, tasks) and present a structured summary
2. ASK_USER: "Would you like to review section-by-section or provide overall feedback?"
3. Collect feedback:
   - For section-by-section: walk through each file and section, ASK_USER for comments
   - For overall: ASK_USER for general feedback on the entire spec
4. ASK_USER for verdict: "Approve", "Approve with suggestions", or "Request changes"
5. WRITE_FILE or EDIT_FILE `reviews.md` — append feedback under the current review round (see reviews.md template)
6. EDIT_FILE `spec.json`:
   - Add or update the reviewer entry with name, status, reviewedAt, and round
   - If verdict is "Approve" or "Approve with suggestions": set reviewer status to `"approved"`, increment `approvals`
   - If verdict is "Request changes": set reviewer status to `"changes-requested"`
   - If `approvals` >= `requiredApprovals`: set `status` to `"approved"`
   - Update `specopsUpdatedWith` to the current SpecOps version (from this instruction file's frontmatter `version:` field)
   - Update `updated` timestamp
7. Regenerate `index.json`

**On platforms without interactive questions (canAskInteractive: false):**
- Parse the user's initial prompt for feedback content and verdict
- If the prompt contains explicit feedback and a clear verdict (e.g., "approve", "request changes"), process it
- If the prompt lacks a clear verdict, write the feedback to `reviews.md` with reviewer status `"pending"` and note: "Human reviewer should confirm verdict."

### Revision Mode

When the spec author returns to a spec with outstanding change requests:

1. READ_FILE `reviews.md` and present a summary of requested changes from the latest round
2. Help the author understand and address each feedback item
3. ASK_USER which feedback items to address (or address all)
4. Assist in revising the spec files based on feedback
5. After revisions:
   - Increment `version` in `spec.json`
   - Increment `reviewRounds`
   - Reset `approvals` to `0`
   - Reset all reviewer statuses to `"pending"`
   - Keep `status` as `"in-review"`
   - Update `specopsUpdatedWith` to the current SpecOps version (from this instruction file's frontmatter `version:` field)
   - Update `updated` timestamp
6. Regenerate `index.json`
7. Inform the user: "Spec revised to version {version}. Commit and notify reviewers for re-review."

### Self-Review Mode

When the spec author reviews their own spec (self-review enabled via `allowSelfApproval: true`):

1. Read all spec files (requirements/bugfix/refactor, design, tasks) and present a structured summary
2. NOTIFY_USER: "Self-review mode: You are reviewing your own spec. This will be recorded as a self-review."
3. If status is `"draft"`, transition to `"in-review"` and set `reviewRounds` to `1`
4. ASK_USER: "Would you like to review section-by-section or provide overall feedback?"
5. Collect feedback:
   - For section-by-section: walk through each file and section, ASK_USER for comments
   - For overall: ASK_USER for general feedback on the entire spec
6. ASK_USER for verdict: "Self-approve", "Self-approve with notes", or "Revise"
7. WRITE_FILE or EDIT_FILE `reviews.md` — append feedback under the current review round:
   - Header: `## Self-Review by {author.name} (Round {round})`
   - Content: feedback notes
   - Verdict line: "Self-approved", "Self-approved with notes", or "Revision needed"
8. EDIT_FILE `spec.json`:
   - Add reviewer entry: `{ "name": "<author.name>", "status": "approved", "selfApproval": true, "reviewedAt": "<ISO 8601>", "round": <round> }`
   - If verdict is "Self-approve" or "Self-approve with notes": increment `approvals`
   - If `approvals` >= `requiredApprovals`:
     - If all reviewer entries with `status: "approved"` have `selfApproval: true` → set spec `status` to `"self-approved"`
     - If at least one reviewer entry with `status: "approved"` does NOT have `selfApproval: true` → set spec `status` to `"approved"`
   - If verdict is "Revise": author edits spec, stay in current status for another round
   - Update `specopsUpdatedWith` to the current SpecOps version (from this instruction file's frontmatter `version:` field)
   - Update `updated` timestamp
9. Regenerate `index.json`

**On platforms without interactive questions (canAskInteractive: false):**
- Parse the user's initial prompt for self-review feedback and verdict
- If the prompt contains a clear self-approval intent, process it
- If the prompt lacks a clear verdict, write the feedback to `reviews.md` with reviewer status `"pending"` and note: "Author should confirm self-review verdict."

### Implementation Gate

At the start of Phase 3, before any implementation begins:

1. READ_FILE `spec.json` if it exists
2. If spec review is enabled (`config.team.specReview.enabled` or `config.team.reviewRequired`):
   - If `status` is `"approved"` or `"self-approved"`: proceed with implementation. If `status` is `"self-approved"`, NOTIFY_USER: "Note: This spec was self-approved without peer review." Set `status` to `"implementing"`, update `specopsUpdatedWith` to the current SpecOps version, update `updated` timestamp, regenerate `index.json`.
   - If `status` is NOT `"approved"` and NOT `"self-approved"`:
     - On interactive platforms: NOTIFY_USER with current status and approval count (e.g., "This spec has 1/2 required approvals."), then ASK_USER "Do you want to proceed anyway? This overrides the review requirement."
     - On non-interactive platforms: NOTIFY_USER("Cannot proceed: spec requires approval. Current status: {status}, approvals: {approvals}/{requiredApprovals}") and STOP
3. If spec review is not enabled: set `status` to `"implementing"` and proceed

### Status Dashboard

When the user requests spec status (`/specops status` or "show specops status"):

1. READ_FILE `<specsDir>/index.json` if it exists
2. If `index.json` does not exist or is invalid, scan `<specsDir>/*/spec.json` to rebuild it
3. Present a formatted status table showing each spec's id, status, approval count, and version
4. Show summary counts: total specs, and count per status
5. If a status filter is provided (e.g., `/specops status in-review`), show only matching specs
6. On interactive platforms: ASK_USER if they want to drill into a specific spec for details
7. On non-interactive platforms: print the table

### Late Review Handling

If a review is submitted while `spec.json.status` is `"implementing"`:
- Append the review to `reviews.md` as normal
- Update the reviewer entry in `spec.json`
- Update `specopsUpdatedWith` to the current SpecOps version and `updated` timestamp
- NOTIFY_USER: "Late review received during implementation. Feedback has been recorded in reviews.md. Consider addressing in a follow-up."
- Do NOT stop implementation or change status

### Completing a Spec

At the end of Phase 4, after all acceptance criteria are verified:
1. Set `spec.json.status` to `"completed"`
2. Update `specopsUpdatedWith` to the current SpecOps version (from this instruction file's frontmatter `version:` field)
3. Update `updated` timestamp
4. Regenerate `index.json`
