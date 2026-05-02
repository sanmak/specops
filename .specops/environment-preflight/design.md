# Design: Environment Pre-flight Checks

## Architecture

The environment pre-flight is implemented as a new sub-step within Phase 3 step 1 (Implementation gates) in `core/workflow.md`. No new module is created -- this is a small, self-contained addition to the existing workflow.

### Pre-flight Step Location

Inserted as step 1.5 in Phase 3, after all existing gates (dependency, review, task tracking, dependency introduction) but before status update to `implementing`:

```
Phase 3, step 1 (Implementation gates):
  - Dependency gate (existing)
  - Review gate (existing)
  - Task tracking gate (existing)
  - Dependency introduction enforcement (existing)
  1.5. **Environment pre-flight** (NEW)
  - Update status to implementing (existing)
```

### Test Command Detection Algorithm

```
1. IF FILE_EXISTS(`package.json`):
     READ_FILE `package.json`
     IF "scripts" contains "test": test_cmd = parsed scripts.test value
2. ELIF FILE_EXISTS(`pyproject.toml`):
     READ_FILE `pyproject.toml`
     IF contains [tool.pytest]: test_cmd = "pytest"
     ELIF contains [tool.unittest]: test_cmd = "python -m unittest"
3. ELIF FILE_EXISTS(`Makefile`):
     READ_FILE `Makefile`
     IF contains "test:" target: test_cmd = "make test"
4. ELIF FILE_EXISTS(`Cargo.toml`): test_cmd = "cargo test"
5. ELIF FILE_EXISTS(`go.mod`): test_cmd = "go test ./..."
6. ELSE: test_cmd = null
     NOTIFY_USER("No test command detected -- manual test execution required")
```

### Dependency Installation Detection

```
Project type detection (reuse from test command detection):
- npm/yarn: check FILE_EXISTS(`node_modules/`)
- Python: check FILE_EXISTS(`.venv/`) or FILE_EXISTS(`__pycache__/`)
- Rust: check FILE_EXISTS(`target/`)
- Go (vendor): check FILE_EXISTS(`vendor/`)

Install command mapping:
- npm: "npm install"
- yarn (FILE_EXISTS(`yarn.lock`)): "yarn install"
- pip: "pip install -r requirements.txt" or "pip install -e ."
- cargo: "cargo build"
- go: "go mod download"
```

### Git Branch State Check

```
RUN_COMMAND(`git status --porcelain`)
Parse output lines:
- Lines starting with "UU", "AA", "DD", "AU", "UA": merge conflicts
  -> STOP with conflict file list
- Any other non-empty lines: dirty working tree
  -> NOTIFY_USER("Working tree has uncommitted changes") (non-blocking warning)
- Empty output: clean
- Command failure (not a git repo): skip silently
```

### Pre-flight Summary Format

```
NOTIFY_USER:
  Environment pre-flight:
  - Test command: [detected command | none detected]
  - Dependencies: [installed | warning: [directory] missing]
  - Git state: [clean | dirty (N files) | BLOCKED: merge conflicts]
```

### Files Modified

| File | Change |
|---|---|
| `core/workflow.md` | Add step 1.5 "Environment pre-flight" to Phase 3 |
| `generator/validate.py` | Add pre-flight markers to existing workflow markers or new PREFLIGHT_MARKERS |

### Dependency Decisions

No new external dependencies required.
