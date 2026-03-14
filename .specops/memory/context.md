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
7 tasks completed, 0 deviations from design, 0 blockers. New core/repo-map.md module with 8 H3 sections: generation algorithm (agent-driven, 4-tier language extraction), staleness detection (time + hash), scope control (100 files, depth 3, ~3000 tokens), /specops map subcommand, and safety rules. Generator pipeline wired for all 4 platforms with 8 REPO_MAP_MARKERS. Gap 31 enforced: markers added to both per-platform and cross-platform validator checks. All 7 tests pass.
