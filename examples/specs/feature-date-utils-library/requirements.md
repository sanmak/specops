# Library: Date Utilities (@acme/date-utils)

## Overview
Create a lightweight, tree-shakeable date utility library for parsing, formatting, validating, diffing, and converting dates across timezones. The library targets both Node.js and browser environments, ships as ESM + CJS dual build, carries zero runtime dependencies, and leverages the built-in `Intl.DateTimeFormat` API for locale-aware formatting and timezone support. The public API surface consists entirely of pure functions with strict TypeScript types, making the library easy to test, compose, and tree-shake.

## Developer Use Cases

### Use Case 1: Parse Date Strings
**As a** developer using this library
**I want** to parse date strings in multiple formats into native `Date` objects
**So that** I can work with dates from diverse API responses and user inputs without writing custom parsers

**Usage Example:**
```typescript
import { parseDate } from '@acme/date-utils';

parseDate('2024-03-15');                        // ISO 8601
parseDate('March 15, 2024');                    // Common locale format
parseDate('15/03/2024', 'DD/MM/YYYY');          // Custom format string
parseDate('2024-03-15T10:30:00Z');              // ISO 8601 with time
parseDate('invalid-date');                      // throws DateParseError
```

**Acceptance Criteria:**
- [ ] Parses ISO 8601 date and datetime strings (with and without timezone offset)
- [ ] Parses common locale formats (e.g., "March 15, 2024", "Mar 15, 2024")
- [ ] Parses custom format strings using token syntax (DD, MM, YYYY, HH, mm, ss)
- [ ] Returns a native `Date` object set to the correct instant
- [ ] Throws a typed `DateParseError` with the original input and expected format
- [ ] Provides a safe variant `parseDateSafe` returning `Date | null` instead of throwing

### Use Case 2: Format Dates
**As a** developer using this library
**I want** to format `Date` objects into human-readable strings with flexible token patterns and locale support
**So that** I can display dates consistently across the application without manual string concatenation

**Usage Example:**
```typescript
import { formatDate, formatRelative } from '@acme/date-utils';

formatDate(date, 'MMMM D, YYYY');              // "March 15, 2024"
formatDate(date, 'YYYY-MM-DD');                 // "2024-03-15"
formatDate(date, 'h:mm A');                     // "10:30 AM"
formatRelative(date);                           // "2 hours ago"
formatRelative(date, baseDate);                 // "in 3 days"
formatRelative(date, baseDate, 'es');           // "dentro de 3 días"
```

**Acceptance Criteria:**
- [ ] Supports token-based formatting (YYYY, MM, DD, HH, mm, ss, MMMM, D, h, A, etc.)
- [ ] Supports locale parameter for localized month/day names via `Intl.DateTimeFormat`
- [ ] `formatRelative` computes human-readable relative time ("2 hours ago", "in 3 days")
- [ ] `formatRelative` accepts optional base date and locale
- [ ] Throws `TypeError` if input is not a valid `Date`
- [ ] Handles edge cases: midnight, noon, year boundaries

### Use Case 3: Validate Dates
**As a** developer using this library
**I want** to validate date inputs including edge cases like leap years and month boundaries
**So that** I can reject invalid dates before they cause downstream errors

**Usage Example:**
```typescript
import { isValidDate, isLeapYear, daysInMonth } from '@acme/date-utils';

isValidDate('2024-02-29');                      // true (leap year)
isValidDate('2024-02-30');                      // false
isValidDate('not-a-date');                      // false
isLeapYear(2024);                               // true
isLeapYear(1900);                               // false (century rule)
daysInMonth(2024, 2);                           // 29
```

**Acceptance Criteria:**
- [ ] `isValidDate` accepts strings, numbers (timestamps), and `Date` objects
- [ ] Correctly identifies leap years including century and 400-year rules
- [ ] `daysInMonth` returns the correct day count for all months and years
- [ ] Does not rely on `Date` object coercion quirks (e.g., month overflow)
- [ ] Returns boolean only, never throws

### Use Case 4: Date Arithmetic
**As a** developer using this library
**I want** to add/subtract time units and compute differences between dates
**So that** I can calculate deadlines, durations, and period boundaries without manual math

**Usage Example:**
```typescript
import { addDays, addMonths, diffInDays, startOf, endOf } from '@acme/date-utils';

addDays(date, 7);                               // 7 days later
addDays(date, -3);                              // 3 days earlier
addMonths(new Date('2024-01-31'), 1);           // 2024-02-29 (clamped)
diffInDays(date1, date2);                       // integer difference
startOf(date, 'month');                         // first moment of the month
endOf(date, 'year');                            // last moment of the year
```

**Acceptance Criteria:**
- [ ] `addDays`, `addMonths`, `addYears` return new `Date` without mutating input
- [ ] Month arithmetic clamps overflow (Jan 31 + 1 month = Feb 28/29, not Mar 2/3)
- [ ] `diffInDays`, `diffInMonths`, `diffInYears` return signed integers
- [ ] `startOf` and `endOf` support units: day, week, month, quarter, year
- [ ] Handles DST transitions correctly (adding 1 day across spring-forward)
- [ ] All functions are pure — no side effects, no mutation

