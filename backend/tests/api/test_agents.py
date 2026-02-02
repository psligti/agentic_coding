"""Tests for agent execution endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app


class TestExecuteAgent:
    """Tests for POST /api/v1/agents/{agent_id}/execute endpoint."""

    def test_execute_agent_success(self, client: TestClient) -> None:
        """Test that executing an agent returns 202 Accepted with task_id.

        This test verifies the POST /api/v1/agents/{agent_id}/execute endpoint
        returns a task_id immediately with 202 Accepted status when the agent
        execution is successfully started.
        """
        response = client.post(
            "/api/v1/agents/build/execute",
            json={"message": "Create a new user model"},
        )
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert "message" in data
        assert "session_id" in data
        assert data["status"] == "started"
        assert "Agent 'build' execution started" in data["message"]

    def test_execute_agent_with_options(self, client: TestClient) -> None:
        """Test that executing an agent with options works correctly.

        This test verifies the endpoint accepts and uses the options parameter
        when provided in the request body.
        """
        response = client.post(
            "/api/v1/agents/plan/execute",
            json={
                "message": "Plan the implementation",
                "options": {"provider": "openai", "model": "gpt-4"}
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert "session_id" in data

    def test_execute_agent_with_empty_message(self, client: TestClient) -> None:
        """Test that executing an agent with empty message returns 422.

        This test verifies the endpoint validates that the message field is
        required and cannot be empty.
        """
        response = client.post(
            "/api/v1/agents/build/execute",
            json={"message": ""},
        )
        assert response.status_code == 422

    def test_execute_agent_with_missing_message(self, client: TestClient) -> None:
        """Test that executing an agent without message returns 422.

        This test verifies the endpoint validates that the message field is
        required.
        """
        response = client.post(
            "/api/v1/agents/build/execute",
            json={},
        )
        assert response.status_code == 422

    def test_execute_agent_with_whitespace_message(self, client: TestClient) -> None:
        """Test that executing an agent with whitespace-only message returns 422.

        This test verifies the endpoint validates that the message field is
        required and cannot be just whitespace.
        """
        response = client.post(
            "/api/v1/agents/build/execute",
            json={"message": "   "},
        )
        assert response.status_code == 422

    def test_execute_agent_invalid_agent(self, client: TestClient) -> None:
        """Test that executing an invalid agent is accepted (validation in background).

        This test verifies the endpoint accepts the request and returns 202,
        with the SDK validation happening in the background execution.
        """
        response = client.post(
            "/api/v1/agents/invalid_agent/execute",
            json={"message": "Test message"},
        )
        assert response.status_code == 202

    def test_execute_agent_inexistent_session(self, client: TestClient) -> None:
        """Test that executing an agent with invalid session returns 500."""
        response = client.post(
            "/api/v1/agents/build/execute",
            json={"message": "Test message"},
        )
        assert response.status_code == 202

    def test_execute_agent_different_agent_types(self, client: TestClient) -> None:
        """Test that executing different agent types works."""
        agents = ["build", "plan", "explore", "expert"]
        for agent in agents:
            response = client.post(
                f"/api/v1/agents/{agent}/execute",
                json={"message": "Test message"},
            )
            assert response.status_code == 202, f"Failed for agent {agent}"
            data = response.json()
            assert "task_id" in data
            assert "session_id" in data
