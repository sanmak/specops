# Design: AST-Based Repo Map

## Architecture Overview
The repo map is a machine-generated steering file that provides structural context about the user's codebase. It follows the established three-layer architecture: a new `core/repo-map.md` module defines the generation algorithm using abstract operations, which are substituted during generation into all 4 platform outputs via Jinja2 templates.

The repo map integrates into the existing steering system — it lives at `<specsDir>/steering/repo-map.md` with `inclusion: always` and extended frontmatter fields for staleness tracking. It is loaded automatically in Phase 1 alongside other steering files.

## Technical Decisions

### Decision 1: Agent-Driven Generation (No External Script)
**Context:** The playbook mentions a "hybrid" approach: agent-driven + optional `scripts/repo-map.py` accelerator.
**Options Considered:**
1. Agent-driven only — use LIST_DIR, READ_FILE, RUN_COMMAND abstract ops
2. Hybrid — agent + `scripts/repo-map.py` for faster generation
3. Script-only — `scripts/repo-map.py` called via RUN_COMMAND

**Decision:** Option 1 — Agent-driven only
**Rationale:** Simplicity principle. The agent already has LIST_DIR + RUN_COMMAND for file discovery and AST extraction. A script adds install-path detection complexity and a new dependency pattern that doesn't exist in the current architecture. If generation performance becomes a problem, the script can be added later.

### Decision 2: File Discovery via `git ls-files`
**Context:** Need to discover project files while respecting `.gitignore`.
**Options Considered:**
1. `git ls-files` — uses git's built-in ignore rules
2. LIST_DIR + manual `.gitignore` parsing
3. RUN_COMMAND(`find`) with exclusion patterns

**Decision:** Option 1 with Option 2 as fallback
**Rationale:** `git ls-files` natively respects `.gitignore`, handles nested ignore files, and is available on all platforms with `canAccessGit: true`. For platforms without git, fall back to LIST_DIR with basic `.gitignore` exclusion.

### Decision 3: 4-Tier Language Classification
**Context:** Different languages benefit from different extraction depths.
**Options Considered:**
1. Uniform extraction — same depth for all languages
2. 4-tier — Python (signatures) > TS/JS (exports) > Go/Rust/Java (declarations) > other (path only)
3. Per-language plugins — extensible extraction system

**Decision:** Option 2 — 4-tier
**Rationale:** Covers the most common languages in AI-assisted development. Python gets the deepest extraction because `ast.parse()` is built-in and reliable. TS/JS and Go/Rust/Java use grep-based extraction that's universally available. Avoids over-engineering with plugin systems.

### Decision 4: Staleness via File List Hash (Not Content Hash)
**Context:** Need to detect when the repo map is outdated.
**Options Considered:**
1. Hash of `git ls-files` output — detects file additions/deletions/renames
2. Hash of file contents — detects any change
3. Git commit count since generation

**Decision:** Option 1 — File list hash
**Rationale:** The repo map captures structure (what files exist, what they export), not content. File content changes (bug fixes, refactoring) rarely change the structural map. Hashing only the file list means the map refreshes on structural changes (new files, deleted files, renames) but not on content edits, avoiding unnecessary regeneration.

### Decision 5: Step 3.5 in Phase 1 (Not Renumbering)
**Context:** Where to insert the repo map freshness check in Phase 1.
**Options Considered:**
1. Renumber steps 4-9 to 5-10, insert as new step 4
2. Use "step 3.5" notation between steering (3) and memory (4)
3. Make it a sub-step of step 3

**Decision:** Option 2 — Step 3.5
**Rationale:** Other modules (memory.md) reference "step 4" by number. Renumbering would break those references. Step 3.5 clearly communicates insertion point without cascading changes.

## Component Design

### Component 1: `core/repo-map.md`
**Responsibility:** Defines the repo map format, generation algorithm, staleness detection, scope control, language tiers, `/specops map` subcommand, safety rules, and platform adaptation.
**Interface:** Used by the generator pipeline — included as `{{ repo_map }}` in platform Jinja2 templates. Abstract operations get substituted with platform-specific tool calls.
**Dependencies:** `core/tool-abstraction.md` (abstract ops), `core/steering.md` (storage format), `core/workflow.md` (Phase 1 integration point)

### Component 2: Workflow Integration
**Responsibility:** Two insertion points in `core/workflow.md`:
1. Phase 1, step 3.5: Auto-detect missing/stale repo map, offer generation or auto-refresh
2. Getting Started: Route `/specops map` subcommand (new step 8)
**Dependencies:** `core/repo-map.md` for the actual algorithm

