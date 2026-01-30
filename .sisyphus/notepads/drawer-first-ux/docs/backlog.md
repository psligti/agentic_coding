# Drawer-First UX - Backlog

**Version**: 1.0
**Date**: 2026-01-30
**Status**: Complete

---

## 1. Overview

This backlog consolidates all user stories from 6 drawer-focused epics into actionable tasks with acceptance criteria and implementation effort estimates.

### Epics Summary

| Epic | Total Stories | Tasks | Implementation Effort |
|------|----------------|-------|------------------|
| Epic 1 - Drawer-First UX | 6 | 23 | High |
| Epic 2 - Providers & Accounts Overlay | 5 | 17 | Medium |
| Epic 3 - Sessions | 4 | 12 | Medium |
| Epic 4 - Subagents | 4 | 15 | High |
| Epic 5 - Themes & UX | 3 | 9 | Low |
| Epic 6 - Observability & Safety | 5 | 18 | Medium |
| **Total** | **27** | **94** | **Very High** |

**Note**: Epic 5 (Themes & UX) documentation was not generated during planning phase. Tasks are estimated based on requirements.

---

## 2. Epic 1: Drawer-First UX

### Stories

#### Story 1.1: Toggle Drawer Visibility
- **Acceptance Criteria**:
  - [ ] Drawer slides in from right side with smooth animation (0.1-0.2s duration)
  - [ ] Drawer has 3 tabs: Todos, Subagents, Navigator
  - [ ] Main timeline remains visible when drawer is open
  - [ ] Ctrl+D keybinding toggles drawer open/close
  - [ ] Navigation keys work within drawer (arrows, Tab, Shift+Tab, Enter)
  - [ ] Focus transitions work correctly
  - [ ] Drawer operates as an overlay (does not push/replace main view)
  - [ ] Drawer state persists across sessions
  - [ ] Drawer closes with Escape key

- **Tasks**:
  - [1.1] Implement DrawerWidget component (3 tabs, slide animation)
  - [1.2] Add drawer state management (visible, width, active_tab)
  - [1.3] Implement tab switching logic (preserve state, reset scroll position)
  - [1.4] Add keyboard bindings (Ctrl+D, Escape, Tab, navigation keys)
  - [1.5] Integrate with event bus (drawer:open, drawer:close)
  - [1.6] Add CSS styling (slide animation, width 30-45%)

**Estimate**: 8 hours

---

#### Story 1.2: Navigate Between Drawer Tabs

- **Acceptance Criteria**:
  - [ ] Tab buttons switch between Todos, Subagents, Navigator
  - [ ] Active tab is visually distinct
  - [ ] Tab switching preserves drawer state (except scroll position)
  - [ ] Focus moves to first interactive element in new tab

- **Tasks**:
  - [2.1] Implement TabButton components for each tab
  - [2.2] Implement tab content switching logic
  - [2.3] Add focus management for tab switching
  - [2.4] Update drawer active_tab reactively

**Estimate**: 3 hours

---

#### Story 1.3: Drawer Content Areas

- **Acceptance Criteria**:
  - [ ] Todos tab shows task list with status indicators
  - [ ] Subagents tab shows subagent list with status
  - [ ] Navigator tab shows timeline index
  - [ ] Content is scrollable when items exceed available height

- **Tasks**:
  - [3.1] Implement TodoList component (DataTable with status icons)
  - [3.2] Implement SubagentList component (DataTable with status indicators)
  - [3.3] Implement NavigatorTimeline component (timeline index)
  - [3.4] Add filter/search functionality to navigator
  - [3.5] Implement scrollable container for each tab content

**Estimate**: 6 hours

---

#### Story 1.4: Focus Transitions

- **Acceptance Criteria**:
  - [ ] Opening drawer does not lose focus on current timeline position
  - [ ] Closing drawer returns focus to where it was before opening
  - [ ] Focus transitions follow predictable patterns
  - [ ] Focus history tracked for debugging

- **Tasks**:
  - [4.1] Implement FocusModel (drawer, main, prompt, top_bar states)
  - [4.2] Implement FocusManager with request/release methods
  - [4.3] Add focus transition tracking (history list)
  - [4.4] Emit focus transition events (FOCUS_WILL_CHANGE, FOCUS_DID_CHANGE)
  - [4.5] Integrate with drawer widget (focus request/release)
  - [4.6] Integrate with existing TUI components

**Estimate**: 5 hours

---

#### Story 1.5: Drawer Persistence

