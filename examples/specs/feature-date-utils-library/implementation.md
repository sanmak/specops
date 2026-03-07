# Implementation Journal: Date Utilities (@acme/date-utils)

## Summary
All 14 tasks completed over 9 working days (under the 2-week estimate). 3 key decisions (Intl.RelativeTimeFormat, fast-check for property testing, cached Intl.DateTimeFormat). 2 deviations from design (merged timezone subpackage, bumped Node minimum to 16). 2 blockers resolved (tsup .d.ts paths, CJS/ESM interop). Final bundle: 3.8 KB gzipped, 99.7% test coverage.

## Decision Log
| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used `Intl.RelativeTimeFormat` for `formatRelative` instead of manual string templates | Provides locale-aware pluralization and grammar out of the box; reduced format module size by ~0.4 KB | Task 4 | 2025-03-05 |
| 2 | Chose `fast-check` for property-based testing | Caught a real bug: `addMonths(new Date('2024-01-31'), 1)` was returning March 2 instead of Feb 29 due to naive `setMonth` usage; switched to day-of-month clamping | Task 9 | 2025-03-10 |
| 3 | Cached `Intl.DateTimeFormat` instances in a module-level `Map` keyed by `locale+timezone` | Construction cost is ~0.5ms per instance; caching yields 30x speedup on repeated `formatDate` and `toTimezone` calls in benchmarks | Tasks 4, 7 | 2025-03-05 |

## Deviations from Design
| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| Separate `@acme/date-utils-timezone` subpackage for timezone module | Merged into single package with subpath export `@acme/date-utils/timezone` | Timezone module was only 0.6 KB gzipped; separate package added npm overhead without meaningful tree-shaking benefit | Task 7 |
| Node >= 14 minimum | Bumped to Node >= 16 | `Intl.supportedValuesOf('timeZone')` is unavailable below Node 16; graceful fallback added but tested and documented as Node 16+ | Task 7 |

## Blockers Encountered
| Blocker | Resolution | Impact | Task |
|---------|------------|--------|------|
| tsup generated incorrect `.d.ts` paths for subpath exports — types resolved to `dist/index.d.ts` instead of `dist/parse/index.d.ts` | Pinned tsup to v8.0.1 and configured explicit `entry` points per module in `tsup.config.ts` | Task 1 delayed by 3 hours | Task 1 |
| CJS output failed in Jest consumers due to ESM-only internal imports (`import` statements in `.cjs` files) | Added `__esModule` interop flag in tsup config and verified with a Jest test project | Task 8 delayed by 1 hour | Task 8 |

## Session Log
- **2025-03-03**: Started implementation. Completed Tasks 1-3. Blocker hit on Task 1 (tsup d.ts).
- **2025-03-05**: Resumed at Task 4. Completed Tasks 4-7.
- **2025-03-10**: Resumed at Task 8. Completed Tasks 8-14. Blocker hit on Task 8 (CJS interop). All tasks done.
