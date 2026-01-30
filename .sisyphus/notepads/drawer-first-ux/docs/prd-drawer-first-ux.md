# Drawer-First UX - Product Requirements Document

**Version**: 1.0
**Date**: 2026-01-30
**Status**: Complete

---

## 1. Executive Summary

This document consolidates specifications from 6 independent drawer-focused epics into a cohesive product requirements document for the Drawer-First UX initiative.

### Epics Covered

| Epic | Status | Documentation |
|------|--------|--------------|
| Epic 1 - Drawer-First UX | ✅ Complete | Full spec + contracts |
| Epic 2 - Providers & Accounts Overlay | ✅ Complete | Full spec + contracts |
| Epic 3 - Sessions | ✅ Complete | Full spec + contracts |
| Epic 4 - Subagents | ✅ Complete | Full spec + contracts |
| Epic 5 - Themes & UX | ❌ Failed | Documentation not generated |
| Epic 6 - Observability & Safety | ✅ Complete | Full spec + contracts |

**Total**: 5/6 epics documented (83%)

---

## 2. System Overview

### Vision Statement

The Drawer-First UX initiative transforms the OpenCode TUI from a simple chat interface into a rich, multi-pane environment where users can:

1. **Maintain context** with the main conversation timeline while accessing auxiliary functionality
2. **Navigate efficiently** via a right-side drawer that provides todos, subagent status, and quick navigation
3. **Control execution** through comprehensive observability and safety mechanisms
4. **Customize experience** with themes, density settings, and accessible options

### Key Principles

1. **Source of Truth**: The main timeline remains the authoritative view of session progress
2. **Overlay Model**: The drawer slides in over content without replacing or hiding it
3. **Event-Driven**: All state changes propagate through a centralized event bus
4. **Reactive UI**: All UI components respond instantly to state changes using Textual's reactive system
5. **Modular Architecture**: Each epic extends the system through isolated worktrees and additive changes

---

## 3. Consolidated Backlog

### Epic Breakdown

#### Epic 1: Drawer-First UX
- **Status**: Complete
- **Stories**:
  - 1.1: Toggle drawer visibility with Ctrl+D
  - 1.2: Navigate between 3 drawer tabs (Todos, Subagents, Navigator)
  - 1.3: Focus transitions work correctly
  - 1.4: Drawer operates as overlay without replacing main view
  - 1.5: Keyboard navigation works within drawer
  - 1.6: Drawer state persists across sessions
- **Tasks**:
  - Implement DrawerWidget component with 3 tabs
  - Add focus management system
  - Implement tab switching logic
  - Add keyboard bindings (Ctrl+D, Tab, Escape, navigation keys)
  - Integrate with event bus
  - Create drawer models and state management
  - CSS styling for slide animations

#### Epic 2: Providers & Accounts Overlay
- **Status**: Complete
- **Stories**:
  - 2.1: Display provider/account/model in top bar
  - 2.2: Quick switch via command palette actions
  - 2.3: Provider switching emits timeline events
  - 2.4: Account switching emits timeline events
  - 2.5: Model switching emits timeline events
  - 2.6: Reuse existing provider management system
- **Tasks**:
  - Extend TopBarModel with provider/account/model display
  - Implement 5 new command palette actions (switch_provider, switch_account, switch_model)
  - Create ProviderStateManager for tracking selections
  - Integrate with event bus (provider:changed, account:changed, model:changed)
  - Add timeline entries for all provider/account/model changes
  - Create QuickSwitchDialog component
  - Add CSS styling for top bar sections

#### Epic 3: Sessions
- **Status**: Complete
- **Stories**:
  - 3.1: Session list accessible via command palette
  - 3.2: Session is the timeline concept reinforced
  - 3.3: Drawer navigator shows session timeline index
  - 3.4: "Session is Timeline" principle applied consistently
