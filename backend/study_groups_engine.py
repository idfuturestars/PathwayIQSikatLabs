"""
Study Groups and Collaborative Learning Engine
Handles group management, real-time messaging, and collaborative features
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
from pymongo import MongoClient
import redis
import json

logger = logging.getLogger(__name__)

class StudyGroupsEngine:
    def __init__(self, mongo_url: str, redis_url: str = "redis://localhost:6379"):
        self.client = MongoClient(mongo_url)
        self.db = self.client.get_database()
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Collections
        self.groups_collection = self.db.study_groups
        self.messages_collection = self.db.group_messages
        self.members_collection = self.db.group_members
        self.sessions_collection = self.db.study_sessions
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Study groups indexes
            self.groups_collection.create_index([("group_id", 1)], unique=True)
            self.groups_collection.create_index([("created_by", 1)])
            self.groups_collection.create_index([("subject", 1)])
            self.groups_collection.create_index([("is_active", 1)])
            
            # Messages indexes
            self.messages_collection.create_index([("group_id", 1), ("timestamp", -1)])
            self.messages_collection.create_index([("user_id", 1)])
            
            # Members indexes
            self.members_collection.create_index([("group_id", 1), ("user_id", 1)], unique=True)
            self.members_collection.create_index([("user_id", 1)])
            
            # Sessions indexes
            self.sessions_collection.create_index([("group_id", 1), ("start_time", -1)])
            self.sessions_collection.create_index([("participants.user_id", 1)])
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # GROUP MANAGEMENT
    async def create_study_group(
        self,
        creator_id: str,
        name: str,
        description: str,
        subject: str,
        max_members: int = 10,
        is_public: bool = True,
        topics: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new study group"""
        try:
            group_id = str(uuid.uuid4())
            
            group_data = {
                "group_id": group_id,
                "name": name,
                "description": description,
                "subject": subject,
                "created_by": creator_id,
                "created_at": datetime.utcnow(),
                "max_members": max_members,
                "current_members": 1,
                "is_public": is_public,
                "is_active": True,
                "topics": topics or [],
                "study_schedule": [],
                "group_settings": {
                    "allow_file_sharing": True,
                    "allow_voice_chat": True,
                    "moderation_enabled": True,
                    "auto_accept_members": is_public
                }
            }
            
            # Insert group
            self.groups_collection.insert_one(group_data)
            
            # Add creator as admin member
            await self._add_member(group_id, creator_id, role="admin")
            
            logger.info(f"Study group created: {group_id} by {creator_id}")
            
            return {
                "success": True,
                "group_id": group_id,
                "group": group_data
            }
            
        except Exception as e:
            logger.error(f"Error creating study group: {e}")
            return {"success": False, "error": str(e)}
    
    async def join_study_group(
        self,
        user_id: str,
        group_id: str,
        join_message: str = ""
    ) -> Dict[str, Any]:
        """Join an existing study group"""
        try:
            # Check if group exists and is active
            group = self.groups_collection.find_one({
                "group_id": group_id,
                "is_active": True
            })
            
            if not group:
                return {"success": False, "error": "Study group not found or inactive"}
            
            # Check if user is already a member
            existing_member = self.members_collection.find_one({
                "group_id": group_id,
                "user_id": user_id
            })
            
            if existing_member:
                return {"success": False, "error": "Already a member of this group"}
            
            # Check group capacity
            if group["current_members"] >= group["max_members"]:
                return {"success": False, "error": "Group is at maximum capacity"}
            
            # Add member
            result = await self._add_member(group_id, user_id, join_message=join_message)
            
            if result["success"]:
                # Update member count
                self.groups_collection.update_one(
                    {"group_id": group_id},
                    {"$inc": {"current_members": 1}}
                )
                
                # Notify group of new member
                await self._send_system_message(
                    group_id,
                    f"New member joined the group!",
                    metadata={"user_joined": user_id}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error joining study group: {e}")
            return {"success": False, "error": str(e)}
    
    async def leave_study_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Leave a study group"""
        try:
            # Remove member
            result = self.members_collection.delete_one({
                "group_id": group_id,
                "user_id": user_id
            })
            
            if result.deleted_count > 0:
                # Update member count
                self.groups_collection.update_one(
                    {"group_id": group_id},
                    {"$inc": {"current_members": -1}}
                )
                
                # Notify group
                await self._send_system_message(
                    group_id,
                    f"A member left the group",
                    metadata={"user_left": user_id}
                )
                
                return {"success": True}
            else:
                return {"success": False, "error": "Not a member of this group"}
                
        except Exception as e:
            logger.error(f"Error leaving study group: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all groups a user is a member of"""
        try:
            # Get user's memberships
            memberships = list(self.members_collection.find({"user_id": user_id}))
            group_ids = [m["group_id"] for m in memberships]
            
            # Get group details
            groups = list(self.groups_collection.find({
                "group_id": {"$in": group_ids},
                "is_active": True
            }))
            
            # Add membership role info
            membership_map = {m["group_id"]: m for m in memberships}
            
            for group in groups:
                membership = membership_map.get(group["group_id"], {})
                group["user_role"] = membership.get("role", "member")
                group["joined_at"] = membership.get("joined_at")
            
            return groups
            
        except Exception as e:
            logger.error(f"Error getting user groups: {e}")
            return []
    
    async def get_public_groups(
        self,
        subject: str = None,
        limit: int = 20,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Get public study groups"""
        try:
            query = {"is_public": True, "is_active": True}
            
            if subject:
                query["subject"] = subject
            
            groups = list(
                self.groups_collection
                .find(query)
                .sort([("created_at", -1)])
                .skip(skip)
                .limit(limit)
            )
            
            return groups
            
        except Exception as e:
            logger.error(f"Error getting public groups: {e}")
            return []
    
    # MESSAGING SYSTEM
    async def send_message(
        self,
        group_id: str,
        user_id: str,
        content: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send a message to a study group"""
        try:
            # Verify user is a member
            member = self.members_collection.find_one({
                "group_id": group_id,
                "user_id": user_id
            })
            
            if not member:
                return {"success": False, "error": "Not a member of this group"}
            
            message_id = str(uuid.uuid4())
            message_data = {
                "message_id": message_id,
                "group_id": group_id,
                "user_id": user_id,
                "content": content,
                "message_type": message_type,
                "timestamp": datetime.utcnow(),
                "edited_at": None,
                "metadata": metadata or {},
                "reactions": [],
                "thread_messages": []
            }
            
            # Insert message
            self.messages_collection.insert_one(message_data)
            
            # Cache recent message for real-time access
            self._cache_recent_message(group_id, message_data)
            
            # Broadcast to connected users
            await self._broadcast_message(group_id, message_data)
            
            return {
                "success": True,
                "message_id": message_id,
                "message": message_data
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_group_messages(
        self,
        group_id: str,
        user_id: str,
        limit: int = 50,
        before_timestamp: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get messages from a study group"""
        try:
            # Verify user is a member
            member = self.members_collection.find_one({
                "group_id": group_id,
                "user_id": user_id
            })
            
            if not member:
                return []
            
            query = {"group_id": group_id}
            
            if before_timestamp:
                query["timestamp"] = {"$lt": before_timestamp}
            
            messages = list(
                self.messages_collection
                .find(query)
                .sort([("timestamp", -1)])
                .limit(limit)
            )
            
            return list(reversed(messages))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error getting group messages: {e}")
            return []
    
    # STUDY SESSIONS
    async def start_study_session(
        self,
        group_id: str,
        creator_id: str,
        topic: str,
        description: str = "",
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """Start a collaborative study session"""
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                "session_id": session_id,
                "group_id": group_id,
                "created_by": creator_id,
                "topic": topic,
                "description": description,
                "start_time": datetime.utcnow(),
                "planned_duration": duration_minutes,
                "end_time": None,
                "is_active": True,
                "participants": [{
                    "user_id": creator_id,
                    "joined_at": datetime.utcnow(),
                    "left_at": None,
                    "participation_score": 0
                }],
                "session_notes": [],
                "shared_resources": [],
                "quiz_questions": [],
                "session_stats": {
                    "total_messages": 0,
                    "active_participants": 1,
                    "resources_shared": 0
                }
            }
            
            # Insert session
            self.sessions_collection.insert_one(session_data)
            
            # Notify group
            await self._send_system_message(
                group_id,
                f"Study session started: {topic}",
                metadata={
                    "session_id": session_id,
                    "type": "session_start"
                }
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "session": session_data
            }
            
        except Exception as e:
            logger.error(f"Error starting study session: {e}")
            return {"success": False, "error": str(e)}
    
    async def join_study_session(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Join an active study session"""
        try:
            # Check if session exists and is active
            session = self.sessions_collection.find_one({
                "session_id": session_id,
                "is_active": True
            })
            
            if not session:
                return {"success": False, "error": "Study session not found or inactive"}
            
            # Check if user is already a participant
            is_participant = any(
                p["user_id"] == user_id for p in session["participants"]
            )
            
            if is_participant:
                return {"success": False, "error": "Already participating in this session"}
            
            # Add participant
            participant_data = {
                "user_id": user_id,
                "joined_at": datetime.utcnow(),
                "left_at": None,
                "participation_score": 0
            }
            
            self.sessions_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"participants": participant_data},
                    "$inc": {"session_stats.active_participants": 1}
                }
            )
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error joining study session: {e}")
            return {"success": False, "error": str(e)}
    
    # PRIVATE HELPER METHODS
    async def _add_member(
        self,
        group_id: str,
        user_id: str,
        role: str = "member",
        join_message: str = ""
    ) -> Dict[str, Any]:
        """Add a member to a study group"""
        try:
            member_data = {
                "group_id": group_id,
                "user_id": user_id,
                "role": role,  # admin, moderator, member
                "joined_at": datetime.utcnow(),
                "join_message": join_message,
                "is_active": True,
                "permissions": {
                    "can_invite": role in ["admin", "moderator"],
                    "can_moderate": role in ["admin", "moderator"],
                    "can_manage_sessions": role in ["admin", "moderator"]
                }
            }
            
            self.members_collection.insert_one(member_data)
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_system_message(
        self,
        group_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """Send a system message to the group"""
        try:
            message_data = {
                "message_id": str(uuid.uuid4()),
                "group_id": group_id,
                "user_id": "system",
                "content": content,
                "message_type": "system",
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            self.messages_collection.insert_one(message_data)
            
            # Cache and broadcast
            self._cache_recent_message(group_id, message_data)
            await self._broadcast_message(group_id, message_data)
            
        except Exception as e:
            logger.error(f"Error sending system message: {e}")
    
    def _cache_recent_message(self, group_id: str, message_data: Dict[str, Any]):
        """Cache recent message in Redis for real-time access"""
        try:
            # Store last 10 messages per group in Redis
            cache_key = f"group_messages:{group_id}"
            
            # Convert datetime to ISO string for JSON serialization
            message_copy = message_data.copy()
            message_copy["timestamp"] = message_copy["timestamp"].isoformat()
            
            # Add to Redis list (keep last 10)
            self.redis_client.lpush(cache_key, json.dumps(message_copy))
            self.redis_client.ltrim(cache_key, 0, 9)
            
            # Set expiry
            self.redis_client.expire(cache_key, 3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Error caching message: {e}")
    
    async def _broadcast_message(self, group_id: str, message_data: Dict[str, Any]):
        """Broadcast message to connected WebSocket clients"""
        try:
            # Store in Redis pub/sub for WebSocket broadcasting
            channel = f"group_messages:{group_id}"
            
            # Convert datetime for JSON serialization
            broadcast_data = message_data.copy()
            broadcast_data["timestamp"] = broadcast_data["timestamp"].isoformat()
            
            self.redis_client.publish(channel, json.dumps(broadcast_data))
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    # ANALYTICS AND INSIGHTS
    async def get_group_analytics(
        self,
        group_id: str,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a study group"""
        try:
            # Verify user is a member
            member = self.members_collection.find_one({
                "group_id": group_id,
                "user_id": user_id
            })
            
            if not member:
                return {"error": "Not a member of this group"}
            
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Message analytics
            message_stats = self.messages_collection.aggregate([
                {
                    "$match": {
                        "group_id": group_id,
                        "timestamp": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "message_count": {"$sum": 1}
                    }
                }
            ])
            
            # Session analytics
            session_stats = self.sessions_collection.aggregate([
                {
                    "$match": {
                        "group_id": group_id,
                        "start_time": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_sessions": {"$sum": 1},
                        "avg_duration": {"$avg": "$planned_duration"}
                    }
                }
            ])
            
            return {
                "message_stats": list(message_stats),
                "session_stats": list(session_stats),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting group analytics: {e}")
            return {"error": str(e)}