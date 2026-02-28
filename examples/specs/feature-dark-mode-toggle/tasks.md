# Implementation Tasks: Dark Mode Toggle

## Task Breakdown

### Task 1: Define CSS Custom Properties and Theme Tokens
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** None
**Priority:** High

**Description:**
Create the global CSS file that defines all design tokens as CSS custom properties, with separate value sets for light and dark themes. This is the foundation that all other tasks depend on.

**Implementation Steps:**
1. Create `src/styles/themes.css` file
2. Define the base custom property names on `:root` (15 tokens)
3. Define light theme values under `:root[data-theme="light"]`
4. Define dark theme values under `:root[data-theme="dark"]`
5. Add theme transition styles with `prefers-reduced-motion` guard
6. Import `themes.css` in the application entry point (`src/index.tsx` or `src/main.tsx`)
7. Verify both themes render correctly by manually toggling `data-theme` in DevTools

**Acceptance Criteria:**
- [ ] All 15 custom properties defined for both light and dark themes
- [ ] Light theme is visually consistent with current application styles
- [ ] Dark theme colors meet WCAG 2.1 AA contrast ratios (4.5:1 text, 3:1 large text)
- [ ] Transitions apply to background, color, border-color, and box-shadow
- [ ] `prefers-reduced-motion: reduce` disables all transitions
- [ ] File imports correctly and does not break existing styles

**Files to Modify:**
- `src/styles/themes.css` (new)
- `src/index.tsx` (add import)

**Tests Required:**
- [ ] Visual inspection of both themes via DevTools `data-theme` toggle
- [ ] Contrast ratio check with browser accessibility tools

---

### Task 2: Create ThemeScript for FOUC Prevention
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** None
**Priority:** High

**Description:**
Build an inline script component that runs synchronously in `<head>` to set the `data-theme` attribute before first paint, preventing any flash of unstyled content.

**Implementation Steps:**
1. Create `src/components/theme/ThemeScript.tsx`
2. Implement the component to render a `<script dangerouslySetInnerHTML>` block
3. Inline script logic: read localStorage → validate → resolve system preference → set `data-theme`
4. Handle missing localStorage gracefully (default to system preference)
5. Handle `matchMedia` absence gracefully (default to light)
6. Add the component to `public/index.html` or the root layout component's `<head>`
7. Test with DevTools network throttling to confirm no FOUC

**Acceptance Criteria:**
- [ ] `data-theme` is set before any stylesheet is parsed
- [ ] No FOUC when loading with dark theme saved in localStorage
- [ ] Falls back to system preference when localStorage is empty
- [ ] Falls back to `'light'` when `matchMedia` is unsupported
- [ ] Script handles localStorage access errors (e.g., private browsing)
- [ ] Inline script is under 500 bytes uncompressed

**Files to Modify:**
- `src/components/theme/ThemeScript.tsx` (new)
- `src/index.html` or root layout (add ThemeScript to `<head>`)

**Tests Required:**
- [ ] Unit test: rendered script content contains localStorage read
- [ ] Unit test: rendered script sets `data-theme` attribute
- [ ] Manual test: no FOUC in Chrome, Firefox, Safari, Edge

---

### Task 3: Implement ThemeContext and ThemeProvider
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 1
**Priority:** High

**Description:**
Create the React Context, reducer, and Provider component that manages theme state, syncs with localStorage and the `data-theme` DOM attribute, and listens for system preference changes.

**Implementation Steps:**
1. Create `src/components/theme/ThemeContext.ts` — define context and types
2. Create `src/components/theme/themeReducer.ts` — implement `SET_THEME` and `SYNC_SYSTEM` actions
3. Create `src/components/theme/ThemeProvider.tsx` — wire up reducer, localStorage, matchMedia, and DOM sync
4. On mount: read localStorage, query matchMedia, initialize state, verify `data-theme` attribute
5. Subscribe to `matchMedia('(prefers-color-scheme: dark)')` change events
6. On `SET_THEME` dispatch: update `data-theme` attribute and write to localStorage
7. On `SYNC_SYSTEM` dispatch: update `data-theme` only if current theme is `'system'`
8. Clean up matchMedia listener on unmount
9. Wrap the application root with `<ThemeProvider>`

