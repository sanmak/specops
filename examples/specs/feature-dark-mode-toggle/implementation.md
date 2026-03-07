# Implementation Journal: Dark Mode Toggle

## Summary
All 12 tasks completed. 3 implementation decisions made (CSS color-mix, lucide-react icons, aria-live region). 2 deviations from design (three-state toggle, CSS filter for images). 2 blockers resolved (react-datepicker theming, Safari FOUC). Test coverage for theme-related code at 87%.

## Decision Log
| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used CSS `color-mix()` for opacity variations (e.g., hover states) instead of separate tokens | Reduces the number of CSS variables from ~25 to 15 while keeping derived colors consistent | Task 1 | 2025-03-01 |
| 2 | Chose `lucide-react` for Sun/Moon/Monitor icons | Already a project dependency; tree-shakeable, so only 3 icons are bundled (~1.2KB) | Task 5 | 2025-03-03 |
| 3 | Added `aria-live="polite"` visually-hidden region for theme announcements | Native `aria-label` changes on the button are not reliably announced by all screen readers on click | Task 5 | 2025-03-03 |

## Deviations from Design
| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| Two toggle states (light / dark) | Three toggle states (light / dark / system) | User feedback during review — "system" option lets users defer to OS preference without losing the ability to override | Task 5 |
| CSS `opacity` overlay on images in dark mode | CSS `filter: brightness(0.85)` on images in dark mode | Overlay approach required wrapping every `<img>` in a container; `filter` is a one-line CSS addition with equivalent visual result | Task 7 |

## Blockers Encountered
| Blocker | Resolution | Impact | Task |
|---------|------------|--------|------|
| Third-party date picker (`react-datepicker`) did not respect CSS variables — rendered with hardcoded white background in dark mode | Wrote a scoped CSS override in `third-party-theme-overrides.css` targeting `.react-datepicker` class; opened upstream issue #4127 | Task 7 delayed by 1.5 hours | Task 7 |
| Initial FOUC on Safari 14 — ThemeScript inline `<script>` was deferred by the browser | Moved ThemeScript to a synchronous inline `<script>` placed before any `<link rel="stylesheet">` tags in `index.html` | Task 2 delayed by 1 hour; required Task 12 CSP documentation update | Task 2 |

## Session Log
- **2025-03-01**: Started implementation. Completed Tasks 1-4.
- **2025-03-03**: Resumed at Task 5. Completed Tasks 5-8. Blockers hit on Tasks 2 and 7.
- **2025-03-05**: Resumed at Task 9. Completed Tasks 9-12. All tasks done.
