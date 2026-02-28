# Library Design: Date Utilities (@acme/date-utils)

## Architecture Overview

The library is structured as a single npm package with five internal modules, each responsible for a distinct concern of date manipulation. All public exports are pure functions — no classes, no singletons, no shared mutable state.

**Key architectural properties:**

- **Single-package, multi-module**: One npm package (`@acme/date-utils`) with subpath exports for tree-shaking (`@acme/date-utils/parse`, `@acme/date-utils/format`, etc.)
- **Pure function design**: Every exported function is deterministic, side-effect-free, and never mutates its inputs
- **ESM + CJS dual build**: Built with tsup to produce `.mjs` (ESM), `.cjs` (CJS), and `.d.ts` (TypeScript declarations) for each module
- **Subpath exports**: `package.json` `exports` field maps each module to its built artifacts, enabling bundler-level tree-shaking
- **Zero runtime dependencies**: All functionality is implemented in pure TypeScript using only built-in APIs (`Date`, `Intl`, `Math`)

```
@acme/date-utils/
├── src/
│   ├── parse/          # Date parsing functions
│   │   ├── index.ts
│   │   ├── iso.ts      # ISO 8601 parsing
│   │   ├── locale.ts   # Natural language parsing
│   │   ├── custom.ts   # Custom format string parsing
│   │   └── errors.ts   # DateParseError
│   ├── format/         # Date formatting functions
│   │   ├── index.ts
│   │   ├── tokens.ts   # Token-based formatting
│   │   └── relative.ts # Relative time formatting
│   ├── validate/       # Date validation functions
│   │   └── index.ts
│   ├── arithmetic/     # Date math functions
│   │   ├── index.ts
│   │   ├── add.ts      # addDays, addMonths, addYears
│   │   ├── diff.ts     # diffInDays, diffInMonths, diffInYears
│   │   └── boundaries.ts # startOf, endOf
│   ├── timezone/       # Timezone conversion functions
│   │   └── index.ts
│   ├── errors.ts       # Shared error classes
│   ├── types.ts        # Shared type definitions
│   └── index.ts        # Barrel export
├── dist/               # Build output (ESM, CJS, .d.ts)
├── tsconfig.json
├── tsup.config.ts
├── vitest.config.ts
├── package.json
└── README.md
```

## Technical Decisions

### Decision 1: Build Tool — tsup vs Rollup vs esbuild

**Context:** Need a build tool that produces ESM + CJS dual output with TypeScript declaration files, supports subpath exports, and minimizes configuration overhead.

**Options Considered:**
1. **tsup** — Zero-config TypeScript bundler built on esbuild
   - Pros: Near-zero configuration, built-in `.d.ts` generation via `dts: true`, esbuild speed, dual ESM/CJS output with a single flag, active maintenance
   - Cons: Less control over advanced Rollup-style plugins, smaller plugin ecosystem
2. **Rollup** — Industry-standard bundler
   - Pros: Mature ecosystem, fine-grained output control, excellent tree-shaking, many plugins
   - Cons: Verbose configuration, requires `@rollup/plugin-typescript` and `rollup-plugin-dts` for TypeScript, slower builds
3. **Raw esbuild** — Ultra-fast bundler
   - Pros: Fastest build times, minimal API
   - Cons: No built-in `.d.ts` generation (requires separate `tsc --emitDeclarationOnly`), more manual configuration for dual output

**Decision:** tsup
**Rationale:**
- Single `tsup.config.ts` handles ESM, CJS, and `.d.ts` output with minimal boilerplate
- esbuild-powered speed means builds complete in < 500ms even for the full library
- Built-in `dts: true` generates declaration files without a separate `tsc` pass
- `splitting: true` enables code-splitting for ESM output, improving tree-shaking
- First-class support for `package.json` `exports` field patterns

### Decision 2: Timezone Approach — Intl API vs Bundled IANA Data

**Context:** The library needs timezone conversion and offset querying. Must work in Node.js and browsers without inflating bundle size.

**Options Considered:**
1. **`Intl.DateTimeFormat` with `timeZone` option** — Use the runtime's built-in timezone database
   - Pros: Zero bundle cost, always up-to-date (updated with OS/browser), accurate for all IANA zones, supports DST transitions
   - Cons: Relies on runtime support (Node 16+, modern browsers), slight inconsistencies between engines, `Intl.supportedValuesOf('timeZone')` requires Node 18+ (fallback needed for 16-17)
