"""Status Bar Widget for Vertical Stack TUI
Displays keyboard hints and session metrics.
"""

from __future__ import annotations
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Horizontal
from textual.widgets import Static
from textual.app import ComposeResult


class StatusBar(Widget):
    """Status bar widget displaying keyboard hints and session metrics"""

    CSS = """
    StatusBar {
        height: 1;
        padding: 0 1;
        background: #141414;
        border-top: solid #56b6c2 40%;
        color: #f5f5f5;
        text-style: none;
        margin: 0;
    }
    """

    # Reactive properties
    message_count: reactive[int] = reactive(0)
    cost: reactive[float] = reactive(0.0)
    tokens: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose status bar with single line of content"""
        yield Static(id="status-content", classes="status-content")

    def on_mount(self) -> None:
        """Called when widget is mounted"""
        self._update_display()

    def _update_display(self) -> None:
        """Update widget content based on reactive properties"""
        hints = "Ctrl+P | Ctrl+Q | Ctrl+Z | Enter | Esc"
        metrics = f"Messages: {self.message_count} | Cost: ${self.cost:.4f} | Tokens: {self.tokens}"
        content = f"{hints}    {metrics}"

        self.query_one("#status-content").update(content)
    
    # Reactive watchers
    def watch_message_count(self, old_value: int, new_value: int) -> None:
        self.message_count = new_value
        self._update_display()
    
    def watch_cost(self, old_value: float, new_value: float) -> None:
        self.cost = new_value
        self._update_display()
    
    def watch_tokens(self, old_value: int, new_value: int) -> None:
        self.tokens = new_value
        self._update_display()