**Acceptance Criteria:**
- [ ] ThemeProvider initializes with correct theme from localStorage
- [ ] ThemeProvider falls back to system preference when localStorage is empty
- [ ] `data-theme` attribute updates when theme state changes
- [ ] localStorage is written on every explicit theme change
- [ ] System preference changes are detected and applied when theme is `'system'`
- [ ] System preference changes are ignored when theme is `'light'` or `'dark'`
- [ ] matchMedia listener is cleaned up on unmount

**Files to Modify:**
- `src/components/theme/ThemeContext.ts` (new)
- `src/components/theme/themeReducer.ts` (new)
- `src/components/theme/ThemeProvider.tsx` (new)
- `src/App.tsx` (wrap with ThemeProvider)

**Tests Required:**
- [ ] Unit test: themeReducer handles SET_THEME for all theme values
- [ ] Unit test: themeReducer handles SYNC_SYSTEM when theme is 'system' and when it is not
- [ ] Component test: ThemeProvider renders children and provides context
- [ ] Component test: ThemeProvider reads initial theme from localStorage
- [ ] Component test: ThemeProvider responds to mocked matchMedia changes

---

### Task 4: Build useTheme Hook
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** Task 3
**Priority:** High

**Description:**
Create a custom hook that provides a clean API for consuming theme state and dispatching changes from any component.

**Implementation Steps:**
1. Create `src/hooks/useTheme.ts`
2. Call `useContext(ThemeContext)` — throw descriptive error if context is null
3. Derive `setTheme` callback (dispatches `SET_THEME`)
4. Derive `toggleTheme` callback (cycles light → dark → system → light)
5. Memoize callbacks with `useCallback`
6. Return `{ theme, resolvedTheme, systemTheme, setTheme, toggleTheme }`
7. Add JSDoc documentation for the hook and its return type

**Acceptance Criteria:**
- [ ] Hook returns all expected values: `theme`, `resolvedTheme`, `systemTheme`, `setTheme`, `toggleTheme`
- [ ] `setTheme('dark')` dispatches correct action and updates theme
- [ ] `toggleTheme()` cycles correctly: light → dark → system → light
- [ ] Hook throws a clear error when used outside ThemeProvider
- [ ] Callbacks are referentially stable across re-renders (memoized)

**Files to Modify:**
- `src/hooks/useTheme.ts` (new)
- `src/components/theme/index.ts` (re-export hook)

**Tests Required:**
- [ ] Unit test: toggleTheme cycles through all three states
- [ ] Unit test: setTheme dispatches correct action
- [ ] Unit test: hook throws error outside ThemeProvider
- [ ] Unit test: callbacks are memoized (referential equality)

---

### Task 5: Create ThemeToggle Component
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 4
**Priority:** High

**Description:**
Build the interactive toggle button with animated icons, accessible labeling, and keyboard support. Integrate it into the application header.

**Implementation Steps:**
1. Create `src/components/theme/ThemeToggle.tsx`
2. Create `src/components/theme/ThemeToggle.module.css`
3. Import Sun, Moon, and Monitor icons from `lucide-react`
4. Render the correct icon based on current `theme` value
5. Add CSS rotation/fade animation on icon change
6. Set dynamic `aria-label`: "Switch to dark mode" / "Switch to system preference" / "Switch to light mode"
7. Add `aria-live="polite"` region for screen reader announcements
8. Ensure 44x44px minimum touch target size
9. Handle keyboard events (Enter and Space trigger toggle)
10. Add the component to the application header (`src/components/layout/Header.tsx`)

**Acceptance Criteria:**
- [ ] Correct icon displayed for each theme state (Sun/Moon/Monitor)
- [ ] Click cycles through light → dark → system
- [ ] Icon animates smoothly on theme change
- [ ] `aria-label` is accurate for each state
- [ ] Screen reader announces theme change via `aria-live` region
- [ ] Button is keyboard-operable (Enter and Space)
- [ ] Button meets 44x44px minimum touch target
- [ ] Button is visually integrated into the header layout

