
# Decisions - Drawer-First UX Implementation

## Strategic Decisions

### Epic 5 (Themes & UX) Handling
**Decision**: Implement basic styling inline with other epics instead of separate Epic 5
**Rationale**:
- Epic 5 documentation failed during planning (only task estimates, no PRD)
- Styling requirements (Posting-inspired colors, focus highlights, drawer width config, accessibility) can be integrated into Epic 1 (DrawerWidget styling)
- Avoids parallel worktree that would cause merge conflicts
- Reduces complexity from 6 independent epics to 5 epics
- Posting-inspired neutral/accent colors can be defined in DrawerWidget CSS
- Drawer width configuration and reduced motion can be added to Settings
- High-contrast mode can be added as accessibility option

**Deferred**: Full theme system with advanced theming to lower priority

---

### Shared Foundation Approach
**Decision**: NO shared foundation epic
**Rationale**:
- Epic 1 (Drawer-First UX) will implement DrawerModel and FocusManager as part of drawer widget
- Other epics can depend on Epic 1's implementations
- Merge plan recommends implementing Epic 1 first, then other epics
- Creating separate shared foundation would require merging Epic 1 anyway
- Reduces merge complexity by having single source in Epic 1

---

### Implementation Approach
**Decision**: Implement directly in current worktree (tui), not separate worktrees
**Rationale**:
- Planning phase created separate worktrees for each epic (drawer-first-ux, providers-accounts, sessions, subagents, themes-ux, observability-safety)
- These were planning artifacts, not implementation targets
- Implementing in current worktree follows merge plan's Phase 2-7 approach
- Avoids cross-worktree merge complexity
- Simpler testing and integration

---

### Parallelization Strategy
**Decision**: Implement Wave 1 tasks in parallel, then subsequent waves sequentially
**Rationale**:
- Wave 1 has independent tasks that can run in parallel
- Wave 2-4 have dependencies on Wave 1 components
- Wave 4 has dependencies on Waves 2-3
- Allows faster delivery of Wave 1 foundation
- Reduces overall timeline

