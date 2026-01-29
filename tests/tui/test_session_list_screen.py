"""Tests for SessionListScreen

TDD Workflow:
- RED: Write failing tests first
- GREEN: Implement screen to pass tests
- REFACTOR: Improve code structure
"""

import pytest
from datetime import datetime

from opencode_python.tui.screens.session_list_screen import SessionListScreen
from opencode_python.core.models import Session


@pytest.fixture
def sessions():
    """Create test sessions"""
    return [
        Session(
            id="session-1",
            slug="session-1",
            project_id="project-1",
            directory="/path/to/project-1",
            title="Test Session 1",
            version="1.0.0",
            time_created=1700000000.0,
            time_updated=1700000000.0,
        ),
        Session(
            id="session-2",
            slug="session-2",
            project_id="project-1",
            directory="/path/to/project-2",
            title="Test Session 2",
            version="1.0.0",
            time_created=1700001000.0,
            time_updated=1700001000.0,
        ),
    ]


def test_session_list_screen_instantiation(sessions):
    """Test that SessionListScreen can be instantiated with sessions"""
    screen = SessionListScreen(sessions=sessions)
    assert screen is not None
    assert screen.sessions == sessions


def test_session_list_find_session_by_id(sessions):
    """Test that _find_session_by_id returns the correct session"""
    screen = SessionListScreen(sessions=sessions)

    # Test finding existing session
    found = screen._find_session_by_id("session-1")
    assert found is not None
    assert found.id == "session-1"
    assert found.title == "Test Session 1"

    # Test finding non-existent session
    not_found = screen._find_session_by_id("non-existent")
    assert not_found is None


def test_session_list_format_time(sessions):
    """Test that _format_time formats timestamp correctly"""
    screen = SessionListScreen(sessions=sessions)

    # Test valid timestamp
    formatted = screen._format_time(1700000000.0)
    # Jan 29, 2026 would be around this time
    assert isinstance(formatted, str)
    assert len(formatted) > 0

    # Test with None or invalid timestamp
    assert screen._format_time(None) == "Unknown"
    assert screen._format_time("invalid") == "Unknown"


def test_session_list_format_time_none(sessions):
    """Test _format_time with None timestamp"""
    screen = SessionListScreen(sessions=sessions)
    result = screen._format_time(None)
    assert result == "Unknown"


def test_session_list_format_time_string(sessions):
    """Test _format_time with invalid string timestamp"""
    screen = SessionListScreen(sessions=sessions)
    result = screen._format_time("invalid timestamp")
    assert result == "Unknown"


def test_session_list_empty_sessions():
    """Test that empty session list is handled"""
    screen = SessionListScreen(sessions=[])

    # Find should return None for all
    assert screen._find_session_by_id("session-1") is None
    assert screen._find_session_by_id("session-2") is None

    # Format time should still work
    assert screen._format_time(1700000000.0) != "Unknown"


def test_session_list_multiple_sessions():
    """Test session list with multiple sessions"""
    # Create 5 sessions
    sessions = [
        Session(
            id=f"session-{i}",
            slug=f"session-{i}",
            project_id="project-1",
            directory=f"/path/to/project-{i}",
            title=f"Test Session {i}",
            version="1.0.0",
            time_created=1700000000.0 + i * 1000,
            time_updated=1700000000.0 + i * 1000,
        )
        for i in range(5)
    ]

    screen = SessionListScreen(sessions=sessions)

    # All sessions should be accessible via find_session_by_id
    for i in range(5):
        found = screen._find_session_by_id(f"session-{i}")
        assert found is not None
        assert found.title == f"Test Session {i}"

    # Non-existent should return None
    assert screen._find_session_by_id("session-99") is None
