# Drawer-First UX Implementation Plan

**Version**: 1.0
**Date**: 2026-01-30
**Status**: Ready for Execution

---

## Executive Summary

Implement Drawer-First UX system across 6 epics (94 tasks, 110 hours estimated). Epic 5 (Themes & UX) documentation was not generated during planning phase - will implement basic styling as part of other epics.

**Strategy**: Implement directly in current worktree (tui) following merge plan's recommended order to reduce cross-epic conflicts.

**Estimated Timeline**: 72-84 hours total

---

## 1. Epic 5 Decision: Themes & UX

**Issue**: Epic 5 documentation failed during planning. Only task estimates exist (15 hours, 9 tasks).

**Decision**: **Implement basic styling inline with other epics**

**Rationale**:
- Epic 5 provides: Posting-inspired palette, focus highlights, drawer width config, accessibility features
- These can be integrated into Epic 1 (DrawerWidget styling), Epic 2 (top bar styling), Epic 6 (error display styling)
- Basic Posting-inspired colors (neutral + accent) can be defined in Epic 1's DrawerWidget CSS
- Drawer width configuration can be added to Settings in Epic 1
- Reduced motion and high-contrast can be added as accessibility options
- Avoids parallel Epic 5 worktree that would cause merge conflicts

**Deferred**: Full theme system with advanced theming to lower priority post-implementation.

---

## 2. Shared Foundation Decision

**Issue**: No global FocusManager or DrawerModel exists yet. All 6 epics would need to integrate with these.

**Decision**: **NO - Implement shared foundation first**

**Rationale**:
- Epic 1 (Drawer-First UX) will implement DrawerWidget, DrawerModel, FocusManager
- These are foundational components that other epics depend on
- Implementing shared foundation as separate epic would require merging Epic 1 anyway
- Merge plan recommends: Phase 2 (Epic 1) first, then other epics
- Other epics can depend on Epic 1's DrawerModel and FocusManager implementations
- Reduces merge complexity by having definitive source in Epic 1

---

## 3. Parallel Task Waves

### Wave 1: Foundation (Epic 1) - MUST COMPLETE FIRST
**Duration**: 8-12 hours
**Status**: BLOCKING all other waves until complete

Tasks 1.1-1.6 (Drawer Widget):
- Implement DrawerWidget with 3 tabs (Todos, Subagents, Navigator)
- Implement FocusManager class
- Add focus transition logic
- Integrate with event bus
- Add keyboard bindings (Ctrl+D, Escape, Tab, navigation keys)
- Add CSS styling with slide animations
- Add drawer state persistence

**Can Parallelize Within Wave**: Yes (Tab components, FocusManager, Event integrations can be done in parallel after DrawerWidget skeleton)

### Wave 2: Content Epics (Epic 2, 3, 4) - AFTER Wave 1
**Duration**: 26-42 hours
**Dependencies**: Wave 1 (DrawerModel, FocusManager, drawer events)

Tasks that can run in parallel:
- Epic 2: TopBarModel with provider/account/model display (4 hours)
- Epic 3: Session list command, timeline index aggregation (4 hours)
- Epic 4: SubagentRegistry, run/rerun functionality (4 hours)

**Must be sequential within Epic 2**: ProviderStateManager → TopBarModel → event integration

**Must be sequential within Epic 3**: SessionListAction → NavigatorTimelineModel → SessionManager extension → event integration

**Must be sequential within Epic 4**: SubagentRegistry → AgentManager extension → SubagentResult model → SubagentDrawer widget

### Wave 3: Enhancement Epic (Epic 6) - AFTER Wave 2
**Duration**: 22 hours
**Dependencies**: Wave 2 (all epics for observability events, error collection)

Tasks:
- AuditTrailManager implementation (5 hours)
- ErrorCollector implementation (3 hours)
- SafetyController implementation (4 hours)
- Integration with TimelineManager (2 hours)
- Event integration (3 hours)
- ConfirmationDialog component (3 hours)

**Can Parallelize**: Yes (AuditTrailManager, ErrorCollector, SafetyController, ConfirmationDialog can be done in parallel)

### Wave 4: Integration & Polish - AFTER Wave 3
**Duration**: 12-16 hours
**Dependencies**: Waves 1-3

Tasks:
- Integrate all epics in TUI app (2 hours)
- End-to-end integration testing (4 hours)
- Cross-epic event flow verification (2 hours)
- Bug fixes and polish (2-4 hours)

---

## 4. Task Specifications

### Wave 1: Foundation (Epic 1)

