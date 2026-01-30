"""Tools Panel Screen

Provides a tools panel for discovering available tools and managing permissions:
- Displays tools in DataTable with Name, Description, Category, Permission columns
- Supports navigation with arrow keys
- Enter key shows tool details
- 'p' key toggles tool permission (allow/deny)
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import logging

from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import DataTable, Static
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Footer


from opencode_python.tools.models import ToolDiscovery
from opencode_python.core.event_bus import bus, Events


logger = logging.getLogger(__name__)


class ToolsPanelScreen(Screen):
    """Tools panel for discovering available tools and managing permissions"""

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("ctrl+c", "quit", "Quit"),
        ("enter", "show_tool_details", "Details"),
        ("p", "toggle_permission", "Toggle Permission"),
    ]

    def __init__(self, tools: List[Dict[str, Any]], session_id: str, **kwargs):
        """Initialize ToolsPanelScreen with tools list and session_id"""
        super().__init__(**kwargs)
        self.tools = tools
        self.session_id = session_id
        self._tool_map: Dict[str, Dict[str, Any]] = {t["tool_id"]: t for t in tools}

    def compose(self) -> ComposeResult:
        """Build the tools panel screen UI"""
        with Vertical(id="tools-panel-screen"):
            yield Static("Tools Panel", id="tools-title")
            with Horizontal():
                yield DataTable(id="tools-table")

    def on_mount(self) -> None:
        """Called when screen is mounted - populate DataTable"""
        data_table = self.query_one(DataTable)

        data_table.add_column("Tool ID", width=20)
        data_table.add_column("Name", width=15)
        data_table.add_column("Description", width=40)
        data_table.add_column("Category", width=15)
        data_table.add_column("Permission", width=10)

        for tool in self.tools:
            permission_state = tool.get("permission_state", "pending")
            data_table.add_row(
                tool["tool_id"],
                tool["name"],
                tool.get("description", ""),
                tool.get("category", "N/A"),
                permission_state.capitalize(),
                key=tool["tool_id"],
            )

        data_table.cursor_type = "row"

    def action_show_tool_details(self) -> None:
        """Handle Enter key to show tool details"""
        data_table = self.query_one(DataTable)

        try:
            cursor_coordinate = data_table.cursor_coordinate
            row_key, _ = data_table.coordinate_to_cell_key(cursor_coordinate)
            if row_key is not None:
                tool_id = str(row_key)
                tool = self._tool_map.get(tool_id)
                if tool:
                    logger.info(f"Showing tool details: {tool['name']}")
                    self._show_tool_details_dialog(tool)
        except Exception as e:
            logger.error(f"Error showing tool details: {e}")

    async def action_toggle_permission(self) -> None:
        """Toggle tool permission (allow/deny)"""
        data_table = self.query_one(DataTable)

        try:
            cursor_coordinate = data_table.cursor_coordinate
            row_key, _ = data_table.coordinate_to_cell_key(cursor_coordinate)
            if row_key is not None:
                tool_id = str(row_key)
                tool = self._tool_map.get(tool_id)
                if tool:
                    current_state = tool.get("permission_state", "pending")
                    new_state = "denied" if current_state == "allowed" else "allowed"
                    tool["permission_state"] = new_state
                    await self._update_tool_permission(tool_id, new_state)

                    data_table.update_cell(row_key, "Permission", new_state.capitalize())
                    logger.info(f"Toggled permission for {tool['name']}: {new_state}")
        except Exception as e:
            logger.error(f"Error toggling permission: {e}")

    async def _update_tool_permission(self, tool_id: str, state: str) -> None:
        """Update tool permission in storage and emit event"""
        from opencode_python.tools.storage import ToolPermissionStorage
        from opencode_python.tools.models import ToolPermission
        from opencode_python.storage.store import Storage

        try:
            storage = Storage(Path(self.app.storage_base_dir))
            permission_storage = ToolPermissionStorage(storage.base_dir)

            existing = await permission_storage.get_permission(self.session_id, tool_id)
            if existing:
                updated = ToolPermission(
                    session_id=existing.session_id,
                    tool_id=existing.tool_id,
                    state=state,
                    reason=f"User toggled to {state}",
                )
                await permission_storage.update_permission(updated)
            else:
                permission = ToolPermission(
                    session_id=self.session_id,
                    tool_id=tool_id,
                    state=state,
                    reason=f"User set to {state}",
                )
                await permission_storage.create_permission(permission)

            event_name = Events.TOOL_ALLOW if state == "allowed" else Events.TOOL_DENY
            await bus.publish(event_name, {
                "session_id": self.session_id,
                "tool_name": tool_id,
            })
        except Exception as e:
            logger.error(f"Error updating tool permission: {e}")

    def _show_tool_details_dialog(self, tool: Dict[str, Any]) -> None:
        """Show tool details in a dialog"""
        logger.info(f"Tool details for {tool['name']}: {tool.get('description', 'N/A')}")
        pass
