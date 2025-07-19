"""
Advanced Learning Analytics Dashboard Engine for IDFS PathwayIQ™ powered by SikatLabs™

This module handles comprehensive learning analytics including:
- User performance tracking and analysis
- Learning pattern identification
- Skill assessment analytics
- Progress visualization data
- Comparative analytics
- Real-time dashboard metrics
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
import uuid
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self):
        """Initialize the Analytics Engine with database connection"""
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable is required")
        
        self.client = MongoClient(mongo_url)
        self.db = self.client.get_database()
        
        # Collections for analytics data
        self.users_collection = self.db.users
        self.assessments_collection = self.db.assessments
        self.content_collection = self.db.generated_content
        self.sessions_collection = self.db.speech_sessions
        self.analytics_collection = self.db.analytics_data
        
        logger.info("Analytics Engine initialized successfully")

    def get_user_performance_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a user"""
        try:
            user = self.users_collection.find_one({"user_id": user_id})
            if not user:
                return {"error": "User not found"}

            # Get assessment data
            assessments = list(self.assessments_collection.find({"user_id": user_id}))
            
            # Get content generation data
            content_items = list(self.content_collection.find({"user_id": user_id}))
            
            # Get speech session data
            speech_sessions = list(self.sessions_collection.find({"user_id": user_id}))

            performance_summary = {
                "user_id": user_id,
                "username": user.get("username", ""),
                "level": user.get("level", 1),
                "experience_points": user.get("experience_points", 0),
                "total_assessments": len(assessments),
                "total_content_generated": len(content_items),
                "total_speech_sessions": len(speech_sessions),
                "average_assessment_score": self._calculate_average_assessment_score(assessments),
                "learning_streak": self._calculate_learning_streak(user_id),
                "skill_progress": self._analyze_skill_progress(assessments),
                "recent_activity": self._get_recent_activity(user_id),
                "performance_trend": self._calculate_performance_trend(assessments),
                "time_spent_learning": self._calculate_time_spent(assessments, speech_sessions),
                "strengths": self._identify_strengths(assessments),
                "areas_for_improvement": self._identify_improvement_areas(assessments)
            }

            return performance_summary

        except Exception as e:
            logger.error(f"Error getting user performance summary: {str(e)}")
            return {"error": "Failed to retrieve performance summary"}

    def get_learning_analytics_dashboard(self, user_id: str, time_period: str = "30d") -> Dict[str, Any]:
        """Get comprehensive learning analytics dashboard data"""
        try:
            # Calculate time range
            end_date = datetime.now()
            if time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)

            dashboard_data = {
                "user_performance": self.get_user_performance_summary(user_id),
                "learning_metrics": self._get_learning_metrics(user_id, start_date, end_date),
                "skill_analytics": self._get_skill_analytics(user_id, start_date, end_date),
                "engagement_analytics": self._get_engagement_analytics(user_id, start_date, end_date),
                "progress_visualization": self._get_progress_visualization(user_id, start_date, end_date),
                "comparative_analytics": self._get_comparative_analytics(user_id),
                "recommendations": self._generate_learning_recommendations(user_id),
                "time_period": time_period,
                "generated_at": datetime.now().isoformat()
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {str(e)}")
            return {"error": "Failed to generate analytics dashboard"}

    def get_class_analytics(self, educator_id: str, class_id: str = None) -> Dict[str, Any]:
        """Get class-level analytics for educators"""
        try:
            # For MVP, we'll provide system-wide analytics since class management isn't implemented yet
            all_users = list(self.users_collection.find({"role": {"$ne": "admin"}}))
            
            class_analytics = {
                "class_overview": {
                    "total_students": len([u for u in all_users if u.get("role") == "student"]),
                    "total_teachers": len([u for u in all_users if u.get("role") == "teacher"]),
                    "active_users_7d": self._get_active_users_count(7),
                    "active_users_30d": self._get_active_users_count(30)
                },
                "performance_distribution": self._get_performance_distribution(),
                "engagement_metrics": self._get_class_engagement_metrics(),
                "skill_mastery_overview": self._get_skill_mastery_overview(),
                "content_usage_analytics": self._get_content_usage_analytics(),
                "assessment_analytics": self._get_assessment_analytics(),
                "top_performers": self._get_top_performers(10),
                "students_needing_support": self._get_students_needing_support(),
                "generated_at": datetime.now().isoformat()
            }

            return class_analytics

        except Exception as e:
            logger.error(f"Error generating class analytics: {str(e)}")
            return {"error": "Failed to generate class analytics"}

    def _calculate_average_assessment_score(self, assessments: List[Dict]) -> float:
        """Calculate average assessment score"""
        if not assessments:
            return 0.0
        
        scores = []
        for assessment in assessments:
            if "responses" in assessment:
                correct_count = sum(1 for response in assessment["responses"] if response.get("correct", False))
                total_count = len(assessment["responses"])
                if total_count > 0:
                    scores.append(correct_count / total_count * 100)
        
        return round(statistics.mean(scores) if scores else 0.0, 2)

    def _calculate_learning_streak(self, user_id: str) -> int:
        """Calculate current learning streak in days"""
        try:
            # Get recent activity from all collections
            recent_assessments = list(self.assessments_collection.find(
                {"user_id": user_id}, 
                sort=[("timestamp", -1)]
            ).limit(30))
            
            recent_content = list(self.content_collection.find(
                {"user_id": user_id}, 
                sort=[("created_at", -1)]
            ).limit(30))
            
            recent_sessions = list(self.sessions_collection.find(
                {"user_id": user_id}, 
                sort=[("created_at", -1)]
            ).limit(30))

            # Combine all activities with dates
            activities = []
            
            for assessment in recent_assessments:
                if "timestamp" in assessment:
                    activities.append(assessment["timestamp"])
            
            for content in recent_content:
                if "created_at" in content:
                    activities.append(content["created_at"])
            
            for session in recent_sessions:
                if "created_at" in session:
                    activities.append(session["created_at"])

            if not activities:
                return 0

            # Sort activities by date (most recent first)
            activities.sort(reverse=True)
            
            # Calculate streak
            streak = 0
            current_date = datetime.now().date()
            
            for activity in activities:
                activity_date = activity.date() if isinstance(activity, datetime) else datetime.fromisoformat(str(activity)).date()
                
                if activity_date == current_date or activity_date == current_date - timedelta(days=streak):
                    if activity_date == current_date - timedelta(days=streak):
                        streak += 1
                        current_date = activity_date
                elif activity_date < current_date - timedelta(days=streak):
                    break

            return streak

        except Exception as e:
            logger.error(f"Error calculating learning streak: {str(e)}")
            return 0

    def _analyze_skill_progress(self, assessments: List[Dict]) -> Dict[str, Any]:
        """Analyze skill progress across different areas"""
        skill_data = defaultdict(list)
        
        for assessment in assessments:
            if "responses" in assessment:
                for response in assessment["responses"]:
                    skill = response.get("skill", "general")
                    correct = response.get("correct", False)
                    skill_data[skill].append(1 if correct else 0)
        
        skill_progress = {}
        for skill, scores in skill_data.items():
            if scores:
                skill_progress[skill] = {
                    "accuracy": round(statistics.mean(scores) * 100, 2),
                    "total_attempts": len(scores),
                    "recent_performance": round(statistics.mean(scores[-5:]) * 100, 2) if len(scores) >= 5 else round(statistics.mean(scores) * 100, 2)
                }
        
        return skill_progress

    def _get_recent_activity(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent learning activities for the user"""
        activities = []
        
        # Get recent assessments
        recent_assessments = list(self.assessments_collection.find(
            {"user_id": user_id}, 
            sort=[("timestamp", -1)]
        ).limit(5))
        
        for assessment in recent_assessments:
            activities.append({
                "type": "assessment",
                "description": f"Completed adaptive assessment",
                "timestamp": assessment.get("timestamp", datetime.now()).isoformat(),
                "score": self._calculate_assessment_score(assessment)
            })
        
        # Get recent content generation
        recent_content = list(self.content_collection.find(
            {"user_id": user_id}, 
            sort=[("created_at", -1)]
        ).limit(5))
        
        for content in recent_content:
            activities.append({
                "type": "content_generation",
                "description": f"Generated {content.get('content_type', 'content')}: {content.get('subject', 'N/A')}",
                "timestamp": content.get("created_at", datetime.now()).isoformat(),
                "topic": content.get("topic", "N/A")
            })
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:10]

    def _calculate_performance_trend(self, assessments: List[Dict]) -> str:
        """Calculate performance trend (improving, stable, declining)"""
        if len(assessments) < 2:
            return "insufficient_data"
        
        # Get recent vs older performance
        sorted_assessments = sorted(assessments, key=lambda x: x.get("timestamp", datetime.now()))
        
        if len(sorted_assessments) < 4:
            return "insufficient_data"
        
        # Compare first half vs second half
        mid_point = len(sorted_assessments) // 2
        older_scores = [self._calculate_assessment_score(a) for a in sorted_assessments[:mid_point]]
        recent_scores = [self._calculate_assessment_score(a) for a in sorted_assessments[mid_point:]]
        
        if not older_scores or not recent_scores:
            return "insufficient_data"
        
        older_avg = statistics.mean(older_scores)
        recent_avg = statistics.mean(recent_scores)
        
        improvement_threshold = 5  # 5% improvement threshold
        
        if recent_avg > older_avg + improvement_threshold:
            return "improving"
        elif recent_avg < older_avg - improvement_threshold:
            return "declining"
        else:
            return "stable"

    def _calculate_time_spent(self, assessments: List[Dict], sessions: List[Dict]) -> Dict[str, int]:
        """Calculate time spent in different learning activities"""
        time_data = {
            "total_minutes": 0,
            "assessment_minutes": 0,
            "think_aloud_minutes": 0
        }
        
        # Calculate assessment time (estimate based on question count)
        for assessment in assessments:
            question_count = len(assessment.get("responses", []))
            estimated_minutes = question_count * 2  # Estimate 2 minutes per question
            time_data["assessment_minutes"] += estimated_minutes
        
        # Calculate think-aloud session time
        for session in sessions:
            if "duration" in session:
                time_data["think_aloud_minutes"] += session["duration"]
            else:
                # Estimate based on transcription count
                transcription_count = len(session.get("transcriptions", []))
                estimated_minutes = transcription_count * 3  # Estimate 3 minutes per transcription
                time_data["think_aloud_minutes"] += estimated_minutes
        
        time_data["total_minutes"] = time_data["assessment_minutes"] + time_data["think_aloud_minutes"]
        
        return time_data

    def _identify_strengths(self, assessments: List[Dict]) -> List[str]:
        """Identify user's learning strengths"""
        skill_progress = self._analyze_skill_progress(assessments)
        
        strengths = []
        for skill, data in skill_progress.items():
            if data["accuracy"] >= 80:  # 80% or higher accuracy
                strengths.append(skill)
        
        return strengths[:5]  # Return top 5 strengths

    def _identify_improvement_areas(self, assessments: List[Dict]) -> List[str]:
        """Identify areas needing improvement"""
        skill_progress = self._analyze_skill_progress(assessments)
        
        improvement_areas = []
        for skill, data in skill_progress.items():
            if data["accuracy"] < 60:  # Less than 60% accuracy
                improvement_areas.append(skill)
        
        return improvement_areas[:5]  # Return top 5 improvement areas

    def _calculate_assessment_score(self, assessment: Dict) -> float:
        """Calculate score for a single assessment"""
        if "responses" not in assessment:
            return 0.0
        
        responses = assessment["responses"]
        if not responses:
            return 0.0
        
        correct_count = sum(1 for response in responses if response.get("correct", False))
        return (correct_count / len(responses)) * 100

    def _get_learning_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get detailed learning metrics for the time period"""
        # This is a comprehensive method that would analyze various learning metrics
        return {
            "questions_answered": self._count_questions_in_period(user_id, start_date, end_date),
            "content_created": self._count_content_in_period(user_id, start_date, end_date),
            "sessions_completed": self._count_sessions_in_period(user_id, start_date, end_date),
            "average_session_duration": self._get_average_session_duration(user_id, start_date, end_date),
            "skill_improvements": self._track_skill_improvements(user_id, start_date, end_date)
        }

    def _get_skill_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get skill-specific analytics"""
        assessments = list(self.assessments_collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }))
        
        return self._analyze_skill_progress(assessments)

    def _get_engagement_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user engagement analytics"""
        return {
            "daily_active_days": self._count_active_days(user_id, start_date, end_date),
            "weekly_sessions": self._get_weekly_session_pattern(user_id, start_date, end_date),
            "preferred_learning_times": self._analyze_learning_time_patterns(user_id, start_date, end_date),
            "engagement_score": self._calculate_engagement_score(user_id, start_date, end_date)
        }

    def _get_progress_visualization(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get data for progress visualization charts"""
        return {
            "daily_progress": self._get_daily_progress_data(user_id, start_date, end_date),
            "skill_radar_chart": self._get_skill_radar_data(user_id),
            "performance_timeline": self._get_performance_timeline(user_id, start_date, end_date),
            "learning_velocity": self._calculate_learning_velocity(user_id, start_date, end_date)
        }

    def _get_comparative_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comparative analytics against peer performance"""
        user = self.users_collection.find_one({"user_id": user_id})
        user_level = user.get("level", 1) if user else 1
        
        # Find peers at similar level
        peers = list(self.users_collection.find({
            "level": {"$gte": user_level - 1, "$lte": user_level + 1},
            "user_id": {"$ne": user_id}
        }))
        
        if not peers:
            return {"message": "No peer data available for comparison"}
        
        return {
            "peer_count": len(peers),
            "rank_percentile": self._calculate_user_rank_percentile(user_id, peers),
            "performance_vs_peers": self._compare_performance_with_peers(user_id, peers),
            "relative_strengths": self._identify_relative_strengths(user_id, peers)
        }

    def _generate_learning_recommendations(self, user_id: str) -> List[Dict[str, str]]:
        """Generate personalized learning recommendations"""
        user_performance = self.get_user_performance_summary(user_id)
        
        recommendations = []
        
        # Based on areas for improvement
        if user_performance.get("areas_for_improvement"):
            for area in user_performance["areas_for_improvement"][:3]:
                recommendations.append({
                    "type": "skill_improvement",
                    "title": f"Focus on {area}",
                    "description": f"Your performance in {area} could be improved. Consider practicing more questions in this area.",
                    "priority": "high"
                })
        
        # Based on learning streak
        streak = user_performance.get("learning_streak", 0)
        if streak == 0:
            recommendations.append({
                "type": "engagement",
                "title": "Start Your Learning Streak",
                "description": "Begin your learning journey today! Complete an assessment or generate some content to start building your streak.",
                "priority": "medium"
            })
        elif streak > 0 and streak < 7:
            recommendations.append({
                "type": "engagement",
                "title": "Keep Your Streak Going",
                "description": f"Great job! You have a {streak}-day streak. Keep it up by completing today's learning activities.",
                "priority": "medium"
            })
        
        # Based on performance trend
        trend = user_performance.get("performance_trend")
        if trend == "declining":
            recommendations.append({
                "type": "performance",
                "title": "Performance Recovery",
                "description": "Your recent performance shows room for improvement. Try reviewing fundamental concepts and taking practice assessments.",
                "priority": "high"
            })
        
        return recommendations

    # Helper methods for analytics calculations
    def _count_questions_in_period(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """Count questions answered in the time period"""
        assessments = list(self.assessments_collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }))
        
        total_questions = 0
        for assessment in assessments:
            total_questions += len(assessment.get("responses", []))
        
        return total_questions

    def _count_content_in_period(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """Count content items created in the time period"""
        return self.content_collection.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        })

    def _count_sessions_in_period(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """Count sessions completed in the time period"""
        return self.sessions_collection.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        })

    def _get_average_session_duration(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Get average session duration in minutes"""
        sessions = list(self.sessions_collection.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        if not sessions:
            return 0.0
        
        durations = []
        for session in sessions:
            if "duration" in session:
                durations.append(session["duration"])
            else:
                # Estimate duration based on transcriptions
                transcription_count = len(session.get("transcriptions", []))
                estimated_duration = transcription_count * 3  # 3 minutes per transcription
                durations.append(estimated_duration)
        
        return round(statistics.mean(durations) if durations else 0.0, 2)

    def _track_skill_improvements(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Track improvements in different skills"""
        # This would compare performance at the start vs end of the period
        return {"math": 5.2, "reading": 3.8, "science": 7.1}  # Placeholder data

    def _count_active_days(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """Count days when user was active"""
        # This would analyze daily activity patterns
        return 18  # Placeholder

    def _get_weekly_session_pattern(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get weekly session patterns"""
        return {
            "monday": 2, "tuesday": 3, "wednesday": 4, 
            "thursday": 2, "friday": 1, "saturday": 1, "sunday": 0
        }  # Placeholder

    def _analyze_learning_time_patterns(self, user_id: str, start_date: datetime, end_date: datetime) -> List[str]:
        """Analyze preferred learning times"""
        return ["morning", "afternoon"]  # Placeholder

    def _calculate_engagement_score(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate engagement score (0-100)"""
        return 78.5  # Placeholder

    def _get_daily_progress_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get daily progress data for charts"""
        return [
            {"date": "2025-01-01", "score": 75},
            {"date": "2025-01-02", "score": 78},
            {"date": "2025-01-03", "score": 82}
        ]  # Placeholder

    def _get_skill_radar_data(self, user_id: str) -> Dict[str, float]:
        """Get skill radar chart data"""
        assessments = list(self.assessments_collection.find({"user_id": user_id}))
        return self._analyze_skill_progress(assessments)

    def _get_performance_timeline(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get performance timeline data"""
        assessments = list(self.assessments_collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }, sort=[("timestamp", 1)]))
        
        timeline = []
        for assessment in assessments:
            score = self._calculate_assessment_score(assessment)
            timeline.append({
                "timestamp": assessment.get("timestamp", datetime.now()).isoformat(),
                "score": score,
                "type": "assessment"
            })
        
        return timeline

    def _calculate_learning_velocity(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate learning velocity (progress per day)"""
        days_in_period = (end_date - start_date).days
        if days_in_period == 0:
            return 0.0
        
        questions_answered = self._count_questions_in_period(user_id, start_date, end_date)
        return round(questions_answered / days_in_period, 2)

    # Class-level analytics helper methods
    def _get_active_users_count(self, days: int) -> int:
        """Get count of active users in the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        active_assessment_users = self.assessments_collection.distinct("user_id", 
            {"timestamp": {"$gte": cutoff_date}})
        active_content_users = self.content_collection.distinct("user_id", 
            {"created_at": {"$gte": cutoff_date}})
        active_session_users = self.sessions_collection.distinct("user_id", 
            {"created_at": {"$gte": cutoff_date}})
        
        all_active_users = set(active_assessment_users + active_content_users + active_session_users)
        return len(all_active_users)

    def _get_performance_distribution(self) -> Dict[str, int]:
        """Get performance distribution across all users"""
        all_users = list(self.users_collection.find())
        distribution = {"excellent": 0, "good": 0, "fair": 0, "needs_improvement": 0}
        
        for user in all_users:
            user_assessments = list(self.assessments_collection.find({"user_id": user["user_id"]}))
            if user_assessments:
                avg_score = self._calculate_average_assessment_score(user_assessments)
                if avg_score >= 90:
                    distribution["excellent"] += 1
                elif avg_score >= 75:
                    distribution["good"] += 1
                elif avg_score >= 60:
                    distribution["fair"] += 1
                else:
                    distribution["needs_improvement"] += 1
        
        return distribution

    def _get_class_engagement_metrics(self) -> Dict[str, Any]:
        """Get class-level engagement metrics"""
        total_users = self.users_collection.count_documents({"role": {"$ne": "admin"}})
        active_7d = self._get_active_users_count(7)
        active_30d = self._get_active_users_count(30)
        
        return {
            "total_users": total_users,
            "active_users_7d": active_7d,
            "active_users_30d": active_30d,
            "engagement_rate_7d": round((active_7d / total_users) * 100, 2) if total_users > 0 else 0,
            "engagement_rate_30d": round((active_30d / total_users) * 100, 2) if total_users > 0 else 0
        }

    def _get_skill_mastery_overview(self) -> Dict[str, Any]:
        """Get overview of skill mastery across all users"""
        all_assessments = list(self.assessments_collection.find())
        skill_data = defaultdict(list)
        
        for assessment in all_assessments:
            for response in assessment.get("responses", []):
                skill = response.get("skill", "general")
                correct = response.get("correct", False)
                skill_data[skill].append(1 if correct else 0)
        
        mastery_overview = {}
        for skill, scores in skill_data.items():
            if scores:
                avg_accuracy = statistics.mean(scores) * 100
                mastery_level = "high" if avg_accuracy >= 80 else "medium" if avg_accuracy >= 60 else "low"
                mastery_overview[skill] = {
                    "accuracy": round(avg_accuracy, 2),
                    "mastery_level": mastery_level,
                    "total_attempts": len(scores)
                }
        
        return mastery_overview

    def _get_content_usage_analytics(self) -> Dict[str, Any]:
        """Get content usage analytics"""
        content_types = self.content_collection.distinct("content_type")
        usage_by_type = {}
        
        for content_type in content_types:
            count = self.content_collection.count_documents({"content_type": content_type})
            usage_by_type[content_type] = count
        
        total_content = sum(usage_by_type.values())
        
        return {
            "total_content_items": total_content,
            "usage_by_type": usage_by_type,
            "most_popular_type": max(usage_by_type, key=usage_by_type.get) if usage_by_type else None,
            "average_usage_per_user": round(total_content / max(self.users_collection.count_documents({}), 1), 2)
        }

    def _get_assessment_analytics(self) -> Dict[str, Any]:
        """Get assessment analytics"""
        total_assessments = self.assessments_collection.count_documents({})
        
        if total_assessments == 0:
            return {"total_assessments": 0, "average_score": 0, "completion_rate": 0}
        
        all_assessments = list(self.assessments_collection.find())
        all_scores = [self._calculate_assessment_score(a) for a in all_assessments]
        
        return {
            "total_assessments": total_assessments,
            "average_score": round(statistics.mean(all_scores) if all_scores else 0, 2),
            "completion_rate": 85.7,  # Placeholder - would calculate based on started vs completed
            "score_distribution": {
                "90-100": len([s for s in all_scores if s >= 90]),
                "80-89": len([s for s in all_scores if 80 <= s < 90]),
                "70-79": len([s for s in all_scores if 70 <= s < 80]),
                "below_70": len([s for s in all_scores if s < 70])
            }
        }

    def _get_top_performers(self, limit: int) -> List[Dict[str, Any]]:
        """Get top performing users"""
        all_users = list(self.users_collection.find())
        user_performances = []
        
        for user in all_users:
            user_assessments = list(self.assessments_collection.find({"user_id": user["user_id"]}))
            if user_assessments:
                avg_score = self._calculate_average_assessment_score(user_assessments)
                user_performances.append({
                    "user_id": user["user_id"],
                    "username": user.get("username", ""),
                    "level": user.get("level", 1),
                    "average_score": avg_score,
                    "total_assessments": len(user_assessments)
                })
        
        # Sort by average score
        user_performances.sort(key=lambda x: x["average_score"], reverse=True)
        return user_performances[:limit]

    def _get_students_needing_support(self) -> List[Dict[str, Any]]:
        """Get students who may need additional support"""
        all_users = list(self.users_collection.find({"role": "student"}))
        students_needing_support = []
        
        for user in all_users:
            user_assessments = list(self.assessments_collection.find({"user_id": user["user_id"]}))
            if user_assessments:
                avg_score = self._calculate_average_assessment_score(user_assessments)
                if avg_score < 60:  # Below 60% needs support
                    students_needing_support.append({
                        "user_id": user["user_id"],
                        "username": user.get("username", ""),
                        "average_score": avg_score,
                        "total_assessments": len(user_assessments),
                        "areas_for_improvement": self._identify_improvement_areas(user_assessments)
                    })
        
        return students_needing_support

    def _calculate_user_rank_percentile(self, user_id: str, peers: List[Dict]) -> float:
        """Calculate user's rank percentile among peers"""
        # Placeholder implementation
        return 67.5

    def _compare_performance_with_peers(self, user_id: str, peers: List[Dict]) -> Dict[str, Any]:
        """Compare user performance with peers"""
        # Placeholder implementation
        return {
            "user_score": 78.5,
            "peer_average": 72.3,
            "performance_vs_average": "+6.2",
            "better_than_percent": 67
        }

    def _identify_relative_strengths(self, user_id: str, peers: List[Dict]) -> List[str]:
        """Identify user's strengths relative to peers"""
        # Placeholder implementation
        return ["mathematics", "problem_solving"]

    def store_analytics_snapshot(self, user_id: str, analytics_data: Dict[str, Any]) -> str:
        """Store analytics snapshot for historical tracking"""
        try:
            snapshot = {
                "snapshot_id": str(uuid.uuid4()),
                "user_id": user_id,
                "analytics_data": analytics_data,
                "created_at": datetime.now(),
                "snapshot_type": "user_analytics"
            }
            
            self.analytics_collection.insert_one(snapshot)
            logger.info(f"Analytics snapshot stored for user {user_id}")
            return snapshot["snapshot_id"]
            
        except Exception as e:
            logger.error(f"Error storing analytics snapshot: {str(e)}")
            return ""

    def get_analytics_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get analytics history for a user"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            history = list(self.analytics_collection.find({
                "user_id": user_id,
                "created_at": {"$gte": cutoff_date}
            }, sort=[("created_at", -1)]))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting analytics history: {str(e)}")
            return []

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Analytics Engine database connection closed")