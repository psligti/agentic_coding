# Drawer-First UX - Implementation Contract

**Version**: 1.0
**Date**: 2026-01-30
**Status**: Complete

---

## 1. Data Models

### Drawer Model
```python
class DrawerModel(BaseModel):
    visible: bool = reactive(False)
    width: int = reactive(40)  # Percentage (30-45)
    active_tab: str = reactive("todos")  # "todos", "subagents", "navigator"
    has_focus: bool = reactive(False)
```

### Focus Model
```python
class FocusModel(BaseModel):
    drawer_focused: bool = reactive(False)
    main_focused: bool = reactive(True)  # Default: main timeline
    prompt_focused: bool = reactive(False)
    top_bar_focused: bool = reactive(False)
    history: List[FocusTransition] = reactive([])  # Track focus transitions
```

### Tab Models
```python
class TabModel(BaseModel):
    id: str = "todos" | "subagents" | "navigator"
    label: str = "Todos" | "Subagents" | "Navigator"
    icon: str = "📋" | "🤖" | "🧭"
```

### Subagent Result Model
```python
class SubagentResult(BaseModel):
    subagent_name: str
    session_id: str
    status: SubagentStatus  # IDLE, RUNNING, COMPLETED, ERROR, CANCELLED
    timestamp: float  # Start time
    timestamp_finished: Optional[float]  # End time
    output: str = ""  # Execution output
    error: Optional[str] = None  # Error message
    metadata: Dict[str, Any] = field(default_factory=dict)  # Custom properties
```

### Audit Trail Model
```python
class AuditRecord(BaseModel):
    record_id: str  # UUID
    session_id: str  # Session UUID
    timestamp: str  # ISO 8601
    actor: str  # "user" | "agent:coder" | "agent:reviewer"
    action_type: str  # "command" | "file_edit" | "tool_call" | etc.
    action_id: str  # Command ID or UUID
    target: str  # File path, API endpoint, etc.
    outcome: str  # "success" | "failed" | "cancelled"
    details: Dict[str, Any]  # Additional context
```

### Safe Command Model
```python
class SafeCommandModel(BaseModel):
    command: str  # Human-readable command name
    description: str  # What the command does
    affected_paths: List[str]  # Files/paths affected
    risk_level: CommandRisk  # LOW, MEDIUM, HIGH, CRITICAL
    requires_confirmation: bool = True if needs confirmation
    dry_run: bool = False  # Simulate without executing
```

---

## 2. Event Schema

### Drawer Events
```python
# Drawer visibility and interaction
DRAWER_OPEN = "drawer:open"
DRAWER_CLOSE = "drawer:close"
DRAWER_TAB_CHANGED = "drawer:tab_changed"
DRAWER_FOCUS_REQUEST = "drawer:focus_requested"
DRAWER_FOCUS_RELEASED = "drawer:focus_released"

# Focus transitions
FOCUS_WILL_CHANGE = "focus:will_change"
FOCUS_DID_CHANGE = "focus:did_change"
```

### Subagent Events
```python
# Subagent lifecycle events
SUBAGENT_RUN = "subagent:run"
SUBAGENT_RERUN = "subagent:rerun"
SUBAGENT_STATUS_CHANGED = "subagent:status_changed"
SUBAGENT_RESULT_READY = "subagent:result_ready"
```

### Observability Events
```python
# Audit and safety events
AUDIT_ACTION_LOGGED = "audit:action_logged"
SAFE_COMMAND_REQUESTED = "safe:command_requested"
SAFE_COMMAND_APPROVED = "safe:command_approved"
DRAWER_ERROR_DISPLAYED = "drawer:error_displayed"
```

### Session Events
```python
# Session management events
SESSION_LIST_LOADED = "session:list_loaded"
SESSION_SELECTED_FROM_PALETTE = "session:selected_from_palette"
```

### Provider/Account Events
```python
# Provider and account management events
PROVIDER_CHANGED = "provider:changed"
ACCOUNT_CHANGED = "account:changed"
MODEL_CHANGED = "model:changed"
PROVIDERS_LOADED = "providers:loaded"
ACCOUNTS_LOADED = "accounts:loaded"
```

