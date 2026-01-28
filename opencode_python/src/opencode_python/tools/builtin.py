"""OpenCode Python - Built-in tools (bash, read, write, grep, glob)"""
from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
import subprocess
import logging

from opencode_python.tools.framework import Tool, ToolContext, ToolResult
from opencode_python.core.models import FilePart
from opencode_python.context.pipeline import GitManager


logger = logging.getLogger(__name__)


class BashTool(Tool):
    """Execute shell commands"""

    id = "bash"
    description = "Execute shell commands in the project directory"

    async def execute(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
        """Execute a bash command

        Args:
            args: {
                "command": str,  # Command to execute
                "description": Optional[str],  # Description for UI
                "cwd": Optional[str],  # Working directory
            }
            ctx: Tool execution context

        Returns:
            ToolResult with output, title, and metadata
        """
        command = args.get("command", "")
        description = args.get("description", command)
        cwd = args.get("cwd", ".")

        if not command:
            return ToolResult(
                title="No command",
                output="",
                metadata={"error": "Command is required"},
            )

        logger.info(f"Executing: {command}")

        try:
            result = subprocess.run(
                [command],
                shell=True,
                cwd=ctx.session_id if cwd == "." else cwd,
                capture_output=True,
                text=True,
                check=True,
            )

            output = result.stdout
            stderr = result.stderr

            # Combine stdout and stderr
            if stderr:
                full_output = f"{output}\n[Stderr]\n{stderr}"
            else:
                full_output = output

            return ToolResult(
                title=description or command,
                output=full_output,
                metadata={
                    "exit_code": result.returncode,
                    "description": description,
                },
            )

        except Exception as e:
            logger.error(f"Bash tool failed: {e}")
            return ToolResult(
                title=f"Error: {command}",
                output=str(e),
                metadata={"error": str(e)},
            )


class ReadTool(Tool):
    """Read file contents"""

    id = "read"
    description = "Read file contents with optional line numbering and diff support"

    async def execute(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
        """Read a file

        Args:
            args: {
                "file": str,  # Path to file (relative to project)
                "limit": Optional[int],  # Max lines to read
                "offset": Optional[int],  # Line number to start from
            }
            ctx: Tool execution context

        Returns:
            ToolResult with file content
        """
        file_path = args.get("file", "")

        if not file_path:
            return ToolResult(
                title="No file specified",
                output="",
                metadata={"error": "File path is required"},
            )

        limit = args.get("limit", 2000)
        offset = args.get("offset", 0)

        try:
            full_path = Path(ctx.session_id if ctx.session_id.startswith("/") else "") / file_path
            if not full_path.exists():
                return ToolResult(
                    title="File not found",
                    output="",
                    metadata={"path": str(file_path), "error": "File not found"},
                )

            # Read file content
            with open(full_path, "r") as f:
                all_lines = f.readlines()

            # Apply offset/limit
            start_line = max(0, offset - 1)
            end_line = min(start_line + limit, len(all_lines))
            lines = all_lines[start_line:end_line]

            content = "".join(lines)

            metadata = {
                "path": str(file_path),
                "lines_read": len(lines),
                "start_line": start_line + 1,
                "end_line": end_line,
            }

            return ToolResult(
                title=f"Read: {file_path}",
                output=content,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Read tool failed: {e}")
            return ToolResult(
                title=f"Error reading: {file_path}",
                output=str(e),
                metadata={"error": str(e)},
            )


class WriteTool(Tool):
    """Write content to files"""

    id = "write"
    description = "Write content to files"

    async def execute(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
        """Write content to a file

        Args:
            args: {
                "file": str,  # Path to file (relative to project)
                "content": str,  # Content to write
                "create": bool,  # Create directories if needed
            }
            ctx: Tool execution context

        Returns:
            ToolResult with operation result
        """
        file_path = args.get("file", "")
        content = args.get("content", "")
        create_dirs = args.get("create", False)

        if not file_path:
            return ToolResult(
                title="No file specified",
                output="",
                metadata={"error": "File path is required"},
            )

        try:
            full_path = Path(ctx.session_id if ctx.session_id.startswith("/") else "") / file_path

            # Create directories if needed
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w") as f:
                f.write(content)

            return ToolResult(
                title=f"Write: {file_path}",
                output=f"Wrote {len(content)} bytes",
                metadata={"path": str(file_path), "bytes": len(content)},
            )

        except Exception as e:
            logger.error(f"Write tool failed: {e}")
            return ToolResult(
                title=f"Error writing: {file_path}",
                output=str(e),
                metadata={"error": str(e)},
            )


class GrepTool(Tool):
    """Search file contents using ripgrep"""

    id = "grep"
    description = "Search file contents using regex patterns"

    async def execute(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
        """Search for patterns in files

        Args:
            args: {
                "query": str,  # Regex pattern to search
                "file_pattern": Optional[str],  # Glob pattern for files
                "max_results": int = 100,  # Max results
            }
            ctx: Tool execution context

        Returns:
            ToolResult with search results
        """
        query = args.get("query", "")
        file_pattern = args.get("file_pattern", "*")
        max_results = args.get("max_results", 100)

        if not query:
            return ToolResult(
                title="No query",
                output="",
                metadata={"error": "Query is required"},
            )

        logger.info(f"Searching: {query}")

        try:
            # Build ripgrep command
            cmd = ["ripgrep", "-e", query, file_pattern]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.returncode != 0:
                return ToolResult(
                    title="Search failed",
                    output=result.stderr,
                    metadata={"error": result.stderr},
                )

            output = result.stdout.strip()
            lines = output.split("\n")[:max_results]

            return ToolResult(
                title=f"Grep: {query}",
                output="\n".join(lines),
                metadata={"matches": len(lines)},
            )

        except Exception as e:
            logger.error(f"Grep tool failed: {e}")
            return ToolResult(
                title=f"Error searching: {query}",
                output=str(e),
                metadata={"error": str(e)},
            )


class GlobTool(Tool):
    """Find files using glob patterns"""

    id = "glob"
    description = "Find files matching glob patterns"

    async def execute(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
        """Find files using glob patterns

        Args:
            args: {
                "pattern": str,  # Glob pattern
                "max_results": int = 100,  # Max results
            }
            ctx: Tool execution context

        Returns:
            ToolResult with matching files
        """
        pattern = args.get("pattern", "*")
        max_results = args.get("max_results", 100)

        if not pattern:
            return ToolResult(
                title="No pattern",
                output="",
                metadata={"error": "Pattern is required"},
            )

        logger.info(f"Finding: {pattern}")

        try:
            # Use ripgrep --files with glob
            cmd = ["ripgrep", "--glob", pattern]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.returncode != 0:
                return ToolResult(
                    title="Glob failed",
                    output=result.stderr,
                    metadata={"error": result.stderr},
                )

            output = result.stdout.strip()
            lines = output.split("\n")[:max_results]

            return ToolResult(
                title=f"Glob: {pattern}",
                output="\n".join(lines),
                metadata={"matches": len(lines)},
            )

        except Exception as e:
            logger.error(f"Glob tool failed: {e}")
            return ToolResult(
                title=f"Error finding: {pattern}",
                output=str(e),
                metadata={"error": str(e)},
            )
