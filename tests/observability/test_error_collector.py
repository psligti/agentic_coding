import pytest
from opencode_python.observability.error_collector import (
    ErrorCollector,
    ErrorLevel,
    ErrorRecord,
)


@pytest.fixture
def collector():
    return ErrorCollector()


@pytest.fixture
def session_id():
    return "test-session-123"


@pytest.fixture
def level():
    return ErrorLevel.ERROR


def test_error_level_values():
    assert ErrorLevel.CRITICAL.value == "critical"
    assert ErrorLevel.ERROR.value == "error"
    assert ErrorLevel.WARNING.value == "warning"


def test_error_level_string_conversion():
    assert str(ErrorLevel.CRITICAL) == "critical"
    assert str(ErrorLevel.ERROR) == "error"
    assert str(ErrorLevel.WARNING) == "warning"


def test_error_record_creation(level, session_id):
    record = ErrorRecord(
        record_id="test-1",
        session_id=session_id,
        level=level,
        message="Test error message",
    )

    assert record.record_id == "test-1"
    assert record.session_id == session_id
    assert record.level == level
    assert record.message == "Test error message"
    assert record.is_resolved is False


def test_error_record_context(level, session_id):
    context = {"component": "test_component", "line": 42}
    record = ErrorRecord(
        record_id="test-2",
        session_id=session_id,
        level=level,
        message="Error with context",
        context=context,
    )

    assert record.context == context


def test_error_record_icon(level, session_id):
    record = ErrorRecord(
        record_id="test-3",
        session_id=session_id,
        level=level,
        message="Test error",
    )

    assert record.icon in ["🔴", "❌", "⚠️"]


def test_error_record_timestamp(level, session_id):
    record = ErrorRecord(
        record_id="test-4",
        session_id=session_id,
        level=level,
        message="Test error",
    )

    assert isinstance(record.formatted_timestamp, str)
    assert len(record.formatted_timestamp) > 0


def test_singleton_pattern():
    collector1 = ErrorCollector()
    collector2 = ErrorCollector()

    assert collector1 is collector2


def test_initial_state(collector):
    assert len(collector._errors) == 0
    assert len(collector._by_session) == 0
    assert len(collector._by_level) == 0


def test_collect_error(collector, session_id, level):
    record_id = collector.collect_error(
        level=level,
        message="Test error message",
        session_id=session_id,
    )

    assert record_id in collector._errors
    assert len(collector.get_errors()) == 1


def test_collect_error_with_context(collector, session_id, level):
    context = {"component": "test", "line": 10}
    record_id = collector.collect_error(
        level=level,
        message="Error with context",
        session_id=session_id,
        context=context,
    )

    record = collector._errors[record_id]
    assert record.context == context


def test_collect_error_with_source(collector, session_id, level):
    record_id = collector.collect_error(
        level=level,
        message="Error from component",
        session_id=session_id,
        source="test_component",
    )

    record = collector._errors[record_id]
    assert record.source == "test_component"


def test_collect_error_with_error_details(collector, session_id, level):
    record_id = collector.collect_error(
        level=level,
        message="Detailed error",
        session_id=session_id,
        error_details="Traceback (most recent call last):\n  File \"test.py\", line 1",
    )

    record = collector._errors[record_id]
    assert record.error_details == "Traceback (most recent call last):\n  File \"test.py\", line 1"


def test_collect_multiple_errors(collector, session_id):
    record_id1 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="First error",
        session_id=session_id,
    )
    record_id2 = collector.collect_error(
        level=ErrorLevel.WARNING,
        message="Second error",
        session_id=session_id,
    )
    record_id3 = collector.collect_error(
        level=ErrorLevel.CRITICAL,
        message="Critical error",
        session_id=session_id,
    )

    assert len(collector.get_errors()) == 3
    assert record_id1 in collector._errors
    assert record_id2 in collector._errors
    assert record_id3 in collector._errors


def test_get_errors_by_session_id(collector, session_id):
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Session error 1",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Session error 2",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.WARNING,
        message="Other session error",
        session_id="other-session",
    )

    session_errors = collector.get_errors(session_id=session_id)
    assert len(session_errors) == 2


