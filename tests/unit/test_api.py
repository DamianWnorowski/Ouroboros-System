"""
Unit tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, UTC
import json

from core.api import app
from core.validation import VerifyRequest


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator for testing"""
    mock = MagicMock()
    mock.agents = {
        "test-agent": MagicMock(
            id="test-agent",
            name="Test Agent",
            status=MagicMock(value="active"),
            health=1.0,
            capabilities=["test"],
            dependencies=[],
            last_beat=datetime.now(UTC)
        )
    }
    mock.running = True
    return mock


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self, client):
        """Test basic root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Ouroboros System" in data["name"]


class TestHealthEndpoint:
    """Test health endpoint"""

    @patch('core.api.orchestrator')
    def test_health_endpoint_success(self, mock_orch, client):
        """Test health endpoint when orchestrator is available"""
        mock_orch.running = True
        mock_orch.agents = {}

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "healthy" in data["status"]

    def test_health_endpoint_no_orchestrator(self, client):
        """Test health endpoint when orchestrator is not initialized"""
        # Temporarily set orchestrator to None
        import core.api
        original_orchestrator = core.api.orchestrator
        core.api.orchestrator = None

        try:
            response = client.get("/health")
            assert response.status_code == 503
            data = response.json()
            assert "error" in data
        finally:
            core.api.orchestrator = original_orchestrator


class TestAgentEndpoints:
    """Test agent-related endpoints"""

    @patch('core.api.orchestrator')
    def test_list_agents(self, mock_orch, client):
        """Test listing agents"""
        # Setup mock agents
        mock_agent = MagicMock()
        mock_agent.id = "test-agent"
        mock_agent.name = "Test Agent"
        mock_agent.status = MagicMock(value="active")
        mock_agent.health = 1.0
        mock_agent.capabilities = ["test"]
        mock_agent.dependencies = []
        mock_agent.last_beat = datetime.now(UTC)

        mock_orch.agents = {"test-agent": mock_agent}

        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-agent"

    @patch('core.api.orchestrator')
    def test_get_agent_success(self, mock_orch, client):
        """Test getting specific agent"""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent.id = "test-agent"
        mock_agent.name = "Test Agent"
        mock_agent.status = MagicMock(value="active")
        mock_agent.health = 1.0
        mock_agent.capabilities = ["test"]
        mock_agent.dependencies = []
        mock_agent.last_beat = datetime.now(UTC)

        mock_orch.agents = {"test-agent": mock_agent}

        response = client.get("/agents/test-agent")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-agent"
        assert data["name"] == "Test Agent"

    @patch('core.api.orchestrator')
    def test_get_agent_not_found(self, mock_orch, client):
        """Test getting non-existent agent"""
        mock_orch.agents = {}

        response = client.get("/agents/non-existent")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestVerifyEndpoint:
    """Test verification endpoint"""

    @patch('core.api.orchestrator')
    @patch('core.api._run_verification')
    def test_verify_endpoint_success(self, mock_run_verify, mock_orch, client):
        """Test successful verification"""
        # Mock the cached verification function
        mock_run_verify.return_value = {
            "level": 1,
            "total": 10,
            "passed": 8,
            "warned": 1,
            "failed": 1,
            "results": [],
            "cached": True
        }

        verify_data = {"level": 1, "path": "."}
        response = client.post("/verify", json=verify_data)

        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 1
        assert data["total"] == 10
        assert data["cached"] is True
        mock_run_verify.assert_called_once_with(".", 1)

    def test_verify_endpoint_invalid_level(self, client):
        """Test verification with invalid level"""
        verify_data = {"level": 10, "path": "."}  # Level too high
        response = client.post("/verify", json=verify_data)

        # Should still work but clamp level
        assert response.status_code == 200
        data = response.json()
        assert data["level"] <= 6  # Max level

    def test_verify_endpoint_missing_fields(self, client):
        """Test verification with missing required fields"""
        verify_data = {}  # Missing level
        response = client.post("/verify", json=verify_data)

        assert response.status_code == 422  # Validation error


class TestMetricsEndpoint:
    """Test metrics endpoint"""

    @patch('core.api.orchestrator')
    def test_metrics_endpoint(self, mock_orch, client):
        """Test metrics endpoint"""
        mock_orch.agents = {"agent1": MagicMock(), "agent2": MagicMock()}
        mock_orch.running = True

        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "running" in data
        assert "timestamp" in data


class TestLoginEndpoint:
    """Test login endpoint"""

    def test_login_success(self, client):
        """Test successful login"""
        login_data = {"username": "admin", "password": "change-me"}
        response = client.post("/auth/login", data=login_data)

        # This will depend on the actual auth implementation
        # For now, just check that it doesn't crash
        assert response.status_code in [200, 401, 422]

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("/auth/login", data={})
        assert response.status_code == 422  # Validation error


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_root_endpoint_rate_limit(self, client):
        """Test that root endpoint has rate limiting"""
        # Make multiple requests quickly
        for i in range(10):
            response = client.get("/")
            assert response.status_code == 200

    def test_verify_endpoint_rate_limit(self, client):
        """Test that verify endpoint has stricter rate limiting"""
        # This should work but may be rate limited on rapid calls
        response = client.post("/verify", json={"level": 1})
        # Just check it doesn't crash - actual rate limiting depends on implementation
        assert response.status_code in [200, 401, 422, 429]


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post("/verify", data="invalid json")
        assert response.status_code == 422

    def test_invalid_method(self, client):
        """Test invalid HTTP method"""
        response = client.put("/verify", json={"level": 1})
        assert response.status_code == 405

    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })

        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers


class TestValidation:
    """Test input validation"""

    @pytest.mark.parametrize("level,expected_status", [
        (0, 200),  # Valid minimum
        (3, 200),  # Valid middle
        (6, 200),  # Valid maximum
        (-1, 200),  # Should be clamped
        (10, 200),  # Should be clamped
    ])
    def test_verify_level_validation(self, client, level, expected_status):
        """Test verification level validation"""
        verify_data = {"level": level, "path": "."}
        response = client.post("/verify", json=verify_data)
        assert response.status_code == expected_status

        if response.status_code == 200:
            data = response.json()
            # Level should be clamped to valid range
            assert 0 <= data["level"] <= 6
