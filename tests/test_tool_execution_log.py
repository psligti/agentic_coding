"""Tests for tool execution logging and diff preview"""
from __future__ import annotations

import pytest
from pathlib import Path
import tempfile

from opencode_python.tools.models import ToolExecutionLog
from opencode_python.tools.storage import ToolExecutionLogStorage
from opencode_python.storage.store import Storage


@pytest.fixture
def temp_storage():
    """Create temporary storage for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage(Path(tmpdir))
        yield storage


@pytest.fixture
def log_storage(temp_storage):
    """Create tool execution log storage fixture"""
    from opencode_python.tools.storage import ToolExecutionLogStorage
    return ToolExecutionLogStorage(temp_storage.base_dir)


class TestToolExecutionLog:
    """Test tool execution log model"""

    def test_log_creation(self):
        """Test creating a tool execution log"""
        log = ToolExecutionLog(
            id="test-log-1",
            session_id="test-session",
            tool_name="bash",
            parameters={"command": "ls"},
            output="file1\nfile2",
            success=True,
        )

        assert log.id == "test-log-1"
        assert log.session_id == "test-session"
        assert log.tool_name == "bash"
        assert log.parameters == {"command": "ls"}
        assert log.output == "file1\nfile2"
        assert log.success is True

    def test_log_with_error(self):
        """Test creating a log with error"""
        log = ToolExecutionLog(
            id="test-log-2",
            session_id="test-session",
            tool_name="write",
            parameters={"path": "test.txt"},
            success=False,
            error="Permission denied",
        )

        assert log.success is False
        assert log.error == "Permission denied"

    def test_log_with_diff(self):
        """Test creating a log with file diff"""
        log = ToolExecutionLog(
            id="test-log-3",
            session_id="test-session",
            tool_name="write",
            parameters={"path": "test.txt"},
            success=True,
            diff={
                "test.txt": "+new content"
            },
        )

        assert log.diff == {"test.txt": "+new content"}

    def test_log_with_duration(self):
        """Test creating a log with duration"""
        log = ToolExecutionLog(
            id="test-log-4",
            session_id="test-session",
            tool_name="bash",
            parameters={},
            duration_seconds=1.5,
        )

        assert log.duration_seconds == 1.5


class TestToolExecutionLogStorage:
    """Test tool execution log storage operations"""

    @pytest.mark.asyncio
    async def test_create_log(self, log_storage):
        """Test creating a tool execution log"""
        log = ToolExecutionLog(
            id="test-log-1",
            session_id="test-session",
            tool_name="bash",
            parameters={"command": "echo hello"},
            output="hello",
            success=True,
        )

        created = await log_storage.create_log(log)

        assert created.id == log.id
        assert created.tool_name == log.tool_name
        assert created.success is True

    @pytest.mark.asyncio
    async def test_get_log(self, log_storage):
        """Test getting a tool execution log"""
        log = ToolExecutionLog(
            id="test-log-1",
            session_id="test-session",
            tool_name="bash",
            parameters={},
        )

        await log_storage.create_log(log)

        retrieved = await log_storage.get_log("test-log-1")

        assert retrieved is not None
        assert retrieved.id == "test-log-1"
        assert retrieved.session_id == "test-session"
        assert retrieved.tool_name == "bash"

    @pytest.mark.asyncio
    async def test_get_nonexistent_log(self, log_storage):
        """Test getting a non-existent log"""
        retrieved = await log_storage.get_log("nonexistent")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_logs(self, log_storage):
        """Test listing logs for a session"""
        await log_storage.create_log(
            ToolExecutionLog(
                id="log-1",
                session_id="test-session",
                tool_name="bash",
                parameters={},
            )
        )
        await log_storage.create_log(
            ToolExecutionLog(
                id="log-2",
                session_id="test-session",
                tool_name="write",
                parameters={},
            )
        )
        await log_storage.create_log(
            ToolExecutionLog(
                id="log-3",
                session_id="test-session",
                tool_name="read",
                parameters={},
            )
        )

        logs = await log_storage.list_logs("test-session")

        assert len(logs) == 3

        tool_names = {log.tool_name for log in logs}
        assert tool_names == {"bash", "write", "read"}

    @pytest.mark.asyncio
    async def test_list_logs_filtered_by_tool(self, log_storage):
        """Test listing logs filtered by tool name"""
        await log_storage.create_log(
            ToolExecutionLog(
                id="log-1",
                session_id="test-session",
                tool_name="bash",
                parameters={},
            )
        )
        await log_storage.create_log(
            ToolExecutionLog(
                id="log-2",
                session_id="test-session",
                tool_name="bash",
                parameters={},
            )
        )
        await log_storage.create_log(
            ToolExecutionLog(
                id="log-3",
                session_id="test-session",
                tool_name="write",
                parameters={},
            )
        )

        bash_logs = await log_storage.list_logs("test-session", tool_name="bash")

        assert len(bash_logs) == 2

        for log in bash_logs:
            assert log.tool_name == "bash"

    @pytest.mark.asyncio
    async def test_list_logs_ordered_by_timestamp(self, log_storage):
        """Test that logs are ordered by timestamp descending"""
        import time

        log1 = ToolExecutionLog(
            id="log-1",
            session_id="test-session",
            tool_name="bash",
            timestamp=time.time() - 100,
        )
        log2 = ToolExecutionLog(
            id="log-2",
            session_id="test-session",
            tool_name="bash",
            timestamp=time.time() - 50,
        )
        log3 = ToolExecutionLog(
            id="log-3",
            session_id="test-session",
            tool_name="bash",
            timestamp=time.time(),
        )

        await log_storage.create_log(log1)
        await log_storage.create_log(log2)
        await log_storage.create_log(log3)

        logs = await log_storage.list_logs("test-session")

        assert len(logs) == 3
        assert logs[0].timestamp >= logs[1].timestamp >= logs[2].timestamp
        assert logs[0].id == "log-3"
        assert logs[1].id == "log-2"
        assert logs[2].id == "log-1"

    @pytest.mark.asyncio
    async def test_list_logs_empty_session(self, log_storage):
        """Test listing logs for a session with no logs"""
        logs = await log_storage.list_logs("nonexistent-session")

        assert len(logs) == 0


class TestDiffPreview:
    """Test diff preview functionality"""

    def test_log_with_file_diff(self):
        """Test log containing file changes diff"""
        log = ToolExecutionLog(
            id="log-1",
            session_id="test-session",
            tool_name="write",
            parameters={"path": "test.txt"},
            diff={
                "test.txt": "+new content\n-old content",
                "other.txt": "+added line",
            },
        )

        assert log.diff is not None
        assert len(log.diff) == 2
        assert "test.txt" in log.diff
        assert "other.txt" in log.diff

    def test_log_without_diff(self):
        """Test log without file changes"""
        log = ToolExecutionLog(
            id="log-1",
            session_id="test-session",
            tool_name="bash",
            parameters={"command": "ls"},
        )

        assert log.diff is None

    def test_log_metadata_with_diff(self):
        """Test log with diff stored in diff field"""
        log = ToolExecutionLog(
            id="log-1",
            session_id="test-session",
            tool_name="write",
            diff={"file.txt": "+content"},
        )

        assert log.diff == {"file.txt": "+content"}
