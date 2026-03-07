## Update Mode

Update mode checks for newer SpecOps versions and guides the user through upgrading. It is triggered only by explicit user request — SpecOps never checks for updates automatically.

### Update Mode Detection

When the user invokes SpecOps, check for update intent **before** entering the standard workflow:

- **Update mode**: The user's request matches patterns like "update", "upgrade", "check for updates", "get latest version", "get latest". Proceed to the **Update Workflow** below.

If update intent is not detected, continue to the next check in the routing chain.

### Update Workflow

#### Step 1: Detect Current Version

1. Read this instruction file's own YAML frontmatter to extract the `version:` field. This is the **running version** of SpecOps.
2. If FILE_EXISTS(`.specops.json`), READ_FILE it and check for `_installedVersion` and `_installedAt` fields.
3. Display:

   ```
   SpecOps — Current Installation

   Running version: {version from frontmatter}
   Installed version: {_installedVersion or "unknown"}
   Installed at: {_installedAt or "unknown"}
   ```

   If `_installedVersion` is absent, show only the running version line.

#### Step 2: Check Latest Available Version

Attempt to fetch the latest release from GitHub. Try the primary method first, then fall back.

**Primary** (requires `gh` CLI):
```
RUN_COMMAND(gh release view --repo sanmak/specops --json tagName,publishedAt -q '.tagName + " (" + .publishedAt + ")"')
```

**Fallback** (requires `curl` + `python3`):
```
RUN_COMMAND(curl -s https://api.github.com/repos/sanmak/specops/releases/latest | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['tag_name'], d.get('published_at',''))")
```

- Parse the tag name from the output. Strip the `v` prefix if present (e.g., `v1.3.0` → `1.3.0`).
- If both commands fail (no network, no `gh` CLI, API rate limited): display the manual check URL and stop:

  ```
  Could not check for updates automatically.
  Check the latest version manually: https://github.com/sanmak/specops/releases
  ```

#### Step 3: Compare Versions

Split both the current version and the latest version on `"."` and compare each segment as integers (major, then minor, then patch).

- If the current version is **equal to or newer** than the latest:

  ```
  You're on the latest version (v{current}).
  ```

  Stop here — no update needed.

- If an update is available:

  ```
  Update available: v{current} → v{latest}

  Changelog: https://github.com/sanmak/specops/releases/tag/v{latest}
  ```

  Continue to Step 4.

#### Step 4: Detect Installation Method

Use heuristic file-path probing to determine how SpecOps was installed. No user input needed.

1. **Claude Plugin Marketplace**: If this instruction file was loaded as a Claude Code plugin/skill (the agent can detect this from its own loading context — e.g., the file path includes a plugin directory like `.claude-plugin/` or the skill was loaded via the plugin system rather than from a project or user skills directory), the installation method is **Plugin Marketplace**.
2. **User-level install** (Claude only): Check FILE_EXISTS for `~/.claude/skills/specops/SKILL.md`. If present, the installation method is **Claude user-level install**. Note: `~` resolves to the user's home directory; if the platform cannot resolve this path, skip this check and fall through.
3. **Project-level install**: Check FILE_EXISTS for platform-specific paths in the current project:
   - `.cursor/rules/specops.mdc` → Cursor project install
   - `.codex/skills/specops/SKILL.md` → Codex project install
   - `.github/instructions/specops.instructions.md` → Copilot project install
   - `.claude/skills/specops/SKILL.md` → Claude project install
4. **Local clone**: Check FILE_EXISTS for `generator/generate.py` in the current directory. If present, the user is running from a cloned SpecOps repository.
5. **Unknown**: If none of the above match, the method is unknown. Show all update options.

#### Step 5: Present Update Instructions

Based on the detected installation method, present the appropriate update command.

##### Plugin Marketplace (Claude only)

```
To update via the plugin marketplace:

  /plugin install specops@specops-marketplace
  /reload-plugins

This will pull the latest version from the marketplace.
```

##### Remote Install (project-level or user-level)

Based on the installation method detected in Step 4, include the appropriate `--scope` flag for Claude installs:

**If Claude user-level install was detected:**
```
To update to v{latest}:

  curl -fsSL https://raw.githubusercontent.com/sanmak/specops/v{latest}/scripts/remote-install.sh | bash -s -- --version v{latest} --platform claude --scope user
```

**If Claude project-level install was detected:**
```
To update to v{latest}:

  curl -fsSL https://raw.githubusercontent.com/sanmak/specops/v{latest}/scripts/remote-install.sh | bash -s -- --version v{latest} --platform claude --scope project
```

**For other platforms** (Cursor, Codex, Copilot — no scope concept):
```
To update to v{latest}:

  curl -fsSL https://raw.githubusercontent.com/sanmak/specops/v{latest}/scripts/remote-install.sh | bash -s -- --version v{latest} --platform {detected-platform}
```

Replace `{detected-platform}` with the platform detected in Step 4 (`cursor`, `codex`, or `copilot`).

##### Local Clone

```
To update your local clone:

  git pull origin main
  bash setup.sh
```

##### Unknown Method

If the installation method could not be determined, show all three options and let the user choose.

**On interactive platforms** (`canAskInteractive: true`): After showing the update command, ASK_USER "Would you like me to run this update command now?" If the user confirms, execute the command via RUN_COMMAND. If the user declines, stop.

**On non-interactive platforms** (`canAskInteractive: false`): Show the commands only. Add a note: "Run the command above in your terminal to update."

#### Step 6: Post-Update Verification

If the update command was auto-executed:

1. NOTIFY_USER that the update is complete.
2. Remind the user: "Restart your AI assistant session to load the new version."

If the update was manual (user will run the command themselves):

1. Display: "After running the update command, restart your AI assistant session to load the new version."

### Platform Gating

- **Interactive platforms** (`canAskInteractive: true`): Full update flow with optional auto-execution.
- **Non-interactive platforms** (`canAskInteractive: false`, e.g., Codex): Show version comparison and update commands only. No auto-execution.
