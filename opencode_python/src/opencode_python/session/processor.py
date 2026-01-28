"""OpenCode Python - Session Message Processor"""
from __future__ import annotations
from typing import Optional, Dict, Any
import asyncio
import logging

from opencode_python.provider.stream_types import (
    StreamEvent,
    TextStartEvent,
    TextDeltaEvent,
    TextEndEvent,
    ReasoningStartEvent,
    ReasoningDeltaEvent,
    ReasoningEndEvent,
    ToolInputStartEvent,
    ToolInputDeltaEvent,
    ToolInputEndEvent,
    ToolCallEvent,
    ToolResultEvent,
    ToolErrorEvent,
    FinishStepEvent,
    FinishEvent,
    generate_id,
)
from opencode_python.core.models import (
    Message,
    AssistantMessage,
    TextPart,
    ToolPart,
    ReasoningPart,
)


logger = logging.getLogger(__name__)


class SessionProcessor:
    """Processes streaming LLM responses and updates message parts incrementally"""

    def __init__(
        self,
        assistant_message: AssistantMessage,
        session_id: str,
        model: Dict[str, str],
        abort: Optional[asyncio.Event] = None
    ):
        self.assistant_message = assistant_message
        self.session_id = session_id
        self.model = model
        self.abort = abort
        self.toolcalls: Dict[str, ToolPart] = {}
        self.current_text: Optional[TextPart] = None
        self.reasoning_map: Dict[str, ReasoningPart] = {}

    async def process(self, stream: asyncio.Queue) -> str:
        """
        Process streaming events and update message parts
        
        Returns:
            "continue" if should continue conversation
        """
        logger.info(f"Processing stream for session {self.session_id}")
        
        try:
            while True:
                event = stream.get()
                
                if event is None:
                    break
                
                if self.abort and self.abort.is_set():
                    logger.info("Processing aborted")
                    break
                
                await self._handle_event(event)
        
        except asyncio.CancelledError:
            logger.info("Processing cancelled")
            return "cancelled"

        return "continue"

    async def _handle_event(self, event: StreamEvent) -> None:
        """Handle individual stream events"""
        
        if isinstance(event, TextStartEvent):
            self.reasoning_map[event.id] = ReasoningPart(
                id=generate_id(),
                message_id=self.assistant_message.id,
                session_id=self.session_id,
                text="",
                time={"start": self._now()},
                metadata=event.provider_metadata,
            )
        
        elif isinstance(event, ReasoningDeltaEvent):
            if event.id in self.reasoning_map:
                part = self.reasoning_map[event.id]
                part.text += event.text
                if part.text:
                    await self._update_part(part, delta=event.text)
        
        elif isinstance(event, ReasoningEndEvent):
            if event.id in self.reasoning_map:
                part = self.reasoning_map[event.id]
                await self._update_part(part)
        
        elif isinstance(event, ToolInputStartEvent):
            self.toolcalls[event.tool_call_id] = ToolPart(
                id=generate_id(),
                message_id=self.assistant_message.id,
                session_id=self.session_id,
                tool=event.tool,
                call_id=event.tool_call_id,
                state={
                    "status": "running",
                    "input": event.input,
                    "time": {"start": self._now()},
                },
            )
        
        elif isinstance(event, ToolInputDeltaEvent):
            if event.tool_call_id in self.toolcalls:
                part = self.toolcalls[event.tool_call_id]
                if "input" in part.state:
                    part.state["input"].update(event.input_delta)
        
        elif isinstance(event, ToolInputEndEvent):
            if event.tool_call_id in self.toolcalls:
                part = self.toolcalls[event.tool_call_id]
                await self._update_part(part, state={"status": "completed"})
        
        elif isinstance(event, ToolCallEvent):
            self.toolcalls[event.tool_call_id] = ToolPart(
                id=generate_id(),
                message_id=self.assistant_message.id,
                session_id=self.session_id,
                tool=event.tool,
                call_id=event.tool_call_id,
                input=event.input,
                state={"status": "pending"},
            )
        
        elif isinstance(event, ToolResultEvent):
            if event.tool_call_id in self.toolcalls:
                part = self.toolcalls[event.tool_call_id]
                part.state = {
                    "status": "completed",
                    "output": event.output,
                }
                if event.error:
                    part.state["error"] = event.error
                await self._update_part(part)
        
        elif isinstance(event, ToolErrorEvent):
            if event.tool_call_id in self.toolcalls:
                part = self.toolcalls[event.tool_call_id]
                part.state = {
                    "status": "error",
                    "error": event.error,
                }
                await self._update_part(part)
        
        elif isinstance(event, TextStartEvent):
            self.current_text = TextPart(
                id=generate_id(),
                message_id=self.assistant_message.id,
                session_id=self.session_id,
                text="",
                time={"start": self._now()},
            )
        
        elif isinstance(event, TextDeltaEvent):
            if self.current_text:
                self.current_text.text += event.text
                if self.current_text.text:
                    await self._update_part(self.current_text, delta=event.text)
        
        elif isinstance(event, TextEndEvent):
            if self.current_text:
                await self._update_part(self.current_text)
                self.current_text = None
        
        elif isinstance(event, FinishStepEvent):
            usage = self._calculate_usage(event.usage, event.provider_metadata)
            self.assistant_message.finish = event.finish_reason
            await self._update_message(self.assistant_message, usage=usage)
        
        elif isinstance(event, FinishEvent):
            usage = event.usage
            self.assistant_message.finish = event.finish_reason
            await self._update_message(self.assistant_message, usage=usage)
        
        else:
            logger.warning(f"Unknown event type: {type(event)}")

    async def _update_part(
        self,
        part: Any,
        delta: Optional[str] = None,
    ) -> None:
        """Update a part (either new or with delta)"""
        part_id = part.id
        part_data = self._part_to_dict(part)
        
        if delta:
            part_data["text"] += delta
        
        await self._save_part(part_id, part_data)

    async def _update_message(
        self,
        message: AssistantMessage,
        usage: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update message in storage"""
        message_data = self._message_to_dict(message)
        
        if usage:
            if "tokens" not in message_data:
                message_data["tokens"] = {}
            message_data["tokens"]["input"] = usage.get("input", 0)
            message_data["tokens"]["output"] = usage.get("output", 0)
            message_data["tokens"]["reasoning"] = usage.get("reasoning", 0)
            message_data["tokens"]["cache"] = {
                "read": usage.get("cache_read", 0),
                "write": usage.get("cache_write", 0),
            }
        
        await self._save_message(message.id, message_data)

    async def _save_part(self, part_id: str, part_data: Dict[str, Any]) -> None:
        """Save part to storage (placeholder - will integrate with actual storage)"""
        logger.debug(f"Saving part {part_id}")
        # TODO: Integrate with SessionStorage.update_part()

    async def _save_message(self, message_id: str, message_data: Dict[str, Any]) -> None:
        """Save message to storage (placeholder - will integrate with actual storage)"""
        logger.debug(f"Saving message {message_id}")
        # TODO: Integrate with SessionStorage.update_message()

    def _calculate_usage(
        self,
        usage: Optional[Dict[str, Any]],
        provider_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate usage from response"""
        if not usage:
            return {"input": 0, "output": 0}
        
        return {
            "input": usage.get("input", 0),
            "output": usage.get("output", 0),
            "reasoning": usage.get("reasoning", 0),
            "cache": {
                "read": usage.get("cache_read", 0),
                "write": usage.get("cache_write", 0),
            },
        }

    def _now(self) -> int:
        """Get current timestamp in milliseconds"""
        import time
        return int(time.time() * 1000)

    def _part_to_dict(self, part: Any) -> Dict[str, Any]:
        """Convert part to dictionary format"""
        from dataclasses import asdict
        return asdict(part)

    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        from dataclasses import asdict
        return asdict(message)
