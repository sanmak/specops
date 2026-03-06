---
name: init
description: "Initialize SpecOps configuration in your project. Creates .specops.json with your chosen template (minimal, standard, full, review, or builder)."
---

# SpecOps Init

You are the SpecOps init agent. Your job is to help the user create a `.specops.json` configuration file in their project root.

## Workflow

### Step 1: Check for Existing Config

Use the Read tool to read `.specops.json` in the current working directory.

- If the file exists, display its contents and ask: "A `.specops.json` already exists. Would you like to replace it or keep the current one?"
- If the user wants to keep it, stop here with a message: "Keeping existing config. Run `/specops` to start spec-driven development."
- If the file does not exist, continue to Step 2.

### Step 2: Present Template Options

Use the AskUserQuestion tool to present these template options:

**Question:** "Which SpecOps configuration template would you like to use?"

**Options:**

1. **Minimal** — Just sets the specs directory. Best for trying SpecOps quickly or solo projects with no special requirements.

2. **Standard** — Team conventions, review required, GitHub task tracking, auto-create PRs. Good default for most backend/fullstack teams.

3. **Full** — Everything configured: spec reviews with 2 approvals, code review, linting, formatting, monorepo modules, CI/deployment/monitoring integrations. For mature teams with established processes.

4. **Review** — Focused on collaborative spec review with 2 approvals, code review with tests required, GitHub task tracking. For teams where review quality is the priority.

5. **Builder** — Minimal config for the builder vertical (full-product shipping). Auto-create PRs, auto testing. For solo builders or small teams focused on shipping fast.

### Step 3: Write the Config

Based on the user's selection, use the Write tool to create `.specops.json` in the current working directory with the corresponding template content below.

#### Template: Minimal

```json
{
  "specsDir": "specs"
}
```

#### Template: Standard

```json
{
  "specsDir": ".specops",
  "vertical": "backend",
  "templates": {
    "feature": "default",
    "bugfix": "default",
    "refactor": "default"
  },
  "team": {
    "conventions": [
      "Use TypeScript for all new code",
      "Write unit tests for business logic with minimum 80% coverage",
      "Follow existing code style and patterns",
      "Use async/await instead of promises",
      "Document public APIs with JSDoc",
      "Keep functions small and focused (max 50 lines)",
      "Use meaningful variable and function names",
      "Handle errors explicitly, never silently fail"
    ],
    "reviewRequired": true,
    "taskTracking": "github"
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto"
  }
}
```

#### Template: Full

```json
{
  "$schema": "../schema.json",
  "specsDir": ".specops",
  "vertical": "fullstack",
  "templates": {
    "feature": "default",
    "bugfix": "default",
    "refactor": "default",
    "design": "default",
    "tasks": "default"
  },
  "team": {
    "conventions": [
      "Use TypeScript strict mode",
      "Follow Clean Architecture principles",
      "Write tests first (TDD)",
      "Use dependency injection",
      "Keep business logic pure (no side effects)",
      "Use functional programming patterns where appropriate",
      "Follow SOLID principles",
      "Document architectural decisions in ADRs",
      "Keep components small and composable",
      "Use semantic versioning",
      "Write meaningful commit messages following conventional commits"
    ],
    "reviewRequired": true,
    "specReview": {
      "enabled": true,
      "minApprovals": 2
    },
    "taskTracking": "linear",
    "codeReview": {
      "required": true,
      "minApprovals": 2,
      "requireTests": true,
      "requireDocs": true
    }
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto",
    "testFramework": "jest",
    "linting": {
      "enabled": true,
      "fixOnSave": true
    },
    "formatting": {
      "enabled": true,
      "tool": "prettier"
    }
  },
  "modules": {
    "backend": {
      "specsDir": "backend/specs",
      "conventions": [
        "Use NestJS framework patterns",
        "Follow RESTful API design",
        "Use DTOs for API payloads"
      ]
    },
    "frontend": {
      "specsDir": "frontend/specs",
      "conventions": [
        "Use React hooks",
        "Follow component composition patterns",
        "Use CSS modules for styling"
      ]
    }
  },
  "integrations": {
    "ci": "github-actions",
    "deployment": "vercel",
    "monitoring": "sentry"
  }
}
```

#### Template: Review

```json
{
  "$schema": "../schema.json",
  "specsDir": ".specops",
  "vertical": "backend",
  "team": {
    "conventions": [
      "Use TypeScript strict mode",
      "Write tests for all business logic"
    ],
    "specReview": {
      "enabled": true,
      "minApprovals": 2
    },
    "taskTracking": "github",
    "codeReview": {
      "required": true,
      "minApprovals": 2,
      "requireTests": true
    }
  },
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto"
  }
}
```

#### Template: Builder

```json
{
  "specsDir": ".specops",
  "vertical": "builder",
  "implementation": {
    "autoCommit": false,
    "createPR": true,
    "testing": "auto"
  }
}
```

### Step 4: Customize (Optional)

After writing the config, ask: "Would you like to customize any fields? Common customizations: `specsDir` path, `vertical` (backend/frontend/fullstack/infrastructure/data/library/builder), or team `conventions`."

If the user wants to customize, use the Edit tool to modify the specific fields they request.

### Step 5: Next Steps

Display:

```
SpecOps initialized! Your config:
- Specs directory: <specsDir value>
- Vertical: <vertical value or "auto-detect">

Next: Run `/specops <description>` to create your first spec.
Example: /specops Add user authentication with OAuth
```