### Component 3: Steering Extension
**Responsibility:** Document three new frontmatter fields in `core/steering.md` for machine-generated steering files: `_generated`, `_generatedAt`, `_sourceHash`.
**Dependencies:** Existing steering file format

### Component 4: Generator Pipeline
**Responsibility:** Wire `repo_map` into generator context dict and add `{{ repo_map }}` to all 4 Jinja2 templates.
**Dependencies:** `generator/generate.py`, `generator/templates/*.j2`

### Component 5: Validator
**Responsibility:** Define `REPO_MAP_MARKERS` and add to both `validate_platform()` and cross-platform consistency check.
**Dependencies:** `generator/validate.py`, `tests/test_platform_consistency.py`

## System Flow

### Repo Map Generation Flow
```
Agent invoked
  → Phase 1, Step 3: Load steering files
  → Step 3.5: Check repo map
    → FILE_EXISTS(repo-map.md)?
      → Yes: Parse frontmatter, check staleness
        → Stale? → Regenerate + NOTIFY_USER
        → Fresh? → Already loaded in step 3, continue
      → No: Offer generation (interactive) / tip (non-interactive)
        → Generate? → Run generation algorithm → WRITE_FILE
  → Step 4: Load memory (continues normally)
```

### Generation Algorithm
```
1. RUN_COMMAND(git ls-files) or LIST_DIR fallback
2. Exclude: specsDir/, node_modules/, .git/, __pycache__/, etc.
3. Apply scope: max 100 files, depth 3
4. Build directory tree
5. For each file:
   - .py → RUN_COMMAND(python3 -c "ast.parse...") → signatures
   - .ts/.js/.tsx/.jsx → RUN_COMMAND(grep "^export ") → exports
   - .go/.rs/.java → RUN_COMMAND(grep "^func\|^fn\|^pub") → declarations
   - other → path only
6. Enforce token budget (~3000 tokens) with tiered truncation
7. Compute _sourceHash from sorted file list
8. WRITE_FILE(repo-map.md) with frontmatter + body
```

### `/specops map` Subcommand Flow
```
User: /specops map
  → Detect "map" pattern in Getting Started routing
  → Read config for specsDir
  → If repo-map.md exists: show metadata, then regenerate
  → If not: generate fresh
  → Display summary: N files mapped, D directories
```

## Repo Map Output Format

```yaml
---
name: "Repo Map"
description: "Machine-generated structural map of the codebase"
inclusion: always
_generated: true
_generatedAt: "2026-03-14T12:00:00Z"
_sourceHash: "a1b2c3d4..."
---
```

```markdown
## Project Structure Map

> Auto-generated by SpecOps. Do not edit manually — run `/specops map` to refresh.

### Directory Tree

<root>/
  src/
    components/
    utils/
  tests/
  docs/

### File Declarations

#### src/ (12 files)

- `app.ts`
  - `export function createApp()`
  - `export const config`
- `server.ts`
  - `export function startServer(port: number)`

#### tests/ (4 files)

- `app.test.ts`
- `server.test.ts`
```

## Security Considerations
- **Path containment**: Generated file paths must not contain `../` or absolute paths
- **No secrets**: Map content is structural only — no file contents beyond declarations. If a declaration line appears to contain a secret (API key pattern, connection string), skip that line
- **Convention sanitization**: Same rules as steering files — if map content appears to contain meta-instructions, skip

## Testing Strategy
- **Validator tests**: REPO_MAP_MARKERS present in all 4 platform outputs
- **Cross-platform consistency**: Same markers across all platforms
- **Build test**: `generator/generate.py --all` succeeds with new module
- **No raw abstract ops**: validator confirms all READ_FILE/LIST_DIR/etc. are substituted

## Ship Plan
1. Create core module (Task 1)
2. Wire workflow + steering (Tasks 2-3, parallel)
3. Wire generator pipeline (Task 4)
4. Add validator markers (Task 5)
5. Regenerate and validate (Task 6)
6. Update docs (Task 7)

## Risks & Mitigations
- **Python `ast.parse()` unavailable** → graceful fallback to path-only listing
- **Large repos exceed 100-file limit** → NOTIFY_USER with cap warning; future configurable limit
- **Validator marker mismatch** → Task 5 adds to BOTH per-platform AND cross-platform (Gap 31 lesson)
- **Step renumbering cascade** → use step 3.5 notation; explicitly renumber Getting Started steps
