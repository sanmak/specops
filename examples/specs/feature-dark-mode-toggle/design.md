# Design: Dark Mode Toggle

## Architecture Overview

The dark mode system is built on three pillars:

- **CSS Custom Properties**: A set of design tokens (colors, shadows, borders) defined as CSS variables on the `:root` element, swapped by toggling a `data-theme` attribute on `<html>`.
- **React Context + useReducer**: A `ThemeProvider` component that manages the current theme state, listens for system preference changes, and exposes a `useTheme` hook for consumers.
- **localStorage Persistence**: The user's explicit choice is written to `localStorage` so it survives page reloads and browser restarts. A synchronous inline script (`ThemeScript`) reads this value before React hydrates to prevent FOUC.

Data flow: `ThemeScript (blocking) → HTML data-theme set → CSS variables resolve → React hydrates → ThemeProvider syncs state → useTheme available`.

## Technical Decisions

### Decision 1: Theming Approach — CSS Custom Properties vs CSS-in-JS vs Tailwind
**Context:** Need a mechanism to swap all color values when the theme changes, compatible with existing CSS Modules.

**Options Considered:**
1. **CSS Custom Properties (Variables)** — Define tokens as `--color-*` on `:root`, swap values via `data-theme` attribute
   - Pros: Zero runtime cost, works with CSS Modules, native browser feature, single repaint on change
   - Cons: Requires migrating existing hardcoded colors, no TypeScript type safety for token names
2. **CSS-in-JS (styled-components / Emotion)** — Theme object passed via React context, consumed in template literals
   - Pros: TypeScript type safety, co-located styles, dynamic theming
   - Cons: Runtime overhead, requires rewriting CSS Modules, larger bundle, FOUC risk
3. **Tailwind CSS dark variant** — Use `dark:` prefix classes
   - Pros: Utility-first, easy toggling, popular ecosystem
   - Cons: Requires Tailwind adoption (not in project), large class lists, migration effort

**Decision:** CSS Custom Properties
**Rationale:**
- Zero runtime JavaScript for the actual style swap — the browser handles it natively
- Works seamlessly with the existing CSS Modules setup (modules reference variables)
- A single `data-theme` attribute change triggers one style recalculation (< 50ms budget)
- No new dependencies; CSS variables are supported in all target browsers

### Decision 2: State Management — React Context with useReducer vs Redux vs Zustand
**Context:** Need to share current theme across the component tree and react to system preference changes.

**Options Considered:**
1. **React Context + useReducer** — Built-in React primitives
   - Pros: No dependencies, simple API, sufficient for single-value global state
   - Cons: All consumers re-render on change (acceptable for infrequent theme changes)
2. **Redux (existing store)** — Add theme slice to Redux store
   - Pros: DevTools, middleware, consistent with app state
   - Cons: Overkill for one value, Redux boilerplate, tight coupling to store
3. **Zustand** — Lightweight state library
   - Pros: Small bundle, selector-based re-renders, simple API
   - Cons: New dependency for a single piece of state

**Decision:** React Context with useReducer
**Rationale:**
- Theme is a single, rarely-changing value — Context re-render cost is negligible
- No new dependencies added to the project
- `useReducer` provides predictable state transitions (SET_THEME, SYNC_SYSTEM)
- Aligns with React best practices for cross-cutting concerns (similar to locale, auth)

### Decision 3: Persistence — localStorage vs Cookie vs Server-Side
**Context:** Need to remember the user's theme preference across sessions.

**Options Considered:**
1. **localStorage** — Client-side key-value storage
   - Pros: Simple API, synchronous read (critical for FOUC prevention), 5MB limit
   - Cons: Not available server-side, cleared if user clears site data
2. **Cookie** — HTTP cookie with theme value
   - Pros: Sent to server (useful for SSR), persists across sessions
   - Cons: Sent on every request (overhead), size limit, requires server handling
3. **Server-side (user profile API)** — Store preference in database
   - Pros: Synced across devices, survives local storage clear
   - Cons: Requires authentication, network latency, FOUC risk on slow connections

**Decision:** localStorage
**Rationale:**
- Synchronous `localStorage.getItem()` in the blocking `ThemeScript` eliminates FOUC entirely
- No server dependency — works for unauthenticated users and offline scenarios
- Simple implementation: one key (`specops-theme`), three valid values (`light`, `dark`, `system`)
- Aligns with client-side-only architecture (no SSR in current project)

## Component Design

