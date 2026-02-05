"""Pytest configuration and fixtures for backend tests."""
import sys
from pathlib import Path

# Add opencode_python to Python path for SDK imports (absolute path for reliable imports)
sys.path.insert(0, "/Users/parkersligting/develop/pt/agentic_coding/.worktrees/webapp/opencode_python/src")

import asyncio
import os
import shutil
from datetime import datetime
from typing import AsyncGenerator, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app
from opencode_python.sdk import OpenCodeAsyncClient
from opencode_python.core.models import Session

# Singleton storage directory for tests
_test_storage_dir = None

_test_sessions: dict[str, Session] = {}


@pytest.fixture
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Create an instance of the default event loop for the test session.

    This fixture is required for pytest-asyncio to work correctly with async FastAPI tests.

    Yields:
        asyncio.AbstractEventLoop: The event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for FastAPI application.

    This fixture provides a TestClient instance that can make HTTP requests
    to the FastAPI application without starting a server.

    Returns:
        TestClient: A test client instance.
    """
    return TestClient(app)


@pytest.fixture
async def test_session(client: TestClient) -> str:
    """Create a test session for message endpoint tests.

    This fixture sets up a test session that can be used by tests
    for adding and listing messages.

    Returns:
        str: The created session ID.
    """
    response = client.post("/api/v1/sessions", json={"title": "Test Session"})
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
async def test_session_with_messages(client: TestClient) -> str:
    """Create a test session with sample messages.

    This fixture sets up a test session with multiple messages
    for testing list functionality.

    Returns:
        str: The created session ID.
    """
    create_response = client.post("/api/v1/sessions", json={"title": "Test Session with Messages"})
    assert create_response.status_code == 200
    session_id = create_response.json()["id"]

    first_message = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"role": "user", "content": "Hello, this is a test message"},
    )
    assert first_message.status_code == 201

    second_message = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"role": "assistant", "content": "Hello! How can I help you?"},
    )
    assert second_message.status_code == 201

    return session_id


@pytest.fixture
async def clean_storage():
    """Clean up test storage directory.

    This fixture clears the test storage directory before and after tests.
    """
    global _test_storage_dir
    import tempfile

    # Set up test storage directory
    _test_storage_dir = os.path.join(tempfile.gettempdir(), "test_sessions")

    # Clean up directory if it exists
    storage_path = Path(_test_storage_dir)
    if storage_path.exists():
        import shutil
        shutil.rmtree(storage_path)

    yield

    # Clean up after tests
    if storage_path.exists():
        shutil.rmtree(storage_path)


@pytest.fixture
def mock_sdk_client():
    """Mock SDK client with in-memory session storage for tests.

    This fixture provides a mock SDK client that stores sessions in memory,
    avoiding the storage persistence issues with the real SDK.

    Yields:
        MagicMock: Mocked OpenCodeAsyncClient.
    """
    global _test_sessions
    _test_sessions.clear()

    async def mock_create_session(title: str, version: str = "1.0.0") -> Session:
        import uuid

        session = Session(
            id=str(uuid.uuid4()),
            slug=title.lower().replace(" ", "-"),
            project_id="test-project",
            directory="/test",
            title=title,
            version=version,
            theme_id="aurora",
            time_created=datetime.now().timestamp(),
            time_updated=datetime.now().timestamp(),
        )
        _test_sessions[session.id] = session
        return session

    async def mock_get_session(session_id: str) -> Optional[Session]:
        return _test_sessions.get(session_id)

    async def mock_delete_session(session_id: str) -> bool:
        if session_id in _test_sessions:
            del _test_sessions[session_id]
            return True
        return False

    async def mock_list_sessions() -> list[Session]:
        return list(_test_sessions.values())

    async def mock_update_session(session_id: str, **kwargs) -> Session:
        if session_id in _test_sessions:
            session = _test_sessions[session_id]
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.time_updated = datetime.now().timestamp()
            return session
        raise ValueError(f"Session not found: {session_id}")

    mock_client = AsyncMock(spec=OpenCodeAsyncClient)
    mock_client.create_session = mock_create_session
    mock_client.get_session = mock_get_session
    mock_client.delete_session = mock_delete_session
    mock_client.list_sessions = mock_list_sessions
    mock_client.update_session = mock_update_session

    yield mock_client

    _test_sessions.clear()