#### Task 1.1: Implement DrawerWidget Component
**Category**: visual-engineering
**Skills**: frontend-ui-ux
**Estimate**: 4 hours
**Dependencies**: None

**Description**: Create DrawerWidget with 3 tabs (Todos, Subagents, Navigator) that slides in from right side as overlay.

**Acceptance Criteria**:
- [ ] DrawerWidget class created in `opencode_python/tui/widgets/drawer.py`
- [ ] Widget has 3 tab buttons with icons (📋 Todos, 🤖 Subagents, 🧭 Navigator)
- [ ] Tab content areas exist (TodoList, SubagentList, NavigatorTimeline)
- [ ] Slide animation implemented (0.15s ease-in-out)
- [ ] Width configurable (30-45% of terminal)
- [ ] Drawer operates as overlay (main content visible when open)
- [ ] Test: `pytest tests/tui/test_drawer_widget.py` - 10 test cases pass
- [ ] Manual verify: Start TUI, press Ctrl+D, drawer slides in smoothly

**Implementation Steps**:
1. Create DrawerWidget class extending Textual Container
2. Implement TabButton component for each tab
3. Create tab content containers (scrollable)
4. Add DrawerModel with reactive properties (visible, width, active_tab, has_focus)
5. Implement toggle_visible() method
6. Implement switch_tab(tab_id) method
7. Add CSS for slide animation and styling
8. Register widget in TUI app's compose()

---

#### Task 1.2: Implement FocusManager
**Category**: ultrabrain
**Skills**: python-programming
**Estimate**: 3 hours
**Dependencies**: None

**Description**: Global focus management system that tracks focus across drawer, main timeline, prompt, top bar.

**Acceptance Criteria**:
- [ ] FocusManager class created in `opencode_python/core/focus_manager.py`
- [ ] FocusModel with states (drawer_focused, main_focused, prompt_focused, top_bar_focused)
- [ ] Focus history tracking (list of transitions)
- [ ] request_focus(target_widget, target_id) method
- [ ] release_focus() method that returns to previous focus
- [ ] Events: FOCUS_WILL_CHANGE, FOCUS_DID_CHANGE emitted
- [ ] Test: `pytest tests/core/test_focus_manager.py` - 8 test cases pass
- [ ] Manual verify: Focus transitions work correctly, focus history tracks changes

**Implementation Steps**:
1. Create FocusModel dataclass
2. Create FocusManager class with singleton pattern
3. Implement request_focus() with validation
4. Implement release_focus() with history lookup
5. Add event emissions for focus transitions
6. Register global instance in event_bus.py

---

#### Task 1.3: Integrate Drawer with Event Bus
**Category**: quick
**Skills**: git-master
**Estimate**: 2 hours
**Dependencies**: 1.1, 1.2 (DrawerWidget, FocusManager created)

**Description**: Add drawer-specific events to event bus and wire up DrawerWidget to emit/receive events.

**Acceptance Criteria**:
- [ ] Events added to Events class: DRAWER_OPEN, DRAWER_CLOSE, DRAWER_TAB_CHANGED, DRAWER_FOCUS_REQUEST, DRAWER_FOCUS_RELEASED
- [ ] DrawerWidget emits DRAWER_OPEN when toggling visible
- [ ] DrawerWidget emits DRAWER_CLOSE when toggling visible
- [ ] DrawerWidget emits DRAWER_TAB_CHANGED when switching tabs
- [ ] DrawerWidget subscribes to FocusManager events
- [ ] Test: `pytest tests/core/test_drawer_events.py` - 6 test cases pass

**Implementation Steps**:
1. Add drawer events to Events class in event_bus.py
2. Implement event handlers in DrawerWidget for focus requests
3. Add publish calls for all state changes
4. Add event subscriptions for external focus changes
5. Verify event flow with tests

---

#### Task 1.4: Add Keyboard Bindings
**Category**: quick
**Skills**: git-master
**Estimate**: 2 hours
**Dependencies**: 1.1, 1.3 (DrawerWidget created)

**Description**: Add Ctrl+D binding for drawer toggle, Escape to close, Tab navigation.

**Acceptance Criteria**:
- [ ] Ctrl+D binding added: toggles drawer visible
- [ ] Escape binding added: closes drawer and returns focus
- [ ] Tab/Shift+Tab: cycles through drawer tabs
- [ ] Navigation keys (arrows) work within active tab content
- [ ] Enter key: activates selected item in drawer
- [ ] Keybindings added to TUI app's BINDINGS list
- [ ] Test: `pytest tests/tui/test_keybindings.py` - drawer keybindings tested
- [ ] Manual verify: All keyboard shortcuts work as expected

