Check for stale documentation after code changes and propose updates for approval.

## Instructions

Follow these steps precisely. This command detects documentation that has fallen out of sync with the codebase and proposes targeted fixes.

### Step 1: Determine change scope

Identify what has changed in the codebase. Use `$ARGUMENTS` if provided as a custom git range (e.g., `HEAD~3..HEAD` or a branch name). Otherwise, default to the last commit plus any uncommitted changes.

```bash
# Last commit changes
git diff --name-only HEAD~1..HEAD

# Uncommitted changes (staged + unstaged)
git diff --name-only HEAD

# Detect renames and deletions specifically
git diff --diff-filter=RD --name-only HEAD~1..HEAD
```

Combine all results into a single deduplicated list of changed files.

### Step 2: Match against dependency map

For each changed file, check which documentation may be affected using this mapping:

| Source files changed | Docs to check |
| --- | --- |
| `.claude/commands/*.md` | `CLAUDE.md` (Custom Slash Commands table), `docs/COMMANDS.md` |
| `schema.json` | `docs/REFERENCE.md` (config options), `README.md` (Configuration section), example configs `examples/*.json` |
| `spec-schema.json`, `index-schema.json` | `docs/REFERENCE.md` (spec structure), example specs `examples/specs/` |
| `core/workflow.md` | `README.md` (How It Works), `docs/REFERENCE.md` (Workflow Phases), `CLAUDE.md` (Architecture) |
| `core/review-workflow.md` | `docs/TEAM_GUIDE.md`, `README.md` (Team Review Workflow) |
| `core/safety.md` | `CLAUDE.md` (Security-Sensitive Files), `SECURITY.md` |
| `core/verticals.md` | `README.md` (Vertical Adaptation), `docs/REFERENCE.md` |
| `core/interview.md` | `docs/COMMANDS.md` (Interview Mode) |
| `core/init.md` | `QUICKSTART.md`, `docs/COMMANDS.md` |
| `platforms/*/platform.json` | `README.md` (Platforms table), `docs/STRUCTURE.md`, `CLAUDE.md` (Platform Capabilities) |
| New platform directory under `platforms/` | `README.md`, `CLAUDE.md` (Adding a New Platform), `docs/STRUCTURE.md`, `CONTRIBUTING.md` |
| `generator/generate.py`, `generator/validate.py` | `CLAUDE.md` (Key Commands, Validation), `docs/STRUCTURE.md` |
| `scripts/*.sh` | `CLAUDE.md` (Key Commands), `QUICKSTART.md` |
| `hooks/*` | `CLAUDE.md` (Security-Sensitive Files) |
| `core/templates/*.md` | `docs/REFERENCE.md` (Spec Templates), example specs |
| `setup.sh`, `scripts/remote-install.sh` | `QUICKSTART.md` (Installation), `README.md` (Quick Start) |
| `.github/workflows/*.yml` | `CLAUDE.md` (CI Notes), `CONTRIBUTING.md` |
| `core/config-handling.md` | `docs/REFERENCE.md` (Configuration Options) |
| `core/custom-templates.md` | `docs/REFERENCE.md` (Spec Templates) |
| `core/data-handling.md` | `CLAUDE.md` (Security-Sensitive Files) |
| `core/dependency-safety.md` | `CLAUDE.md` (Security-Sensitive Files, core modules list), `docs/REFERENCE.md` (Configuration Options), `docs/STRUCTURE.md` |
| `core/dependency-introduction.md` | `CLAUDE.md` (core modules list), `docs/STRUCTURE.md` |
| `core/evaluation.md` | `CLAUDE.md` (core modules list), `docs/REFERENCE.md` (Configuration Options), `docs/STRUCTURE.md` |
| `core/learnings.md` | `CLAUDE.md` (core modules list), `docs/REFERENCE.md` (Configuration Options), `docs/STRUCTURE.md`, `docs/COMMANDS.md` (Learn) |
| `core/error-handling.md` | `docs/REFERENCE.md` |
| `core/feedback.md` | `docs/COMMANDS.md` (Send Feedback) |
| `core/from-plan.md` | `docs/COMMANDS.md` (From Plan) |
| `core/memory.md` | `docs/COMMANDS.md` (Local Memory), `docs/REFERENCE.md` |
| `core/metrics.md` | `docs/REFERENCE.md` (Usage Metrics), `docs/TOKEN-USAGE.md` |
| `core/run-logging.md` | `docs/REFERENCE.md` (Configuration Options) |
| `core/plan-validation.md` | `docs/REFERENCE.md` (Configuration Options) |
| `core/git-checkpointing.md` | `docs/REFERENCE.md` (Configuration Options) |
| `core/pipeline.md` | `docs/COMMANDS.md` (Pipeline Mode), `docs/REFERENCE.md` |
| `core/reconciliation.md` | `docs/COMMANDS.md` (Drift Detection) |
| `core/repo-map.md` | `docs/COMMANDS.md` (Repo Map), `docs/REFERENCE.md` |
| `core/simplicity.md` | `CLAUDE.md` (Simplicity Principle) |
| `core/steering.md` | `docs/COMMANDS.md` (Steering Files), `docs/STEERING_GUIDE.md` |
| `core/task-delegation.md` | `docs/REFERENCE.md` (Configuration Options) |
| `core/task-tracking.md` | `docs/REFERENCE.md` |
| `core/tool-abstraction.md` | `CLAUDE.md` (Tool Abstraction) |
| `core/writing-quality.md` | `CLAUDE.md`, `README.md` (Writing and Engineering Philosophy) |
| `core/engineering-discipline.md` | `CLAUDE.md`, `README.md` (Writing and Engineering Philosophy), `docs/STRUCTURE.md` |
| `core/update.md` | `docs/COMMANDS.md` (Update) |
| `core/view.md` | `docs/COMMANDS.md` (View/List) |
| `core/decomposition.md` | `docs/COMMANDS.md` (Initiative Management), `docs/REFERENCE.md` (Spec Structure), `docs/STRUCTURE.md`, `docs/DIAGRAMS.md`, `README.md` (Multi-Spec Features), `CLAUDE.md` (Architecture) |
| `core/initiative-orchestration.md` | `docs/COMMANDS.md` (Initiative Management), `docs/REFERENCE.md`, `docs/STRUCTURE.md`, `docs/DIAGRAMS.md`, `CLAUDE.md` (Architecture) |
| `core/dispatcher.md` | `CLAUDE.md` (Architecture), `docs/STRUCTURE.md`, `README.md` (Context-Aware Dispatch) |
| `core/mode-manifest.json` | `CLAUDE.md` (Architecture, Mode Architecture — update mode count), `docs/STRUCTURE.md` |
| `initiative-schema.json` | `docs/REFERENCE.md` (Spec Structure), `docs/STRUCTURE.md` |
| New `core/*.md` (not in table) | `docs/STRUCTURE.md`, determine target docs from module content |