### Component 1: ThemeProvider
**Responsibility:** Wraps the application root, manages theme state via useReducer, listens for system preference changes, syncs to localStorage, and sets `data-theme` on `<html>`.

**Interface:**
```typescript
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

type Theme = 'light' | 'dark' | 'system';
type ResolvedTheme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;           // User's explicit choice (or "system")
  resolvedTheme: ResolvedTheme;  // Actual applied theme after system resolution
  systemTheme: ResolvedTheme;    // Current OS preference
}

type ThemeAction =
  | { type: 'SET_THEME'; payload: Theme }
  | { type: 'SYNC_SYSTEM'; payload: ResolvedTheme };

function ThemeProvider({ children, defaultTheme = 'system', storageKey = 'specops-theme' }: ThemeProviderProps): JSX.Element;
```

**Dependencies:**
- React (useReducer, useEffect, useCallback)
- ThemeContext (created internally)
- localStorage API
- `window.matchMedia('(prefers-color-scheme: dark)')`

**Behavior:**
1. On mount, reads `localStorage[storageKey]` — falls back to `defaultTheme` if missing or invalid
2. Queries `matchMedia` to determine current system preference
3. Resolves actual theme: if `theme === 'system'`, use `systemTheme`; otherwise use `theme`
4. Sets `document.documentElement.dataset.theme = resolvedTheme`
5. Subscribes to `matchMedia` `change` event — dispatches `SYNC_SYSTEM` when OS preference changes
6. On state change, writes `theme` to `localStorage` (not `resolvedTheme`)

### Component 2: ThemeToggle
**Responsibility:** Renders a button that cycles through theme options (light → dark → system) with animated icon and accessible labeling.

**Interface:**
```typescript
interface ThemeToggleProps {
  className?: string;
  size?: number;           // Icon size in px, default 20
  showLabel?: boolean;     // Show text label next to icon, default false
  cycleOrder?: Theme[];    // Custom cycle order, default ['light', 'dark', 'system']
}

function ThemeToggle({ className, size, showLabel, cycleOrder }: ThemeToggleProps): JSX.Element;
```

**Dependencies:**
- useTheme hook
- Sun / Moon / Monitor icons (from `lucide-react`)
- CSS Module for styling

**Behavior:**
1. Reads current `theme` from `useTheme()`
2. On click, advances to next theme in `cycleOrder`
3. Renders icon: Sun for light, Moon for dark, Monitor for system
4. Sets `aria-label` dynamically: "Switch to dark mode", "Switch to system preference", "Switch to light mode"
5. Animates icon rotation on theme change via CSS transition
6. Meets 44x44px minimum touch target

### Component 3: useTheme Hook
**Responsibility:** Provides convenient access to theme context values and actions.

**Interface:**
```typescript
interface UseThemeReturn {
  theme: Theme;                 // Current setting: 'light' | 'dark' | 'system'
  resolvedTheme: ResolvedTheme; // Actual visual theme: 'light' | 'dark'
  systemTheme: ResolvedTheme;   // OS preference: 'light' | 'dark'
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;      // Convenience: cycles light → dark → system
}

function useTheme(): UseThemeReturn;
```

**Dependencies:**
- ThemeContext (React.useContext)

**Behavior:**
1. Calls `useContext(ThemeContext)` — throws descriptive error if used outside `ThemeProvider`
2. Returns memoized `setTheme` and `toggleTheme` callbacks
3. `toggleTheme` cycles: light → dark → system → light
4. All values are derived from the reducer state — no local state

### Component 4: ThemeScript
**Responsibility:** Inline blocking script injected into `<head>` that sets the initial `data-theme` attribute before any CSS or React code executes, preventing FOUC.

**Interface:**
```typescript
interface ThemeScriptProps {
  storageKey?: string;      // localStorage key, default 'specops-theme'
  defaultTheme?: Theme;     // Fallback if no stored value, default 'system'
  attribute?: string;       // HTML attribute name, default 'data-theme'
}

function ThemeScript({ storageKey, defaultTheme, attribute }: ThemeScriptProps): JSX.Element;
```

**Dependencies:**
- None (renders a raw `<script>` tag with inline JavaScript — no React runtime needed)

**Behavior:**
1. Renders a `<script dangerouslySetInnerHTML>` block
2. The inline script runs synchronously before stylesheets parse:
   - Reads `localStorage.getItem(storageKey)`
   - Validates value is one of `'light'`, `'dark'`, `'system'`
   - If `'system'` or missing, checks `window.matchMedia('(prefers-color-scheme: dark)').matches`
   - Sets `document.documentElement.setAttribute(attribute, resolvedTheme)`
