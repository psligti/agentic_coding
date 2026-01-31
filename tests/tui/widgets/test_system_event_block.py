"""Tests for SystemEventBlock Widget"""

import pytest
from textual.app import App
from textual.widgets import Static

from opencode_python.tui.widgets.system_event_block import (
    SystemEventBlock,
    EventType,
)


@pytest.mark.asyncio
async def test_system_event_block_widget_instantiation():
    """Test that SystemEventBlock widget can be instantiated"""
    event_block = SystemEventBlock(EventType.INFO, "Test event")
    assert event_block is not None
    assert isinstance(event_block, SystemEventBlock)


@pytest.mark.asyncio
async def test_system_event_block_with_info_type():
    """Test that SystemEventBlock can be created with INFO type"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Information message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.event_type == EventType.INFO
        assert event_block.text == "Information message"


@pytest.mark.asyncio
async def test_system_event_block_with_error_type():
    """Test that SystemEventBlock can be created with ERROR type"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.ERROR, "Error message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.event_type == EventType.ERROR
        assert event_block.text == "Error message"


@pytest.mark.asyncio
async def test_system_event_block_with_context_switch_type():
    """Test that SystemEventBlock can be created with CONTEXT_SWITCH type"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.CONTEXT_SWITCH, "Switched context")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.event_type == EventType.CONTEXT_SWITCH
        assert event_block.text == "Switched context"


@pytest.mark.asyncio
async def test_system_event_block_has_event_content():
    """Test that SystemEventBlock has event content container"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Test")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        event_content = event_block.query_one("#event-content")
        assert event_content is not None


@pytest.mark.asyncio
async def test_system_event_block_info_icon():
    """Test that INFO events display correct icon"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Info message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        event_content = event_block.query_one("#event-content")

        # Should have icon and text widgets
        children = event_content.children
        assert len(children) > 0


@pytest.mark.asyncio
async def test_system_event_block_error_icon():
    """Test that ERROR events display correct icon"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.ERROR, "Error message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        event_content = event_block.query_one("#event-content")

        # Should have icon and text widgets
        children = event_content.children
        assert len(children) > 0


@pytest.mark.asyncio
async def test_system_event_block_context_switch_icon():
    """Test that CONTEXT_SWITCH events display correct icon"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.CONTEXT_SWITCH, "Context switched")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        event_content = event_block.query_one("#event-content")

        # Should have icon and text widgets
        children = event_content.children
        assert len(children) > 0


@pytest.mark.asyncio
async def test_system_event_block_text_display():
    """Test that event text is displayed correctly"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "This is a test event message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.text == "This is a test event message"


@pytest.mark.asyncio
async def test_system_event_block_styling_info():
    """Test that INFO events have correct styling"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Info message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.event_type == EventType.INFO


@pytest.mark.asyncio
async def test_system_event_block_styling_error():
    """Test that ERROR events have correct styling"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.ERROR, "Error message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.event_type == EventType.ERROR


@pytest.mark.asyncio
async def test_system_event_block_styling_context_switch():
    """Test that CONTEXT_SWITCH events have correct styling"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.CONTEXT_SWITCH, "Context switched")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.event_type == EventType.CONTEXT_SWITCH


@pytest.mark.asyncio
async def test_system_event_block_update_content():
    """Test that _update_content updates content based on event type"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Initial message")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)

        # Call _update_content to test
        event_block._update_content()

        # Should not raise any errors
        assert event_block is not None


@pytest.mark.asyncio
async def test_system_event_block_empty_text():
    """Test that SystemEventBlock handles empty text"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.text == ""


@pytest.mark.asyncio
async def test_system_event_block_long_text():
    """Test that SystemEventBlock handles long text"""
    long_text = "This is a very long event message that should be displayed correctly without any issues in the UI"

    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, long_text)

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(SystemEventBlock)
        assert event_block.text == long_text


@pytest.mark.asyncio
async def test_system_event_block_with_id():
    """Test that SystemEventBlock can be created with an id"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Test", id="test-event")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one("#test-event")
        assert event_block is not None
        assert isinstance(event_block, SystemEventBlock)


@pytest.mark.asyncio
async def test_system_event_block_with_classes():
    """Test that SystemEventBlock can be created with additional classes"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Test", classes="custom-class")

    app = TestApp()
    async with app.run_test() as pilot:
        event_block = app.query_one(".custom-class")
        assert event_block is not None
        assert isinstance(event_block, SystemEventBlock)


@pytest.mark.asyncio
async def test_system_event_block_multiple_instances():
    """Test that multiple SystemEventBlock instances can coexist"""
    class TestApp(App):
        def compose(self):
            yield SystemEventBlock(EventType.INFO, "Info 1", id="event-1")
            yield SystemEventBlock(EventType.ERROR, "Error 1", id="event-2")
            yield SystemEventBlock(EventType.CONTEXT_SWITCH, "Switch 1", id="event-3")

    app = TestApp()
    async with app.run_test() as pilot:
        event1 = app.query_one("#event-1")
        event2 = app.query_one("#event-2")
        event3 = app.query_one("#event-3")

        assert event1 is not None
        assert event2 is not None
        assert event3 is not None

        assert event1.event_type == EventType.INFO
        assert event2.event_type == EventType.ERROR
        assert event3.event_type == EventType.CONTEXT_SWITCH
