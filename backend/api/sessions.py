"""Session management API endpoints."""

import os
import tempfile
import hashlib
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Coroutine

from fastapi import APIRouter, Body, HTTPException, status

from opencode_python.sdk import OpenCodeAsyncClient
from opencode_python.core.config import SDKConfig
from opencode_python.core.session import SessionManager
from opencode_python.storage.store import SessionStorage
from opencode_python.agents.runtime import AgentRuntime, create_agent_runtime
from opencode_python.agents.orchestrator import AgentOrchestrator, create_agent_orchestrator
from opencode_python.agents.registry import create_agent_registry
from opencode_python.core.session_lifecycle import SessionLifecycle
from pydantic import BaseModel


def handle_session_errors(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Decorator for consistent error handling in session endpoints.

    Args:
        func: The function to wrap.

    Returns:
        Wrapped function with consistent error handling.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{getattr(func, '__name__', str(func))} failed: {str(e)}",
            )
    return wrapper


class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""

    title: str
    version: str = "1.0.0"
    theme_id: Optional[str] = None


class ExecuteSessionRequest(BaseModel):
    """Request model for executing an agent in a session."""

    agent_name: str
    user_message: str
    options: Optional[Dict[str, Any]] = None


class UpdateSessionRequest(BaseModel):
    """Request model for updating session metadata."""

    theme_id: Optional[str] = None


router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


_api_storage_dir = None
_api_client = None
_api_test_name = None
_api_runtime = None
_api_lifecycle = None
_api_orchestrator = None


async def get_sdk_client() -> OpenCodeAsyncClient:
    """Get SDK client instance with shared storage.

    Returns:
        OpenCodeAsyncClient: Initialized SDK client.

    Raises:
        HTTPException: If client initialization fails.
    """
    global _api_storage_dir, _api_client, _api_test_name

    try:
        current_test = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test and current_test != _api_test_name:
            _api_test_name = current_test
            _api_client = None
            test_key = hashlib.sha1(current_test.encode("utf-8")).hexdigest()[:12]
            _api_storage_dir = os.path.join(tempfile.gettempdir(), "test_sessions", test_key)

        if _api_client is not None:
            return _api_client

        if _api_storage_dir is None:
            _api_storage_dir = os.path.join(tempfile.gettempdir(), "api_sessions")

        # Create SDKConfig with custom project_dir and storage_path
        storage_dir = _api_storage_dir or os.path.join(tempfile.gettempdir(), "api_sessions")
        storage_path = Path(storage_dir)
        project_dir = Path(os.environ.get("WEBAPP_PROJECT_DIR", Path.cwd()))
        config = SDKConfig(
            storage_path=storage_path,
            project_dir=project_dir,
        )
        # Create client with custom config
        _api_client = OpenCodeAsyncClient(config=config)
        return _api_client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize SDK client: {str(e)}",
        )


def get_session_manager(client: OpenCodeAsyncClient) -> SessionManager:
    """Create a SessionManager backed by the API client's configured storage."""
    storage = SessionStorage(client.config.storage_path)
    return SessionManager(storage=storage, project_dir=Path(client.config.project_dir))


def get_agent_runtime() -> AgentRuntime:
    """Get AgentRuntime instance for API.

    Returns:
        AgentRuntime: Initialized runtime for agent execution.

    Raises:
        HTTPException: If runtime initialization fails.
    """
    global _api_runtime, _api_lifecycle

    try:
        if _api_runtime is not None:
            return _api_runtime

        _api_storage_dir_local = _api_storage_dir
        if _api_storage_dir_local is None:
            _api_storage_dir_local = os.path.join(tempfile.gettempdir(), "api_sessions")

        storage_path = Path(_api_storage_dir_local)
        project_dir = Path(os.environ.get("WEBAPP_PROJECT_DIR", Path.cwd()))

        _api_lifecycle = SessionLifecycle()

        agent_registry = create_agent_registry(
            persistence_enabled=False,
            storage_dir=_api_storage_dir_local,
        )

        _api_runtime = create_agent_runtime(
            agent_registry=agent_registry,
            base_dir=project_dir,
            session_lifecycle=_api_lifecycle,
        )

        return _api_runtime
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize agent runtime: {str(e)}",
        )


def get_agent_orchestrator() -> AgentOrchestrator:
    """Get AgentOrchestrator instance for API.

    Returns:
        AgentOrchestrator: Initialized orchestrator for multi-agent coordination.

    Raises:
        HTTPException: If orchestrator initialization fails.
    """
    global _api_orchestrator

    try:
        if _api_orchestrator is not None:
            return _api_orchestrator

        runtime = get_agent_runtime()
        _api_orchestrator = create_agent_orchestrator(agent_runtime=runtime)

        return _api_orchestrator
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize agent orchestrator: {str(e)}",
        )


