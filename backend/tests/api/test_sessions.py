"""Tests for session management endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for FastAPI application.

    This fixture provides a TestClient instance that can make HTTP requests
    to the FastAPI application without starting a server.

    Returns:
        TestClient: A test client instance.
    """
    return TestClient(app)


class TestListSessions:
    """Tests for GET /api/v1/sessions endpoint."""

    def test_list_sessions_success(self, client: TestClient) -> None:
        """Test that listing sessions returns 200 OK with session data.

        This test verifies the GET /api/v1/sessions endpoint returns a successful response
        with a list of sessions when sessions exist.
        """
        response = client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "count" in data
        assert isinstance(data["sessions"], list)
        assert isinstance(data["count"], int)

    def test_list_sessions_empty(self, client: TestClient) -> None:
        """Test that listing empty sessions returns empty list.

        This test verifies the GET /api/v1/sessions endpoint returns an empty list
        when no sessions exist.
        """
        response = client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["sessions"] == []


class TestGetSession:
    """Tests for GET /api/v1/sessions/{session_id} endpoint."""

    def test_get_session_success(self, client: TestClient) -> None:
        """Test that getting a session returns 200 OK with session details.

        This test verifies the GET /api/v1/sessions/{session_id} endpoint returns
        the correct session details when a valid session ID is provided.
        """
        # First create a session
        create_response = client.post("/api/v1/sessions", json={"title": "Test Session"})
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]

        # Then get the session
        response = client.get(f"/api/v1/sessions/{session_id}")
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert "title" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_session_not_found(self, client: TestClient) -> None:
        """Test that getting a non-existent session returns 404 Not Found.

        This test verifies the GET /api/v1/sessions/{session_id} endpoint returns
        404 Not Found when the session ID doesn't exist.
        """
        response = client.get("/api/v1/sessions/non_existent_session_id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCreateSession:
    """Tests for POST /api/v1/sessions endpoint."""

    def test_create_session_success(self, client: TestClient) -> None:
        """Test that creating a session returns 201 Created with session details.

        This test verifies the POST /api/v1/sessions endpoint creates a session
        correctly and returns the session details including ID, title, and timestamps.
        """
        title = "My Test Session"
        response = client.post(
            "/api/v1/sessions",
            json={"title": title, "version": "1.0.0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == title
        assert data["version"] == "1.0.0"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_session_with_empty_title(self, client: TestClient) -> None:
        """Test that creating a session with empty title returns 400 Bad Request.

        This test verifies the POST /api/v1/sessions endpoint returns 400 when
        the title is empty or whitespace-only.
        """
        response = client.post("/api/v1/sessions", json={"title": ""})
        assert response.status_code == 400
        assert "title is required" in response.json()["detail"].lower()

    def test_create_session_with_whitespace_title(self, client: TestClient) -> None:
        """Test that creating a session with whitespace-only title returns 400.

        This test verifies the POST /api/v1/sessions endpoint returns 400 when
        the title contains only whitespace characters.
        """
        response = client.post("/api/v1/sessions", json={"title": "   "})
        assert response.status_code == 400
        assert "title is required" in response.json()["detail"].lower()

    def test_create_session_has_default_theme_id(self, client: TestClient) -> None:
        """Test that creating a session sets default theme_id='aurora'.

        This test verifies the POST /api/v1/sessions endpoint creates a session
        with the default theme_id of 'aurora' when no theme_id is provided.
        """
        title = "Theme Test Session"
        response = client.post("/api/v1/sessions", json={"title": title})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == title
        assert data["theme_id"] == "aurora"  # Verify default theme_id

    def test_create_session_custom_theme_id(self, client: TestClient) -> None:
        """Test that creating a session can set custom theme_id.

        This test verifies the POST /api/v1/sessions endpoint accepts a custom
        theme_id value when provided.
        """
        title = "Custom Theme Session"
        response = client.post(
            "/api/v1/sessions",
            json={"title": title, "theme_id": "ocean"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == title
        assert data["theme_id"] == "ocean"  # Verify custom theme_id


class TestDeleteSession:
    """Tests for DELETE /api/v1/sessions/{session_id} endpoint."""

    def test_delete_session_success(self, client: TestClient) -> None:
        """Test that deleting a session returns 200 OK with confirmation.

        This test verifies the DELETE /api/v1/sessions/{session_id} endpoint
        successfully deletes a session and returns a confirmation message.
        """
        # First create a session
        create_response = client.post("/api/v1/sessions", json={"title": "To Delete"})
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]

        # Then delete the session
        response = client.delete(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session deleted successfully"
        assert data["session_id"] == session_id

        # Verify session is actually deleted
        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, client: TestClient) -> None:
        """Test that deleting a non-existent session returns 404 Not Found.

        This test verifies the DELETE /api/v1/sessions/{session_id} endpoint returns
        404 Not Found when the session ID doesn't exist.
        """
        response = client.delete("/api/v1/sessions/non_existent_session_id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateSession:
    """Tests for PUT /api/v1/sessions/{session_id} endpoint."""

    def test_update_session_theme_id_success(self, client: TestClient) -> None:
        """Test that updating a session's theme_id returns 200 OK with updated session.

        This test verifies the PUT /api/v1/sessions/{session_id} endpoint successfully
        updates a session's theme_id and returns the updated session with the new theme_id.
        """
        # First create a session
        create_response = client.post("/api/v1/sessions", json={"title": "Test Session"})
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]

        update_response = client.put(
            f"/api/v1/sessions/{session_id}",
            json={"theme_id": "ocean"}
        )
        assert update_response.status_code == 200
        data = update_response.json()

        # Verify the response contains the updated theme_id
        assert data["id"] == session_id
        assert data["theme_id"] == "ocean"
        assert "created_at" in data
        assert "updated_at" in data

    def test_update_session_invalid_theme_id(self, client: TestClient) -> None:
        """Test that updating with an invalid theme_id returns 400 Bad Request.

        This test verifies the PUT endpoint returns 400 when theme_id is not provided.
        """
        # First create a session
        create_response = client.post("/api/v1/sessions", json={"title": "Test Session"})
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]

        # Try to update without theme_id (should fail)
        response = client.put(f"/api/v1/sessions/{session_id}", json={})
        assert response.status_code == 400
        assert "theme_id is required" in response.json()["detail"].lower()

    def test_update_session_not_found(self, client: TestClient) -> None:
        """Test that updating a non-existent session returns 404 Not Found.

        This test verifies the PUT /api/v1/sessions/{session_id} endpoint returns
        404 Not Found when the session ID doesn't exist.
        """
        response = client.put(
            "/api/v1/sessions/non_existent_session_id",
            json={"theme_id": "aurora"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
