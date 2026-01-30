# Epic 3: Sessions - Decisions

## Documentation Decisions

### Decision 1: Separate Spec and Contract Documents
**Decision**: Create `drawer-sessions.md` (spec) and `drawer-sessions-contract.md` (contract)
**Rationale**: Clear separation aids maintainability, different audiences

### Decision 2: Include Complete Code Examples
**Decision**: Include full method signatures and usage examples for all models
**Rationale**: Reduces ambiguity, provides copy-paste ready code

## Architecture Decisions

### Decision 3: "Session is Timeline" Philosophy
**Decision**: Treat session as complete chronological record of conversation
**Rationale**: Consistent with observability concept, drawer navigator reinforces view

### Decision 4: Aggregation Layer for Timeline
**Decision**: Create `SessionManager.get_timeline_events()` to merge messages and timeline events
**Rationale**: Minimal changes, clean separation, no schema changes required

### Decision 5: Client-Side Filtering
**Decision**: Implement filtering in `NavigatorTimelineModel.apply_filters()`
**Rationale**: Simple to implement, fast, reactive feedback

## Data Model Decisions

### Decision 6: Summary Field on TimelineEvent
**Decision**: Add `summary` field to `TimelineEvent` model
**Rationale**: Consistent, generated once, allows human-crafted summaries

### Decision 7: NavigatorTimelineEvent as Unified Model
**Decision**: Create unified model with conversion methods
**Rationale**: Single model for display, clean separation from sources

## Event Schema Decisions

### Decision 8: Six New Events for Palette/Navigator
**Decision**: Add 6 events: SESSION_LIST_LOADED, SESSION_SELECTED_FROM_PALETTE, TIMELINE_INDEX_UPDATED, NAVIGATOR_SCROLL_TO_EVENT, NAVIGATOR_FILTER_APPLIED, NAVIGATOR_SEARCH_APPLIED
**Rationale**: Decouples components, clear boundaries, testable

## UI/UX Decisions

### Decision 9: Drawer Always Shows Timeline Index
**Decision**: Navigator tab always shows timeline index, even for new sessions
**Rationale**: Consistent UX, shows progress, filters handle empty state

### Decision 10: Type Pills for Event Differentiation
**Decision**: Use colored pills: [msg] [plan] [tool] [error]
**Rationale**: Quick visual scan, terminal-safe, compact

## Testing Decisions

### Decision 11: Separate Unit and Integration Tests
**Decision**: Separate test files for unit and integration tests
**Rationale**: Fast unit tests, full integration tests, clear separation

### Decision 12: Use pytest-asyncio for All Tests
**Decision**: Use `@pytest.mark.asyncio` for all tests
**Rationale**: Consistent with existing patterns, async/await throughout

## Dependency Decisions

### Decision 13: Minimal Changes to Core Modules
**Decision**: Submit focused, minimal changes as shared-change requests
**Rationale**: Lower review burden, faster approval, less risk

### Decision 14: Create Drawer Widgets as New Files
**Decision**: Create new widget files rather than modifying existing screens
**Rationale**: Clean separation, reusable, independent testing

## Implementation Order Decisions

### Decision 15: 5-Phase Implementation Plan
**Decision**: Break into 5 sequential phases
**Rationale**: Each phase delivers value, incremental testing, early feedback
