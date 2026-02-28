# Implementation Tasks: Date Utilities (@acme/date-utils)

## Task Breakdown

### Task 1: Initialize Project with TypeScript and tsup
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** None
**Priority:** High
**Documentation Required:** Yes (README.md scaffolding, package.json metadata)
**Breaking Change:** No

**Description:**
Set up the project repository with TypeScript strict mode, tsup build configuration for ESM + CJS dual output, Vitest for testing, and the `package.json` `exports` field for subpath imports.

**Implementation Steps:**
1. Initialize npm package with `npm init`
2. Install dev dependencies: `typescript`, `tsup`, `vitest`, `eslint`, `prettier`, `@typescript-eslint/eslint-plugin`
3. Create `tsconfig.json` with strict mode, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`
4. Create `tsup.config.ts` with entry points for each module, ESM + CJS output, `dts: true`
5. Configure `package.json` `exports` field mapping each subpath to its build artifacts
6. Set `"sideEffects": false` in `package.json` for tree-shaking
7. Create `vitest.config.ts` with coverage configuration
8. Add ESLint and Prettier configs
9. Create `.gitignore`, `.npmignore`, `LICENSE`
10. Scaffold `src/` directory structure with empty `index.ts` files

**Acceptance Criteria:**
- [ ] `npm run build` produces `dist/` with `.mjs`, `.cjs`, and `.d.ts` files for each module
- [ ] `npm run test` runs Vitest with zero tests passing (placeholder)
- [ ] `npm run lint` runs ESLint with no errors on empty modules
- [ ] TypeScript strict mode enabled with all recommended flags
- [ ] `package.json` `exports` field correctly maps all subpaths
- [ ] `"sideEffects": false` set for tree-shaking support

**Files to Create/Modify:**
- `package.json`
- `tsconfig.json`
- `tsup.config.ts`
- `vitest.config.ts`
- `.eslintrc.cjs`
- `.prettierrc`
- `src/index.ts`
- `src/parse/index.ts`
- `src/format/index.ts`
- `src/validate/index.ts`
- `src/arithmetic/index.ts`
- `src/timezone/index.ts`

**Tests Required:**
- [ ] Build completes without errors
- [ ] Output files exist in expected locations
- [ ] TypeScript compilation succeeds in strict mode

---

### Task 2: Define Core Types and Error Classes
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** None
**Priority:** High
**Documentation Required:** Yes (JSDoc on all exports)
**Breaking Change:** No

**Description:**
Define the shared TypeScript types (`DateUnit`, `FormatToken`, `TimezoneString`) and error classes (`DateParseError`, `DateRangeError`) used across all modules.

**Implementation Steps:**
1. Create `src/types.ts` with `DateUnit`, `FormatToken`, `TimezoneString` type definitions
2. Create `src/errors.ts` with `DateParseError` and `DateRangeError` classes
3. `DateParseError` properties: `input`, `expectedFormat`, `code`
4. `DateRangeError` properties: `value`, `min`, `max`, `code`
5. Both errors extend `Error` and set `name` for clean stack traces
6. Add comprehensive JSDoc with `@example` tags on all exports
7. Export types and errors from `src/index.ts`

**Acceptance Criteria:**
- [ ] `DateParseError` extends `Error` with `input`, `expectedFormat`, and `code` properties
- [ ] `DateRangeError` extends `Error` with `value`, `min`, `max`, and `code` properties
- [ ] Both error classes set `name` and support `instanceof` checks
- [ ] `DateUnit` type includes: `'day'`, `'week'`, `'month'`, `'quarter'`, `'year'`
- [ ] `FormatToken` type includes all documented tokens
- [ ] All exports have JSDoc documentation

**Files to Create/Modify:**
- `src/types.ts`
- `src/errors.ts`
- `src/index.ts`

**Tests Required:**
- [ ] `DateParseError` captures input and format correctly
- [ ] `DateRangeError` captures value, min, max correctly
- [ ] `instanceof` checks work for both error classes
- [ ] Error `name` property is set correctly
- [ ] Error `message` is human-readable

---

### Task 3: Implement Parse Module
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 2
**Priority:** High
**Documentation Required:** Yes (JSDoc with `@example`, `@throws`)
**Breaking Change:** No

**Description:**
Implement `parseDate` and `parseDateSafe` functions supporting ISO 8601, common locale formats, and custom format string parsing.

**Implementation Steps:**
1. Create `src/parse/iso.ts` — strict ISO 8601 regex parser for date, datetime, and datetime with offset
2. Create `src/parse/locale.ts` — recognize common English locale formats ("March 15, 2024", "Mar 15, 2024")
3. Create `src/parse/custom.ts` — tokenize format string and match positionally against input
4. Create `src/parse/index.ts` — `parseDate` tries ISO first, then locale, then custom (if format provided); throws `DateParseError` on failure
5. Implement `parseDateSafe` as a wrapper that catches `DateParseError` and returns `null`
6. Validate parsed components (month 1-12, day 1-N, hour 0-23, etc.) before constructing `Date`
7. Add JSDoc with examples on all exports

**Acceptance Criteria:**
- [ ] Parses ISO 8601 dates: `2024-03-15`, `2024-03-15T10:30:00`, `2024-03-15T10:30:00Z`, `2024-03-15T10:30:00+05:30`
- [ ] Parses locale formats: `March 15, 2024`, `Mar 15, 2024`
- [ ] Parses custom formats: `DD/MM/YYYY`, `MM-DD-YYYY`, `YYYY.MM.DD`
- [ ] Throws `DateParseError` with `input` and `expectedFormat` for unparseable strings
- [ ] `parseDateSafe` returns `null` for unparseable strings (never throws)
- [ ] Rejects structurally valid but semantically invalid dates (e.g., `2024-02-30`)
- [ ] No reliance on `new Date(string)` for non-ISO formats

**Files to Create/Modify:**
- `src/parse/index.ts`
- `src/parse/iso.ts`
- `src/parse/locale.ts`
- `src/parse/custom.ts`
- `src/parse/errors.ts` (re-export from shared)

**Tests Required:**
- [ ] ISO 8601 date parsing (date only, datetime, with offset, with Z)
- [ ] Locale format parsing (full month, abbreviated month)
- [ ] Custom format parsing (DD/MM/YYYY, MM-DD-YYYY, etc.)
- [ ] Invalid input throws `DateParseError`
- [ ] `parseDateSafe` returns `null` for invalid input
- [ ] Semantic validation (Feb 30, month 13, hour 25 rejected)
- [ ] Edge cases: midnight, year boundaries, negative timezone offsets

---

### Task 4: Implement Format Module
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 2
**Priority:** High
**Documentation Required:** Yes (JSDoc with `@example`, token reference table)
**Breaking Change:** No

**Description:**
Implement `formatDate` for token-based formatting and `formatRelative` for human-readable relative time strings using `Intl.RelativeTimeFormat`.

**Implementation Steps:**
1. Create `src/format/tokens.ts` — define token-to-extractor mapping, implement `formatDate`
2. Support tokens: `YYYY`, `YY`, `MMMM`, `MMM`, `MM`, `M`, `DD`, `D`, `HH`, `H`, `hh`, `h`, `mm`, `m`, `ss`, `s`, `SSS`, `A`, `a`
3. For month/day name tokens (`MMMM`, `MMM`), use `Intl.DateTimeFormat` with the provided locale
4. Cache `Intl.DateTimeFormat` instances per locale in a module-level `Map`
5. Create `src/format/relative.ts` — implement `formatRelative` using `Intl.RelativeTimeFormat`
6. Auto-select the best unit (seconds, minutes, hours, days, months, years) based on delta magnitude
7. Cache `Intl.RelativeTimeFormat` instances per locale
8. Validate input is a `Date` with `getTime()` that returns a number; throw `TypeError` otherwise

**Acceptance Criteria:**
- [ ] `formatDate(date, 'MMMM D, YYYY')` produces "March 15, 2024"
- [ ] `formatDate(date, 'YYYY-MM-DD')` produces "2024-03-15"
- [ ] `formatDate(date, 'h:mm A')` produces "10:30 AM"
- [ ] Locale parameter works for month names via `Intl.DateTimeFormat`
- [ ] `formatRelative` produces "2 hours ago", "in 3 days", "1 year ago" etc.
- [ ] `formatRelative` locale parameter produces localized output
- [ ] Throws `TypeError` for non-Date inputs
- [ ] `Intl` instances are cached (no repeated construction)

**Files to Create/Modify:**
- `src/format/index.ts`
- `src/format/tokens.ts`
- `src/format/relative.ts`

**Tests Required:**
- [ ] All format tokens produce correct output
- [ ] Locale-aware month names (en, de, ja, es)
- [ ] AM/PM formatting
- [ ] Relative time: seconds, minutes, hours, days, months, years
- [ ] Relative time with custom base date
- [ ] Relative time with locale
- [ ] TypeError for invalid Date input
- [ ] Edge cases: midnight (12:00 AM), noon (12:00 PM), year boundary

---

### Task 5: Implement Validate Module
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** Task 2
**Priority:** High
**Documentation Required:** Yes (JSDoc with `@example`)
**Breaking Change:** No

**Description:**
Implement `isValidDate`, `isLeapYear`, and `daysInMonth` utility functions for date validation and calendar queries.

**Implementation Steps:**
1. Implement `isLeapYear` using the Gregorian rule (div by 4, not 100, except 400)
2. Implement `daysInMonth` using a lookup array with leap year adjustment for February
3. Implement `isValidDate` that accepts strings, numbers, and `Date` objects
4. For string input, attempt structured parsing (not `new Date(string)`) and validate components
5. For number input, check `Number.isFinite` and within valid timestamp range
6. For `Date` input, check `!isNaN(date.getTime())`
7. All functions return boolean only, never throw

**Acceptance Criteria:**
- [ ] `isLeapYear(2024)` returns `true` (divisible by 4)
- [ ] `isLeapYear(1900)` returns `false` (century rule)
- [ ] `isLeapYear(2000)` returns `true` (400-year rule)
- [ ] `daysInMonth(2024, 2)` returns `29` (leap year February)
- [ ] `daysInMonth(2023, 2)` returns `28` (non-leap year February)
- [ ] `isValidDate('2024-02-29')` returns `true`
- [ ] `isValidDate('2024-02-30')` returns `false`
- [ ] `isValidDate('not-a-date')` returns `false`
- [ ] All functions return boolean; none throw exceptions

**Files to Create/Modify:**
- `src/validate/index.ts`

**Tests Required:**
- [ ] Leap year positive cases (2024, 2000, 1600)
- [ ] Leap year negative cases (1900, 2100, 2023)
- [ ] Days in month for all 12 months in a non-leap year
- [ ] Days in month for February in a leap year
- [ ] `isValidDate` with valid ISO strings
- [ ] `isValidDate` with invalid strings
- [ ] `isValidDate` with timestamp numbers
- [ ] `isValidDate` with `Date` objects (valid and invalid)
- [ ] `isValidDate` with null, undefined, NaN (returns false)

---

### Task 6: Implement Arithmetic Module
**Status:** Pending
**Estimated Effort:** M (3-4 hours)
**Dependencies:** Task 2
**Priority:** High
**Documentation Required:** Yes (JSDoc with `@example`, DST behavior notes)
**Breaking Change:** No

**Description:**
Implement date addition (`addDays`, `addMonths`, `addYears`), differencing (`diffInDays`, `diffInMonths`, `diffInYears`), and boundary functions (`startOf`, `endOf`).

**Implementation Steps:**
1. Create `src/arithmetic/add.ts` — `addDays` (UTC millisecond math), `addMonths` (with day clamping), `addYears`
2. `addMonths` clamps day-of-month to the target month's max (e.g., Jan 31 + 1 = Feb 28/29)
3. `addDays` normalizes to UTC milliseconds to handle DST transitions
4. Create `src/arithmetic/diff.ts` — `diffInDays` (normalize to midnight UTC, divide), `diffInMonths`, `diffInYears`
5. All diff functions return signed integers (positive if `a > b`)
6. Create `src/arithmetic/boundaries.ts` — `startOf` and `endOf` for `DateUnit` values
7. `startOf('week')` uses Monday as the first day (ISO 8601)
8. `endOf` sets to the last millisecond (23:59:59.999)
9. All functions are pure — return new `Date`, never mutate input
10. Validate inputs: throw `TypeError` if date is not a valid `Date`

**Acceptance Criteria:**
- [ ] `addDays(date, 7)` returns a date 7 days later without mutating input
- [ ] `addDays(date, -3)` returns a date 3 days earlier
- [ ] `addMonths(Jan 31, 1)` returns Feb 28/29 (clamped, not March 2/3)
- [ ] `addYears(Feb 29, 1)` returns Feb 28 (clamped for non-leap year)
- [ ] `diffInDays` returns correct signed integer difference
- [ ] `diffInMonths` and `diffInYears` return whole-unit differences
- [ ] `startOf(date, 'month')` returns first moment of the month
- [ ] `endOf(date, 'year')` returns 2024-12-31T23:59:59.999
- [ ] DST transitions do not cause off-by-one errors in `addDays`
- [ ] All functions are pure (input not mutated)

**Files to Create/Modify:**
- `src/arithmetic/index.ts`
- `src/arithmetic/add.ts`
- `src/arithmetic/diff.ts`
- `src/arithmetic/boundaries.ts`

**Tests Required:**
- [ ] Add positive and negative days
- [ ] Month addition with day-of-month clamping (Jan 31 + 1, Mar 31 + 1)
- [ ] Year addition across leap year boundary (Feb 29 + 1 year)
- [ ] Diff in days, months, years (positive and negative)
- [ ] startOf for all DateUnit values (day, week, month, quarter, year)
- [ ] endOf for all DateUnit values
- [ ] DST spring-forward: addDays across March transition (US timezone)
- [ ] DST fall-back: addDays across November transition (US timezone)
- [ ] Input immutability (original Date unchanged after operation)
- [ ] TypeError for invalid Date input

---

### Task 7: Implement Timezone Module
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 2
**Priority:** High
**Documentation Required:** Yes (JSDoc with `@example`, runtime requirements note)
**Breaking Change:** No

**Description:**
Implement `toTimezone`, `getTimezoneOffset`, and `listTimezones` using the `Intl.DateTimeFormat` API for zero-bundle-cost timezone support.

**Implementation Steps:**
1. Implement `toTimezone` — construct `Intl.DateTimeFormat` with `timeZone` option, extract date parts via `formatToParts`, reconstruct a `Date`
2. Implement `getTimezoneOffset` — compare UTC representation to localized representation, compute delta in minutes
3. Implement `listTimezones` — use `Intl.supportedValuesOf('timeZone')` with try/catch fallback for Node 16-17
4. Cache `Intl.DateTimeFormat` instances per timezone string in a module-level `Map`
5. Let `RangeError` from `Intl.DateTimeFormat` propagate for invalid timezone identifiers
6. Add JSDoc documenting runtime requirements (Node 16+, modern browsers)

**Acceptance Criteria:**
- [ ] `toTimezone(utcDate, 'America/New_York')` returns the correct ET equivalent
- [ ] `toTimezone` handles DST correctly (EDT vs EST)
- [ ] `getTimezoneOffset` returns correct offset in minutes (e.g., -300 for EST, -240 for EDT)
- [ ] `listTimezones()` returns a non-empty string array in Node 18+ and modern browsers
- [ ] `listTimezones()` returns empty array with console warning in Node 16-17
- [ ] Invalid timezone throws `RangeError`
- [ ] `Intl.DateTimeFormat` instances are cached per timezone

**Files to Create/Modify:**
- `src/timezone/index.ts`

**Tests Required:**
- [ ] Convert UTC to America/New_York (EST and EDT)
- [ ] Convert UTC to Asia/Tokyo (no DST)
- [ ] Convert UTC to Europe/London (GMT and BST)
- [ ] Offset for America/New_York in winter (EST = -300) and summer (EDT = -240)
- [ ] `listTimezones` returns an array (may be empty in older runtimes)
- [ ] Invalid timezone throws `RangeError`
- [ ] DST transition dates produce correct results

---

### Task 8: Create Barrel Exports and Package.json Exports Map
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7
**Priority:** High
**Documentation Required:** Yes (update README with import examples)
**Breaking Change:** No

**Description:**
Wire up the barrel export (`src/index.ts`) and configure the `package.json` `exports` field so consumers can use both full imports (`@acme/date-utils`) and subpath imports (`@acme/date-utils/parse`).

**Implementation Steps:**
1. Update `src/index.ts` to re-export all public functions and types from all 5 modules
2. Configure `package.json` `exports` field with conditional exports for ESM, CJS, and types
3. Add `"main"` and `"module"` fields for backward compatibility
4. Add `"types"` field pointing to the main declaration file
5. Verify tsup builds all entry points correctly
6. Test that subpath imports resolve in both ESM and CJS consumers
7. Add `"files"` field to `package.json` to include only `dist/` in the published package

**Acceptance Criteria:**
- [ ] `import { parseDate } from '@acme/date-utils'` works (barrel import)
- [ ] `import { parseDate } from '@acme/date-utils/parse'` works (subpath import)
- [ ] `const { parseDate } = require('@acme/date-utils')` works (CJS)
- [ ] `const { parseDate } = require('@acme/date-utils/parse')` works (CJS subpath)
- [ ] TypeScript resolves types correctly for all import paths
- [ ] Build produces correct file structure under `dist/`
- [ ] Published package only includes `dist/`, `README.md`, `LICENSE`, `package.json`

**Files to Create/Modify:**
- `src/index.ts`
- `package.json` (exports, main, module, types, files)
- `tsup.config.ts` (entry points)

**Tests Required:**
- [ ] Build output structure matches exports field expectations
- [ ] ESM import resolution works
- [ ] CJS require resolution works
- [ ] TypeScript declaration files resolve for all subpaths

---

### Task 9: Write Comprehensive Test Suite
**Status:** Pending
**Estimated Effort:** L (5-6 hours)
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
**Priority:** High
**Documentation Required:** No
**Breaking Change:** No

**Description:**
Write the full test suite including unit tests for every exported function, property-based tests with fast-check, edge case coverage for DST and leap years, and cross-module integration tests.

**Implementation Steps:**
1. Install `fast-check` for property-based testing
2. Write unit tests for `parse` module (ISO, locale, custom, error cases)
3. Write unit tests for `format` module (all tokens, locale, relative time)
4. Write unit tests for `validate` module (leap years, days in month, all input types)
5. Write unit tests for `arithmetic` module (add, diff, boundaries, DST)
6. Write unit tests for `timezone` module (conversion, offset, list)
7. Write property-based tests: parse/format round-trip, add/subtract identity, diff/add consistency
8. Write integration tests: parse -> format -> parse round-trip, arithmetic -> diff consistency
9. Write DST-specific test suite with known transition dates
10. Configure coverage reporting; verify 100% on public API

**Acceptance Criteria:**
- [ ] Every exported function has at least 5 unit test cases
- [ ] Property-based tests cover: parse/format round-trip, add/subtract identity, diff/add consistency
- [ ] DST test suite covers spring-forward and fall-back for US, EU, and Australia
- [ ] Leap year edge cases tested across multiple centuries
- [ ] Invalid input handling tested for every function
- [ ] 100% line coverage on all `src/` files
- [ ] All tests pass in CI across Node 16, 18, 20

**Files to Create/Modify:**
- `tests/parse.test.ts`
- `tests/format.test.ts`
- `tests/validate.test.ts`
- `tests/arithmetic.test.ts`
- `tests/timezone.test.ts`
- `tests/property.test.ts`
- `tests/integration.test.ts`
- `tests/dst.test.ts`

**Tests Required:**
- [ ] 100% line coverage achieved on `src/`
- [ ] All property-based tests pass with 1000+ iterations
- [ ] DST edge cases pass across Node versions

---

### Task 10: Set Up CI/CD with GitHub Actions
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 9
**Priority:** Medium
**Documentation Required:** Yes (CONTRIBUTING.md with CI workflow description)
**Breaking Change:** No

**Description:**
Configure GitHub Actions workflows for CI (lint, type-check, test, build, size check) and CD (npm publish on tag push with provenance).

**Implementation Steps:**
1. Create `.github/workflows/ci.yml` — runs on push to main and PRs
2. CI matrix: Node 16, 18, 20, latest on Ubuntu
3. CI steps: install, lint, type-check, test with coverage, build, size check
4. Create `.github/workflows/publish.yml` — runs on `v*` tag push
5. Publish steps: install, lint, type-check, test, build, size check, `npm publish --provenance`
6. Configure `size-limit` in `package.json` with per-module budgets
7. Add `commitlint` and Husky for conventional commit enforcement
8. Add status badges to README

**Acceptance Criteria:**
- [ ] CI runs automatically on push to main and on PRs
- [ ] CI tests across Node 16, 18, 20, and latest
- [ ] CI fails if lint, type-check, tests, or size-limit fail
- [ ] Publish workflow triggers on `v*` tag push
- [ ] npm publish includes `--provenance` flag
- [ ] Size-limit check reports per-module and total sizes
- [ ] `CONTRIBUTING.md` documents the CI workflow

**Files to Create/Modify:**
- `.github/workflows/ci.yml`
- `.github/workflows/publish.yml`
- `package.json` (size-limit config, commitlint config)
- `.husky/commit-msg`
- `CONTRIBUTING.md`

**Tests Required:**
- [ ] CI workflow runs successfully on a test push
- [ ] Size-limit check reports sizes accurately
- [ ] Publish workflow dry-run passes

---

### Task 11: Bundle Size Optimization and Verification
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 8
**Priority:** Medium
**Documentation Required:** No
**Breaking Change:** No

**Description:**
Optimize the built output to meet the < 5 KB gzipped budget for the full library and < 1.5 KB per module, and set up automated size tracking.

**Implementation Steps:**
1. Install `size-limit` and `@size-limit/preset-small-lib`
2. Configure size-limit in `package.json` with entries for each module and the full library
3. Run `size-limit` and analyze current sizes
4. Optimize: remove dead code, consolidate shared helpers, minimize regex patterns
5. Verify tree-shaking works by creating a test consumer that imports one function
6. Configure tsup minification for production builds
7. Add `size-limit` to CI pipeline (already created in Task 10, verify integration)
8. Document size budget in README with a badge

**Acceptance Criteria:**
- [ ] Full library bundle < 5 KB gzipped
- [ ] Each module bundle < 1.5 KB gzipped
- [ ] Tree-shaking verified: importing one function does not pull in other modules
- [ ] `size-limit` check integrated in CI and blocks on budget exceed
- [ ] Size badge displayed in README

**Files to Create/Modify:**
- `package.json` (size-limit configuration)
- `tsup.config.ts` (minification settings)
- `README.md` (size badge)

**Tests Required:**
- [ ] `size-limit` passes for all entries
- [ ] Tree-shaking test: single-function import produces minimal output
- [ ] Build output analysis shows no unexpected large modules

---

### Task 12: Write API Documentation
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
**Priority:** Medium
**Documentation Required:** Yes (this IS the documentation task)
**Breaking Change:** No

**Description:**
Write comprehensive API documentation including README with quick start, full API reference for every exported function, browser/Node compatibility table, and migration guide template.

**Implementation Steps:**
1. Write README.md sections: Installation, Quick Start, API Reference, Browser/Node Compatibility, Bundle Size, Contributing, License
2. API Reference: document every exported function with signature, description, parameters, return type, throws, and example
3. Create compatibility table showing Node and browser version requirements
4. Add bundle size badges (full library, per module)
5. Write `MIGRATION.md` template for future major version upgrades
6. Verify all JSDoc `@example` tags in source code are accurate and runnable
7. Add TypeDoc or API Extractor configuration for auto-generated reference (optional)

**Acceptance Criteria:**
- [ ] README includes: Installation, Quick Start (copy-paste working example), API Reference
- [ ] Every exported function documented with signature, params, returns, throws, example
- [ ] Compatibility table shows Node >= 16, browser versions, TypeScript >= 4.7
- [ ] Bundle size badges display accurate numbers
- [ ] `MIGRATION.md` template created for future use
- [ ] All JSDoc `@example` tags are valid TypeScript that compiles

**Files to Create/Modify:**
- `README.md`
- `MIGRATION.md`
- `src/**/*.ts` (verify JSDoc accuracy)

**Tests Required:**
- [ ] README examples compile and run correctly (manual or snapshot test)
- [ ] JSDoc examples are valid TypeScript

---

### Task 13: Browser Compatibility Testing
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
**Priority:** Medium
**Documentation Required:** No
**Breaking Change:** No

**Description:**
Set up and run browser compatibility tests using Playwright to verify the library works correctly in Chromium, Firefox, and WebKit, with particular focus on `Intl.DateTimeFormat` consistency.

**Implementation Steps:**
1. Install `@playwright/test` as a dev dependency
2. Create `playwright.config.ts` with Chromium, Firefox, WebKit projects
3. Create browser test files that run the same assertions as the Vitest unit tests
4. Focus on `Intl`-dependent functions: `formatDate` with locale, `formatRelative`, `toTimezone`, `listTimezones`
5. Test `listTimezones()` returns non-empty arrays in all browsers
6. Compare `toTimezone` results across engines for known DST transition dates
7. Document any cross-browser inconsistencies found
8. Add browser tests to CI as a separate workflow step

**Acceptance Criteria:**
- [ ] All public API functions pass tests in Chromium, Firefox, and WebKit
- [ ] `Intl.DateTimeFormat` timezone support works in all three engines
- [ ] `listTimezones()` returns consistent results across engines
- [ ] DST transitions produce consistent results across engines
- [ ] Known inconsistencies (if any) are documented in README
- [ ] Browser tests run in CI

**Files to Create/Modify:**
- `playwright.config.ts`
- `tests/browser/parse.spec.ts`
- `tests/browser/format.spec.ts`
- `tests/browser/timezone.spec.ts`
- `.github/workflows/ci.yml` (add browser test step)

**Tests Required:**
- [ ] Parse module works in all 3 browsers
- [ ] Format module (including Intl) works in all 3 browsers
- [ ] Timezone module works in all 3 browsers
- [ ] Cross-engine consistency verified for DST edge cases

---

### Task 14: Publish Beta and Gather Feedback
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13
**Priority:** Medium
**Documentation Required:** Yes (CHANGELOG.md, GitHub Release notes)
**Breaking Change:** No

**Description:**
Publish the first beta release to npm, create a GitHub Release, share with internal teams for feedback, and set up a feedback tracking mechanism.

**Implementation Steps:**
1. Generate changelog from conventional commits using `conventional-changelog-cli`
2. Set version to `0.1.0-beta.1` in `package.json`
3. Run full CI pipeline locally: lint, type-check, test, build, size-limit
4. Create and push git tag `v0.1.0-beta.1`
5. Verify GitHub Actions publish workflow triggers and publishes with `--tag beta`
6. Create GitHub Release with auto-generated notes
7. Share package link with 3+ internal teams for adoption
8. Create a GitHub Discussions board or issue template for feedback
9. Monitor npm downloads and issue reports

**Acceptance Criteria:**
- [ ] `@acme/date-utils@0.1.0-beta.1` published to npm with `beta` dist-tag
- [ ] `npm install @acme/date-utils@beta` installs successfully
- [ ] GitHub Release created with changelog and install instructions
- [ ] Package includes only `dist/`, `README.md`, `LICENSE`, `package.json`
- [ ] npm provenance attestation attached to the published version
- [ ] At least 3 internal teams notified and provided adoption guide
- [ ] Feedback tracking mechanism in place (GitHub Issues or Discussions)

**Files to Create/Modify:**
- `package.json` (version bump)
- `CHANGELOG.md`

**Tests Required:**
- [ ] Published package installs and imports correctly in a fresh project
- [ ] Both ESM and CJS imports work from the published package
- [ ] TypeScript types resolve correctly from the published package

---

## Implementation Order

### Week 1: Foundation and Core Modules

**Day 1:**
1. Task 1: Initialize Project (foundation — all other tasks depend on this)
2. Task 2: Core Types and Errors (foundation for all modules)

**Day 2-3:**
3. Task 3: Parse Module (depends on Task 2)
4. Task 4: Format Module (depends on Task 2, parallel with Task 3)
5. Task 5: Validate Module (depends on Task 2, parallel with Tasks 3-4)

**Day 4-5:**
6. Task 6: Arithmetic Module (depends on Task 2)
7. Task 7: Timezone Module (depends on Task 2)
8. Task 8: Barrel Exports and Exports Map (depends on Tasks 3-7)

### Week 2: Quality, Documentation, and Release

**Day 1-2:**
9. Task 9: Comprehensive Test Suite (depends on Tasks 3-8)
10. Task 11: Bundle Size Optimization (depends on Task 8, parallel with Task 9)

**Day 3:**
11. Task 10: CI/CD with GitHub Actions (depends on Task 9)
12. Task 13: Browser Compatibility Testing (depends on Tasks 3-8, parallel with Task 10)

**Day 4:**
13. Task 12: API Documentation (depends on Tasks 3-8)

**Day 5:**
14. Task 14: Publish Beta (depends on all previous tasks)

## Progress Tracking

**Total Tasks:** 14
**Completed:** 0
**In Progress:** 0
**Remaining:** 14

**Estimated Total Effort:** ~30-35 hours (~2 weeks for 1 developer)

### Status Legend
- **Pending**: Not started
- **In Progress**: Currently being worked on
- **Completed**: Done and tested
- **Blocked**: Waiting on dependencies or external factors

### Progress by Category
- **Project Setup**: 0/2 (Tasks 1-2)
- **Core Modules**: 0/5 (Tasks 3-7)
- **Integration**: 0/1 (Task 8)
- **Testing**: 0/2 (Tasks 9, 13)
- **CI/CD**: 0/1 (Task 10)
- **Optimization**: 0/1 (Task 11)
- **Documentation**: 0/1 (Task 12)
- **Release**: 0/1 (Task 14)

## Notes

- Tasks 1-2 are foundational and must be completed first
- Tasks 3-7 (core modules) can be developed in parallel after Tasks 1-2
- Task 8 (barrel exports) requires all modules but is lightweight
- Task 9 (test suite) is the largest single task; consider writing tests alongside module development
- Task 11 (size optimization) should start as soon as Task 8 is done, before tests are finalized
- Task 13 (browser tests) can run in parallel with CI setup and documentation
- Task 14 (publish beta) is the final gate — all previous tasks must pass
- No tasks have a "Breaking Change: Yes" flag because this is a greenfield library (v0.x)

## Risk Items

- **Intl API availability**: If Node 16 support proves too limiting for `Intl.supportedValuesOf`, consider bumping minimum to Node 18 (Task 7)
- **Bundle size**: If the 5 KB budget is too tight, consider dropping custom format string parsing (the largest module) into a separate optional package
- **DST edge cases**: `addDays` across DST boundaries needs careful testing; budget extra time for Task 6
- **tsup .d.ts generation**: tsup's DTS plugin can produce incorrect paths for subpath exports; test early in Task 1 and pin version if needed
- **fast-check performance**: Property-based tests may slow CI; limit iterations to 1000 in CI, 10000 locally
