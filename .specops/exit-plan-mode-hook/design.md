# Design: ExitPlanMode Hook for Auto-Triggering SpecOps

## Overview

This feature adds a Claude Code PostToolUse hook that fires on ExitPlanMode, detects SpecOps-configured projects, and instructs the agent to run `/specops from-plan` instead of implementing directly. The hook is injected by both the local and remote installers.

## Architecture

### Hook Definition

The hook is a PostToolUse entry in Claude Code's `settings.json`:

```json
{
  "matcher": "ExitPlanMode",
  "command": "test -f .specops.json && echo \"SPECOPS HOOK: A plan was just approved. This project uses SpecOps (.specops.json detected). Do NOT implement directly. Instead, run /specops from-plan to convert the plan into a structured spec before implementation. Implementing without a spec in a SpecOps-configured project is a protocol breach.\" # specops-hook"
}
```

Key design elements:
- `test -f .specops.json` -- only activates in SpecOps-configured projects (inert elsewhere)
- `# specops-hook` marker -- enables future uninstall tooling to find and remove it
- "protocol breach" language -- matches existing enforcement pattern in SpecOps workflow

### Settings File Selection Logic

The installer determines which `settings.json` to modify based on installation scope:

| Installation Path | Settings File | Rationale |
|---|---|---|
| User install (`~/.claude/skills/specops`) | `~/.claude/settings.json` | Global, inert in non-SpecOps projects |
| Project install (`./.claude/skills/specops`) | `./.claude/settings.json` | Project-scoped |
| Custom path | `~/.claude/settings.json` | Safest default |

### Injection Method

Python3 inline script (reuses existing pattern from install.sh lines 120-138):
1. Load existing settings.json or create empty dict
2. Ensure `hooks.PostToolUse` array exists
3. Check for existing `specops-hook` marker (idempotent)
4. Append the hook entry
5. Write back with `indent=2`
6. Graceful fallback if python3 unavailable (warning + manual instructions)

## Architecture Decisions

### AD-1: PostToolUse Hook vs Behavioral Detection
**Decision:** Use PostToolUse hook instead of relying on Step 10.5 behavioral detection.
**Rationale:** Behavioral detection is unreliable -- the agent can skip Step 10.5 under context pressure. PostToolUse hooks fire deterministically every time ExitPlanMode is called, providing a guaranteed trigger point.

### AD-2: Shell Command Guard vs Hook Config
**Decision:** Use `test -f .specops.json` in the shell command rather than a hook-level configuration.
**Rationale:** Claude Code's PostToolUse hooks don't support conditional activation at the config level. The shell guard makes the hook universally installable while only activating in SpecOps-configured projects.

### AD-3: Global Settings for User Install
**Decision:** Write to `~/.claude/settings.json` for user-scoped installations.
**Rationale:** The hook is inert in non-SpecOps projects (the `test -f` guard prevents any output), so global installation is safe and ensures coverage across all projects without per-project setup.

### AD-4: Dogfood in settings.local.json
**Decision:** Use `.claude/settings.local.json` for the SpecOps repo's own hook.
**Rationale:** `.claude/settings.json` is gitignored by the `.claude/*` pattern. `.claude/settings.local.json` is the appropriate location for repo-specific settings that should be committed.

## Component Interactions

```text
ExitPlanMode (Claude Code)
    |
    v
PostToolUse hook fires
    |
    v
test -f .specops.json
    |
    ├── exists: echo "SPECOPS HOOK: ..." → agent receives as user feedback
    |                                       → agent runs /specops from-plan
    |
    └── not found: silent (exit code 1, no output)
```

## Files to Modify

| File | Change |
|---|---|
| `platforms/claude/install.sh` | Add `install_hook()` function + settings file selection |
| `scripts/remote-install.sh` | Mirror hook injection in `install_claude()` |
| `.claude/settings.local.json` | Add hook for SpecOps repo dogfooding |
| `docs/COMPARISON.md` | Update feature matrix and Kiro comparison |
