"""Conversation History Widget for Vertical Stack TUI
Scrollable message timeline with system event blocks.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING, Union
from datetime import datetime
from textual.widget import Widget
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.app import ComposeResult
from enum import Enum
import logging

from opencode_python.tui.message_view import MessageView
from opencode_python.tui.models import (
    Message,
    MessagePart,
    MessagePartType,
    MessageData,
    SystemEvent,
    Timestamp,
    EventType as ModelEventType,
    MessageType,
    ToolState,
)

if TYPE_CHECKING:
    from textual.containers import ScrollableContainer as ScrollableContainerType


class EventType(Enum):
    """System event type enum (legacy, use ModelEventType for new code)"""
    CONTEXT_SWITCH = "context_switch"
    ERROR = "error"
    INFO = "info"


logger = logging.getLogger(__name__)


class ConversationHistory(Widget):
    """Conversation history widget with message timeline and system events"""

    CSS = """
    ConversationHistory {
        overflow-y: auto;
        color: #f5f5f5;
    }

    ConversationHistory .message-block {
        margin: 0 1;
        padding: 0 1;
        border-bottom: solid #56b6c2 20%;
        color: #f5f5f5;
    }

    ConversationHistory .message-block.user {
        border-left: thick #7fd88f 60%;
        padding-left: 1;
    }

    ConversationHistory .message-block.assistant {
        border-left: thick #56b6c2 60%;
        padding-left: 1;
    }

    ConversationHistory .message-block.system {
        border-left: thick #a0a0a0 60%;
        padding-left: 1;
        background: #141414;
        color: #a0a0a0;
    }

    ConversationHistory .event-icon {
        margin-right: 1;
    }

    ConversationHistory > ScrollableContainer {
        height: 100%;
        overflow-y: auto;
    }
    """

    # Reactive properties - using Union of Pydantic models and dict for backward compatibility
    messages: reactive[List[Union[Message, SystemEvent, Dict[str, Any]]]] = reactive([])

    def compose(self) -> ComposeResult:
        """Compose the widget with a scrollable container"""
        yield ScrollableContainer(id="messages-container")

    def on_mount(self) -> None:
        """Called when widget is mounted"""
        self._render_messages()

    def _render_messages(self) -> None:
        """Render all messages"""
        try:
            container = self.query_one("#messages-container", ScrollableContainer)
            container.remove_children()
        except Exception:
            logger.error("Failed to find messages container")
            return

        # Add messages in order
        for message in self.messages:
            self._render_single_message(message)

    def _render_single_message(self, message: Union[Message, SystemEvent, Dict[str, Any]]) -> None:
        """Render a single message or event

        Args:
            message: Message data (Pydantic model or dict for backward compatibility)
        """
        if isinstance(message, Message):
            self._add_message_block_from_model(message)
        elif isinstance(message, SystemEvent):
            self._add_system_event_from_model(message)
        elif isinstance(message, dict):
            msg_type = message.get('type')
            if msg_type == 'user':
                self._add_message_block(message, 'user')
            elif msg_type == 'assistant':
                self._add_message_block(message, 'assistant')
            elif msg_type in ('system', 'error'):
                self._add_system_event(message)
    
    def _add_message_block(self, message: Dict[str, Any], role: str) -> None:
        """Add a user or assistant message block (legacy dict-based)

        Args:
            message: Message data as dictionary
            role: Message role (user, assistant)
        """
        block = MessageView(
            message_data={
                'role': role,
                'time': message.get('time'),
                'parts': message.get('parts', []),
            }
        )
        block.add_class(role)
        container = self.query_one(ScrollableContainer)
        container.mount(block)
        container.scroll_end()

    def _add_message_block_from_model(self, message: Message) -> None:
        """Add a message block from Pydantic Message model

        Args:
            message: Message Pydantic model
        """
        message_data = MessageData(
            role=message.type,
            time=message.time,
            parts=message.parts,
            is_streaming=False
        )
        block = MessageView(message_data=message_data.model_dump())
        block.add_class(message.type)
        container = self.query_one(ScrollableContainer)
        container.mount(block)
        container.scroll_end()
    
    def _add_system_event(self, event: Dict[str, Any]) -> None:
        """Add a system event or error block (legacy dict-based)

        Args:
            event: Event data as dictionary
        """
        event_type = event.get('event_type', EventType.INFO)
        icon = "ℹ️" if event_type == EventType.INFO else "⚠️" if event_type == EventType.ERROR else "→"

        event_text = event.get('text', '')

        from textual.widgets import Static
        block = Static(f"[event-icon] {event_text}", classes="message-block system")

        try:
            container = self.query_one(ScrollableContainer)
            container.mount(block)
            container.scroll_end()
        except Exception:
            pass

    def _add_system_event_from_model(self, event: SystemEvent) -> None:
        """Add a system event from Pydantic SystemEvent model

        Args:
            event: SystemEvent Pydantic model
        """
        icon = "ℹ️" if event.event_type == ModelEventType.INFO else "⚠️" if event.event_type == ModelEventType.ERROR else "→"

        from textual.widgets import Static
        block = Static(f"[event-icon] {event.text}]", classes="message-block system")

        try:
            container = self.query_one(ScrollableContainer)
            container.mount(block)
            container.scroll_end()
        except Exception:
            pass
    
    def add_message(self, role: str, text: str, **kwargs) -> None:
        """Add a new message (legacy interface, still uses dict internally)

        Args:
            role: Message role (user, assistant, system)
            text: Message text content
            **kwargs: Additional message metadata
        """
        timestamp_data = Timestamp(created=datetime.now().isoformat())
        text_part = MessagePart(part_type=MessagePartType.TEXT, text=text)

        message = Message(
            type=MessageType(role),
            time=timestamp_data,
            parts=[text_part]
        )

        self.messages.append(message)
        self._render_messages()
        self.scroll_to_bottom()

    def add_system_event(self, event_type: EventType, text: str) -> None:
        """Add a system event (legacy interface)

        Args:
            event_type: Event type from EventType enum
            text: Event description text
        """
        timestamp_data = Timestamp(created=datetime.now().isoformat())

        event = SystemEvent(
            event_type=ModelEventType(event_type.value),
            text=text,
            time=timestamp_data
        )

        self.messages.append(event)
        try:
            self._render_messages()
            self.scroll_to_bottom()
        except Exception as e:
            logger.error(f"Failed to add system event: {e}")
    
    def scroll_to_bottom(self) -> None:
        """Scroll to newest message"""
        container = self.query_one(ScrollableContainer)
        container.scroll_end()
