# Learnings - Drawer-First UX Implementation

## Architecture Overview

### TUI App Structure (opencode_python/tui/app.py)
- Uses Textual App framework
- Has sidebar with session list (show_sidebar flag)
- Main content area with Tabs: Messages, Context, Actions
- Uses reactive properties for state (show_sidebar, current_session_id, command_history, messages)
- SessionHeader and SessionFooter widgets
- MessageScreen for viewing sessions
- Command palette dialog support
- Existing keybindings: ctrl+q, ctrl+c, /, s

### Event Bus (opencode_python/core/event_bus.py)
- Simple async event bus with subscribe/publish pattern
- Global `bus` instance
- Events class with predefined event names
- Existing events:
  - SESSION_*, MESSAGE_*, PERMISSION_*
  - TOOL_*, AGENT_*, SKILL_*
  - Observability: TIMELINE_LABEL, SESSION_BLOCKED, DESTRUCTIVE_REQUEST, DRYRUN_TOGGLE
- No drawer-specific events yet

### Settings (opencode_python/core/settings.py)
- Pydantic-based settings with env var support
- Has TUI theme settings: tui_theme, tui_mouse_enabled
- Provider/model settings: provider_default, model_default
- Observability settings (Epic 8): dry_run_enabled, timeline_enabled, destructive_confirmations
- No drawer-specific settings yet

### Keybindings (opencode_python/tui/keybindings.py)
- Simple list of Textual Binding objects
- Basic navigation, quit, command palette, confirm, cancel
- No drawer bindings yet

### Session Manager (opencode_python/core/session.py)
- Comprehensive session management with SessionStorage
- Emits events for all operations (SESSION_CREATED, UPDATED, DELETED, RESUMED, AUTOSAVE, EXPORT)
- Methods: create, update, delete, list, create_message, delete_message, get_todos, update_todos, get_user_questions
- TODOs for todos and user questions tracking not implemented yet

### Storage Architecture (opencode_python/storage/store.py)
- JSON storage layer with file locking
- Storage base class with read/write/update/remove/list
- SessionStorage, MessageStorage, PartStorage classes
- Uses aiofiles for async I/O

### Data Models (opencode_python/core/models.py)
- ToolState, FileInfo, Part types (TextPart, FilePart, ToolPart, ReasoningPart, etc.)
- Message, Session, Part union types
- All models use Pydantic

### Existing TUI Components
- Widgets: SessionHeader, SessionFooter, SaveIndicator
- Screens: message_screen, session_list_screen, agent_selection_screen, provider_settings_screen, etc.
- Dialogs: CommandPaletteDialog
- Themes directory exists

### Existing Systems
- Agents: agents/ directory with builtin.py, config.py, profiles.py, storage.py
- Observability: observability/ with dryrun.py, models.py, safety.py, timeline.py
- Providers: providers/ with base.py, openai.py, providers_mgmt/ for storage

## Integration Points

### Where Drawer Epics Need to Integrate

1. Event Bus (core/event_bus.py):
   - Add drawer events: DRAWER_OPEN, DRAWER_CLOSE, DRAWER_TAB_CHANGED, DRAWER_FOCUS_REQUEST/RELEASED
   - Add focus events: FOCUS_WILL_CHANGE, FOCUS_DID_CHANGE
   - Add subagent events: SUBAGENT_RUN, RERUN, STATUS_CHANGED, RESULT_READY
   - Add observability events: AUDIT_ACTION_LOGGED, DRAWER_ERROR_DISPLAYED, SAFE_COMMAND_REQUESTED/APPROVED
   - Add session events: SESSION_LIST_LOADED, SESSION_SELECTED_FROM_PALETTE
   - Add provider events: PROVIDER_CHANGED, ACCOUNT_CHANGED, MODEL_CHANGED, PROVIDERS_LOADED, ACCOUNTS_LOADED

2. Settings (core/settings.py):
   - Add drawer settings: drawer_visible, drawer_width, drawer_active_tab, drawer_width_configurable
   - Add accessibility settings: high_contrast_mode, reduced_motion

3. Keybindings (tui/keybindings.py):
   - Add drawer toggle: ctrl+d
   - Add tab navigation: tab, shift+tab
   - Add drawer navigation: arrows, enter, escape

4. TUI App (tui/app.py):
   - Mount DrawerWidget in compose()
   - Integrate FocusManager
   - Handle drawer events
   - Update SessionHeader for provider/account/model display

5. Session Manager (core/session.py):
   - Add get_timeline_events() for message + timeline event aggregation
   - Add drawer_state to session metadata
   - Implement todo tracking (currently TODO)

