# Project Memory

## Completed Specs

### ears-notation (feature) — 2026-03-07
4 tasks completed. EARS notation added to feature requirements template (5 patterns with inline guidance, progress checklist as optional derivative), bugfix template updated with SHALL CONTINUE TO section and three-category testing plan. All 4 platform outputs regenerated and validated. All 7 tests pass. No deviations from design. No blockers.

### bugfix-regression-analysis (feature) — 2026-03-08
4 tasks completed, 0 deviations from design, 0 blockers. Implementation followed the design exactly — Regression Risk Analysis section inserted between Reproduction Steps and Proposed Fix in bugfix.md, severity-tiered workflow guidance replaced the single-paragraph bugfix instruction in workflow.md, and 6 regression markers added to validate.py. All platform outputs regenerated, validator passes, all 7 tests pass.

### steering-files (feature) — 2026-03-08
6 tasks completed, 0 deviations from design, 0 blockers. Implemented steering files as a new core module integrated into the three-layer architecture (core → generator → platforms), using a convention-based `<specsDir>/steering/` directory with a fixed 20-file safety limit instead of schema-based steering config. All validation passes, all 7 tests pass. SpecOps's own steering files created as dogfood proof (product.md, tech.md, structure.md in `.specops/steering/`).

### drift-detection (feature) — 2026-03-08
6 tasks completed across core module, workflow routing, generator pipeline, validation, test consistency, and full integration. Key decisions: promoted drift check headings from H4 to H3 to match heading-prefixed validator markers. All 7 tests pass. Dogfood audit on 3 completed specs: all Healthy across all 5 checks.

### local-memory-layer (feature) — 2026-03-14
5 tasks completed, 0 deviations from design, 0 blockers. New core/memory.md module with memory loading (Phase 1), memory writing (Phase 4), pattern detection, and /specops memory subcommand. Generator pipeline wired for all 4 platforms with 10 MEMORY_MARKERS. Memory seeded from 4 completed specs: 5 decisions, 2 category patterns, 5 file overlaps. All 7 tests pass.

### ast-based-repo-map (feature) — 2026-03-14
7 tasks completed, 0 deviations from design, 0 blockers. New core/repo-map.md module with 8 H3 sections: generation algorithm (agent-driven, 4-tier language extraction), staleness detection (time + hash), scope control (100 files, depth 3, ~3000 tokens), /specops map subcommand, and safety rules. Generator pipeline wired for all 4 platforms with 9 REPO_MAP_MARKERS. Gap 31 enforced: markers added to both per-platform and cross-platform validator checks. All 7 tests pass.

### task-delegation (feature) — 2026-03-18
8 tasks completed, 0 deviations from design, 0 blockers. New core/task-delegation.md module with three platform-adaptive strategies: sub-agent delegation (Claude Code via Agent tool), session checkpoint (Cursor/Copilot via user prompt), and enhanced sequential (Codex with detailed checkpointing). Added canDelegateTask capability flag and taskDelegation config option (auto/always/never). Generator pipeline wired for all 4 platforms with 7 DELEGATION_MARKERS. All 7 tests pass.

### workflow-enforcement-gates (feature) — 2026-03-15
6 tasks completed, 1 deviation from design (validation marker casing). Converted 3 weak workflow points into enforcement gates with "protocol breach" language: Phase 1 pre-flight gate (added content-level steering check + STOP consequence), Phase 4 memory write (mandatory label + forward reference), Phase 3 task tracking gate (restructured as named sub-list, removed "advisory" language, added "attempted creation" principle). Updated validator and tests with new marker. All 4 platform outputs regenerated. All 7 tests pass.

