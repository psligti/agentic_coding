"""OpenCode Python - Confirmation Dialog for Destructive Actions

Provides a modal dialog for confirming destructive operations with warning styling.
Designed for dangerous commands requiring explicit user consent.
"""
from __future__ import annotations

from typing import Optional, Callable, Awaitable

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Center
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, Markdown
from textual import on


class ConfirmationDialog(ModalScreen[bool]):
    """Modal confirmation dialog for destructive/dangerous actions.

    This dialog provides a clear, visually striking warning interface for dangerous operations.
    Uses explicit "Yes/No" button labels (not Confirm/Cancel) to increase user awareness.

    Args:
        title: Bold warning title displayed at the top
        detail_text: Detailed explanation of the action's consequences
        on_confirm: Async callback executed when user confirms
        on_cancel: Async callback executed when user cancels
    """

    DEFAULT_CSS = """
    ConfirmationDialog {
        height: auto;
        width: 90;
        align: center middle;
        background: $primary;
        border: thick panel;
        padding: 2;
    }

    ConfirmationDialog > Vertical {
        height: auto;
        width: 100%;
    }

    #dialog_title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin: 1 0;
    }

    #warning_icon {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin: 1 0;
    }

    #detail_text {
        text-align: center;
        margin: 1 0;
        text-style: italic;
    }

    #detail_text > Markdown {
        padding: 1;
    }

    #button_container {
        height: auto;
        align: center middle;
        margin-top: 2;
    }

    Button.-yes {
        width: 20;
        background: $error;
        color: $primary;
        border: heavy panel;
        text-style: bold;
        margin-right: 3;
    }

    Button.-yes:hover {
        background: $error;
        border: double panel;
        text-style: bold underline;
    }

    Button.-no {
        width: 20;
        background: $panel;
        color: $text;
        border: solid panel;
        margin-right: 1;
    }

    Button.-no:hover {
        background: $panel;
        border: double panel;
        text-style: bold;
    }

    #dialog_container {
        height: auto;
        width: 100%;
    }
    """

    def __init__(
        self,
        title: str,
        detail_text: str,
        on_confirm: Optional[Callable[[], Awaitable[None]]] = None,
        on_cancel: Optional[Callable[[], Awaitable[None]]] = None,
    ):
        """Initialize confirmation dialog.

        Args:
            title: Warning title (e.g., "DELETE FILES?")
            detail_text: Detailed message about what will happen
            on_confirm: Async callback executed when user confirms
            on_cancel: Async callback executed when user cancels
        """
        super().__init__()
        self.title = title
        self.detail_text = detail_text
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self._result: bool = False
        self._confirmed: bool = False

    def compose(self) -> ComposeResult:
        """Compose dialog widgets with warning styling."""
        yield Vertical(id="dialog_container")

        yield Static("⚠️  WARNING  ⚠️", id="warning_icon")

        if self.title:
            yield Label(self.title, id="dialog_title")

        yield Static("─" * 40, id="separator")

        yield Markdown(self.detail_text, id="detail_text")

        yield Horizontal(
            Button("Yes, I understand", id="btn_yes", variant="error", classes="-yes"),
            Button("No, cancel", id="btn_no", variant="default", classes="-no"),
            id="button_container",
        )

        yield Vertical()

    async def on_mount(self) -> None:
        """Called when dialog is mounted. Focus No button by default for safety."""
        try:
            no_button = self.query_one("#btn_no", Button)
            no_button.focus()
        except Exception:
            pass

    @on(Button.Pressed, "#btn_yes")
    async def on_yes_pressed(self, event: Button.Pressed) -> None:
        """Handle Yes button press - confirm the dangerous action."""
        self._result = True
        self._confirmed = True

        if self.on_confirm:
            await self.on_confirm()

        self.dismiss(True)

    @on(Button.Pressed, "#btn_no")
    async def on_no_pressed(self, event: Button.Pressed) -> None:
        """Handle No button press - cancel the dangerous action."""
        self._result = False
        self._confirmed = False

        if self.on_cancel:
            await self.on_cancel()

        self.dismiss(False)

    def action_yes(self) -> None:
        """Action handler for Yes (typically not bound for safety)."""
        pass

    def action_no(self) -> None:
        """Action handler for No."""
        self.action_cancel()

    def action_confirm(self) -> None:
        """Action handler for confirm (deprecated - use explicit button)."""
        pass

    def action_cancel(self) -> None:
        """Action handler for cancel - safe default."""
        self._result = False
        self._confirmed = False
        self.dismiss(False)

    def action_escape(self) -> None:
        """Handle Escape key - safe default to cancel."""
        self.action_cancel()

    def get_result(self) -> bool:
        """Get dialog result.

        Returns:
            True if user confirmed the action, False otherwise
        """
        return self._result

    def is_confirmed(self) -> bool:
        """Check if user confirmed the action.

        Returns:
            True if user clicked Yes, False otherwise
        """
        return self._confirmed