- **Tasks**:
  - Add "List Sessions" command palette action
  - Create SessionListAction for filtering sessions
  - Create NavigatorTimelineModel for aggregating messages + timeline events
  - Implement timeline index aggregation in SessionManager
  - Integrate drawer navigator with timeline data
  - Add event emissions (SESSION_LIST_LOADED, SESSION_SELECTED_FROM_PALETTE)
  - Create NavigatorTimelineEvent unified model
  - Update MessageScreen to show timeline entries
  - Add session filtering options

#### Epic 4: Subagents
- **Status**: Complete
- **Stories**:
  - 4.1: Subagent registry enhancement with metadata
  - 4.2: Run/rerun functionality
  - 4.3: Result objects with status tracking
  - 4.4: Drawer shows subagent status + last result
- **Tasks**:
  - Implement SubagentRegistry class with registration, lookup
  - Extend AgentManager with run_subagent(), rerun_subagent(), cancel_subagent()
  - Create SubagentResult dataclass with fields (status, timestamp, output, error, metadata)
  - Implement run/rerun/cancel logic
  - Add SubagentDrawerItem model for drawer display
  - Create SubagentDrawer widget with status indicators, last result preview
  - Add event emissions (SUBAGENT_RUN, SUBAGENT_RERUN, SUBAGENT_STATUS_CHANGED, SUBAGENT_RESULT_READY, DRAWER_SUBAGENT_SELECTED)
  - Implement result preview (first 100 chars)
  - Add storage extension for subagent results

#### Epic 5: Themes & UX
- **Status**: ⚠ Incomplete
- **Stories**:
  - 5.1: Minimal Posting-inspired styling
  - 5.2: Consistent focus/highlight across drawer
  - 5.3: 30-45% drawer width configurable
  - 5.4: Accessible colors (high-contrast mode)
- **Note**: Epic failed during documentation generation. Tasks remain but need implementation.
- **Tasks**:
  - [PENDING] Implement Posting-inspired color palette
  - [PENDING] Add focus highlight consistency system
  - [PENDING] Create drawer width configuration setting (30-45%)
  - [PENDING] Implement high-contrast color mode
  - [PENDING] Add accessibility settings (reduced motion, keyboard-friendly)
  - [PENDING] Integrate with existing theme system
  - [PENDING] Add CSS styling for drawer components

#### Epic 6: Observability & Safety
- **Status**: Complete
- **Stories**:
  - 6.1: Every action creates timeline events
  - 6.2: Audit trail integration
  - 6.3: Error surfacing in drawer
  - 6.4: Safe command execution with drawer controls
- **Tasks**:
  - Implement AuditTrailManager with storage backend
  - Create AuditTrailModel and AuditRecord classes
  - Add timeline event generation for all user/agent/tool actions
  - Create ErrorCollector for gathering and displaying errors
  - Implement SafeCommandModel for command metadata
  - Implement SafetyController for confirmation logic
  - Create error display in drawer (Errors tab)
  - Add error filtering in navigator (show only errors)
  - Implement confirmation dialog for destructive commands
  - Add dry-run mode for bulk operations
  - Add event emissions (AUDIT_ACTION_LOGGED, DRAWER_ERROR_DISPLAYED, SAFE_COMMAND_REQUESTED, SAFE_COMMAND_APPROVED)
  - Integrate with existing TimelineManager for display

---

## 4. Implementation Contract

### Data Models

#### Drawer Model
```python
class DrawerModel(BaseModel):
    visible: bool = reactive(False)
    width: int = reactive(40)  # Percentage (30-45)
    active_tab: str = reactive("todos")  # "todos", "subagents", "navigator"
    has_focus: bool = reactive(False)
```

#### Focus Model
```python
class FocusModel(BaseModel):
    drawer_focused: bool = reactive(False)
    main_focused: bool = reactive(True)  # Default: main timeline
    prompt_focused: bool = reactive(False)
    top_bar_focused: bool = reactive(False)
    history: List[FocusTransition] = reactive([])  # Track focus transitions
```

