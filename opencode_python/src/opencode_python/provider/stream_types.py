"""OpenCode Python - Stream Types and Events"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Dict, Any, Optional
import uuid
import logging


logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    """Base class for all stream events"""
    type: str
    id: Optional[str] = None


@dataclass
class TextStartEvent(StreamEvent):
    """Text content starts"""
    type: Literal["text-start"] = "text-start"
    id: str
    parent_id: Optional[str] = None


@dataclass
class TextDeltaEvent(StreamEvent):
    """Text content delta (incremental)"""
    type: Literal["text-delta"] = "text-delta"
    id: str
    text: str


@dataclass
class TextEndEvent(StreamEvent):
    """Text content ends"""
    type: Literal["text-end"] = "text-end"
    id: str


@dataclass
class ReasoningStartEvent(StreamEvent):
    """Reasoning/thinking starts"""
    type: Literal["reasoning-start"] = "reasoning-start"
    id: str
    parent_id: Optional[str] = None
    provider_metadata: Optional[Dict[str, Any]] = None


@dataclass
class ReasoningDeltaEvent(StreamEvent):
    """Reasoning/thinking delta"""
    type: Literal["reasoning-delta"] = "reasoning-delta"
    id: str
    text: str


@dataclass
class ReasoningEndEvent(StreamEvent):
    """Reasoning/thinking ends"""
    type: Literal["reasoning-end"] = "reasoning-end"
    id: str


@dataclass
class ToolInputStartEvent(StreamEvent):
    """Tool input starts"""
    type: Literal["tool-input-start"] = "tool-input-start"
    id: str
    tool_call_id: str
    tool: str
    input: Dict[str, Any]
    provider_metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolInputDeltaEvent(StreamEvent):
    """Tool input delta"""
    type: Literal["tool-input-delta"] = "tool-input-delta"
    id: str
    input_delta: Dict[str, Any]


@dataclass
class ToolInputEndEvent(StreamEvent):
    """Tool input ends"""
    type: Literal["tool-input-end"] = "tool-input-end"
    id: str


@dataclass
class ToolCallEvent(StreamEvent):
    """Tool is called"""
    type: Literal["tool-call"] = "tool-call"
    id: str
    tool_call_id: str
    tool_name: str
    input: Dict[str, Any]
    provider_metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolResultEvent(StreamEvent):
    """Tool execution result"""
    type: Literal["tool-result"] = "tool-result"
    id: str
    tool_call_id: str
    tool_name: str
    output: str
    error: Optional[str] = None
    provider_metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolErrorEvent(StreamEvent):
    """Tool execution error"""
    type: Literal["tool-error"] = "tool-error"
    id: str
    tool_call_id: str
    tool_name: str
    error: str
    provider_metadata: Optional[Dict[str, Any]] = None


@dataclass
class FinishStepEvent(StreamEvent):
    """LLM turn completes"""
    type: Literal["finish-step"] = "finish-step"
    id: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    provider_metadata: Optional[Dict[str, Any]] = None


@dataclass
class FinishEvent(StreamEvent):
    """Full response completes"""
    type: Literal["finish"] = "finish"
    id: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    provider_metadata: Optional[Dict[str, Any]] = None


StreamEvent = (
    TextStartEvent
    | TextDeltaEvent
    | TextEndEvent
    | ReasoningStartEvent
    | ReasoningDeltaEvent
    | ReasoningEndEvent
    | ToolInputStartEvent
    | ToolInputDeltaEvent
    | ToolInputEndEvent
    | ToolCallEvent
    | ToolResultEvent
    | ToolErrorEvent
    | FinishStepEvent
    | FinishEvent
)


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())
