"""
PathwayIQ Caching Strategy
Multi-level caching for optimal performance
"""

import asyncio
import json
import hashlib
import time
from typing import Any, Optional, Dict, List
from functools import wraps
import logging
from session_manager import session_manager

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self.default_ttl = 3600  # 1 hour
        
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str, use_redis: bool = True) -> Optional[Any]:
        """Get value from cache (Redis first, then memory)"""
        try:
            # Try Redis first
            if use_redis:
                cached_value = session_manager.cache_get(key)
                if cached_value is not None:
                    self.cache_stats['hits'] += 1
                    return cached_value
            
            # Fallback to memory cache
            if key in self.memory_cache:
                cache_entry = self.memory_cache[key]
                if cache_entry['expires_at'] > time.time():
                    self.cache_stats['hits'] += 1
                    return cache_entry['value']
                else:
                    # Expired, remove from memory
                    del self.memory_cache[key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, use_redis: bool = True) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            
            # Set in Redis
            if use_redis:
                success = session_manager.cache_set(key, value, ttl)
                if success:
                    self.cache_stats['sets'] += 1
                    return True
            
            # Fallback to memory cache
            self.memory_cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str, use_redis: bool = True) -> bool:
        """Delete value from cache"""
        try:
            success = False
            
            # Delete from Redis
            if use_redis:
                success = session_manager.cache_delete(key)
            
            # Delete from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
                success = True
            
            if success:
                self.cache_stats['deletes'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_all(self, pattern: Optional[str] = None) -> bool:
        """Clear cache (optionally by pattern)"""
        try:
            # Clear Redis cache
            if session_manager.redis_client:
                if pattern:
                    keys = session_manager.redis_client.keys(f"cache:{pattern}*")
                    if keys:
                        session_manager.redis_client.delete(*keys)
                else:
                    keys = session_manager.redis_client.keys("cache:*")
                    if keys:
                        session_manager.redis_client.delete(*keys)
            
            # Clear memory cache
            if pattern:
                keys_to_delete = [key for key in self.memory_cache.keys() if pattern in key]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            else:
                self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'deletes': self.cache_stats['deletes'],
            'hit_rate_percentage': hit_rate,
            'memory_cache_size': len(self.memory_cache),
            'redis_available': session_manager.redis_client is not None
        }
    
    def cleanup_expired(self):
        """Clean up expired entries from memory cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry['expires_at'] < current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        return len(expired_keys)

# Global cache manager instance
cache_manager = CacheManager()

# Decorator for caching function results
def cache_result(prefix: str, ttl: Optional[int] = None, use_redis: bool = True):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key, use_redis)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_manager.set(cache_key, result, ttl, use_redis)
            
            return result
        return wrapper
    return decorator

# Specific caching functions for PathwayIQ
class PathwayIQCache:
    """PathwayIQ-specific caching functions"""
    
    @staticmethod
    @cache_result("user_profile", ttl=1800)  # 30 minutes
    async def get_user_profile(user_id: str):
        """Cache user profile data"""
        # This would be implemented in the actual server
        pass
    
    @staticmethod
    @cache_result("question_bank", ttl=3600)  # 1 hour
    async def get_questions_by_subject(subject: str, difficulty: str):
        """Cache question bank queries"""
        # This would be implemented in the actual server
        pass
    
    @staticmethod
    @cache_result("user_analytics", ttl=900)  # 15 minutes
    async def get_user_analytics(user_id: str):
        """Cache user analytics data"""
        # This would be implemented in the actual server
        pass
    
    @staticmethod
    @cache_result("leaderboard", ttl=300)  # 5 minutes
    async def get_leaderboard(subject: str, limit: int = 10):
        """Cache leaderboard data"""
        # This would be implemented in the actual server
        pass
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"user_profile:{user_id}",
            f"user_analytics:{user_id}",
            "leaderboard:*"  # Leaderboard might change
        ]
        
        for pattern in patterns:
            await cache_manager.clear_all(pattern)
    
    @staticmethod
    async def invalidate_question_cache(subject: str = None):
        """Invalidate question cache"""
        if subject:
            await cache_manager.clear_all(f"question_bank:{subject}")
        else:
            await cache_manager.clear_all("question_bank:")
    
    @staticmethod
    async def warm_up_cache():
        """Warm up commonly accessed cache entries"""
        # This would pre-populate cache with frequently accessed data
        logger.info("Cache warm-up started")
        
        # Example: Pre-cache popular subjects
        popular_subjects = ["mathematics", "science", "english", "history"]
        for subject in popular_subjects:
            try:
                # This would call actual data loading functions
                logger.info(f"Pre-caching {subject} questions")
            except Exception as e:
                logger.error(f"Cache warm-up failed for {subject}: {e}")
        
        logger.info("Cache warm-up completed")

# Background task for cache maintenance
async def cache_maintenance_task():
    """Background task for cache maintenance"""
    while True:
        try:
            # Clean up expired entries
            expired_count = cache_manager.cleanup_expired()
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache entries")
            
            # Log cache statistics
            stats = cache_manager.get_stats()
            logger.info(f"Cache stats: {stats}")
            
            # Wait 5 minutes before next maintenance
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Cache maintenance error: {e}")
            await asyncio.sleep(300)

# CLI command for cache operations
async def main():
    """Cache management CLI"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cache_manager.py [stats|clear|warmup]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        stats = cache_manager.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif command == "clear":
        await cache_manager.clear_all()
        print("Cache cleared successfully")
    
    elif command == "warmup":
        await PathwayIQCache.warm_up_cache()
        print("Cache warm-up completed")
    
    else:
        print("Unknown command. Use: stats, clear, or warmup")

if __name__ == "__main__":
    asyncio.run(main())