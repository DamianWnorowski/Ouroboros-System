"""
Ouroboros System - Authentication & Authorization
JWT-based authentication with rate limiting
"""

import os
import time
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, List
from functools import wraps
from collections import defaultdict

try:
    import jwt
    from jwt import PyJWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# Rate limiting storage (in-memory, use Redis in production)
_rate_limit_store: Dict[str, List[float]] = defaultdict(list)
_rate_limit_lock = {}  # Simple lock per IP


class AuthenticationError(HTTPException):
    """Authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """Authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class RateLimitError(HTTPException):
    """Rate limit exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET', 'change-me-in-production-min-32-chars')
        self.algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        self.token_expiration = int(os.getenv('JWT_EXPIRATION', '3600'))
        
        if len(self.secret_key) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT is required for authentication")
    
    def create_token(self, user_id: str, roles: List[str] = None) -> str:
        """Create JWT token"""
        if roles is None:
            roles = ['user']
        
        payload = {
            'user_id': user_id,
            'roles': roles,
            'exp': datetime.now(UTC) + timedelta(seconds=self.token_expiration),
            'iat': datetime.now(UTC)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except PyJWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, window: int = 60) -> bool:
        """Check if rate limit is exceeded"""
        now = time.time()
        window_start = now - window
        
        # Clean old entries
        if identifier in _rate_limit_store:
            _rate_limit_store[identifier] = [
                req_time for req_time in _rate_limit_store[identifier]
                if req_time > window_start
            ]
        
        # Check limit
        if len(_rate_limit_store[identifier]) >= max_requests:
            return False
        
        # Add current request
        _rate_limit_store[identifier].append(now)
        return True


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create auth manager"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# FastAPI security scheme
security = HTTPBearer(auto_error=False)


def require_auth(roles: List[str] = None):
    """Decorator to require authentication"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or (args[0] if args else None)
            if not isinstance(request, Request):
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Get token from header
            credentials: HTTPAuthorizationCredentials = await security(request)
            if not credentials:
                raise AuthenticationError("Missing authentication token")
            
            # Verify token
            auth_manager = get_auth_manager()
            payload = auth_manager.verify_token(credentials.credentials)
            
            # Check roles
            if roles:
                user_roles = payload.get('roles', [])
                if not any(role in user_roles for role in roles):
                    raise AuthorizationError(f"Required roles: {roles}")
            
            # Add user info to request
            request.state.user = payload
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or (args[0] if args else None)
            if not isinstance(request, Request):
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Get client identifier
            client_ip = request.client.host if request.client else "unknown"
            identifier = f"{client_ip}:{request.url.path}"
            
            # Check rate limit
            auth_manager = get_auth_manager()
            if not auth_manager.check_rate_limit(identifier, max_requests, window):
                raise RateLimitError(f"Rate limit exceeded: {max_requests} requests per {window} seconds")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