3. Because this runs before first paint, users never see the wrong theme

## Sequence Diagrams

### Flow 1: Initial Page Load
```
Browser -> HTML: Request page
HTML -> ThemeScript: Execute inline <script> (synchronous, blocking)
ThemeScript -> localStorage: getItem('specops-theme')
localStorage -> ThemeScript: 'dark' | 'light' | 'system' | null
Alt: stored === 'light' or stored === 'dark'
  ThemeScript -> HTML: setAttribute('data-theme', stored)
Else: stored === 'system' or null
  ThemeScript -> matchMedia: query('(prefers-color-scheme: dark)')
  matchMedia -> ThemeScript: { matches: true/false }
  ThemeScript -> HTML: setAttribute('data-theme', matches ? 'dark' : 'light')
End
HTML -> CSS: Parse stylesheets — :root[data-theme] variables resolve correctly
CSS -> Browser: First contentful paint (correct theme, no FOUC)
Browser -> React: Hydrate application
React -> ThemeProvider: Mount — reads localStorage, matchMedia, initializes reducer
ThemeProvider -> useTheme: Context available to all consumers
ThemeProvider -> HTML: Verify data-theme matches state (no-op if ThemeScript was correct)
```

### Flow 2: Manual Theme Toggle
```
User -> ThemeToggle: Click toggle button
ThemeToggle -> useTheme: toggleTheme()
useTheme -> ThemeProvider: dispatch({ type: 'SET_THEME', payload: 'dark' })
ThemeProvider -> Reducer: Compute new state { theme: 'dark', resolvedTheme: 'dark' }
ThemeProvider -> HTML: document.documentElement.dataset.theme = 'dark'
HTML -> CSS: :root[data-theme="dark"] variables activate
CSS -> Browser: Single style recalculation + repaint (~5-15ms)
Browser -> User: Dark theme visible with CSS transition (200ms ease)
ThemeProvider -> localStorage: setItem('specops-theme', 'dark')
ThemeToggle -> ThemeToggle: Icon animates from Sun to Moon
ThemeToggle -> ScreenReader: aria-live region announces "Dark mode enabled"
```

### Flow 3: System Preference Change
```
User -> OS: Change system appearance (e.g., macOS dark mode toggle)
OS -> Browser: prefers-color-scheme media query changes
Browser -> matchMedia: 'change' event fires { matches: true }
matchMedia -> ThemeProvider: Listener callback invoked
ThemeProvider -> Reducer: dispatch({ type: 'SYNC_SYSTEM', payload: 'dark' })
Reducer -> ThemeProvider: New state { systemTheme: 'dark' }
Alt: theme === 'system'
  ThemeProvider -> HTML: document.documentElement.dataset.theme = 'dark'
  HTML -> CSS: :root[data-theme="dark"] variables activate
  CSS -> Browser: Repaint with dark theme
  Browser -> User: Theme follows OS change
Else: theme === 'light' or theme === 'dark'
  ThemeProvider -> ThemeProvider: No visual change — user's manual choice preserved
  Note: systemTheme updated internally for when user switches back to 'system'
End
```

## State Management

> **Note:** This section replaces "Data Model Changes" per the frontend vertical adaptation — no database tables or server-side models are needed. All state is client-side.

### React Context Shape
```typescript
interface ThemeContextValue {
  state: ThemeState;
  dispatch: React.Dispatch<ThemeAction>;
}

interface ThemeState {
  theme: Theme;                 // 'light' | 'dark' | 'system'
  resolvedTheme: ResolvedTheme; // 'light' | 'dark'
  systemTheme: ResolvedTheme;   // 'light' | 'dark'
}

type ThemeAction =
  | { type: 'SET_THEME'; payload: Theme }
  | { type: 'SYNC_SYSTEM'; payload: ResolvedTheme };
```

### Reducer Logic
```typescript
function themeReducer(state: ThemeState, action: ThemeAction): ThemeState {
  switch (action.type) {
    case 'SET_THEME': {
      const theme = action.payload;
      const resolvedTheme = theme === 'system' ? state.systemTheme : theme;
      return { ...state, theme, resolvedTheme };
    }
    case 'SYNC_SYSTEM': {
      const systemTheme = action.payload;
      const resolvedTheme = state.theme === 'system' ? systemTheme : state.resolvedTheme;
      return { ...state, systemTheme, resolvedTheme };
    }
    default:
      return state;
  }
}
```

