# Epic 3: Sessions - Learnings

## Documentation Generation Patterns

### File Structure
- Spec document (`drawer-sessions.md`): 449 lines
- Contract document (`drawer-sessions-contract.md`): 1,183 lines
- Contract is significantly larger due to detailed model and event schema definitions

### Content Organization

**Spec Document Structure**:
1. Epic Restatement (what and why)
2. Success Criteria (UX and technical)
3. Command Palette Integration
4. "Session is the Timeline" Reinforcement
5. Drawer Navigator Integration
6. Reuse Strategy for Existing SessionManager
7. Event Schema Additions
8. Integration Points with Existing Modules
9. Dependencies on Shared Modules
10. Open Questions
11. Next Steps

**Contract Document Structure**:
1. Overview
2. Data Models (detailed with usage examples)
3. Event Schema (all 6 events with payload schemas)
4. Integration Points (by module with code examples)
5. Testing Requirements (unit and integration tests)
6. Dependencies Summary (tables of changes/new files)
7. Implementation Order (5 phases)
8. Glossary

## Codebase Understanding

### Existing Session Management

**SessionManager Location**: `opencode_python/core/session.py`
- Already implements full CRUD operations
- `list_sessions()`, `get_session()`, `create()`, `update_session()`, `delete_session()`
- `list_messages()`, `create_message()`, `get_messages()`
- Strong foundation for reuse - minimal additions needed

**TimelineManager Location**: `opencode_python/observability/timeline.py`
- Manages timeline events (`TimelineEvent` with EventType)
- `add_event()`, `get_events()`, `set_session_status()`
- Already emits `timeline:label` event
- Provides event tracking beyond messages

**Event Bus**: `opencode_python/core/event_bus.py`
- Central pub/sub system
- Already has session-related events (`SESSION_CREATED`, `SESSION_UPDATED`, etc.)
- Already has timeline-related events (`TIMELINE_LABEL`)
- Clean pattern for adding new events

### Command Palette

**Location**: `opencode_python/tui/dialogs/command_palette_dialog.py`
- Uses `ModalScreen` from Textual
- Has command list with filtering
- Uses `Static` widgets for display
- Keybindings: Enter, Escape, Up, Down
- Already has "session-list" and "create-session" commands defined

### TUI Screens

**MessageScreen**: `opencode_python/tui/screens/message_screen.py`
- Shows message timeline
- Has DataTable for messages
- Keybindings: Escape, Ctrl+C, Enter, N
- Currently shows only messages, not full timeline

**OpenCodeTUI**: `opencode_python/tui/app.py`
- Main TUI application
- Uses `DataTable` for session list in sidebar
- Already has command palette integration (`Ctrl+P`)
- Reactive attributes for state management

## Key Design Decisions

### "Session is Timeline" Philosophy

**Concept**: Session is not just metadata - it's the complete chronological record
- Messages (user/assistant/system)
- Tool calls and results
- Plans and planning events
- Code changes and diffs
- Errors and failures

**Implementation**:
- Drawer navigator shows ALL timeline events, not just messages
- Type pills differentiate events (msg/plan/tool/error/etc)
- Summaries provide quick understanding
- Each event is scrollable target in main timeline

### Event Aggregation Strategy

**Challenge**: Messages in `SessionManager`, timeline events in `TimelineManager`
**Solution**: New method `SessionManager.get_timeline_events()` that:
1. Loads messages via `list_messages()`
2. Gets timeline events via `timeline_manager.get_events()`
3. Converts both to `NavigatorTimelineEvent` format
4. Merges and sorts by timestamp
5. Returns unified timeline

**Alternative Considered**: Store all as timeline events
- **Rejected**: Too much refactoring, risk to existing code
- **Chosen Approach**: Aggregation layer, clean separation

### Summary Generation

**Challenge**: Navigator needs short summaries for display
**Options**:
1. Store with event (persistent, requires schema change)
2. Generate on-the-fly (flexible, no schema changes)
3. Hybrid: Generate and cache when needed

**Decision**: Store with event when possible
- **Why**: Consistency, performance, simpler code
- **Fallback**: Generate from text if missing
- **Implementation**: Add `summary` field to `TimelineEvent`

### Filter Design

**Navigator Filters**:
- Speaker types: user, agent, subagent
- Event types: msg, plan, tool, diff, result, error
- Both optional (empty = all)
- Applied client-side in `NavigatorTimelineModel`