### install-integrity-verification (feature) — 2026-03-17
5 tasks completed, 0 deviations from design, 0 blockers. Added SHA-256 checksum verification to `remote-install.sh` addressing Agent Trust Hub HIGH-priority finding. Three new functions: `detect_hash_cmd()`, `fetch_checksums()`, `verify_file()`. `--no-verify` flag for development use. Security documentation updated: SECURITY.md (install trust chain, manual verification, residual risks), SBOM.md (automatic verification), SECURITY-AUDIT.md (Agent Trust Hub findings). ShellCheck clean, all 7 tests pass.

### writing-quality-rules (feature) — 2026-03-20
5 tasks completed, 0 deviations from design, 0 blockers. New `core/writing-quality.md` module (48 lines) with 6 imperative writing rule sections distilled from 9 vetted technical writing references (Rich Sutton, George Orwell, Simon Peyton Jones, Jeff Bezos, Leslie Lamport, Donald Knuth, Paul Graham, Steven Pinker, William Zinsser). Generator pipeline wired for all 4 platforms with 9 WRITING_QUALITY_MARKERS. README "Writing Philosophy" section adds public attribution. All 7 tests pass, validator passes with 0 errors.

### enforcement-roadmap (feature) — 2026-03-18
8 tasks completed, 0 deviations from design, 0 blockers. Created `scripts/lint-spec-artifacts.py` with 3 validation checks (checkbox staleness, documentation review, version validation) integrated into test suite. Added Phase 1 Context Summary gate and Phase 4 Documentation Review gate to `core/workflow.md`. Added Workflow Impact annotations for all behavioral config values in `core/config-handling.md`. Added COHERENCE_MARKERS to `generator/validate.py` with cross-platform consistency. Added pre-task anchoring to `core/task-tracking.md` and vertical vocabulary verification to `core/verticals.md`. All 4 platform outputs regenerated, all 8 tests pass.

### plan-to-specops-automation (feature) — 2026-03-18
8 tasks completed, 0 deviations from design, 0 blockers. Implemented 3-layer enforcement for plan mode → SpecOps automation: (1) enhanced `core/from-plan.md` with file path input (Branch B) and platform auto-discovery (Branch C using `planFileDirectory`), (2) added step 10.5 post-plan-acceptance gate to `core/workflow.md` with protocol breach enforcement, (3) added Step 8 SpecOps handoff to `.claude/commands/resume-plan.md`. Added `planFileDirectory: "~/.claude/plans"` to Claude's `platform.json`. Updated FROM_PLAN_MARKERS in `generator/validate.py` with "auto-discovery" and "planFileDirectory". All 4 platform outputs regenerated, all 8 tests pass.

### project-type-awareness (feature) — 2026-03-21
6 tasks completed, 0 deviations from design, 0 blockers. Made SpecOps project-type-aware across greenfield, brownfield, and migration projects: (1) migration vertical in `core/verticals.md` with domain vocabulary (Migration Requirements, Migration Architecture, Cutover Plan, Coexistence Strategy) + schema/validator/test updates, (2) auto-init suggestion in `core/workflow.md` step 1 when `.specops.json` missing, (3) project type detection in `core/init.md` step 1.5 (auto-classifies greenfield/brownfield, migration override), (4) brownfield assisted steering in `core/init.md` step 4.7 (auto-populates from README/deps), (5) greenfield adaptive Phase 1 in `core/workflow.md` step 7.5 (replaces hollow codebase exploration with structure proposal and steering auto-population). All 8 tests pass.

### proxy-metrics (feature) — 2026-03-21
8 tasks completed, 0 deviations from design, 0 blockers. New `core/metrics.md` module with 6-step metrics capture procedure using abstract operations. Integrated into Phase 4 as step 2.5 (sub-step notation per project convention — no renumbering). Generator pipeline wired for all 4 platforms with 8 METRICS_MARKERS. Schema extended with optional `metrics` object (7 integer fields). Documentation: `docs/TOKEN-USAGE.md` with benchmarks and ROI guidance, updates to REFERENCE.md, README.md, STRUCTURE.md, CLAUDE.md. All 8 tests pass.