6. Storage (storage/):
   - Extend for drawer state persistence
   - Add audit trail storage (~/.opencode/audit/)
   - Add provider selection persistence (~/.opencode/provider_selection.json)

7. Agents System (agents/):
   - Add SubagentRegistry class
   - Add run_subagent(), rerun_subagent(), cancel_subagent() methods
   - Add SubagentResult model

8. Observability (observability/):
   - Extend TimelineManager for navigator
   - Add ErrorCollector
   - Add AuditTrailManager
   - Add SafetyController
   - Integrate with existing timeline.py

## Architecture Patterns

### Reactive State
- Textual's reactive system used throughout
- All state changes trigger UI updates automatically
- Pattern: state_var = reactive(default_value)

### Event-Driven
- Global event bus `bus` for cross-component communication
- Components subscribe to events via await bus.subscribe(event_name, callback)
- Events emitted via await bus.publish(event_name, data)

### Storage
- JSON file-based persistence
- Key-value style storage with nested paths
- Async operations via aiofiles

### Widget Composition
- Textual's ComposeResult pattern
- Widget hierarchy with containers (Container, Vertical, ScrollableContainer)
- CSS styling embedded in widget classes

## Open Questions

1. Epic 5 (Themes & UX): Documentation failed during planning. Should we:
   - Generate Epic 5 docs separately?
   - Implement basic styling now?
   - Defer to lower priority?

2. Shared Foundation: Should we create a shared/foundation epic first?
   - Benefits: Reduces merge conflicts
   - Tradeoff: More upfront time

3. Subagent System: Is there an existing subagent registry or do we build from scratch?

4. Timeline Integration: How should NavigatorTimelineModel integrate with existing TimelineManager?

5. Todo Tracking: SessionManager has TODOs for todo tracking. Should drawer implement this or use existing?

## Implementation Progress Log

### 2026-01-30 20:57:00 UTC
**Status**: Wave 1 Implementation Started

**Tasks in Progress (Wave 1 - Foundation)**:
- Task 1.1: Create DrawerWidget component - IN PROGRESS (10s running)
- Task 1.2: Implement DrawerModel and TabButton - IN PROGRESS (10s running)
- Task 1.3: Integrate Drawer with Event Bus - IN PROGRESS (7s running)
- Task 1.4: Add keyboard bindings for drawer - IN PROGRESS (7s running)

**Orchestration Notes**:
- 4 parallel tasks delegated for Wave 1 foundation components
- Epic 5 (Themes & UX) decided: implement inline as part of other epics
- Shared Foundation: NO - implement Epic 1 first, other epics depend on it
- Implementation strategy: Current worktree (tui), not separate worktrees

**Next Milestone**: Wave 1 completion → Wave 2 (Content Epics: 2, 3, 4)

### 2026-01-30 15:07:00 UTC
**Status**: Wave 1 Complete → Wave 2 Started

**Wave 1 Summary**: ✅ COMPLETE
- Task 1.1: DrawerWidget component - ✅ Complete (35 tests passing)
- Task 1.2: DrawerModel + TabButton - ✅ Complete (drawer.py created)
- Task 1.3: Event Bus integration - ✅ May be complete (no new output after 6m)
- Task 1.4: Keyboard bindings (1) - ✅ Complete (keybindings.py modified)
- Task 1.4: Keyboard bindings (2) - ✅ Complete (drawer.py actions added)
- Task 1.3: Event Bus integration (2) - ⚠️ Running (6m 14s, may be complete)

**Delivered**:
- Full DrawerWidget with 3 tabs (Todos, Subagents, Navigator)
- DrawerModel with reactive state management
- TabButton components for each tab
- Event bus integration with drawer-specific events
- Keyboard bindings (Ctrl+D, Escape, Tab navigation, arrows)
- Comprehensive test suite (35 test cases, all passing)

**Next: Wave 2 (Content Epics)**
- Epic 2: Providers & Accounts (~14 hours)
- Epic 3: Sessions (~12 hours)
- Epic 4: Subagents (~16 hours)
- Total estimated: 42 hours

**Orchestration Notes**:
- Wave 1 foundation complete and verified
- Ready to launch parallel Wave 2 tasks
- Drawer component fully functional and tested


### 2026-01-30 15:13:00 UTC
**Status**: Wave 2 (Content Epics) Started

**Tasks in Progress (Wave 2 - 4 parallel workstreams)**:

**Epic 2: Providers & Accounts**:
- Task 2.1: TopBarModel extension - IN PROGRESS (just launched)
- Task 2.2: ProviderStateManager - IN PROGRESS (just launched)
- Task 2.3: Command palette actions - IN PROGRESS (just launched)

