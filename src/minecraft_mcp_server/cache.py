"""Cache management for Minecraft MCP Server."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached item with expiration.
    
    Attributes:
        data: The cached data (can be any type).
        expires_at: Datetime when this entry expires.
    """

    data: Any
    expires_at: datetime


class CacheManager:
    """Manages in-memory caching with TTL (Time To Live).
    
    This cache manager stores data in memory with automatic expiration.
    It's designed for caching HTTP responses and API data to reduce
    external requests and improve response times.
    
    Attributes:
        default_ttl: Default time-to-live in seconds for cache entries.
    """

    def __init__(self, default_ttl: int = 3600) -> None:
        """Initialize the cache manager.
        
        Args:
            default_ttl: Default TTL in seconds (default: 3600 = 1 hour).
        """
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}
        logger.debug(f"CacheManager initialized with default_ttl={default_ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached data if not expired.
        
        Args:
            key: Cache key to retrieve.
            
        Returns:
            The cached data if found and not expired, None otherwise.
        """
        if key not in self._cache:
            logger.debug(f"Cache miss: {key}")
            return None

        entry = self._cache[key]
        now = datetime.now()

        if now >= entry.expires_at:
            # Entry has expired, remove it
            logger.debug(f"Cache expired: {key}")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit: {key}")
        return entry.data

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Store data in cache with TTL.
        
        Args:
            key: Cache key to store under.
            data: Data to cache.
            ttl: Time-to-live in seconds (uses default_ttl if None).
        """
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        self._cache[key] = CacheEntry(data=data, expires_at=expires_at)
        logger.debug(f"Cache set: {key} (TTL={ttl_seconds}s)")

        # Perform cleanup periodically
        if len(self._cache) % 10 == 0:
            self._cleanup_expired()

    def invalidate(self, key: str) -> None:
        """Remove specific cache entry.
        
        Args:
            key: Cache key to remove.
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache invalidated: {key}")
        else:
            logger.debug(f"Cache invalidation attempted for non-existent key: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache.
        
        This is called periodically during set() operations to prevent
        the cache from growing indefinitely with expired entries.
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items() if now >= entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics including size and expired entries.
        """
        now = datetime.now()
        total = len(self._cache)
        expired = sum(1 for entry in self._cache.values() if now >= entry.expires_at)
        active = total - expired

        return {
            "total_entries": total,
            "active_entries": active,
            "expired_entries": expired,
            "default_ttl": self.default_ttl,
        }