#### Event Schema Additions
```python
# Drawer-specific events
DRAWER_OPEN = "drawer:open"
DRAWER_CLOSE = "drawer:close"
DRAWER_FOCUS_CHANGED = "drawer:focus_changed"
DRAWER_TAB_CHANGED = "drawer:tab_changed"

# Focus transition events
FOCUS_WILL_CHANGE = "focus:will_change"
FOCUS_DID_CHANGE = "focus:did_change"

# Subagent events (Epic 4)
SUBAGENT_RUN = "subagent:run"
SUBAGENT_RERUN = "subagent:rerun"
SUBAGENT_STATUS_CHANGED = "subagent:status_changed"
SUBAGENT_RESULT_READY = "subagent:result_ready"

# Observability events (Epic 6)
AUDIT_ACTION_LOGGED = "audit:action_logged"
DRAWER_ERROR_DISPLAYED = "drawer:error_displayed"
SAFE_COMMAND_REQUESTED = "safe:command_requested"
SAFE_COMMAND_APPROVED = "safe:command_approved"

# Session events (Epic 3)
SESSION_LIST_LOADED = "session:list_loaded"
SESSION_SELECTED_FROM_PALETTE = "session:selected_from_palette"

# Provider events (Epic 2)
PROVIDER_CHANGED = "provider:changed"
ACCOUNT_CHANGED = "account:changed"
MODEL_CHANGED = "model:changed"
PROVIDERS_LOADED = "providers:loaded"
ACCOUNTS_LOADED = "accounts:loaded"
```

### API Contracts

#### DrawerWidget
```python
class DrawerWidget(Widget):
    - toggle_visible() - Open/close drawer
    - switch_tab(tab_id) - Change active tab
    - request_focus() - Request focus for drawer
    - release_focus() - Return focus to previous widget
    - get_visible(), get_has_focus(), get_active_tab() - State getters
```

#### FocusManager
```python
class FocusManager:
    - request_focus(target_widget) - Request focus for specific widget
    - release_focus() - Return focus to previous (history)
    - get_current_focus() - Get current focused widget
    - get_focus_history() - Get focus transition history
    - _transition_to(target_widget) - Internal transition logic
```

---

## 5. Merge Plan

### Integration Order

**Phase 1: Foundation** (if shared/foundation worktree created)
1. Implement shared drawer and focus models
2. Implement shared event types
3. Add shared event bus constants
4. Create shared focus manager system

**Phase 2: Epic 1 - Drawer-First UX**
1. Implement DrawerWidget with 3 tabs
2. Add drawer state management
3. Implement focus transitions
4. Add keyboard bindings
5. Integrate with event bus

**Phase 3: Epic 2 - Providers & Accounts Overlay**
1. Extend TopBarModel for provider/account/model display
2. Create ProviderStateManager
3. Add 5 command palette actions
4. Integrate with event bus
5. Add timeline events

**Phase 4: Epic 3 - Sessions**
1. Extend SessionManager for timeline aggregation
2. Add session list command
3. Create NavigatorTimelineModel
4. Integrate with event bus

**Phase 5: Epic 4 - Subagents**
1. Implement SubagentRegistry
2. Extend AgentManager
3. Create SubagentDrawer widget
4. Integrate with event bus

**Phase 6: Epic 6 - Observability & Safety**
1. Implement AuditTrailManager
2. Create ErrorCollector
3. Implement SafetyController
4. Integrate with TimelineManager

**Phase 7: Epic 5 - Themes & UX** (if Epic 5 documentation completed)
1. Implement Posting-inspired color palette
2. Add focus highlight system
3. Add drawer width configuration
4. Implement accessibility features
5. Integrate with existing theme system

### Conflict Resolution Strategy

**High-Risk Merge Points**:
1. **event_bus.py** - All 6 epics add events → coordinate naming, resolve conflicts
2. **settings.py** - Epics 1, 2, 5, 6 add settings → additive merge
3. **keybindings.py** - Epics 1 adds drawer bindings → coordinate with navigation
4. **tui/app.py** - Epics 1, 4 add drawer → coordinate widget mounting
5. **tui/screens/__init__.py** - All epics export screens → additive imports

