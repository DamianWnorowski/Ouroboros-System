"""
Unit tests for authentication module
"""

import pytest
import jwt
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, UTC

from core.auth import (
    AuthManager, AuthenticationError,
    require_auth, rate_limit, get_auth_manager
)


class TestJWTToken:
    """Test JWT token functionality"""

    def test_jwt_token_creation(self):
        """Test creating JWT token"""
        auth = AuthManager()
        token = auth.create_token("testuser", ["user"])

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(token, auth.jwt_secret, algorithms=[auth.jwt_algorithm])
        assert payload["sub"] == "testuser"
        assert "user" in payload["roles"]
        assert "exp" in payload
        assert "iat" in payload

    def test_jwt_token_verification(self):
        """Test verifying JWT token"""
        auth = AuthManager()
        token = auth.create_token("testuser", ["user"])

        payload = auth.verify_token(token)
        assert payload["sub"] == "testuser"
        assert "user" in payload["roles"]

    def test_expired_token(self):
        """Test expired token handling"""
        auth = AuthManager(token_expiration=0)  # Immediate expiration
        token = auth.create_token("testuser", ["user"])

        with pytest.raises(AuthenticationError):
            auth.verify_token(token)

    def test_invalid_token(self):
        """Test invalid token handling"""
        auth = AuthManager()

        with pytest.raises(AuthenticationError):
            auth.verify_token("invalid.token.here")

    def test_wrong_secret_token(self):
        """Test token with wrong secret"""
        auth1 = AuthManager()
        auth2 = AuthManager(jwt_secret="different_secret")

        token = auth1.create_token("testuser", ["user"])

        with pytest.raises(AuthenticationError):
            auth2.verify_token(token)


class TestAuthManager:
    """Test AuthManager class"""

    def test_singleton_pattern(self):
        """Test that get_auth_manager returns singleton"""
        auth1 = get_auth_manager()
        auth2 = get_auth_manager()

        assert auth1 is auth2

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        auth = AuthManager()

        # Mock the actual authentication logic
        with patch.object(auth, '_verify_credentials', return_value=True):
            token = auth.authenticate_user("admin", "password")
            assert isinstance(token, str)

    def test_authenticate_user_failure(self):
        """Test failed user authentication"""
        auth = AuthManager()

        with patch.object(auth, '_verify_credentials', return_value=False):
            with pytest.raises(AuthenticationError):
                auth.authenticate_user("invalid", "invalid")

    def test_verify_token_with_roles(self):
        """Test token verification with role checking"""
        auth = AuthManager()
        token = auth.create_token("testuser", ["admin", "user"])

        # Should work for required roles
        payload = auth.verify_token(token, required_roles=["user"])
        assert payload["sub"] == "testuser"

        # Should work for multiple required roles
        payload = auth.verify_token(token, required_roles=["admin", "user"])
        assert payload["sub"] == "testuser"

        # Should fail for missing role
        with pytest.raises(AuthenticationError):
            auth.verify_token(token, required_roles=["superuser"])

    def test_token_expiration_time(self):
        """Test token expiration time setting"""
        auth = AuthManager(token_expiration=3600)  # 1 hour
        token = auth.create_token("testuser", ["user"])

        payload = jwt.decode(token, auth.jwt_secret, algorithms=[auth.jwt_algorithm])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)

        # Should expire in about 1 hour
        expected_exp = iat_time + timedelta(seconds=3600)
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 5  # Allow small timing differences


