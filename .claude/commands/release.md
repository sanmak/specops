Create a versioned release: update CHANGELOG, bump version, validate, commit, push, and publish a GitHub Release.

## Instructions

Follow these steps precisely. Do NOT add a Co-Authored-By line to the commit.

The version to release is provided via `$ARGUMENTS`. If `$ARGUMENTS` is empty or missing, ask the user "What version should this release be? (format: MAJOR.MINOR.PATCH)" and wait for their response before continuing.

---

### Step 1: Validate version

Validate that the version matches semver format `MAJOR.MINOR.PATCH` (e.g., `1.2.0`, `2.0.1`). It must NOT have a `v` prefix -- strip it if present.

If invalid, inform the user and stop.

### Step 2: Pre-flight checks

Run all of these checks. If any fail, report the issue and stop.

1. **Working tree is clean**: Run `git status`. If there are uncommitted changes, tell the user "Working tree is not clean. Run /commit first or stash changes before releasing." and stop.
2. **On main branch**: Run `git rev-parse --abbrev-ref HEAD`. If not on `main`, tell the user "Releases must be created from the main branch. Currently on `<branch>`." and stop.
3. **No unpushed commits**: Run `git log @{upstream}..HEAD --oneline`. If there are unpushed commits, tell the user "There are unpushed commits. Run /push first." and stop.
4. **GitHub CLI available**: Run `gh --version`. If `gh` is not available, tell the user "GitHub CLI (gh) is required for creating releases. Install it with: brew install gh" and stop.
5. **Tag does not exist**: Run `git tag -l v<version>`. If the tag already exists, tell the user "Tag v<version> already exists. Choose a different version number." and stop.

### Step 3: Gather changes since last release

1. Find the last release tag: `git describe --tags --abbrev=0 2>/dev/null`. If no tags exist, use the root commit.
2. List all commits since: `git log --oneline <last-tag>..HEAD`
3. Read the full diffs for each commit to understand the actual changes: `git log -p <last-tag>..HEAD`
4. Read the current `CHANGELOG.md` to check if there is existing content in the `[Unreleased]` section

### Step 4: Draft CHANGELOG entries

Based on the commits and diffs from Step 3, draft a CHANGELOG section for this version.

**Categorize changes** using commit prefixes and diff analysis:
- `feat:` commits go under `### Added`
- `fix:` commits go under `### Fixed`
- `refactor:`, `chore:` (non-version) commits go under `### Changed`
- Removed functionality goes under `### Removed`

**Writing guidelines**:
- Write meaningful entries describing WHAT was added/changed from a user's perspective, not just repeating commit messages
- Use bold for the main feature name, then a brief description (e.g., `- **Builder vertical**: new vertical for...`)
- Group related sub-items under their main feature
- If the `[Unreleased]` section in `CHANGELOG.md` already has entries, incorporate and refine them (they may have been written earlier and are more detailed)
- Skip pure housekeeping commits (checksum regeneration, merge commits) unless they represent user-visible changes
- Only include sections (Added, Changed, Fixed, Removed) that have entries

**Present the draft to the user** before writing. Show the full formatted section and ask if they want any changes. Wait for approval before proceeding.

### Step 5: Update CHANGELOG.md

Edit `CHANGELOG.md`:
1. Keep the `## [Unreleased]` header but clear its content
2. Insert the new version section immediately after `## [Unreleased]`: `## [<version>] - <YYYY-MM-DD>` (use today's date)
3. Add the categorized entries from Step 4 under the version header

### Step 6: Bump version

Run `bash scripts/bump-version.sh <version> --checksums` to update all 4 `platform.json` files and regenerate `CHECKSUMS.sha256`.

### Step 7: Regenerate platform outputs

Run `python3 generator/generate.py --all` to regenerate all platform outputs. This ensures generated files are fresh after the version bump.

### Step 8: Run validation

Run these checks. If any fail, report the failure and stop.

1. `python3 generator/validate.py` -- platform validation
2. `shasum -a 256 -c CHECKSUMS.sha256` -- checksum verification
3. `bash scripts/run-tests.sh` -- full test suite

### Step 9: Stage and commit

Stage these files:
- `CHANGELOG.md`
- `platforms/claude/platform.json`, `platforms/cursor/platform.json`, `platforms/codex/platform.json`, `platforms/copilot/platform.json`
- `CHECKSUMS.sha256`

Check if any generated files actually changed with `git diff platforms/claude/SKILL.md platforms/cursor/specops.mdc platforms/codex/SKILL.md platforms/copilot/specops.instructions.md skills/ .claude-plugin/`. If any have changes, stage them too.

Run the commit using a heredoc:

```
git commit -m "$(cat <<'EOF'
chore: release v<version>
EOF
)"
```

Do NOT use `--no-verify`. If the pre-commit hook fails:
1. Read the error output
2. Fix the issue (regenerate files, fix JSON, etc.)
3. Re-stage changes with `git add`
4. Retry the commit
5. If it fails again, report errors to the user and stop

### Step 10: Push

Run `git push origin main`.

Do NOT use `--no-verify`. If the push or pre-push hook fails, report the failure and stop.

### Step 11: Create GitHub Release

Extract the changelog section for this version from `CHANGELOG.md` (everything between `## [<version>]` and the next `## [` heading). Use this as the release notes.

Create the release:

```
gh release create v<version> --title "v<version>" --notes "$(cat <<'EOF'
<changelog section content>
EOF
)"
```

If the release creation fails, report the error. The commit and push already succeeded, so tell the user they can create the release manually via the GitHub UI.

### Step 12: Confirm

Report the release summary:
1. Show the release URL from Step 11
2. Run `git log --oneline -1` to show the release commit
3. Run `grep '"version"' platforms/*/platform.json` to confirm version is updated
4. Show `shasum -a 256 -c CHECKSUMS.sha256` to confirm checksums are valid
