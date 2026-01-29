"""Tests for MessageScreen scroll navigation actions

Verifies that all scroll navigation methods exist and are callable.
"""

import pytest

from opencode_python.tui.screens.message_screen import MessageScreen
from opencode_python.core.models import Session


@pytest.fixture
def session():
    """Create a test session"""
    return Session(
        id="test-session",
        slug="test-session",
        project_id="test-project",
        directory="/path/to/project",
        title="Test Session",
        version="1.0.0",
        time_created=1700000000.0,
        time_updated=1700000000.0,
    )


def test_scroll_methods_exist(session):
    """Test that all scroll navigation methods exist"""
    screen = MessageScreen(session=session)

    # Verify all scroll methods exist
    assert hasattr(screen, 'action_scroll_home')
    assert hasattr(screen, 'action_scroll_end')
    assert hasattr(screen, 'action_scroll_page_up')
    assert hasattr(screen, 'action_scroll_page_down')
    assert hasattr(screen, 'action_scroll_to_top')
    assert hasattr(screen, 'action_scroll_to_bottom')
    assert hasattr(screen, 'action_scroll_half_page_up')
    assert hasattr(screen, 'action_scroll_half_page_down')
    assert hasattr(screen, 'action_jump_to_top')
    assert hasattr(screen, 'action_jump_to_bottom')

    # Verify methods are callable
    assert callable(screen.action_scroll_home)
    assert callable(screen.action_scroll_end)
    assert callable(screen.action_scroll_page_up)
    assert callable(screen.action_scroll_page_down)
    assert callable(screen.action_scroll_to_top)
    assert callable(screen.action_scroll_to_bottom)
    assert callable(screen.action_scroll_half_page_up)
    assert callable(screen.action_scroll_half_page_down)
    assert callable(screen.action_jump_to_top)
    assert callable(screen.action_jump_to_bottom)


def test_scroll_home(session):
    """Test that action_scroll_home method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_home()
    assert screen.action_scroll_home() is None


def test_scroll_end(session):
    """Test that action_scroll_end method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_end()
    assert screen.action_scroll_end() is None


def test_scroll_page_up(session):
    """Test that action_scroll_page_up method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_page_up()
    assert screen.action_scroll_page_up() is None


def test_scroll_page_down(session):
    """Test that action_scroll_page_down method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_page_down()
    assert screen.action_scroll_page_down() is None


def test_scroll_to_top(session):
    """Test that action_scroll_to_top method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_to_top()
    assert screen.action_scroll_to_top() is None


def test_scroll_to_bottom(session):
    """Test that action_scroll_to_bottom method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_to_bottom()
    assert screen.action_scroll_to_bottom() is None


def test_scroll_half_page_up(session):
    """Test that action_scroll_half_page_up method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_half_page_up()
    assert screen.action_scroll_half_page_up() is None


def test_scroll_half_page_down(session):
    """Test that action_scroll_half_page_down method works"""
    screen = MessageScreen(session=session)
    screen.action_scroll_half_page_down()
    assert screen.action_scroll_half_page_down() is None


def test_jump_to_top(session):
    """Test that action_jump_to_top method works"""
    screen = MessageScreen(session=session)
    screen.action_jump_to_top()
    assert screen.action_jump_to_top() is None


def test_jump_to_bottom(session):
    """Test that action_jump_to_bottom method works"""
    screen = MessageScreen(session=session)
    screen.action_jump_to_bottom()
    assert screen.action_jump_to_bottom() is None