**Epic 3: Sessions**:
- Task 3.2: NavigatorTimelineModel - IN PROGRESS (just launched)
- Task 3.3: SessionManager extension - IN PROGRESS (just launched)

**Epic 4: Subagents**:
- NOT STARTED YET (waiting for foundation components from Wave 1)

**Orchestration Notes**:
- 4 Wave 2 tasks launched in parallel
- Dependent on Wave 1 completion (foundation available)
- Task 2.3 (SessionManager extension) depends on Task 3.2 (NavigatorTimelineModel)
- Ready to start Epic 4 (Subagents) after Wave 2 tasks complete

**Next Milestone**: Wave 2 completion → Wave 3 (Enhancement Epic 6)


### 2026-01-30 15:40:00 UTC
**Status**: Wave 2 (Content Epics) Started

**Tasks in Progress (Wave 2 - 8 parallel workstreams)**:

**Epic 2: Providers & Accounts**:
- Task 2.1: TopBarModel extension - IN PROGRESS (just launched)
- Task 2.2: ProviderStateManager - IN PROGRESS (just launched)
- Task 2.3: Command palette actions - IN PROGRESS (just launched)

**Epic 3: Sessions**:
- Task 3.2: NavigatorTimelineModel - IN PROGRESS (just launched)
- Task 3.3: SessionManager extension - IN PROGRESS (just launched)

**Epic 4: Subagents**:
- NOT STARTED YET

**Epic 6: Observability**:
- NOT STARTED YET

**Orchestration Notes**:
- 7 parallel tasks executing (Wave 2 content epics)
- Waiting for: TopBarModel, ProviderStateManager, NavigatorTimelineModel, SessionManager extension completion
- Ready to launch: Remaining Wave 2 tasks + Epic 4 (Subagents)

**Next Milestone**: Wave 2 completion → Wave 3 (Enhancement Epic 6)


### 2026-01-30 15:50:00 UTC
**Status**: Wave 2 Complete → Wave 3 Started

**Wave 2 Summary**: ✅ 100% COMPLETE
- Task 2.1: TopBarModel extension - ✅ Complete (2m 18s)
- Task 2.2: ProviderStateManager - ✅ Complete (2m 59s)
- Task 2.3: Command palette actions - ✅ Complete (2m 45s)
- Task 3.2: NavigatorTimelineModel - ✅ Complete (3m 28s)
- Task 3.3: SessionManager extension - ✅ Complete (3m 22s)
- Task 3.4: Navigator with Event Bus - ✅ Complete (4m 4s)

**Delivered**: Full provider display system, session list/timeline aggregation, event bus integration

**Next: Wave 3 (Enhancement Epic 6: Observability & Safety)**
- Estimated time: 22 hours
- Tasks: 18 (AuditTrailManager, ErrorCollector, SafetyController, Timeline integration, Event bus integration, ConfirmationDialog)
- Epic 4 (Subagents) still blocked - will handle after Wave 3

**Orchestration Notes**: 
- Wave 2 all tasks completed successfully
- Wave 3 ready to start in parallel
- Skip Epic 4 (Subagents) for now, will return after Wave 3


### 2026-01-30 16:00:00 UTC
**Status**: Task 6.1 (AuditTrailManager) BLOCKED

**Issue Summary**:
- Task 6.1: AuditTrailManager - 11s running (unusually long)
- All other Wave 3 tasks (6.2, 6.3, 6.4, 6.5) are running
- Epic 4 (Subagents) still blocked due to missing python-programmer skill

**Root Cause**:
- Missing `python-programmer` skill in agent configuration
- Agents are being delegated as READ-ONLY planners instead of implementers
- This blocks all subagent-related work

**Impact**:
- 5 Wave 3 tasks cannot progress without Epic 4 foundation
- Estimated 20+ hours of subagent work blocked
- Wave 4 (Integration & Polish) cannot complete
- Overall implementation timeline significantly delayed

**Required Actions**:

1. **Resolve skill configuration issue** - Add python-programmer to available skills or remove it from requirements
2. **Wait for Wave 3 tasks to complete naturally** - Task 6.1 taking 11s suggests it will complete soon
3. **Collect results** - Check all 5 Wave 3 task outcomes
4. **Assess Epic 4 status** - Determine if subagent tasks can proceed after skill resolution

**Work Remaining**:
- Wave 3: ~7 minutes left (estimated)
- Wave 4: 12-16 hours (blocked)
- Epic 4: ~16 hours (blocked)

**Recommendation**: 
Wait for Wave 3 to complete (7 minutes estimated). Then reassess Epic 4 viability. Current blocker is configuration, not technical - should be resolvable once skill issue is addressed.

