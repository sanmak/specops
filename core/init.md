## Init Mode

Init mode creates a `.specops.json` configuration file in the user's project. It is triggered when the user's request matches init-related patterns.

### Init Mode Detection

When the user invokes SpecOps, check for init intent **before** checking for view/list commands:

- **Init mode**: The user's request matches patterns like "init", "initialize", "setup", "configure", or "create config". Proceed to the **Init Workflow** below.
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

#### Step 4: Customize (Optional)

After writing the config, ASK_USER: "Would you like to customize any fields? Common customizations: `specsDir` path, `vertical` (backend/frontend/fullstack/infrastructure/data/library/builder), or team `conventions`."

If the user wants to customize, EDIT_FILE(`.specops.json`) to modify the specific fields they request.

#### Step 5: Next Steps

NOTIFY_USER with:

```
SpecOps initialized! Your config:
- Specs directory: <specsDir value>
- Vertical: <vertical value or "auto-detect">

Next: Run `/specops <description>` to create your first spec.
Example: /specops Add user authentication with OAuth
```
