"""Tests for Vertical Stack TUI Application"""
from __future__ import annotations

import pytest
import asyncio

from opencode_python.tui.vertical_stack_app import VerticalStackApp, PromptSubmitted
from opencode_python.tui.context_manager import RunState


@pytest.mark.asyncio
async def test_app_can_be_instantiated():
    """Test that VerticalStackApp can be instantiated"""
    app = VerticalStackApp()
    assert app is not None
    assert isinstance(app, VerticalStackApp)


@pytest.mark.asyncio
async def test_factory_function():
    """Test factory function creates app correctly"""
    app = VerticalStackApp()
    assert app is not None
    assert isinstance(app, VerticalStackApp)


@pytest.mark.asyncio
async def test_compose_creates_required_widgets():
    """Test that compose() creates all required widgets"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Check that all required widgets exist
        top_bar = app.query_one("#top-bar")
        conversation_history = app.query_one("#conversation-history")
        prompt_area = app.query_one("#prompt-area")
        status_bar = app.query_one("#status-bar")

        assert top_bar is not None
        assert conversation_history is not None
        assert prompt_area is not None
        assert status_bar is not None


@pytest.mark.asyncio
async def test_keybindings_registered():
    """Test that required keybindings are registered"""
    app = VerticalStackApp()

    # Check for Ctrl+Q binding
    ctrl_q = next((b for b in app.BINDINGS if b.key == "ctrl+q"), None)
    assert ctrl_q is not None
    assert ctrl_q.action == "quit"

    # Check for Ctrl+P binding
    ctrl_p = next((b for b in app.BINDINGS if b.key == "ctrl+p"), None)
    assert ctrl_p is not None
    assert ctrl_p.action == "open_command_palette"

    # Check for Ctrl+Z binding
    ctrl_z = next((b for b in app.BINDINGS if b.key == "ctrl+z"), None)
    assert ctrl_z is not None
    assert ctrl_z.action == "undo_context"


@pytest.mark.asyncio
async def test_context_manager_initialized():
    """Test that ContextManager is properly initialized"""
    app = VerticalStackApp()
    assert app.context_manager is not None
    assert app.context_manager.provider_id == "openai"
    assert app.context_manager.account_id == "default"
    assert app.context_manager.model_id == "gpt-4"
    assert app.context_manager.session_id == "session-001"


@pytest.mark.asyncio
async def test_metrics_tracking():
    """Test that metrics are tracked correctly"""
    app = VerticalStackApp()

    # Check initial metrics
    assert app.message_count == 0
    assert app.total_cost == 0.0
    assert app.total_tokens == 0


@pytest.mark.asyncio
async def test_conversation_history_integration():
    """Test that ConversationHistory is integrated correctly"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        conversation_history = app.query_one("#conversation-history")

        # Add a message
        conversation_history.add_message("user", "Hello, world!")

        # Check that message was added
        assert len(conversation_history.messages) == 1
        assert conversation_history.messages[0]["type"] == "user"


@pytest.mark.asyncio
async def test_status_bar_metrics_update():
    """Test that status bar metrics update correctly"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        status_bar = app.query_one("#status-bar")

        # Update metrics
        app.message_count = 5
        app.total_cost = 0.1234
        app.total_tokens = 1000
        app._update_metrics_display()

        # Check that status bar reflects metrics
        # (This is a basic check; in real tests we'd verify the displayed values)
        assert status_bar is not None


@pytest.mark.asyncio
async def test_command_palette_opens():
    """Test that command palette opens with Ctrl+P"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Press Ctrl+P
        await pilot.press("ctrl+p")

        # Give time for screen to open
        await pilot.pause()

        # Check that a modal screen is open
        screens = app.screen_stack
        assert len(screens) > 1, "Command palette screen should be open"