### localStorage Schema
```
Key:   'specops-theme'
Value: 'light' | 'dark' | 'system'
```
- Written on every `SET_THEME` dispatch
- Read once on `ThemeProvider` mount and once in `ThemeScript`
- Invalid or missing values treated as `'system'`

### CSS Custom Properties

All design tokens are defined as CSS custom properties on `:root` and scoped by `data-theme`.

```css
/* Base tokens (used by components via var(--color-*)) */
:root {
  --color-bg-primary: ;
  --color-bg-secondary: ;
  --color-bg-tertiary: ;
  --color-text-primary: ;
  --color-text-secondary: ;
  --color-text-muted: ;
  --color-primary: ;
  --color-primary-hover: ;
  --color-border: ;
  --color-border-subtle: ;
  --color-shadow: ;
  --color-overlay: ;
  --color-surface: ;
  --color-surface-hover: ;
  --color-focus-ring: ;
}
```

### Light Theme Definition
```css
:root[data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-bg-tertiary: #e9ecef;
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #495057;
  --color-text-muted: #868e96;
  --color-primary: #4263eb;
  --color-primary-hover: #3b5bdb;
  --color-border: #dee2e6;
  --color-border-subtle: #e9ecef;
  --color-shadow: rgba(0, 0, 0, 0.08);
  --color-overlay: rgba(0, 0, 0, 0.5);
  --color-surface: #ffffff;
  --color-surface-hover: #f1f3f5;
  --color-focus-ring: rgba(66, 99, 235, 0.4);
}
```

### Dark Theme Definition
```css
:root[data-theme="dark"] {
  --color-bg-primary: #0d1117;
  --color-bg-secondary: #161b22;
  --color-bg-tertiary: #21262d;
  --color-text-primary: #e6edf3;
  --color-text-secondary: #b1bac4;
  --color-text-muted: #768390;
  --color-primary: #58a6ff;
  --color-primary-hover: #79c0ff;
  --color-border: #30363d;
  --color-border-subtle: #21262d;
  --color-shadow: rgba(0, 0, 0, 0.3);
  --color-overlay: rgba(0, 0, 0, 0.7);
  --color-surface: #161b22;
  --color-surface-hover: #1c2129;
  --color-focus-ring: rgba(88, 166, 255, 0.4);
}
```

### Theme Transition Styles
```css
:root {
  --theme-transition-duration: 200ms;
  --theme-transition-easing: ease;
}

/* Applied to all themed elements for smooth switching */
*,
*::before,
*::after {
  transition:
    background-color var(--theme-transition-duration) var(--theme-transition-easing),
    color var(--theme-transition-duration) var(--theme-transition-easing),
    border-color var(--theme-transition-duration) var(--theme-transition-easing),
    box-shadow var(--theme-transition-duration) var(--theme-transition-easing);
}

/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition-duration: 0ms !important;
  }
}
```

## Security Considerations

### localStorage Validation
- Read values are validated against an allowlist (`['light', 'dark', 'system']`)
- Invalid or tampered values fall back to `'system'` — never used directly in DOM manipulation
- No user-generated content is stored; XSS risk is minimal

### Script Injection Prevention
- `ThemeScript` uses a hardcoded inline script — no dynamic interpolation of user input
- The `storageKey` prop is set at build time, not from user input
- `dangerouslySetInnerHTML` is safe here because the script content is a static string

### Content Security Policy
- The inline `ThemeScript` requires a CSP `script-src` nonce or hash
- Document the required CSP hash in the rollout plan so the infrastructure team can add it

## Performance Considerations

### Zero-JS Initial Paint
- `ThemeScript` executes synchronously before any stylesheet or React bundle
- The `data-theme` attribute is set before the browser's first style calculation
- Result: correct theme on first contentful paint, zero layout shift, no FOUC

### CSS Variable Swap Cost
- Changing `data-theme` triggers a single style recalculation on `:root`
- All descendant elements inherit new variable values — no JavaScript iteration
- Measured cost: ~5-15ms on mid-range devices (well within the 50ms budget)

### Bundle Impact
- `ThemeProvider` + `useTheme` + `ThemeToggle`: ~1.2KB gzipped (no external dependencies except React)
- `ThemeScript` inline script: ~300 bytes uncompressed
- CSS variable definitions: ~800 bytes for both themes
- Total theming overhead: ~1.5KB gzipped (under 2KB budget)

### No Additional Network Requests
- Theme switching is entirely client-side (CSS variables + localStorage)
- No API calls, no dynamic stylesheet loading, no font changes between themes

## Testing Strategy

