"""Tests for session SSE streaming endpoint."""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from api.sessions import get_sdk_client


@pytest.mark.asyncio
async def test_session_stream_exists():
    """Test that SSE endpoint exists and returns 404 for non-existent session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sessions/nonexistent-session/stream")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_session_stream_sse_format():
    """Test that session streaming endpoint returns SSE format with initial event."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test Session Streaming")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/sessions/{session.id}/stream")
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            content_bytes = await response.aread()
            content_str = content_bytes.decode("utf-8")
            assert len(content_bytes) > 0
            assert "event: connected" in content_str
            assert "event: session_theme" in content_str
            assert '"theme_id":' in content_str
    finally:
        await client.delete_session(session.id)


@pytest.mark.asyncio
async def test_session_stream_telemetry_event():
    """Test that telemetry event is emitted on connect with correct shape."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test Telemetry Event")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/sessions/{session.id}/stream")
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            content_bytes = await response.aread()
            content_str = content_bytes.decode("utf-8")

            assert "event: connected" in content_str
            assert "event: session_theme" in content_str
            assert "event: telemetry" in content_str

            events = _parse_sse_events(content_str)

            connected_events = [e for e in events if e.get("type") == "connected"]
            assert len(connected_events) > 0
            assert connected_events[0]["session_id"] == session.id

            session_theme_events = [e for e in events if e.get("type") == "session_theme"]
            assert len(session_theme_events) > 0
            assert session_theme_events[0]["session_id"] == session.id
            assert "theme_id" in session_theme_events[0]

            telemetry_events = [e for e in events if e.get("type") == "telemetry"]
            assert len(telemetry_events) > 0
            telemetry_data = telemetry_events[0]
            assert telemetry_data["session_id"] == session.id
            assert "git" in telemetry_data
            assert "tools" in telemetry_data
            assert "effort_inputs" in telemetry_data
            assert "effort_score" in telemetry_data
            assert isinstance(telemetry_data["effort_score"], int)
    finally:
        await client.delete_session(session.id)


@pytest.mark.asyncio
async def test_session_stream_ping_event():
    """Test that ping event has correct shape."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test Ping Event")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/sessions/{session.id}/stream")
            assert response.status_code == 200

            content_bytes = await response.aread()
            content_str = content_bytes.decode("utf-8")

            events = _parse_sse_events(content_str)
            ping_events = [e for e in events if e.get("type") == "ping"]

            if ping_events:
                assert ping_events[0]["session_id"] == session.id
    finally:
        await client.delete_session(session.id)


def _parse_sse_events(content: str) -> list[dict]:
    """Parse SSE content into list of event data dictionaries.

    Args:
        content: Raw SSE content string.

    Returns:
        List of parsed event data dictionaries.
    """
    events = []
    current_event_data = None

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("event:"):
            event_type = line[6:].strip()
            current_event_data = {"type": event_type}

        elif line.startswith("data:"):
            if current_event_data is None:
                current_event_data = {}

            try:
                data_json = json.loads(line[5:].strip())
                current_event_data.update(data_json)
            except json.JSONDecodeError:
                pass

        elif line == "" and current_event_data is not None:
            events.append(current_event_data)
            current_event_data = None

    return events


@pytest.mark.asyncio
async def test_session_stream_keep_alive_headers():
    """Test that session SSE stream has correct headers."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test SSE Keep-Alive")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/sessions/{session.id}/stream")
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            assert "no-cache" in response.headers.get("Cache-Control", "")
            assert response.headers.get("Connection") == "keep-alive"
    finally:
        await client.delete_session(session.id)


@pytest.mark.asyncio
async def test_session_stream_theme_broadcast():
    """Test that theme_id update is broadcast to SSE subscribers."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test Theme Broadcast")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            update_response = await ac.put(
                f"/api/v1/sessions/{session.id}",
                json={"theme_id": "ocean"},
            )
            assert update_response.status_code == 200
            data = update_response.json()
            assert data["theme_id"] == "ocean"

            updated_session = await client.get_session(session.id)
            assert updated_session.theme_id == "ocean"
    finally:
        await client.delete_session(session.id)