Collect all matched target docs into a deduplicated list. If no matches found, report "No documentation impact detected" and skip to Step 4.

### Step 3: Check for structural changes (renames and deletions)

If any files were renamed or deleted (from the `--diff-filter=RD` output in Step 1):

1. Get the old file paths from the rename/delete list
2. Search ALL markdown files in the repo for references to these old paths:

   ```bash
   grep -rl "old/path/filename" *.md docs/*.md CLAUDE.md README.md QUICKSTART.md CONTRIBUTING.md
   ```

3. Add any files with stale references to the target docs list

### Step 4: Check CHANGELOG staleness

1. Find the latest version tag: `git describe --tags --abbrev=0 2>/dev/null`
2. If a tag exists, get commits since that tag: `git log --oneline <tag>..HEAD`
3. Read `CHANGELOG.md` and check its `## [Unreleased]` section
4. If there are `feat:` or `fix:` commits not reflected in the Unreleased section, add `CHANGELOG.md` to the target docs list with specific entries to add

If no version tag exists, skip this step.

### Step 5: Read and analyze each target doc

For each doc in the target list:

1. Read the full doc content
2. Read the source file(s) that triggered the match
3. Compare specific sections — identify exactly what is stale:
   - **Outdated file paths** — references to files that were renamed or deleted
   - **Missing entries** — new commands, features, or options not listed
   - **Wrong descriptions** — text that no longer matches the actual behavior
   - **Outdated tables** — rows missing, values changed
   - **Stale examples** — code snippets or config examples that don't match current format
4. If the doc content already matches reality, mark it as "up to date" and skip it

Only flag genuinely stale content. Do NOT flag docs where the changes are in areas the doc doesn't cover.

### Step 6: Generate proposed updates

For each stale doc, prepare the specific edits needed. Draft the updated sections with minimal changes — only fix what's actually stale, don't rewrite surrounding content.

Present a summary to the user:

```text
Documentation Sync Report
=========================

Changes analyzed: <list of source files that changed>

Stale docs found: N

1. CLAUDE.md
   - Custom Slash Commands table: missing /docs-sync entry
   - Security-Sensitive Files: path changed from X to Y

2. docs/REFERENCE.md
   - Configuration Options: new "reviewMode" field not documented

3. CHANGELOG.md
   - Unreleased section: 2 feat commits not listed

Up to date: README.md, QUICKSTART.md, docs/STRUCTURE.md
```

### Step 7: Present for approval

If stale docs were found, ask the user using AskUserQuestion:

**Question**: "How would you like to apply documentation updates?"

**Options**:

- **Apply all** — Apply all proposed updates at once
- **Review individually** — Step through each doc one at a time, approving or skipping each
- **Skip** — Don't apply any changes right now

### Step 8: Apply approved changes

Based on the user's choice:

- **Apply all**: Edit each stale doc with the proposed changes. Use the Edit tool for targeted section updates (not full file rewrites).
- **Review individually**: For each doc, show the proposed change (old vs new) and ask "Apply this update to `<filename>`?" (Yes/Skip). Edit only approved ones.
- **Skip**: Report "No changes applied. You can run `/docs-sync` again later." and stop.

After applying, report: "Updated N documentation files: `<list>`"

### Step 9: Validate examples (if schema changed)

If `schema.json` was among the changed files:

1. For each example config in `examples/*.json`:

   ```bash
   python3 -c "
   import json, jsonschema
   schema = json.load(open('schema.json'))
   config = json.load(open('examples/<file>'))
   jsonschema.validate(config, schema)
   print('VALID: examples/<file>')
   " 2>&1
   ```

2. Report any validation failures — these example configs need manual fixes
3. If any fail, list them with the specific validation error

### Step 10: Summary

Report the final status:

- Number of docs updated
- Number of docs already up to date
- Any example validation failures that need manual attention
- Suggest committing the doc updates: "Run `/commit` to commit these documentation updates."