**Implementation Steps**:
1. Add Ctrl+D binding to app.py BINDINGS
2. Add Escape binding
3. Add Tab/Shift+Tab bindings
4. Add navigation key bindings (arrows, enter)
5. Implement action methods in app.py or DrawerWidget
6. Test all keyboard shortcuts

---

#### Task 1.5: Add Drawer State Persistence
**Category**: deep
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: 1.1 (DrawerWidget created)

**Description**: Persist drawer state (visible, width, active_tab) across TUI sessions.

**Acceptance Criteria**:
- [ ] Drawer state added to session metadata in core/models.py
- [ ] SessionManager.update_session() saves drawer state
- [ ] SessionManager.get_session() loads drawer state on resume
- [ ] TUI app loads drawer state on session start
- [ ] Test: `pytest tests/core/test_drawer_persistence.py` - 4 test cases pass
- [ ] Manual verify: Open TUI, open drawer, close TUI, reopen - state persists

**Implementation Steps**:
1. Extend Session model with drawer_state field (dict)
2. Add drawer_state to SessionManager.update_session() calls
3. Add drawer_state loading in TUI app on session resume
4. Add drawer_state saving in DrawerWidget when state changes
5. Verify persistence with tests

---

#### Task 1.6: Add Basic Styling (Posting-Inspired)
**Category**: visual-engineering
**Skills**: frontend-ui-ux
**Estimate**: 1 hour
**Dependencies**: 1.1 (DrawerWidget created)

**Description**: Apply basic Posting-inspired colors (neutral grays, accent color) to DrawerWidget.

**Acceptance Criteria**:
- [ ] CSS variables defined for drawer colors
- [ ] Neutral background (dark gray), accent color (cyan/blue)
- [ ] Focus highlight style (border, bold text)
- [ ] Hover states for interactive elements
- [ ] Test: Visual inspection confirms consistent styling
- [ ] Manual verify: Drawer looks clean, minimal design

**Implementation Steps**:
1. Define CSS color variables in DrawerWidget.CSS
2. Apply neutral background to drawer container
3. Apply accent color to active tab and focus indicators
4. Add hover states for buttons and list items
5. Ensure contrast ratios meet WCAG AA (4.5:1 minimum)

---

### Wave 2: Content Epics (Epic 2, 3, 4) - AFTER Wave 1

#### Task 2.1: Extend TopBarModel for Provider Display
**Category**: visual-engineering
**Skills**: frontend-ui-ux
**Estimate**: 2 hours
**Dependencies**: Wave 1 (Settings updated)

**Description**: Update SessionHeader to display current provider, account, model with color-coded sections.

**Acceptance Criteria**:
- [ ] TopBarModel created in `opencode_python/tui/widgets/top_bar_model.py`
- [ ] Provider display (accent color, clickable)
- [ ] Account display (success color)
- [ ] Model display (info color)
- [ ] Quick switch dialog on click (Ctrl+Shift+P)
- [ ] Test: `pytest tests/tui/test_top_bar.py` - 6 test cases pass
- [ ] Manual verify: Top bar shows provider/account/model correctly

**Implementation Steps**:
1. Create TopBarModel with reactive provider/account/model fields
2. Extend SessionHeader to use TopBarModel
3. Add color-coded display sections
4. Add click handler for quick switch
5. Wire up with ProviderStateManager events

---

#### Task 2.2: Create ProviderStateManager
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: None (can parallel with 2.1)

**Description**: Manage provider/account/model selection state with persistence.

**Acceptance Criteria**:
- [ ] ProviderStateManager in `opencode_python/providers/state_manager.py`
- [ ] Tracks active provider/account/model
- [ ] Persists to ~/.opencode/provider_selection.json
- [ ] Loads saved selection on startup
- [ ] Emits PROVIDER_CHANGED, ACCOUNT_CHANGED, MODEL_CHANGED events
- [ ] Test: `pytest tests/providers/test_state_manager.py` - 8 test cases pass

**Implementation Steps**:
1. Create ProviderStateManager class
2. Implement load_selection() from JSON
3. Implement save_selection() to JSON
4. Implement set_provider(), set_account(), set_model() methods
5. Add event emissions for all state changes
6. Add storage directory creation

---

#### Task 2.3: Add Command Palette Actions
**Category**: quick
**Skills**: git-master
**Estimate**: 2 hours
**Dependencies**: 2.2 (ProviderStateManager created)