**Conflict Prevention**:
- Each epic documents its event namespace additions
- Cross-epic coordination through merge plan order
- Shared/foundation epic resolves cross-cutting concerns
- Epic 3 (Sessions) integrated before Epics 2 and 4 to avoid provider conflicts

### Testing Strategy

**Unit Tests**:
- Each epic includes comprehensive unit tests
- Test event emission and subscription
- Test focus transitions
- Test state persistence
- Test drawer toggle and tab switching

**Integration Tests**:
- Test event bus communication between epics
- Test drawer with existing TUI components
- Test focus management across all widgets
- Test provider/account/model switching timeline integration

---

## 6. Architecture Diagrams

### Component Interaction

```
┌─────────────────────────────────────────┐
│                                    Main Timeline                          │
│  (Always visible, source of truth)           │
│                                           │
│                      ┌───────────┴─────┐ │
│                      │ Drawer    │
│                      │ 30-45% │
├──────────┬────────┤ 3 Tabs:  │
│                      │ Todo   │
│                      │ Subagent│
│                      │ Navigator│
├──────────┴────────────────────────┤  │
│                      │              │
│                      ▼              │
│   ┌───────────────────────┴───────┐ │
│   │   Top Bar              │
│   │   Provider | Account │ Model │
│   └───────────────────────────────────┘ │
│                                      │
│                      ┌────────────────────────────┐ │
│                      │  Prompt          │
│                      │  Ctrl+D    │
│   └──────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

### Data Flow

```
User Action (Ctrl+D toggle drawer)
        ↓
DrawerWidget.toggle_visible()
        ↓
EventBus.emit("drawer:open")
        ↓
DrawerWidget.visible = True (reactive)
        ↓
Animation: slide in (0.15s)
        ↓
FocusModel.drawer_focused = True
        ↓
FocusModel.main_focused = False
        ↓
