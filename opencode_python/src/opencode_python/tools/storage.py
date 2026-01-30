"""Tool permission and execution log storage"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime

from opencode_python.storage.store import Storage
from opencode_python.tools.models import ToolPermission, ToolExecutionLog


class ToolPermissionStorage(Storage):
    """Storage for tool permissions"""

    async def get_permission(self, session_id: str, tool_id: str) -> Optional[ToolPermission]:
        """Get permission for a tool in a session"""
        data = await self.read(["tool_permission", session_id, tool_id])
        if data:
            return ToolPermission(**data)
        return None

    async def list_permissions(self, session_id: str) -> List[ToolPermission]:
        """List all permissions for a session"""
        keys = await self.list(["tool_permission", session_id])
        permissions = []
        for key in keys:
            data = await self.read(key)
            if data:
                permissions.append(ToolPermission(**data))
        return permissions

    async def create_permission(self, permission: ToolPermission) -> ToolPermission:
        """Create a new permission record"""
        await self.write(
            ["tool_permission", permission.session_id, permission.tool_id],
            permission.model_dump(mode="json")
        )
        return permission

    async def update_permission(self, permission: ToolPermission) -> ToolPermission:
        """Update an existing permission"""
        permission.time_updated = datetime.now().timestamp()
        await self.write(
            ["tool_permission", permission.session_id, permission.tool_id],
            permission.model_dump(mode="json")
        )
        return permission

    async def delete_permission(self, session_id: str, tool_id: str) -> bool:
        """Delete a permission record"""
        key = f"{tool_id}.json"
        return await self.remove(["tool_permission", session_id, key])


class ToolExecutionLogStorage(Storage):
    """Storage for tool execution logs"""

    async def get_log(self, log_id: str) -> Optional[ToolExecutionLog]:
        """Get execution log by ID"""
        data = await self.read(["tool_execution_log", log_id])
        if data:
            return ToolExecutionLog(**data)
        return None

    async def list_logs(self, session_id: str, tool_name: Optional[str] = None) -> List[ToolExecutionLog]:
        """List execution logs for a session, optionally filtered by tool"""
        keys = await self.list(["tool_execution_log", session_id])
        logs = []
        for key in keys:
            data = await self.read(key)
            if data:
                log = ToolExecutionLog(**data)
                if tool_name is None or log.tool_name == tool_name:
                    logs.append(log)
        logs.sort(key=lambda l: l.timestamp, reverse=True)
        return logs

    async def create_log(self, log: ToolExecutionLog) -> ToolExecutionLog:
        """Create a new execution log"""
        await self.write(
            ["tool_execution_log", log.session_id, log.id],
            log.model_dump(mode="json")
        )
        return log