- **Acceptance Criteria**:
  - [ ] Drawer state (visible, width, active_tab) persists across sessions
  - [ ] Drawer state is saved/restored when resuming sessions
  - [ ] Drawer state is stored in session metadata

- **Tasks**:
  - [5.1] Extend session metadata in core/models.py (drawer_state field)
  - [5.2] Update SessionManager to save/load drawer state
  - [5.3] Update TUI app to save drawer state on session start/load
  - [5.4] Update TUI app to restore drawer state on resume

**Estimate**: 3 hours

---

#### Story 1.6: Drawer Animation

- **Acceptance Criteria**:
  - [ ] Drawer slide animation is smooth (0.1-0.2s duration)
  - [ ] Reduced motion mode respects accessibility settings
  - [ ] Animation can be disabled via theme setting

- **Tasks**:
  - [6.1] Implement CSS transition with ease-in-out (0.15s)
  - [6.2] Add reduced motion support (CSS class on drawer)
  - [6.3] Integrate with theme system (check reduced_motion setting)
  - [6.4] Add animation duration configuration

**Estimate**: 2 hours

---

## 3. Epic 2: Providers & Accounts Overlay

### Stories

#### Story 2.1: Top Bar Display

- **Acceptance Criteria**:
  - [ ] Top bar displays current provider, account, and model
  - [ ] Color-coded sections (provider=accent, account=success, model=info)
  - [ ] Clickable to open quick switch dialog

- **Tasks**:
  - [7.1] Implement TopBarModel component with reactive fields
  - [7.2] Add SessionHeader integration (existing component, extend model)
  - [7.3] Implement color-coded display logic
  - [7.4] Add click handler for quick switch (Ctrl+Shift+P)

**Estimate**: 4 hours

---

#### Story 2.2: Command Palette Integration

- **Acceptance Criteria**:
  - [ ] Command palette provides quick access to switch provider/account/model
  - [ ] Actions are available globally (Ctrl+Shift+P)

- **Tasks**:
  - [8.1] Add switch_provider command action
  - [8.2] Add switch_account command action
  - [8.3] Add switch_model command action
  - [8.4] Add manage_providers command action
  - [8.5] Add manage_accounts command action
  - [8.6] Integrate with command palette dialog
  - [8.7] Add command palette action handlers

**Estimate**: 4 hours

---

#### Story 2.3: Provider Switching Events

- **Acceptance Criteria**:
  - [ ] Provider switching emits timeline events
  - [ ] Events include current and previous values for audit trail
  - [ ] Timeline shows provider/account/model changes with visual indicators

- **Tasks**:
  - [9.1] Add provider:changed event to event_bus
  - [9.2] Add account:changed event to event_bus
  - [9.3] Add model:changed event to event_bus
  - [9.4] Add providers:loaded event for TUI startup
  - [9.5] Add accounts:loaded event for TUI startup
  - [9.6] Integrate with MessageScreen for timeline display

**Estimate**: 3 hours

---

#### Story 2.4: Provider State Persistence

- **Acceptance Criteria**:
  - [ ] Active provider/account/model selections persist across TUI sessions
  - [ ] Selection survives TUI restart

- **Tasks**:
  - [10.1] Create ProviderStateManager class
  - [10.2] Implement state persistence (~/.opencode/provider_selection.json)
  - [10.3] Load saved selections on TUI initialization
  - [10.4] Provide reactive state management
  - [10.5] Emit events on state changes (provider:changed, account:changed, model:changed)
  - [10.6] Integrate with SessionHeader for display updates

**Estimate**: 3 hours

---

## 4. Epic 3: Sessions

### Stories

#### Story 3.1: Session List via Command Palette

- **Acceptance Criteria**:
  - [ ] Session list accessible via command palette action
  - [ ] "Session is Timeline" concept reinforced
  - [ ] Drawer navigator shows session timeline index

- **Tasks**:
  - [11.1] Add "List Sessions" command palette action
  - [11.2] Create SessionListAction for filtering sessions
  - [11.3] Implement session filtering (by name, by date, by status)
  - [11.4] Add session sorting options
  - [11.5] Add session selection (Enter to open selected session)
  - [11.6] Integrate with command palette dialog

**Estimate**: 3 hours

---

#### Story 3.2: Timeline Index in Drawer

- **Acceptance Criteria**:
  - [ ] Drawer navigator shows session timeline index
  - [ ] Timeline index aggregates messages and timeline events
  - [ ] Navigation to drawer navigator jumps to timeline position

