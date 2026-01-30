"""Tests for ConfirmationDialog component"""
import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button

from opencode_python.observability.confirmation_dialog import ConfirmationDialog


@pytest.fixture
def basic_dialog():
    """Create a basic confirmation dialog for testing"""
    return ConfirmationDialog(
        title="DELETE FILES?",
        detail_text="This will permanently delete all selected files.",
    )


@pytest.fixture
def dialog_with_callbacks():
    """Create a confirmation dialog with callbacks for testing"""
    confirmed = [False]
    cancelled = [False]

    async def on_confirm():
        confirmed[0] = True

    async def on_cancel():
        cancelled[0] = True

    dialog = ConfirmationDialog(
        title="RESET HARD?",
        detail_text="All uncommitted changes will be lost forever.",
        on_confirm=on_confirm,
        on_cancel=on_cancel,
    )

    return dialog, confirmed, cancelled


class TestConfirmationDialogBasics:
    """Basic functionality tests for ConfirmationDialog"""

    def test_dialog_imports(self):
        """ConfirmationDialog should be importable"""
        assert ConfirmationDialog is not None

    def test_dialog_is_modal_screen(self):
        """ConfirmationDialog should extend ModalScreen"""
        from textual.screen import ModalScreen
        assert issubclass(ConfirmationDialog, ModalScreen)

    def test_dialog_has_title(self, basic_dialog):
        """Dialog should store the title"""
        assert basic_dialog.title == "DELETE FILES?"

    def test_dialog_has_detail_text(self, basic_dialog):
        """Dialog should store the detail text"""
        assert basic_dialog.detail_text == "This will permanently delete all selected files."

    def test_dialog_default_result(self, basic_dialog):
        """Dialog should default to not confirmed"""
        assert basic_dialog.get_result() is False
        assert basic_dialog.is_confirmed() is False

    @pytest.mark.asyncio
    async def test_dialog_displays_warning_icon(self, basic_dialog):
        """Dialog should display a warning icon"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            warning_icon = dialog.query_one("#warning_icon")
            assert warning_icon is not None

    @pytest.mark.asyncio
    async def test_dialog_displays_title(self, basic_dialog):
        """Dialog should display the title"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            title = dialog.query_one("#dialog_title")
            assert title is not None

    @pytest.mark.asyncio
    async def test_dialog_displays_detail_text(self, basic_dialog):
        """Dialog should display the detail text"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            detail = dialog.query_one("#detail_text")
            assert detail is not None


class TestConfirmationDialogButtons:
    """Button interaction tests for ConfirmationDialog"""

    @pytest.mark.asyncio
    async def test_dialog_has_yes_and_no_buttons(self, basic_dialog):
        """Dialog should have both Yes and No buttons"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            buttons = dialog.query(Button)
            assert len(buttons) == 2

            yes_button = dialog.query_one("#btn_yes", Button)
            no_button = dialog.query_one("#btn_no", Button)

            assert yes_button.label == "Yes, I understand"
            assert no_button.label == "No, cancel"

    @pytest.mark.asyncio
    async def test_yes_button_confirm_action(self, basic_dialog):
        """Clicking Yes should confirm the action"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            assert dialog.get_result() is False

            await dialog.on_yes_pressed(None)

            assert dialog.get_result() is True
            assert dialog.is_confirmed() is True

    @pytest.mark.asyncio
    async def test_no_button_cancel_action(self, basic_dialog):
        """Clicking No should cancel the action"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            assert dialog.get_result() is False

            await dialog.on_no_pressed(None)

            assert dialog.get_result() is False
            assert dialog.is_confirmed() is False

    @pytest.mark.asyncio
    async def test_yes_button_higher_priority_danger(self, basic_dialog):
        """Yes button should use error variant for danger styling"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            yes_button = dialog.query_one("#btn_yes", Button)
            assert yes_button.variant == "error"

    @pytest.mark.asyncio
    async def test_no_button_default_variant(self, basic_dialog):
        """No button should use default variant"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            no_button = dialog.query_one("#btn_no", Button)
            assert no_button.variant == "default"


