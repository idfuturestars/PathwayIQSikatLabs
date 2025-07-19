"""
Advanced Learning Analytics Engine
Comprehensive data analysis, visualization, and insights generation
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
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"

class MetricType(str, Enum):
    """Types of learning metrics"""
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    PROGRESS = "progress"
    TIME_ANALYSIS = "time_analysis"
    SKILL_MASTERY = "skill_mastery"
    BEHAVIORAL = "behavioral"

class AnalyticsRequest(BaseModel):
    """Request model for analytics queries"""
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY
    metric_types: List[MetricType] = []
    filters: Dict[str, Any] = {}

class LearningMetrics(BaseModel):
    """Comprehensive learning metrics model"""
    user_id: str
    timeframe: str
    performance_metrics: Dict[str, Any] = {}
    engagement_metrics: Dict[str, Any] = {}
    progress_metrics: Dict[str, Any] = {}
    time_metrics: Dict[str, Any] = {}
    skill_metrics: Dict[str, Any] = {}
    behavioral_metrics: Dict[str, Any] = {}
    calculated_at: datetime
    insights: List[str] = []
    recommendations: List[str] = []

class AnalyticsEngine:
    """Main analytics processing engine"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def initialize(self):
        """Initialize analytics database indexes"""
        await self._create_analytics_indexes()
        
    async def _create_analytics_indexes(self):
        """Create database indexes for analytics performance"""
        try:
            # Analytics data indexes
            await self.db.learning_analytics.create_index([("user_id", 1), ("timeframe", 1)])
            await self.db.learning_analytics.create_index([("calculated_at", -1)])
            
            # Performance aggregation indexes
            await self.db.assessment_sessions.create_index([("user_id", 1), ("created_at", -1)])
            await self.db.user_answers.create_index([("user_id", 1), ("created_at", -1)])
            await self.db.think_aloud_sessions.create_index([("user_id", 1), ("created_at", -1)])
            await self.db.generated_content.create_index([("user_id", 1), ("created_at", -1)])
            
            logger.info("Analytics database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating analytics indexes: {str(e)}")
    
    async def generate_user_analytics(
        self, 
        user_id: str, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY
    ) -> LearningMetrics:
        """Generate comprehensive analytics for a user"""
        
        try:
            # Calculate timeframe boundaries
            start_date, end_date = self._get_timeframe_boundaries(timeframe)
            
            # Gather all user data
            user_data = await self._gather_user_data(user_id, start_date, end_date)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(user_data)
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(user_data)
            
            # Calculate progress metrics
            progress_metrics = await self._calculate_progress_metrics(user_data)
            
            # Calculate time analysis metrics
            time_metrics = await self._calculate_time_metrics(user_data)
            
            # Calculate skill mastery metrics
            skill_metrics = await self._calculate_skill_metrics(user_data)
            
            # Calculate behavioral metrics
            behavioral_metrics = await self._calculate_behavioral_metrics(user_data)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(user_id, {
                "performance": performance_metrics,
                "engagement": engagement_metrics,
                "progress": progress_metrics,
                "time": time_metrics,
                "skills": skill_metrics,
                "behavioral": behavioral_metrics
            })
            
            recommendations = await self._generate_recommendations(user_id, insights)
            
            # Create analytics record
            analytics = LearningMetrics(
                user_id=user_id,
                timeframe=timeframe.value,
                performance_metrics=performance_metrics,
                engagement_metrics=engagement_metrics,
                progress_metrics=progress_metrics,
                time_metrics=time_metrics,
                skill_metrics=skill_metrics,
                behavioral_metrics=behavioral_metrics,
                calculated_at=datetime.now(timezone.utc),
                insights=insights,
                recommendations=recommendations
            )
            
            # Store analytics data
            await self._store_analytics(analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating user analytics: {str(e)}")
            raise
    
    def _get_timeframe_boundaries(self, timeframe: AnalyticsTimeframe) -> tuple:
        """Calculate start and end dates for timeframe"""
        now = datetime.now(timezone.utc)
        
        if timeframe == AnalyticsTimeframe.DAILY:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            start_date = now - timedelta(days=7)
            end_date = now
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            start_date = now - timedelta(days=30)
            end_date = now
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            start_date = now - timedelta(days=90)
            end_date = now
        elif timeframe == AnalyticsTimeframe.YEARLY:
            start_date = now - timedelta(days=365)
            end_date = now
        else:  # ALL_TIME
            start_date = datetime.min.replace(tzinfo=timezone.utc)
            end_date = now
            
        return start_date, end_date
    
    async def _gather_user_data(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, List]:
        """Gather all user data for analytics calculation"""
        
        # Assessment sessions
        assessment_sessions = await self.db.assessment_sessions.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # User answers
        user_answers = await self.db.user_answers.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Think-aloud sessions
        think_aloud_sessions = await self.db.think_aloud_sessions.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Generated content
        generated_content = await self.db.generated_content.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # User achievements
        achievements = await self.db.user_achievements.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Leaderboard entries
        leaderboard_entries = await self.db.leaderboard_entries.find({
            "user_id": user_id,
            "updated_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        return {
            "assessment_sessions": assessment_sessions,
            "user_answers": user_answers,
            "think_aloud_sessions": think_aloud_sessions,
            "generated_content": generated_content,
            "achievements": achievements,
            "leaderboard_entries": leaderboard_entries
        }
    
    async def _calculate_performance_metrics(self, user_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate performance-related metrics"""
        
        user_answers = user_data["user_answers"]
        assessment_sessions = user_data["assessment_sessions"]
        
        if not user_answers:
            return {
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy_rate": 0.0,
                "average_score": 0.0,
                "performance_trend": "stable",
                "difficulty_breakdown": {},
                "subject_performance": {}
            }
        
        # Basic performance calculations
        total_questions = len(user_answers)
        correct_answers = sum(1 for answer in user_answers if answer.get("is_correct", False))
        accuracy_rate = correct_answers / total_questions if total_questions > 0 else 0
        
        # Calculate average score from assessment sessions
        scores = [session.get("final_score", 0) for session in assessment_sessions if session.get("final_score") is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Performance trend analysis
        performance_trend = await self._calculate_performance_trend(user_answers)
        
        # Difficulty breakdown
        difficulty_breakdown = defaultdict(lambda: {"total": 0, "correct": 0})
        for answer in user_answers:
            difficulty = answer.get("difficulty", "medium")
            difficulty_breakdown[difficulty]["total"] += 1
            if answer.get("is_correct", False):
                difficulty_breakdown[difficulty]["correct"] += 1
        
        # Convert to percentages
        for difficulty, stats in difficulty_breakdown.items():
            if stats["total"] > 0:
                stats["accuracy"] = stats["correct"] / stats["total"]
        
        # Subject performance analysis
        subject_performance = await self._analyze_subject_performance(user_answers)
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "accuracy_rate": accuracy_rate,
            "average_score": average_score,
            "performance_trend": performance_trend,
            "difficulty_breakdown": dict(difficulty_breakdown),
            "subject_performance": subject_performance,
            "recent_scores": scores[-10:] if scores else []  # Last 10 scores
        }
    
    async def _calculate_engagement_metrics(self, user_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate engagement-related metrics"""
        
        assessment_sessions = user_data["assessment_sessions"]
        think_aloud_sessions = user_data["think_aloud_sessions"]
        generated_content = user_data["generated_content"]
        achievements = user_data["achievements"]
        
        # Session frequency
        total_sessions = len(assessment_sessions)
        think_aloud_sessions_count = len(think_aloud_sessions)
        content_generation_count = len(generated_content)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score({
            "assessment_sessions": total_sessions,
            "think_aloud_sessions": think_aloud_sessions_count,
            "content_generated": content_generation_count,
            "achievements_earned": len([a for a in achievements if a.get("status") == "completed"])
        })
        
        # Feature usage breakdown
        feature_usage = {
            "adaptive_assessments": total_sessions,
            "think_aloud_assessments": think_aloud_sessions_count,
            "ai_content_generation": content_generation_count,
            "achievements_system": len(achievements)
        }
        
        # Activity pattern analysis
        activity_pattern = await self._analyze_activity_pattern(assessment_sessions)
        
        return {
            "engagement_score": engagement_score,
            "total_sessions": total_sessions,
            "feature_usage": feature_usage,
            "activity_pattern": activity_pattern,
            "consistency_rating": self._calculate_consistency_rating(assessment_sessions)
        }
    
    async def _calculate_progress_metrics(self, user_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate progress-related metrics"""
        
        achievements = user_data["achievements"]
        assessment_sessions = user_data["assessment_sessions"]
        
        # Achievement progress
        completed_achievements = len([a for a in achievements if a.get("status") == "completed"])
        in_progress_achievements = len([a for a in achievements if a.get("status") == "in_progress"])
        
        # Skill progression
        skill_progression = await self._calculate_skill_progression(assessment_sessions)
        
        # Learning velocity
        learning_velocity = await self._calculate_learning_velocity(assessment_sessions)
        
        # Milestone tracking
        milestones = await self._track_milestones(user_data)
        
        return {
            "completed_achievements": completed_achievements,
            "in_progress_achievements": in_progress_achievements,
            "skill_progression": skill_progression,
            "learning_velocity": learning_velocity,
            "milestones": milestones,
            "progress_percentage": self._calculate_overall_progress(user_data)
        }
    
    async def _calculate_time_metrics(self, user_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate time-related metrics"""
        
        assessment_sessions = user_data["assessment_sessions"]
        
        # Time spent analysis
        total_time_spent = sum(session.get("duration", 0) for session in assessment_sessions)
        average_session_time = total_time_spent / len(assessment_sessions) if assessment_sessions else 0
        
        # Peak activity times
        peak_times = await self._analyze_peak_activity_times(assessment_sessions)
        
        # Study streak analysis
        study_streak = await self._calculate_study_streak(assessment_sessions)
        
        return {
            "total_time_spent": total_time_spent,
            "average_session_time": average_session_time,
            "peak_activity_times": peak_times,
            "current_study_streak": study_streak,
            "time_efficiency": self._calculate_time_efficiency(assessment_sessions)
        }
    
    async def _calculate_skill_metrics(self, user_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate skill mastery metrics"""
        
        user_answers = user_data["user_answers"]
        
        # Skill mastery by subject
        skill_mastery = defaultdict(lambda: {"questions": 0, "correct": 0, "mastery_level": 0})
        
        for answer in user_answers:
            # Get question to determine subject/skill
            question = await self.db.questions.find_one({"id": answer["question_id"]})
            if question:
                subject = question.get("subject", "general")
                skill_mastery[subject]["questions"] += 1
                if answer.get("is_correct", False):
                    skill_mastery[subject]["correct"] += 1
        
        # Calculate mastery levels
        for subject, stats in skill_mastery.items():
            if stats["questions"] > 0:
                accuracy = stats["correct"] / stats["questions"]
                stats["mastery_level"] = self._determine_mastery_level(accuracy, stats["questions"])
        
        # Identify strong and weak areas
        strong_areas = [subject for subject, stats in skill_mastery.items() if stats["mastery_level"] >= 0.8]
        weak_areas = [subject for subject, stats in skill_mastery.items() if stats["mastery_level"] < 0.6]
        
        return {
            "skill_mastery": dict(skill_mastery),
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "overall_mastery": sum(stats["mastery_level"] for stats in skill_mastery.values()) / len(skill_mastery) if skill_mastery else 0
        }
    
    async def _calculate_behavioral_metrics(self, user_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate behavioral pattern metrics"""
        
        # Help-seeking behavior analysis
        help_seeking = await self._analyze_help_seeking_behavior(user_data["user_answers"])
        
        # Risk factors identification
        risk_factors = await self._identify_risk_factors(user_data)
        
        # Learning style indicators
        learning_style = await self._detect_learning_style(user_data)
        
        return {
            "help_seeking_behavior": help_seeking,
            "risk_factors": risk_factors,
            "learning_style_indicators": learning_style,
            "engagement_patterns": await self._analyze_engagement_patterns(user_data)
        }
    
    async def _generate_insights(self, user_id: str, metrics: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights from metrics"""
        
        insights = []
        
        # Performance insights
        if metrics["performance"]["accuracy_rate"] > 0.85:
            insights.append("Excellent performance! You're consistently scoring above 85% accuracy.")
        elif metrics["performance"]["accuracy_rate"] < 0.6:
            insights.append("Consider reviewing challenging topics to improve your accuracy rate.")
        
        # Engagement insights
        if metrics["engagement"]["engagement_score"] > 0.8:
            insights.append("High engagement levels detected! You're actively using multiple features.")
        elif metrics["engagement"]["engagement_score"] < 0.4:
            insights.append("Try exploring different features like think-aloud assessments or content generation.")
        
        # Progress insights
        if metrics["progress"]["learning_velocity"] > 0.7:
            insights.append("Great learning velocity! You're making rapid progress.")
        
        # Time insights
        if metrics["time"]["current_study_streak"] > 7:
            insights.append(f"Impressive {metrics['time']['current_study_streak']}-day study streak! Keep it up!")
        
        # Skill insights
        if metrics["skills"]["weak_areas"]:
            insights.append(f"Focus areas identified: {', '.join(metrics['skills']['weak_areas'][:3])}")
        
        return insights
    
    async def _generate_recommendations(self, user_id: str, insights: List[str]) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = [
            "Continue your regular study schedule to maintain momentum",
            "Try the think-aloud assessment feature for deeper learning insights",
            "Use the AI content generator to create personalized study materials",
            "Check out the leaderboards to see how you compare with other learners"
        ]
        
        return recommendations[:3]  # Return top 3 recommendations
    
    # Helper methods for calculations
    def _calculate_engagement_score(self, activity_data: Dict[str, int]) -> float:
        """Calculate engagement score based on activity"""
        weights = {
            "assessment_sessions": 0.4,
            "think_aloud_sessions": 0.3,
            "content_generated": 0.2,
            "achievements_earned": 0.1
        }
        
        max_values = {
            "assessment_sessions": 50,
            "think_aloud_sessions": 20,
            "content_generated": 10,
            "achievements_earned": 10
        }
        
        score = 0
        for activity, count in activity_data.items():
            normalized = min(count / max_values.get(activity, 1), 1.0)
            score += normalized * weights.get(activity, 0)
        
        return min(score, 1.0)
    
    def _determine_mastery_level(self, accuracy: float, question_count: int) -> float:
        """Determine skill mastery level"""
        if question_count < 5:
            return accuracy * 0.7  # Lower confidence with fewer questions
        elif question_count < 10:
            return accuracy * 0.85
        else:
            return accuracy
    
    async def _store_analytics(self, analytics: LearningMetrics):
        """Store analytics data in database"""
        try:
            await self.db.learning_analytics.insert_one(analytics.dict())
            logger.info(f"Analytics stored for user {analytics.user_id}")
        except Exception as e:
            logger.error(f"Error storing analytics: {str(e)}")
    
    # Placeholder methods for complex calculations
    async def _calculate_performance_trend(self, user_answers: List) -> str:
        """Calculate performance trend - simplified implementation"""
        if len(user_answers) < 5:
            return "insufficient_data"
        
        recent_accuracy = sum(1 for answer in user_answers[-10:] if answer.get("is_correct", False)) / min(10, len(user_answers))
        early_accuracy = sum(1 for answer in user_answers[:10] if answer.get("is_correct", False)) / min(10, len(user_answers))
        
        if recent_accuracy > early_accuracy + 0.1:
            return "improving"
        elif recent_accuracy < early_accuracy - 0.1:
            return "declining"
        else:
            return "stable"
    
    async def _analyze_subject_performance(self, user_answers: List) -> Dict[str, float]:
        """Analyze performance by subject"""
        subject_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for answer in user_answers:
            # This would need to be enhanced with actual question-subject mapping
            subject = "general"  # Placeholder
            subject_stats[subject]["total"] += 1
            if answer.get("is_correct", False):
                subject_stats[subject]["correct"] += 1
        
        return {subject: stats["correct"] / stats["total"] if stats["total"] > 0 else 0 
                for subject, stats in subject_stats.items()}
    
    async def _analyze_activity_pattern(self, sessions: List) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        if not sessions:
            return {"pattern": "inactive", "peak_hours": [], "active_days": []}
        
        # Simplified analysis
        return {
            "pattern": "regular" if len(sessions) > 5 else "occasional",
            "peak_hours": [9, 14, 20],  # Placeholder
            "active_days": ["monday", "wednesday", "friday"]  # Placeholder
        }
    
    def _calculate_consistency_rating(self, sessions: List) -> float:
        """Calculate consistency rating"""
        if len(sessions) < 3:
            return 0.0
        
        # Simplified consistency calculation
        return min(len(sessions) / 30.0, 1.0)  # Based on sessions per month
    
    async def _calculate_skill_progression(self, sessions: List) -> Dict[str, float]:
        """Calculate skill progression over time"""
        return {"mathematics": 0.75, "science": 0.68, "reading": 0.82}  # Placeholder
    
    async def _calculate_learning_velocity(self, sessions: List) -> float:
        """Calculate learning velocity"""
        if not sessions:
            return 0.0
        return min(len(sessions) / 20.0, 1.0)  # Simplified calculation
    
    async def _track_milestones(self, user_data: Dict) -> List[Dict[str, Any]]:
        """Track learning milestones"""
        milestones = []
        
        if len(user_data["assessment_sessions"]) >= 10:
            milestones.append({"name": "Assessment Explorer", "achieved": True})
        if len(user_data["think_aloud_sessions"]) >= 5:
            milestones.append({"name": "Think-Aloud Practitioner", "achieved": True})
        
        return milestones
    
    def _calculate_overall_progress(self, user_data: Dict) -> float:
        """Calculate overall progress percentage"""
        # Simplified progress calculation
        factors = [
            len(user_data["assessment_sessions"]) / 50.0,
            len(user_data["achievements"]) / 20.0,
            len(user_data["think_aloud_sessions"]) / 10.0
        ]
        return min(sum(factors) / len(factors), 1.0) * 100
    
    async def _analyze_peak_activity_times(self, sessions: List) -> List[int]:
        """Analyze peak activity times"""
        return [9, 14, 20]  # Placeholder hours
    
    async def _calculate_study_streak(self, sessions: List) -> int:
        """Calculate current study streak"""
        if not sessions:
            return 0
        
        # Simplified streak calculation
        return min(len(sessions), 30)  # Max 30-day streak
    
    def _calculate_time_efficiency(self, sessions: List) -> float:
        """Calculate time efficiency metric"""
        if not sessions:
            return 0.0
        
        # Simplified efficiency calculation
        avg_duration = sum(session.get("duration", 0) for session in sessions) / len(sessions)
        return min(3600 / max(avg_duration, 1), 1.0)  # Efficiency based on session duration
    
    async def _analyze_help_seeking_behavior(self, answers: List) -> Dict[str, Any]:
        """Analyze help-seeking patterns"""
        help_used = sum(1 for answer in answers if answer.get("ai_help_used", False))
        return {
            "help_frequency": help_used / len(answers) if answers else 0,
            "help_effectiveness": 0.75,  # Placeholder
            "independence_level": 1 - (help_used / len(answers)) if answers else 1
        }
    
    async def _identify_risk_factors(self, user_data: Dict) -> List[str]:
        """Identify learning risk factors"""
        risk_factors = []
        
        if len(user_data["assessment_sessions"]) == 0:
            risk_factors.append("No recent assessment activity")
        
        return risk_factors
    
    async def _detect_learning_style(self, user_data: Dict) -> Dict[str, float]:
        """Detect learning style preferences"""
        return {
            "visual": 0.7,
            "auditory": 0.3,
            "kinesthetic": 0.5,
            "reading_writing": 0.6
        }  # Placeholder
    
    async def _analyze_engagement_patterns(self, user_data: Dict) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        return {
            "preferred_features": ["adaptive_assessment", "ai_content_generation"],
            "engagement_consistency": 0.75,
            "feature_exploration": 0.6
        }  # Placeholder

# Global analytics engine instance
analytics_engine = None

def get_analytics_engine(db: AsyncIOMotorDatabase) -> AnalyticsEngine:
    """Get analytics engine instance"""
    global analytics_engine
    if analytics_engine is None:
        analytics_engine = AnalyticsEngine(db)
    return analytics_engine