"""
IDFS PathwayIQ™ Gamification Engine - Phase 2
Complete gamification system with:
- Comprehensive Badge & Achievement System
- Leaderboards & Competitive Elements
- Study Groups & Collaborative Learning
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class BadgeType(str, Enum):
    ACHIEVEMENT = "achievement"
    SKILL_MASTERY = "skill_mastery"
    PARTICIPATION = "participation"
    COLLABORATION = "collaboration"
    STREAK = "streak"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"

class BadgeRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class CompetitionType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    CUSTOM = "custom"

class StudyGroupRole(str, Enum):
    LEADER = "leader"
    MODERATOR = "moderator"
    MEMBER = "member"
    GUEST = "guest"

class Badge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str
    badge_type: BadgeType
    rarity: BadgeRarity
    criteria: Dict[str, Any]
    points: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    category: str = "general"
    prerequisites: List[str] = []

class UserBadge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_id: str
    earned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: Dict[str, Any] = {}
    progress: float = 1.0  # 0.0 to 1.0
    is_featured: bool = False

class Competition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    competition_type: CompetitionType
    start_date: datetime
    end_date: datetime
    rules: Dict[str, Any]
    prizes: List[Dict[str, Any]]
    participants: List[str] = []
    is_active: bool = True
    created_by: str

class StudyGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    subject: str
    leader_id: str
    members: List[Dict[str, Any]] = []  # {user_id, role, joined_at}
    max_members: int = 20
    is_private: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    settings: Dict[str, Any] = {}
    activity_stats: Dict[str, Any] = {}

class GamificationEngine:
    def __init__(self):
        self.badge_definitions = self._initialize_badge_definitions()
        self.achievement_trackers = {}
        self.leaderboard_cache = {}
        self.competition_engine = CompetitionEngine()
        self.study_group_engine = StudyGroupEngine()
        
    def _initialize_badge_definitions(self) -> Dict[str, Badge]:
        """Initialize predefined badge definitions"""
        badges = {
            "first_login": Badge(
                name="Welcome Aboard!",
                description="First time logging into PathwayIQ",
                icon="👋",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.COMMON,
                criteria={"action": "first_login"},
                points=10,
                category="engagement"
            ),
            "streak_7": Badge(
                name="Week Warrior",
                description="7-day learning streak",
                icon="🔥",
                badge_type=BadgeType.STREAK,
                rarity=BadgeRarity.UNCOMMON,
                criteria={"streak_days": 7},
                points=50,
                category="consistency"
            ),
            "streak_30": Badge(
                name="Monthly Master",
                description="30-day learning streak",
                icon="⚡",
                badge_type=BadgeType.STREAK,
                rarity=BadgeRarity.RARE,
                criteria={"streak_days": 30},
                points=200,
                category="consistency"
            ),
            "perfect_score": Badge(
                name="Perfectionist",
                description="Perfect score on assessment",
                icon="🎯",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.UNCOMMON,
                criteria={"perfect_score": True},
                points=75,
                category="excellence"
            ),
            "fast_learner": Badge(
                name="Speed Demon",
                description="Complete assessment in record time",
                icon="⚡",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.RARE,
                criteria={"time_percentile": 90},
                points=100,
                category="efficiency"
            ),
            "helper": Badge(
                name="Study Buddy",
                description="Help 5 fellow students",
                icon="🤝",
                badge_type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.UNCOMMON,
                criteria={"help_count": 5},
                points=60,
                category="social"
            ),
            "math_master": Badge(
                name="Math Virtuoso",
                description="Master mathematics concepts",
                icon="🧮",
                badge_type=BadgeType.SKILL_MASTERY,
                rarity=BadgeRarity.EPIC,
                criteria={"subject": "mathematics", "mastery_level": 0.9},
                points=250,
                category="subject_mastery"
            ),
            "group_leader": Badge(
                name="Team Captain",
                description="Lead a study group successfully",
                icon="👨‍💼",
                badge_type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.RARE,
                criteria={"study_group_leadership": True},
                points=150,
                category="leadership"
            ),
            "night_owl": Badge(
                name="Night Owl",
                description="Learning after midnight",
                icon="🦉",
                badge_type=BadgeType.PARTICIPATION,
                rarity=BadgeRarity.UNCOMMON,
                criteria={"night_learning": True},
                points=40,
                category="dedication"
            ),
            "early_bird": Badge(
                name="Early Bird",
                description="Learning before 6 AM",
                icon="🐦",
                badge_type=BadgeType.PARTICIPATION,
                rarity=BadgeRarity.UNCOMMON,
                criteria={"early_learning": True},
                points=40,
                category="dedication"
            )
        }
        
        return badges
    
    async def check_and_award_badges(self, user_id: str, action_data: Dict[str, Any]) -> List[UserBadge]:
        """Check if user qualifies for any badges and award them"""
        awarded_badges = []
        
        for badge_id, badge in self.badge_definitions.items():
            if await self._check_badge_criteria(user_id, badge, action_data):
                # Check if user already has this badge
                if not await self._user_has_badge(user_id, badge_id):
                    user_badge = UserBadge(
                        user_id=user_id,
                        badge_id=badge_id,
                        evidence=action_data
                    )
                    awarded_badges.append(user_badge)
                    await self._save_user_badge(user_badge)
        
        return awarded_badges
    
    async def _check_badge_criteria(self, user_id: str, badge: Badge, action_data: Dict[str, Any]) -> bool:
        """Check if user meets badge criteria"""
        criteria = badge.criteria
        
        # First login badge
        if criteria.get("action") == "first_login":
            return action_data.get("action") == "first_login"
        
        # Streak badges
        if "streak_days" in criteria:
            user_streak = await self._get_user_streak(user_id)
            return user_streak >= criteria["streak_days"]
        
        # Perfect score badge
        if criteria.get("perfect_score"):
            return action_data.get("score") == 100
        
        # Time-based badges
        if "time_percentile" in criteria:
            user_time = action_data.get("completion_time", 0)
            percentile = await self._calculate_time_percentile(user_time, action_data.get("subject"))
            return percentile >= criteria["time_percentile"]
        
        # Help count badge
        if "help_count" in criteria:
            help_count = await self._get_user_help_count(user_id)
            return help_count >= criteria["help_count"]
        
        # Subject mastery badges
        if "subject" in criteria and "mastery_level" in criteria:
            mastery = await self._get_subject_mastery(user_id, criteria["subject"])
            return mastery >= criteria["mastery_level"]
        
        # Time-based learning badges
        if criteria.get("night_learning"):
            current_hour = datetime.now().hour
            return current_hour >= 24 or current_hour < 6
        
        if criteria.get("early_learning"):
            current_hour = datetime.now().hour
            return current_hour < 6
        
        return False
    
    async def _user_has_badge(self, user_id: str, badge_id: str) -> bool:
        """Check if user already has a specific badge"""
        # This would query the database in real implementation
        return False
    
    async def _save_user_badge(self, user_badge: UserBadge):
        """Save user badge to database"""
        # This would save to database in real implementation
        pass
    
    async def _get_user_streak(self, user_id: str) -> int:
        """Get user's current learning streak"""
        # This would query user activity in real implementation
        return 1
    
    async def _calculate_time_percentile(self, completion_time: int, subject: str) -> float:
        """Calculate time percentile for completion time"""
        # This would calculate based on historical data
        return 75.0
    
    async def _get_user_help_count(self, user_id: str) -> int:
        """Get count of how many users this user has helped"""
        # This would query help/collaboration data
        return 0
    
    async def _get_subject_mastery(self, user_id: str, subject: str) -> float:
        """Get user's mastery level in a subject"""
        # This would calculate based on assessment results
        return 0.5
    
    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all badges for a user"""
        # This would query database for user badges
        return []
    
    async def get_badge_progress(self, user_id: str, badge_id: str) -> Dict[str, Any]:
        """Get progress towards a specific badge"""
        badge = self.badge_definitions.get(badge_id)
        if not badge:
            return {}
        
        # Calculate progress based on criteria
        progress = 0.0
        current_value = 0
        target_value = 0
        
        if "streak_days" in badge.criteria:
            current_streak = await self._get_user_streak(user_id)
            target_streak = badge.criteria["streak_days"]
            progress = min(current_streak / target_streak, 1.0)
            current_value = current_streak
            target_value = target_streak
        
        return {
            "badge_id": badge_id,
            "badge_name": badge.name,
            "progress": progress,
            "current_value": current_value,
            "target_value": target_value,
            "description": badge.description
        }

class CompetitionEngine:
    def __init__(self):
        self.active_competitions = {}
        self.leaderboards = {}
    
    async def create_competition(self, competition_data: Dict[str, Any]) -> Competition:
        """Create a new competition"""
        competition = Competition(**competition_data)
        self.active_competitions[competition.id] = competition
        return competition
    
    async def join_competition(self, competition_id: str, user_id: str) -> bool:
        """Join a competition"""
        if competition_id in self.active_competitions:
            competition = self.active_competitions[competition_id]
            if user_id not in competition.participants:
                competition.participants.append(user_id)
                return True
        return False
    
    async def get_competition_leaderboard(self, competition_id: str) -> List[Dict[str, Any]]:
        """Get leaderboard for a competition"""
        # This would calculate leaderboard based on competition rules
        return []
    
    async def get_global_leaderboard(self, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get global leaderboard"""
        # This would query user performance data
        return []

