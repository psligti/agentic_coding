# Drawer-First UX - Merge Plan

**Version**: 1.0
**Date**: 2026-01-30
**Status**: Complete

---

## 1. Executive Summary

This merge plan defines the integration strategy for implementing the 6 drawer-focused epics into the OpenCode TUI. 5 out of 6 epics have completed documentation (Epic 5 failed to generate docs), and all artifacts are ready for implementation.

### Epics Status

| Epic | Status | Documentation | Contract | Ready to Implement |
|------|--------|--------------|----------------|----------------|
| Epic 1 - Drawer-First UX | ✅ Complete | ✅ Complete | ✅ Yes |
| Epic 2 - Providers & Accounts Overlay | ✅ Complete | ✅ Complete | ✅ Yes |
| Epic 3 - Session | ✅ Complete | ✅ Complete | ✅ Yes |
| Epic 4 - Subagents | ✅ Complete | ✅ Complete | ✅ Yes |
| Epic 5 - Themes & UX | ⚠ Incomplete | ⚠ Incomplete | ❌ No |
| Epic 6 - Observability & Safety | ✅ Complete | ✅ Complete | ✅ Yes |
| **Total** | **5/6 (83.3%)** | **5/6 (83.3%)** | **5/6 (83.3%)** |

**Note**: Epic 5 (Themes & UX) must be completed (documentation + implementation) before this merge plan can be fully executed.

---

## 2. Integration Strategy

### Recommended Approach: Parallel Integration

**Phase 1: Foundation (Optional but Recommended)**
If significant cross-epic conflicts are anticipated, create a `shared/foundation` epic first:

**Purpose**: Implement shared infrastructure that all epics depend on:
- Focus management (global FocusManager)
- Drawer state management (DrawerModel)
- Event bus constants (all new event types)
- Storage extensions (if needed)

**Benefits**:
- Reduces merge conflicts
- Ensures consistent implementation of shared systems
- Provides single source of truth for focus and drawer models

**Phase 2- Parallel Epic Implementation**
Implement all 6 epics in parallel worktrees, following integration order:

**Wave 1: Foundation + Core Epics**
1. Create `shared/foundation` worktree (if needed)
2. Implement FocusManager in shared foundation
3. Implement DrawerModel in shared foundation
4. Add shared event bus constants

5. Implement **Epic 1: Drawer-First UX** (foundation component)
   - DrawerWidget with 3 tabs
   - Focus integration
   - Event emissions

6. Implement **Epic 2: Providers & Accounts Overlay**
   - TopBarModel integration
   - Command palette actions
   - Event emissions

**Wave 2: Content Epics**
7. Implement **Epic 3: Sessions**
   - Session list command
   - Timeline aggregation
   - Event emissions

8. Implement **Epic 4: Subagents**
   - SubagentRegistry integration
   - Drawer integration
   - Event emissions

**Wave 3: Enhancement Epics**
9. Implement **Epic 6: Observability & Safety**
   - AuditTrailManager
   - ErrorCollector
   - SafetyController
   - Event emissions

10. Implement **Epic 5: Themes & UX**
   - Generate documentation
   - Implement basic functionality
   - Event emissions

**Note**: Epic 5 is the only epic requiring documentation generation before implementation.

### Integration Order

**Merge Sequence**:
1. shared/foundation (if created)
2. Epic 1 (Drawer-First UX) - foundation component, all epics depend on it
3. Epic 2 (Providers & Accounts Overlay)
4. Epic 3 (Sessions)
5. Epic 4 (Subagents)
6. Epic 6 (Observability & Safety)
7. Epic 5 (Themes & UX) - needs to complete before full integration

### Alternative Sequential Integration (if no shared/foundation)

**Phase 1**: Epic 1 → Epic 2 → Epic 3 → Epic 4 → Epic 6 → Epic 5

**Benefits**:
- More predictable integration timeline
- Earlier epics provide foundation for later epics
- Each epic builds on stable foundation
- Reduced merge complexity (fewer conflicts at once)

