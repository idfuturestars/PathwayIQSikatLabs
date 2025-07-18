"""
Leaderboard System - Competitive Elements and Rankings
Real-time leaderboards, competitions, and social rankings
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)

class LeaderboardCategory(str, Enum):
    """Leaderboard categories"""
    OVERALL = "overall"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SUBJECT_MATH = "subject_math"
    SUBJECT_SCIENCE = "subject_science"
    SUBJECT_ENGLISH = "subject_english"
    SUBJECT_HISTORY = "subject_history"
    THINK_ALOUD = "think_aloud"
    CONTENT_CREATION = "content_creation"
    ASSESSMENT_SPEED = "assessment_speed"
    STREAK = "streak"
    BADGES = "badges"

class CompetitionType(str, Enum):
    """Competition types"""
    DAILY_CHALLENGE = "daily_challenge"
    WEEKLY_TOURNAMENT = "weekly_tournament"
    MONTHLY_CHAMPIONSHIP = "monthly_championship"
    SUBJECT_SHOWDOWN = "subject_showdown"
    TEAM_COMPETITION = "team_competition"

class CompetitionStatus(str, Enum):
    """Competition status"""
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LeaderboardEntry(BaseModel):
    """Leaderboard entry model"""
    id: str
    user_id: str
    username: str
    category: LeaderboardCategory
    score: float
    rank: int = 0
    previous_rank: int = 0
    rank_change: int = 0
    additional_data: Dict[str, Any] = {}
    updated_at: datetime = None

class Competition(BaseModel):
    """Competition model"""
    id: str
    name: str
    description: str
    type: CompetitionType
    category: LeaderboardCategory
    status: CompetitionStatus
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    entry_requirements: Dict[str, Any] = {}
    prizes: Dict[str, Any] = {}
    rules: List[str] = []
    participants: List[str] = []
    leaderboard: List[LeaderboardEntry] = []
    created_at: datetime = None

class LeaderboardSystem:
    """Main leaderboard and competition system"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_competitions = {}
        
    async def initialize(self):
        """Initialize the leaderboard system"""
        await self._create_database_indexes()
        await self._create_default_competitions()
        await self._refresh_all_leaderboards()
        
    async def _create_database_indexes(self):
        """Create database indexes for performance"""
        try:
            # Leaderboard indexes
            await self.db.leaderboard_entries.create_index([("category", 1), ("score", -1)])
            await self.db.leaderboard_entries.create_index([("user_id", 1), ("category", 1)], unique=True)
            await self.db.leaderboard_entries.create_index([("updated_at", -1)])
            
            # Competition indexes
            await self.db.competitions.create_index([("status", 1), ("start_date", 1)])
            await self.db.competitions.create_index([("type", 1), ("category", 1)])
            await self.db.competitions.create_index([("end_date", 1)])
            
            logger.info("Leaderboard database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating database indexes: {str(e)}")
    
    async def _create_default_competitions(self):
        """Create default recurring competitions"""
        try:
            # Daily Challenge
            daily_challenge = Competition(
                id="daily_challenge",
                name="Daily Learning Challenge",
                description="Complete as many assessments as possible in one day!",
                type=CompetitionType.DAILY_CHALLENGE,
                category=LeaderboardCategory.OVERALL,
                status=CompetitionStatus.ACTIVE,
                start_date=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999),
                max_participants=None,
                entry_requirements={},
                prizes={
                    "1st": {"points": 500, "badge": "daily_champion"},
                    "2nd": {"points": 300, "badge": "daily_runner_up"},
                    "3rd": {"points": 200, "badge": "daily_bronze"}
                },
                rules=[
                    "Complete adaptive assessments to earn points",
                    "Higher scores earn more points",
                    "Competition resets daily at midnight UTC"
                ],
                created_at=datetime.now(timezone.utc)
            )
            
            # Weekly Tournament
            week_start = datetime.now(timezone.utc) - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
            
            weekly_tournament = Competition(
                id="weekly_tournament",
                name="Weekly Learning Tournament",
                description="Compete with learners worldwide in this week-long challenge!",
                type=CompetitionType.WEEKLY_TOURNAMENT,
                category=LeaderboardCategory.WEEKLY,
                status=CompetitionStatus.ACTIVE,
                start_date=week_start,
                end_date=week_end,
                max_participants=1000,
                entry_requirements={"assessments_completed": 5},
                prizes={
                    "1st": {"points": 2000, "badge": "weekly_champion"},
                    "2nd": {"points": 1500, "badge": "weekly_runner_up"},
                    "3rd": {"points": 1000, "badge": "weekly_bronze"},
                    "top_10": {"points": 500, "badge": "weekly_top_10"}
                },
                rules=[
                    "Must complete at least 5 assessments to qualify",
                    "Points awarded based on assessment performance",
                    "Bonus points for consistency and improvement"
                ],
                created_at=datetime.now(timezone.utc)
            )
            
            # Monthly Championship
            month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(seconds=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(seconds=1)
            
            monthly_championship = Competition(
                id="monthly_championship",
                name="Monthly PathwayIQ Championship",
                description="The ultimate monthly challenge for dedicated learners!",
                type=CompetitionType.MONTHLY_CHAMPIONSHIP,
                category=LeaderboardCategory.MONTHLY,
                status=CompetitionStatus.ACTIVE,
                start_date=month_start,
                end_date=month_end,
                max_participants=5000,
                entry_requirements={"assessments_completed": 20, "badges_earned": 3},
                prizes={
                    "1st": {"points": 10000, "badge": "monthly_champion", "special": "Golden PathwayIQ Trophy"},
                    "2nd": {"points": 7500, "badge": "monthly_runner_up", "special": "Silver PathwayIQ Trophy"},
                    "3rd": {"points": 5000, "badge": "monthly_bronze", "special": "Bronze PathwayIQ Trophy"},
                    "top_25": {"points": 2000, "badge": "monthly_elite"}
                },
                rules=[
                    "Must complete at least 20 assessments to qualify",
                    "Must have earned at least 3 badges",
                    "Points from all activities count toward ranking",
                    "Special recognition for most improved learner"
                ],
                created_at=datetime.now(timezone.utc)
            )
            
            competitions = [daily_challenge, weekly_tournament, monthly_championship]
            
            for competition in competitions:
                existing = await self.db.competitions.find_one({"id": competition.id})
                if not existing:
                    await self.db.competitions.insert_one(competition.dict())
                    self.active_competitions[competition.id] = competition
                    
            logger.info(f"Initialized {len(competitions)} default competitions")
            
        except Exception as e:
            logger.error(f"Error creating default competitions: {str(e)}")
    
    async def update_user_score(self, user_id: str, category: LeaderboardCategory, score_data: Dict[str, Any]):
        """Update user's score in a specific leaderboard category"""
        try:
            # Get user info
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                return
            
            username = user.get("username", "Unknown")
            
            # Calculate score based on category
            score = await self._calculate_category_score(user_id, category, score_data)
            
            # Get current entry
            current_entry = await self.db.leaderboard_entries.find_one({
                "user_id": user_id,
                "category": category
            })
            
            if current_entry:
                # Update existing entry
                await self.db.leaderboard_entries.update_one(
                    {"user_id": user_id, "category": category},
                    {
                        "$set": {
                            "score": score,
                            "additional_data": score_data,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
            else:
                # Create new entry
                entry = LeaderboardEntry(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    username=username,
                    category=category,
                    score=score,
                    additional_data=score_data,
                    updated_at=datetime.now(timezone.utc)
                )
                await self.db.leaderboard_entries.insert_one(entry.dict())
            
            # Update rankings for this category
            await self._update_category_rankings(category)
            
            # Update competition leaderboards
            await self._update_competition_leaderboards(user_id, category, score)
            
        except Exception as e:
            logger.error(f"Error updating user score: {str(e)}")
    
    async def _calculate_category_score(self, user_id: str, category: LeaderboardCategory, score_data: Dict[str, Any]) -> float:
        """Calculate score for a specific leaderboard category"""
        try:
            if category == LeaderboardCategory.OVERALL:
                # Overall score based on total points
                user = await self.db.users.find_one({"id": user_id})
                return user.get("total_points", 0) if user else 0
            
            elif category == LeaderboardCategory.WEEKLY:
                # Weekly score based on recent activity
                week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                weekly_assessments = await self.db.assessment_sessions.find({
                    "user_id": user_id,
                    "created_at": {"$gte": week_ago},
                    "status": "completed"
                }).to_list(None)
                
                total_score = 0
                for assessment in weekly_assessments:
                    score = assessment.get("final_score", 0)
                    total_score += score * 100  # Convert to points
                
                return total_score
            
            elif category == LeaderboardCategory.MONTHLY:
                # Monthly score based on recent activity
                month_ago = datetime.now(timezone.utc) - timedelta(days=30)
                monthly_assessments = await self.db.assessment_sessions.find({
                    "user_id": user_id,
                    "created_at": {"$gte": month_ago},
                    "status": "completed"
                }).to_list(None)
                
                total_score = 0
                for assessment in monthly_assessments:
                    score = assessment.get("final_score", 0)
                    total_score += score * 100
                
                return total_score
            
            elif category == LeaderboardCategory.THINK_ALOUD:
                # Think-aloud score based on sessions and quality
                sessions = await self.db.think_aloud_sessions.find({
                    "user_id": user_id,
                    "status": "completed"
                }).to_list(None)
                
                total_score = 0
                for session in sessions:
                    effectiveness = session.get("summary", {}).get("session_effectiveness", 3)
                    total_score += effectiveness * 20  # Convert to points
                
                return total_score
            
            elif category == LeaderboardCategory.CONTENT_CREATION:
                # Content creation score
                content_items = await self.db.generated_content.find({
                    "user_id": user_id
                }).to_list(None)
                
                total_score = 0
                for item in content_items:
                    quality = item.get("quality_score", 0.5)
                    total_score += quality * 100
                
                return total_score
            
            elif category == LeaderboardCategory.ASSESSMENT_SPEED:
                # Assessment speed score (inverse of average time)
                assessments = await self.db.assessment_sessions.find({
                    "user_id": user_id,
                    "status": "completed",
                    "completion_time": {"$exists": True}
                }).to_list(None)
                
                if not assessments:
                    return 0
                
                total_time = sum(a.get("completion_time", 0) for a in assessments)
                avg_time = total_time / len(assessments)
                
                # Convert to speed score (faster = higher score)
                return 10000 / (avg_time + 1)  # +1 to avoid division by zero
            
            elif category == LeaderboardCategory.STREAK:
                # Streak score based on consecutive days
                return score_data.get("consecutive_days", 0) * 10
            
            elif category == LeaderboardCategory.BADGES:
                # Badge score based on badges earned
                badges_count = await self.db.user_achievements.count_documents({
                    "user_id": user_id,
                    "status": "completed"
                })
                return badges_count * 50
            
            else:
                return score_data.get("score", 0)
                
        except Exception as e:
            logger.error(f"Error calculating category score: {str(e)}")
            return 0
    
    async def _update_category_rankings(self, category: LeaderboardCategory):
        """Update rankings for a specific category"""
        try:
            # Get all entries for this category, sorted by score
            entries = await self.db.leaderboard_entries.find({
                "category": category
            }).sort("score", -1).to_list(None)
            
            # Update ranks
            for i, entry in enumerate(entries):
                new_rank = i + 1
                previous_rank = entry.get("rank", 0)
                rank_change = previous_rank - new_rank if previous_rank > 0 else 0
                
                await self.db.leaderboard_entries.update_one(
                    {"id": entry["id"]},
                    {
                        "$set": {
                            "rank": new_rank,
                            "previous_rank": previous_rank,
                            "rank_change": rank_change
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Error updating category rankings: {str(e)}")
    
    async def _update_competition_leaderboards(self, user_id: str, category: LeaderboardCategory, score: float):
        """Update competition leaderboards"""
        try:
            # Find active competitions for this category
            competitions = await self.db.competitions.find({
                "status": CompetitionStatus.ACTIVE,
                "category": category
            }).to_list(None)
            
            for comp_data in competitions:
                competition = Competition(**comp_data)
                
                # Check if user meets entry requirements
                if await self._check_competition_requirements(user_id, competition.entry_requirements):
                    # Add user to participants if not already there
                    if user_id not in competition.participants:
                        competition.participants.append(user_id)
                        
                        # Update competition in database
                        await self.db.competitions.update_one(
                            {"id": competition.id},
                            {"$addToSet": {"participants": user_id}}
                        )
                
        except Exception as e:
            logger.error(f"Error updating competition leaderboards: {str(e)}")
    
    async def _check_competition_requirements(self, user_id: str, requirements: Dict[str, Any]) -> bool:
        """Check if user meets competition entry requirements"""
        try:
            for requirement, threshold in requirements.items():
                if requirement == "assessments_completed":
                    count = await self.db.assessment_sessions.count_documents({
                        "user_id": user_id,
                        "status": "completed"
                    })
                    if count < threshold:
                        return False
                        
                elif requirement == "badges_earned":
                    count = await self.db.user_achievements.count_documents({
                        "user_id": user_id,
                        "status": "completed"
                    })
                    if count < threshold:
                        return False
                        
                elif requirement == "minimum_score":
                    user = await self.db.users.find_one({"id": user_id})
                    if not user or user.get("total_points", 0) < threshold:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking competition requirements: {str(e)}")
            return False
    
    async def get_leaderboard(self, category: LeaderboardCategory, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get leaderboard for a specific category"""
        try:
            # Get leaderboard entries
            entries = await self.db.leaderboard_entries.find({
                "category": category
            }).sort("rank", 1).skip(offset).limit(limit).to_list(limit)
            
            # Get total count
            total_entries = await self.db.leaderboard_entries.count_documents({
                "category": category
            })
            
            return {
                "category": category,
                "entries": entries,
                "total_entries": total_entries,
                "page": offset // limit + 1,
                "per_page": limit
            }
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return {"category": category, "entries": [], "total_entries": 0}
    
    async def get_user_ranking(self, user_id: str, category: LeaderboardCategory) -> Dict[str, Any]:
        """Get user's ranking in a specific category"""
        try:
            entry = await self.db.leaderboard_entries.find_one({
                "user_id": user_id,
                "category": category
            })
            
            if not entry:
                return {
                    "category": category,
                    "rank": None,
                    "score": 0,
                    "total_participants": 0
                }
            
            total_participants = await self.db.leaderboard_entries.count_documents({
                "category": category
            })
            
            return {
                "category": category,
                "rank": entry.get("rank", 0),
                "score": entry.get("score", 0),
                "rank_change": entry.get("rank_change", 0),
                "total_participants": total_participants,
                "percentile": (1 - (entry.get("rank", 1) / total_participants)) * 100 if total_participants > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user ranking: {str(e)}")
            return {"category": category, "rank": None, "score": 0, "total_participants": 0}
    
    async def get_active_competitions(self) -> List[Dict[str, Any]]:
        """Get all active competitions"""
        try:
            competitions = await self.db.competitions.find({
                "status": CompetitionStatus.ACTIVE
            }).to_list(None)
            
            return competitions
            
        except Exception as e:
            logger.error(f"Error getting active competitions: {str(e)}")
            return []
    
    async def get_competition_leaderboard(self, competition_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get leaderboard for a specific competition"""
        try:
            competition = await self.db.competitions.find_one({"id": competition_id})
            if not competition:
                return {"error": "Competition not found"}
            
            # Get leaderboard entries for competition category
            entries = await self.db.leaderboard_entries.find({
                "category": competition["category"],
                "user_id": {"$in": competition["participants"]}
            }).sort("rank", 1).limit(limit).to_list(limit)
            
            return {
                "competition": competition,
                "leaderboard": entries,
                "total_participants": len(competition["participants"])
            }
            
        except Exception as e:
            logger.error(f"Error getting competition leaderboard: {str(e)}")
            return {"error": str(e)}
    
    async def _refresh_all_leaderboards(self):
        """Refresh all leaderboard rankings"""
        try:
            categories = [category.value for category in LeaderboardCategory]
            for category in categories:
                await self._update_category_rankings(category)
                
            logger.info("All leaderboards refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing leaderboards: {str(e)}")
    
    async def join_competition(self, user_id: str, competition_id: str) -> Dict[str, Any]:
        """Join a competition"""
        try:
            competition = await self.db.competitions.find_one({"id": competition_id})
            if not competition:
                return {"success": False, "error": "Competition not found"}
            
            competition_obj = Competition(**competition)
            
            # Check if competition is active
            if competition_obj.status != CompetitionStatus.ACTIVE:
                return {"success": False, "error": "Competition is not active"}
            
            # Check if user already joined
            if user_id in competition_obj.participants:
                return {"success": False, "error": "Already joined this competition"}
            
            # Check max participants
            if competition_obj.max_participants and len(competition_obj.participants) >= competition_obj.max_participants:
                return {"success": False, "error": "Competition is full"}
            
            # Check entry requirements
            if not await self._check_competition_requirements(user_id, competition_obj.entry_requirements):
                return {"success": False, "error": "Entry requirements not met"}
            
            # Add user to competition
            await self.db.competitions.update_one(
                {"id": competition_id},
                {"$addToSet": {"participants": user_id}}
            )
            
            return {"success": True, "message": "Successfully joined competition"}
            
        except Exception as e:
            logger.error(f"Error joining competition: {str(e)}")
            return {"success": False, "error": str(e)}

# Global leaderboard system instance
leaderboard_system = None

def get_leaderboard_system(db: AsyncIOMotorDatabase) -> LeaderboardSystem:
    """Get leaderboard system instance"""
    global leaderboard_system
    if leaderboard_system is None:
        leaderboard_system = LeaderboardSystem(db)
    return leaderboard_system