**Description**: Add 5 command palette actions: switch_provider, switch_account, switch_model, manage_providers, manage_accounts.

**Acceptance Criteria**:
- [ ] Actions added to CommandPaletteDialog
- [ ] switch_provider opens provider selection dialog
- [ ] switch_account opens account selection dialog
- [ ] switch_model opens model selection dialog
- [ ] manage_providers opens provider settings screen
- [ ] manage_accounts opens account settings screen
- [ ] Test: `pytest tests/tui/test_provider_commands.py` - 10 test cases pass
- [ ] Manual verify: Press /, type provider, action available and works

**Implementation Steps**:
1. Create action handlers for each switch action
2. Integrate with ProviderStateManager
3. Add action registration to CommandPaletteDialog
4. Test all command palette actions
5. Verify event emissions

---

#### Task 2.4: Integrate with Event Bus
**Category**: quick
**Skills**: git-master
**Estimate**: 2 hours
**Dependencies**: 2.1-2.3 (All Epic 2 components created)

**Description**: Add provider/account events to event bus and wire up Epic 2 components.

**Acceptance Criteria**:
- [ ] Events added: PROVIDER_CHANGED, ACCOUNT_CHANGED, MODEL_CHANGED, PROVIDERS_LOADED, ACCOUNTS_LOADED
- [ ] TopBarModel subscribes to provider/account events
- [ ] Command palette actions emit events on selection
- [ ] Test: `pytest tests/core/test_provider_events.py` - 6 test cases pass

**Implementation Steps**:
1. Add provider events to Events class
2. Add event subscriptions in TopBarModel
3. Add event emissions in command actions
4. Verify event flow with tests

---

#### Task 2.5: Add Timeline Events for Provider Changes
**Category**: quick
**Skills**: git-master
**Estimate**: 2 hours
**Dependencies**: 2.4 (Events integrated)

**Description**: Ensure provider/account/model switches create timeline entries.

**Acceptance Criteria**:
- [ ] Provider switches emit timeline events with metadata
- [ ] Account switches emit timeline events with metadata
- [ ] Model switches emit timeline events with metadata
- [ ] Timeline events visible in MessageScreen
- [ ] Test: `pytest tests/core/test_provider_timeline.py` - 4 test cases pass
- [ ] Manual verify: Switch provider, timeline shows change entry

**Implementation Steps**:
1. Add timeline event type in MessageScreen or TimelineManager
2. Subscribe to provider/account events
3. On event, create timeline entry with change details
4. Display timeline entries in session view
5. Verify with tests

---

#### Task 3.1: Add Session List Command
**Category**: quick
**Skills**: git-master
**Estimate**: 1 hour
**Dependencies**: Wave 1 (Settings updated)

**Description**: Add "List Sessions" command to command palette.

**Acceptance Criteria**:
- [ ] Command added to CommandPaletteDialog
- [ ] Opens SessionListScreen
- [ ] Shows all sessions with filtering options
- [ ] Test: `pytest tests/tui/test_session_list_command.py` - 5 test cases pass
- [ ] Manual verify: Press /, type "list sessions", command opens session list

**Implementation Steps**:
1. Create SessionListAction handler
2. Integrate with SessionManager.list_sessions()
3. Add action to CommandPaletteDialog
4. Test command functionality
5. Verify session filtering works

---

#### Task 3.2: Create NavigatorTimelineModel
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: None (can parallel with 3.1)

**Description**: Aggregates messages + timeline events into unified navigator index.

**Acceptance Criteria**:
- [ ] NavigatorTimelineModel in `opencode_python/tui/models/navigator_timeline.py`
- [ ] Merges messages and timeline events chronologically
- [ ] Provides filtering by event type
- [ ] Exports event_id, timestamp, event_type, actor, details
- [ ] Test: `pytest tests/tui/test_navigator_timeline.py` - 8 test cases pass
- [ ] Manual verify: Navigator shows messages and events in order

**Implementation Steps**:
1. Create NavigatorTimelineEvent model
2. Create NavigatorTimelineModel class
3. Implement get_timeline_events(session_id) method
4. Merge messages from SessionManager with timeline events
5. Sort chronologically and return unified list
6. Add filter methods

---

#### Task 3.3: Extend SessionManager for Timeline Aggregation
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 1 hour
**Dependencies**: 3.2 (NavigatorTimelineModel created)

**Description**: Add timeline aggregation method to SessionManager.