- **Tasks**:
  - [12.1] Create NavigatorTimelineModel (unified message+event aggregation)
  - [12.2] Extend SessionManager.get_timeline_events() to merge messages + timeline events
  - [12.3] Implement NavigatorTimeline component (event list, filter/search)
  - [12.4] Add event emission (TIMELINE_INDEX_UPDATED, NAVIGATOR_SCROLL_TO_EVENT)
  - [12.5] Add click navigation (jump to timeline position)
  - [12.6] Integrate with MessageScreen (scroll to event)

**Estimate**: 4 hours

---

#### Story 3.3: "Session is Timeline" Principle

- **Acceptance Criteria**:
  - [ ] Session is the timeline concept reinforced
  - [ ] Timeline is the authoritative view of session progress

- **Tasks**:
  - [13.1] Ensure all user/agent actions emit timeline events
  - [13.2] Ensure timeline events are comprehensive
  - [13.3] Add timeline event type validation
  - [13.4] Document "Session is Timeline" principle in user guide

**Estimate**: 2 hours

---

## 5. Epic 4: Subagents

### Stories

#### Story 4.1: Subagent Registry Enhancement

- **Acceptance Criteria**:
  - [ ] Subagent registry with metadata (description, capabilities, last_run_info)
  - [ ] Lookup subagents by name
  - [ ] Query subagent status and execution history

- **Tasks**:
  - [14.1] Implement SubagentRegistry class (register, lookup, get_subagent_status)
  - [14.2] Add metadata fields to Agent model (description, capabilities)
  - [14.3] Implement get_subagent_status() method
  - [14.4] Implement get_last_result() method (query by name, session_id, since)
  - [14.5] Create SubagentResult dataclass (status, timestamp, output, error, metadata)

**Estimate**: 4 hours

---

#### Story 4.2: Run/Rerun Functionality

- **Acceptance Criteria**:
  - [ ] Run subagent with parameters
  - [ ] Rerun subagent with previous execution parameters
  - [ ] Cancel running subagent execution

- **Tasks**:
  - [15.1] Extend AgentManager with run_subagent() method
  - [15.2] Implement run_subagent() with parameters, session_id
  - [15.3] Implement rerun_subagent() with last parameters
  - [15.4] Implement cancel_subagent() method
  - [15.5] Add SubagentResult tracking (status, timestamp)
  - [15.6] Emit events (SUBAGENT_RUN, SUBAGENT_RERUN, SUBAGENT_STATUS_CHANGED, SUBAGENT_RESULT_READY)

**Estimate**: 5 hours

---

#### Story 4.3: Result Objects with Status

- **Acceptance Criteria**:
  - [ ] Result objects track execution status
  - [ ] Status enum: IDLE, RUNNING, COMPLETED, ERROR, CANCELLED
  - [ ] Timestamps for start/end/duration_ms

- **Tasks**:
  - [16.1] Define SubagentStatus enum
  - [16.2] Define SubagentResult dataclass with all required fields
  - [16.3] Add status transitions (running → completed/error)
  - [16.4] Add computed properties (duration_ms, output_preview)
  - [16.5] Implement error tracking (error messages, stack traces)
  - [16.6] Add metadata dictionary for custom properties

**Estimate**: 3 hours

---

#### Story 4.4: Drawer Display

- **Acceptance Criteria**:
  - [ ] Drawer shows subagent status and last result
  - [ ] Status indicators are color-coded (idle=gray, running=blue, completed=green, error=red)
  - [ ] Last result preview (first 100 chars or error message)

- **Tasks**:
  - [17.1] Implement SubagentDrawer widget (status list, actions, preview)
  - [17.2] Implement SubagentList component (DataTable with status icons)
  - [17.3] Add run button (disabled while running)
  - [17.4] Add rerun button
  - [17.5] Add cancel button
  - [17.6] Add result preview display
  - [17.7] Integrate with SubagentRegistry (real-time updates)
  - [17.8] Add event emissions (SUBAGENT_STATUS_CHANGED, SUBAGENT_RESULT_READY, DRAWER_SUBAGENT_SELECTED)

**Estimate**: 4 hours

---

## 6. Epic 6: Observability & Safety

### Stories

#### Story 6.1: Timeline Event Generation

- **Acceptance Criteria**:
  - [ ] Every action creates timeline event
  - [ ] Events include full metadata (timestamp, actor, action type, outcome)
  - [ ] Audit trail integration for compliance and debugging

- **Tasks**:
  - [18.1] Implement AuditTrailManager class with storage backend
  - [18.2] Create AuditRecord and AuditTrailQuery models
  - [18.3] Implement log_event() method for all user/agent/tool actions
  - [18.4] Add event types (AUDIT_ACTION_LOGGED)
  - [18.5] Create query methods (by_session, by_actor, by_action_type, by_time_range)
  - [18.6] Integrate with TimelineManager for display updates
  - [18.7] Store audit records as immutable JSON files