### Unit Tests
- `themeReducer`: All action types and edge cases (invalid actions, unknown themes)
- `useTheme` hook: Return values, `setTheme`, `toggleTheme` cycle order
- `ThemeScript` output: Verify inline script content for each default theme value
- localStorage helpers: Read, write, validate, fallback behavior

### Component Tests (React Testing Library)
- `ThemeProvider`: Mounts with correct initial theme, responds to dispatched actions
- `ThemeToggle`: Renders correct icon per theme, cycles on click, accessible attributes present
- `ThemeToggle`: Keyboard interaction (Enter, Space) triggers toggle
- `ThemeToggle`: `aria-label` updates on each theme state

### Integration Tests
- Full toggle cycle: light → dark → system → light — verify `data-theme` and localStorage at each step
- System preference change: mock `matchMedia` change event, verify theme follows when set to "system"
- Persistence: set theme, remount `ThemeProvider`, verify theme is restored from localStorage
- Invalid localStorage: set garbage value, mount provider, verify graceful fallback

### Visual Regression Tests
- Capture baseline screenshots of key pages in light and dark themes
- Detect unintended color changes, missing variable migrations, or contrast failures
- Run on CI for every PR that modifies CSS files

### Accessibility Tests
- Automated axe-core audit on every page in both themes (zero violations)
- Keyboard navigation flow through the toggle and surrounding elements
- Screen reader announcement verification (`aria-live` region)
- Contrast ratio validation for all text/background combinations (4.5:1 minimum)

## Rollout Plan

### Phase 1: Development (Days 1-3)
- Define CSS custom properties and theme tokens
- Build ThemeProvider, useTheme, ThemeToggle, ThemeScript
- Migrate global styles to CSS variables
- Unit and component tests passing

### Phase 2: Visual QA (Day 4)
- Migrate all component-level CSS Modules to use CSS variables
- Visual regression baselines captured for both themes
- Manual QA across Chrome, Firefox, Safari, Edge
- Accessibility audit with axe-core (both themes)

### Phase 3: Staging (Day 5)
- Deploy to staging environment
- Full E2E test suite runs (Playwright)
- Performance profiling (theme switch latency, bundle size)
- Cross-browser testing (BrowserStack)

### Phase 4: Production
- Deploy behind feature flag (`ENABLE_DARK_MODE`)
- Gradual rollout: 10% → 50% → 100% over 3 days
- Monitor error rates, performance metrics, user feedback
- Remove feature flag after stable rollout

## Risks & Mitigations

### Risk 1: Flash of Unstyled Content (FOUC)
**Impact:** Users see a white flash before the dark theme applies — poor UX, especially in low-light environments
**Probability:** Medium (common pitfall in SPA theme implementations)
**Mitigation:**
- `ThemeScript` runs synchronously in `<head>` before any CSS or JS
- Test on slow 3G throttling to confirm no flash
- Safari-specific testing (known to delay inline script execution in some cases)

### Risk 2: Third-Party Component Incompatibility
**Impact:** Components from external libraries (date pickers, modals, tooltips) ignore CSS variables and display in hardcoded light styles
**Probability:** Medium
**Mitigation:**
- Audit all third-party components for theme compatibility before implementation
- Write scoped CSS overrides for incompatible components (e.g., `.dark-theme .datepicker { ... }`)
- Open upstream issues for libraries that should support theming
- Document overrides in a `third-party-theme-overrides.css` file

### Risk 3: Contrast Regression
**Impact:** Designers or developers add new UI elements that fail contrast checks in one theme, creating accessibility violations
**Probability:** High (ongoing risk as UI evolves)
**Mitigation:**
- Automated axe-core checks in CI for both themes
- Visual regression tests catch color changes
- Add a "Dark Mode Checklist" to the PR template
- Stylelint rule to enforce usage of CSS variables instead of hardcoded colors

### Risk 4: localStorage Unavailable
**Impact:** Private browsing mode or restrictive browser settings block localStorage access, breaking persistence
**Probability:** Low
**Mitigation:**
- Wrap localStorage access in try/catch
- Fall back to in-memory storage (preference lasts for current session only)
- ThemeScript handles the exception gracefully (defaults to system preference)

## Future Enhancements
- Server-side theme resolution for SSR/SSG (read cookie or header)
- Sync theme preference to user profile API (cross-device consistency)
- Custom accent color picker (CSS variable overrides)
- Scheduled automatic switching (light during day, dark at night)
- High-contrast mode as a fourth theme option
- Per-component theme overrides for embedded widgets
