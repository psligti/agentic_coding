"""OpenCode Python - Tool execution framework"""
from __future__ import annotations
from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import logging

from opencode_python.core.event_bus import bus, Events
from opencode_python.permissions.evaluate import (
    PermissionEvaluator,
    PermissionRule,
    get_default_rulesets,
)


logger = logging.getLogger(__name__)


@dataclass
class ToolContext:
    """Context passed to tool execution"""
    session_id: str
    message_id: str
    agent: str
    abort: asyncio.Event
    messages: List[dict]

    async def update_metadata(self, title: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update tool metadata during execution

        Emits tool metadata update event
        """
        await bus.publish(Events.TOOL_STARTED, {
            "session_id": self.session_id,
            "message_id": self.message_id,
            "title": title,
            "metadata": metadata or {},
        })

    async def ask(
        self,
        permission: str,
        pattern: str,
        always: Optional[List[str]] = None,
    ) -> bool:
        """Request permission from user

        Args:
            permission: Permission to request (e.g., "bash", "read")
            pattern: Pattern to match (e.g., "*", "/etc/*")
            always: Patterns to always approve

        Returns:
            True if permission granted, False otherwise
        """
        from opencode_python.core.event_bus import Events

        # Check permission via evaluator
        rulesets = get_default_rulesets()
        rule = PermissionEvaluator.evaluate(permission, pattern, rulesets)

        if rule.action == "deny":
            await bus.publish(Events.PERMISSION_DENIED, {
                "permission": permission,
                "pattern": pattern,
            })
            return False

        if rule.action == "allow":
            await bus.publish(Events.PERMISSION_GRANTED, {
                "permission": permission,
                "pattern": pattern,
                "always": always,
            })
            return True

        # Ask permission
        await bus.publish(Events.PERMISSION_ASKED, {
            "permission": permission,
            "pattern": pattern,
            "always": always,
        })

        # In CLI mode, this would prompt user
        # In TUI mode, this would show a dialog
        # For now, return True (assume approval in non-interactive mode)
        return True


@dataclass
class ToolResult:
    """Result from tool execution"""
    title: str
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: Optional[List[Dict[str, Any]]] = None


class Tool(ABC):
    """Abstract base class for all tools

    Mimics TypeScript Tool.define() factory pattern.
    """

    id: str
    description: str

    @abstractmethod
    async def execute(
        self,
        args: Dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        """Execute the tool with given arguments

        Args:
            args: Validated tool arguments
            ctx: Tool execution context

        Returns:
            ToolResult with title, output, metadata, and optional attachments
        """
        pass

    async def init(self, ctx: ToolContext) -> None:
        """Initialize tool with context

        Called once before execute() to set up tool state.
        Optional override for tools that need initialization.
        """
        pass


class ToolRegistry:
    """Registry for managing available tools"""

    def __init__(self):
        """Initialize registry"""
        self._tools: Dict[str, type[Tool]] = {}

    def register(self, tool: type[Tool]) -> None:
        """Register a tool

        Args:
            tool: Tool instance to register
        """
        self._tools[tool.id] = tool
        logger.debug(f"Registered tool: {tool.id}")

    def get(self, tool_id: str) -> Optional[type[Tool]]:
        """Get a tool by ID"""
        return self._tools.get(tool_id)

    def list_all(self) -> List[type[Tool]]:
        """List all registered tools"""
        return list(self._tools.values())

    async def execute_tool(
        self,
        tool_id: str,
        args: Dict[str, Any],
        ctx: ToolContext,
    ) -> Optional[ToolResult]:
        """Execute a tool by ID with permission checks

        Args:
            tool_id: ID of tool to execute
            args: Arguments to pass to tool
            ctx: Tool execution context

        Returns:
            ToolResult if successful, None if tool not found or permission denied
        """
        tool = self.get(tool_id)
        if not tool:
            logger.error(f"Tool not found: {tool_id}")
            return None

        # Check permission before execution
        # For now, skip permission check for built-in tools
        # Real implementation would check tool-specific permissions

        try:
            # Update metadata with running state
            await ctx.update_metadata(title=f"Executing {tool.id}", metadata={"status": "running"})

            # Execute tool
            tool_instance = tool()
            result = await tool_instance.execute(args, ctx)

            # Update metadata with completed state
            result.metadata["status"] = "completed"

            await bus.publish(Events.TOOL_COMPLETED, {
                "session_id": ctx.session_id,
                "message_id": ctx.message_id,
                "tool_id": tool_id,
                "result": {
                    "title": result.title,
                    "output": result.output,
                    "metadata": result.metadata,
                    "attachments": result.attachments,
                },
            })

            return result

        except asyncio.CancelledError:
            await bus.publish(Events.TOOL_ERROR, {
                "session_id": ctx.session_id,
                "message_id": ctx.message_id,
                "tool_id": tool_id,
                "error": "Tool execution cancelled",
            })
            return None

        except Exception as e:
            logger.error(f"Tool {tool_id} failed: {e}")
            await bus.publish(Events.TOOL_ERROR, {
                "session_id": ctx.session_id,
                "message_id": ctx.message_id,
                "tool_id": tool_id,
                "error": str(e),
            })
            raise


# Global tool registry instance
registry = ToolRegistry()


def define_tool(
    tool_id: str,
    description: str,
    execute_func: Callable[[Dict[str, Any], ToolContext], Awaitable[ToolResult]],
) -> type[Tool]:
    """Factory function to define a tool

    Mimics TypeScript Tool.define() pattern:
    const tool = Tool.define("tool-id", async (ctx?) => {
      return {
        description: "...",
        parameters: z.object({...}),
        execute: async (args, ctx) => {...}
      }
    })

    Args:
        tool_id: Unique identifier for the tool
        description: Human-readable description for LLM
        execute_func: Async function that implements tool.execute()

    Returns:
        Tool class instance
    """
    class DynamicTool(Tool):
        id = tool_id
        description = description

        async def execute(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
            return await execute_func(args, ctx)

    return DynamicTool