---

## 3. Conflict Resolution Strategy

### High-Risk Merge Points

**File**: `opencode_python/src/opencode_python/core/event_bus.py`
- **Risk**: All 6 epics add events → coordinate naming, resolve conflicts
- **Mitigation**: Each epic documents its event namespace additions
- **Resolution**: Follow event naming convention, use unique event types

**File**: `opencode_python/src/opencode_python/core/settings.py`
- **Risk**: Epics 1, 2, 5, 6 add settings → additive merge
- **Mitigation**: Document each epic's settings additions clearly
- **Resolution**: Additive merge only, no breaking changes

**File**: `opencode_python/src/opencode_python/tui/keybindings.py`
- **Risk**: Epic 1 adds drawer bindings → coordinate with navigation
- **Mitigation**: Coordinate with Epics 2, 3, 4, 6 to avoid keybinding conflicts
- **Resolution**: Document drawer bindings clearly, use unique combinations

**File**: `opencode_python/src/opencode_python/tui/app.py`
- **Risk**: Epics 1, 4 add drawer → coordinate widget mounting
- **Mitigation**: Ensure drawer widget is registered correctly

### Conflict Prevention

**Cross-Epic Dependencies**:
- Epic 3 (Sessions) must integrate before Epics 2, 4 (provider/account)
- Epic 4 (Subagents) must integrate before Epic 6 (observability)
- Epic 2 (Providers) must integrate before Epics 3 (sessions)
- Epic 6 (Observability) must integrate after all content epics

**Shared Foundation Recommendation**:
If cross-epic conflicts are high, create `shared/foundation` epic with:
- Global FocusManager
- DrawerModel
- All shared event bus constants
- Shared drawer and focus state models
- Integration utilities

**Risk Assessment**: MEDIUM (without shared foundation) to HIGH (with shared foundation)

---

## 4. Testing Strategy

### Integration Testing

1. **Event Bus Communication**
   - Test event emissions from Epic 1 propagate to other epics
   - Test event subscriptions work correctly
   - Verify no event loss or duplication

2. **Drawer Integration**
   - Test drawer functionality with all TUI components
   - Verify drawer state persistence across sessions
   - Test focus transitions work correctly
   - Verify tab switching preserves state

3. **Provider/Account Switching**
   - Test top bar updates are visible
   - Verify command palette actions work
   - Test timeline events are emitted on switches

4. **Focus Management**
   - Test focus requests from drawer to main, prompt, top bar
   - Test focus history tracking works
   - Verify focus returns to correct previous widget

5. **Subagent Integration**
   - Test subagent registry operations
   - Verify run/rerun functionality works
   - Test drawer shows subagent status correctly
   - Verify result objects track status

6. **Observability**
   - Test audit trail logging
   - Verify error collection and display
   - Test safe command validation
   - Verify confirmation dialogs work

### Acceptance Testing

**Epic 1**: Manual testing of drawer toggle, tab switching, focus transitions
**Epic 2**: Manual testing of provider/account switching commands
**Epic 3**: Manual testing of session list and timeline navigation
**Epic 4**: Manual testing of subagent operations
**Epic 6**: Manual testing of audit trail queries and error display

---

## 5. Rollout Plan

### Phase 1: Foundation Setup (if needed)

**Goal**: Ensure shared infrastructure is in place before starting epic implementation.

**Actions**:
1. Create `shared/foundation` epic worktree
2. Implement global FocusManager class
3. Implement shared DrawerModel class
4. Add shared event bus constants
5. Integrate shared foundation into base branch

**Dependencies**: None (foundation stands alone)

**Estimated Time**: 4-8 hours

### Phase 2: Epic 1 Implementation (Foundation + Core)

**Goal**: Implement foundation drawer component that other epics depend on.

**Actions**:
1. Implement DrawerWidget with 3 tabs
2. Implement FocusManager integration
3. Add all drawer event types
4. Add drawer keyboard bindings
5. Test foundation components independently