**Acceptance Criteria**:
- [ ] SessionManager.get_timeline_events() implemented
- [ ] Queries NavigatorTimelineModel for unified events
- [ ] Caches timeline events for performance
- [ ] Test: `pytest tests/core/test_session_timeline.py` - 5 test cases pass
- [ ] Manual verify: Get timeline events, shows messages + events

**Implementation Steps**:
1. Add get_timeline_events(session_id) method to SessionManager
2. Call NavigatorTimelineModel to get unified events
3. Add caching layer if needed
4. Return sorted timeline list
5. Test with session data

---

#### Task 3.4: Integrate Navigator with Event Bus
**Category**: quick
**Skills**: git-master
**Estimate**: 1 hour
**Dependencies**: 3.3 (SessionManager extended)

**Description**: Add session navigation events and wire up navigator tab.

**Acceptance Criteria**:
- [ ] Events added: SESSION_LIST_LOADED, SESSION_SELECTED_FROM_PALETTE
- [ ] Navigator tab subscribes to session events
- [ ] Timeline index updates on session events
- [ ] Test: `pytest tests/tui/test_navigator_events.py` - 4 test cases pass
- [ ] Manual verify: Select session, navigator updates

**Implementation Steps**:
1. Add session events to Events class
2. Add event subscriptions in NavigatorTimeline widget
3. Emit SESSION_LIST_LOADED when session list loaded
4. Emit SESSION_SELECTED_FROM_PALETTE on selection
5. Verify event flow

---

#### Task 4.1: Implement SubagentRegistry
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 3 hours
**Dependencies**: Wave 1 (Settings updated)

**Description**: Registry for subagents with metadata lookup.

**Acceptance Criteria**:
- [ ] SubagentRegistry in `opencode_python/agents/registry.py`
- [ ] register_subagent(agent) method
- [ ] get_subagent(name) method
- [ ] list_subagents() method
- [ ] get_subagent_status(name) method
- [ ] get_last_result(name, session_id, since) method
- [ ] Test: `pytest tests/agents/test_registry.py` - 10 test cases pass
- [ ] Manual verify: Register subagent, look it up

**Implementation Steps**:
1. Create SubagentRegistry class
2. Implement registry storage (in-memory or file)
3. Add register/get/list/status methods
4. Add metadata support (description, capabilities)
5. Implement result tracking

---

#### Task 4.2: Extend AgentManager for Subagent Operations
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 3 hours
**Dependencies**: 4.1 (SubagentRegistry created)

**Description**: Add run_subagent(), rerun_subagent(), cancel_subagent() to AgentManager.

**Acceptance Criteria**:
- [ ] run_subagent(agent_name, params, session_id) implemented
- [ ] rerun_subagent(subagent_name, session_id) implemented (uses last params)
- [ ] cancel_subagent(subagent_name, session_id) implemented
- [ ] Returns SubagentResult with tracking
- [ ] Test: `pytest tests/agents/test_subagent_operations.py` - 8 test cases pass
- [ ] Manual verify: Run subagent, see status, rerun, cancel

**Implementation Steps**:
1. Extend AgentManager class in agents/manager.py
2. Add run_subagent() method with async execution
3. Add rerun_subagent() that fetches last result and re-executes
4. Add cancel_subagent() method
5. Integrate with SubagentRegistry
6. Return SubagentResult objects

---

#### Task 4.3: Create SubagentResult Model
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: None (can parallel with 4.1)

**Description**: Result object for subagent execution with status tracking.

**Acceptance Criteria**:
- [ ] SubagentResult in `opencode_python/agents/models.py`
- [ ] Fields: subagent_name, session_id, status, timestamp, timestamp_finished, output, error, metadata
- [ ] SubagentStatus enum: IDLE, RUNNING, COMPLETED, ERROR, CANCELLED
- [ ] Computed properties: duration_ms, output_preview (first 100 chars)
- [ ] Test: `pytest tests/agents/test_subagent_result.py` - 6 test cases pass
- [ ] Manual verify: Create result, check status fields

**Implementation Steps**:
1. Create SubagentStatus enum
2. Create SubagentResult dataclass
3. Add required fields
4. Add optional fields (error, metadata)
5. Add computed properties (duration_ms, output_preview)
6. Verify with tests

---

#### Task 4.4: Create SubagentDrawer Widget
**Category**: visual-engineering
**Skills**: frontend-ui-ux
**Estimate**: 3 hours
**Dependencies**: 4.1-4.3 (SubagentRegistry, AgentManager extended, SubagentResult created)

**Description**: Drawer tab showing subagent list with status indicators and last result preview.

