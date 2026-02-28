## What changed and why

<!-- 1-2 sentences. What does this PR do and why is it needed? -->

## Checklist

### Always required
- [ ] CI checks pass (JSON validation, schema tests, platform consistency, ShellCheck, verify.sh)

### If `core/` or `generator/` was changed
- [ ] Ran `python3 generator/generate.py --all`
- [ ] Ran `python3 generator/validate.py`
- [ ] Ran `python3 tests/test_platform_consistency.py` and `python3 tests/test_build.py`

### If `schema.json` or `platforms/claude/skill.json` was changed
- [ ] Ran `python3 tests/check_schema_sync.py` (schemas are in sync)

### If shell scripts were changed
- [ ] Ran `shellcheck setup.sh verify.sh scripts/bump-version.sh platforms/*/install.sh`

### If a security-sensitive file was changed
(`core/workflow.md`, `core/safety.md`, `schema.json`, `platforms/claude/skill.json`, `setup.sh`, `generator/generate.py`)
- [ ] Explained why the change is needed
- [ ] Described the security implications
