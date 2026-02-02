"""Pytest configuration and fixtures for backend tests."""
import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from main import app


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