**Dependencies**:
- Event bus (existing)
- Settings (existing)
- Keybindings (existing)
- TUI app (existing)

**Estimated Time**: 8-12 hours

### Phase 3-7: Parallel Epic Implementation

**Goal**: Implement all 6 epics in their worktrees following merge order.

**Epic 1**: 8-12 hours
**Epic 2**: 14 hours
**Epic 3**: 12 hours
**Epic 4**: 16 hours
**Epic 6**: 22 hours
**Epic 5**: TBD (documentation generation first)

**Total Estimated Time**: 72-84 hours

### Phase 4: Integration & Testing

**Goal**: Merge all epic branches into base branch and resolve conflicts.

**Actions**:
1. Merge Epic 2 (Providers & Accounts) into base
2. Merge Epic 3 (Sessions) into base
3. Merge Epic 4 (Subagents) into base
4. Merge Epic 6 (Observability & Safety) into base
5. Merge Epic 1 (Drawer-First UX) into base
6. Generate Epic 5 documentation (if not done) and merge

**Testing**:
- Comprehensive integration testing for all cross-epic functionality
- Fix any merge conflicts
- Verify all event bus subscriptions work
- Test focus management across all epics
- Run full test suite

**Estimated Time**: 12-16 hours

### Phase 5: Epic 5 Completion & Polish

**Goal**: Generate Epic 5 documentation and implement basic functionality.

**Actions**:
1. Generate Epic 5 documentation (if not done)
2. Implement basic Posting-inspired styling
3. Implement focus highlight consistency
4. Implement drawer width configuration
5. Implement accessibility features
6. Test and validate all features

**Estimated Time**: 4-8 hours

---

## 6. Risk Mitigation

### High Risks

1. **Epic 5 Incomplete**: Without Epic 5 documentation, other epics implement without clear theme/UX guidelines.
   - **Mitigation**: Prioritize Epic 5 documentation generation or implement basic features in other epics first.

2. **Cross-Epic Conflicts**: All epics modify the same files (event_bus.py, settings.py, keybindings.py).
   - **Mitigation**: Create `shared/foundation` epic with shared focus and drawer models, implement all shared event types. This eliminates conflicts at source.

### Medium Risks

1. **Focus System Complexity**: Coordinating focus across 6 epics without shared foundation may lead to inconsistent implementations.
   - **Mitigation**: Document clear focus management requirements for all epics to follow.

2. **Event Bus Scalability**: 6 epics all emitting events may impact performance.
   - **Mitigation**: Add event batching or debouncing if performance issues occur.

3. **Epic 3 Timeline Aggregation**: Large session aggregations may be slow.
   - **Mitigation**: Implement efficient querying and caching in NavigatorTimelineModel.

### Low Risks

1. **Storage Backward Compatibility**: Audit trail storage should not break existing session storage.
   - **Mitigation**: Use separate storage namespace (~/.opencode/audit/), validate compatibility.

---

## 7. Success Metrics

### Readiness for Implementation

- **Architecture**: 100% - Clear models, contracts, integration points
- **Data Flow**: 100% - Complete diagrams and event flows
- **Epic 3-6 Dependencies**: 100% - All cross-epic integration points documented
- **Testing Strategy**: 100% - Unit and integration test approaches defined
- **Epic 5 Documentation**: 0% - Epic 5 documentation incomplete

### Implementation Metrics

- **Total Tasks**: 94
- **Total Estimate**: 72-84 hours
- **Confidence**: High (assuming Epic 5 is completed before starting)

---

## 8. Next Steps

1. **Decision Point**: Epic 5 - Proceed with documentation generation or implement as lower priority?

2. **Recommended Action**: Proceed with shared foundation epic first for safer integration, then implement all 6 epics in parallel.

3. **Final Integration**: Follow Phase 2-7 merge plan once all epics are documented.

---

**Plan Status**: ✅ Complete