**Files to Modify:**
- `src/components/theme/ThemeToggle.tsx` (new)
- `src/components/theme/ThemeToggle.module.css` (new)
- `src/components/layout/Header.tsx` (add ThemeToggle)

**Tests Required:**
- [ ] Component test: renders Sun icon in dark mode, Moon in light mode, Monitor in system mode
- [ ] Component test: click cycles through themes
- [ ] Component test: keyboard Enter triggers toggle
- [ ] Component test: keyboard Space triggers toggle
- [ ] Component test: aria-label updates per theme state
- [ ] Accessibility test: axe-core reports no violations

---

### Task 6: Update Global Styles to Use CSS Variables
**Status:** Pending
**Estimated Effort:** L (4-5 hours)
**Dependencies:** Task 1
**Priority:** Medium

**Description:**
Migrate all hardcoded color values in global stylesheets to use the CSS custom properties defined in Task 1. This includes base styles, resets, typography, and utility classes.

**Implementation Steps:**
1. Audit all files in `src/styles/` for hardcoded color values
2. Create a mapping of existing colors to the nearest CSS variable token
3. Replace each hardcoded value with the corresponding `var(--color-*)` reference
4. Update global reset/normalize styles to use variables
5. Update typography styles (headings, links, code blocks)
6. Update utility classes (backgrounds, borders, shadows)
7. Update scrollbar styles for dark mode (`scrollbar-color` property)
8. Verify visual consistency in light mode matches pre-migration appearance
9. Verify dark mode renders correctly with the new variables

**Acceptance Criteria:**
- [ ] No hardcoded color values remain in global stylesheets
- [ ] Light theme appearance is identical to the pre-migration design
- [ ] Dark theme renders with correct colors throughout
- [ ] Scrollbar adapts to theme where browser supports it
- [ ] No visual regressions in existing pages (verified by visual comparison)
- [ ] Code blocks and syntax highlighting adapt to theme

**Files to Modify:**
- `src/styles/global.css`
- `src/styles/reset.css`
- `src/styles/typography.css`
- `src/styles/utilities.css`

**Tests Required:**
- [ ] Visual comparison: light theme before and after migration (screenshot diff)
- [ ] Visual check: dark theme across all major pages
- [ ] Grep for hardcoded hex/rgb values in `src/styles/` (should find zero)

---

### Task 7: Update Component-Level Styles
**Status:** Pending
**Estimated Effort:** L (4-5 hours)
**Dependencies:** Task 6
**Priority:** Medium

**Description:**
Migrate all CSS Module files across application components to replace hardcoded color values with CSS custom properties.

**Implementation Steps:**
1. Run a codebase-wide search for hardcoded color values in `*.module.css` files
2. Prioritize high-visibility components (Header, Sidebar, Card, Button, Input, Modal)
3. Replace each hardcoded color with the appropriate `var(--color-*)` token
4. Handle component-specific colors that don't map to global tokens (create component-level variables if needed)
5. Update box-shadow values to use `var(--color-shadow)`
6. Update border values to use `var(--color-border)` or `var(--color-border-subtle)`
7. Test each migrated component in both themes
8. Fix any visual inconsistencies or contrast issues found during testing

**Acceptance Criteria:**
- [ ] All component CSS Modules use CSS variables for color values
- [ ] No hardcoded color values remain in `*.module.css` files
- [ ] Each component renders correctly in both light and dark themes
- [ ] No contrast violations in either theme (spot-checked)
- [ ] Component hover, focus, and active states work in both themes
- [ ] No visual regressions in light theme (visual comparison with pre-migration)

**Files to Modify:**
- `src/components/**/*.module.css` (all component CSS Modules)

**Tests Required:**
- [ ] Visual comparison: key components in both themes
- [ ] Grep for hardcoded hex/rgb values in `*.module.css` (should find zero)
- [ ] Interactive state check: hover/focus/active in both themes

---

### Task 8: Handle Images and Media for Dark Mode
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 1
**Priority:** Medium

