"""Tests for tool permissioning and allow/deny workflow"""
from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import asyncio

from opencode_python.tools.models import ToolPermission
from opencode_python.tools.storage import ToolPermissionStorage
from opencode_python.storage.store import Storage


@pytest.fixture
def temp_storage():
    """Create temporary storage for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(Path(tmpdir))
        yield storage


@pytest.fixture
def permission_storage(temp_storage):
    """Create tool permission storage fixture"""
    from opencode_python.tools.storage import ToolPermissionStorage
    return ToolPermissionStorage(temp_storage.base_dir)


class TestToolPermission:
    """Test tool permission model"""

    def test_permission_creation(self):
        """Test creating a tool permission"""
        permission = ToolPermission(
            session_id="test-session",
            tool_id="bash",
            state="allowed",
            reason="User approved",
        )

        assert permission.session_id == "test-session"
        assert permission.tool_id == "bash"
        assert permission.state == "allowed"
        assert permission.reason == "User approved"

    def test_permission_states(self):
        """Test different permission states"""
        states = ["allowed", "denied", "pending"]

        for state in states:
            permission = ToolPermission(
                session_id="test-session",
                tool_id="bash",
                state=state,
            )
            assert permission.state == state


class TestToolPermissionStorage:
    """Test tool permission storage operations"""

    @pytest.mark.asyncio
    async def test_create_permission(self, permission_storage):
        """Test creating a tool permission"""
        permission = ToolPermission(
            session_id="test-session",
            tool_id="bash",
            state="allowed",
            reason="Test",
        )

        created = await permission_storage.create_permission(permission)

        assert created.session_id == permission.session_id
        assert created.tool_id == permission.tool_id
        assert created.state == permission.state

    @pytest.mark.asyncio
    async def test_get_permission(self, permission_storage):
        """Test getting a tool permission"""
        permission = ToolPermission(
            session_id="test-session",
            tool_id="bash",
            state="denied",
        )

        await permission_storage.create_permission(permission)

        retrieved = await permission_storage.get_permission("test-session", "bash")

        assert retrieved is not None
        assert retrieved.session_id == "test-session"
        assert retrieved.tool_id == "bash"
        assert retrieved.state == "denied"

    @pytest.mark.asyncio
    async def test_get_nonexistent_permission(self, permission_storage):
        """Test getting a non-existent permission"""
        retrieved = await permission_storage.get_permission("nonexistent", "bash")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_permissions(self, permission_storage):
        """Test listing all permissions for a session"""
        await permission_storage.create_permission(
            ToolPermission(session_id="test-session", tool_id="bash", state="allowed")
        )
        await permission_storage.create_permission(
            ToolPermission(session_id="test-session", tool_id="write", state="denied")
        )
        await permission_storage.create_permission(
            ToolPermission(session_id="test-session", tool_id="read", state="allowed")
        )

        permissions = await permission_storage.list_permissions("test-session")

        assert len(permissions) == 3

        tool_ids = {p.tool_id for p in permissions}
        assert tool_ids == {"bash", "write", "read"}

    @pytest.mark.asyncio
    async def test_update_permission(self, permission_storage):
        """Test updating a tool permission"""
        permission = ToolPermission(
            session_id="test-session",
            tool_id="bash",
            state="allowed",
            reason="Original",
        )

        await permission_storage.create_permission(permission)

        updated = ToolPermission(
            session_id="test-session",
            tool_id="bash",
            state="denied",
            reason="Updated",
        )

        result = await permission_storage.update_permission(updated)

        assert result.state == "denied"
        assert result.reason == "Updated"
        assert result.time_updated > permission.time_updated

    @pytest.mark.asyncio
    async def test_delete_permission(self, permission_storage):
        """Test deleting a tool permission"""
        permission = ToolPermission(
            session_id="test-session",
            tool_id="bash",
            state="allowed",
        )

        await permission_storage.create_permission(permission)

        deleted = await permission_storage.delete_permission("test-session", "bash")

        assert deleted is True

        retrieved = await permission_storage.get_permission("test-session", "bash")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_permission(self, permission_storage):
        """Test deleting a non-existent permission"""
        deleted = await permission_storage.delete_permission("nonexistent", "bash")

        assert deleted is False


class TestAllowDenyWorkflow:
    """Test allow/deny workflow"""

    @pytest.mark.asyncio
    async def test_allow_tool_then_deny(self, permission_storage):
        """Test workflow: allow tool, then deny it"""
        session_id = "test-session"
        tool_id = "bash"

        # Allow the tool
        allowed = ToolPermission(
            session_id=session_id,
            tool_id=tool_id,
            state="allowed",
            reason="User approved",
        )
        await permission_storage.create_permission(allowed)

        retrieved = await permission_storage.get_permission(session_id, tool_id)
        assert retrieved.state == "allowed"

        # Deny the tool
        denied = ToolPermission(
            session_id=session_id,
            tool_id=tool_id,
            state="denied",
            reason="User denied",
        )
        await permission_storage.update_permission(denied)

        retrieved = await permission_storage.get_permission(session_id, tool_id)
        assert retrieved.state == "denied"
        assert retrieved.reason == "User denied"

    @pytest.mark.asyncio
    async def test_multiple_session_permissions(self, permission_storage):
        """Test that permissions are session-scoped"""
        tool_id = "bash"

        # Session 1: allow bash
        await permission_storage.create_permission(
            ToolPermission(session_id="session-1", tool_id=tool_id, state="allowed")
        )

        # Session 2: deny bash
        await permission_storage.create_permission(
            ToolPermission(session_id="session-2", tool_id=tool_id, state="denied")
        )

        perm1 = await permission_storage.get_permission("session-1", tool_id)
        perm2 = await permission_storage.get_permission("session-2", tool_id)

        assert perm1.state == "allowed"
        assert perm2.state == "denied"

    @pytest.mark.asyncio
    async def test_list_permissions_returns_session_specific(self, permission_storage):
        """Test that list_permissions only returns permissions for specific session"""
        # Create permissions for different sessions
        await permission_storage.create_permission(
            ToolPermission(session_id="session-1", tool_id="bash", state="allowed")
        )
        await permission_storage.create_permission(
            ToolPermission(session_id="session-1", tool_id="write", state="allowed")
        )
        await permission_storage.create_permission(
            ToolPermission(session_id="session-2", tool_id="bash", state="denied")
        )

        # List permissions for session-1
        perms1 = await permission_storage.list_permissions("session-1")
        assert len(perms1) == 2

        # List permissions for session-2
        perms2 = await permission_storage.list_permissions("session-2")
        assert len(perms2) == 1