### Use Case 5: Timezone Handling
**As a** developer using this library
**I want** to convert dates between IANA timezones and query timezone offsets
**So that** I can display localized times for users in different regions

**Usage Example:**
```typescript
import { toTimezone, getTimezoneOffset, listTimezones } from '@acme/date-utils';

toTimezone(date, 'America/New_York');           // Date adjusted to ET
toTimezone(date, 'Asia/Tokyo');                 // Date adjusted to JST
getTimezoneOffset(date, 'Europe/London');       // +0 or +1 depending on DST
listTimezones();                                // string[] of all IANA zones
```

**Acceptance Criteria:**
- [ ] `toTimezone` converts a `Date` to the equivalent instant in the target timezone
- [ ] Uses `Intl.DateTimeFormat` under the hood — no bundled IANA data
- [ ] `getTimezoneOffset` returns the UTC offset in minutes for a given date and timezone
- [ ] `listTimezones` returns all IANA timezone identifiers from `Intl.supportedValuesOf`
- [ ] Handles DST transitions (spring-forward, fall-back) correctly
- [ ] Throws `RangeError` for invalid timezone identifiers

## API Design Principles
- **Pure functions**: Every export is a pure function — same input always yields the same output, no side effects
- **Immutability**: Input `Date` objects are never mutated; all operations return new instances
- **Typed errors**: Failures throw specific error subclasses (`DateParseError`, `DateRangeError`) rather than generic `Error`
- **Tree-shakeable exports**: Each module is independently importable via subpath exports (`@acme/date-utils/parse`)
- **Minimal API surface**: Expose the smallest set of functions that covers 95% of use cases; resist feature creep
- **Predictable naming**: Verb-first naming convention (`parseDate`, `formatDate`, `addDays`, `diffInDays`)

## Compatibility Requirements
- **Node.js**: >= 16.x (required for `Intl.supportedValuesOf`)
- **Browsers**: Last 2 versions of Chrome, Firefox, Safari, Edge
- **Module formats**: ESM (`.mjs`) and CJS (`.cjs`) dual build via tsup
- **TypeScript**: >= 4.7 (required for `exports` field resolution in `package.json`)
- **Bundle size**: < 5 KB gzipped for the full library; individual modules < 1.5 KB gzipped
- **No polyfills required**: Relies only on APIs available in the target environments

## Library Quality Requirements
- **Tree-shakeable**: Side-effect-free modules marked with `"sideEffects": false` in `package.json`
- **Zero dependencies**: No runtime dependencies; all dev dependencies are devDependencies only
- **Strict TypeScript**: `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`
- **100% JSDoc coverage**: Every exported function, type, and constant has JSDoc with `@param`, `@returns`, `@throws`, and `@example`
- **Comprehensive README**: Installation, quick start, full API reference, browser/Node compatibility table, bundle size badge
- **Semantic versioning**: Follows semver strictly; breaking changes only in major versions with migration guides

## Constraints & Assumptions

### Constraints
- Must not depend on moment.js, date-fns, dayjs, or any external date library
- Must handle DST edge cases correctly (spring-forward gaps, fall-back overlaps)
- Must not use deprecated `Date` patterns (e.g., `new Date(string)` for non-ISO formats, two-digit year parsing)
- Must not bundle IANA timezone data — rely on `Intl` API provided by the runtime
- Build output must include source maps for debugging

### Assumptions
- Target environments support `Intl.DateTimeFormat` with timezone option (Node 16+, modern browsers)
- Target environments support `Intl.supportedValuesOf('timeZone')` (Node 18+ at full accuracy; graceful fallback for Node 16)
- Consumers use a bundler that supports `package.json` `exports` field (webpack 5, Vite, esbuild)
- CI pipeline has access to npm registry for publishing

## Team Conventions
- Use TypeScript strict mode for all source code
- Write unit tests with Vitest; target 100% coverage on public API functions
- Follow existing code style (Prettier, ESLint with `@typescript-eslint`)
- Use conventional commits for changelog generation
- Document all public APIs with JSDoc including `@example` tags
- Keep individual functions under 40 lines; extract helpers for complex logic
- Prefer explicit types over `any` or type assertions
- Handle errors explicitly with typed error classes

## Success Metrics
- Bundle size < 5 KB gzipped (full library), < 1.5 KB per module
- 100% test coverage on all public API functions
- 3+ internal projects adopt the library within the first quarter
- Zero critical bugs reported in the first month after stable release
- npm download count > 500/week within 3 months of public release
- TypeScript type accuracy: zero reported type inference issues

## Out of Scope (Future Considerations)
- Calendar UI components or date picker widgets
- Recurrence rule parsing (RRULE / RFC 5545)
- Bundling locale data (rely on runtime `Intl` for locale support)
- Date-range or interval objects (e.g., `DateRange` class)
- Cron expression parsing
- Astronomy or holiday calculations
- Duration formatting (ISO 8601 duration strings)
