"""System Event Block Widget for Vertical Stack TUI
Renders context switches and errors.
"""

from __future__ import annotations
from textual.widget import Widget
from textual.containers import Horizontal
from textual.widgets import Static
from enum import Enum


class EventType(Enum):
    """System event type enum"""
    CONTEXT_SWITCH = "context_switch"
    ERROR = "error"
    INFO = "info"


class SystemEventBlock(Widget):
    """System event block widget"""
    
    CSS = """
    SystemEventBlock {
        padding: 1;
        margin: 0 1;
        border-bottom: solid $primary 20%;
    }
    
    SystemEventBlock .event-content {
        display: flex;
        align-items: center;
    }
    
    SystemEventBlock .event-icon {
        margin-right: 1;
        color: $warning;
    }
    
    SystemEventBlock .event-text {
        color: $text-muted;
    }
    """
    
    def __init__(self, event_type: EventType, text: str, **kwargs):
        """Initialize SystemEventBlock
        
        Args:
            event_type: Type of system event
            text: Event text description
            **kwargs: Additional Widget arguments
        """
        super().__init__(**kwargs)
        self.event_type = event_type
        self.text = text
        self._update_content()
    
    def _update_content(self) -> None:
        """Update content based on event type"""
        icon = "ℹ️" if self.event_type == EventType.INFO else "⚠️" if self.event_type == EventType.ERROR else "→"
        
        from textual.widgets import Static
        self.query_one("#event-content").remove_children()
        
        # Event icon
        icon_widget = Static(icon, classes="event-icon")
        self.query_one("#event-content").mount(icon_widget)
        
        # Event text
        text_widget = Static(self.text, classes="event-text")
        self.query_one("#event-content").mount(text_widget)
