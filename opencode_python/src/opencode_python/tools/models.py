"""Tool permission and execution log models"""
from __future__ import annotations
from typing import Literal, Optional, Dict, Any
from datetime import datetime
import pydantic as pd


class ToolPermission(pd.BaseModel):
    """Tool permission state for a session

    Stores whether a tool is allowed or denied, with optional reasoning.
    """
    session_id: str
    tool_id: str
    state: Literal["allowed", "denied", "pending"]
    reason: Optional[str] = None
    time_created: float = pd.Field(default_factory=lambda: datetime.now().timestamp())
    time_updated: float = pd.Field(default_factory=lambda: datetime.now().timestamp())

    model_config = pd.ConfigDict(extra="forbid")


class ToolExecutionLog(pd.BaseModel):
    """Log of tool execution with inputs, outputs, and diffs

    Stores complete execution history for audit and review.
    """
    id: str
    session_id: str
    tool_name: str
    timestamp: float = pd.Field(default_factory=lambda: datetime.now().timestamp())
    parameters: Dict[str, Any] = pd.Field(default_factory=dict)
    output: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    diff: Optional[Dict[str, Any]] = None  # File changes if applicable
    metadata: Dict[str, Any] = pd.Field(default_factory=dict)

    model_config = pd.ConfigDict(extra="forbid")


class ToolDiscovery(pd.BaseModel):
    """Tool discovery metadata

    Information about available tools for the tools panel.
    """
    tool_id: str
    name: str
    description: str
    category: Optional[str] = None
    parameters_schema: Dict[str, Any] = pd.Field(default_factory=dict)
    permission_state: Literal["allowed", "denied", "pending"] = "pending"
    permission_reason: Optional[str] = None

    model_config = pd.ConfigDict(extra="forbid")