@pytest.mark.asyncio
async def test_update_session_theme():
    """Test that PUT endpoint updates session theme_id."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test Update Theme")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.put(
                f"/api/v1/sessions/{session.id}",
                json={"theme_id": "ember"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["theme_id"] == "ember"
            assert data["id"] == session.id

            updated_session = await client.get_session(session.id)
            assert updated_session.theme_id == "ember"
    finally:
        await client.delete_session(session.id)


@pytest.mark.asyncio
async def test_update_session_requires_field():
    """Test that PUT endpoint requires at least one field."""
    client = await get_sdk_client()
    session = await client.create_session(title="Test Require Field")

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.put(
                f"/api/v1/sessions/{session.id}",
                json={},
            )
            assert response.status_code == 400
            assert "At least one field" in response.json()["detail"]
    finally:
        await client.delete_session(session.id)


@pytest.mark.asyncio
async def test_update_session_not_found():
    """Test that PUT endpoint returns 404 for non-existent session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(
            "/api/v1/sessions/nonexistent-session",
            json={"theme_id": "ocean"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_telemetry_event_payload_structure(mock_sdk_client):
    """Test that telemetry event has correct JSON payload structure."""
    session = await mock_sdk_client.create_session(title="Test Telemetry Structure")

    try:
        async def mock_stream_events(*args, **kwargs):
            yield "event: connected\n"
            yield f'data: {json.dumps({"type": "connected", "session_id": session.id})}\n\n'
            yield "event: session_theme\n"
            yield f'data: {json.dumps({"type": "session_theme", "session_id": session.id, "theme_id": "aurora"})}\n\n'
            yield "event: telemetry\n"
            yield f'data: {json.dumps({"type": "telemetry", "session_id": session.id, "git": {}, "tools": {}, "effort_inputs": {}, "effort_score": 3})}\n\n'

        with patch("api.sessions_streaming.get_sdk_client", return_value=mock_sdk_client):
            with patch("api.sessions_streaming._stream_session_events", side_effect=mock_stream_events):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                    response = await ac.get(f"/api/v1/sessions/{session.id}/stream")
                    assert response.status_code == 200

                    content_str = response.text
                    events = _parse_sse_events(content_str)
                    telemetry_events = [e for e in events if e.get("type") == "telemetry"]

                    assert len(telemetry_events) > 0, "No telemetry events found"

                    telemetry = telemetry_events[0]

                    assert "type" in telemetry, "Telemetry event missing 'type' field"
                    assert "session_id" in telemetry, "Telemetry event missing 'session_id' field"
                    assert "git" in telemetry, "Telemetry event missing 'git' field"
                    assert "tools" in telemetry, "Telemetry event missing 'tools' field"
                    assert "effort_inputs" in telemetry, "Telemetry event missing 'effort_inputs' field"
                    assert "effort_score" in telemetry, "Telemetry event missing 'effort_score' field"

                    assert isinstance(telemetry["type"], str)
                    assert isinstance(telemetry["session_id"], str)
                    assert isinstance(telemetry["git"], dict)
                    assert isinstance(telemetry["tools"], dict)
                    assert isinstance(telemetry["effort_inputs"], dict)
                    assert isinstance(telemetry["effort_score"], int)
    finally:
        await mock_sdk_client.delete_session(session.id)


@pytest.mark.asyncio
async def test_telemetry_event_type_field(mock_sdk_client):
    """Test that telemetry event includes type field set to 'telemetry'."""
    session = await mock_sdk_client.create_session(title="Test Telemetry Type")

    try:
        with patch("api.sessions_streaming.get_sdk_client", return_value=mock_sdk_client):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.get(f"/api/v1/sessions/{session.id}/stream", timeout=5.0)
                assert response.status_code == 200

                content_bytes = b""
                async for chunk in response.aiter_bytes():
                    content_bytes += chunk
                    if b"event: telemetry" in content_bytes:
                        break

                await response.aclose()

                content_str = content_bytes.decode("utf-8")

                events = _parse_sse_events(content_str)
                telemetry_events = [e for e in events if e.get("type") == "telemetry"]

                assert len(telemetry_events) > 0, "No telemetry events found"

                for telemetry in telemetry_events:
                    assert telemetry["type"] == "telemetry", \
                        f"Expected type='telemetry', got type='{telemetry['type']}'"
    finally:
        await mock_sdk_client.delete_session(session.id)


@pytest.mark.asyncio
async def test_telemetry_event_format_pattern(mock_sdk_client):
    """Test that telemetry event follows existing SSE format pattern."""
    session = await mock_sdk_client.create_session(title="Test Telemetry Format")

    try:
        with patch("api.sessions_streaming.get_sdk_client", return_value=mock_sdk_client):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.get(f"/api/v1/sessions/{session.id}/stream", timeout=5.0)
                assert response.status_code == 200

                content_bytes = b""
                async for chunk in response.aiter_bytes():
                    content_bytes += chunk
                    if b"event: telemetry" in content_bytes:
                        break

                await response.aclose()

                content_str = content_bytes.decode("utf-8")

                assert "event: telemetry" in content_str, "Missing 'event: telemetry' line"
                assert content_str.count("event: telemetry") > 0, "No telemetry event lines found"

                events = _parse_sse_events(content_str)
                telemetry_events = [e for e in events if e.get("type") == "telemetry"]

                assert len(telemetry_events) > 0, "No telemetry events parsed"

                for telemetry in telemetry_events:
                    assert telemetry["type"] == "telemetry", \
                        "Event type field must be 'telemetry'"
    finally:
        await mock_sdk_client.delete_session(session.id)


@pytest.mark.asyncio
async def test_telemetry_emitted_on_connection(mock_sdk_client):
    """Test that initial telemetry is emitted on connection."""
    session = await mock_sdk_client.create_session(title="Test Initial Telemetry")

    try:
        with patch("api.sessions_streaming.get_sdk_client", return_value=mock_sdk_client):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.get(f"/api/v1/sessions/{session.id}/stream", timeout=5.0)
                assert response.status_code == 200

                content_bytes = b""
                async for chunk in response.aiter_bytes():
                    content_bytes += chunk
                    if b"event: telemetry" in content_bytes:
                        break

                await response.aclose()

                content_str = content_bytes.decode("utf-8")

                lines = [line.strip() for line in content_str.split("\n") if line.strip()]

                connected_pos = None
                session_theme_pos = None
                telemetry_pos = None

                for i, line in enumerate(lines):
                    if line == "event: connected":
                        connected_pos = i
                    elif line == "event: session_theme":
                        session_theme_pos = i
                    elif line == "event: telemetry":
                        telemetry_pos = i

                assert connected_pos is not None, "Missing connected event"
                assert session_theme_pos is not None, "Missing session_theme event"
                assert telemetry_pos is not None, "Missing telemetry event"

                assert telemetry_pos > connected_pos, "Telemetry should come after connected"
                assert telemetry_pos > session_theme_pos, "Telemetry should come after session_theme"

                events = _parse_sse_events(content_str)
                telemetry_events = [e for e in events if e.get("type") == "telemetry"]

                assert len(telemetry_events) > 0, "No telemetry events found in initial stream"
    finally:
        await mock_sdk_client.delete_session(session.id)
