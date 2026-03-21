## Custom Template Loading

The agent supports custom templates that override the hardcoded defaults. Custom templates allow teams to enforce their own spec structure.

### Resolution Order

When creating a spec file (requirements.md, bugfix.md, refactor.md, design.md, or tasks.md), resolve the template as follows:

1. **Read the template name** from `.specops.json` for the current file:
   - `config.templates.feature` for requirements.md (feature specs)
   - `config.templates.bugfix` for bugfix.md (bugfix specs)
   - `config.templates.refactor` for refactor.md (refactor specs)
   - `config.templates.design` for design.md (all spec types)
   - `config.templates.tasks` for tasks.md (all spec types)

2. **If the template name is `"default"` or not set**, use the hardcoded templates defined in the "Specification Templates" section, with Vertical Adaptation Rules applied if the detected vertical is not `backend` or `fullstack`. Skip the remaining steps.

3. **If the template name is NOT `"default"`**, look for a custom template file at:

   ```text
   <specsDir>/templates/<template-name>.md
   ```

   For example, if `specsDir` is `.specops` and `templates.feature` is `"detailed"`, look for:

   ```text
   .specops/templates/detailed.md
   ```

4. **If the custom template file exists**, read its contents and use it as the starting structure for the spec. Replace any `{{variable}}` placeholders contextually:
   - `{{title}}` — the feature/bugfix/refactor title derived from the user's request
   - `{{stories}}` — generated user stories (for feature specs)
   - `{{criteria}}` — generated acceptance criteria
   - `{{conventions}}` — the team conventions from `config.team.conventions`, formatted as a bulleted list
   - `{{date}}` — the current date
   - `{{type}}` — the spec type (feature, bugfix, or refactor)
   - `{{vertical}}` — the detected or configured vertical (e.g., "infrastructure", "data", "library")
   - Any other `{{variable}}` placeholders should be filled in contextually based on the variable name and the surrounding template content

5. **If the custom template file does NOT exist**, log a warning to the user (e.g., "Custom template 'detailed' not found at .specops/templates/detailed.md, falling back to default template") and fall back to the hardcoded default template.

### Custom Template Example

A custom template file at `.specops/templates/detailed.md` might look like:

```markdown
# {{type}}: {{title}}

## Overview
{{overview}}

## User Stories
{{stories}}

## Acceptance Criteria
{{criteria}}

## Team Conventions
{{conventions}}

## Additional Context
{{context}}
```

### Notes on Custom Templates

- Custom templates can be used for **any** spec file: requirements/bugfix/refactor, design.md, and tasks.md.
- When using a custom template, Vertical Adaptation Rules are NOT applied — the custom template defines its own structure.
- When NO custom template is set (template name is `"default"`), the hardcoded default template is used with Vertical Adaptation Rules applied.
- If a template uses `{{variable}}` placeholders not in the known list above, infer the appropriate content from context. For example, `{{context}}` should be filled with relevant codebase context discovered during Phase 1.
- Teams can create multiple templates (e.g., `"detailed"`, `"minimal"`, `"infra-requirements"`) and switch between them via `.specops.json`.