**Description:**
Ensure images, SVGs, logos, and other media assets adapt appropriately to the dark theme — reducing brightness, inverting decorative images, and using `currentColor` for inline SVGs.

**Implementation Steps:**
1. Audit all images and SVGs in the application
2. Update inline SVGs to use `currentColor` or CSS variable fills
3. Add CSS `filter: brightness(0.85)` for photographic images in dark mode
4. Create dark-mode variants for logos with light backgrounds (or add padding/rounded bg)
5. Use the `<picture>` element or CSS `content` for images that need entirely different assets
6. Add utility CSS class `.theme-invert` for decorative images that should fully invert
7. Test all media assets in both themes

**Acceptance Criteria:**
- [ ] Inline SVGs adapt to theme via `currentColor` or CSS variables
- [ ] Photographic images have reduced brightness in dark mode (not blindingly bright)
- [ ] Logos are legible in both themes (contrast with background)
- [ ] Decorative illustrations invert or adapt as needed
- [ ] No images appear broken or invisible in either theme
- [ ] `<picture>` or CSS-based image swapping works for critical assets

**Files to Modify:**
- `src/styles/themes.css` (add image utility classes)
- `src/components/**/*.tsx` (update SVG fills to `currentColor`)
- `src/assets/` (add dark-mode logo variants if needed)

**Tests Required:**
- [ ] Visual check: all pages with images in dark mode
- [ ] Verify SVGs adapt to theme changes dynamically
- [ ] Check logo legibility in both themes

---

### Task 9: Add System Preference Listener
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** Task 3
**Priority:** Medium

**Description:**
Ensure the `matchMedia` listener in ThemeProvider correctly tracks OS-level color scheme changes in real time and handles edge cases like initial query failure.

**Implementation Steps:**
1. Verify `matchMedia('(prefers-color-scheme: dark)')` subscription in ThemeProvider
2. Add fallback for environments where `matchMedia` is undefined (e.g., older browsers, SSR)
3. Test that `SYNC_SYSTEM` dispatch fires on OS theme change
4. Verify that the listener is properly removed on component unmount
5. Test rapid OS theme toggling (debounce if needed)
6. Verify behavior when `addListener` is used instead of `addEventListener` (Safari < 14)

**Acceptance Criteria:**
- [ ] OS dark mode toggle is detected and applied within 100ms
- [ ] Theme updates when user is on "system" mode and OS preference changes
- [ ] Theme does NOT change when user has an explicit "light" or "dark" choice
- [ ] Listener is cleaned up on ThemeProvider unmount (no memory leaks)
- [ ] Graceful fallback when `matchMedia` is unavailable
- [ ] Works in Safari 14+ (uses `addEventListener`, falls back to `addListener`)

**Files to Modify:**
- `src/components/theme/ThemeProvider.tsx` (refine listener logic)
- `src/utils/matchMediaPolyfill.ts` (new, if Safari fallback needed)

**Tests Required:**
- [ ] Unit test: mocked matchMedia fires change, state updates
- [ ] Unit test: listener removed on unmount
- [ ] Unit test: matchMedia unavailable — no crash, defaults to light
- [ ] Integration test: rapid OS changes handled without errors

---

### Task 10: Implement Accessibility Audit
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 5, Task 6, Task 7, Task 8
**Priority:** High

**Description:**
Perform a comprehensive accessibility audit of both themes, fix all issues, and add automated accessibility checks to the test suite.

**Implementation Steps:**
1. Install `@axe-core/react` for development-mode runtime checks
2. Run `axe-core` audit on all major pages in light theme — document violations
3. Run `axe-core` audit on all major pages in dark theme — document violations
4. Fix all contrast ratio failures (adjust CSS variable values as needed)
5. Verify all interactive elements have visible focus indicators in both themes
6. Test keyboard navigation through the entire application in both themes
7. Test with a screen reader (VoiceOver on macOS) — verify theme toggle announcements
8. Add automated `axe-core` checks to the component test suite
9. Create a CI job that runs accessibility tests against both themes