**Acceptance Criteria**:
- [ ] SubagentDrawer in `opencode_python/tui/widgets/subagent_drawer.py`
- [ ] Shows subagent list with status icons (idle=gray, running=blue, completed=green, error=red)
- [ ] Shows last result preview (first 100 chars)
- [ ] Run button (disabled while running)
- [ ] Rerun button
- [ ] Cancel button
- [ ] Emits DRAWER_SUBAGENT_SELECTED on selection
- [ ] Test: `pytest tests/tui/test_subagent_drawer.py` - 8 test cases pass
- [ ] Manual verify: Open drawer, see subagents, run one

**Implementation Steps**:
1. Create SubagentDrawer widget
2. Implement DataTable for subagent list
3. Add status icon rendering
4. Add action buttons (run, rerun, cancel)
5. Add result preview display
6. Subscribe to subagent status events
7. Integrate with SubagentRegistry

---

#### Task 4.5: Integrate Subagent Events
**Category**: quick
**Skills**: git-master
**Estimate**: 2 hours
**Dependencies**: 4.4 (SubagentDrawer created)

**Description**: Add subagent lifecycle events to event bus and wire up Epic 4 components.

**Acceptance Criteria**:
- [ ] Events added: SUBAGENT_RUN, SUBAGENT_RERUN, SUBAGENT_STATUS_CHANGED, SUBAGENT_RESULT_READY
- [ ] SubagentRegistry emits events on operations
- [ ] AgentManager emits events on execution
- [ ] SubagentDrawer subscribes to status events
- [ ] Test: `pytest tests/core/test_subagent_events.py` - 6 test cases pass
- [ ] Manual verify: Run subagent, see status update in drawer

**Implementation Steps**:
1. Add subagent events to Events class
2. Add event emissions in SubagentRegistry
3. Add event emissions in AgentManager
4. Add event subscriptions in SubagentDrawer
5. Verify event flow

---

### Wave 3: Enhancement Epic (Epic 6)

#### Task 6.1: Implement AuditTrailManager
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 5 hours
**Dependencies**: Wave 2 (all epics for events)

**Description**: Manager for logging and querying audit trail of all user/agent/tool actions.

**Acceptance Criteria**:
- [ ] AuditTrailManager in `opencode_python/observability/audit_trail.py`
- [ ] log_event(event) method
- [ ] query(query) method with filters
- [ ] AuditRecord model with fields: record_id, session_id, timestamp, actor, action_type, action_id, target, outcome, details
- [ ] Storage backend (~/.opencode/audit/)
- [ ] Test: `pytest tests/observability/test_audit_trail.py` - 10 test cases pass
- [ ] Manual verify: Perform action, verify audit record created

**Implementation Steps**:
1. Create AuditRecord model
2. Create AuditTrailQuery model
3. Create AuditTrailManager class
4. Implement async file-based storage in audit directory
5. Implement log_event() with JSON file creation
6. Implement query() with file filtering and aggregation
7. Add indexing for performance

---

#### Task 6.2: Implement ErrorCollector
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 3 hours
**Dependencies**: Wave 2 (all epics for errors)

**Description**: Collect and display errors from all system components.

**Acceptance Criteria**:
- [ ] ErrorCollector in `opencode_python/observability/error_collector.py`
- [ ] collect_error(level, message, context) method
- [ ] get_errors(session_id, filters) method
- [ ] ErrorLevel enum: CRITICAL, ERROR, WARNING
- [ ] Emits DRAWER_ERROR_DISPLAYED events
- [ ] Test: `pytest tests/observability/test_error_collector.py` - 6 test cases pass
- [ ] Manual verify: Error occurs, collected, visible in drawer

**Implementation Steps**:
1. Create ErrorLevel enum
2. Create ErrorCollector class
3. Implement in-memory error storage
4. Add collect_error() method
5. Add get_errors() with filtering
6. Subscribe to error events from all epics
7. Emit DRAWER_ERROR_DISPLAYED events

---

#### Task 6.3: Implement SafetyController
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 4 hours
**Dependencies**: Wave 2 (all epics for safety)

**Description**: Validate and confirm destructive/dangerous commands.

**Acceptance Criteria**:
- [ ] SafetyController in `opencode_python/observability/safety.py`
- [ ] validate_command(command) method returns risk level
- [ ] SafeCommandModel with fields: command, description, affected_paths, risk_level, requires_confirmation, dry_run
- [ ] ConfirmDialog component for user confirmation
- [ ] Emits SAFE_COMMAND_REQUESTED, SAFE_COMMAND_APPROVED events
- [ ] Test: `pytest tests/observability/test_safety.py` - 8 test cases pass
- [ ] Manual verify: Destructive command triggers confirmation dialog

