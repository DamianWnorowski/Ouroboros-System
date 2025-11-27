"""
Ouroboros System - Caching Layer
Redis-based caching with async support
"""

import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import asyncio

try:
    from .pooling import get_pool_manager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


class CacheManager:
    """Cache manager with Redis backend"""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._pool_manager = None
    
    async def _get_pool(self):
        """Get pool manager"""
        if not self._pool_manager:
            self._pool_manager = await get_pool_manager()
        return self._pool_manager
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"ouroboros:{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not CACHE_AVAILABLE:
            return None
        
        try:
            pool_manager = await self._get_pool()
            async with pool_manager.get_redis() as redis:
                value = await redis.get(key)
                if value:
                    return json.loads(value)
        except Exception:
            return None
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not CACHE_AVAILABLE:
            return False
        
        try:
            pool_manager = await self._get_pool()
            async with pool_manager.get_redis() as redis:
                ttl = ttl or self.default_ttl
                await redis.setex(key, ttl, json.dumps(value))
                return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not CACHE_AVAILABLE:
            return False
        
        try:
            pool_manager = await self._get_pool()
            async with pool_manager.get_redis() as redis:
                await redis.delete(key)
                return True
        except Exception:
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not CACHE_AVAILABLE:
            return 0
        
        try:
            pool_manager = await self._get_pool()
            async with pool_manager.get_redis() as redis:
                keys = []
                async for key in redis.scan_iter(match=pattern):
                    keys.append(key)
                
                if keys:
                    await redis.delete(*keys)
                
                return len(keys)
        except Exception:
            return 0


# Global cache manager
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = await get_cache_manager()
            cache_key = cache_manager._make_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

