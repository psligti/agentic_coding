"""OpenCode Python - Event bus for async communication"""
from __future__ import annotations
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
import asyncio
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class Events:
    """Event name constants for agent lifecycle and operations"""

    # Agent lifecycle events
    AGENT_INITIALIZED = "agent.initialized"
    AGENT_READY = "agent.ready"
    AGENT_EXECUTING = "agent.executing"
    AGENT_ERROR = "agent.error"
    AGENT_CLEANUP = "agent.cleanup"

    # Session events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    SESSION_DELETED = "session.deleted"
    SESSION_MESSAGE_CREATED = "session.message_created"

    # Tool events
    TOOL_EXECUTED = "tool.executed"
    TOOL_ERROR = "tool.error"

    # Task events
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


@dataclass
class Event:
    """Event data container"""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventSubscription:
    """Event subscription with callback"""
    event_name: str
    callback: Callable[[Event], Any]
    once: bool = False


class EventBus:
    """Async event bus for decoupled communication"""

    def __init__(self) -> None:
        """Initialize event bus"""
        self._subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(
        self,
        event_name: str,
        callback: Callable[[Event], Any],
        once: bool = False,
    ) -> Callable[[], Any]:
        """Subscribe to an event

        Args:
            event_name: Name of the event to subscribe to
            callback: Async function to call when event is published
            once: If True, unsubscribe after first call

        Returns:
            Unsubscribe function
        """
        subscription = EventSubscription(
            event_name=event_name,
            callback=callback,
            once=once,
        )
        self._subscriptions[event_name].append(subscription)

        def unsubscribe():
            self._subscriptions[event_name].remove(subscription)

        return unsubscribe

    async def publish(self, event_name: str, data: Dict[str, Any]) -> None:
        """Publish an event to all subscribers

        Args:
            event_name: Name of the event
            data: Event data (key-value pairs)
        """
        event = Event(name=event_name, data=data)

        subscriptions = list(self._subscriptions.get(event_name, []))

        for subscription in subscriptions:
            try:
                await subscription.callback(event)
                if subscription.once:
                    self._subscriptions[event_name].remove(subscription)
            except Exception as e:
                logger.error(f"Error in event handler for {event_name}: {e}")

    async def publish_sync(self, event_name: str, data: Dict[str, Any]) -> None:
        """Synchronous publish helper"""
        async with self._lock:
            await self.publish(event_name, data)


# Global event bus instance
bus = EventBus()
