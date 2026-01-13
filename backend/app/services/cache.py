"""
Redis cache service for AI processing results.
"""

import redis
import json
import ssl
from typing import Optional, Any
from app.config import settings


class CacheService:
    """Redis-based caching service for AI processing results."""

    def __init__(self):
        """Initialize Redis client with connection from settings."""
        try:
            redis_url = settings.REDIS_URL
            print(f"🔍 [Redis Debug] Starting Redis connection...")
            print(f"🔍 [Redis Debug] REDIS_URL exists: {bool(redis_url)}")

            if redis_url:
                # Show first 30 chars for debugging (hide password)
                url_preview = redis_url[:30] + "..." if len(redis_url) > 30 else redis_url
                print(f"🔍 [Redis Debug] URL preview: {url_preview}")
                print(f"🔍 [Redis Debug] Is SSL (rediss://): {redis_url.startswith('rediss://')}")

            # For SSL connections (rediss://), pass SSL parameters directly
            if redis_url and redis_url.startswith('rediss://'):
                print(f"🔍 [Redis Debug] Using SSL connection with CERT_NONE")
                print(f"🔍 [Redis Debug] ssl_cert_reqs value: {ssl.CERT_NONE}")
                print(f"🔍 [Redis Debug] Creating redis client...")

                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    ssl_cert_reqs=ssl.CERT_NONE,
                    ssl_check_hostname=False
                )
                print(f"🔍 [Redis Debug] Client created successfully")
            else:
                # Non-SSL connection
                print(f"🔍 [Redis Debug] Using non-SSL connection")
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True
                )
                print(f"🔍 [Redis Debug] Client created successfully")

            # Test connection
            print(f"🔍 [Redis Debug] Attempting PING...")
            result = self.redis_client.ping()
            print(f"🔍 [Redis Debug] PING result: {result}")
            print("✅ Redis cache connected successfully")

        except redis.ConnectionError as e:
            print(f"❌ [Redis Debug] ConnectionError details:")
            print(f"   - Error type: {type(e).__name__}")
            print(f"   - Error message: {e}")
            print(f"   - Error args: {e.args if hasattr(e, 'args') else 'N/A'}")
            self.redis_client = None
        except Exception as e:
            print(f"❌ [Redis Debug] Unexpected error:")
            print(f"   - Error type: {type(e).__name__}")
            print(f"   - Error message: {e}")
            import traceback
            print(f"   - Traceback: {traceback.format_exc()}")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value (deserialized from JSON) or None if not found
        """
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with TTL (Time To Live).

        Args:
            key: Cache key
            value: Value to cache (will be serialized to JSON)
            ttl: Time to live in seconds (default: 3600 = 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)  # default=str handles datetime objects
            )
            return True
        except Exception as e:
            print(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists check error for key '{key}': {e}")
            return False

    def cache_key_tender_summary(self, tender_id: str) -> str:
        """
        Generate cache key for tender summary.

        Args:
            tender_id: Tender UUID

        Returns:
            Cache key string
        """
        return f"tender:summary:{tender_id}"

    def cache_key_tender_entities(self, tender_id: str) -> str:
        """
        Generate cache key for tender extracted entities.

        Args:
            tender_id: Tender UUID

        Returns:
            Cache key string
        """
        return f"tender:entities:{tender_id}"

    def cache_key_tender_quick_scan(self, tender_id: str) -> str:
        """
        Generate cache key for tender quick scan.

        Args:
            tender_id: Tender UUID

        Returns:
            Cache key string
        """
        return f"tender:quick_scan:{tender_id}"

    def invalidate_tender_cache(self, tender_id: str) -> bool:
        """
        Invalidate all cache entries for a tender.

        Args:
            tender_id: Tender UUID

        Returns:
            True if successful, False otherwise
        """
        keys = [
            self.cache_key_tender_summary(tender_id),
            self.cache_key_tender_entities(tender_id),
            self.cache_key_tender_quick_scan(tender_id)
        ]

        success = True
        for key in keys:
            if not self.delete(key):
                success = False

        return success


# Global cache service instance
cache_service = CacheService()
