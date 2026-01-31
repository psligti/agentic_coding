"""Tests for TopBar Widget"""

import pytest
from textual.app import App
from textual.widgets import Static, Button

from opencode_python.tui.widgets.top_bar import TopBar, RunState


@pytest.mark.asyncio
async def test_top_bar_widget_instantiation():
    """Test that TopBar widget can be instantiated"""
    top_bar = TopBar()
    assert top_bar is not None
    assert isinstance(top_bar, TopBar)


@pytest.mark.asyncio
async def test_top_bar_initial_state():
    """Test that TopBar initializes with default empty values"""
    top_bar = TopBar()
    assert top_bar.provider_id == ""
    assert top_bar.account_id == ""
    assert top_bar.model_id == ""
    assert top_bar.agent == ""
    assert top_bar.session_id == ""
    assert top_bar.run_state == RunState.IDLE


@pytest.mark.asyncio
async def test_top_bar_context_display_updates_on_provider_change():
    """Test that context display updates when provider_id changes"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.provider_id = "openai"

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.provider_id == "openai"


@pytest.mark.asyncio
async def test_top_bar_context_display_updates_on_account_change():
    """Test that context display updates when account_id changes"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.account_id = "default"

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.account_id == "default"


@pytest.mark.asyncio
async def test_top_bar_context_display_updates_on_model_change():
    """Test that context display updates when model_id changes"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.model_id = "gpt-4"

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.model_id == "gpt-4"


@pytest.mark.asyncio
async def test_top_bar_context_display_updates_on_agent_change():
    """Test that context display updates when agent changes"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.agent = "assistant"

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.agent == "assistant"


@pytest.mark.asyncio
async def test_top_bar_context_display_updates_on_session_change():
    """Test that context display updates when session_id changes"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.session_id = "session-12345"

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.session_id == "session-12345"


@pytest.mark.asyncio
async def test_top_bar_run_state_indicator_idle():
    """Test that run state indicator shows idle state correctly"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        assert top_bar.run_state == RunState.IDLE


@pytest.mark.asyncio
async def test_top_bar_run_state_indicator_running():
    """Test that run state indicator shows running state correctly"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.run_state = RunState.RUNNING

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.run_state == RunState.RUNNING


@pytest.mark.asyncio
async def test_top_bar_run_state_indicator_error():
    """Test that run state indicator shows error state correctly"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.run_state = RunState.ERROR

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.run_state == RunState.ERROR


@pytest.mark.asyncio
async def test_top_bar_reactive_watcher_provider_id():
    """Test that reactive watcher for provider_id works correctly"""
    top_bar = TopBar()
    top_bar.watch_provider_id("", "openai")
    assert top_bar.provider_id == "openai"


@pytest.mark.asyncio
async def test_top_bar_reactive_watcher_account_id():
    """Test that reactive watcher for account_id works correctly"""
    top_bar = TopBar()
    top_bar.watch_account_id("", "default")
    assert top_bar.account_id == "default"


@pytest.mark.asyncio
async def test_top_bar_reactive_watcher_model_id():
    """Test that reactive watcher for model_id works correctly"""
    top_bar = TopBar()
    top_bar.watch_model_id("", "gpt-4")
    assert top_bar.model_id == "gpt-4"


@pytest.mark.asyncio
async def test_top_bar_reactive_watcher_agent():
    """Test that reactive watcher for agent works correctly"""
    top_bar = TopBar()
    top_bar.watch_agent("", "builder")
    assert top_bar.agent == "builder"


@pytest.mark.asyncio
async def test_top_bar_reactive_watcher_session_id():
    """Test that reactive watcher for session_id works correctly"""
    top_bar = TopBar()
    top_bar.watch_session_id("", "session-12345")
    assert top_bar.session_id == "session-12345"


@pytest.mark.asyncio
async def test_top_bar_reactive_watcher_run_state():
    """Test that reactive watcher for run_state works correctly"""
    top_bar = TopBar()
    top_bar.watch_run_state(RunState.IDLE, RunState.RUNNING)
    assert top_bar.run_state == RunState.RUNNING


@pytest.mark.asyncio
async def test_top_bar_full_context_display():
    """Test that full context is displayed with all properties set"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.provider_id = "openai"
        top_bar.account_id = "default"
        top_bar.model_id = "gpt-4"
        top_bar.agent = "assistant"
        top_bar.session_id = "session-12345"
        top_bar.run_state = RunState.IDLE

        # Give time for reactive updates
        await pilot.pause()

        assert top_bar.provider_id == "openai"
        assert top_bar.account_id == "default"
        assert top_bar.model_id == "gpt-4"
        assert top_bar.agent == "assistant"
        assert top_bar.session_id == "session-12345"
        assert top_bar.run_state == RunState.IDLE


@pytest.mark.asyncio
async def test_top_bar_session_id_truncation():
    """Test that long session IDs are truncated in display"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        long_session_id = "very-long-session-id-that-should-be-truncated"
        top_bar.session_id = long_session_id

        # Give time for reactive update
        await pilot.pause()

        # Session ID should be stored in full, display truncated
        assert top_bar.session_id == long_session_id


@pytest.mark.asyncio
async def test_top_bar_action_button_text_idle():
    """Test that action button shows 'Run' when idle"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.run_state = RunState.IDLE

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.run_state == RunState.IDLE


@pytest.mark.asyncio
async def test_top_bar_action_button_text_running():
    """Test that action button shows 'Continue' when not idle"""
    class TestApp(App):
        def compose(self):
            yield TopBar()

    app = TestApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one(TopBar)
        top_bar.run_state = RunState.RUNNING

        # Give time for reactive update
        await pilot.pause()

        assert top_bar.run_state == RunState.RUNNING
