## Init Mode

Init mode creates a `.specops.json` configuration file in the user's project. It is triggered when the user's request matches init-related patterns.

### Init Mode Detection

When the user invokes SpecOps, check for init intent **before** checking for view/list commands:

- **Init mode**: The user's request is specifically about setting up SpecOps itself — patterns like "init", "initialize", "setup specops", "configure specops", or "create config". Bare "setup" or "configure" alone only match if there is no product feature described (e.g., "set up autoscaling" is NOT init mode). Proceed to the **Init Workflow** below.
- If init intent is not detected, continue to the view/list check and then the standard workflow.

### Init Workflow

#### Step 1: Check for Existing Config

READ_FILE(`.specops.json`) in the current working directory.

- If the file exists, display its contents and ASK_USER: "A `.specops.json` already exists. Would you like to replace it or keep the current one?"
- If the user wants to keep it, stop here with a message: "Keeping existing config. Run `/specops <description>` to start spec-driven development."
- If the file does not exist, continue to Step 1.5.

#### Step 1.5: Detect Project Type

Determine the project type by scanning the repository. This step adapts init behavior for greenfield, brownfield, and migration projects.

1. **Scan repository state:**
   - Prefer version control metadata when available: RUN_COMMAND(`git ls-files`) from the project root to list tracked files. Exclude files under `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `vendor/`, `.specops/`.
   - If `git ls-files` is not available or fails (e.g., not a git repo), fall back to LIST_DIR(`.`) the project root (exclude `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `vendor/`, `.specops/`).
   - From the resulting file list, count source code files — files that are NOT config-only files (`.gitignore`, `LICENSE`, `README.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json`, `tsconfig.json`, `Makefile`, `Dockerfile`, `.editorconfig`, `.prettierrc`, `.eslintrc.*`)
   - Check FILE_EXISTS for documentation: `README.md`, `CONTRIBUTING.md`, `docs/`, `architecture.md`
   - Check FILE_EXISTS for dependency manifests: `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json`

2. **Classify project type:**
   - **Greenfield**: Source code file count ≤ 5 (only scaffolding/config files present)
   - **Brownfield**: Source code file count > 5 (dependency manifests or documentation strengthen confidence but are not required for classification)
   - **Migration**: Cannot be auto-detected reliably — only set if the user overrides

3. **Present detection result:**
   - On interactive platforms (`canAskInteractive = true`):
     ASK_USER: "Detected project type: **[Greenfield / Brownfield]** ([reason: e.g., 'found 3 source files' / 'found 47 source files, package.json, README.md']). Is this correct?"

     Options:
     - **Greenfield** — New project, building from scratch. Recommends: Builder template, adaptive Phase 1 (skips codebase exploration, proposes initial structure)
     - **Brownfield** — Existing project, adding SpecOps. Recommends: Standard template, auto-populated steering files from existing documentation
     - **Migration** — Re-platforming or modernizing an existing system. Recommends: Standard template with migration vertical

   - On non-interactive platforms (`canAskInteractive = false`):
     NOTIFY_USER: "Detected project type: **[Greenfield / Brownfield]** ([reason]). Using recommended defaults."
     Use the detected type without confirmation.

4. **Apply project type:**
   - Store the confirmed project type for use in subsequent init steps
   - If **Greenfield**: pre-select Builder template in Step 2, note that Phase 1 will adapt for empty repos
   - If **Brownfield**: pre-select Standard template in Step 2, enable assisted steering population in Step 4.7
   - If **Migration**: pre-select Standard template in Step 2 with `vertical: "migration"` customization prompt in Step 4

#### Step 2: Present Template Options

ASK_USER with these template options:

**Question:** "Which SpecOps configuration template would you like to use?"

**Options:**

1. **Minimal** — Just sets the specs directory. Best for trying SpecOps quickly or solo projects with no special requirements.

2. **Standard** — Team conventions, review required, GitHub task tracking, auto-create PRs. Good default for most backend/fullstack teams.

3. **Full** — Everything configured: spec reviews with 2 approvals, code review, linting, formatting, monorepo modules, CI/deployment/monitoring integrations. For mature teams with established processes.

4. **Review** — Focused on collaborative spec review with 2 approvals, code review with tests required, GitHub task tracking. For teams where review quality is the priority.

5. **Builder** — Minimal config for the builder vertical (full-product shipping). Auto-create PRs, auto testing. For solo builders or small teams focused on shipping fast.

#### Step 3: Write the Config

Based on the user's selection, WRITE_FILE(`.specops.json`) with the corresponding template content below.

{{ init_templates }}

#### Step 3.5: Solo or Team (Conditional)

If the selected template has `specReview.enabled: true` (Standard, Full, or Review templates):

ASK_USER: "Are you working solo or with a team?"

- **Solo**: EDIT_FILE(`.specops.json`) to set `team.specReview.allowSelfApproval` to `true` and `team.specReview.minApprovals` to `1`. This enables the self-review workflow so solo developers can review and approve their own specs.
- **Team**: Keep the template defaults (`allowSelfApproval: false`). No changes needed.

#### Step 4: Customize (Optional)

After writing the config, ASK_USER: "Would you like to customize any fields? Common customizations: `specsDir` path, `vertical` (backend/frontend/fullstack/infrastructure/data/library/builder/migration), or team `conventions`."