**Implementation Steps**:
1. Create SafeCommandModel
2. Create RiskLevel enum (LOW, MEDIUM, HIGH, CRITICAL)
3. Create SafetyController class
4. Implement validate_command() for risk assessment
5. Create ConfirmationDialog component
6. Integrate with settings (dry_run_enabled, destructive_confirmations)
7. Add event emissions

---

#### Task 6.4: Integrate Observability with Timeline
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: 6.1-6.3 (AuditTrailManager, ErrorCollector, SafetyController created)

**Description**: Extend TimelineManager for observability events (audit trail, errors).

**Acceptance Criteria**:
- [ ] TimelineManager handles audit events
- [ ] TimelineManager handles error events
- [ ] Timeline entries displayed in MessageScreen
- [ ] Filter by error type available
- [ ] Test: `pytest tests/core/test_timeline_observability.py` - 5 test cases pass
- [ ] Manual verify: Audit action visible in timeline

**Implementation Steps**:
1. Extend TimelineManager to handle observability events
2. Add AUDIT_ACTION_LOGGED event handling
3. Add DRAWER_ERROR_DISPLAYED event handling
4. Add event-to-timeline-entry conversion
5. Test with audit/error data
6. Verify filtering works

---

#### Task 6.5: Add Observability Events
**Category**: quick
**Skills**: git-master
**Estimate**: 3 hours
**Dependencies**: 6.4 (Timeline integrated)

**Description**: Add observability events to event bus and wire up Epic 6 components.

**Acceptance Criteria**:
- [ ] Events added: AUDIT_ACTION_LOGGED, DRAWER_ERROR_DISPLAYED, SAFE_COMMAND_REQUESTED, SAFE_COMMAND_APPROVED
- [ ] AuditTrailManager emits events on logging
- [ ] ErrorCollector emits events on collection
- [ ] SafetyController emits events on approval/denial
- [ ] Test: `pytest tests/core/test_observability_events.py` - 6 test cases pass
- [ ] Manual verify: Action logged, audit event visible

**Implementation Steps**:
1. Add observability events to Events class
2. Add event emissions in AuditTrailManager
3. Add event emissions in ErrorCollector
4. Add event emissions in SafetyController
5. Verify event flow

---

### Wave 4: Integration & Polish

#### Task 7.1: Integrate All Epics in TUI App
**Category**: deep
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: Waves 1-3 (all epics implemented)

**Description**: Mount DrawerWidget, update SessionHeader, wire up all event handlers in main app.

**Acceptance Criteria**:
- [ ] DrawerWidget mounted in app.py compose()
- [ ] SessionHeader uses TopBarModel for provider display
- [ ] Command palette includes all new actions
- [ ] Event bus subscriptions registered
- [ ] FocusManager integrated with app focus handling
- [ ] Test: `pytest tests/tui/test_app_integration.py` - 10 test cases pass
- [ ] Manual verify: Start TUI, drawer works, all features accessible

**Implementation Steps**:
1. Update app.py compose() to include DrawerWidget
2. Update SessionHeader to use TopBarModel
3. Add event subscriptions for all epics
4. Integrate FocusManager with app focus
5. Add drawer state loading on session resume
6. Test all integrated features

---

#### Task 7.2: End-to-End Integration Testing
**Category**: deep
**Skills**: python-programmer
**Estimate**: 4 hours
**Dependencies**: 7.1 (All epics integrated)

**Description**: Comprehensive integration tests for cross-epic functionality.

**Acceptance Criteria**:
- [ ] Test drawer toggle doesn't break main timeline
- [ ] Test provider switching updates top bar + timeline
- [ ] Test session selection updates navigator
- [ ] Test subagent execution updates drawer + timeline
- [ ] Test audit trail captures all actions
- [ ] Test error collection and display
- [ ] Test safety controls on destructive commands
- [ ] Test focus transitions across all components
- [ ] All integration tests pass (30+ test cases)

**Implementation Steps**:
1. Create integration test suite
2. Test drawer with existing TUI components
3. Test provider switching end-to-end
4. Test session management with drawer
5. Test subagent lifecycle
6. Test observability features
7. Verify no regressions in existing tests

---

#### Task 7.3: Cross-Epic Event Flow Verification
**Category**: ultrabrain
**Skills**: python-programmer
**Estimate**: 2 hours
**Dependencies**: 7.2 (Integration tests passing)

