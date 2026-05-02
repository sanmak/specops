# Environment Pre-flight Checks

## Overview

Phase 3 assumes the development environment is ready for implementation. When it is not -- missing dependencies, wrong branch, uncommitted conflicts -- the spec fails partway through implementation, wasting all Phase 1 and Phase 2 effort. A lightweight pre-flight at the start of Phase 3 catches these problems in seconds.

## Product Requirements

### FR-1: Test Command Detection

<!-- EARS: Event-Driven -->
WHEN Phase 3 implementation gates begin, THE SYSTEM SHALL detect the project's test command by checking project configuration files in priority order: `package.json` (scripts.test), `pyproject.toml` ([tool.pytest] or [tool.unittest]), `Makefile` (test target), `Cargo.toml` (cargo test), `go.mod` (go test). THE SYSTEM SHALL record the detected test command in `implementation.md`.

**Acceptance Criteria:**
- [x] Test command detected from at least 3 project config file formats
- [x] Detection follows priority order (package.json first)
- [x] Detected command recorded in implementation.md
- [x] If no test command detected, note "No test command detected -- manual test execution required" and continue

### FR-2: Dependency Installation Check

<!-- EARS: Event-Driven -->
WHEN Phase 3 implementation gates begin, THE SYSTEM SHALL verify that project dependencies are installed by checking for the presence of the dependency directory: `node_modules/` for npm/yarn projects, `.venv/` or `__pycache__/` for Python projects, `target/` for Rust projects, `vendor/` for Go vendor projects.

<!-- EARS: Unwanted Behavior -->
IF the expected dependency directory is missing, THEN THE SYSTEM SHALL warn the user: "Dependencies may not be installed. Run [detected install command] before proceeding." and continue (non-blocking).

**Acceptance Criteria:**
- [x] Dependency directory existence checked for the detected project type
- [x] Missing dependencies produce a warning with the appropriate install command
- [x] Check is non-blocking (warn and continue, do not stop)

### FR-3: Git Branch State Check

<!-- EARS: Event-Driven -->
WHEN Phase 3 implementation gates begin, THE SYSTEM SHALL check the git working tree for uncommitted merge conflicts by running `git status --porcelain` and checking for conflict markers (lines starting with `UU`, `AA`, `DD`).

<!-- EARS: Unwanted Behavior -->
IF uncommitted merge conflicts are detected, THEN THE SYSTEM SHALL STOP and notify the user: "Merge conflicts detected in: [file list]. Resolve conflicts before implementation."

**Acceptance Criteria:**
- [x] Git status checked for merge conflict markers
- [x] Conflicts are blocking (STOP, do not proceed)
- [x] Non-conflict dirty state is non-blocking (warn only)
- [x] If not a git repo, skip this check silently

### FR-4: Pre-flight Summary

<!-- EARS: Ubiquitous -->
THE SYSTEM SHALL display a pre-flight summary after all checks complete, showing: test command (detected or none), dependency status (installed or warning), and git state (clean, dirty, or conflicts).

**Acceptance Criteria:**
- [x] Pre-flight summary displayed before implementation begins
- [x] Summary includes all three check results
- [x] Summary is concise (3-4 lines maximum)

## Non-Functional Requirements

- **NFR-1**: Pre-flight checks complete in under 2 seconds (all checks use file existence or single git commands).
- **NFR-2**: No new module required. Implemented as additions to `core/workflow.md` Phase 3 step 1.
- **NFR-3**: All checks use abstract operations (no platform-specific tool names).
- **NFR-4**: Pre-flight checks are unconditional -- no config switch to disable them.

## Team Conventions

- Conventional commits: feat:, fix:, chore:, docs:, test:, refactor:
- Core files must use abstract operations from core/tool-abstraction.md only
- Never edit generated platform output files directly
- All JSON schema objects must use additionalProperties: false
