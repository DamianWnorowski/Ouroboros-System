"""
Unit tests for validation module
"""

import pytest
from pydantic import ValidationError
from typing import Dict, List, Any, Optional

from core.validation import (
    VerifyRequest, AgentCreateRequest, AgentUpdateRequest,
    PaginationParams, FilterParams, ErrorResponse
)


class TestVerifyRequest:
    """Test VerifyRequest validation"""

    def test_verify_request_valid(self):
        """Test valid VerifyRequest"""
        request = VerifyRequest(level=3, path="some/path", export_json=True)
        assert request.level == 3
        assert request.path == "some/path"
        assert request.export_json is True

    def test_verify_request_defaults(self):
        """Test VerifyRequest with defaults"""
        request = VerifyRequest()
        assert request.level == 6  # Default level
        assert request.path is None  # Default path (no default set)
        assert request.export_json is False  # Default export

    def test_verify_request_level_validation(self):
        """Test level validation"""
        # Valid levels
        for level in [0, 1, 2, 3, 4, 5, 6]:
            request = VerifyRequest(level=level)
            assert request.level == level

        # Invalid levels should raise ValidationError
        with pytest.raises(ValidationError):
            VerifyRequest(level=-1)

        with pytest.raises(ValidationError):
            VerifyRequest(level=7)

        with pytest.raises(ValidationError):
            VerifyRequest(level=10)

    def test_verify_request_path_validation(self):
        """Test path validation"""
        # Valid paths (no absolute paths or path traversal)
        valid_paths = [".", "relative/path", "src/code", "tests/unit"]
        for path in valid_paths:
            request = VerifyRequest(path=path)
            assert request.path == path

        # Path traversal attempts should be blocked
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\windows\\system32\\config\\sam",
            "../parent",
            "/"
        ]

        for path in malicious_paths:
            with pytest.raises(ValidationError):
                VerifyRequest(path=path)

    @pytest.mark.parametrize("level,path,export_json", [
        (0, ".", False),
        (3, "app", True),
        (6, "src", False),
        (1, None, True),  # None path should work
    ])
    def test_verify_request_parametrized(self, level, path, export_json):
        """Test VerifyRequest with various parameters"""
        request = VerifyRequest(level=level, path=path, export_json=export_json)

        assert request.level == level
        assert request.path == path  # Should match exactly what was passed
        assert request.export_json == export_json


class TestAgentRequests:
    """Test agent-related request validation"""

    def test_agent_create_request_valid(self):
        """Test valid AgentCreateRequest"""
        request = AgentCreateRequest(
            name="Test Agent",
            capabilities=["test", "demo"],
            dependencies=["base"],
            auto_heal=False
        )
        assert request.name == "Test Agent"
        assert request.capabilities == ["test", "demo"]
        assert request.dependencies == ["base"]
        assert request.auto_heal is False

    def test_agent_create_request_defaults(self):
        """Test AgentCreateRequest defaults"""
        request = AgentCreateRequest(name="Test Agent")
        assert request.name == "Test Agent"
        assert request.capabilities == []
        assert request.dependencies == []
        assert request.auto_heal is True  # Default value

    def test_agent_create_request_validation(self):
        """Test AgentCreateRequest validation"""
        # Test name length validation
        request = AgentCreateRequest(name="Valid Name")
        assert request.name == "Valid Name"

        # Name too short
        with pytest.raises(ValidationError):
            AgentCreateRequest(name="")  # Empty name

        # Name too long
        with pytest.raises(ValidationError):
            AgentCreateRequest(name="a" * 101)  # Too long

    def test_agent_update_request(self):
        """Test AgentUpdateRequest"""
        request = AgentUpdateRequest(
            name="Updated Agent",
            capabilities=["new", "caps"],
            auto_heal=False
        )
        assert request.name == "Updated Agent"
        assert request.capabilities == ["new", "caps"]
        assert request.auto_heal is False

    def test_agent_update_request_optional(self):
        """Test AgentUpdateRequest with optional fields"""
        # All fields optional
        request = AgentUpdateRequest()
        assert request.name is None
        assert request.capabilities is None
        assert request.auto_heal is None

        # Partial update
        request = AgentUpdateRequest(name="New Name")
        assert request.name == "New Name"
        assert request.capabilities is None


