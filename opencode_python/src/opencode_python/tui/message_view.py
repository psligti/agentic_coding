"""OpenCode Python - Message and Part rendering for TUI"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Markdown, Button, Input
from textual.app import ComposeResult
from textual.reactive import reactive
import logging

logger = logging.getLogger(__name__)


class MessagePartView(Container):
    """Display a message part (text, tool, file, etc.)"""

    def __init__(self, part_data: dict):
        super().__init__()
        self.part_data = part_data
        self.part_type = part_data.get("part_type", "text")

    def compose(self) -> None:
        """Build UI for the part type"""
        if self.part_type == "text":
            yield Static(f"[dim]{self.part_data.get('text', '')}[/dim]", id="part-content")
        
        elif self.part_type == "tool":
            tool_name = self.part_data.get("tool", "unknown")
            status = self.part_data.get("state", {}).get("status", "unknown")
            output = self.part_data.get("output", "")
            
            yield Static(f"[bold cyan]Tool:[/bold cyan] {tool_name}")
            yield Static(f"[dim]Status:[/dim] {status}")
            if output:
                lines = output.split("\n")[:10]
                for line in lines:
                    yield Static(f"[dim]  {line}[/dim]")
                if len(output.split("\n")) > 10:
                    output_lines = output.split('\n')
                    yield Static(f"[dim]... ({len(output_lines)} more lines)[/dim]")
            
        elif self.part_type == "file":
            filename = self.part_data.get("filename", "")
            mime = self.part_data.get("mime", "")
            yield Static(f"[bold green]File:[/bold green] {filename} ({mime})")
        
        elif self.part_type == "reasoning":
            text = self.part_data.get("text", "")
            yield Static(f"[bold yellow]Thinking:[/bold yellow]")
            yield Static(f"[dim]{text}[/dim]")
        
        elif self.part_type == "snapshot":
            snapshot_id = self.part_data.get("snapshot", "")
            yield Static(f"[bold magenta]Snapshot:[/bold magenta] {snapshot_id}")
        
        elif self.part_type == "patch":
            files_count = len(self.part_data.get("files", []))
            patch_hash = self.part_data.get("hash", "")
            yield Static(f"[bold blue]Patch:[/bold blue] {files_count} files ({patch_hash})")
        
        elif self.part_type == "agent":
            agent_name = self.part_data.get("name", "")
            yield Static(f"[bold purple]Agent:[/bold purple] {agent_name}")
        
        elif self.part_type == "subtask":
            session_id = self.part_data.get("session_id", "")
            yield Static(f"[bold purple]Subtask:[/bold purple] {session_id}")
        
        elif self.part_type == "retry":
            attempt = self.part_data.get("attempt", 1)
            yield Static(f"[bold orange]Retry:[/bold orange] Attempt {attempt}")
        
        elif self.part_type == "compaction":
            auto = self.part_data.get("auto", False)
            yield Static(f"[bold cyan]Compaction:[/bold cyan] {'Auto' if auto else 'Manual'}")


class MessageView(Container):
    """Display a complete message with all parts"""

    def __init__(self, message_data: dict):
        super().__init__()
        self.message_data = message_data
        self.role = message_data.get("role", "user")
        self.created = message_data.get("created", "")

    def compose(self) -> None:
        """Build UI for the complete message"""
        # Header
        role_color = "green" if self.role == "user" else "blue"
        yield Static(f"[bold {role_color}]Role:[/bold {role_color}] {self.role.upper()}")
        yield Static(f"[dim]Created:[/dim] {self._format_timestamp(self.created)}")
        yield Static("")

        # Message content parts
        parts = self.message_data.get("parts", [])
        
        if parts:
            yield Static("[bold]Message:[/bold]")
            for part_data in parts:
                part_view = MessagePartView(part_data)
                yield part_view
        else:
            yield Static("[dim italic]No content[/dim italic]")

    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        import pendulum
        try:
            dt = pendulum.from_timestamp(timestamp)
            return dt.format("YYYY-MM-DD HH:mm")
        except Exception:
            return str(timestamp)