**Description**: Verify all event-driven flows work correctly across all epics.

**Acceptance Criteria**:
- [ ] Event flow documented
- [ ] All event emissions verified
- [ ] Event subscriptions verified
- [ ] No event loops or cascading issues
- [ ] Test: `pytest tests/core/test_event_flows.py` - 8 test cases pass
- [ ] Manual verify: Trace event flow through system

**Implementation Steps**:
1. Document all event flows
2. Create event flow verification tests
3. Test each event emission triggers expected handlers
4. Test event subscription receives correct data
5. Verify no memory leaks or orphaned events
6. Document event architecture

---

#### Task 7.4: Bug Fixes and Polish
**Category**: unspecified-high
**Skills**: python-programmer
**Estimate**: 4 hours
**Dependencies**: 7.3 (Event flows verified)

**Description**: Fix bugs discovered during integration testing and polish UX.

**Acceptance Criteria**:
- [ ] All integration test bugs fixed
- [ ] UX polish applied (animations, transitions, focus)
- [ ] Performance optimizations applied
- [ ] Code review findings addressed
- [ ] Documentation updated
- [ ] All tests passing (including integration tests)

**Implementation Steps**:
1. Review integration test failures
2. Fix identified bugs
3. Apply UX improvements
4. Optimize performance
5. Update code comments
6. Update documentation
7. Final test suite run

---

## 5. Success Criteria

### Functional Requirements
- [ ] Drawer slides in from right with smooth animation (0.15s)
- [ ] Drawer has 3 working tabs: Todos, Subagents, Navigator
- [ ] Top bar displays provider/account/model with color coding
- [ ] Command palette has all provider/subagent/session actions
- [ ] Subagent registry enables run/rerun/cancel operations
- [ ] Audit trail logs all user/agent/tool actions
- [ ] Errors collected and displayed in drawer
- [ ] Safety controls require confirmation for destructive commands
- [ ] Focus management works correctly across all components
- [ ] All state changes persist across TUI sessions
- [ ] Keyboard navigation works for all features

### Technical Requirements
- [ ] All event emissions properly wired
- [ ] No event loops or cascading issues
- [ ] All tests passing (unit + integration)
- [ ] Code follows existing patterns (Textual, async, Pydantic)
- [ ] Type checking passes (mypy strict)
- [ ] No regressions in existing TUI functionality

### Integration Requirements
- [ ] Drawer doesn't break existing session management
- [ ] Provider switching doesn't break timeline
- [ ] Subagent execution integrates with observability
- [ ] Safety controls work across all epics
- [ ] Focus transitions predictable and consistent

---

## 6. Timeline & Phasing

**Estimated Total**: 72-84 hours

### Phase 1: Foundation (Wave 1) - 8-12 hours
- Week 1: Epic 1 implementation
- Deliverable: Working drawer with 3 tabs, focus management, basic styling

### Phase 2: Content Epics (Wave 2) - 26-42 hours
- Week 2-3: Epic 2, 3, 4 implementation
- Deliverable: Provider display, session list, subagent system
- Can parallelize within each epic

### Phase 3: Enhancement (Wave 3) - 22 hours
- Week 4: Epic 6 implementation
- Deliverable: Observability and safety systems
- Can parallelize within epic

### Phase 4: Integration & Polish (Wave 4) - 12-16 hours
- Week 5: Integration testing, bug fixes
- Deliverable: Fully functional system with all epics working together
- Full test coverage

### Phase 5: Testing & Documentation - 8-12 hours
- Week 6: Final testing, documentation, deployment
- Deliverable: Production-ready Drawer-First UX system

**Total Timeline**: 5-6 weeks for complete implementation

---

## 7. Notes

### Cross-Epic Integration Strategy
- Implement in current worktree (tui) following merge plan order
- Epic 1 first (foundation), then Epics 2, 3, 4 (can parallelize), then Epic 6
- Epic 5 (Themes & UX) handled inline as basic styling in Epic 1
- All event bus additions coordinated to avoid conflicts
- Settings additions additive only

### Testing Strategy
- TDD approach: Write tests first, implement, refactor
- Unit tests for each component/widget
- Integration tests for cross-epic functionality
- End-to-end testing in Wave 4
- Manual verification with TUI interaction testing

### Risk Mitigation
- Start with Epic 1 (foundation) to reduce merge conflicts
- Run integration tests continuously to catch issues early
- Document all event flows for debugging
- Keep changes small and testable
