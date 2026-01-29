"""OpenCode Python - Session List Screen for TUI

Provides a session list screen with DataTable for browsing and selecting sessions:
- Displays sessions in DataTable with ID, Title, and Time columns
- Supports navigation with arrow keys
- Enter key opens selected session in MessageScreen
"""

from typing import List
import logging

from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import DataTable
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

from opencode_python.core.models import Session


logger = logging.getLogger(__name__)


class SessionListScreen(Screen):
    """Session list screen for browsing and selecting sessions"""

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("ctrl+c", "quit", "Quit"),
        ("enter", "open_selected_session", "Open"),
    ]

    sessions: List[Session]

    def __init__(self, sessions: List[Session], **kwargs):
        """Initialize SessionListScreen with session list"""
        super().__init__(**kwargs)
        self.sessions = sessions

    def compose(self) -> ComposeResult:
        """Build the session list screen UI"""
        with Vertical(id="session-list-screen"):
            yield DataTable(id="session-table")

    def on_mount(self) -> None:
        """Called when screen is mounted - populate DataTable"""
        data_table = self.query_one(DataTable)
        if data_table is None:
            return

        data_table.title = "Sessions"

        # Add columns
        data_table.add_column("ID", width=15)
        data_table.add_column("Title", width=40)
        data_table.add_column("Time", width=20)

        # Add rows for each session
        for session in self.sessions:
            row_key = data_table.add_row(
                session.id,
                session.title,
                self._format_time(session.time_updated),
                key=session.id,
            )

        # Clear selection and focus on first row
        data_table.clear_selected()
        if data_table.row_count > 0:
            data_table.move_cursor(end=False)

    def _format_time(self, timestamp: float) -> str:
        """Format timestamp for display"""
        from datetime import datetime

        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return "Unknown"

    def action_open_selected_session(self) -> None:
        """Handle Enter key to open selected session"""
        data_table = self.query_one(DataTable)
        selected_row = data_table.selected_row

        if selected_row is None:
            logger.warning("No session selected")
            return

        session_id = data_table.row_key(selected_row).key
        selected_session = self._find_session_by_id(session_id)

        if selected_session is None:
            logger.error(f"Session not found: {session_id}")
            return

        logger.info(f"Opening session: {selected_session.title} ({selected_session.id})")

        # Import here to avoid circular dependency
        from opencode_python.tui.screens.message_screen import MessageScreen

        self.push_screen("message", selected_session)

    def _find_session_by_id(self, session_id: str) -> Session | None:
        """Find session by ID from the session list"""
        for session in self.sessions:
            if session.id == session_id:
                return session
        return None
