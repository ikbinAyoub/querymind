"""Schema cache using Redis."""

import hashlib
import json
from typing import Optional

import redis.asyncio as redis

from app.config import get_settings
from app.core.exceptions import CacheException
from app.models.schema import SchemaInfo

settings = get_settings()


class SchemaCache:
    """Redis-based cache for database schemas."""

    def __init__(self, redis_url: Optional[str] = None, ttl: Optional[int] = None):
        """
        Initialize schema cache.
        
        Args:
            redis_url: Redis connection URL.
            ttl: Cache TTL in seconds.
        """
        self.redis_url = redis_url or settings.redis_url
        self.ttl = ttl or settings.schema_cache_ttl
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            try:
                self._client = redis.from_url(self.redis_url)
            except Exception as e:
                raise CacheException(
                    message="Failed to connect to Redis",
                    details={"error": str(e)}
                )
        return self._client

    def _generate_key(self, host: str, port: int, database: str) -> str:
        """Generate cache key from connection details."""
        key_str = f"{host}:{port}:{database}"
        hash_str = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        return f"schema:{hash_str}"

    async def get(self, host: str, port: int, database: str) -> Optional[SchemaInfo]:
        """
        Get cached schema.
        
        Args:
            host: Database host.
            port: Database port.
            database: Database name.
            
        Returns:
            Cached SchemaInfo or None if not found.
        """
        try:
            client = await self._get_client()
            key = self._generate_key(host, port, database)
            
            data = await client.get(key)
            if data:
                schema_dict = json.loads(data)
                return SchemaInfo(**schema_dict)
            return None
        except CacheException:
            raise
        except Exception:
            # Cache miss is not critical - return None
            return None

    async def set(
        self,
        host: str,
        port: int,
        database: str,
        schema: SchemaInfo
    ) -> bool:
        """
        Cache a schema.
        
        Args:
            host: Database host.
            port: Database port.
            database: Database name.
            schema: Schema to cache.
            
        Returns:
            True if cached successfully.
        """
        try:
            client = await self._get_client()
            key = self._generate_key(host, port, database)
            
            data = schema.model_dump_json()
            await client.setex(key, self.ttl, data)
            return True
        except Exception:
            # Cache write failure is not critical
            return False

    async def invalidate(self, host: str, port: int, database: str) -> bool:
        """
        Invalidate cached schema.
        
        Args:
            host: Database host.
            port: Database port.
            database: Database name.
            
        Returns:
            True if invalidated successfully.
        """
        try:
            client = await self._get_client()
            key = self._generate_key(host, port, database)
            await client.delete(key)
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
