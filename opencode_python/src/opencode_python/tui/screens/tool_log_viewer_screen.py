"""Tool Execution Log Viewer Screen

Provides a tool execution log viewer with diff preview:
- Displays tool execution logs in DataTable with Tool, Timestamp, Status, Duration columns
- Shows tool parameters and output in a details panel
- Displays diff preview for file changes
- Supports navigation with arrow keys
"""
from __future__ import annotations

from datetime import datetime
from typing import List
import logging

from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import DataTable, Static
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, RichLog


from opencode_python.tools.models import ToolExecutionLog


logger = logging.getLogger(__name__)


class ToolLogViewerScreen(Screen):
    """Tool execution log viewer screen"""

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("ctrl+c", "quit", "Quit"),
        ("enter", "show_log_details", "Details"),
    ]

    def __init__(self, logs: List[ToolExecutionLog], **kwargs):
        """Initialize ToolLogViewerScreen with execution logs"""
        super().__init__(**kwargs)
        self.logs = logs
        self._log_map: dict[str, ToolExecutionLog] = {l.id: l for l in logs}

    def compose(self) -> ComposeResult:
        """Build the tool log viewer screen UI"""
        with Vertical(id="tool-log-viewer-screen"):
            yield Static("Tool Execution Log", id="log-title")
            with Horizontal():
                yield DataTable(id="log-table")
                with Vertical(id="log-details-panel"):
                    yield Static("Select a log entry for details", id="log-details")

    def on_mount(self) -> None:
        """Called when screen is mounted - populate DataTable"""
        data_table = self.query_one(DataTable)

        data_table.add_column("Tool", width=15)
        data_table.add_column("Timestamp", width=20)
        data_table.add_column("Status", width=10)
        data_table.add_column("Duration", width=10)

        for log in self.logs:
            status = "✓" if log.success else "✗"
            duration = self._format_duration(log.duration_seconds)
            data_table.add_row(
                log.tool_name,
                self._format_timestamp(log.timestamp),
                status,
                duration,
                key=log.id,
            )

        data_table.cursor_type = "row"

    def action_show_log_details(self) -> None:
        """Handle Enter key to show log details"""
        data_table = self.query_one(DataTable)
        details_panel = self.query_one("#log-details", Static)

        try:
            cursor_coordinate = data_table.cursor_coordinate
            row_key, _ = data_table.coordinate_to_cell_key(cursor_coordinate)
            if row_key is not None:
                log_id = str(row_key)
                log = self._log_map.get(log_id)
                if log:
                    details_text = self._format_log_details(log)
                    details_panel.update(details_text)
        except Exception as e:
            logger.error(f"Error showing log details: {e}")
            details_panel.update("Error loading details")

    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return "Unknown"

    def _format_duration(self, duration: float | None) -> str:
        """Format duration for display"""
        if duration is None:
            return "N/A"
        if duration < 1:
            return f"{duration * 1000:.0f}ms"
        if duration < 60:
            return f"{duration:.1f}s"
        return f"{duration / 60:.1f}m"

    def _format_log_details(self, log: ToolExecutionLog) -> str:
        """Format log details for display"""
        details = f"[bold]Tool:[/bold] {log.tool_name}\n\n"
        details += f"[bold]Status:[/bold] {'Success' if log.success else 'Failed'}\n\n"
        details += f"[bold]Timestamp:[/bold] {self._format_timestamp(log.timestamp)}\n\n"

        if log.duration_seconds:
            details += f"[bold]Duration:[/bold] {self._format_duration(log.duration_seconds)}\n\n"

        if log.parameters:
            details += f"[bold]Parameters:[/bold]\n"
            for key, value in log.parameters.items():
                details += f"  {key}: {value}\n"
            details += "\n"

        if log.output:
            details += f"[bold]Output:[/bold]\n{log.output}\n\n"

        if log.error:
            details += f"[bold]Error:[/bold] {log.error}\n\n"

        if log.diff:
            details += f"[bold]File Changes:[/bold]\n"
            for path, changes in log.diff.items():
                details += f"  {path}: {changes}\n"

        return details