class StudyGroupEngine:
    def __init__(self):
        self.study_groups = {}
    
    async def create_study_group(self, group_data: Dict[str, Any]) -> StudyGroup:
        """Create a new study group"""
        study_group = StudyGroup(**group_data)
        self.study_groups[study_group.id] = study_group
        return study_group
    
    async def join_study_group(self, group_id: str, user_id: str) -> bool:
        """Join a study group"""
        if group_id in self.study_groups:
            group = self.study_groups[group_id]
            if len(group.members) < group.max_members:
                group.members.append({
                    "user_id": user_id,
                    "role": StudyGroupRole.MEMBER,
                    "joined_at": datetime.now(timezone.utc).isoformat()
                })
                return True
        return False
    
    async def get_study_group_activity(self, group_id: str) -> Dict[str, Any]:
        """Get study group activity and statistics"""
        if group_id not in self.study_groups:
            return {}
        
        group = self.study_groups[group_id]
        return {
            "group_id": group_id,
            "member_count": len(group.members),
            "activity_stats": group.activity_stats,
            "recent_activity": []  # Would be populated from database
        }
    
    async def get_user_study_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all study groups for a user"""
        user_groups = []
        for group_id, group in self.study_groups.items():
            for member in group.members:
                if member["user_id"] == user_id:
                    user_groups.append({
                        "group_id": group_id,
                        "name": group.name,
                        "role": member["role"],
                        "member_count": len(group.members)
                    })
        return user_groups

# Global instances
gamification_engine = GamificationEngine()
competition_engine = CompetitionEngine()
study_group_engine = StudyGroupEngine()