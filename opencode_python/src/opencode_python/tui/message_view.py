"""OpenCode Python - Message and Part rendering for TUI"""
from __future__ import annotations

from typing import Any, Optional

from textual.containers import Container, Horizontal
from textual.widgets import Static
from textual.app import ComposeResult
import logging

from opencode_python.tui.models import (
    MessageData,
    MessagePart as MessagePartModel,
    MessagePartType,
    ToolState,
    Timestamp,
)

logger = logging.getLogger(__name__)


class MessagePartView(Container):
    """Display a message part (text, tool, file, etc.)"""

    CSS = """
    MessagePartView {
        margin: 0 1;
    }

    .part-header {
        text-style: bold;
        margin-bottom: 0;
    }

    .part-content {
        padding: 0 1;
        margin-bottom: 1;
    }

    .tool-status-pending {
        color: yellow;
    }

    .tool-status-running {
        color: cyan;
    }

    .tool-status-completed {
        color: green;
    }

    .tool-status-error {
        color: red;
    }
    """

    part_data: MessagePartModel

    def __init__(self, part_data: MessagePartModel):
        super().__init__()
        self.part_data = part_data

    def compose(self) -> ComposeResult:
        part_type = self.part_data.part_type

        if part_type == MessagePartType.TEXT:
            text = self.part_data.text or ""
            yield Static(text, classes="part-content")

        elif part_type == MessagePartType.TOOL:
            tool_name = self.part_data.tool or "unknown"
            state = self.part_data.state

            if state:
                status = state.status.value if isinstance(state.status, ToolState) else state.status
                status_class = f"tool-status-{status}"
                status_emoji = {
                    "pending": "⏳",
                    "running": "▶️",
                    "completed": "✅",
                    "error": "❌",
                    "unknown": "❓",
                }.get(status, "❓")

                yield Static(f"[bold cyan]{status_emoji} {tool_name}[/bold cyan]", classes="part-header")
                yield Static(f"[dim]Status: [{status_class}]{status}[/][/dim]", classes="part-content")

                if state.input_data:
                    yield Static(f"[dim]Input: {state.input_data}[/dim]", classes="part-content")

                if state.output:
                    yield Static("[dim]Output:[/dim]", classes="part-header")
                    lines = state.output.split("\n")[:10]
                    for line in lines:
                        yield Static(f"[dim]  {line}[/dim]", classes="part-content")
                    if len(state.output.split("\n")) > 10:
                        output_lines = state.output.split('\n')
                        yield Static(f"[dim]... ({len(output_lines)} more lines)[/dim]", classes="part-content")

        elif part_type == MessagePartType.FILE:
            filename = self.part_data.filename or ""
            mime = self.part_data.mime or ""
            yield Static(f"[bold green]📎 {filename}[/bold green] [dim]({mime})[/dim]", classes="part-header")

        elif part_type == MessagePartType.REASONING:
            text = self.part_data.text or ""
            yield Static("[bold yellow]💭 Thinking[/bold yellow]", classes="part-header")
            yield Static(f"[dim]{text}[/dim]", classes="part-content")

        elif part_type == MessagePartType.SNAPSHOT:
            snapshot_id = self.part_data.snapshot or ""
            yield Static(f"[bold magenta]📸 Snapshot:[/bold magenta] {snapshot_id}", classes="part-header")

        elif part_type == MessagePartType.PATCH:
            files = self.part_data.files or []
            files_count = len(files)
            patch_hash = self.part_data.hash or ""
            yield Static(f"[bold blue]🔧 Patch:[/bold blue] {files_count} files [dim]({patch_hash[:8]})[/dim]", classes="part-header")
            if files:
                for file in files[:5]:
                    yield Static(f"[dim]  • {file}[/dim]", classes="part-content")
                if len(files) > 5:
                    yield Static(f"[dim]  ... and {len(files) - 5} more[/dim]", classes="part-content")

        elif part_type == MessagePartType.AGENT:
            agent_name = self.part_data.name or ""
            yield Static(f"[bold purple]🤖 Agent:[/bold purple] {agent_name}", classes="part-header")

        elif part_type == MessagePartType.SUBTASK:
            session_id = self.part_data.session_id or ""
            category = self.part_data.category or ""
            yield Static(f"[bold purple]📋 Subtask:[/bold purple] {category}", classes="part-header")
            yield Static(f"[dim]{session_id}[/dim]", classes="part-content")

        elif part_type == MessagePartType.RETRY:
            attempt = self.part_data.attempt or 1
            yield Static(f"[bold orange]🔄 Retry:[/bold orange] Attempt {attempt}", classes="part-header")

        elif part_type == MessagePartType.COMPACTION:
            auto = self.part_data.auto or False
            yield Static(f"[bold cyan]📦 Compaction:[/bold cyan] {'Auto' if auto else 'Manual'}", classes="part-header")


class MessageView(Container):
    """Display a complete message with all parts"""

    CSS = """
    MessageView {
        padding: 0;
        margin-bottom: 0;
        border: none;
    }

    MessageView.user {
        background: $primary 5%;
        border-color: green;
    }

    MessageView.assistant {
        background: $primary 10%;
        border-color: blue;
    }

    MessageView.system {
        background: $primary 5%;
        border-color: gray;
    }

    .message-header {
        padding: 0 0 1 0;
        margin-bottom: 1;
    }

    .role-badge {
        padding: 0 1;
        border: solid;
        border-radius: 1;
    }

    .role-badge.user {
        border: green;
        color: green;
    }

    .role-badge.assistant {
        border: blue;
        color: blue;
    }

    .role-badge.system {
        border: gray;
        color: gray;
    }

    .timestamp {
        color: $text-muted;
        text-style: dim;
        margin-left: 1;
    }

    .streaming-indicator {
        color: cyan;
        text-style: italic;
    }
    """

    message_data: dict[str, Any]

    def __init__(self, message_data: dict[str, Any]):
        super().__init__()
        self.message_data = message_data

    def compose(self) -> ComposeResult:
        role = self.message_data.get("role", "user")
        is_streaming = self.message_data.get("is_streaming", False)

        role_color = {
            "user": "green",
            "assistant": "blue",
            "system": "gray",
        }.get(role, "white")

        role_emoji = {
            "user": "👤",
            "assistant": "🤖",
            "system": "⚙️",
        }.get(role, "❓")

        timestamp = self._format_timestamp()

        with Horizontal(classes="message-header"):
            yield Static(f"[{role_color}]{role_emoji} {role.upper()}[/]", classes=f"role-badge {role}")
            yield Static(timestamp, classes="timestamp")

        if is_streaming:
            yield Static("[cyan]✍️ Thinking...[/cyan]", classes="streaming-indicator")

        parts = self.message_data.get("parts", [])

        if parts:
            for part_data in parts:
                part_view = MessagePartView(MessagePartModel(**part_data))
                yield part_view
        else:
            yield Static("[dim italic]No content[/dim italic]")

    def _format_timestamp(self) -> str:
        """Format timestamp for display"""
        time_data = self.message_data.get("time", {})
        if isinstance(time_data, dict):
            created = time_data.get("created") or time_data.get("updated")
        else:
            created = None
        
        if created:
            try:
                import pendulum
                dt = pendulum.from_timestamp(created)
                return dt.strftime("HH:mm:ss")
            except Exception:
                return str(created)[:8]
        
        return ""

    def _compose_content(self) -> ComposeResult:
        """Compose message content for streaming updates"""
        return self.compose()
