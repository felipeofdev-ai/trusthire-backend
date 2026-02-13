"""
TrustHire Redis Cache Service
High-performance caching for analysis results
"""

import json
import redis
from typing import Optional, Any
from config import settings
from utils.logger import get_logger

logger = get_logger("cache")


class CacheService:
    """
    Redis-based caching service
    
    Features:
    - Automatic serialization/deserialization
    - TTL support
    - Prefix namespacing
    - Error resilience
    """
    
    def __init__(self):
        self.enabled = settings.CACHE_ENABLED
        self.prefix = settings.CACHE_PREFIX
        self.default_ttl = settings.CACHE_TTL
        
        if self.enabled:
            try:
                self.client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                # Test connection
                self.client.ping()
                logger.info("Cache service connected")
            except Exception as e:
                logger.warning(f"Cache unavailable: {e}")
                self.enabled = False
                self.client = None
        else:
            self.client = None
            logger.info("Cache disabled")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            full_key = f"{self.prefix}{key}"
            value = self.client.get(full_key)
            
            if value:
                logger.debug(f"Cache hit: {key}")
                return self._deserialize(value)
            
            logger.debug(f"Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            Success status
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            full_key = f"{self.prefix}{key}"
            serialized = self._serialize(value)
            ttl = ttl or self.default_ttl
            
            self.client.setex(full_key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            full_key = f"{self.prefix}{key}"
            self.client.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        # Handle Pydantic models
        if hasattr(value, "dict"):
            return json.dumps(value.dict())
        return json.dumps(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value


# Singleton instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get singleton cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
