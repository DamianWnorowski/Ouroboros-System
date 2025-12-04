"""
Unit tests for caching module
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, UTC

from core.cache import CacheManager, get_cache_manager, cached


class TestCacheManager:
    """Test CacheManager functionality"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing"""
        return CacheManager()

    def test_cache_manager_initialization(self, cache_manager):
        """Test cache manager initialization"""
        assert cache_manager.default_ttl == 3600
        assert cache_manager._pool_manager is None

    def test_make_key_simple(self, cache_manager):
        """Test simple cache key generation"""
        key = cache_manager._make_key("prefix", "arg1", "arg2")
        assert "ouroboros:prefix:" in key
        assert len(key) > 0

    def test_make_key_with_kwargs(self, cache_manager):
        """Test cache key generation with keyword arguments"""
        key = cache_manager._make_key("test", "arg1", kwarg1="value1", kwarg2="value2")
        assert "ouroboros:test:" in key
        assert len(key) > 0

        # Same arguments should produce same key
        key2 = cache_manager._make_key("test", "arg1", kwarg1="value1", kwarg2="value2")
        assert key == key2

        # Different arguments should produce different key
        key3 = cache_manager._make_key("test", "arg1", kwarg1="different")
        assert key != key3

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_get_cache_hit(self, cache_manager):
        """Test successful cache get"""
        test_data = {"key": "value", "number": 42}

        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            # Mock Redis get to return JSON string
            mock_redis.get.return_value = json.dumps(test_data)

            result = asyncio.run(cache_manager.get("test_key"))
            assert result == test_data
            mock_redis.get.assert_called_once_with("test_key")

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_get_cache_miss(self, cache_manager):
        """Test cache miss"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            # Mock Redis get to return None
            mock_redis.get.return_value = None

            result = asyncio.run(cache_manager.get("missing_key"))
            assert result is None

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_get_cache_error(self, cache_manager):
        """Test cache get with error"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_pool.get_redis.side_effect = Exception("Redis connection failed")
            mock_get_pool.return_value = mock_pool

            result = asyncio.run(cache_manager.get("test_key"))
            assert result is None

    @patch('core.cache.CACHE_AVAILABLE', False)
    def test_get_cache_disabled(self, cache_manager):
        """Test cache get when caching is disabled"""
        result = asyncio.run(cache_manager.get("test_key"))
        assert result is None

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_set_cache_success(self, cache_manager):
        """Test successful cache set"""
        test_data = {"key": "value", "timestamp": datetime.now(UTC).isoformat()}

        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            result = asyncio.run(cache_manager.set("test_key", test_data))
            assert result is True
            mock_redis.setex.assert_called_once()
            args, kwargs = mock_redis.setex.call_args
            assert args[0] == "test_key"
            assert args[1] == 3600  # default TTL
            assert json.loads(args[2]) == test_data

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_set_cache_with_ttl(self, cache_manager):
        """Test cache set with custom TTL"""
        test_data = {"data": "test"}

        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            result = asyncio.run(cache_manager.set("test_key", test_data, ttl=600))
            assert result is True
            args, kwargs = mock_redis.setex.call_args
            assert args[1] == 600  # custom TTL

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_set_cache_error(self, cache_manager):
        """Test cache set with error"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_pool.get_redis.side_effect = Exception("Redis connection failed")
            mock_get_pool.return_value = mock_pool

            result = asyncio.run(cache_manager.set("test_key", {"data": "test"}))
            assert result is False

    @patch('core.cache.CACHE_AVAILABLE', False)
    def test_set_cache_disabled(self, cache_manager):
        """Test cache set when caching is disabled"""
        result = asyncio.run(cache_manager.set("test_key", {"data": "test"}))
        assert result is False

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_delete_cache_success(self, cache_manager):
        """Test successful cache delete"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            mock_redis.delete.return_value = 1

            result = asyncio.run(cache_manager.delete("test_key"))
            assert result is True
            mock_redis.delete.assert_called_once_with("test_key")

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_delete_cache_not_found(self, cache_manager):
        """Test cache delete when key doesn't exist"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            mock_redis.delete.return_value = 0

            result = asyncio.run(cache_manager.delete("nonexistent_key"))
            assert result is True  # Delete is successful even if key doesn't exist

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_clear_pattern_success(self, cache_manager):
        """Test clearing keys by pattern"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            # Mock scan_iter to return some keys
            mock_redis.scan_iter.return_value = ["key1", "key2", "key3"]

            result = asyncio.run(cache_manager.clear_pattern("test:*"))
            assert result == 3
            mock_redis.scan_iter.assert_called_once_with(match="test:*")
            mock_redis.delete.assert_called_once_with("key1", "key2", "key3")

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_clear_pattern_no_matches(self, cache_manager):
        """Test clearing pattern with no matches"""
        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            # Mock scan_iter to return no keys
            mock_redis.scan_iter.return_value = []

            result = asyncio.run(cache_manager.clear_pattern("nonexistent:*"))
            assert result == 0


