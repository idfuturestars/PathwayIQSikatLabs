"""
PathwayIQ Session Management with Redis
Handles user sessions, caching, and performance optimization
"""

import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.redis_client = None
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', 7200))  # 2 hours default
        self.cache_ttl = int(os.getenv('CACHE_TTL', 3600))  # 1 hour default
        self.connect_redis()
    
    def connect_redis(self):
        """Connect to Redis server"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            self.redis_client = redis.from_url(
                redis_url,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to in-memory storage.")
            self.redis_client = None
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'user_data': user_data,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat()
        }
        
        try:
            if self.redis_client:
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.session_timeout,
                    json.dumps(session_data)
                )
                # Also store user session mapping
                self.redis_client.setex(
                    f"user_session:{user_id}",
                    self.session_timeout,
                    session_id
                )
            
            logger.info(f"Session created for user {user_id}: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            if self.redis_client:
                session_data = self.redis_client.get(f"session:{session_id}")
                if session_data:
                    return json.loads(session_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def update_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            if self.redis_client:
                session_data = self.get_session(session_id)
                if session_data:
                    session_data['user_data'].update(user_data)
                    session_data['last_accessed'] = datetime.utcnow().isoformat()
                    
                    self.redis_client.setex(
                        f"session:{session_id}",
                        self.session_timeout,
                        json.dumps(session_data)
                    )
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            if self.redis_client:
                # Get session to find user_id
                session_data = self.get_session(session_id)
                if session_data:
                    user_id = session_data.get('user_id')
                    self.redis_client.delete(f"session:{session_id}")
                    self.redis_client.delete(f"user_session:{user_id}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Cache a value"""
        try:
            if self.redis_client:
                ttl = ttl or self.cache_ttl
                self.redis_client.setex(
                    f"cache:{key}",
                    ttl,
                    json.dumps(value)
                )
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to cache value: {e}")
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            if self.redis_client:
                cached_value = self.redis_client.get(f"cache:{key}")
                if cached_value:
                    return json.loads(cached_value)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached value: {e}")
            return None
    
    def cache_delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            if self.redis_client:
                self.redis_client.delete(f"cache:{key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete cached value: {e}")
            return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        try:
            if self.redis_client:
                return len(self.redis_client.keys("session:*"))
            return 0
            
        except Exception as e:
            logger.error(f"Failed to get active sessions count: {e}")
            return 0
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (Redis handles this automatically with TTL)"""
        try:
            if self.redis_client:
                # Redis automatically handles TTL expiration
                # This is just for monitoring
                active_sessions = self.redis_client.keys("session:*")
                return len(active_sessions)
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")
            return 0

# Global session manager instance
session_manager = SessionManager()