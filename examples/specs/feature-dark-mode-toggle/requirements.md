# Feature: Dark Mode Toggle

## Overview
Add a dark mode toggle to the React application that allows users to switch between light and dark themes. The feature should detect the user's system preference on first visit, persist their manual choice across browser sessions via localStorage, and provide a seamless, accessible experience with smooth CSS transitions and no flash of unstyled content (FOUC). The implementation will use CSS custom properties for theming, React Context for state management, and a blocking inline script to ensure the correct theme is applied before first paint.

## User Stories

### Story 1: Theme Toggle
**As a** user
**I want** to toggle between light and dark themes using a button in the header
**So that** I can choose the visual style that is most comfortable for my eyes

**Acceptance Criteria:**
- [ ] A toggle button is visible in the application header
- [ ] Clicking the button switches from light to dark (and vice versa)
- [ ] Theme switch is instant with no flash of unstyled content (FOUC)
- [ ] The toggle button icon reflects the current theme (sun for dark mode, moon for light mode)
- [ ] All application pages and components reflect the selected theme
- [ ] Theme switch does not cause a full page reload
- [ ] Toggle cycles through three states: light, dark, system (matching OS preference)
- [ ] Toggle state is visually distinct for each of the three modes

### Story 2: System Preference Detection
**As a** first-time visitor
**I want** the application to respect my operating system's color scheme preference
**So that** the theme matches the rest of my desktop environment without manual configuration

**Acceptance Criteria:**
- [ ] Application detects `prefers-color-scheme` media query on initial load
- [ ] If no manual preference is stored, the system preference is used
- [ ] When the OS color scheme changes (e.g., macOS auto dark mode at sunset), the app follows in real time
- [ ] System preference is only followed when the user has not set a manual override
- [ ] The toggle button indicates "system" state when following OS preference
- [ ] Detection works on all major browsers (Chrome, Firefox, Safari, Edge)

### Story 3: Preference Persistence
**As a** returning user
**I want** my theme preference to be remembered across browser sessions
**So that** I do not have to re-select my preferred theme every time I visit

**Acceptance Criteria:**
- [ ] User's manual theme choice is saved to localStorage
- [ ] Theme preference survives browser close and reopen
- [ ] Manual choice overrides the system preference until explicitly reset
- [ ] Clearing localStorage falls back to system preference gracefully
- [ ] Theme is applied before first paint (no white flash in dark mode)
- [ ] Stored value is validated on read (invalid values fall back to "system")
- [ ] localStorage key follows project naming conventions (`specops-theme`)

### Story 4: Accessible Theme Toggle
**As a** user who relies on assistive technology
**I want** the theme toggle to be fully accessible
**So that** I can switch themes using a keyboard or screen reader

**Acceptance Criteria:**
- [ ] Toggle button is focusable and operable via keyboard (Enter and Space)
- [ ] Button has an accessible label describing the current state and action (e.g., "Switch to dark mode")
- [ ] `aria-live` region announces theme change to screen readers
- [ ] Both light and dark themes meet WCAG 2.1 AA contrast requirements (4.5:1 for normal text, 3:1 for large text)
- [ ] Focus indicators are visible in both themes
- [ ] Toggle button meets minimum touch target size (44x44px)
- [ ] Color is not the sole means of conveying information in either theme

### Story 5: Smooth Theme Transitions
**As a** user
**I want** theme changes to feel smooth and polished
**So that** switching themes is a pleasant, non-jarring experience

**Acceptance Criteria:**
- [ ] CSS transitions animate color changes over 200-300ms
- [ ] Transitions apply to background, text, border, and shadow properties
- [ ] No layout shift occurs during theme transition
- [ ] Images and media adapt to the active theme (e.g., reduced brightness or inverted logos)
- [ ] Transitions are disabled when the user has `prefers-reduced-motion` enabled
- [ ] Scrollbar colors adapt to the active theme where supported
- [ ] SVG icons and illustrations use `currentColor` or CSS variables for theme awareness

## Non-Functional Requirements

### Performance
- Theme switch completes in under 50ms (measured as time from click to full repaint)
- No additional network requests required for theme switching
- Theming CSS adds less than 2KB (gzipped) to total bundle size
- Initial theme is resolved before first contentful paint (no FOUC)

### Accessibility
- Both light and dark themes pass WCAG 2.1 AA audit (axe-core, zero violations)
- All interactive elements have visible focus indicators in both themes
- Theme toggle is operable via keyboard and announced by screen readers
- Respects `prefers-reduced-motion` by disabling transitions

### Maintainability
- All color values in the application must use CSS custom properties (no hardcoded hex/rgb)
- Adding a new component must require zero theming boilerplate beyond using existing variables
- Theme definitions are centralized in a single file (`src/styles/themes.css`)

### Browser Compatibility
- Supported browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Graceful fallback for browsers without CSS custom property support (light theme)
- `prefers-color-scheme` detection works across all supported browsers

## Constraints & Assumptions

### Constraints
- Existing React application uses CSS Modules for component styling
- No external UI framework (e.g., Material UI, Chakra) is in use — raw CSS and CSS Modules only
- Must not introduce new runtime dependencies beyond what ships with React
- Must not break existing component styles or visual tests

### Assumptions
- The project already uses TypeScript and a modern build tool (Vite or webpack 5+)
- CSS custom properties are supported in the target browser matrix
- The application renders client-side (no SSR/SSG requiring server-side theme resolution)
- Existing color values are hardcoded in CSS Modules and need migration to CSS variables
- `lucide-react` is already installed as a project dependency (used for icons)

## Team Conventions
- Use TypeScript for all new code with strict mode enabled
- Write unit tests for hooks and utility functions with minimum 80% coverage
- Write component tests with React Testing Library for interactive elements
- Follow existing file and folder naming conventions (`PascalCase` for components, `camelCase` for hooks)
- Use CSS Modules for component-scoped styles; global variables in `src/styles/themes.css`
- Document public interfaces and hooks with JSDoc
- Keep components focused — presentation components should have no side effects
- Handle edge cases explicitly (missing localStorage, unsupported APIs)

## Success Metrics
- 100% of pages render correctly in both light and dark themes (visual regression baseline)
- Theme switch p95 latency < 50ms (measured via Performance API)
- Zero WCAG 2.1 AA violations in both themes (automated axe-core audit)
- No FOUC reported in manual QA across Chrome, Firefox, Safari, Edge
- User preference persistence works across sessions (automated Playwright test)

## Out of Scope (Future Considerations)
- Per-page or per-section theme overrides
- Custom color picker or user-defined accent colors
- Scheduled theme switching (e.g., dark mode after 6 PM)
- High-contrast mode (beyond standard dark/light)
- Server-side theme resolution for SSR/SSG
- Syncing theme preference across devices via a backend API
- Theme-aware syntax highlighting for code blocks (handled separately)
- Print stylesheet theme adjustments