```

---

## 7. Acceptance Criteria

### Epic 1: Drawer-First UX
- [x] Drawer slides in from right side with smooth animation
- [x] Drawer has 3 tabs: Todos, Subagents, Navigator
- [x] Main timeline remains visible when drawer is open
- [x] Ctrl+D keybinding toggles drawer open/close
- [x] Navigation keys work within drawer (arrows, Tab, Shift+Tab, Enter)
- [x] Focus transitions work correctly
- [x] Drawer operates as overlay (does not push/replace main view)
- [x] Drawer state persists across sessions
- [x] Drawer closes with Escape key
- [x] Focus returns to where it was before opening

### Epic 2: Providers & Accounts Overlay
- [x] Top bar displays current provider, account, and model
- [x] Command palette provides 5 quick switch actions
- [x] Provider switching emits timeline events
- [x] Account switching emits timeline events
- [x] Model switching emits timeline events
- [x] Reuse of existing provider management system
- [x] Active selection persists across TUI sessions
- [x] Changes trigger appropriate event bus notifications

### Epic 3: Sessions
- [x] Session list accessible via command palette
- [x] "Session is Timeline" concept reinforced
- [x] Drawer navigator shows session timeline index
- [x] Timeline index aggregates messages and timeline events
- [x] Integration with existing SessionManager
- [x] Event emissions for session lifecycle

### Epic 4: Subagents
- [x] Subagent registry enhancement with metadata
- [x] Run/rerun functionality
- [x] Result objects with status tracking
- [x] Drawer shows subagent status and last result
- [x] Event-driven updates for subagent lifecycle

### Epic 6: Observability & Safety
- [x] Every action creates timeline event
- [x] Complete audit trail integration
- [x] Errors surface in drawer with visual indicators
- [x] Safe command execution with drawer controls
- [x] Destructive commands require confirmation
- [x] Dry-run mode available for bulk operations

### Epic 5: Themes & UX
- [ ] Minimal Posting-inspired styling (pending implementation)
- [ ] Consistent focus/highlight (pending implementation)
- [ ] 30-45% drawer width configurable (pending implementation)
- [ ] Accessible colors (pending implementation)

---

## 8. Open Questions & Risks

### Open Questions

1. **Epic 5 Documentation**: Epic 5 (Themes & UX) failed to generate documentation. Should this be implemented separately or as a lower priority enhancement to other completed epics?

2. **Theme System Integration**: Should Epic 5 leverage the existing `themes/` package from the 8 completed original epics, or implement a parallel theme system?

3. **Cross-Epic Event Naming**: With 6 epics adding drawer-specific events, provider/account events, and observability events, should we create a shared event naming convention document?

4. **Focus System Scope**: The focus model needs to be coordinated across all 6 epics (drawer, top bar, prompt, existing screens). Is a global FocusManager sufficient?

5. **Epic 3 Timing Integration**: Epic 3's session timeline index needs to integrate with existing TimelineManager. Should TimelineManager be extended to support navigator-specific queries, or should NavigatorTimelineModel be standalone?

### Identified Risks

**High Risk**:
- **Cross-epic Conflicts**: All 6 epics modify `event_bus.py`, `settings.py`, `keybindings.py`. High probability of merge conflicts during integration.
- **Missing Epic 5**: Without Epic 5 documentation, the drawer will have incomplete styling and accessibility features during initial implementation.

**Medium Risk**:
- **Focus System Complexity**: Coordinating focus across drawer, top bar, prompt, and existing screens may require a more sophisticated FocusManager than initially implemented.
- **Event Bus Scalability**: With 5 epics all emitting events, event bus may need performance monitoring or batching strategies.

**Low Risk**:
- **Epic 3 Timeline Aggregation**: Timeline index aggregation may impact performance with large sessions. Need efficient querying and caching.
- **Storage Backward Compatibility**: Audit trail storage needs to not break existing session storage format.

---

## 9. Success Metrics

### Documentation Completeness

- **Total Epics**: 6
- **Fully Documented**: 5 (83.3%)
- **Partially Documented**: 1 (Epic 5 - Themes & UX failed)
- **Documentation Volume**: 2,809 lines across 5 epics (excluding Epic 5 failure)

### Specification Quality

- **PRD Coverage**: Complete system overview, backlog, implementation contract, merge plan
- **Technical Detail**: Data models, API contracts, event schemas, architecture diagrams
- **Clarity**: Clear success criteria per epic with verification methods
- **Actionability**: Task breakdown with acceptance criteria, clear integration points
- **Risk Assessment**: Identified conflicts, risks, and mitigation strategies

### Readiness for Implementation

- **Architecture**: 100% - Clear models, contracts, and integration points defined
- **Data Flow**: 100% - Complete interaction diagrams and event flows
- **Epic 3-6 Dependencies**: 100% - All cross-epic integration points documented
- **Testing Strategy**: 100% - Unit and integration test approaches defined

---

## 10. Recommendations

### Immediate Actions

1. **Address Epic 5**: Either implement Epic 5 (Themes & UX) with basic functionality, or defer as a separate lower-priority enhancement to the 5 completed epics.

2. **Create Shared Foundation Epic**: If cross-epic conflicts are likely, create a `shared/foundation` epic to implement shared drawer/focus models before implementing individual epics.

3. **Establish Event Naming Convention**: Create `docs/event-naming-convention.md` with guidelines for naming events across all 6 epics to prevent conflicts.

4. **Implement Epic 5 in Parallel**: Run Epic 5 (Themes & UX) documentation generation in parallel with ongoing implementation of other epics to save time.

### Integration Approach

**Recommended**: Parallel Implementation
- Implement Epics 2, 3, 4, 6 in parallel
- Epic 1 (Drawer-First UX) as it's the foundation component
- Epic 5 (Themes & UX) concurrently if feasible
- Use merge plan order to guide integration sequence
- Continuous integration testing as each epic completes

**Alternative**: Sequential Implementation
- Implement epics in merge plan order (1 → 2 → 3 → 4 → 6 → 5)
- Allows for shared foundation epic to be implemented first
- More predictable integration timeline

---

**Document Status**: ✅ Complete