2. **Bundled IANA timezone data** (e.g., `@formatjs/intl-datetimeformat` polyfill or `moment-timezone` data)
   - Pros: Consistent across environments, works in older runtimes
   - Cons: Adds 20-80 KB to bundle size, must be updated regularly, defeats the "zero dependencies" goal
3. **UTC-offset only** — Only support fixed UTC offsets (e.g., `+05:30`), not named timezones
   - Pros: Trivial to implement, zero external data
   - Cons: Cannot handle DST, cannot use IANA zone names, severely limited usefulness

**Decision:** `Intl.DateTimeFormat` with `timeZone` option
**Rationale:**
- Zero bundle size impact — timezone data is provided by the runtime's ICU dataset
- Always accurate and up-to-date without library releases
- Node 16+ and all modern browsers support `Intl.DateTimeFormat` with `timeZone`
- For `listTimezones()`, use `Intl.supportedValuesOf('timeZone')` where available, with a graceful degradation path for Node 16-17 (return an empty array with a console warning)
- Aligns with the library's "zero dependencies" and "< 5 KB gzipped" goals

### Decision 3: Error Handling — Exceptions vs Result Type

**Context:** Need a consistent strategy for handling invalid inputs across all modules (unparseable dates, invalid timezones, out-of-range values).

**Options Considered:**
1. **Typed exceptions** — Throw specific error subclasses (`DateParseError`, `DateRangeError`)
   - Pros: Familiar JS/TS pattern, integrates with existing try/catch flows, stack traces, `instanceof` checks, no wrapper overhead
   - Cons: Exceptions are not type-checked by the compiler, caller can forget to catch
2. **Result type** — Return `{ ok: true, value: T } | { ok: false, error: E }` discriminated union
   - Pros: Compiler enforces error handling, no exceptions, functional style
   - Cons: Unfamiliar to most JS developers, verbose call sites, doesn't integrate with existing try/catch, adds wrapper allocation overhead
3. **Return `null` on failure** — Return `null` instead of throwing
   - Pros: Simple, no exceptions
   - Cons: Loses error context (why did it fail?), null checks everywhere, can't distinguish between "not found" and "invalid input"

**Decision:** Typed exceptions with safe variants
**Rationale:**
- Follows JavaScript ecosystem conventions — developers expect functions to throw on invalid input
- Custom error classes (`DateParseError`, `DateRangeError`) provide structured error information (original input, expected format, error code)
- For performance-sensitive paths where exceptions are undesirable, provide `*Safe` variants (e.g., `parseDateSafe`) that return `T | null`
- Error classes extend `Error` and set `name` properly for clean stack traces
- TypeScript's `@throws` JSDoc tag documents which errors each function may throw

## Module Design

### Module 1: parse

**Responsibility:** Convert string and numeric inputs into native `Date` objects with strict validation.

**Exports:**

| Export | Signature | Description |
|--------|-----------|-------------|
| `parseDate` | `(input: string, format?: string) => Date` | Parse a date string; throws `DateParseError` on failure |
| `parseDateSafe` | `(input: string, format?: string) => Date \| null` | Safe variant; returns `null` instead of throwing |
| `DateParseError` | `class extends Error` | Typed error with `input`, `expectedFormat`, and `code` properties |

**Internal Dependencies:** `errors.ts` (shared error base)

**Implementation Notes:**
- ISO 8601 parsing uses a strict regex to avoid `new Date(string)` browser inconsistencies
- Custom format parsing tokenizes the format string and matches positionally
- Locale format parsing recognizes month names in English; for other locales, consumers should use `Intl.DateTimeFormat` directly
- The `format` parameter uses tokens: `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`, `SSS`

### Module 2: format

**Responsibility:** Convert `Date` objects into human-readable string representations with locale support.

**Exports:**

| Export | Signature | Description |
|--------|-----------|-------------|
| `formatDate` | `(date: Date, pattern: string, locale?: string) => string` | Format a date using token pattern |
| `formatRelative` | `(date: Date, baseDate?: Date, locale?: string) => string` | Format as relative time ("2 hours ago") |

**Internal Dependencies:** None (uses `Intl.DateTimeFormat` and `Intl.RelativeTimeFormat` directly)

