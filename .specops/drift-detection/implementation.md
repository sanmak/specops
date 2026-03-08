# Implementation Journal: Drift Detection & Guided Reconciliation

## Summary
6 tasks completed across core module, workflow routing, generator pipeline, validation, test consistency, and full integration. Key decisions: promoted drift check headings from H4 to H3 to match heading-prefixed validator markers (Gap 13 lesson applied proactively). All abstract ops use argument form throughout core/reconciliation.md (Gap 18). Non-interactive fallback explicit for reconcile mode (Gap 20). No hard-coded step numbers in workflow routing (Gap 21). COMMANDS.md updated with audit/reconcile rows and Drift Detection section (Gap 22). All 7 tests pass. Dogfood audit on 3 completed specs: all Healthy across all 5 checks.

## Decision Log
| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used H3 headings for drift checks (`### File Drift`, etc.) instead of H4 with "Check N:" prefix | Heading-level markers prevent substring collision in validators (Gap 13). H4 "Check N:" naming was verbose and the "Check N:" prefix added no semantic value. | Task 1 / Task 6 | 2026-03-08 |
| 2 | Reconcile mode requires `canAskInteractive: true`; audit works on all platforms | Audit is read-only and produces a report regardless of platform. Reconcile makes destructive edits to tasks.md and must confirm each repair — requires interactive input. | Task 1 | 2026-03-08 |
| 3 | All-specs audit targets `status ≠ completed` instead of all specs | Completed specs are frozen — auditing them for staleness would always produce false Warnings. Only active specs need drift detection. | Task 1 | 2026-03-08 |

## Deviations from Design
| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| `#### Check 1: File Drift` heading style | `### File Drift` heading style | Validator markers must match heading text exactly; H3 anchors prevent false positives; H4 "Check N:" prefix adds noise without value | Task 1 |

## Blockers Encountered

## Session Log
- 2026-03-08: Resumed from prior session. Tasks 1–4 already completed. Completed Task 5 (test_platform_consistency.py), then Task 6 (generate → validate → COMMANDS.md → tests → dogfood proof). Dogfood audit results: all 3 completed specs (ears-notation, bugfix-regression-analysis, steering-files) scored Healthy across all 5 drift checks. Discovered validator failure due to H4 heading mismatch — fixed by restructuring core/reconciliation.md to use H3 headings directly. All 7 tests pass.