@router.get("", response_model=Dict[str, Any])
@handle_session_errors
async def list_sessions() -> Dict[str, Any]:
    """List all sessions.

    Returns:
        Dictionary containing the list of sessions.

    Raises:
        HTTPException: 500 if listing sessions fails.
    """
    client = await get_sdk_client()
    sessions = await client.list_sessions()

    return {
        "sessions": [
            {
                "id": session.id,
                "title": session.title,
                "version": session.version,
                "theme_id": session.theme_id,
                "created_at": datetime.fromtimestamp(session.time_created).isoformat(),
                "updated_at": datetime.fromtimestamp(session.time_updated).isoformat(),
            }
            for session in sessions
        ],
        "count": len(sessions),
    }


@router.get("/{session_id}", response_model=Dict[str, Any])
@handle_session_errors
async def get_session(session_id: str) -> Dict[str, Any]:
    """Get a single session by ID.

    Args:
        session_id: The session ID to retrieve.

    Returns:
        Dictionary containing session details.

    Raises:
        HTTPException: 404 if session not found, 500 if retrieval fails.
    """
    client = await get_sdk_client()
    session = await client.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    return {
        "id": session.id,
        "title": session.title,
        "version": session.version,
        "theme_id": session.theme_id,
        "created_at": datetime.fromtimestamp(session.time_created).isoformat(),
        "updated_at": datetime.fromtimestamp(session.time_updated).isoformat(),
    }


@router.post("", response_model=Dict[str, Any])
async def create_session(request: CreateSessionRequest = Body(...)) -> Dict[str, Any]:
    """Create a new session.

    Args:
        request: CreateSessionRequest with title and optional version.

    Returns:
        Dictionary containing the created session details.

    Raises:
        HTTPException: 400 for invalid input, 500 if creation fails.
    """
    if not request.title or not request.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session title is required and cannot be empty",
        )

    client = await get_sdk_client()
    session = await client.create_session(title=request.title, version=request.version)

    if request.theme_id:
        manager = get_session_manager(client)
        session = await manager.update_session(
            session_id=session.id,
            theme_id=request.theme_id
        )

    return {
        "id": session.id,
        "title": session.title,
        "version": request.version,
        "theme_id": session.theme_id,
        "created_at": datetime.fromtimestamp(session.time_created).isoformat(),
        "updated_at": datetime.fromtimestamp(session.time_updated).isoformat(),
    }


@router.delete("/{session_id}", response_model=Dict[str, Any])
@handle_session_errors
async def delete_session(session_id: str) -> Dict[str, Any]:
    """Delete a session by ID.

    Args:
        session_id: The session ID to delete.

    Returns:
        Dictionary confirming deletion.

    Raises:
        HTTPException: 404 if session not found, 500 if deletion fails.
    """
    client = await get_sdk_client()
    deleted = await client.delete_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    return {
        "message": "Session deleted successfully",
        "session_id": session_id,
    }


@router.put("/{session_id}", response_model=Dict[str, Any])
@handle_session_errors
async def update_session(session_id: str, request: UpdateSessionRequest = Body(...)) -> Dict[str, Any]:
    """Update session metadata including theme_id."""
    if request.theme_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="theme_id is required for this update endpoint",
        )

    client = await get_sdk_client()
    session = await client.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    manager = get_session_manager(client)

    updated_session = await manager.update_session(
        session_id=session_id,
        theme_id=request.theme_id
    )

    from api.sessions_streaming import _notify_theme_change
    await _notify_theme_change(session_id, request.theme_id)

    return {
        "id": updated_session.id,
        "title": updated_session.title,
        "theme_id": updated_session.theme_id,
        "created_at": datetime.fromtimestamp(updated_session.time_created).isoformat(),
        "updated_at": datetime.fromtimestamp(updated_session.time_updated).isoformat(),
    }


@router.post("/{session_id}/execute", response_model=Dict[str, Any])
@handle_session_errors
async def execute_session(session_id: str, request: ExecuteSessionRequest = Body(...)) -> Dict[str, Any]:
    """Execute an agent within an existing session."""
    if not request.user_message or not request.user_message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User message is required",
        )

    client = await get_sdk_client()
    session = await client.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    from api.sessions_streaming import (
        _notify_agent_started,
        _notify_agent_completed,
        _notify_agent_failed,
    )

    task_id = request.options.get("task_id") if request.options else None

    await _notify_agent_started(session_id, request.agent_name, task_id)

    try:
        result = await client.execute_agent(
            agent_name=request.agent_name,
            session_id=session_id,
            user_message=request.user_message,
            options=request.options or {},
        )

        if result.error:
            await _notify_agent_failed(session_id, request.agent_name, result.error, result.duration, task_id)
        else:
            await _notify_agent_completed(session_id, request.agent_name, result.duration, task_id)

        return {
            "session_id": session_id,
            "agent_name": result.agent_name,
            "response": result.response,
            "tools_used": result.tools_used,
            "duration": result.duration,
            "error": result.error,
        }
    except Exception as e:
        duration = 0.0
        await _notify_agent_failed(session_id, request.agent_name, str(e), duration, task_id)
        raise