**Acceptance Criteria:**
- [ ] Zero axe-core violations in light theme
- [ ] Zero axe-core violations in dark theme
- [ ] All text meets 4.5:1 contrast ratio (normal text) and 3:1 (large text) in both themes
- [ ] Focus indicators visible in both themes
- [ ] Theme toggle operable by keyboard and announced by screen reader
- [ ] `aria-live` region announces theme changes
- [ ] Automated accessibility tests added to CI

**Files to Modify:**
- `src/styles/themes.css` (adjust colors for contrast if needed)
- `src/components/theme/ThemeToggle.tsx` (refine ARIA attributes if needed)
- `src/setupTests.ts` (add axe-core integration)
- `.github/workflows/ci.yml` or equivalent (add accessibility CI step)

**Tests Required:**
- [ ] Automated axe-core audit: both themes, all pages, zero violations
- [ ] Manual screen reader test: toggle announces theme change
- [ ] Manual keyboard test: full tab navigation in both themes

---

### Task 11: Write Tests
**Status:** Pending
**Estimated Effort:** M (3-4 hours)
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10
**Priority:** High

**Description:**
Write the full test suite covering unit, component, integration, visual regression, and accessibility tests for all theme-related code.

**Implementation Steps:**
1. Write unit tests for `themeReducer` (all actions, edge cases, unknown actions)
2. Write unit tests for `useTheme` hook (return values, setTheme, toggleTheme, error outside provider)
3. Write unit tests for ThemeScript (rendered output for each default value)
4. Write unit tests for localStorage read/write/validate helpers
5. Write component tests for ThemeProvider (initialization, state changes, matchMedia sync)
6. Write component tests for ThemeToggle (icons, cycling, keyboard, aria-label, aria-live)
7. Write integration tests for full toggle cycle (light → dark → system → light with DOM and localStorage verification)
8. Write integration test for persistence (set theme, remount, verify restoration)
9. Write integration test for invalid localStorage (garbage value, missing key)
10. Capture visual regression baselines for key pages in both themes
11. Add axe-core automated checks for both themes in component tests
12. Verify test coverage > 80% for all theme-related files

**Acceptance Criteria:**
- [ ] All unit tests pass
- [ ] All component tests pass
- [ ] All integration tests pass
- [ ] Visual regression baselines captured
- [ ] Accessibility tests pass (zero violations)
- [ ] Test coverage for theme-related code > 80%
- [ ] Tests run successfully in CI pipeline
- [ ] No flaky tests (run suite 3 times to confirm stability)

**Files to Modify:**
- `src/components/theme/__tests__/themeReducer.test.ts` (new)
- `src/components/theme/__tests__/ThemeProvider.test.tsx` (new)
- `src/components/theme/__tests__/ThemeToggle.test.tsx` (new)
- `src/components/theme/__tests__/ThemeScript.test.tsx` (new)
- `src/hooks/__tests__/useTheme.test.ts` (new)
- `tests/integration/theme.test.tsx` (new)
- `tests/visual/theme.visual.test.ts` (new)

**Tests Required:**
- [ ] 80%+ coverage for all files in `src/components/theme/` and `src/hooks/useTheme.ts`
- [ ] All critical paths tested (initial load, toggle, persist, system sync)
- [ ] Edge cases covered (invalid localStorage, missing matchMedia, unmount cleanup)

---

### Task 12: Documentation and Rollout
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** Task 11
**Priority:** Medium

**Description:**
Document the theming system for other developers, add the feature flag, update the PR template, and prepare for staged production rollout.

**Implementation Steps:**
1. Add JSDoc comments to all exported types, components, and hooks
2. Write a `THEMING.md` guide in `docs/` explaining how to use CSS variables in new components
3. Document the "Dark Mode Checklist" for adding new UI (use variables, check contrast, test both themes)
4. Add `ENABLE_DARK_MODE` feature flag to environment configuration
5. Wrap ThemeToggle render in a feature flag check
6. Update PR template with "Dark Mode Checklist" section
7. Document required CSP hash for ThemeScript inline script
8. Prepare rollout plan: 10% → 50% → 100% with monitoring checkpoints
9. Create rollback instructions (disable feature flag, revert if needed)
10. Update CHANGELOG with the new feature

