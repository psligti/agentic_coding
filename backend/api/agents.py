"""Agent execution endpoints for WebApp API."""

import asyncio
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel

from api.sessions import get_sdk_client


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


_background_tasks: Dict[str, asyncio.Task] = {}
task_status: Dict[str, str] = {}


router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("", response_model=list[Dict[str, Any]])
async def list_agents() -> list[Dict[str, Any]]:
    """List all available agents.

    Returns:
        List of agent summaries with metadata.
    """
    try:
        from opencode_python.agents.builtin import get_all_agents

        agents = get_all_agents()
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "mode": agent.mode,
                "native": agent.native,
                "hidden": agent.hidden,
                "model": agent.model,
                "permission": agent.permission,
            }
            for agent in agents
            if not agent.hidden
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}",
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
            options=options or {}
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