**Implementation Notes:**
- Token replacement supports: `YYYY`, `YY`, `MMMM`, `MMM`, `MM`, `M`, `DD`, `D`, `HH`, `H`, `hh`, `h`, `mm`, `m`, `ss`, `s`, `A`, `a`
- `formatRelative` picks the most appropriate unit (seconds, minutes, hours, days, months, years) based on the delta magnitude
- Locale-aware formatting delegates to `Intl.RelativeTimeFormat` for proper pluralization and grammar
- `Intl.DateTimeFormat` instances are cached per locale to avoid repeated construction overhead

### Module 3: validate

**Responsibility:** Validate date inputs and query calendar properties without side effects.

**Exports:**

| Export | Signature | Description |
|--------|-----------|-------------|
| `isValidDate` | `(input: string \| number \| Date) => boolean` | Check if the input represents a valid date |
| `isLeapYear` | `(year: number) => boolean` | Check if a year is a leap year |
| `daysInMonth` | `(year: number, month: number) => number` | Return the number of days in a given month (1-12) |

**Internal Dependencies:** None

**Implementation Notes:**
- `isValidDate` for strings attempts ISO 8601 parsing first, then falls back to a structured check
- Does not use `Date` object coercion tricks (e.g., checking `isNaN(new Date(input).getTime())`) because those accept many invalid inputs
- `isLeapYear` implements the full Gregorian rule: divisible by 4, not by 100, except by 400
- `daysInMonth` uses a lookup array with leap year adjustment for February

### Module 4: arithmetic

**Responsibility:** Perform date addition, subtraction, differencing, and boundary snapping.

**Exports:**

| Export | Signature | Description |
|--------|-----------|-------------|
| `addDays` | `(date: Date, days: number) => Date` | Add (or subtract) days |
| `addMonths` | `(date: Date, months: number) => Date` | Add (or subtract) months with day-of-month clamping |
| `addYears` | `(date: Date, years: number) => Date` | Add (or subtract) years |
| `diffInDays` | `(a: Date, b: Date) => number` | Signed difference in whole days |
| `diffInMonths` | `(a: Date, b: Date) => number` | Signed difference in whole months |
| `diffInYears` | `(a: Date, b: Date) => number` | Signed difference in whole years |
| `startOf` | `(date: Date, unit: DateUnit) => Date` | Snap to the start of the given unit |
| `endOf` | `(date: Date, unit: DateUnit) => Date` | Snap to the end of the given unit |

**Internal Dependencies:** `types.ts` (`DateUnit` type)

**Implementation Notes:**
- `addMonths` clamps the day-of-month to the target month's maximum (e.g., Jan 31 + 1 month = Feb 28/29, not March 2/3)
- `addDays` adjusts for DST by working with UTC milliseconds, then converting back
- `diffInDays` normalizes both dates to midnight UTC before computing `(a - b) / 86_400_000`
- `startOf` and `endOf` support `DateUnit` values: `'day'`, `'week'`, `'month'`, `'quarter'`, `'year'`
- Week boundaries assume Monday as the first day (ISO 8601); a future option could make this configurable

### Module 5: timezone

**Responsibility:** Convert dates between IANA timezones and query timezone metadata.

**Exports:**

| Export | Signature | Description |
|--------|-----------|-------------|
| `toTimezone` | `(date: Date, tz: string) => Date` | Convert a date to the equivalent local time in the target timezone |
| `getTimezoneOffset` | `(date: Date, tz: string) => number` | Get the UTC offset in minutes for a timezone at a given instant |
| `listTimezones` | `() => string[]` | List all IANA timezone identifiers supported by the runtime |

**Internal Dependencies:** None

**Implementation Notes:**
- `toTimezone` constructs an `Intl.DateTimeFormat` with the target `timeZone`, extracts the parts, and reconstructs a `Date`
- `getTimezoneOffset` computes the offset by comparing the UTC representation to the localized representation
- `listTimezones` uses `Intl.supportedValuesOf('timeZone')` (Node 18+ / modern browsers) with a try/catch fallback that returns an empty array and logs a warning for Node 16-17
- `Intl.DateTimeFormat` instances are cached per timezone string to avoid re-creation overhead

## Public API Surface

The barrel export (`src/index.ts`) re-exports all public functions and types:

```typescript
// ── Parse ──────────────────────────────────────────────
export { parseDate, parseDateSafe, DateParseError } from './parse';

// ── Format ─────────────────────────────────────────────
export { formatDate, formatRelative } from './format';

// ── Validate ───────────────────────────────────────────
export { isValidDate, isLeapYear, daysInMonth } from './validate';

// ── Arithmetic ─────────────────────────────────────────
export {
  addDays,
  addMonths,
  addYears,
  diffInDays,
  diffInMonths,
  diffInYears,
  startOf,
  endOf,
} from './arithmetic';

// ── Timezone ───────────────────────────────────────────
export { toTimezone, getTimezoneOffset, listTimezones } from './timezone';

// ── Types ──────────────────────────────────────────────
export type { DateUnit, FormatToken, TimezoneString } from './types';

// ── Errors ─────────────────────────────────────────────
export { DateParseError, DateRangeError } from './errors';
```

### Complete Function Signatures

```typescript
/**
 * Parse a date string into a native Date object.
 *
 * @param input - The date string to parse
 * @param format - Optional format string using tokens (YYYY, MM, DD, HH, mm, ss)
 * @returns A Date object representing the parsed instant
 * @throws {DateParseError} If the input cannot be parsed
 *
 * @example
 * parseDate('2024-03-15')                     // ISO 8601
 * parseDate('15/03/2024', 'DD/MM/YYYY')       // Custom format
 */
export function parseDate(input: string, format?: string): Date;

/**
 * Parse a date string, returning null instead of throwing on failure.
 *
 * @param input - The date string to parse
 * @param format - Optional format string
 * @returns A Date object, or null if parsing fails
 *
 * @example
 * parseDateSafe('not-a-date')                 // null
 */
export function parseDateSafe(input: string, format?: string): Date | null;

/**
 * Format a Date object into a string using a token-based pattern.
 *
 * @param date - The Date to format
 * @param pattern - Format pattern (e.g., 'YYYY-MM-DD', 'MMMM D, YYYY')
 * @param locale - Optional BCP 47 locale tag (default: 'en-US')
 * @returns The formatted date string
 * @throws {TypeError} If date is not a valid Date object
 *
 * @example
 * formatDate(new Date('2024-03-15'), 'MMMM D, YYYY')  // "March 15, 2024"
 */
export function formatDate(date: Date, pattern: string, locale?: string): string;

/**
 * Format a Date as a human-readable relative time string.
 *
 * @param date - The Date to describe relative to the base
 * @param baseDate - The reference point (default: now)
 * @param locale - Optional BCP 47 locale tag (default: 'en-US')
 * @returns A relative time string (e.g., "2 hours ago", "in 3 days")
 * @throws {TypeError} If date is not a valid Date object
 *
 * @example
 * formatRelative(pastDate)                   // "2 hours ago"
 * formatRelative(futureDate, now, 'es')      // "dentro de 3 días"
 */
export function formatRelative(date: Date, baseDate?: Date, locale?: string): string;

/**
 * Check if the given input represents a valid date.
 *
 * @param input - A date string, timestamp number, or Date object
 * @returns true if the input is a valid date, false otherwise
 *
 * @example
 * isValidDate('2024-02-29')                  // true (leap year)
 * isValidDate('2024-02-30')                  // false
 */
export function isValidDate(input: string | number | Date): boolean;

/**
 * Check if a year is a leap year under the Gregorian calendar.
 *
 * @param year - The four-digit year
 * @returns true if the year is a leap year
 *
 * @example
 * isLeapYear(2024)                           // true
 * isLeapYear(1900)                           // false
 */
export function isLeapYear(year: number): boolean;

/**
 * Return the number of days in a given month.
 *
 * @param year - The four-digit year
 * @param month - The month number (1-12)
 * @returns The number of days in that month
 *
 * @example
 * daysInMonth(2024, 2)                       // 29
 */
export function daysInMonth(year: number, month: number): number;

/**
 * Add (or subtract) a number of days to a date.
 *
 * @param date - The starting Date
 * @param days - Number of days to add (negative to subtract)
 * @returns A new Date with the days applied
 *
 * @example
 * addDays(new Date('2024-03-15'), 7)         // 2024-03-22
 */
export function addDays(date: Date, days: number): Date;

/**
 * Add (or subtract) a number of months to a date.
 * Day-of-month is clamped to the target month's maximum.
 *
 * @param date - The starting Date
 * @param months - Number of months to add (negative to subtract)
 * @returns A new Date with the months applied
 *
 * @example
 * addMonths(new Date('2024-01-31'), 1)       // 2024-02-29 (clamped)
 */
export function addMonths(date: Date, months: number): Date;

/**
 * Add (or subtract) a number of years to a date.
 *
 * @param date - The starting Date
 * @param years - Number of years to add (negative to subtract)
 * @returns A new Date with the years applied
 *
 * @example
 * addYears(new Date('2024-02-29'), 1)        // 2025-02-28 (clamped)
 */
export function addYears(date: Date, years: number): Date;

/**
 * Compute the signed difference in whole days between two dates.
 *
 * @param a - The first Date
 * @param b - The second Date
 * @returns The number of whole days (a - b), positive if a is later
 *
 * @example
 * diffInDays(new Date('2024-03-15'), new Date('2024-03-10'))  // 5
 */
export function diffInDays(a: Date, b: Date): number;

/**
 * Compute the signed difference in whole months between two dates.
 *
 * @param a - The first Date
 * @param b - The second Date
 * @returns The number of whole months (a - b)
 */
export function diffInMonths(a: Date, b: Date): number;

/**
 * Compute the signed difference in whole years between two dates.
 *
 * @param a - The first Date
 * @param b - The second Date
 * @returns The number of whole years (a - b)
 */
export function diffInYears(a: Date, b: Date): number;

/**
 * Snap a date to the start of the given unit.
 *
 * @param date - The Date to snap
 * @param unit - The unit to snap to ('day', 'week', 'month', 'quarter', 'year')
 * @returns A new Date at the start of the unit
 *
 * @example
 * startOf(new Date('2024-03-15T14:30:00'), 'month')  // 2024-03-01T00:00:00
 */
export function startOf(date: Date, unit: DateUnit): Date;

/**
 * Snap a date to the end of the given unit.
 *
 * @param date - The Date to snap
 * @param unit - The unit to snap to ('day', 'week', 'month', 'quarter', 'year')
 * @returns A new Date at the last millisecond of the unit
 *
 * @example
 * endOf(new Date('2024-03-15T14:30:00'), 'year')     // 2024-12-31T23:59:59.999
 */
export function endOf(date: Date, unit: DateUnit): Date;

/**
 * Convert a date to the equivalent local time in the target timezone.
 *
 * @param date - The Date to convert
 * @param tz - An IANA timezone identifier (e.g., 'America/New_York')
 * @returns A new Date adjusted to the target timezone
 * @throws {RangeError} If the timezone identifier is invalid
 *
 * @example
 * toTimezone(new Date('2024-03-15T12:00:00Z'), 'America/New_York')
 * // Date representing 2024-03-15T08:00:00 in ET
 */
export function toTimezone(date: Date, tz: string): Date;

/**
 * Get the UTC offset in minutes for a timezone at a given instant.
 *
 * @param date - The instant to check
 * @param tz - An IANA timezone identifier
 * @returns The offset from UTC in minutes (e.g., -300 for EST)
 *
 * @example
 * getTimezoneOffset(new Date('2024-03-15'), 'America/New_York')  // -240 (EDT)
 */
export function getTimezoneOffset(date: Date, tz: string): number;

/**
 * List all IANA timezone identifiers supported by the runtime.
 *
 * @returns An array of timezone strings (e.g., ['Africa/Abidjan', ...])
 */
export function listTimezones(): string[];
```