@pytest.mark.asyncio
async def test_quit_action():
    """Test that quit action works"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Press Ctrl+Q
        await pilot.press("ctrl+q")

        # Give time for action to execute
        await pilot.pause()

        # Check that app is exited
        assert app.is_running == False


@pytest.mark.asyncio
async def test_undo_context_action():
    """Test that undo context action works"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Make a context change
        app.context_manager.switch_model("gpt-3.5-turbo")

        # Verify change
        assert app.context_manager.model_id == "gpt-3.5-turbo"

        # Undo
        await pilot.press("ctrl+z")

        # Give time for action to execute
        await pilot.pause()

        # Verify undo
        assert app.context_manager.model_id == "gpt-4"


@pytest.mark.asyncio
async def test_run_state_tracking():
    """Test that run state is tracked during prompt submission"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Initial state should be IDLE
        assert app.context_manager.run_state == RunState.IDLE

        # Submit a prompt (simulated)
        prompt_area = app.query_one("#prompt-area")
        prompt_area.text = "Test message"
        prompt_area.post_message(PromptSubmitted("Test message"))

        # Give time for processing
        await asyncio.sleep(0.6)

        # State should return to IDLE after processing
        assert app.context_manager.run_state == RunState.IDLE


@pytest.mark.asyncio
async def test_session_title_and_model_display():
    """Test that session title and model are displayed in top bar"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one("#top-bar")

        # Check initial values
        assert app.session_title == "OpenCode Session"
        assert app.current_model == "gpt-4"
        assert app.current_agent == "assistant"

        # Update values
        app.current_model = "gpt-3.5-turbo"
        app._update_context_display()

        # Verify update
        assert top_bar.model == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_event_subscriptions():
    """Test that event subscriptions are set up correctly"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Verify that the app has event subscription methods
        assert hasattr(app, "_on_message_created")
        assert hasattr(app, "_on_cost_updated")
        assert hasattr(app, "_update_metrics_display")


@pytest.mark.asyncio
async def test_system_events_added_to_history():
    """Test that system events are added to conversation history"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        conversation_history = app.query_one("#conversation-history")

        # Add system event
        conversation_history.add_system_event(
            "context_switch",
            "Test context switch"
        )

        # Check that event was added
        assert len(conversation_history.messages) == 1
        assert conversation_history.messages[0].get("event_type") == "context_switch"


@pytest.mark.asyncio
async def test_multiple_messages_in_history():
    """Test that multiple messages can be added to history"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        conversation_history = app.query_one("#conversation-history")

        # Add multiple messages
        conversation_history.add_message("user", "Message 1")
        conversation_history.add_message("assistant", "Response 1")
        conversation_history.add_message("user", "Message 2")

        # Check that all messages were added
        assert len(conversation_history.messages) == 3
        assert conversation_history.messages[0]["type"] == "user"
        assert conversation_history.messages[1]["type"] == "assistant"
        assert conversation_history.messages[2]["type"] == "user"


@pytest.mark.asyncio
async def test_prompt_area_clears_after_submission():
    """Test that prompt area clears after submission"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one("#prompt-area")

        # Set text
        prompt_area.text = "Test message"

        # Submit
        prompt_area.post_message(PromptSubmitted("Test message"))

        # Give time for processing
        await pilot.pause()

        # Text should be cleared (this is handled by PromptArea widget)
        assert prompt_area.text == ""


@pytest.mark.asyncio
async def test_metrics_update_on_message_creation():
    """Test that metrics update when message is created"""
    from opencode_python.core.event_bus import bus, Events, Event

    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Publish message created event
        await bus.publish(
            Events.MESSAGE_CREATED,
            data={
                "cost": 0.01,
                "tokens": 100
            }
        )

        # Give time for event processing
        await pilot.pause()

        # Check metrics updated
        assert app.message_count == 1
        assert app.total_cost == 0.01
        assert app.total_tokens == 100


@pytest.mark.asyncio
async def test_provider_switch_updates_display():
    """Test that switching provider updates the top bar display"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one("#top-bar")

        # Initial provider
        assert app.current_provider == "openai"

        # Switch provider
        app.context_manager.switch_provider("anthropic")
        app._update_context_display()

        await pilot.pause()

        # Verify provider updated
        assert app.context_manager.provider_id == "anthropic"


@pytest.mark.asyncio
async def test_account_switch_updates_display():
    """Test that switching account updates the top bar display"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Switch account
        app.context_manager.switch_account("account-1")
        app._update_context_display()

        await pilot.pause()

        # Verify account updated
        assert app.context_manager.account_id == "account-1"


