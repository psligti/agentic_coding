"""Top Bar Widget for Vertical Stack TUI
Displays provider/account/model/agent/session, run state, and primary action.
"""

from __future__ import annotations
from textual.widget import Widget
from textual.reactive import reactive
from textual.widgets import Static
from textual.app import ComposeResult


class TopBar(Widget):
    """Top bar widget displaying context and run state"""
    
    CSS = """
    TopBar {
        height: 1;
        padding: 0 1;
        background: #1e1e1e;
        border-bottom: solid #56b6c2 40%;
        color: #f5f5f5;
        margin: 0;
    }

    TopBar .content {
        display: inline;
    }
    """

    # Reactive properties
    provider_id: reactive[str] = reactive("")
    account_id: reactive[str] = reactive("")
    model_id: reactive[str] = reactive("")
    agent: reactive[str] = reactive("")
    session_id: reactive[str] = reactive("")
    run_state: reactive[str] = reactive("idle")

    def compose(self) -> ComposeResult:
        yield Static(id="content", classes="content")

    def __init__(self, **kwargs):
        """Initialize TopBar"""
        super().__init__(**kwargs)

    def on_mount(self) -> None:
        """Called when widget is mounted"""
        self._update_display()

    def _update_display(self) -> None:
        if not hasattr(self, 'app'):
            return

        parts = []
        if self.provider_id:
            parts.append(self.provider_id)
        else:
            parts.append("[dim]Provider[/dim]")

        parts.append(" | ")

        if self.account_id:
            parts.append(self.account_id)
        else:
            parts.append("[dim]Account[/dim]")

        parts.append(" | ")

        if self.model_id:
            parts.append(self.model_id)
        else:
            parts.append("[dim]Model[/dim]")

        parts.append(" | ")

        if self.agent:
            parts.append(self.agent)
        else:
            parts.append("[dim]Agent[/dim]")

        parts.append(" | ")

        if self.session_id:
            display_session = self.session_id[:12] + "..." if len(self.session_id) > 12 else self.session_id
            parts.append(display_session)
        else:
            parts.append("[dim]Session[/dim]")

        status_icon = "●"
        if self.run_state == "running":
            status_icon = "[#f5a742]●[/]"
        elif self.run_state == "error":
            status_icon = "[#e06c75]●[/]"
        else:
            status_icon = "[#7fd88f]●[/]"

        parts.append(f"  {status_icon} {self.run_state}")

        content = " ".join(parts)
        self.query_one("#content").update(content)
    
    # Reactive watchers
    def watch_provider_id(self, old_value: str, new_value: str) -> None:
        self.provider_id = new_value
        self._update_display()
    
    def watch_account_id(self, old_value: str, new_value: str) -> None:
        self.account_id = new_value
        self._update_display()
    
    def watch_model_id(self, old_value: str, new_value: str) -> None:
        self.model_id = new_value
        self._update_display()
    
    def watch_agent(self, old_value: str, new_value: str) -> None:
        self.agent = new_value
        self._update_display()
    
    def watch_session_id(self, old_value: str, new_value: str) -> None:
        self.session_id = new_value
        self._update_display()

    def watch_run_state(self, old_value: str, new_value: str) -> None:
        self.run_state = new_value
        self._update_display()