### Exported Types

```typescript
/**
 * Date unit for startOf/endOf and diff operations.
 */
export type DateUnit = 'day' | 'week' | 'month' | 'quarter' | 'year';

/**
 * Format tokens recognized by formatDate.
 */
export type FormatToken =
  | 'YYYY' | 'YY'
  | 'MMMM' | 'MMM' | 'MM' | 'M'
  | 'DD' | 'D'
  | 'HH' | 'H' | 'hh' | 'h'
  | 'mm' | 'm'
  | 'ss' | 's'
  | 'SSS'
  | 'A' | 'a';

/**
 * A branded string type representing a valid IANA timezone identifier.
 * Used for documentation; runtime validation is performed by Intl.DateTimeFormat.
 */
export type TimezoneString = string & { readonly __brand: 'TimezoneString' };
```

## Usage Examples

### Example 1: Parsing and Formatting

```typescript
import { parseDate, formatDate } from '@acme/date-utils';

// Parse an ISO date and reformat it
const date = parseDate('2024-03-15T10:30:00Z');
console.log(formatDate(date, 'MMMM D, YYYY'));       // "March 15, 2024"
console.log(formatDate(date, 'MM/DD/YYYY'));          // "03/15/2024"
console.log(formatDate(date, 'dddd, MMMM D'));        // "Friday, March 15"

// Parse a custom format
const invoiceDate = parseDate('15-03-2024', 'DD-MM-YYYY');
console.log(formatDate(invoiceDate, 'YYYY/MM/DD'));   // "2024/03/15"

// Locale-aware formatting
console.log(formatDate(date, 'MMMM D, YYYY', 'de')); // "März 15, 2024"
console.log(formatDate(date, 'MMMM D, YYYY', 'ja')); // "3月 15, 2024"
```