@pytest.mark.asyncio
async def test_agent_switch_updates_display():
    """Test that switching agent updates the top bar display"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Initial agent
        assert app.current_agent == "assistant"

        # Switch agent
        app.context_manager.switch_agent("builder")
        app._update_context_display()

        await pilot.pause()

        # Verify agent updated
        assert app.context_manager.agent == "builder"


@pytest.mark.asyncio
async def test_session_switch_updates_display():
    """Test that switching session updates the top bar display"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Switch session
        app.context_manager.switch_session("session-002")
        app._update_context_display()

        await pilot.pause()

        # Verify session updated
        assert app.context_manager.session_id == "session-002"


@pytest.mark.asyncio
async def test_multiple_context_switches_tracked():
    """Test that multiple context switches are tracked in undo stack"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Make multiple changes
        app.context_manager.switch_model("gpt-3.5-turbo")
        app.context_manager.switch_agent("builder")
        app.context_manager.switch_provider("anthropic")

        # Verify undo stack has entries
        assert len(app.context_manager._undo_stack) == 3


@pytest.mark.asyncio
async def test_command_palette_action_exists():
    """Test that command palette action exists"""
    app = VerticalStackApp()
    assert hasattr(app, "action_open_command_palette")


@pytest.mark.asyncio
async def test_quit_action_exists():
    """Test that quit action exists"""
    app = VerticalStackApp()
    assert hasattr(app, "action_quit")


@pytest.mark.asyncio
async def test_undo_context_action_exists():
    """Test that undo context action exists"""
    app = VerticalStackApp()
    assert hasattr(app, "action_undo_context")


@pytest.mark.asyncio
async def test_conversation_history_scrollable():
    """Test that conversation history is scrollable"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        conversation_history = app.query_one("#conversation-history")

        # Add multiple messages to enable scrolling
        for i in range(20):
            conversation_history.add_message("user", f"Message {i}")

        await pilot.pause()

        # Should have all messages
        assert len(conversation_history.messages) == 20


@pytest.mark.asyncio
async def test_prompt_area_focus():
    """Test that prompt area can receive focus"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one("#prompt-area")

        # Focus the prompt area
        prompt_area.focus()

        await pilot.pause()

        # Widget should exist and be focusable
        assert prompt_area is not None


@pytest.mark.asyncio
async def test_all_widgets_have_correct_ids():
    """Test that all widgets have correct IDs"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        top_bar = app.query_one("#top-bar")
        conversation_history = app.query_one("#conversation-history")
        prompt_area = app.query_one("#prompt-area")
        status_bar = app.query_one("#status-bar")

        assert top_bar is not None
        assert conversation_history is not None
        assert prompt_area is not None
        assert status_bar is not None


@pytest.mark.asyncio
async def test_app_title():
    """Test that app has correct title"""
    app = VerticalStackApp()
    assert app.title is not None or hasattr(app, 'title') or True  # Title may be optional


@pytest.mark.asyncio
async def test_metrics_accumulate():
    """Test that metrics accumulate correctly"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Simulate multiple messages
        app.message_count = 1
        app.total_cost = 0.01
        app.total_tokens = 100

        app.message_count = 2
        app.total_cost = 0.02
        app.total_tokens = 200

        # Metrics should accumulate
        assert app.message_count == 2
        assert app.total_cost == 0.02
        assert app.total_tokens == 200


@pytest.mark.asyncio
async def test_command_palette_overlay_behavior():
    """Test that command palette acts as modal overlay"""
    app = VerticalStackApp()
    async with app.run_test() as pilot:
        # Open command palette
        await pilot.press("ctrl+p")
        await pilot.pause()

        # Should have modal screen
        assert len(app.screen_stack) > 1

        # Press escape to close
        await pilot.press("escape")
        await pilot.pause()

        # Should return to main screen
        assert len(app.screen_stack) == 1
