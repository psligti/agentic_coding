"""SSE (Server-Sent Events) streaming endpoint for task execution."""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Optional, Set

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from api.sessions import get_sdk_client


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


# Global storage for active stream tasks
_active_streams: dict[str, asyncio.Task[None]] = {}

# Global storage for task subscribers
_task_subscribers: dict[str, Set[asyncio.Queue[str]]] = {}


async def _notify_agent_started(task_id: str, agent_name: str) -> None:
    if task_id not in _task_subscribers:
        return

    event_data = json.dumps({
        "type": "start",
        "task_id": task_id,
        "agent_name": agent_name,
    })

    for queue in _task_subscribers[task_id]:
        try:
            await queue.put(event_data)
        except Exception:
            pass


async def _notify_agent_finished(task_id: str, agent_name: str, duration: float) -> None:
    if task_id not in _task_subscribers:
        return

    event_data = json.dumps({
        "type": "finish",
        "task_id": task_id,
        "agent_name": agent_name,
        "duration": duration,
    })

    for queue in _task_subscribers[task_id]:
        try:
            await queue.put(event_data)
        except Exception:
            pass


async def _notify_agent_error(task_id: str, agent_name: str, error: str) -> None:
    if task_id not in _task_subscribers:
        return

    event_data = json.dumps({
        "type": "error",
        "task_id": task_id,
        "agent_name": agent_name,
        "message": error,
    })

    for queue in _task_subscribers[task_id]:
        try:
            await queue.put(event_data)
        except Exception:
            pass


async def stream_task_events(task_id: str, request: Request) -> AsyncGenerator[str, None]:
    """Generate SSE events for a task execution.

    Args:
        task_id: The task/session ID to stream events for.
        request: The FastAPI request object for cancellation detection.

    Yields:
        str: SSE-formatted event strings.
    """
    client = await get_sdk_client()

    # Verify session exists and get messages
    session = None
    messages_list: list[Any] = []
    queue: Optional[asyncio.Queue[str]] = None

    try:
        session = await client.get_session(task_id)
        if session is None:
            return

        if hasattr(client, 'get_messages'):
            try:
                messages = await client.get_messages(task_id)
                messages_list = messages.messages if messages else []
            except Exception:
                messages_list = []
        else:
            messages_list = []

        queue = asyncio.Queue[str]()
        if task_id not in _task_subscribers:
            _task_subscribers[task_id] = set()
        _task_subscribers[task_id].add(queue)

        yield f"event: connected\n"
        yield f"data: {json.dumps({'type': 'connected', 'task_id': task_id, 'message_count': len(messages_list)})}\n\n"

    except Exception as e:
        error_msg = str(e)
        yield f"event: error\n"
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        return

    try:
        for i, msg in enumerate(messages_list):
            yield f"event: message\n"
            yield f"data: {json.dumps({'type': 'message', 'index': i, 'role': msg.role, 'content': msg.content})}\n\n"
            await asyncio.sleep(0.1)

        while True:
            if task_id in _task_subscribers and queue is not None:
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=0.5)
                    yield event_data + "\n"
                except asyncio.TimeoutError:
                    pass

            if await request.is_disconnected():
                yield f"event: disconnect\n"
                yield f"data: {json.dumps({'type': 'disconnect', 'task_id': task_id})}\n\n"
                break

            current_time = time.time()
            if current_time % 25 < 1:
                yield ": keep-alive\n\n"

            await asyncio.sleep(1)
    finally:
        if queue is not None and task_id in _task_subscribers:
            _task_subscribers[task_id].discard(queue)
            if not _task_subscribers[task_id]:
                del _task_subscribers[task_id]


@router.get("/{task_id}/stream")
async def stream_task_events_endpoint(task_id: str, request: Request) -> StreamingResponse:
    """Stream task execution events as Server-Sent Events (SSE).

    This endpoint provides real-time updates for a task session using
    Server-Sent Events (SSE), which is a unidirectional server-to-client
    streaming protocol.

    Args:
        task_id: The task/session ID to stream events for.
        request: The FastAPI request object for handling disconnects.

    Returns:
        StreamingResponse: Server-Sent Events stream with real-time updates.

    SSE Format:
        - event: connected
          data: {"type": "connected", "task_id": "...", "message_count": N}

        - event: message
          data: {"type": "message", "index": N, "role": "user|assistant", "content": "..."}

        - event: disconnect
          data: {"type": "disconnect", "task_id": "..."}

        - event: error
          data: {"type": "error", "message": "..."}

        - comment: : keep-alive

    Raises:
        HTTPException: 404 if task_id not found, 500 if streaming fails.
    """
    try:
        # Check if already streaming
        if task_id in _active_streams:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Task {task_id} is already being streamed",
            )

        # Verify session exists before creating generator
        client = await get_sdk_client()
        session = await client.get_session(task_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}",
            )

        # Define async generator inline
        async def _stream_generator() -> AsyncGenerator[str, None]:
            async for event in stream_task_events(task_id, request):
                yield event

        # Create generator instance
        gen = _stream_generator()

        # Return StreamingResponse with generator
        return StreamingResponse(
            gen,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start streaming: {str(e)}",
        )