If the confirmed project type from Step 1.5 is **Migration** and the user has not yet set the vertical, suggest: "Since this is a migration project, would you like to set the vertical to `migration`? This adapts spec templates with migration-specific sections (Source System Analysis, Cutover Plan, Coexistence Strategy)."

If the user wants to customize, EDIT_FILE(`.specops.json`) to modify the specific fields they request.

#### Step 4.5: Steering Files

Create foundation steering files by default. These give the agent persistent project context for better specs. Only create files that do not already exist — existing user-authored content is never overwritten.

1. RUN_COMMAND(`mkdir -p <specsDir>/steering`)
2. If FILE_EXISTS(`<specsDir>/steering/product.md`) is false, WRITE_FILE(`<specsDir>/steering/product.md`) with the product.md foundation template from the Steering Files module
3. If FILE_EXISTS(`<specsDir>/steering/tech.md`) is false, WRITE_FILE(`<specsDir>/steering/tech.md`) with the tech.md foundation template from the Steering Files module
4. If FILE_EXISTS(`<specsDir>/steering/structure.md`) is false, WRITE_FILE(`<specsDir>/steering/structure.md`) with the structure.md foundation template from the Steering Files module
5. If all three files already existed, NOTIFY_USER("Steering files already exist — preserved existing content.")

#### Step 4.6: Memory Scaffold

Create empty memory files so the directory structure is complete from day one. Memory is populated automatically when specs complete Phase 4. Only create files that do not already exist — existing memory data is never overwritten.

1. RUN_COMMAND(`mkdir -p <specsDir>/memory`)
2. If FILE_EXISTS(`<specsDir>/memory/decisions.json`) is false, WRITE_FILE(`<specsDir>/memory/decisions.json`) with: `{"version": 1, "decisions": []}`
3. If FILE_EXISTS(`<specsDir>/memory/context.md`) is false, WRITE_FILE(`<specsDir>/memory/context.md`) with: `# Project Memory\n\n## Completed Specs\n`
4. If FILE_EXISTS(`<specsDir>/memory/patterns.json`) is false, WRITE_FILE(`<specsDir>/memory/patterns.json`) with: `{"version": 1, "decisionCategories": [], "fileOverlaps": []}`

#### Step 4.7: Assisted Steering Population (Brownfield)

If the confirmed project type from Step 1.5 is **brownfield**, check for existing documentation to pre-populate the steering file templates. Only populate files that still contain placeholder text (bracket-enclosed placeholders like `[One-sentence description`, `[Who uses this`, `[What makes this`, `[Primary language`). Skip this step entirely if all three steering files already have non-placeholder content or if the project type is not Brownfield.

1. READ_FILE(`<specsDir>/steering/product.md`). If the body contains only foundation template placeholders:
   - If FILE_EXISTS(`README.md`), READ_FILE(`README.md`). Extract:
     - First paragraph or section after the title → Product Overview
     - Any "Features", "About", or "Description" section content → populate relevant fields
   - If useful content was found, EDIT_FILE(`<specsDir>/steering/product.md`) to replace the placeholder lines with the extracted content. Preserve the YAML frontmatter unchanged.

2. READ_FILE(`<specsDir>/steering/tech.md`). If the body contains only foundation template placeholders:
   - Scan for dependency/config files in this priority order (stop at first found):
     - `package.json` → extract `dependencies`, `devDependencies` keys for framework/library detection
     - `pyproject.toml` or `requirements.txt` → extract dependencies
     - `Cargo.toml` → extract `[dependencies]`
     - `go.mod` → extract module path and requires
     - `pom.xml` or `build.gradle` → note Java/Kotlin + build tool
     - `Gemfile` → extract gems
     - `composer.json` → extract PHP dependencies
   - If a dependency file was found, READ_FILE it and EDIT_FILE(`<specsDir>/steering/tech.md`) to populate:
     - Core Stack: primary language + framework (inferred from dependencies)
     - Development Tools: build system, package manager (inferred from config file type)
     - Quality & Testing: test framework (inferred from test dependencies like jest, pytest, mocha, rspec, etc.)

3. READ_FILE(`<specsDir>/steering/structure.md`). If the body contains only foundation template placeholders:
   - LIST_DIR(`.`) to get the top-level directory listing
   - EDIT_FILE(`<specsDir>/steering/structure.md`) to populate:
     - Directory Layout: list top-level directories with brief purpose descriptions inferred from conventional names (src/, lib/, tests/, docs/, app/, public/, scripts/, etc.)
     - Key Files: list notable root files (README.md, config files, entry points)

4. If any steering files were populated:
   NOTIFY_USER("Pre-populated steering files from existing project documentation. Review `<specsDir>/steering/` and refine as needed.")

#### Step 5: Next Steps

NOTIFY_USER with a message that reflects what actually happened in Steps 4.5 and 4.6. For each of "Steering files" and "Memory scaffold", use "created in" if all files were newly written in that step, "verified existing in" if all files already existed, or "set up in" if some files were created and some already existed. Example when all files are new:

```
SpecOps initialized! Your config:
- Specs directory: <specsDir value>
- Vertical: <vertical value or "auto-detect">
- Steering files created in <specsDir>/steering/
- Memory scaffold created in <specsDir>/memory/

Edit product.md, tech.md, and structure.md to describe your project — the agent loads these automatically before every spec. Memory is populated automatically as you complete specs.

Next: Run `/specops <description>` to create your first spec.
Example: /specops Add user authentication with OAuth
```

Adjust each line to say "verified existing in" instead of "created in" if those files already existed before this run.
