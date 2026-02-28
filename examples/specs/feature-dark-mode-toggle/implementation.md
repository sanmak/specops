# Implementation Notes: Dark Mode Toggle

## Decisions Made During Implementation
| Decision | Rationale | Task |
|----------|-----------|------|
| Used CSS `color-mix()` for opacity variations (e.g., hover states) instead of separate tokens | Reduces the number of CSS variables from ~25 to 15 while keeping derived colors consistent | Task 1 |
| Chose `lucide-react` for Sun/Moon/Monitor icons | Already a project dependency; tree-shakeable, so only 3 icons are bundled (~1.2KB) | Task 5 |
| Added `aria-live="polite"` visually-hidden region for theme announcements | Native `aria-label` changes on the button are not reliably announced by all screen readers on click | Task 5 |

## Deviations from Design
| Planned | Actual | Reason |
|---------|--------|--------|
| Two toggle states (light / dark) | Three toggle states (light / dark / system) | User feedback during review — "system" option lets users defer to OS preference without losing the ability to override |
| CSS `opacity` overlay on images in dark mode | CSS `filter: brightness(0.85)` on images in dark mode | Overlay approach required wrapping every `<img>` in a container; `filter` is a one-line CSS addition with equivalent visual result |

## Blockers Encountered
| Blocker | Resolution | Impact |
|---------|------------|--------|
| Third-party date picker (`react-datepicker`) did not respect CSS variables — rendered with hardcoded white background in dark mode | Wrote a scoped CSS override in `third-party-theme-overrides.css` targeting `.react-datepicker` class; opened upstream issue #4127 | Task 7 delayed by 1.5 hours |
| Initial FOUC on Safari 14 — ThemeScript inline `<script>` was deferred by the browser | Moved ThemeScript to a synchronous inline `<script>` placed before any `<link rel="stylesheet">` tags in `index.html` | Task 2 delayed by 1 hour; required Task 12 CSP documentation update |

## Notes
- All 12 tasks completed; test coverage for theme-related code at 87%
- Visual regression tests caught 2 contrast issues (muted text on dark bg, subtle border invisible in dark mode) — both fixed before merge
- ThemeScript CSP `sha256` hash documented in `docs/THEMING.md` for the infrastructure team
- Feature flag `ENABLE_DARK_MODE` deployed to 10% of production traffic; monitoring for 48 hours before expanding
