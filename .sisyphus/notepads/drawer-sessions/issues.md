# Epic 3: Sessions - Issues

## Documentation Generation Issues

### None Encountered
Documentation generation completed successfully without issues.

## Potential Future Issues

### Issue 1: Summary Field on TimelineEvent
**Problem**: `TimelineEvent` model may not have `summary` field
**Impact**: Navigator needs summaries for display
**Workaround**: Generate on-the-fly from `details` field
**Resolution**: Add `summary` field to `TimelineEvent` in `observability/models.py`

### Issue 2: SessionManager Timeline Aggregation
**Problem**: Messages and timeline events are in separate managers
**Impact**: Need aggregation layer to merge them
**Workaround**: New method in SessionManager calls both managers
**Resolution**: Implement `get_timeline_events()` in SessionManager

### Issue 3: Drawer Widget Not Yet Created
**Problem**: Drawer container and timeline navigator widgets don't exist
**Impact**: Contract references non-existent files
**Workaround**: Create widgets during implementation
**Resolution**: Create `tui/widgets/drawer.py` and `tui/widgets/timeline_navigator.py`

## No Critical Blockers

All identified issues have workarounds or clear resolution paths.
