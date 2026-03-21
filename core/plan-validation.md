## Code-Grounded Plan Validation

Code-grounded plan validation verifies that file paths and code references in spec artifacts (design.md, tasks.md) actually exist in the codebase before Phase 3 implementation begins. This complements coherence verification (Phase 2 step 5.5, which checks NFR/design logic contradictions) with reference accuracy — catching wrong paths, renamed files, and non-existent modules before implementation effort is wasted. The repo map (loaded in Phase 1 step 3.5) serves as the primary lookup source.

### Validation Scope

What gets validated:
1. File paths from `**Files to Modify:**` sections in `tasks.md` — each path is the text after the colon, trimmed, with leading/trailing backticks removed
2. File paths from sections in `design.md` containing "Files" or "Affected Files" in the heading
3. Function/class/method references in backtick code spans in design.md and tasks.md (e.g., `UserService.authenticate()`, `formatDate()`)

Exclusions:
- Paths marked as NEW files to create. Detection heuristic: if the task's Implementation Steps contain "create", "add new file", "scaffold", or "new" referencing that path, skip validation for it.
- References in spec templates (requirement descriptions, acceptance criteria text) — only design.md and tasks.md are validated.
- Paths that are clearly directory references (ending with `/`) — these are informational, not file references.

### Validation Procedure

Runs as Phase 2 step 5.7, after coherence verification (5.5) and vocabulary verification (5.6), gated by `config.implementation.validateReferences`:

1. If `config.implementation.validateReferences` is `"off"`, skip this step entirely.
2. READ_FILE(`<specsDir>/<spec-name>/tasks.md`) — extract all file paths from `**Files to Modify:**` lines.
3. READ_FILE(`<specsDir>/<spec-name>/design.md`) — extract file paths from sections containing "Files" in the heading. Also extract backtick-enclosed references.
4. For each extracted reference, apply the Reference Resolution procedure below.
5. Classify results and take action based on `validateReferences` level:
   - `"warn"`: NOTIFY_USER with a summary of unresolved references. Continue to next step.
   - `"strict"`: NOTIFY_USER with unresolved references. If any file path is unresolved AND not marked as a new file to create:
     - If `canAskInteractive` is true: ASK_USER("Plan references {N} file(s) that don't exist. Fix the spec before implementation, or proceed anyway?")
     - If `canAskInteractive` is false: NOTIFY_USER("Plan references {N} non-existent file(s). Proceeding with assumptions noted.") and continue (cannot block non-interactive platforms).

### Reference Resolution

For each extracted reference:

1. **Repo map lookup**: If `<specsDir>/steering/repo-map.md` was loaded in Phase 1, search its File Declarations for a matching path or symbol. A match means the reference is valid.
2. **FILE_EXISTS fallback**: If not found in the repo map, check FILE_EXISTS(`<path>`) for file paths. For symbol references (function/class names), this is a repo-map-only check — symbols not in the map are flagged as "not found in repo map" rather than definitively unresolved.
3. **Prefix normalization**: If the path starts with `./`, strip the prefix and retry. If the path does not match, attempt common prefix adjustments (e.g., strip leading `src/` if the project root contains the file directly).

Classification:
- **Resolved**: Found in repo map or confirmed via FILE_EXISTS
- **Unresolved**: Not found in repo map AND FILE_EXISTS returns false AND not a new-file path
- **New file**: Detected by the new-file heuristic (skip validation)
- **Symbol only**: Backtick reference not found in repo map (advisory — never blocks)

### Validation Outcomes

Record results in `implementation.md` under `## Phase 1 Context Summary`:

```
- Plan validation: [pass — N references validated / warn — M unresolved of N / strict-blocked — M unresolved of N, user intervention required]
```

For `"warn"` mode with unresolved references, the notification includes each unresolved path and a suggestion: the closest match from the repo map or directory listing if available.

### Plan Validation Safety

- **Path containment**: Validated paths must be relative paths within the project root. Paths starting with `/` (absolute) are flagged as invalid. Paths containing `../` traversal sequences are rejected outright.
- **READ_FILE guard**: Before reading any user-supplied path for validation, verify: (1) path is relative, (2) path is contained under the project root, (3) path does not contain `../` traversal. This aligns with the path safety rules in the Safety module.
- **No network calls**: Validation uses only local file system checks and the repo map. No external API calls or network requests.
- **Non-blocking by default**: The `"warn"` mode (and `"off"` mode) never blocks implementation. Only `"strict"` mode on interactive platforms blocks — and even then, the user can override.

### Platform Adaptation

| Capability | Impact |
|-----------|--------|
| `canAskInteractive: true` | In strict mode, ASK_USER before blocking |
| `canAskInteractive: false` | In strict mode, note unresolved references as assumptions and proceed |
| `canAccessGit: true` | No special impact — validation uses FILE_EXISTS and repo map, not git |

No platform-specific fallbacks needed for warn/off modes. Strict mode degrades gracefully on non-interactive platforms.
