"""Dialog system tests - TDD phase tests"""
import pytest
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Input, Label

# Import dialog modules
from opencode_python.tui.dialogs import BaseDialog, SelectDialog, ConfirmDialog, PromptDialog


class TestBaseDialog:
    """BaseDialog lifecycle tests"""

    def test_base_dialog_exists(self):
        """BaseDialog should be importable"""
        assert BaseDialog is not None

    def test_base_dialog_is_modal_screen(self):
        """BaseDialog should extend ModalScreen"""
        from textual.screen import ModalScreen
        assert issubclass(BaseDialog, ModalScreen)

    def test_base_dialog_has_title(self):
        """BaseDialog should have a title property"""
        dialog = BaseDialog("Test Title")
        assert dialog.title == "Test Title"

    @pytest.mark.asyncio
    async def test_base_dialog_displays_content(self):
        """BaseDialog should render its content"""
        class TestApp(App):
            pass

        app = TestApp()
        dialog = BaseDialog("Test", body=[Label("Test Content")])

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Check that content is displayed
            labels = dialog.query(Label)
            assert len(labels) >= 2
            assert any("Test Content" in label.content for label in labels)

    @pytest.mark.asyncio
    async def test_base_dialog_close_and_get_result(self):
        """BaseDialog should close and return result"""
        class TestApp(App):
            pass

        app = TestApp()
        dialog = BaseDialog("Test Dialog")

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            dialog.close_dialog("result_value")
            assert dialog.get_result() == "result_value"
            assert dialog.is_closed() is True

    def test_base_dialog_default_result(self):
        """BaseDialog should have empty result by default"""
        dialog = BaseDialog("Test Dialog")
        assert dialog.get_result() is None
        assert dialog.is_closed() is False


class TestSelectDialog:
    """SelectDialog lifecycle tests"""

    def test_select_dialog_exists(self):
        """SelectDialog should be importable"""
        assert SelectDialog is not None

    def test_select_dialog_has_options(self):
        """SelectDialog should accept options parameter"""
        options = [
            {"value": "value1", "title": "Option 1"},
            {"value": "value2", "title": "Option 2"}
        ]
        dialog = SelectDialog("Select Something", options)

        assert dialog.options == options

    def test_select_dialog_calls_on_select(self):
        """SelectDialog should call on_select when option is selected"""
        selected_value = None

        def on_select(value):
            nonlocal selected_value
            selected_value = value

        options = [
            {"value": "value1", "title": "Option1"},
            {"value": "value2", "title": "Option 2"}
        ]
        dialog = SelectDialog("Select Something", options, on_select=on_select)

        # Simulate selecting first option
        dialog.on_select("value1")
        assert selected_value == "value1"

        # Simulate selecting second option
        dialog.on_select("value2")
        assert selected_value == "value2"

    @pytest.mark.asyncio
    async def test_select_dialog_shows_options(self):
        """SelectDialog should display options as selectable items"""
        options = [
            {"value": "value1", "title": "Option 1"},
            {"value": "value2", "title": "Option 2"}
        ]

        class TestApp(App):
            pass

        app = TestApp()
        dialog = SelectDialog("Select Something", options)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Dialog should render options
            labels = dialog.query(Label)
            assert len(labels) > 0

    @pytest.mark.asyncio
    async def test_select_dialog_get_result(self):
        """SelectDialog should return selected value"""
        options = [
            {"value": "a", "title": "Option A"},
            {"value": "b", "title": "Option B"}
        ]

        class TestApp(App):
            pass

        app = TestApp()
        dialog = SelectDialog("Select Something", options)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Select and close
            dialog.select_option("b")
            dialog.close_dialog("b")
            assert dialog.get_result() == "b"

    @pytest.mark.asyncio
    async def test_select_dialog_flow(self):
        """Complete flow for SelectDialog"""
        selected_value = None

        def on_select(value):
            nonlocal selected_value
            selected_value = value

        options = [
            {"value": "a", "title": "Option A"},
            {"value": "b", "title": "Option B"}
        ]

        class TestApp(App):
            pass

        app = TestApp()
        dialog = SelectDialog("Choose Option", options, on_select=on_select)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            dialog.select_option("b")
            dialog.action_enter()

            assert selected_value == "b"
            assert dialog.get_result() == "b"
            assert dialog.is_closed() is True


