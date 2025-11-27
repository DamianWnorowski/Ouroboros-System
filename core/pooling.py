"""
Ouroboros System - Connection Pooling
Async connection pools for Redis, PostgreSQL, Neo4j
"""

import os
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class ConnectionPoolManager:
    """Manages connection pools for all services"""
    
    def __init__(self):
        self.redis_pool: Optional[Any] = None
        self.postgres_pool: Optional[Any] = None
        self.neo4j_driver: Optional[Any] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize all connection pools"""
        if self._initialized:
            return
        
        # Initialize Redis pool
        if REDIS_AVAILABLE:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            redis_db = int(os.getenv('REDIS_DB', '0'))
            
            self.redis_pool = aioredis.ConnectionPool(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                max_connections=50,
                decode_responses=True
            )
        
        # Initialize PostgreSQL pool
        if POSTGRES_AVAILABLE:
            postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
            postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
            postgres_db = os.getenv('POSTGRES_DB', 'ouroboros')
            postgres_user = os.getenv('POSTGRES_USER', 'ouroboros')
            postgres_password = os.getenv('POSTGRES_PASSWORD', '')
            
            self.postgres_pool = await asyncpg.create_pool(
                host=postgres_host,
                port=postgres_port,
                database=postgres_db,
                user=postgres_user,
                password=postgres_password,
                min_size=5,
                max_size=20
            )
        
        # Initialize Neo4j driver
        if NEO4J_AVAILABLE:
            neo4j_host = os.getenv('NEO4J_HOST', 'localhost')
            neo4j_port = int(os.getenv('NEO4J_PORT', '7687'))
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', '')
            
            uri = f"bolt://{neo4j_host}:{neo4j_port}"
            self.neo4j_driver = AsyncGraphDatabase.driver(
                uri,
                auth=(neo4j_user, neo4j_password)
            )
        
        self._initialized = True
    
    async def close(self):
        """Close all connection pools"""
        if self.redis_pool:
            await self.redis_pool.disconnect()
        
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        
        self._initialized = False
    
    @asynccontextmanager
    async def get_redis(self):
        """Get Redis connection from pool"""
        if not REDIS_AVAILABLE or not self.redis_pool:
            raise RuntimeError("Redis not available")
        
        conn = aioredis.Redis(connection_pool=self.redis_pool)
        try:
            yield conn
        finally:
            await conn.close()
    
    @asynccontextmanager
    async def get_postgres(self):
        """Get PostgreSQL connection from pool"""
        if not POSTGRES_AVAILABLE or not self.postgres_pool:
            raise RuntimeError("PostgreSQL not available")
        
        async with self.postgres_pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def get_neo4j_session(self):
        """Get Neo4j session"""
        if not NEO4J_AVAILABLE or not self.neo4j_driver:
            raise RuntimeError("Neo4j not available")
        
        async with self.neo4j_driver.session() as session:
            yield session


# Global pool manager
_pool_manager: Optional[ConnectionPoolManager] = None


async def get_pool_manager() -> ConnectionPoolManager:
    """Get or create pool manager"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
        await _pool_manager.initialize()
    return _pool_manager

