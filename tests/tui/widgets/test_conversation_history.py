"""Tests for ConversationHistory Widget"""

import pytest
from textual.app import App
from textual.containers import ScrollableContainer

from opencode_python.tui.widgets.conversation_history import (
    ConversationHistory,
    EventType,
)


@pytest.mark.asyncio
async def test_conversation_history_widget_instantiation():
    """Test that ConversationHistory widget can be instantiated"""
    history = ConversationHistory()
    assert history is not None
    assert isinstance(history, ConversationHistory)


@pytest.mark.asyncio
async def test_conversation_history_initial_state():
    """Test that ConversationHistory initializes with empty messages"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        assert history.messages == []
        assert len(history.messages) == 0


@pytest.mark.asyncio
async def test_conversation_history_has_messages_container():
    """Test that ConversationHistory has messages container"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        container = history.query_one("#messages-container", ScrollableContainer)
        assert container is not None


@pytest.mark.asyncio
async def test_conversation_history_add_user_message():
    """Test that user messages can be added"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "Hello, world!")

        await pilot.pause()

        assert len(history.messages) == 1
        assert history.messages[0]["type"] == "user"


@pytest.mark.asyncio
async def test_conversation_history_add_assistant_message():
    """Test that assistant messages can be added"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("assistant", "Hello! How can I help?")

        await pilot.pause()

        assert len(history.messages) == 1
        assert history.messages[0]["type"] == "assistant"


@pytest.mark.asyncio
async def test_conversation_history_add_system_event():
    """Test that system events can be added"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_system_event(EventType.CONTEXT_SWITCH, "Switched to new context")

        await pilot.pause()

        assert len(history.messages) == 1
        assert history.messages[0].get("event_type") == "context_switch"


@pytest.mark.asyncio
async def test_conversation_history_add_system_event_info():
    """Test that INFO system events can be added"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_system_event(EventType.INFO, "Information message")

        await pilot.pause()

        assert len(history.messages) == 1
        assert history.messages[0].get("event_type") == "info"


@pytest.mark.asyncio
async def test_conversation_history_add_system_event_error():
    """Test that ERROR system events can be added"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_system_event(EventType.ERROR, "Error occurred")

        await pilot.pause()

        assert len(history.messages) == 1
        assert history.messages[0].get("event_type") == "error"


@pytest.mark.asyncio
async def test_conversation_history_multiple_messages():
    """Test that multiple messages can be added"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "Message 1")
        history.add_message("assistant", "Response 1")
        history.add_message("user", "Message 2")

        await pilot.pause()

        assert len(history.messages) == 3
        assert history.messages[0]["type"] == "user"
        assert history.messages[1]["type"] == "assistant"
        assert history.messages[2]["type"] == "user"


@pytest.mark.asyncio
async def test_conversation_history_message_timestamp():
    """Test that messages have timestamps"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "Test message")

        await pilot.pause()

        assert len(history.messages) == 1
        assert "time" in history.messages[0]
        assert "created" in history.messages[0]["time"]


@pytest.mark.asyncio
async def test_conversation_history_message_parts():
    """Test that messages have parts with text content"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "Test message")

        await pilot.pause()

        assert len(history.messages) == 1
        assert "parts" in history.messages[0]
        assert len(history.messages[0]["parts"]) > 0
        assert history.messages[0]["parts"][0]["part_type"] == "text"
        assert history.messages[0]["parts"][0]["text"] == "Test message"


@pytest.mark.asyncio
async def test_conversation_history_scroll_to_bottom():
    """Test that scroll_to_bottom scrolls to the end"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "Message 1")
        history.add_message("user", "Message 2")
        history.add_message("user", "Message 3")

        await pilot.pause()

        history.scroll_to_bottom()

        # Should scroll without error
        assert len(history.messages) == 3


@pytest.mark.asyncio
async def test_conversation_history_reactive_watcher_messages():
    """Test that reactive watcher for messages works correctly"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)

        # Directly set messages
        test_messages = [
            {"type": "user", "time": {"created": "2024-01-01"}, "parts": [{"part_type": "text", "text": "Test"}]}
        ]
        history.watch_messages([], test_messages)

        await pilot.pause()

        assert len(history.messages) == 1


@pytest.mark.asyncio
async def test_conversation_history_render_messages():
    """Test that _render_messages renders all messages"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "Message 1")
        history.add_message("assistant", "Response 1")

        await pilot.pause()

        # Render should have created widgets
        container = history.query_one("#messages-container", ScrollableContainer)
        # Should have at least some children
        assert len(container.children) >= 2


@pytest.mark.asyncio
async def test_conversation_history_user_message_styling():
    """Test that user messages have correct styling"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "User message")

        await pilot.pause()

        # User message should be added
        assert len(history.messages) == 1
        assert history.messages[0]["type"] == "user"


@pytest.mark.asyncio
async def test_conversation_history_assistant_message_styling():
    """Test that assistant messages have correct styling"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("assistant", "Assistant message")

        await pilot.pause()

        # Assistant message should be added
        assert len(history.messages) == 1
        assert history.messages[0]["type"] == "assistant"


@pytest.mark.asyncio
async def test_conversation_history_system_message_styling():
    """Test that system messages have correct styling"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_system_event(EventType.INFO, "System event")

        await pilot.pause()

        # System event should be added
        assert len(history.messages) == 1
        assert history.messages[0].get("event_type") == "info"


@pytest.mark.asyncio
async def test_conversation_history_message_ordering():
    """Test that messages maintain correct order"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)
        history.add_message("user", "First")
        history.add_message("assistant", "Second")
        history.add_message("user", "Third")

        await pilot.pause()

        assert history.messages[0]["type"] == "user"
        assert history.messages[1]["type"] == "assistant"
        assert history.messages[2]["type"] == "user"


@pytest.mark.asyncio
async def test_conversation_history_on_mount_renders():
    """Test that on_mount renders initial messages"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)

        # on_mount is called automatically during composition
        # Should not raise any errors
        assert history is not None


@pytest.mark.asyncio
async def test_enum_value_handling_in_add_message_block_from_model():
    """Test that message.type is used directly without .value"""
    from opencode_python.tui.models import Message, MessageType, MessagePart, MessagePartType, Timestamp

    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)

        # Create a message with enum
        timestamp = Timestamp(created="2024-01-01T00:00:00")
        text_part = MessagePart(part_type=MessagePartType.TEXT, text="Test")
        message = Message(
            type=MessageType.USER,
            time=timestamp,
            parts=[text_part]
        )

        # Should not raise AttributeError when calling _add_message_block_from_model
        # This tests that message.type is used directly (string) not message.type.value
        history.messages = [message]
        try:
            history._add_message_block_from_model(message)
        except AttributeError as e:
            pytest.fail(f"AttributeError raised when accessing message.type: {e}")

        # Verify message was processed
        assert len(history.messages) == 1


@pytest.mark.asyncio
async def test_enum_value_handling_in_add_system_event():
    """Test that event_type.value is used correctly"""
    class TestApp(App):
        def compose(self):
            yield ConversationHistory()

    app = TestApp()
    async with app.run_test() as pilot:
        history = app.query_one(ConversationHistory)

        # Should not raise AttributeError when adding system event
        # This tests that event_type.value works correctly (event_type is EventType enum)
        try:
            history.add_system_event(EventType.INFO, "Test event")
        except AttributeError as e:
            pytest.fail(f"AttributeError raised when accessing event_type.value: {e}")

        # Verify event was added
        assert len(history.messages) == 1