**Command Palette Filters**:
- Text search on session title
- Optional: Sort by time/status
- Applied in `SessionListAction.filter_sessions()`

## Integration Patterns

### Event Bus Usage Pattern

```python
# Emitting event
await bus.publish(Events.EVENT_NAME, {
    "field1": value1,
    "field2": value2,
    "timestamp": datetime.now().timestamp(),
})

# Subscribing to event
await bus.subscribe(Events.EVENT_NAME, callback)

async def callback(event: Event):
    data = event.data
    # Handle event
```

**Pattern Observed**:
- All events have timestamp
- Data is dict, not typed object
- Callbacks receive `Event` wrapper
- Use `asyncio.create_task()` for fire-and-forget

### Model Reuse Pattern

**SessionManager Usage**:
```python
# Direct method calls
sessions = await session_manager.list_sessions()
session = await session_manager.get_session(session_id)
new_session = await session_manager.create(title=...)
```

**TimelineManager Usage**:
```python
# Get events from manager
events = timeline_manager.get_events(session_id)

# Add new event
event = await timeline_manager.add_event(
    session_id,
    event_type,
    details={"key": "value"},
    error_details=None,
)
```

## Testing Approach

### Unit Test Structure

**Test Files**:
- `tests/tui/test_session_list_action.py`
- `tests/tui/test_navigator_timeline_model.py`

**Test Pattern**:
```python
@pytest.mark.asyncio
async def test_feature(fixture):
    """Description of what's tested"""
    # Arrange
    obj = ClassUnderTest(fixture)

    # Act
    result = await obj.method()

    # Assert
    assert expected == result
```

**Fixtures Needed**:
- `session_manager`: Mock or real SessionManager instance
- `timeline_manager`: Mock or real TimelineManager instance

### Integration Test Structure

**Test File**: `tests/tui/test_command_palette_integration.py`

**Test Pattern**:
```python
@pytest.mark.asyncio
async def test_end_to_end(session_manager):
    """Test full user flow"""
    app = App()
    dialog = CommandPaletteDialog(session_manager=session_manager)

    async with app.run_test() as pilot:
        await pilot.press("/")  # Open palette
        # Type search
        for char in "session list":
            await pilot.press(char)
        # Select
        await pilot.press("enter")

        # Verify
        assert dialog.get_result() == "session-list"
```

## Open Questions and Decisions

### Question 1: Summary Storage
- **Decision**: Store with event (add `summary` field to `TimelineEvent`)
- **Reason**: Consistency, performance, simplicity

### Question 2: Navigator Detail Level
- **Decision**: Show all events with filters
- **Reason**: Comprehensive view, filters reduce noise

### Question 3: Session List Sort Order
- **Decision**: Most recently updated (default)
- **Reason**: Intuitive for session switching
- **Note**: Can add sort option later

## Dependencies Identified

### Core Module Changes
1. **event_bus.py**: Add 6 event constants (HIGH priority)
2. **session.py**: Add `get_timeline_events()` and `generate_summary()` (HIGH priority)
3. **models.py**: Optional `summary` field on `TimelineEvent` (MEDIUM priority)

### TUI Module Changes
1. **command_palette_dialog.py**: Integrate `SessionListAction` (MEDIUM priority)
2. **app.py**: Subscribe to selection events (MEDIUM priority)
3. **message_screen.py**: Add scroll-to-event method (MEDIUM priority)

### New Files Required
1. **tui/widgets/drawer.py**: Drawer container and timeline navigator
2. **tui/widgets/timeline_navigator.py**: Extracted navigator widget
3. **tests/tui/test_session_list_action.py**: Unit tests
4. **tests/tui/test_navigator_timeline_model.py**: Unit tests
5. **tests/tui/test_command_palette_integration.py**: Integration tests

## Successful Patterns to Follow

### Documentation Style
- Clear separation between spec and contract
- Contract has complete code examples
- Tables for dependencies and changes
- Glossary for terminology
- Implementation phases clearly numbered

### Model Design
- Dataclasses for models
- Type hints throughout
- Docstrings for all public methods
- `@staticmethod` for conversion methods
- Optional fields with defaults

### Event Schema
- Consistent payload structure
- Always include timestamp
- Clear field descriptions
- Usage examples in docstrings
- Emit event immediately after action

### Testing
- pytest-asyncio for async tests
- Descriptive test names
- Arrange-Act-Assert pattern
- Async test markers
- Separate unit and integration tests