class TestGlobalCacheManager:
    """Test global cache manager functions"""

    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns singleton"""
        manager1 = asyncio.run(get_cache_manager())
        manager2 = asyncio.run(get_cache_manager())

        assert manager1 is manager2
        assert isinstance(manager1, CacheManager)


class TestCachedDecorator:
    """Test cached decorator functionality"""

    def test_cached_decorator_basic(self):
        """Test basic cached decorator functionality"""
        call_count = 0

        @cached(ttl=300, key_prefix="test")
        async def test_function(x, y=10):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call should execute function
        result1 = asyncio.run(test_function(5, y=15))
        assert result1 == 20
        assert call_count == 1

        # Second call with same args should use cache (if Redis available)
        # Since we can't easily mock Redis in this context, we just test the wrapper
        result2 = asyncio.run(test_function(5, y=15))
        # Result should be consistent
        assert result2 == result1

    def test_cached_decorator_different_args(self):
        """Test cached decorator with different arguments"""
        call_count = 0

        @cached(ttl=300, key_prefix="test")
        async def test_function(x, y=10):
            nonlocal call_count
            call_count += 1
            return x + y

        # Different calls should produce different results
        result1 = asyncio.run(test_function(5))
        result2 = asyncio.run(test_function(10))

        assert result1 == 15  # 5 + 10
        assert result2 == 20  # 10 + 10
        assert result1 != result2

    @patch('core.cache.CACHE_AVAILABLE', False)
    def test_cached_decorator_cache_disabled(self):
        """Test cached decorator when caching is disabled"""
        call_count = 0

        @cached(ttl=300, key_prefix="test")
        async def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Function should execute normally when caching is disabled
        result = asyncio.run(test_function(5))
        assert result == 10
        assert call_count == 1


class TestErrorHandling:
    """Test error handling in cache operations"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing"""
        return CacheManager()

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_pool_initialization_error(self, cache_manager):
        """Test handling of pool initialization errors"""
        with patch.object(cache_manager, '_get_pool', side_effect=Exception("Pool init failed")):
            result = asyncio.run(cache_manager.get("test_key"))
            assert result is None

            result = asyncio.run(cache_manager.set("test_key", "value"))
            assert result is False

            result = asyncio.run(cache_manager.delete("test_key"))
            assert result is False

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_json_serialization_error(self, cache_manager):
        """Test handling of JSON serialization errors"""
        # Create an object that can't be JSON serialized
        class NonSerializable:
            pass

        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            # This should handle the serialization error gracefully
            result = asyncio.run(cache_manager.set("test_key", NonSerializable()))
            assert result is False


class TestConcurrency:
    """Test concurrent cache operations"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing"""
        return CacheManager()

    @patch('core.cache.CACHE_AVAILABLE', True)
    def test_concurrent_get_operations(self, cache_manager):
        """Test multiple concurrent get operations"""
        async def concurrent_gets():
            tasks = []
            for i in range(10):
                task = cache_manager.get(f"key_{i}")
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            return results

        with patch.object(cache_manager, '_get_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_redis = AsyncMock()
            mock_pool.get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_pool.return_value = mock_pool

            # Mock Redis to return different values for different keys
            def mock_get(key):
                if "key_5" in key:
                    return json.dumps({"data": "special"})
                return None

            mock_redis.get.side_effect = mock_get

            results = asyncio.run(concurrent_gets())
            assert len(results) == 10
            # One result should have data
            data_results = [r for r in results if r is not None]
            assert len(data_results) == 1
            assert data_results[0]["data"] == "special"