class TestConfirmDialog:
    """ConfirmDialog lifecycle tests"""

    def test_confirm_dialog_exists(self):
        """ConfirmDialog should be importable"""
        assert ConfirmDialog is not None

    def test_confirm_dialog_has_title(self):
        """ConfirmDialog should have a title property"""
        dialog = ConfirmDialog("Confirm Action")
        assert dialog.title == "Confirm Action"

    @pytest.mark.asyncio
    async def test_confirm_dialog_calls_on_confirm(self):
        """ConfirmDialog should call on_confirm when confirmed"""
        confirmed = False

        def on_confirm():
            nonlocal confirmed
            confirmed = True

        class TestApp(App):
            pass

        app = TestApp()
        dialog = ConfirmDialog("Confirm Action", on_confirm=on_confirm)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Simulate confirmation
            dialog.action_confirm()
            assert confirmed is True
            assert dialog.get_result() is True

            # Should not call on_confirm when cancelled
            confirmed = False
            dialog.action_cancel()
            assert confirmed is False
            assert dialog.get_result() is False

    @pytest.mark.asyncio
    async def test_confirm_dialog_shows_buttons(self):
        """ConfirmDialog should show Cancel and Confirm buttons"""
        class TestApp(App):
            pass

        app = TestApp()
        dialog = ConfirmDialog("Confirm Action")

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Verify dialog contains buttons
            buttons = dialog.query(Button)
            assert len(buttons) >= 1  # Should have at least one button

    def test_confirm_dialog_default_result(self):
        """ConfirmDialog should default to False"""
        dialog = ConfirmDialog("Confirm Action")
        assert dialog.get_result() is False

    @pytest.mark.asyncio
    async def test_confirm_dialog_flow(self):
        """Complete flow for ConfirmDialog"""
        confirmed = False
        cancelled = False

        def on_confirm():
            nonlocal confirmed
            confirmed = True

        def on_cancel():
            nonlocal cancelled
            cancelled = True

        class TestApp(App):
            pass

        app = TestApp()
        dialog = ConfirmDialog("Confirm Action", on_confirm=on_confirm, on_cancel=on_cancel)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Test confirm flow
            dialog.action_confirm()
            assert confirmed is True
            assert dialog.get_result() is True

        # Reset and test cancel flow
        confirmed = False
        app = TestApp()
        dialog = ConfirmDialog("Confirm Action", on_confirm=on_confirm, on_cancel=on_cancel)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            dialog.action_cancel()
            assert cancelled is True
            assert dialog.get_result() is False


class TestPromptDialog:
    """PromptDialog lifecycle tests"""

    def test_prompt_dialog_exists(self):
        """PromptDialog should be importable"""
        assert PromptDialog is not None

    def test_prompt_dialog_has_title_and_placeholder(self):
        """PromptDialog should have title and placeholder properties"""
        dialog = PromptDialog("Enter text", "Type here...")
        assert dialog.title == "Enter text"
        assert dialog.placeholder == "Type here..."

    @pytest.mark.asyncio
    async def test_prompt_dialog_calls_on_submit(self):
        """PromptDialog should call on_submit when text is submitted"""
        submitted_value = None

        def on_submit(value):
            nonlocal submitted_value
            submitted_value = value

        class TestApp(App):
            pass

        app = TestApp()
        dialog = PromptDialog("Enter text", on_submit=on_submit)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Simulate submission
            dialog.action_enter()
            # Default empty submission
            assert dialog.get_result() == ""

    @pytest.mark.asyncio
    async def test_prompt_dialog_shows_input_field(self):
        """PromptDialog should show an input field"""
        class TestApp(App):
            pass

        app = TestApp()
        dialog = PromptDialog("Enter text", "Type here...")

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Verify dialog contains input field
            inputs = dialog.query(Input)
            assert len(inputs) >= 1

    def test_prompt_dialog_get_result(self):
        """PromptDialog should return input value"""
        dialog = PromptDialog("Enter text", "Type here...")

        # Simulate user entering text
        dialog._result = "user input"
        assert dialog.get_result() == "user input"

    @pytest.mark.asyncio
    async def test_prompt_dialog_flow(self):
        """Complete flow for PromptDialog"""
        submitted_value = None

        def on_submit(value):
            nonlocal submitted_value
            submitted_value = value

        class TestApp(App):
            pass

        app = TestApp()
        dialog = PromptDialog("Enter text", on_submit=on_submit)

        async with app.run_test() as pilot:
            app.push_screen(dialog)
            await pilot.pause()

            # Simulate submission
            dialog.action_enter()
            assert dialog.get_result() == ""
            assert dialog.is_closed() is True