class TestConfirmationDialogCallbacks:
    """Callback tests for ConfirmationDialog"""

    @pytest.mark.asyncio
    async def test_on_confirm_callback_called(self, dialog_with_callbacks):
        """on_confirm callback should be called when Yes is clicked"""
        dialog, confirmed, cancelled = dialog_with_callbacks

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            await dialog.on_yes_pressed(None)

            assert confirmed[0] is True
            assert cancelled[0] is False

    @pytest.mark.asyncio
    async def test_on_cancel_callback_called(self, dialog_with_callbacks):
        """on_cancel callback should be called when No is clicked"""
        dialog, confirmed, cancelled = dialog_with_callbacks

        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            await dialog.on_no_pressed(None)

            assert confirmed[0] is False
            assert cancelled[0] is True

    @pytest.mark.asyncio
    async def test_callbacks_optional(self, basic_dialog):
        """Dialog should work without callbacks"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            await dialog.on_yes_pressed(None)

            assert dialog.get_result() is True


class TestConfirmationDialogKeyboardActions:
    """Keyboard action tests for ConfirmationDialog"""

    @pytest.mark.asyncio
    async def test_escape_key_cancels(self, basic_dialog):
        """Pressing Escape should cancel the action"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            dialog.action_escape()

            assert dialog.get_result() is False
            assert dialog.is_confirmed() is False

    @pytest.mark.asyncio
    async def test_cancel_action_works(self, basic_dialog):
        """Cancel action should work"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            dialog.action_cancel()

            assert dialog.get_result() is False
            assert dialog.is_confirmed() is False

    @pytest.mark.asyncio
    async def test_no_action_works(self, basic_dialog):
        """No action should work"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            dialog.action_no()

            assert dialog.get_result() is False

    @pytest.mark.asyncio
    async def test_yes_action_safe_by_default(self, basic_dialog):
        """Yes action should not work for safety (requires explicit click)"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            dialog.action_yes()

            assert dialog.is_confirmed() is False

    @pytest.mark.asyncio
    async def test_confirm_action_safe_by_default(self, basic_dialog):
        """Confirm action should not work for safety (requires explicit click)"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            dialog.action_confirm()

            assert dialog.is_confirmed() is False


class TestConfirmationDialogFocus:
    """Focus behavior tests for ConfirmationDialog"""

    @pytest.mark.asyncio
    async def test_no_button_focused_by_default(self, basic_dialog):
        """No button should be focused by default for safety"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            no_button = dialog.query_one("#btn_no", Button)

            await pilot.pause()

            assert no_button.has_focus is True

    @pytest.mark.asyncio
    async def test_dialog_mounts_successfully(self, basic_dialog):
        """Dialog should mount without errors"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog
            assert dialog is not None


class TestConfirmationDialogEdgeCases:
    """Edge case tests for ConfirmationDialog"""

    def test_empty_title_and_detail(self):
        """Dialog should handle empty title and detail text"""
        dialog = ConfirmationDialog("", "")
        assert dialog.title == ""
        assert dialog.detail_text == ""

    def test_very_long_title(self):
        """Dialog should handle very long titles"""
        long_title = "WARNING" * 20
        dialog = ConfirmationDialog(long_title, "Detail")
        assert dialog.title == long_title

    def test_markdown_in_detail_text(self):
        """Dialog should support markdown in detail text"""
        markdown_detail = "**Bold text** and *italic text*"
        dialog = ConfirmationDialog("Title", markdown_detail)
        assert dialog.detail_text == markdown_detail

    @pytest.mark.asyncio
    async def test_multiple_clicks_same_button(self, basic_dialog):
        """Multiple clicks on same button should not cause errors"""
        class TestApp(App):
            def compose(self) -> ComposeResult:
                self._dialog = basic_dialog
                yield self._dialog

        app = TestApp()
        async with app.run_test() as pilot:
            dialog = app._dialog

            await dialog.on_yes_pressed(None)
            await dialog.on_yes_pressed(None)
            await dialog.on_yes_pressed(None)

            assert dialog.get_result() is True