class TestPaginationParams:
    """Test pagination parameters"""

    def test_pagination_params_valid(self):
        """Test valid PaginationParams"""
        params = PaginationParams(page=2, page_size=50)
        assert params.page == 2
        assert params.page_size == 50

    def test_pagination_params_defaults(self):
        """Test PaginationParams defaults"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_pagination_params_validation(self):
        """Test pagination validation"""
        # Valid page numbers
        for page in [1, 2, 100, 1000]:
            params = PaginationParams(page=page)
            assert params.page == page

        # Invalid page numbers
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

        with pytest.raises(ValidationError):
            PaginationParams(page=-1)

        # Valid page sizes
        for page_size in [10, 20, 50, 100]:
            params = PaginationParams(page_size=page_size)
            assert params.page_size == page_size

        # Invalid page sizes
        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)

        with pytest.raises(ValidationError):
            PaginationParams(page_size=101)

        with pytest.raises(ValidationError):
            PaginationParams(page_size=1000)

        # Test offset and limit properties
        params = PaginationParams(page=2, page_size=25)
        assert params.offset == 25  # (2-1) * 25
        assert params.limit == 25


class TestFilterParams:
    """Test filter parameters"""

    def test_filter_params_valid(self):
        """Test valid FilterParams"""
        params = FilterParams(
            status="active",
            capability="test",
            search="agent"
        )
        assert params.status == "active"
        assert params.capability == "test"
        assert params.search == "agent"

    def test_filter_params_defaults(self):
        """Test FilterParams defaults"""
        params = FilterParams()
        assert params.status is None
        assert params.capability is None
        assert params.search is None

    def test_filter_params_validation(self):
        """Test filter validation"""
        # Valid search lengths
        params = FilterParams(search="short search")
        assert params.search == "short search"

        # Search too long
        with pytest.raises(ValidationError):
            FilterParams(search="a" * 101)  # Over max_length


class TestErrorResponse:
    """Test error response model"""

    def test_error_response_creation(self):
        """Test creating ErrorResponse"""
        error = ErrorResponse(
            error="Validation Error",
            code="VALIDATION_ERROR",
            details={"field": "level", "value": -1}
        )
        assert error.error == "Validation Error"
        assert error.code == "VALIDATION_ERROR"
        assert error.details == {"field": "level", "value": -1}

    def test_error_response_defaults(self):
        """Test ErrorResponse defaults"""
        error = ErrorResponse(error="Test error")
        assert error.error == "Test error"
        assert error.code is None  # No default value set
        assert error.details is None


class TestPathValidation:
    """Test path validation functionality"""

    def test_path_validation_none_allowed(self):
        """Test that None paths are allowed"""
        request = VerifyRequest(path=None)
        assert request.path is None

    def test_path_validation_relative_allowed(self):
        """Test that relative paths are allowed"""
        valid_paths = ["src", "tests/unit", "path/to/file", "file.txt"]
        for path in valid_paths:
            request = VerifyRequest(path=path)
            assert request.path == path

    def test_path_validation_absolute_blocked(self):
        """Test that absolute paths are blocked"""
        # This depends on OS - on Windows, C: is absolute
        import os
        if os.name == 'nt':  # Windows
            with pytest.raises(ValidationError):
                VerifyRequest(path="C:\\windows\\system32")
        else:  # Unix-like
            with pytest.raises(ValidationError):
                VerifyRequest(path="/etc/passwd")


class TestIntegrationValidation:
    """Test validation integration scenarios"""

    def test_full_request_validation_flow(self):
        """Test complete request validation flow"""
        # Simulate a full API request validation
        try:
            verify_req = VerifyRequest(level=2, path="src/", export_json=False)
            pagination = PaginationParams(page=1, size=20)
            filters = FilterParams(status="active", capabilities=["test"])

            # All should validate successfully
            assert verify_req.level == 2
            assert pagination.page == 1
            assert filters.status == "active"

        except ValidationError:
            pytest.fail("Valid request should not raise ValidationError")

    def test_validation_error_handling(self):
        """Test proper error handling for validation failures"""
        with pytest.raises(ValidationError) as exc_info:
            VerifyRequest(level=10)  # Invalid level

        error = exc_info.value
        assert len(error.errors()) > 0

        # Should have details about the validation failure
        error_details = error.errors()[0]
        assert "level" in str(error_details)

    def test_nested_validation(self):
        """Test validation of nested structures"""
        # Test with nested capabilities and dependencies
        capabilities = ["web", "api", "database"]
        dependencies = ["auth", "validation"]

        request = AgentCreateRequest(
            name="Test Agent",
            capabilities=capabilities,
            dependencies=dependencies
        )

        assert request.capabilities == capabilities
        assert request.dependencies == dependencies
        assert len(request.capabilities) == 3

    def test_validation_performance(self):
        """Test that validation doesn't have performance issues"""
        import time

        start_time = time.time()

        # Create many validation instances
        for i in range(100):
            req = VerifyRequest(level=i % 7, path=f"path_{i}")
            assert req.level >= 0 and req.level <= 6

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly (less than 1 second for 100 validations)
        assert duration < 1.0