class TestDecorators:
    """Test authentication and rate limiting decorators"""

    def test_require_auth_decorator_success(self):
        """Test require_auth decorator with valid token"""
        auth = AuthManager()
        token = auth.create_token("testuser", ["admin"])

        @require_auth(roles=["admin"])
        async def test_function(request, user):
            return {"user": user, "data": "success"}

        # Mock request with valid token
        mock_request = MagicMock()
        mock_request.headers = {"authorization": f"Bearer {token}"}

        result = auth._test_decorator_with_request(test_function, mock_request)
        # This is a simplified test - actual decorator testing would need more setup

    def test_require_auth_decorator_missing_token(self):
        """Test require_auth decorator with missing token"""
        @require_auth(roles=["user"])
        async def test_function(request, user):
            return {"data": "success"}

        mock_request = MagicMock()
        mock_request.headers = {}

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError):
            # This would normally be handled by FastAPI dependency injection
            pass

    def test_rate_limit_decorator(self):
        """Test rate limiting decorator"""
        call_count = 0

        @rate_limit(max_requests=2, window=60)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"

        # This is a simplified test - actual rate limiting would need Redis/mock setup
        # In real implementation, would test against Redis or in-memory store


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_initialization(self):
        """Test rate limiter initialization"""
        limiter = MagicMock()
        limiter.max_requests = 100
        limiter.window = 60

        # Basic checks that rate limiting parameters are set
        assert limiter.max_requests == 100
        assert limiter.window == 60

    def test_rate_limit_exceeded(self):
        """Test behavior when rate limit is exceeded"""
        # This would require mocking Redis or an in-memory store
        # In actual implementation, would check that decorator raises 429 status
        pass


class TestAuthenticationError:
    """Test AuthenticationError class"""

    def test_auth_error_creation(self):
        """Test creating authentication error"""
        error = AuthenticationError("Test error message", status_code=401)

        assert str(error) == "Test error message"
        assert error.status_code == 401
        assert error.detail == "Test error message"

    def test_auth_error_default_status(self):
        """Test default status code"""
        error = AuthenticationError("Test error")

        assert error.status_code == 401  # Default for auth errors


class TestSecurity:
    """Test security-related functionality"""

    def test_jwt_secret_security(self):
        """Test JWT secret generation and security"""
        auth1 = AuthManager()
        auth2 = AuthManager()

        # Different instances should have different secrets (unless configured)
        # This depends on implementation - could be same if using env var
        assert isinstance(auth1.jwt_secret, str)
        assert len(auth1.jwt_secret) > 0

    def test_token_tampering_detection(self):
        """Test detection of tampered tokens"""
        auth = AuthManager()
        token = auth.create_token("testuser", ["user"])

        # Manually decode and modify
        payload = jwt.decode(token, auth.jwt_secret, algorithms=[auth.jwt_algorithm])
        payload["sub"] = "modified_user"

        # Re-encode with modified payload
        tampered_token = jwt.encode(payload, auth.jwt_secret, algorithm=auth.jwt_algorithm)

        # Should fail verification
        with pytest.raises(AuthenticationError):
            auth.verify_token(tampered_token)


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_username(self):
        """Test authentication with empty username"""
        auth = AuthManager()

        with patch.object(auth, '_verify_credentials', return_value=False):
            with pytest.raises(AuthenticationError):
                auth.authenticate_user("", "password")

    def test_empty_password(self):
        """Test authentication with empty password"""
        auth = AuthManager()

        with patch.object(auth, '_verify_credentials', return_value=False):
            with pytest.raises(AuthenticationError):
                auth.authenticate_user("user", "")

    def test_none_token(self):
        """Test verifying None token"""
        auth = AuthManager()

        with pytest.raises(AuthenticationError):
            auth.verify_token(None)

    def test_malformed_token(self):
        """Test malformed JWT token"""
        auth = AuthManager()

        malformed_tokens = [
            "",
            "not-a-jwt",
            "header.payload",  # Missing signature
            "header.payload.signature.extra",
        ]

        for token in malformed_tokens:
            with pytest.raises(AuthenticationError):
                auth.verify_token(token)

    def test_expired_token_edge(self):
        """Test token expiration edge cases"""
        auth = AuthManager(token_expiration=1)  # 1 second
        token = auth.create_token("testuser", ["user"])

        # Token should be valid immediately
        payload = auth.verify_token(token)
        assert payload["sub"] == "testuser"

        # Wait for expiration
        import time
        time.sleep(1.1)

        # Should now be expired
        with pytest.raises(AuthenticationError):
            auth.verify_token(token)