---

## 3. API Contracts

### DrawerWidget API
```python
class DrawerWidget(Widget):
    # State management
    def toggle_visible() -> None
    def switch_tab(tab_id: str) -> None
    def request_focus() -> None
    def release_focus() -> None
    
    # Getters
    def get_visible() -> bool
    def get_has_focus() -> bool
    def get_active_tab() -> str
```

### FocusManager API
```python
class FocusManager:
    # Focus request/release
    def request_focus(target_widget: str, target_id: str) -> None
    def release_focus() -> None
    
    # State access
    def get_current_focus() -> Optional[str]
    def get_focus_history() -> List[FocusTransition]
```

### SubagentRegistry API
```python
class SubagentRegistry:
    # Registry operations
    def register_subagent(agent: Agent) -> None
    def get_subagent(name: str) -> Optional[Agent]
    def list_subagents() -> List[Agent]
    
    # Status/result methods
    def get_subagent_status(name: str) -> Optional[SubagentStatus]
    def get_last_result(name: str, session_id: str) -> Optional[SubagentResult]
```

### AuditTrailManager API
```python
class AuditTrailManager:
    # Audit trail operations
    async def log_event(event: AuditEvent) -> None
    async def query(query: AuditTrailQuery) -> List[AuditRecord]
```

### Event Bus Integration
All epics must subscribe to and emit events using the following event types:

**Drawer events**: DRAWER_OPEN, DRAWER_CLOSE, DRAWER_TAB_CHANGED

**Subagent events**: SUBAGENT_RUN, SUBAGENT_RERUN, SUBAGENT_STATUS_CHANGED, SUBAGENT_RESULT_READY

**Observability events**: AUDIT_ACTION_LOGGED, DRAWER_ERROR_DISPLAYED, SAFE_COMMAND_REQUESTED, SAFE_COMMAND_APPROVED

**Session events**: SESSION_LIST_LOADED, SESSION_SELECTED_FROM_PALETTE

**Provider/Account events**: PROVIDER_CHANGED, ACCOUNT_CHANGED, MODEL_CHANGED, PROVIDERS_LOADED, ACCOUNTS_LOADED
```

---

## 4. Implementation Guidelines

### Event Naming Convention

**Namespace Format**: `{domain}:{action}`

Examples:
- `drawer:open` - Drawer opened
- `drawer:close` - Drawer closed
- `drawer:tab_changed` - Drawer tab switched
- `subagent:run` - Subagent execution started
- `subagent:result_ready` - Subagent result ready
- `audit:action_logged` - Audit action recorded
- `safe:command_requested` - Safe command requested
- `safe:command_approved` - Safe command approved
- `drawer:error_displayed` - Error shown in drawer

### Priority Convention

**Event Priority Levels**:
- P0: Drawer visibility events
- P1: Subagent events (affects execution state)
- P2: Provider/account/model switching events (affects configuration)
- P3: Session lifecycle events (affects session state)
- P4: Audit and safety events (critical for compliance)

---

## 5. Testing Requirements

### Unit Tests per Epic

**Epic 1**: DrawerWidget, FocusManager, Tab components
- Test drawer toggle behavior
- Test tab switching logic
- Test focus request/release
- Test focus history tracking
- Test event emission and subscription

**Epic 2**: TopBarModel, CommandPalette
- Test provider/account/model display
- Test command palette actions
- Test event emissions for switching

**Epic 4**: SubagentRegistry, SubagentDrawer
- Test subagent registration and lookup
- Test run/rerun/cancel methods
- Test result object creation
- Test drawer integration and updates

**Epic 6**: AuditTrailManager, ErrorCollector, SafetyController
- Test audit trail logging and querying
- Test error collection and display
- Test safe command validation
- Test confirmation dialogs

### Integration Tests

- Test event bus communication between all epics
- Test drawer integration with TUI components
- Test provider/account/model switching updates timeline
- Test subagent status updates drawer
- Test observability events update timeline

---

**Document Status**: ✅ Complete