### Example 2: Date Arithmetic

```typescript
import { addDays, addMonths, diffInDays, startOf, endOf } from '@acme/date-utils';

const today = new Date('2024-03-15');

// Add and subtract
const nextWeek = addDays(today, 7);                   // 2024-03-22
const lastMonth = addMonths(today, -1);               // 2024-02-15

// Month-end clamping
const jan31 = new Date('2024-01-31');
const feb = addMonths(jan31, 1);                      // 2024-02-29 (leap year, clamped)

// Differences
const daysBetween = diffInDays(nextWeek, today);      // 7

// Boundaries
const monthStart = startOf(today, 'month');           // 2024-03-01T00:00:00
const yearEnd = endOf(today, 'year');                 // 2024-12-31T23:59:59.999

// Calculate billing period
const billingStart = startOf(today, 'month');
const billingEnd = endOf(today, 'month');
const billingDays = diffInDays(billingEnd, billingStart) + 1;  // 31
```

### Example 3: Relative Time

```typescript
import { formatRelative } from '@acme/date-utils';

const now = new Date('2024-03-15T12:00:00Z');
const twoHoursAgo = new Date('2024-03-15T10:00:00Z');
const threeDaysLater = new Date('2024-03-18T12:00:00Z');
const lastYear = new Date('2023-03-15T12:00:00Z');

console.log(formatRelative(twoHoursAgo, now));        // "2 hours ago"
console.log(formatRelative(threeDaysLater, now));      // "in 3 days"
console.log(formatRelative(lastYear, now));            // "1 year ago"

// Localized relative time
console.log(formatRelative(twoHoursAgo, now, 'es'));   // "hace 2 horas"
console.log(formatRelative(threeDaysLater, now, 'ja'));// "3日後"
console.log(formatRelative(twoHoursAgo, now, 'fr'));   // "il y a 2 heures"
```

### Example 4: Tree-Shaking via Subpath Imports

```typescript
// ❌ Full import — pulls in everything (but still tree-shakeable at function level)
import { parseDate, formatDate } from '@acme/date-utils';

// ✅ Subpath import — only the parse module is bundled
import { parseDate } from '@acme/date-utils/parse';
import { formatDate } from '@acme/date-utils/format';

// ✅ Subpath import for timezone only (when you don't need parse/format/etc.)
import { toTimezone } from '@acme/date-utils/timezone';

// The package.json exports field makes this possible:
// {
//   "exports": {
//     ".":          { "import": "./dist/index.mjs", "require": "./dist/index.cjs", "types": "./dist/index.d.ts" },
//     "./parse":    { "import": "./dist/parse/index.mjs", "require": "./dist/parse/index.cjs", "types": "./dist/parse/index.d.ts" },
//     "./format":   { "import": "./dist/format/index.mjs", "require": "./dist/format/index.cjs", "types": "./dist/format/index.d.ts" },
//     "./validate": { "import": "./dist/validate/index.mjs", "require": "./dist/validate/index.cjs", "types": "./dist/validate/index.d.ts" },
//     "./arithmetic": { "import": "./dist/arithmetic/index.mjs", "require": "./dist/arithmetic/index.cjs", "types": "./dist/arithmetic/index.d.ts" },
//     "./timezone": { "import": "./dist/timezone/index.mjs", "require": "./dist/timezone/index.cjs", "types": "./dist/timezone/index.d.ts" }
//   }
// }
```

