"""
Gamification System - Badge and Achievement Engine
Comprehensive badge management, achievement tracking, and progress monitoring
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)

class BadgeType(str, Enum):
    """Types of badges available"""
    LEARNING_MILESTONE = "learning_milestone"
    STREAK_ACHIEVEMENT = "streak_achievement"
    SKILL_MASTERY = "skill_mastery"
    SOCIAL_ENGAGEMENT = "social_engagement"
    ASSESSMENT_PERFORMANCE = "assessment_performance"
    THINK_ALOUD_MASTERY = "think_aloud_mastery"
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    INNOVATION = "innovation"
    DEDICATION = "dedication"

class BadgeTier(str, Enum):
    """Badge difficulty tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class AchievementStatus(str, Enum):
    """Achievement completion status"""
    LOCKED = "locked"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    CLAIMED = "claimed"

class BadgeDefinition(BaseModel):
    """Badge definition model"""
    id: str
    name: str
    description: str
    type: BadgeType
    tier: BadgeTier
    icon: str
    requirements: Dict[str, Any]
    points: int
    rarity: float  # 0.0 to 1.0 (1.0 = very rare)
    prerequisites: List[str] = []
    active: bool = True
    created_at: datetime = None

class UserAchievement(BaseModel):
    """User achievement progress model"""
    id: str
    user_id: str
    badge_id: str
    status: AchievementStatus
    progress: Dict[str, Any] = {}
    progress_percentage: float = 0.0
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    created_at: datetime = None

class AchievementNotification(BaseModel):
    """Achievement notification model"""
    id: str
    user_id: str
    badge_id: str
    type: str  # "unlocked", "progress", "completed"
    message: str
    read: bool = False
    created_at: datetime = None

