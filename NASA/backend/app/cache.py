"""Cache Service for NASA Space Biology Knowledge Engine.

Provides multi-tier caching with Redis primary, SQLite fallback, 
and in-memory last resort for optimal performance and reliability.
"""

import time
import asyncio
import json
from typing import Any, Optional, Dict
from .config import settings, logger
import aiosqlite
import os

# Optional Redis import
try:
    import aioredis
except ImportError:
    aioredis = None
    logger.warning("Redis not available, using SQLite fallback")

class InMemoryCache:
    """In-memory cache with TTL support - last resort fallback."""
    
    def __init__(self, max_size: int = 1000):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        self.max_size = max_size

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            # Check expiry
            if key in self._expiry and self._expiry[key] < time.time():
                self._cleanup_key(key)
                return None
            
            if key in self._store:
                self._access_times[key] = time.time()
                return self._store[key]
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        async with self._lock:
            # Cleanup if at max size
            if len(self._store) >= self.max_size:
                await self._evict_oldest()
            
            self._store[key] = value
            self._expiry[key] = time.time() + ttl
            self._access_times[key] = time.time()

    async def delete(self, key: str):
        async with self._lock:
            self._cleanup_key(key)

    def _cleanup_key(self, key: str):
        """Remove key from all internal stores."""
        self._store.pop(key, None)
        self._expiry.pop(key, None)
        self._access_times.pop(key, None)

    async def _evict_oldest(self):
        """Evict oldest accessed key to make space."""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times, key=self._access_times.get)
        self._cleanup_key(oldest_key)

class SQLiteCache:
    """SQLite-based cache for persistent fallback storage."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialized = False

    async def init(self):
        """Initialize SQLite cache database."""
        if self._initialized:
            return
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        expires_at REAL NOT NULL,
                        created_at REAL NOT NULL
                    )
                """)
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
                """)
                await db.commit()
            
            self._initialized = True
            logger.info(f"SQLite cache initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQLite cache: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from SQLite cache."""
        if not self._initialized:
            return None
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Clean expired entries first
                await db.execute(
                    "DELETE FROM cache WHERE expires_at < ?", 
                    (time.time(),)
                )
                
                # Get the value
                async with db.execute(
                    "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
                    (key, time.time())
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
                    return None
                    
        except Exception as e:
            logger.error(f"SQLite cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in SQLite cache."""
        if not self._initialized:
            return
            
        try:
            expires_at = time.time() + ttl
            created_at = time.time()
            value_json = json.dumps(value)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expires_at, created_at) VALUES (?, ?, ?, ?)",
                    (key, value_json, expires_at, created_at)
                )
                await db.commit()
                
        except Exception as e:
            logger.error(f"SQLite cache set error: {e}")

    async def delete(self, key: str):
        """Delete value from SQLite cache."""
        if not self._initialized:
            return
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM cache WHERE key = ?", (key,))
                await db.commit()
                
        except Exception as e:
            logger.error(f"SQLite cache delete error: {e}")

    async def cleanup_expired(self):
        """Clean up expired cache entries."""
        if not self._initialized:
            return
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                result = await db.execute(
                    "DELETE FROM cache WHERE expires_at < ?", 
                    (time.time(),)
                )
                await db.commit()
                logger.debug(f"Cleaned up {result.rowcount} expired cache entries")
                
        except Exception as e:
            logger.error(f"SQLite cache cleanup error: {e}")

class CacheService:
    """Multi-tier cache service with Redis -> SQLite -> Memory fallback."""
    
    def __init__(self):
        self.redis_url = settings.redis_url
        self.redis_client = None
        
        # SQLite fallback
        sqlite_path = os.path.join(settings.data_dir, "cache.db")
        self.sqlite_cache = SQLiteCache(sqlite_path)
        
        # In-memory last resort
        self.memory_cache = InMemoryCache(max_size=settings.max_cache_size)
        
        logger.info(f"Cache service configured:")
        logger.info(f"  - Redis: {'✓' if self.redis_url else '✗'}")
        logger.info(f"  - SQLite: ✓ (at {sqlite_path})")
        logger.info(f"  - Memory: ✓ (max size: {settings.max_cache_size})")

    async def init(self):
        """Initialize cache service with all fallback tiers."""
        # Try to initialize Redis
        if self.redis_url and aioredis:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using SQLite fallback.")
                self.redis_client = None
        
        # Initialize SQLite fallback
        try:
            await self.sqlite_cache.init()
        except Exception as e:
            logger.warning(f"SQLite cache initialization failed: {e}. Using memory only.")
        
        logger.info("Cache service initialized with multi-tier fallback")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache using fallback hierarchy."""
        # Try Redis first
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value is not None:
                    return json.loads(value)
            except Exception as e:
                logger.debug(f"Redis get failed for {key}: {e}")
        
        # Try SQLite fallback
        try:
            value = await self.sqlite_cache.get(key)
            if value is not None:
                # Cache hit in SQLite - optionally promote to Redis
                if self.redis_client:
                    try:
                        await self.redis_client.setex(
                            key, 
                            settings.cache_ttl, 
                            json.dumps(value)
                        )
                    except Exception:
                        pass  # Ignore promotion failures
                return value
        except Exception as e:
            logger.debug(f"SQLite get failed for {key}: {e}")
        
        # Try memory fallback
        return await self.memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache across all available tiers."""
        if ttl is None:
            ttl = settings.cache_ttl
        
        # Set in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl, json.dumps(value))
            except Exception as e:
                logger.debug(f"Redis set failed for {key}: {e}")
        
        # Set in SQLite
        try:
            await self.sqlite_cache.set(key, value, ttl)
        except Exception as e:
            logger.debug(f"SQLite set failed for {key}: {e}")
        
        # Set in memory cache
        await self.memory_cache.set(key, value, ttl)

    async def delete(self, key: str):
        """Delete value from all cache tiers."""
        # Delete from Redis
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.debug(f"Redis delete failed for {key}: {e}")
        
        # Delete from SQLite
        try:
            await self.sqlite_cache.delete(key)
        except Exception as e:
            logger.debug(f"SQLite delete failed for {key}: {e}")
        
        # Delete from memory
        await self.memory_cache.delete(key)

    async def clear_expired(self):
        """Clean up expired entries across all cache tiers."""
        try:
            await self.sqlite_cache.cleanup_expired()
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health information."""
        stats = {
            "redis_available": self.redis_client is not None,
            "sqlite_available": self.sqlite_cache._initialized,
            "memory_available": True
        }
        
        # Redis stats
        if self.redis_client:
            try:
                await self.redis_client.ping()
                stats["redis_healthy"] = True
            except Exception:
                stats["redis_healthy"] = False
        
        return stats

    async def close(self):
        """Close cache connections."""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis cache connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
