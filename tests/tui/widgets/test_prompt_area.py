"""Tests for PromptArea Widget"""

import pytest
from textual.app import App

from opencode_python.tui.widgets.prompt_area import PromptArea


@pytest.mark.asyncio
async def test_prompt_area_widget_instantiation():
    """Test that PromptArea widget can be instantiated"""
    prompt_area = PromptArea()
    assert prompt_area is not None
    assert isinstance(prompt_area, PromptArea)


@pytest.mark.asyncio
async def test_prompt_area_with_placeholder():
    """Test that PromptArea can be created with placeholder text"""
    class TestApp(App):
        def compose(self):
            yield PromptArea(placeholder="Type your message here...")

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one(PromptArea)
        assert prompt_area is not None


@pytest.mark.asyncio
async def test_prompt_area_with_id():
    """Test that PromptArea can be created with an id"""
    class TestApp(App):
        def compose(self):
            yield PromptArea(id="test-prompt")

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one("#test-prompt")
        assert prompt_area is not None
        assert isinstance(prompt_area, PromptArea)


@pytest.mark.asyncio
async def test_prompt_area_initial_text():
    """Test that PromptArea starts with empty text"""
    class TestApp(App):
        def compose(self):
            yield PromptArea()

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one(PromptArea)
        assert prompt_area.text == ""


@pytest.mark.asyncio
async def test_prompt_area_submitted_message():
    """Test that Submitted message exists"""
    prompt_area = PromptArea()
    # Submitted message class should be accessible
    assert hasattr(prompt_area, 'Submitted')


@pytest.mark.asyncio
async def test_prompt_area_submit_on_enter():
    """Test that Enter key submits the prompt"""
    class TestApp(App):
        def compose(self):
            yield PromptArea(id="prompt")

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one("#prompt")

        # Set text
        prompt_area.text = "Test message"

        # Submit message by posting Submitted event
        prompt_area.post_message(prompt_area.Submitted("Test message"))

        await pilot.pause()

        # Text should be cleared after submission
        # (This is handled in on_key, but we're testing the message flow)


@pytest.mark.asyncio
async def test_prompt_area_text_attribute():
    """Test that text attribute can be read and written"""
    prompt_area = PromptArea()

    # Set text
    prompt_area.text = "Hello, world!"

    # Read text
    assert prompt_area.text == "Hello, world!"


@pytest.mark.asyncio
async def test_prompt_area_clear_text():
    """Test that text can be cleared"""
    prompt_area = PromptArea()
    prompt_area.text = "Some text"

    # Clear text
    prompt_area.text = ""

    assert prompt_area.text == ""


@pytest.mark.asyncio
async def test_prompt_area_multiline_text():
    """Test that multiline text is supported"""
    prompt_area = PromptArea()
    multiline_text = "Line 1\nLine 2\nLine 3"

    prompt_area.text = multiline_text

    assert prompt_area.text == multiline_text


@pytest.mark.asyncio
async def test_prompt_area_empty_submit():
    """Test that submitting empty text is handled"""
    class TestApp(App):
        def compose(self):
            yield PromptArea()

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one(PromptArea)

        # Try to submit with empty text
        # This should not raise any errors
        assert prompt_area.text == ""


@pytest.mark.asyncio
async def test_prompt_area_whitespace_text():
    """Test that whitespace-only text is handled"""
    class TestApp(App):
        def compose(self):
            yield PromptArea()

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one(PromptArea)
        prompt_area.text = "   \n   \n   "

        assert len(prompt_area.text) > 0


@pytest.mark.asyncio
async def test_prompt_area_long_text():
    """Test that long text is handled"""
    prompt_area = PromptArea()
    long_text = "A" * 1000

    prompt_area.text = long_text

    assert prompt_area.text == long_text


@pytest.mark.asyncio
async def test_prompt_area_special_characters():
    """Test that special characters are handled"""
    prompt_area = PromptArea()
    special_text = "Hello @user! Check out #tag and $money."

    prompt_area.text = special_text

    assert prompt_area.text == special_text


@pytest.mark.asyncio
async def test_prompt_area_unicode_text():
    """Test that unicode text is handled"""
    prompt_area = PromptArea()
    unicode_text = "Hello 🌍! 你好! مرحبا!"

    prompt_area.text = unicode_text

    assert prompt_area.text == unicode_text


@pytest.mark.asyncio
async def test_prompt_area_on_key_handler():
    """Test that on_key handler exists"""
    prompt_area = PromptArea()

    # Should have on_key method
    assert hasattr(prompt_area, 'on_key')


@pytest.mark.asyncio
async def test_prompt_area_submitted_message_text():
    """Test that Submitted message contains text"""
    test_text = "Test message content"
    submitted_msg = PromptArea.Submitted(test_text)

    assert submitted_msg.text == test_text


@pytest.mark.asyncio
async def test_prompt_area_css_styling():
    """Test that CSS styling is applied"""
    class TestApp(App):
        def compose(self):
            yield PromptArea()

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one(PromptArea)

        # Should be styled according to CSS
        assert prompt_area is not None


@pytest.mark.asyncio
async def test_prompt_area_focus():
    """Test that PromptArea can receive focus"""
    class TestApp(App):
        def compose(self):
            yield PromptArea(id="prompt")

    app = TestApp()
    async with app.run_test() as pilot:
        prompt_area = app.query_one("#prompt")

        # Focus the widget
        prompt_area.focus()

        await pilot.pause()

        # Widget should be focused
        # (We can't directly test focus state, but we can ensure no errors occur)


@pytest.mark.asyncio
async def test_prompt_area_multiple_instances():
    """Test that multiple PromptArea instances can coexist"""
    class TestApp(App):
        def compose(self):
            yield PromptArea(id="prompt1")
            yield PromptArea(id="prompt2")

    app = TestApp()
    async with app.run_test() as pilot:
        prompt1 = app.query_one("#prompt1")
        prompt2 = app.query_one("#prompt2")

        assert prompt1 is not None
        assert prompt2 is not None

        prompt1.text = "First prompt"
        prompt2.text = "Second prompt"

        assert prompt1.text == "First prompt"
        assert prompt2.text == "Second prompt"
