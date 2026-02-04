# Architectural Decisions

## Session Theme Architecture
- `theme_id` stored per session in backend
- Frontend uses `data-theme="<id>"` attribute on root element
- Light/dark mode is `.dark` class (local-only, not persisted to API)
- SSE endpoint: `GET /api/v1/sessions/{session_id}/stream` for theme updates

## SSE Event Format
```javascript
{
  type: "session_theme",
  session_id: "<id>",
  theme_id: "<id>"
}
```

## Default Theme
- Default session theme: `aurora`

---

## Task 9: Theme Picker UI Architecture Decisions

1. **No Optimistic Updates for Theme Changes**
   - Decision: ThemePicker calls API directly without immediate local state update
   - Rationale: 
     - SSE stream (Task 8) updates session when backend responds
     - ThemeProvider watches `currentSession.theme_id` and applies theme automatically
     - Prevents UI inconsistencies between local state and server state
   - Tradeoff: Small delay between click and theme change is acceptable for data consistency

2. **Loading State Management**
   - Decision: Simple boolean `updating` state + "Updating..." indicator
   - Rationale:
     - Prevents double-clicks on theme buttons
     - Provides user feedback during API call
     - Single update at a time prevents race conditions
   - Implementation: `setUpdating(themeId)` before API call, `setUpdating(null)` in finally block

3. **Gradient Swatches in Component**
   - Decision: Inline gradient styles defined in component TypeScript
   - Rationale:
     - Self-contained component without external CSS dependencies
     - Clear visual representation of each theme's palette
     - Immediate visual feedback without external lookups
   - Future improvement: Migrate to use CSS variables from themes.css (Task 10)

4. **No Session State Handling**
   - Decision: Show "Create a session to change themes" message when no session
   - Rationale:
     - Prevents confusion when theme picker has nothing to act on
     - Guides user to create session first
     - Graceful degradation for edge case
   - Alternative (rejected): Disable theme picker silently (confusing)

5. **Separate Light/Dark Toggle and Theme Picker**
   - Decision: Keep Mode toggle (light/dark) separate from Theme picker (aurora/ocean/ember)
   - Rationale:
     - Mode is user preference (localStorage)
     - Theme is session setting (API persisted)
     - Clear distinction in UI: "Mode" vs "Theme Preset"
     - Matches decisions.md: light/dark is local-only

---
## Task 10.1 Decisions

### Decision 1: Use Standard CSS for #root Styling
**Choice**: Added `#root` styling to `index.css` using standard CSS instead of Tailwind utility classes

**Rationale**:
- Layout constraints (max-width, margin: 0 auto) are clearer as CSS rules
- #root is a global element, not a component requiring Tailwind utilities
- Maintains consistency with other global styles in index.css
- Preserves existing layout behavior without visual regression

**Alternative Considered**: Using Tailwind utilities like `max-w-[1280px] w-full mx-auto`
**Rejection**: Would require adding classes to #root in index.html, which adds complexity for global layout

### Decision 2: Preserve Max-Width Constraint
**Choice**: Keep `max-width: 1280px` on #root

**Rationale**:
- Prevents app from becoming too wide on large displays
- Centers content with better visual hierarchy
- Maintains existing user experience
- Consistent with modern app design patterns

### Decision 3: Remove Unused Legacy CSS
**Choice**: Delete all legacy CSS from App.css (.logo, .card, .read-the-docs, animations)

**Rationale**:
- These classes are not used anywhere in the codebase
- Code search confirmed no references to these classes
- Reduces bundle size by removing dead code
- Simplifies codebase for future maintainers