def test_get_errors_by_level(collector, session_id):
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error message",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.WARNING,
        message="Warning message",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Another error",
        session_id=session_id,
    )

    errors = collector.get_errors(level=ErrorLevel.ERROR)
    assert len(errors) == 2
    assert all(e.level == ErrorLevel.ERROR for e in errors)


def test_get_errors_by_resolved(collector, session_id):
    record_id1 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Unresolved error",
        session_id=session_id,
    )
    record_id2 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Another unresolved error",
        session_id=session_id,
    )
    collector.resolve_error(record_id1)

    unresolved = collector.get_errors(resolved=False)
    assert len(unresolved) == 1

    resolved = collector.get_errors(resolved=True)
    assert len(resolved) == 1


def test_get_errors_combined_filters(collector, session_id):
    record_id1 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error in session",
        session_id=session_id,
    )
    record_id2 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error in other session",
        session_id="other-session",
    )
    collector.resolve_error(record_id1)

    filtered = collector.get_errors(
        session_id=session_id, resolved=False, level=ErrorLevel.ERROR
    )
    assert len(filtered) == 1
    assert filtered[0].record_id == record_id1


def test_get_errors_count(collector, session_id):
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 1",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 2",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.WARNING,
        message="Warning",
        session_id=session_id,
    )

    assert collector.get_errors_count(session_id=session_id) == 3
    assert collector.get_errors_count(session_id=session_id, level=ErrorLevel.ERROR) == 2
    assert collector.get_errors_count(resolved=True) == 0


def test_resolve_error(collector, session_id):
    record_id = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Test error",
        session_id=session_id,
    )

    assert collector.resolve_error(record_id) is True
    assert collector._errors[record_id].is_resolved is True


def test_resolve_nonexistent_error(collector, session_id):
    result = collector.resolve_error("nonexistent-id")
    assert result is False


def test_clear_session_errors(collector, session_id):
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 1",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 2",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.WARNING,
        message="Other session error",
        session_id="other-session",
    )

    cleared = collector.clear_session_errors(session_id)
    assert cleared == 2
    assert len(collector.get_errors(session_id=session_id)) == 0
    assert len(collector.get_errors()) == 1


def test_clear_all_errors(collector, session_id):
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 1",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 2",
        session_id=session_id,
    )

    cleared = collector.clear_all_errors()
    assert cleared == 2
    assert len(collector.get_errors()) == 0
    assert len(collector._by_session) == 0
    assert len(collector._by_level) == 0


def test_get_statistics(collector, session_id):
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 1",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Error 2",
        session_id=session_id,
    )
    collector.collect_error(
        level=ErrorLevel.WARNING,
        message="Warning",
        session_id=session_id,
    )
    record_id = collector.collect_error(
        level=ErrorLevel.CRITICAL,
        message="Critical error",
        session_id=session_id,
    )
    collector.resolve_error(record_id)

    stats = collector.get_statistics()

    assert stats["total_errors"] == 4
    assert stats["unresolved"] == 3
    assert stats["by_level"]["error"] == 2
    assert stats["by_level"]["warning"] == 1
    assert stats["by_level"]["critical"] == 1
    assert session_id in stats["by_session"]
    assert stats["by_session"][session_id] == 4


def test_errors_sorted_by_timestamp(collector, session_id):
    import time

    record_id1 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="First error",
        session_id=session_id,
    )
    time.sleep(0.01)
    record_id2 = collector.collect_error(
        level=ErrorLevel.ERROR,
        message="Second error",
        session_id=session_id,
    )

    errors = collector.get_errors(session_id=session_id)
    assert errors[0].record_id == record_id2
    assert errors[1].record_id == record_id1


def test_multiple_collectors_dont_share_state():
    collector1 = ErrorCollector()
    collector2 = ErrorCollector()

    record_id = collector1.collect_error(
        level=ErrorLevel.ERROR,
        message="Error in collector 1",
        session_id="session-1",
    )

    assert len(collector1.get_errors()) == 1
    assert len(collector2.get_errors()) == 0
