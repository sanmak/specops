# Feature: Solution Exploration Mode

## Problem Statement

Developers often know what problem to solve but not which technical approach to take. SpecOps currently jumps straight from problem understanding to spec writing (Phase 2), forcing users to commit to a design direction before evaluating alternatives. The interview mode helps refine vague ideas (convergent), but there is no divergent exploration step that generates multiple codebase-grounded approaches with tradeoff analysis before the user commits to a spec.

## User Stories

<!-- EARS: When the user has a clear problem but unclear approach, the system shall generate 3-5 solution approaches grounded in the actual codebase. -->
- As a developer, I want to explore multiple solution approaches before committing to a spec, so that I pick the best technical direction for my codebase.

<!-- EARS: When the user invokes explore mode, the system shall reference real files from the repo map and real patterns from steering files. -->
- As a developer, I want each approach to reference actual files and patterns in my codebase, so that the proposals are grounded in reality rather than generic advice.

<!-- EARS: When the user selects an approach, the system shall flow the selected approach into Phase 2 as a pre-populated design direction. -->
- As a developer, I want to select an approach and have it flow directly into spec creation, so that the exploration work is not lost.

<!-- EARS: When the platform is non-interactive, the system shall generate all approaches as output without requiring user selection. -->
- As a developer on a non-interactive platform, I want all approaches generated as output so I can review and pick one offline.

## Acceptance Criteria

- [x] New `core/explore.md` module defines the explore mode workflow
- [x] Explore mode generates 3-5 codebase-grounded solution approaches for a given problem statement
- [x] Each approach includes: name, description, key files to modify, tradeoff analysis (pros/cons), complexity estimate, risk assessment
- [x] Approaches reference actual project files from the repo map and patterns from steering files
- [x] User selects an approach (interactive) or receives all approaches (non-interactive)
- [x] Selected approach flows into Phase 2 as a pre-populated design direction
- [x] Depth flag integration: lightweight depth generates fewer approaches (minimum 2), deep generates more (up to 5)
- [x] Detection patterns registered in `core/dispatcher.md`: "explore", "explore options", "what are my options", "solution options"
- [x] Mode registered in `core/mode-manifest.json` with required modules
- [x] Generator pipeline wired: `generate.py` context dict updated, `validate.py` markers added, Jinja2 templates updated
- [x] New mode file generated for Claude platform at `platforms/claude/modes/explore.md`
- [x] All existing tests pass after changes
- [x] Validation passes with `python3 generator/validate.py`

## Non-Goals

- This mode does not replace interview mode (interview is for vague ideas, explore is for clear problems with unclear approaches)
- This mode does not modify the evaluation system (that is action-routing and multi-persona-review territory)
- This mode does not produce a complete spec -- it produces a design direction that feeds into Phase 2
- No new external dependencies

## Dependencies

- depth-calibration (completed): Provides depth flag that may influence explore mode behavior
