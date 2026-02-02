"""Agent execution endpoints for WebApp API."""

import asyncio
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel

from opencode_python.sdk import OpenCodeAsyncClient
from opencode_python.core.config import SDKConfig


class ExecuteAgentRequest(BaseModel):
    """Request model for executing an agent."""

    message: str
    options: Optional[Dict[str, Any]] = None


class ExecuteAgentResponse(BaseModel):
    """Response model for agent execution."""

    task_id: str
    status: str
    message: str
    session_id: str


_api_storage_dir = None
_background_tasks: Dict[str, asyncio.Task] = {}
task_status: Dict[str, str] = {}


router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


async def get_sdk_client() -> OpenCodeAsyncClient:
    """Get SDK client instance with shared storage.

    Returns:
        OpenCodeAsyncClient: Initialized SDK client.

    Raises:
        HTTPException: If client initialization fails.
    """
    global _api_storage_dir

    try:
        if _api_storage_dir is None:
            _api_storage_dir = os.path.join(tempfile.gettempdir(), "api_agents")

        storage_path = Path(_api_storage_dir)
        config = SDKConfig(
            storage_path=storage_path,
            project_dir=storage_path,
        )
        client = OpenCodeAsyncClient(config=config)
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize SDK client: {str(e)}",
        )


async def execute_agent_background(task_id: str, agent_id: str, session_id: str, message: str, options: Optional[Dict[str, Any]]):
    """Execute agent in background and update task status.

    Args:
        task_id: The task identifier
        agent_id: The agent name to execute
        session_id: The session to execute in
        message: The user message to process
        options: Optional execution parameters
    """
    try:
        task_status[task_id] = "running"
        client = await get_sdk_client()

        result = await client.execute_agent(
            agent_name=agent_id,
            session_id=session_id,
            user_message=message,
            options=options
        )

        task_status[task_id] = "completed" if result.success else "failed"

    except Exception as e:
        task_status[task_id] = f"failed: {str(e)}"


@router.post(
    "/{agent_id}/execute",
    response_model=ExecuteAgentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute an agent",
    description="Execute an agent asynchronously for a given message. Returns a task_id immediately."
)
async def execute_agent(
    agent_id: str,
    request: ExecuteAgentRequest = Body(...),
) -> ExecuteAgentResponse:
    """Execute an agent asynchronously for a user message.

    This endpoint accepts a message and agent ID, and immediately returns a task_id
    indicating the agent execution has started. The actual agent execution happens
    in the background, so this response is returned before agent completion.

    Args:
        agent_id: The name of the agent to execute (e.g., "build", "plan", "explore")
        request: ExecuteAgentRequest containing the message and optional options.

    Returns:
        ExecuteAgentResponse with task_id and initial status.

    Raises:
        HTTPException: If message is invalid (422) or agent initialization fails (500).
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message is required and cannot be empty or whitespace-only",
        )

    try:
        task_id = f"task_{uuid.uuid4().hex}"

        client = await get_sdk_client()
        session = await client.create_session(title=request.message[:50])

        task = asyncio.create_task(
            execute_agent_background(
                task_id=task_id,
                agent_id=agent_id,
                session_id=session.id,
                message=request.message,
                options=request.options
            )
        )

        _background_tasks[task_id] = task

        return ExecuteAgentResponse(
            task_id=task_id,
            status="started",
            message=f"Agent '{agent_id}' execution started for session {session.id}",
            session_id=session.id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start agent execution: {str(e)}",
        )
