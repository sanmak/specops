## Collaborative Spec Review

### Overview

When `config.team.specReview.enabled` is true (or `config.team.reviewRequired` is true as a fallback), specs go through a collaborative review cycle before implementation. This enables team-based decision making where multiple engineers can review, provide feedback, and approve specs before any code is written.

### Spec Metadata (spec.json)

**Always create** a `spec.json` file in the spec directory at the end of Phase 2, regardless of whether review is enabled. This ensures consistent structure and enables retroactive review enablement.

After creating the spec files, create `spec.json`:

1. RUN_COMMAND(`git config user.name`) to get author name
2. RUN_COMMAND(`git config user.email`) to get author email
3. If git config is unavailable, use "Unknown" for name and "" for email
4. WRITE_FILE(`<specsDir>/<spec-name>/spec.json`) with:

```json
{
  "id": "<spec-name>",
  "type": "<feature|bugfix|refactor>",
  "status": "draft",
  "version": 1,
  "created": "<ISO 8601 timestamp>",
  "updated": "<ISO 8601 timestamp>",
  "author": {
    "name": "<from git config>",
    "email": "<from git config>"
  },
  "reviewers": [],
  "reviewRounds": 0,
  "approvals": 0,
  "requiredApprovals": <from config.team.specReview.minApprovals or 1>
}
```

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
draft → in-review → approved → implementing → completed
              ↑          |
              |          | (changes requested)
              └──────────┘ (revision cycle)
```

- **draft**: Spec just created, not yet submitted for review
- **in-review**: Spec submitted for team review, awaiting approvals
- **approved**: Required approvals met, ready for implementation
- **implementing**: Implementation in progress
- **completed**: Implementation done, all acceptance criteria met

### Mode Detection

When the user invokes SpecOps referencing an existing spec, detect the interaction mode:

1. READ_FILE(`<specsDir>/<spec-name>/spec.json`)
2. RUN_COMMAND(`git config user.email`) to get the current user's email
3. Determine mode:
   - If `spec.json` does not exist → treat as **legacy spec**, proceed with implementation
   - If current user email ≠ `author.email` AND status is `"draft"` or `"in-review"` → **Review mode**
   - If current user email = `author.email` AND status is `"in-review"` AND any reviewer has `"changes-requested"` → **Revision mode**
   - If current user email = `author.email` AND status is `"in-review"` AND no changes requested → **Author waiting** (inform user that review is pending)
   - If status is `"approved"` → **Implement mode**
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
   - Add or update the reviewer entry with name, email, status, reviewedAt, and round
   - If verdict is "Approve" or "Approve with suggestions": set reviewer status to `"approved"`, increment `approvals`
   - If verdict is "Request changes": set reviewer status to `"changes-requested"`
   - If `approvals` >= `requiredApprovals`: set `status` to `"approved"`
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
   - Update `updated` timestamp
6. Regenerate `index.json`
7. Inform the user: "Spec revised to version {version}. Commit and notify reviewers for re-review."

### Implementation Gate

At the start of Phase 3, before any implementation begins:

1. READ_FILE `spec.json` if it exists
2. If spec review is enabled (`config.team.specReview.enabled` or `config.team.reviewRequired`):
   - If `status` is `"approved"`: proceed with implementation, set `status` to `"implementing"`, regenerate `index.json`
   - If `status` is NOT `"approved"`:
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
- NOTIFY_USER: "Late review received during implementation. Feedback has been recorded in reviews.md. Consider addressing in a follow-up."
- Do NOT stop implementation or change status

### Completing a Spec

At the end of Phase 4, after all acceptance criteria are verified:
1. Set `spec.json.status` to `"completed"`
2. Update `updated` timestamp
3. Regenerate `index.json`
