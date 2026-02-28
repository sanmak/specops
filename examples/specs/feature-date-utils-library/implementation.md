# Implementation Notes: Date Utilities (@acme/date-utils)

## Decisions Made During Implementation
| Decision | Rationale | Task |
|----------|-----------|------|
| Used `Intl.RelativeTimeFormat` for `formatRelative` instead of manual string templates | Provides locale-aware pluralization and grammar out of the box; reduced format module size by ~0.4 KB | Task 4 |
| Chose `fast-check` for property-based testing | Caught a real bug: `addMonths(new Date('2024-01-31'), 1)` was returning March 2 instead of Feb 29 due to naive `setMonth` usage; switched to day-of-month clamping | Task 9 |
| Cached `Intl.DateTimeFormat` instances in a module-level `Map` keyed by `locale+timezone` | Construction cost is ~0.5ms per instance; caching yields 30x speedup on repeated `formatDate` and `toTimezone` calls in benchmarks | Tasks 4, 7 |

## Deviations from Design
| Planned | Actual | Reason |
|---------|--------|--------|
| Separate `@acme/date-utils-timezone` subpackage for timezone module | Merged into single package with subpath export `@acme/date-utils/timezone` | Timezone module was only 0.6 KB gzipped; separate package added npm overhead without meaningful tree-shaking benefit |
| Node >= 14 minimum | Bumped to Node >= 16 | `Intl.supportedValuesOf('timeZone')` is unavailable below Node 16; graceful fallback added but tested and documented as Node 16+ |

## Blockers Encountered
| Blocker | Resolution | Impact |
|---------|------------|--------|
| tsup generated incorrect `.d.ts` paths for subpath exports — types resolved to `dist/index.d.ts` instead of `dist/parse/index.d.ts` | Pinned tsup to v8.0.1 and configured explicit `entry` points per module in `tsup.config.ts` | Task 1 delayed by 3 hours |
| CJS output failed in Jest consumers due to ESM-only internal imports (`import` statements in `.cjs` files) | Added `__esModule` interop flag in tsup config and verified with a Jest test project | Task 8 delayed by 1 hour |

## Notes
- All 14 tasks completed over 9 working days (under the 2-week estimate)
- Final bundle size: 3.8 KB gzipped (full library), largest module is parse at 1.2 KB gzipped
- Test coverage: 99.7% lines, 98.9% branches — one unreachable catch block in the `Intl.supportedValuesOf` fallback accounts for the gap
- 2 internal projects (`@acme/dashboard` and `@acme/reporting-api`) adopted the library during the beta phase; both replaced `date-fns` with zero issues