**Estimate**: 5 hours

---

#### Story 6.2: Audit Trail Integration

- **Acceptance Criteria**:
  - [ ] Complete audit trail for compliance and debugging
  - [ ] Audit trail can be queried by time range, actor, action type
  - [ ] Audit trail persists across TUI sessions

- **Tasks**:
  - [19.1] Extend SessionStorage to support audit trail storage
  - [19.2] Implement storage directory structure (~/.opencode/audit/)
  - [19.3] Implement AuditTrailStorage class with JSON file operations
  - [19.4] Add indexing support (by session, subagent, timestamp)
  - [19.5] Integrate with TimelineManager for audit event display

**Estimate**: 4 hours

---

#### Story 6.3: Error Surfacing in Drawer

- **Acceptance Criteria**:
  - [ ] Drawer shows error events with visual indicators
  - [ ] Error filter available in navigator (show only errors)
  - [ ] Error events link to corresponding timeline entry

- **Tasks**:
  - [20.1] Implement ErrorCollector class for gathering errors
  - [20.2] Define error levels (CRITICAL, ERROR, WARNING)
  - [20.3] Create error display widget (Errors tab)
  - [20.4] Implement error filtering in NavigatorTimelineModel
  - [20.5] Add visual indicators (color-coded icons, severity text)
  - [20.6] Link errors to timeline entries (event_id reference)
  - [20.7] Integrate with drawer widget (Errors tab)

**Estimate**: 3 hours

---

#### Story 6.4: Safe Command Execution

- **Acceptance Criteria**:
  - [ ] Commands requiring confirmation trigger drawer confirmation dialog
  - [ ] Confirmation dialog shows command description, affected paths, potential impact
  - [ ] User can approve/deny commands
  - [ ] Dry-run mode available for bulk operations

- **Tasks**:
  - [21.1] Implement SafeCommandModel with risk assessment
  - [21.2] Implement ConfirmationDialog component
  - [21.3] Add risk level indicators (LOW, MEDIUM, HIGH, CRITICAL)
  - [21.4] Implement approve/deny buttons
  - [21.5] Implement dry-run toggle
  - [21.6] Add confirmation history to audit trail
  - [21.7] Integrate with SafetyController for validation logic
  - [21.8] Add event emissions (SAFE_COMMAND_REQUESTED, SAFE_COMMAND_APPROVED)

**Estimate**: 4 hours

---

## 7. Epic 5: Themes & UX

### Stories

#### Story 5.1: Minimal Posting-Inspired Styling

- **Acceptance Criteria**:
  - [ ] Posting-inspired color palette (neutral, accent colors)
  - [ ] Consistent focus/highlight across drawer
  - [ ] Minimal design with clear visual hierarchy

- **Note**: Epic 5 documentation was not generated. Tasks are estimated based on Epic 2 (Providers & Accounts) top bar styling and Epic 1 (Drawer-First UX) component structure.

- **Tasks**:
  - [22.1] [PENDING] Define color palette variables
  - [22.2] [PENDING] Apply Posting-inspired colors to drawer CSS
  - [22.3] [PENDING] Add focus highlight consistency (active focus color, consistent patterns)
  - [22.4] [PENDING] Integrate with existing theme system if available
  - [22.5] [PENDING] Add minimal styling to drawer components (padding, borders, spacing)
  - [22.6] [PENDING] Ensure contrast ratios meet WCAG AA/AAA standards (4.5:1 for text)

**Estimate**: 4 hours (deferred until Epic 5 docs are generated)

---

#### Story 5.2: Consistent Focus/Highlight

- **Acceptance Criteria**:
  - [ ] Focus highlight pattern is consistent across drawer
  - [ ] Active focus is clearly visible
  - [ ] Focus transitions follow predictable patterns

- **Tasks**:
  - [23.1] [PENDING] Define focus highlight styles (CSS classes)
  - [23.2] [PENDING] Add focus indicators to widgets (focus ring, border color)
  - [23.3] [PENDING] Ensure consistency between drawer tabs
  - [23.4] [PENDING] Coordinate focus transitions via FocusManager

**Estimate**: 3 hours (deferred until Epic 5 docs are generated)

---

#### Story 5.3: Drawer Width Configuration

