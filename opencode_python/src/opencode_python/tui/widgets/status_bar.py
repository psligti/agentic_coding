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
        dock: bottom;
        height: auto;
        padding: 1 2;
        background: $secondary;
        border-top: solid $primary 40%;
    }

    StatusBar .hints {
        height: auto;
        text-align: left;
        color: $text-muted;
    }

    StatusBar .metrics {
        height: auto;
        text-align: right;
        color: $text-muted;
    }

    StatusBar .metric-value {
        color: $accent;
    }
    """

    # Reactive properties
    message_count: reactive[int] = reactive(0)
    cost: reactive[float] = reactive(0.0)
    tokens: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        """Compose the status bar with hints and metrics containers"""
        yield Horizontal(id="hints")
        yield Horizontal(id="metrics")

    def on_mount(self) -> None:
        """Called when widget is mounted"""
        self._update_display()
    
    def _update_display(self) -> None:
        """Update widget content based on reactive properties"""
        # Left side: keyboard hints
        hints = [
            Static("Ctrl+P", classes="hint"),
            Static(" Ctrl+Q", classes="hint"),
            Static(" Ctrl+Z", classes="hint"),
            Static(" | ", classes="separator"),
            Static("Enter", classes="hint"),
            Static(" Esc", classes="hint"),
        ]
        
        # Right side: metrics
        metrics = []
        metrics.append(Static(f"Messages: ", classes="metric-label"))
        metrics.append(Static(f"[bold]{self.message_count}[/bold]", classes="metric-value"))
        metrics.append(Static(" | ", classes="separator"))
        metrics.append(Static(f"Cost: $", classes="metric-label"))
        metrics.append(Static(f"[bold]{self.cost:.4f}[/bold]", classes="metric-value"))
        metrics.append(Static(" | ", classes="separator"))
        metrics.append(Static(f"Tokens: ", classes="metric-label"))
        metrics.append(Static(f"[bold]{self.tokens}[/bold]", classes="metric-value"))
        
        with self.query_one("#hints", Horizontal):
            self.query_one("#hints").remove_children()
            for hint in hints:
                self.query_one("#hints").mount(hint)
        
        with self.query_one("#metrics", Horizontal):
            self.query_one("#metrics").remove_children()
            for metric in metrics:
                self.query_one("#metrics").mount(metric)
    
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