class GamificationEngine:
    """Main gamification engine"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.badge_definitions = {}
        
    async def initialize(self):
        """Initialize the gamification system with default badges"""
        await self._create_default_badges()
        await self._create_database_indexes()
        
    async def _create_database_indexes(self):
        """Create database indexes for performance"""
        try:
            # User achievements indexes
            await self.db.user_achievements.create_index([("user_id", 1), ("badge_id", 1)], unique=True)
            await self.db.user_achievements.create_index([("user_id", 1), ("status", 1)])
            await self.db.user_achievements.create_index([("completed_at", -1)])
            
            # Notifications indexes
            await self.db.achievement_notifications.create_index([("user_id", 1), ("read", 1)])
            await self.db.achievement_notifications.create_index([("created_at", -1)])
            
            # Leaderboard indexes
            await self.db.leaderboard_entries.create_index([("category", 1), ("score", -1)])
            await self.db.leaderboard_entries.create_index([("user_id", 1), ("category", 1)], unique=True)
            
            logger.info("Gamification database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating database indexes: {str(e)}")
    
    async def _create_default_badges(self):
        """Create default badge definitions"""
        default_badges = [
            # Learning Milestone Badges
            {
                "id": "first_assessment",
                "name": "First Steps",
                "description": "Complete your first adaptive assessment",
                "type": BadgeType.LEARNING_MILESTONE,
                "tier": BadgeTier.BRONZE,
                "icon": "🎯",
                "requirements": {"assessments_completed": 1},
                "points": 50,
                "rarity": 0.1
            },
            {
                "id": "assessment_ace",
                "name": "Assessment Ace",
                "description": "Complete 10 adaptive assessments",
                "type": BadgeType.LEARNING_MILESTONE,
                "tier": BadgeTier.SILVER,
                "icon": "🏆",
                "requirements": {"assessments_completed": 10},
                "points": 200,
                "rarity": 0.3
            },
            {
                "id": "century_scholar",
                "name": "Century Scholar",
                "description": "Complete 100 adaptive assessments",
                "type": BadgeType.LEARNING_MILESTONE,
                "tier": BadgeTier.GOLD,
                "icon": "💎",
                "requirements": {"assessments_completed": 100},
                "points": 1000,
                "rarity": 0.7
            },
            
            # Streak Achievement Badges
            {
                "id": "daily_learner",
                "name": "Daily Learner",
                "description": "Complete assessments for 7 consecutive days",
                "type": BadgeType.STREAK_ACHIEVEMENT,
                "tier": BadgeTier.BRONZE,
                "icon": "📅",
                "requirements": {"consecutive_days": 7},
                "points": 100,
                "rarity": 0.4
            },
            {
                "id": "dedication_master",
                "name": "Dedication Master",
                "description": "Complete assessments for 30 consecutive days",
                "type": BadgeType.STREAK_ACHIEVEMENT,
                "tier": BadgeTier.GOLD,
                "icon": "🔥",
                "requirements": {"consecutive_days": 30},
                "points": 500,
                "rarity": 0.8
            },
            
            # Skill Mastery Badges
            {
                "id": "perfect_score",
                "name": "Perfect Score",
                "description": "Achieve 100% on an adaptive assessment",
                "type": BadgeType.SKILL_MASTERY,
                "tier": BadgeTier.SILVER,
                "icon": "⭐",
                "requirements": {"perfect_scores": 1},
                "points": 150,
                "rarity": 0.3
            },
            {
                "id": "consistency_champion",
                "name": "Consistency Champion",
                "description": "Score above 85% on 10 consecutive assessments",
                "type": BadgeType.SKILL_MASTERY,
                "tier": BadgeTier.GOLD,
                "icon": "🎖️",
                "requirements": {"consecutive_high_scores": 10, "threshold": 0.85},
                "points": 300,
                "rarity": 0.6
            },
            
            # Think-Aloud Mastery Badges
            {
                "id": "voice_pioneer",
                "name": "Voice Pioneer",
                "description": "Complete your first think-aloud assessment",
                "type": BadgeType.THINK_ALOUD_MASTERY,
                "tier": BadgeTier.BRONZE,
                "icon": "🎤",
                "requirements": {"think_aloud_completed": 1},
                "points": 75,
                "rarity": 0.2
            },
            {
                "id": "articulate_thinker",
                "name": "Articulate Thinker",
                "description": "Complete 20 think-aloud assessments with clear reasoning",
                "type": BadgeType.THINK_ALOUD_MASTERY,
                "tier": BadgeTier.SILVER,
                "icon": "🗣️",
                "requirements": {"think_aloud_completed": 20, "clarity_score": 0.8},
                "points": 400,
                "rarity": 0.5
            },
            
            # Content Creation Badges
            {
                "id": "content_creator",
                "name": "Content Creator",
                "description": "Generate your first AI-powered learning content",
                "type": BadgeType.CONTENT_CREATION,
                "tier": BadgeTier.BRONZE,
                "icon": "📝",
                "requirements": {"content_generated": 1},
                "points": 60,
                "rarity": 0.25
            },
            {
                "id": "content_master",
                "name": "Content Master",
                "description": "Generate 50 pieces of high-quality learning content",
                "type": BadgeType.CONTENT_CREATION,
                "tier": BadgeTier.GOLD,
                "icon": "📚",
                "requirements": {"content_generated": 50, "quality_threshold": 0.8},
                "points": 600,
                "rarity": 0.7
            },
            
            # Social Engagement Badges
            {
                "id": "team_player",
                "name": "Team Player",
                "description": "Join your first study group",
                "type": BadgeType.SOCIAL_ENGAGEMENT,
                "tier": BadgeTier.BRONZE,
                "icon": "👥",
                "requirements": {"study_groups_joined": 1},
                "points": 50,
                "rarity": 0.3
            },
            {
                "id": "collaboration_expert",
                "name": "Collaboration Expert",
                "description": "Successfully complete 10 group learning activities",
                "type": BadgeType.COLLABORATION,
                "tier": BadgeTier.SILVER,
                "icon": "🤝",
                "requirements": {"group_activities_completed": 10},
                "points": 250,
                "rarity": 0.5
            },
            
            # Special Achievement Badges
            {
                "id": "innovation_pioneer",
                "name": "Innovation Pioneer",
                "description": "Be among the first 100 users to try a new feature",
                "type": BadgeType.INNOVATION,
                "tier": BadgeTier.PLATINUM,
                "icon": "🚀",
                "requirements": {"early_adopter": True},
                "points": 200,
                "rarity": 0.9
            },
            {
                "id": "pathwayiq_champion",
                "name": "PathwayIQ Champion",
                "description": "Earn 10 different badges and score in top 10% of users",
                "type": BadgeType.DEDICATION,
                "tier": BadgeTier.DIAMOND,
                "icon": "👑",
                "requirements": {"badges_earned": 10, "percentile_rank": 0.1},
                "points": 1000,
                "rarity": 0.95
            }
        ]
        
        for badge_data in default_badges:
            badge = BadgeDefinition(
                created_at=datetime.now(timezone.utc),
                **badge_data
            )
            
            # Store in database
            existing = await self.db.badge_definitions.find_one({"id": badge.id})
            if not existing:
                await self.db.badge_definitions.insert_one(badge.dict())
                
            # Store in memory for quick access
            self.badge_definitions[badge.id] = badge
            
        logger.info(f"Initialized {len(default_badges)} badge definitions")
    
    async def check_user_achievements(self, user_id: str, event_data: Dict[str, Any]):
        """Check and update user achievements based on event data"""
        try:
            # Get all badge definitions
            badges = await self.db.badge_definitions.find({"active": True}).to_list(None)
            
            achievements_unlocked = []
            achievements_progressed = []
            
            for badge_data in badges:
                badge = BadgeDefinition(**badge_data)
                
                # Get or create user achievement record
                user_achievement = await self.db.user_achievements.find_one({
                    "user_id": user_id,
                    "badge_id": badge.id
                })
                
                if not user_achievement:
                    # Create new achievement record
                    user_achievement = UserAchievement(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        badge_id=badge.id,
                        status=AchievementStatus.LOCKED,
                        created_at=datetime.now(timezone.utc)
                    )
                    await self.db.user_achievements.insert_one(user_achievement.dict())
                else:
                    user_achievement = UserAchievement(**user_achievement)
                
                # Skip if already completed
                if user_achievement.status == AchievementStatus.COMPLETED:
                    continue
                
                # Check if prerequisites are met
                if badge.prerequisites:
                    prereqs_met = await self._check_prerequisites(user_id, badge.prerequisites)
                    if not prereqs_met:
                        continue
                
                # Update progress based on badge requirements
                progress_updated, is_completed = await self._update_badge_progress(
                    user_id, badge, user_achievement, event_data
                )
                
                if is_completed:
                    achievements_unlocked.append(badge)
                    await self._complete_achievement(user_id, badge, user_achievement)
                elif progress_updated:
                    achievements_progressed.append((badge, user_achievement))
                    await self._update_achievement_progress(user_achievement)
            
            # Send notifications for achievements
            await self._send_achievement_notifications(user_id, achievements_unlocked, achievements_progressed)
            
            return {
                "unlocked": len(achievements_unlocked),
                "progressed": len(achievements_progressed),
                "badges_unlocked": [badge.dict() for badge in achievements_unlocked]
            }
            
        except Exception as e:
            logger.error(f"Error checking user achievements: {str(e)}")
            return {"error": str(e)}
    
    async def _check_prerequisites(self, user_id: str, prerequisites: List[str]) -> bool:
        """Check if user has completed prerequisite badges"""
        for prereq_badge_id in prerequisites:
            achievement = await self.db.user_achievements.find_one({
                "user_id": user_id,
                "badge_id": prereq_badge_id,
                "status": AchievementStatus.COMPLETED
            })
            if not achievement:
                return False
        return True
    
    async def _update_badge_progress(
        self, 
        user_id: str, 
        badge: BadgeDefinition, 
        user_achievement: UserAchievement, 
        event_data: Dict[str, Any]
    ) -> tuple[bool, bool]:
        """Update badge progress and check completion"""
        progress_updated = False
        is_completed = False
        
        # Get user statistics for evaluation
        user_stats = await self._get_user_statistics(user_id)
        
        # Combine event data with user stats
        evaluation_data = {**user_stats, **event_data}
        
        # Check each requirement
        all_requirements_met = True
        total_requirements = len(badge.requirements)
        met_requirements = 0
        
        for requirement, threshold in badge.requirements.items():
            current_value = evaluation_data.get(requirement, 0)
            
            if isinstance(threshold, (int, float)):
                if current_value >= threshold:
                    met_requirements += 1
                    user_achievement.progress[requirement] = {
                        "current": current_value,
                        "required": threshold,
                        "completed": True
                    }
                else:
                    all_requirements_met = False
                    user_achievement.progress[requirement] = {
                        "current": current_value,
                        "required": threshold,
                        "completed": False
                    }
            elif isinstance(threshold, bool):
                if current_value == threshold:
                    met_requirements += 1
                    user_achievement.progress[requirement] = {
                        "current": current_value,
                        "required": threshold,
                        "completed": True
                    }
                else:
                    all_requirements_met = False
                    user_achievement.progress[requirement] = {
                        "current": current_value,
                        "required": threshold,
                        "completed": False
                    }
        
        # Update progress percentage
        new_percentage = (met_requirements / total_requirements) * 100
        
        if new_percentage != user_achievement.progress_percentage:
            progress_updated = True
            user_achievement.progress_percentage = new_percentage
            
            # Update status
            if all_requirements_met:
                is_completed = True
                user_achievement.status = AchievementStatus.COMPLETED
                user_achievement.completed_at = datetime.now(timezone.utc)
            elif new_percentage > 0:
                user_achievement.status = AchievementStatus.IN_PROGRESS
        
        return progress_updated, is_completed
    
    async def _get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics for achievement evaluation"""
        try:
            # Assessment statistics
            assessment_stats = await self._get_assessment_statistics(user_id)
            
            # Think-aloud statistics
            think_aloud_stats = await self._get_think_aloud_statistics(user_id)
            
            # Content generation statistics
            content_stats = await self._get_content_generation_statistics(user_id)
            
            # Social engagement statistics
            social_stats = await self._get_social_statistics(user_id)
            
            # Combine all statistics
            return {
                **assessment_stats,
                **think_aloud_stats,
                **content_stats,
                **social_stats
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {}
    
    async def _get_assessment_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get assessment-related statistics"""
        # Count total assessments completed
        total_assessments = await self.db.assessment_sessions.count_documents({
            "user_id": user_id,
            "status": "completed"
        })
        
        # Get assessment results for scoring analysis
        assessment_results = await self.db.assessment_sessions.find({
            "user_id": user_id,
            "status": "completed",
            "final_score": {"$exists": True}
        }).to_list(None)
        
        # Calculate performance metrics
        scores = [result.get("final_score", 0) for result in assessment_results]
        perfect_scores = sum(1 for score in scores if score >= 1.0)
        high_scores = sum(1 for score in scores if score >= 0.85)
        
        # Calculate streaks
        consecutive_days = await self._calculate_consecutive_learning_days(user_id)
        consecutive_high_scores = await self._calculate_consecutive_high_scores(user_id, 0.85)
        
        return {
            "assessments_completed": total_assessments,
            "perfect_scores": perfect_scores,
            "high_scores_count": high_scores,
            "consecutive_days": consecutive_days,
            "consecutive_high_scores": consecutive_high_scores,
            "average_score": sum(scores) / len(scores) if scores else 0
        }
    
    async def _get_think_aloud_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get think-aloud assessment statistics"""
        think_aloud_count = await self.db.think_aloud_sessions.count_documents({
            "user_id": user_id,
            "status": "completed"
        })
        
        # Get think-aloud sessions with analysis
        sessions_with_analysis = await self.db.think_aloud_sessions.find({
            "user_id": user_id,
            "status": "completed",
            "summary.session_effectiveness": {"$exists": True}
        }).to_list(None)
        
        # Calculate clarity score average
        clarity_scores = []
        for session in sessions_with_analysis:
            effectiveness = session.get("summary", {}).get("session_effectiveness", 3)
            clarity_scores.append(effectiveness / 5.0)  # Normalize to 0-1
        
        average_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
        
        return {
            "think_aloud_completed": think_aloud_count,
            "clarity_score": average_clarity
        }
    
    async def _get_content_generation_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get content generation statistics"""
        total_content = await self.db.generated_content.count_documents({
            "user_id": user_id
        })
        
        # Get high-quality content count
        high_quality_content = await self.db.generated_content.count_documents({
            "user_id": user_id,
            "quality_score": {"$gte": 0.8}
        })
        
        return {
            "content_generated": total_content,
            "high_quality_content": high_quality_content,
            "quality_threshold": high_quality_content / total_content if total_content > 0 else 0
        }
    
    async def _get_social_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get social engagement statistics"""
        # Note: These will be implemented when social features are added
        return {
            "study_groups_joined": 0,
            "group_activities_completed": 0,
            "social_interactions": 0
        }
    
    async def _calculate_consecutive_learning_days(self, user_id: str) -> int:
        """Calculate consecutive days of learning activity"""
        try:
            # Get assessment sessions ordered by date
            sessions = await self.db.assessment_sessions.find({
                "user_id": user_id,
                "status": "completed"
            }).sort("created_at", -1).to_list(None)
            
            if not sessions:
                return 0
            
            # Group by date and count consecutive days
            session_dates = set()
            for session in sessions:
                date_only = session.get("created_at", datetime.now()).date()
                session_dates.add(date_only)
            
            # Sort dates in descending order
            sorted_dates = sorted(session_dates, reverse=True)
            
            # Count consecutive days from most recent
            consecutive_days = 0
            current_date = datetime.now().date()
            
            for session_date in sorted_dates:
                days_diff = (current_date - session_date).days
                if days_diff == consecutive_days:
                    consecutive_days += 1
                else:
                    break
            
            return consecutive_days
        except Exception as e:
            logger.error(f"Error calculating consecutive learning days: {str(e)}")
            return 0
    
    async def _calculate_consecutive_high_scores(self, user_id: str, threshold: float) -> int:
        """Calculate consecutive high scores"""
        try:
            # Get recent assessment results ordered by date
            results = await self.db.assessment_sessions.find({
                "user_id": user_id,
                "status": "completed",
                "final_score": {"$exists": True}
            }).sort("created_at", -1).to_list(20)  # Last 20 assessments
            
            consecutive_count = 0
            for result in results:
                score = result.get("final_score", 0)
                if score >= threshold:
                    consecutive_count += 1
                else:
                    break
            
            return consecutive_count
        except Exception as e:
            logger.error(f"Error calculating consecutive high scores: {str(e)}")
            return 0
    
    async def _complete_achievement(self, user_id: str, badge: BadgeDefinition, user_achievement: UserAchievement):
        """Complete an achievement and award points"""
        try:
            # Update achievement status
            await self.db.user_achievements.update_one(
                {"id": user_achievement.id},
                {
                    "$set": {
                        "status": AchievementStatus.COMPLETED,
                        "completed_at": datetime.now(timezone.utc),
                        "progress": user_achievement.progress,
                        "progress_percentage": 100.0
                    }
                }
            )
            
            # Award points to user
            await self._award_points(user_id, badge.points, f"Badge earned: {badge.name}")
            
            logger.info(f"Achievement completed: {badge.name} for user {user_id}")
        except Exception as e:
            logger.error(f"Error completing achievement: {str(e)}")
    
    async def _update_achievement_progress(self, user_achievement: UserAchievement):
        """Update achievement progress in database"""
        try:
            await self.db.user_achievements.update_one(
                {"id": user_achievement.id},
                {
                    "$set": {
                        "status": user_achievement.status,
                        "progress": user_achievement.progress,
                        "progress_percentage": user_achievement.progress_percentage
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating achievement progress: {str(e)}")
    
    async def _award_points(self, user_id: str, points: int, reason: str):
        """Award points to user and update leaderboard"""
        try:
            # Update user points
            await self.db.users.update_one(
                {"id": user_id},
                {"$inc": {"total_points": points}}
            )
            
            # Create points transaction record
            transaction = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "points": points,
                "reason": reason,
                "type": "badge_earned",
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.points_transactions.insert_one(transaction)
            
            # Update leaderboard
            await self._update_leaderboard(user_id)
            
        except Exception as e:
            logger.error(f"Error awarding points: {str(e)}")
    
    async def _update_leaderboard(self, user_id: str):
        """Update user position in leaderboard"""
        try:
            # Get user's total points
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                return
            
            total_points = user.get("total_points", 0)
            
            # Update or create leaderboard entry
            await self.db.leaderboard_entries.update_one(
                {"user_id": user_id, "category": "overall"},
                {
                    "$set": {
                        "user_id": user_id,
                        "username": user.get("username", "Unknown"),
                        "category": "overall",
                        "score": total_points,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating leaderboard: {str(e)}")
    
    async def _send_achievement_notifications(
        self, 
        user_id: str, 
        unlocked_badges: List[BadgeDefinition], 
        progressed_badges: List[tuple]
    ):
        """Send notifications for achievement updates"""
        try:
            notifications = []
            
            # Create notifications for unlocked badges
            for badge in unlocked_badges:
                notification = AchievementNotification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    badge_id=badge.id,
                    type="completed",
                    message=f"🎉 Achievement Unlocked: {badge.name}! You earned {badge.points} points.",
                    created_at=datetime.now(timezone.utc)
                )
                notifications.append(notification.dict())
            
            # Create notifications for progressed badges (milestone progress)
            for badge, user_achievement in progressed_badges:
                if user_achievement.progress_percentage in [25, 50, 75]:  # Milestone notifications
                    notification = AchievementNotification(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        badge_id=badge.id,
                        type="progress",
                        message=f"📈 Progress Update: {badge.name} - {int(user_achievement.progress_percentage)}% complete!",
                        created_at=datetime.now(timezone.utc)
                    )
                    notifications.append(notification.dict())
            
            if notifications:
                await self.db.achievement_notifications.insert_many(notifications)
                
        except Exception as e:
            logger.error(f"Error sending achievement notifications: {str(e)}")
    
    async def get_user_badges(self, user_id: str) -> Dict[str, Any]:
        """Get all badges for a user"""
        try:
            # Get user achievements
            achievements = await self.db.user_achievements.find({
                "user_id": user_id
            }).to_list(None)
            
            # Get badge definitions
            badge_ids = [ach["badge_id"] for ach in achievements]
            badges = await self.db.badge_definitions.find({
                "id": {"$in": badge_ids}
            }).to_list(None)
            
            # Create badge lookup
            badge_lookup = {badge["id"]: badge for badge in badges}
            
            # Combine achievements with badge data
            user_badges = []
            for achievement in achievements:
                badge_data = badge_lookup.get(achievement["badge_id"])
                if badge_data:
                    user_badges.append({
                        "badge": badge_data,
                        "achievement": achievement
                    })
            
            # Get user stats
            user = await self.db.users.find_one({"id": user_id})
            total_points = user.get("total_points", 0) if user else 0
            
            return {
                "badges": user_badges,
                "total_badges": len(user_badges),
                "completed_badges": len([b for b in user_badges if b["achievement"]["status"] == "completed"]),
                "total_points": total_points
            }
            
        except Exception as e:
            logger.error(f"Error getting user badges: {str(e)}")
            return {"badges": [], "total_badges": 0, "completed_badges": 0, "total_points": 0}
    
    async def get_achievement_notifications(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent achievement notifications for a user"""
        try:
            notifications = await self.db.achievement_notifications.find({
                "user_id": user_id
            }).sort("created_at", -1).limit(limit).to_list(limit)
            
            return notifications
        except Exception as e:
            logger.error(f"Error getting achievement notifications: {str(e)}")
            return []
    
    async def mark_notifications_read(self, user_id: str, notification_ids: List[str] = None):
        """Mark notifications as read"""
        try:
            query = {"user_id": user_id}
            if notification_ids:
                query["id"] = {"$in": notification_ids}
            
            await self.db.achievement_notifications.update_many(
                query,
                {"$set": {"read": True}}
            )
        except Exception as e:
            logger.error(f"Error marking notifications as read: {str(e)}")

# Global gamification engine instance
gamification_engine = None

def get_gamification_engine(db: AsyncIOMotorDatabase) -> GamificationEngine:
    """Get gamification engine instance"""
    global gamification_engine
    if gamification_engine is None:
        gamification_engine = GamificationEngine(db)
    return gamification_engine