- **Acceptance Criteria**:
  - [ ] Drawer width is configurable (30-45% of terminal width)
  - [ ] Width setting persists across sessions
  - [ ] Drawer respects minimum width constraints (20%)

- **Tasks**:
  - [24.1] [PENDING] Add drawer width configuration to settings
  - [24.2] [PENDING] Add drawer width range validation (20-80%)
  - [24.3] [PENDING] Implement drawer width reactive property
  - [24.4] [PENDING] Update DrawerWidget to use width setting
  - [24.5] [PENDING] Add CSS to enforce width constraints

**Estimate**: 2 hours (deferred until Epic 5 docs are generated)

---

#### Story 5.4: Accessible Colors

- **Acceptance Criteria**:
  - [ ] High-contrast color mode available
  - [ ] Accessible colors for better readability

- **Tasks**:
  - [25.1] [PENDING] Define high-contrast color palette
  - [25.2] [PENDING] Add high-contrast mode toggle to settings
  - [25.3] [PENDING] Apply high-contrast colors to drawer CSS
  - [25.4] [PENDING] Ensure all interactive elements are keyboard-accessible
  - [25.5] [PENDING] Test contrast ratios against WCAG standards (4.5:1 min)

**Estimate**: 3 hours (deferred until Epic 5 docs are generated)

---

## 8. Effort Estimates

| Epic | Total Tasks | Total Estimate |
|------|-------------|--------------|
| Epic 1 - Drawer-First UX | 23 | 31 hours |
| Epic 2 - Providers & Accounts Overlay | 17 | 14 hours |
| Epic 3 - Sessions | 12 | 12 hours |
| Epic 4 - Subagents | 15 | 16 hours |
| Epic 5 - Themes & UX | 9 | 15 hours |
| Epic 6 - Observability & Safety | 18 | 22 hours |
| **Total** | **94** | **110 hours** |

**Note**: Epic 5 (Themes & UX) tasks are estimated based on requirements from other epics. Epic 5 documentation should be generated to provide accurate estimates.

---

## 9. Dependencies

### Epic 1: Drawer-First UX
**Depends on**:
- Event bus (existing)
- Settings (existing)
- Keybindings (existing)
- TUI app (existing)

### Epic 2: Providers & Accounts Overlay
**Depends on**:
- Event bus (existing)
- Settings (existing)
- TUI app (existing)
- Provider management (existing)

### Epic 3: Sessions
**Depends on**:
- Event bus (existing)
- Settings (existing)
- TUI app (existing)
- Session management (existing)

### Epic 4: Subagents
**Depends on**:
- Event bus (existing)
- Settings (existing)
- TUI app (existing)
- Agent management (existing)

### Epic 5: Themes & UX
**Depends on**:
- Event bus (existing)
- Settings (existing)
- Keybindings (existing)
- Theme system (unknown if exists)
- TUI app (existing)
- Provider management (existing)

### Epic 6: Observability & Safety
**Depends on**:
- Event bus (existing)
- Settings (existing)
- Timeline management (existing)
- Session management (existing)
- Storage (existing)

---

## 10. Success Criteria Verification

Each epic includes explicit success criteria. This backlog marks which criteria have been met by the implementation.

### Epic 1: Drawer-First UX
- ✅ All 6 acceptance criteria documented
- ✅ Verification methods: manual testing, user acceptance feedback

### Epic 2: Providers & Accounts Overlay
- ✅ All 5 acceptance criteria documented
- ✅ Verification methods: command palette testing, event emission verification

### Epic 3: Sessions
- ✅ All 4 acceptance criteria documented
- ✅ Verification methods: session list testing, timeline navigation testing

### Epic 4: Subagents
- ✅ All 4 acceptance criteria documented
- ✅ Verification methods: subagent testing, drawer display testing

### Epic 6: Observability & Safety
- ✅ All 5 acceptance criteria documented
- ✅ Verification methods: audit trail verification, error display testing, safety control testing

### Epic 5: Themes & UX
- ⚠ Documentation not generated
- ⚠ Tasks estimated based on other epics
- ⚠ Verification methods cannot be defined until documentation is complete

---

**Backlog Status**: ✅ Complete for 5 out of 6 epics

---

**Priority Levels**:
- **P0 (Critical)**: Epic 1 - Drawer-First UX (foundational component)
- **P1 (High)**: Epic 4 - Subagents (enables complex agent execution)
- **P2 (Medium)**: Epic 2, 3, 6 (enhance existing systems)
- **P3 (Low)**: Epic 5 (styling enhancement)

**Implementation Order Recommendation**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 6 → Phase 5

---

**Document Status**: ✅ Complete