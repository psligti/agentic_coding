"""Session service with handler injection.

This module provides the session service protocol and default implementation
that uses SessionManager for core logic and injected handlers for I/O.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable, List, Dict, Any
import warnings

from opencode_python.storage.store import SessionStorage
from opencode_python.core.session import SessionManager
from opencode_python.core.models import Session, Message
from opencode_python.interfaces.io import (
    IOHandler,
    ProgressHandler,
    NotificationHandler,
    QuietIOHandler,
    NoOpProgressHandler,
    NoOpNotificationHandler,
    Notification,
    NotificationType,
)


@runtime_checkable
class SessionService(Protocol):
    """Protocol for session service with handler injection.

    This protocol defines the interface for session operations that
    use injected handlers for I/O, progress, and notifications.
    """

    async def list_sessions(self) -> list[Session]:
        """List all sessions.

        Returns:
            List of Session objects.
        """
        ...

    async def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: The session ID.

        Returns:
            Session object or None if not found.
        """
        ...


class DefaultSessionService:
    """Default implementation of SessionService with handler injection.

    This service wraps SessionManager and uses injected handlers for
    user interaction, progress tracking, and notifications.
    """

    def __init__(
        self,
        storage: SessionStorage,
        project_dir: Path | None = None,
        io_handler: IOHandler | None = None,
        progress_handler: ProgressHandler | None = None,
        notification_handler: NotificationHandler | None = None,
    ):
        """Initialize session service with handlers.

        Args:
            storage: SessionStorage instance for persistence.
            project_dir: Project directory path (optional, defaults to cwd).
            io_handler: Optional I/O handler for user interaction.
            progress_handler: Optional progress handler for operations.
            notification_handler: Optional notification handler for feedback.
        """
        self.storage = storage
        self.project_dir = project_dir or Path.cwd()

        # Use provided handlers or no-op defaults
        self._io_handler = io_handler or QuietIOHandler()
        self._progress_handler = progress_handler or NoOpProgressHandler()
        self._notification_handler = notification_handler or NoOpNotificationHandler()

        # Initialize SessionManager
        self._manager = SessionManager(storage, self.project_dir)

    async def list_sessions(self) -> list[Session]:
        """List all sessions.

        Returns:
            List of Session objects.
        """
        sessions = await self._manager.list_sessions()
        return sessions

    async def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: The session ID.

        Returns:
            Session object or None if not found.
        """
        session = await self._manager.get_session(session_id)
        return session

    async def get_export_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data for export.

        Args:
            session_id: The session ID.

        Returns:
            Dictionary with session and messages data.
        """
        # Start progress
        self._progress_handler.start("Exporting session", 100)
        self._progress_handler.update(50, f"Loading session {session_id}")

        # Get export data from manager
        export_data = await self._manager.get_export_data(session_id)

        # Complete progress
        self._progress_handler.update(100, "Export complete")
        self._progress_handler.complete("Session exported successfully")

        # Show notification
        self._notification_handler.show(
            Notification(
                notification_type=NotificationType.SUCCESS,
                message=f"Session {session_id} exported",
                details={"message_count": len(export_data.get("messages", []))},
            )
        )

        return export_data

    async def import_session(
        self, session_data: Dict[str, Any], project_id: str | None = None
    ) -> Session:
        """Import session data.

        Args:
            session_data: Dictionary with session and messages data.
            project_id: Optional project ID for multi-project repos.

        Returns:
            The imported Session object.
        """
        # Start progress
        self._progress_handler.start("Importing session", 100)
        self._progress_handler.update(50, "Processing session data")

        # Import data via manager
        session = await self._manager.import_data(session_data, project_id)

        # Complete progress
        self._progress_handler.update(100, "Import complete")
        self._progress_handler.complete("Session imported successfully")

        # Show notification
        self._notification_handler.show(
            Notification(
                notification_type=NotificationType.SUCCESS,
                message=f"Session {session.id} imported",
                details={"title": session.title},
            )
        )

        return session