## Security Considerations

### Input Validation
- All string inputs to `parseDate` are validated against expected patterns before constructing a `Date`; no reliance on `new Date(unsanitizedString)` which can produce surprising results
- Numeric inputs to arithmetic functions are validated as finite numbers (`Number.isFinite`); `NaN`, `Infinity`, and `-Infinity` throw `TypeError`
- Timezone strings passed to `toTimezone` are validated by attempting to construct an `Intl.DateTimeFormat` — invalid zones produce a `RangeError` from the engine, which is allowed to propagate

### Prototype Pollution Prevention
- No use of `Object.assign` or spread on user-supplied objects
- No dynamic property access on user-controlled keys
- All internal data structures use `Object.create(null)` or `Map` for lookup caches

### Code Execution Safety
- No use of `eval`, `new Function`, or `setTimeout` with string arguments
- No dynamic `import()` of user-supplied module paths
- Format pattern tokens are matched via a whitelist; unrecognized tokens are passed through as literal text, never interpreted as code

### Supply Chain
- Zero runtime dependencies eliminates transitive supply chain risk
- Lock dev dependencies with exact versions in `package-lock.json`
- Enable npm provenance on publish for SLSA verification

## Performance Considerations

### Intl Object Caching
- `Intl.DateTimeFormat` and `Intl.RelativeTimeFormat` instances are expensive to construct (~0.5ms each)
- The library maintains internal `Map` caches keyed by `locale + timezone + options` hash
- Cache entries are never evicted (bounded by the finite number of locale/timezone combinations a single app uses)
- Benchmarks show a 10-50x speedup on repeated formatting calls after the initial construction

### Regex Compilation
- All regular expressions used for ISO 8601 parsing and token matching are compiled once at module load time as module-level constants
- No regex is constructed dynamically from user input

### Date Object Allocation
- Pure-function design means every operation allocates a new `Date` object
- For hot loops, consumers can use raw timestamp arithmetic and call `new Date(ms)` once at the end
- Benchmark guidance is provided in the README for performance-critical scenarios

### Bundle Size Budget
- Target: < 5 KB gzipped for the full library
- Each module target: < 1.5 KB gzipped
- CI pipeline includes a `size-limit` check that fails the build if the budget is exceeded
- Tree-shaking analysis is run on every PR to verify dead-code elimination works correctly

## Testing Strategy

### Unit Tests (Vitest)
- Every exported function has dedicated unit tests covering:
  - Happy path with typical inputs
  - Edge cases (midnight, year boundaries, DST transitions, month-end clamping, leap years)
  - Invalid inputs (malformed strings, NaN, null, undefined)
  - Error types and messages
- Target: 100% line and branch coverage on `src/` directory

### Property-Based Tests (fast-check)
- `parseDate(formatDate(date, 'YYYY-MM-DDTHH:mm:ss'), 'YYYY-MM-DDTHH:mm:ss')` round-trips correctly for arbitrary dates
- `addDays(date, n)` then `addDays(result, -n)` returns the original date (modulo DST edge cases)
- `diffInDays(addDays(date, n), date) === n` for all `n`
- `isLeapYear(year) === (daysInMonth(year, 2) === 29)` for all years
- `startOf(date, unit) <= date <= endOf(date, unit)` for all dates and units

### Browser Compatibility Tests (Playwright)
- Run the full test suite in Chromium, Firefox, and WebKit via Playwright
- Verify `Intl.DateTimeFormat` timezone support works consistently across engines
- Test that `listTimezones()` returns a non-empty array in all browsers
- Run in CI as a separate workflow step

### Bundle Size Verification (size-limit)
- `size-limit` configured in `package.json` with per-module and total budgets
- Runs on every PR; blocks merge if budget is exceeded
- Reports size delta in PR comments via `size-limit/action` GitHub Action

### CI Matrix
- Node.js: 16, 18, 20, latest
- OS: Ubuntu (primary), macOS (secondary for Intl consistency check)
- Browser: Chromium, Firefox, WebKit (via Playwright)

## Release Plan

### Versioning
- Follows semantic versioning (semver) strictly
- MAJOR: Breaking API changes (function signatures, error types, removed exports)
- MINOR: New functions, new format tokens, new `DateUnit` values
- PATCH: Bug fixes, performance improvements, documentation corrections

