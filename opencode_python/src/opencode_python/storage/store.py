"""OpenCode Python - Storage backend for sessions and messages"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import aiofiles
import asyncio
import logging
from datetime import datetime
import hashlib
import uuid

from opencode_python.core.models import Session, Message

logger = logging.getLogger(__name__)


class SessionStorage:
    """JSON file-based session storage"""

    def __init__(self, base_dir: Path):
        """Initialize storage with base directory"""
        self.base_dir = base_dir
        self.sessions_file = base_dir / "sessions.json"
        self._lock = asyncio.Lock()

    async def create_session(self, session: Session) -> bool:
        """Create a new session"""
        async with self._lock:
            sessions = await self._load_sessions()
            sessions[session.id] = session.model_dump(mode="json")
            await self._save_sessions(sessions)
            logger.info(f"Created session: {session.id}")
            return True

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        sessions = await self._load_sessions()
        session_data = sessions.get(session_id)
        if session_data:
            return Session(**session_data)
        return None

    async def update_session(self, session: Session) -> bool:
        """Update existing session"""
        async with self._lock:
            sessions = await self._load_sessions()
            if session.id in sessions:
                session_data = session.model_dump(mode="json")
                session_data["time_updated"] = datetime.now().timestamp()
                sessions[session.id] = session_data
                await self._save_sessions(sessions)
                logger.debug(f"Updated session: {session.id}")
                return True
            return False

    async def delete_session(self, session_id: str, project_id: str) -> bool:
        """Delete a session"""
        async with self._lock:
            sessions = await self._load_sessions()
            if session_id in sessions:
                # Check project_id matches
                if sessions[session_id].get("project_id") == project_id:
                    del sessions[session_id]
                    await self._save_sessions(sessions)
                    logger.info(f"Deleted session: {session_id}")
                    return True
            return False

    async def list_sessions(self, project_id: str) -> List[Dict[str, Any]]:
        """List all sessions for a project"""
        sessions = await self._load_sessions()
        return [
            s for s in sessions.values()
            if s.get("project_id") == project_id
        ]

    async def _load_sessions(self) -> Dict[str, Any]:
        """Load sessions from JSON file"""
        if not self.sessions_file.exists():
            return {}

        try:
            async with aiofiles.open(self.sessions_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return {}

    async def _save_sessions(self, sessions: Dict[str, Any]) -> None:
        """Save sessions to JSON file"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        try:
            content = json.dumps(sessions, indent=2)
            async with aiofiles.open(self.sessions_file, "w") as f:
                await f.write(content)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")


class MessageStorage:
    """JSON file-based message storage"""

    def __init__(self, base_dir: Path):
        """Initialize message storage"""
        self.base_dir = base_dir
        self.messages_dir = base_dir / "messages"
        self._lock = asyncio.Lock()

    async def create_message(self, session_id: str, message: Message) -> bool:
        """Create a message for a session"""
        async with self._lock:
            self.messages_dir.mkdir(parents=True, exist_ok=True)
            message_file = self._message_file(session_id, message.id)
            message_data = message.model_dump(mode="json")

            try:
                content = json.dumps(message_data, indent=2)
                async with aiofiles.open(message_file, "w") as f:
                    await f.write(content)
                return True
            except Exception as e:
                logger.error(f"Failed to create message: {e}")
                return False

    async def get_message(self, session_id: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Get message by session and message ID"""
        message_file = self._message_file(session_id, message_id)
        if not message_file.exists():
            return None

        try:
            async with aiofiles.open(message_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load message: {e}")
            return None

    async def list_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """List all messages for a session"""
        session_dir = self.messages_dir / session_id
        if not session_dir.exists():
            return []

        messages = []
        for message_file in session_dir.glob("*.json"):
            try:
                async with aiofiles.open(message_file, "r") as f:
                    content = await f.read()
                    messages.append(json.loads(content))
            except Exception as e:
                logger.error(f"Failed to load message from {message_file}: {e}")

        return sorted(messages, key=lambda m: m.get("time", {}).get("created", 0))

    async def delete_message(self, session_id: str, message_id: str) -> bool:
        """Delete a message"""
        message_file = self._message_file(session_id, message_id)
        if not message_file.exists():
            return False

        try:
            message_file.unlink()
            logger.info(f"Deleted message: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False

    def _message_file(self, session_id: str, message_id: str) -> Path:
        """Get file path for a message"""
        session_dir = self.messages_dir / session_id
        return session_dir / f"{message_id}.json"


class PartStorage:
    """JSON file-based part storage for message parts"""

    def __init__(self, base_dir: Path):
        """Initialize part storage"""
        self.base_dir = base_dir
        self.parts_dir = base_dir / "parts"
        self._lock = asyncio.Lock()

    async def create_part(self, message_id: str, part: Any) -> bool:
        """Create a part for a message"""
        async with self._lock:
            self.parts_dir.mkdir(parents=True, exist_ok=True)
            part_file = self._part_file(message_id, part.id)

            try:
                part_data = part.model_dump(mode="json") if hasattr(part, "model_dump") else part.__dict__
                content = json.dumps(part_data, indent=2)
                async with aiofiles.open(part_file, "w") as f:
                    await f.write(content)
                return True
            except Exception as e:
                logger.error(f"Failed to create part: {e}")
                return False

    async def get_part(self, message_id: str, part_id: str) -> Optional[Dict[str, Any]]:
        """Get part by message and part ID"""
        part_file = self._part_file(message_id, part_id)
        if not part_file.exists():
            return None

        try:
            async with aiofiles.open(part_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load part: {e}")
            return None

    async def list_parts(self, message_id: str) -> List[Dict[str, Any]]:
        """List all parts for a message"""
        message_dir = self.parts_dir / message_id
        if not message_dir.exists():
            return []

        parts = []
        for part_file in message_dir.glob("*.json"):
            try:
                async with aiofiles.open(part_file, "r") as f:
                    content = await f.read()
                    parts.append(json.loads(content))
            except Exception as e:
                logger.error(f"Failed to load part from {part_file}: {e}")

        return parts

    def _part_file(self, message_id: str, part_id: str) -> Path:
        """Get file path for a part"""
        message_dir = self.parts_dir / message_id
        return message_dir / f"{part_id}.json"