**Acceptance Criteria:**
- [ ] All public APIs have JSDoc documentation
- [ ] Theming guide explains how to add theme-aware components
- [ ] Feature flag controls ThemeToggle visibility
- [ ] PR template includes dark mode checklist
- [ ] CSP requirements documented for infrastructure team
- [ ] Rollout plan reviewed with team
- [ ] Rollback steps documented and tested
- [ ] CHANGELOG updated

**Files to Modify:**
- `src/components/theme/*.tsx` (add JSDoc)
- `src/hooks/useTheme.ts` (add JSDoc)
- `docs/THEMING.md` (new)
- `src/config/featureFlags.ts` (add ENABLE_DARK_MODE)
- `.github/PULL_REQUEST_TEMPLATE.md` (add dark mode checklist)
- `CHANGELOG.md`

**Tests Required:**
- [ ] Feature flag hides ThemeToggle when disabled
- [ ] Feature flag shows ThemeToggle when enabled
- [ ] Documentation accuracy verified by peer review

---

## Implementation Order

### Days 1-2: Foundation
**Day 1:**
1. Task 1: Define CSS custom properties and theme tokens (foundation — all styling depends on this)
2. Task 2: Create ThemeScript for FOUC prevention (parallel with Task 1 — no dependencies)

**Day 2:**
3. Task 3: Implement ThemeContext and ThemeProvider (depends on Task 1)
4. Task 4: Build useTheme hook (depends on Task 3)
5. Task 5: Create ThemeToggle component (depends on Task 4)

### Days 3-4: Migration
**Day 3:**
6. Task 6: Update global styles to use CSS variables (depends on Task 1)
7. Task 8: Handle images and media for dark mode (depends on Task 1, parallel with Task 6)

**Day 4:**
8. Task 7: Update component-level styles (depends on Task 6)
9. Task 9: Add system preference listener (depends on Task 3, parallel with Task 7)

### Day 5: Quality & Ship
**Day 5:**
10. Task 10: Implement accessibility audit (depends on Tasks 5-8)
11. Task 11: Write tests (depends on all previous tasks)
12. Task 12: Documentation and rollout (depends on Task 11)

## Progress Tracking

**Total Tasks:** 12
**Completed:** 0
**In Progress:** 0
**Remaining:** 12

**Estimated Total Effort:** ~25-32 hours (~1 week for 1 developer)

### Status Legend
- **Pending**: Not started
- **In Progress**: Currently being worked on
- **Completed**: Done and tested
- **Blocked**: Waiting on dependencies or external factors

### Progress by Category
- **Foundation**: 0/2 (Tasks 1-2)
- **State Management**: 0/3 (Tasks 3-4, 9)
- **UI Component**: 0/1 (Task 5)
- **Style Migration**: 0/3 (Tasks 6-8)
- **Quality**: 0/2 (Tasks 10-11)
- **Documentation**: 0/1 (Task 12)

## Notes

- Tasks 1 and 2 are independent and can be done in parallel on Day 1
- Task 3 is the core state management piece — Tasks 4, 5, and 9 depend on it
- Tasks 6-8 (style migration) are the most time-consuming but are parallelizable with the state management track
- Task 10 (accessibility) should happen after visual components are complete but before final tests
- Task 11 (testing) should be done incrementally alongside implementation but the final comprehensive pass is listed here
- Task 12 (documentation) should be the last task before merging

## Risk Items

- **Style migration scope**: Hardcoded colors across many components may take longer than estimated (Tasks 6-7)
- **Third-party components**: External libraries may require CSS overrides for dark mode (Task 8)
- **Safari FOUC**: Safari may handle inline scripts differently — needs explicit cross-browser testing (Task 2)
- **Contrast issues**: Some existing color choices may not have sufficient contrast in the dark theme — budget time for adjustments (Task 10)
- **Visual regression noise**: Minor rendering differences between themes may cause false positives in visual regression tests (Task 11)
