"""
Update tools registry with compaction tool.

Includes all 22 tools (5 builtin + 17 additional).
"""

import logging
from typing import Dict

from .builtin import (
    BashTool,
    ReadTool,
    WriteTool,
    GrepTool,
    GlobTool
)
from .additional import (
    EditTool,
    ListTool,
    TaskTool,
    QuestionTool,
    TodoTool,
    TodowriteTool,
    WebFetchTool,
    WebSearchTool,
    MultiEditTool,
    CodeSearchTool,
    LspTool,
    SkillTool,
    ExternalDirectoryTool,
    PlanEnterTool,
    PlanExitTool,
    BatchTool,
    CompactionTool
)
from .framework import ToolRegistry, Tool, ToolContext, ToolResult
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


class ToolRegistry(ToolRegistry):
    """Extended tool registry with all tools"""

    def __init__(self):
        self.tools: Dict[str, "Tool"] = {}
        self._init_builtin_tools()
        self._init_additional_tools()
    
    def _init_builtin_tools(self):
        self.tools["bash"] = BashTool()
        self.tools["read"] = ReadTool()
        self.tools["write"] = WriteTool()
        self.tools["grep"] = GrepTool()
        self.tools["glob"] = GlobTool()
        self.tools["edit"] = EditTool()
        self.tools["list"] = ListTool()
        self.tools["task"] = TaskTool()
        self.tools["question"] = QuestionTool()
        self.tools["todoread"] = TodoTool()
        self.tools["todowrite"] = TodowriteTool()
        self.tools["webfetch"] = WebFetchTool()
        self.tools["websearch"] = WebSearchTool()
        self.tools["multiedit"] = MultiEditTool()
        self.tools["codesearch"] = CodeSearchTool()
        self.tools["lsp"] = LspTool()
        self.tools["skill"] = SkillTool()
        self.tools["externaldirectory"] = ExternalDirectoryTool()
        self.tools["planenter"] = PlanEnterTool()
        self.tools["planexit"] = PlanExitTool()
        self.tools["batch"] = BatchTool()
        self.tools["compact"] = CompactionTool()

        logger.info(f"Registered {len(self.tools) - 17} additional tools")

    def _init_additional_tools(self):
        pass
    async def get_all(self) -> Dict[str, "Tool"]:
        """Get all available tools"""
        return self.tools
    
    async def execute(self, tool_name: str, args: Dict, ctx: ToolContext) -> ToolResult:
        """Execute tool by name"""
        import time
        import uuid

        from opencode_python.core.event_bus import Events, bus

        tool = self.tools.get(tool_name.lower())
        if not tool:
            logger.error(f"Tool {tool_name} not found")
            await ctx.log_tool_execution(
                tool_name=tool_name,
                parameters=args,
                output=None,
                success=False,
                error=f"Tool {tool_name} is not available",
            )
            return ToolResult(
                title=f"Unknown tool: {tool_name}",
                output=f"Tool {tool_name} is not available",
                metadata={"error": f"unknown_tool: {tool_name}"}
            )

        ctx.tool_name = tool_name
        ctx.call_id = str(uuid.uuid4())
        ctx.time_created = time.time()

        await bus.publish(Events.TOOL_EXECUTE, {
            "session_id": ctx.session_id,
            "message_id": ctx.message_id,
            "tool_name": tool_name,
            "call_id": ctx.call_id,
            "parameters": args,
        })

        try:
            result = await tool.execute(args, ctx)
            ctx.time_finished = time.time()

            await ctx.log_tool_execution(
                tool_name=tool_name,
                parameters=args,
                output=result.output,
                success=True,
                diff=result.metadata.get("diff") if result.metadata else None,
            )

            await bus.publish(Events.TOOL_COMPLETED, {
                "session_id": ctx.session_id,
                "message_id": ctx.message_id,
                "tool_name": tool_name,
                "call_id": ctx.call_id,
                "title": result.title,
            })

            return result
        except Exception as e:
            ctx.time_finished = time.time()
            logger.error(f"Tool {tool_name} execution error: {e}")

            await ctx.log_tool_execution(
                tool_name=tool_name,
                parameters=args,
                output=None,
                success=False,
                error=str(e),
            )

            await bus.publish(Events.TOOL_ERROR, {
                "session_id": ctx.session_id,
                "message_id": ctx.message_id,
                "tool_name": tool_name,
                "call_id": ctx.call_id,
                "error": str(e),
            })

            return ToolResult(
                title=f"Tool error: {tool_name}",
                output=f"Error executing {tool_name}: {str(e)}",
                metadata={"error": str(e)},
            )
