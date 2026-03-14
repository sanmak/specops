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
- If the file does not exist, continue to Step 2.

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

After writing the config, ASK_USER: "Would you like to customize any fields? Common customizations: `specsDir` path, `vertical` (backend/frontend/fullstack/infrastructure/data/library/builder), or team `conventions`."

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

#### Step 5: Next Steps

NOTIFY_USER with a message that reflects what actually happened in Steps 4.5 and 4.6. For each of "Steering files" and "Memory scaffold", use "created in" if the files were newly written in that step, or "verified existing in" if the files already existed. Example when all files are new:

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