### Changelog Generation
- Conventional commits enforced via `commitlint` and Husky pre-commit hook
- Changelog auto-generated by `conventional-changelog-cli` on each release
- Commit types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `chore`, `BREAKING CHANGE`

### Publish Pipeline (GitHub Actions)
1. Developer pushes a tag matching `v*` (e.g., `v1.0.0`)
2. GitHub Actions workflow triggers:
   a. Install dependencies
   b. Lint and type-check
   c. Run full test suite (unit, property-based, browser)
   d. Build with tsup
   e. Verify bundle size within budget
   f. Publish to npm with `--provenance` flag
   g. Create GitHub Release with auto-generated notes
3. npm provenance enabled for SLSA supply-chain verification

### Release Phases

**Phase 1: Pre-release (v0.1.0-beta.1)**
- Core modules implemented (parse, format, validate, arithmetic, timezone)
- Full test suite passing
- Internal team adoption for feedback
- Published as `@acme/date-utils@0.1.0-beta.1` with `--tag beta`
- Breaking changes allowed without migration guides

**Phase 2: Release Candidate (v0.1.0-rc.1)**
- Feedback from beta incorporated
- API surface frozen
- Documentation complete (README, API reference, CONTRIBUTING.md)
- Published as `@acme/date-utils@0.1.0-rc.1` with `--tag next`
- Breaking changes require team sign-off

**Phase 3: Stable Release (v1.0.0)**
- All acceptance criteria met
- Bundle size verified (< 5 KB gzipped)
- 100% test coverage on public API
- Published as `@acme/date-utils@1.0.0` with `--tag latest`
- Breaking changes follow full semver with migration guides

### Migration Guides
- Every MAJOR version release includes a migration guide in `MIGRATION.md`
- Guide includes: breaking changes list, before/after code examples, automated codemods where feasible
- Migration guide is linked from the GitHub Release notes and the README

## Risks & Mitigations

### Risk 1: Intl API Inconsistencies Across Engines
**Impact:** Different timezone offsets or formatted strings between Node.js, Chrome, Firefox, and Safari
**Likelihood:** Medium
**Mitigation:**
- Run browser compatibility tests in CI with Playwright across Chromium, Firefox, and WebKit
- Document known cross-engine differences in the README
- For critical formatting, provide an `exact` mode that uses manual formatting instead of `Intl`
- Pin test assertions to UTC where possible to reduce engine-specific variance

### Risk 2: DST Edge Cases
**Impact:** Incorrect date arithmetic during spring-forward (gap) and fall-back (overlap) transitions
**Likelihood:** Medium
**Mitigation:**
- Property-based tests with `fast-check` generate dates specifically around DST transition boundaries
- `addDays` operates on UTC milliseconds to avoid local-time ambiguity
- Document DST behavior explicitly in the API reference for each affected function
- Include a dedicated DST test suite with transitions from multiple timezones (US, EU, Australia)

### Risk 3: Bundle Size Creep
**Impact:** Library exceeds the 5 KB gzipped budget, reducing its competitive advantage over date-fns/dayjs
**Likelihood:** Low-Medium
**Mitigation:**
- `size-limit` CI check blocks PRs that increase size beyond budget
- PR review checklist includes "Did you check bundle impact?"
- Prefer code patterns that compress well (consistent naming, avoid deep nesting)
- Regularly run `npx esbuild --bundle --minify --analyze` to identify size hotspots

### Risk 4: Intl.supportedValuesOf Availability
**Impact:** `listTimezones()` returns empty array on Node 16-17
**Likelihood:** Low (Node 16 is EOL September 2023; most consumers are on 18+)
**Mitigation:**
- Implement try/catch fallback with a console warning
- Document the limitation in the API reference
- Consider dropping Node 16 support in v2.0.0

### Risk 5: Custom Format Parsing Ambiguity
**Impact:** A format string like `'M/D/YYYY'` may match incorrectly for inputs like `'1/2/2024'` (is it Jan 2 or Feb 1?)
**Likelihood:** Medium
**Mitigation:**
- Document that single-digit tokens (`M`, `D`) match greedily
- Recommend zero-padded tokens (`MM`, `DD`) for unambiguous parsing
- `parseDateSafe` allows consumers to handle ambiguity without exceptions
- Consider adding a `strict` option in a future minor release
