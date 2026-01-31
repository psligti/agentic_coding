"""Conversation History Widget for Vertical Stack TUI
Scrollable message timeline with system event blocks.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from textual.widget import Widget
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.app import ComposeResult
from enum import Enum


from opencode_python.tui.message_view import MessageView

if TYPE_CHECKING:
    from textual.containers import ScrollableContainer as ScrollableContainerType


class EventType(Enum):
    """System event type enum"""
    CONTEXT_SWITCH = "context_switch"
    ERROR = "error"
    INFO = "info"


class ConversationHistory(Widget):
    """Conversation history widget with message timeline and system events"""

    CSS = """
    ConversationHistory {
        height: 1fr;
        overflow-y: auto;
    }

    ConversationHistory .message-block {
        margin: 0 1;
        padding: 0 1;
        border-bottom: solid $primary 20%;
    }

    ConversationHistory .message-block.user {
        border-left: thick $success 60%;
        padding-left: 1;
    }

    ConversationHistory .message-block.assistant {
        border-left: thick $accent 60%;
        padding-left: 1;
    }

    ConversationHistory .message-block.system {
        border-left: thick $text-muted 60%;
        padding-left: 1;
        background: $panel;
    }

    ConversationHistory .event-icon {
        margin-right: 1;
    }
    """

    # Reactive properties
    messages: reactive[List[Dict[str, Any]]] = reactive([])

    def compose(self) -> ComposeResult:
        """Compose the widget with a scrollable container"""
        yield ScrollableContainer(id="messages-container")

    def on_mount(self) -> None:
        """Called when widget is mounted"""
        self._render_messages()
    
    def _render_messages(self) -> None:
        """Render all messages"""
        container = self.query_one("#messages-container", ScrollableContainer)
        container.remove_children()
        
        # Add messages in order
        for message in self.messages:
            if message.get('type') == 'user':
                self._add_message_block(message, 'user')
            elif message.get('type') == 'assistant':
                self._add_message_block(message, 'assistant')
            elif message.get('type') == 'system':
                self._add_system_event(message)
            elif message.get('type') == 'error':
                self._add_system_event(message)
    
    def _add_message_block(self, message: Dict[str, Any], role: str) -> None:
        """Add a user or assistant message block"""
        block = MessageView(
            message_data={
                'role': role,
                'time': message.get('time'),
                'parts': message.get('parts', []),
            }
        )
        block.set_class(role, True)
        container = self.query_one(ScrollableContainer)
        container.mount(block)
        container.scroll_end()
    
    def _add_system_event(self, event: Dict[str, Any]) -> None:
        """Add a system event or error block"""
        event_type = event.get('event_type', EventType.INFO)
        icon = "ℹ️" if event_type == EventType.INFO else "⚠️" if event_type == EventType.ERROR else "→"
        
        event_text = event.get('text', '')
        
        from textual.widgets import Static
        block = Static(f"[event-icon] {event_text}", classes="message-block system")
        
        container = self.query_one(ScrollableContainer)
        container.mount(block)
        container.scroll_end()
    
    def watch_messages(self, old_value: List[Dict[str, Any]], new_value: List[Dict[str, Any]]) -> None:
        """Watch messages reactive property"""
        self.messages = new_value
        self._render_messages()
    
    def add_message(self, role: str, text: str, **kwargs) -> None:
        """Add a new message"""
        from datetime import datetime
        message = {
            'type': role,
            'time': {'created': datetime.now().isoformat()},
            'parts': [{'part_type': 'text', 'text': text}],
            **kwargs
        }
        self.messages.append(message)
        self._render_messages()
        self.scroll_to_bottom()
    
    def add_system_event(self, event_type: EventType, text: str) -> None:
        """Add a system event"""
        event = {
            'event_type': event_type.value,
            'text': text,
            'time': {'created': datetime.now().isoformat()},
        }
        self.messages.append(event)
        self._render_messages()
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self) -> None:
        """Scroll to newest message"""
        container = self.query_one(ScrollableContainer)
        container.scroll_end()
