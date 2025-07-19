"""
Advanced Learning Analytics Dashboard
Provides comprehensive analytics, insights, and data visualization
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import asyncio
from pymongo import MongoClient
import redis
import json
import numpy as np
from collections import defaultdict, Counter
import os

logger = logging.getLogger(__name__)

class LearningAnalytics:
    def __init__(self, mongo_url: str, redis_url: str = "redis://localhost:6379"):
        self.client = MongoClient(mongo_url)
        db_name = os.getenv('DB_NAME', 'idfs_pathwayiq_database')
        self.db = self.client[db_name]
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Collections
        self.users_collection = self.db.users
        self.assessments_collection = self.db.assessments
        self.content_collection = self.db.content_generation
        self.groups_collection = self.db.study_groups
        self.messages_collection = self.db.group_messages
        self.sessions_collection = self.db.study_sessions
        self.speech_sessions_collection = self.db.speech_sessions
        
        # Create indexes for performance
        self._create_analytics_indexes()
    
    def _create_analytics_indexes(self):
        """Create indexes optimized for analytics queries"""
        try:
            # Assessment analytics indexes
            self.assessments_collection.create_index([
                ("user_id", 1), 
                ("created_at", -1)
            ])
            self.assessments_collection.create_index([
                ("subject", 1), 
                ("created_at", -1)
            ])
            
            # Content generation analytics
            self.content_collection.create_index([
                ("user_id", 1), 
                ("created_at", -1)
            ])
            self.content_collection.create_index([
                ("content_type", 1), 
                ("created_at", -1)
            ])
            
            # Group analytics
            self.messages_collection.create_index([
                ("group_id", 1), 
                ("timestamp", -1)
            ])
            
        except Exception as e:
            logger.error(f"Error creating analytics indexes: {e}")
    
    # USER ANALYTICS
    async def get_user_learning_dashboard(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive learning dashboard for a user"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get user info
            user = self.users_collection.find_one({"id": user_id})
            if not user:
                return {"error": "User not found"}
            
            # Assessment analytics
            assessment_stats = await self._get_user_assessment_analytics(user_id, since_date)
            
            # Content generation analytics
            content_stats = await self._get_user_content_analytics(user_id, since_date)
            
            # Study group participation
            group_stats = await self._get_user_group_analytics(user_id, since_date)
            
            # Learning patterns
            learning_patterns = await self._analyze_learning_patterns(user_id, since_date)
            
            # Performance trends
            performance_trends = await self._calculate_performance_trends(user_id, since_date)
            
            # Recommendations
            recommendations = await self._generate_learning_recommendations(user_id, assessment_stats, content_stats, group_stats)
            
            dashboard = {
                "user_info": {
                    "id": user_id,
                    "username": user.get("username"),
                    "level": user.get("level", 1),
                    "xp": user.get("xp", 0),
                    "role": user.get("role", "student")
                },
                "summary": {
                    "total_assessments": assessment_stats.get("total_assessments", 0),
                    "avg_performance": assessment_stats.get("average_score", 0),
                    "content_generated": content_stats.get("total_content", 0),
                    "study_groups": group_stats.get("active_groups", 0),
                    "active_days": learning_patterns.get("active_days", 0)
                },
                "assessment_analytics": assessment_stats,
                "content_analytics": content_stats,
                "collaboration_analytics": group_stats,
                "learning_patterns": learning_patterns,
                "performance_trends": performance_trends,
                "recommendations": recommendations,
                "period_days": days
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting user learning dashboard: {e}")
            return {"error": str(e)}
    
    async def _get_user_assessment_analytics(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Get detailed assessment analytics for a user"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_assessments": {"$sum": 1},
                        "total_questions": {"$sum": "$questions_answered"},
                        "total_correct": {"$sum": "$questions_correct"},
                        "avg_score": {"$avg": "$final_score"},
                        "avg_ability": {"$avg": "$final_ability_estimate"},
                        "subjects": {"$addToSet": "$subject"},
                        "assessment_types": {"$addToSet": "$assessment_type"}
                    }
                }
            ]
            
            result = list(self.assessments_collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                return {
                    "total_assessments": stats.get("total_assessments", 0),
                    "total_questions": stats.get("total_questions", 0),
                    "total_correct": stats.get("total_correct", 0),
                    "accuracy_rate": (stats.get("total_correct", 0) / max(stats.get("total_questions", 1), 1)) * 100,
                    "average_score": round(stats.get("avg_score", 0), 2),
                    "average_ability": round(stats.get("avg_ability", 0), 2),
                    "subjects_studied": stats.get("subjects", []),
                    "assessment_types": stats.get("assessment_types", [])
                }
            else:
                return {
                    "total_assessments": 0,
                    "total_questions": 0,
                    "total_correct": 0,
                    "accuracy_rate": 0,
                    "average_score": 0,
                    "average_ability": 0,
                    "subjects_studied": [],
                    "assessment_types": []
                }
                
        except Exception as e:
            logger.error(f"Error getting user assessment analytics: {e}")
            return {}
    
    async def _get_user_content_analytics(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Get content generation analytics for a user"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$content_type",
                        "count": {"$sum": 1},
                        "avg_quality": {"$avg": "$quality_score"},
                        "total_usage": {"$sum": "$usage_count"}
                    }
                }
            ]
            
            results = list(self.content_collection.aggregate(pipeline))
            
            content_types = {}
            total_content = 0
            total_usage = 0
            avg_quality = 0
            
            for result in results:
                content_type = result["_id"]
                count = result["count"]
                
                content_types[content_type] = {
                    "count": count,
                    "avg_quality": round(result.get("avg_quality", 0), 2),
                    "total_usage": result.get("total_usage", 0)
                }
                
                total_content += count
                total_usage += result.get("total_usage", 0)
                avg_quality += result.get("avg_quality", 0)
            
            if results:
                avg_quality = avg_quality / len(results)
            
            return {
                "total_content": total_content,
                "content_by_type": content_types,
                "total_usage": total_usage,
                "average_quality": round(avg_quality, 2),
                "most_used_type": max(content_types.items(), key=lambda x: x[1]["count"])[0] if content_types else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user content analytics: {e}")
            return {}
    
    async def _get_user_group_analytics(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Get study group participation analytics for a user"""
        try:
            # Get user's group memberships
            group_memberships = list(self.db.group_members.find({
                "user_id": user_id
            }))
            
            group_ids = [membership["group_id"] for membership in group_memberships]
            
            if not group_ids:
                return {
                    "active_groups": 0,
                    "messages_sent": 0,
                    "sessions_participated": 0,
                    "collaboration_score": 0
                }
            
            # Count messages sent
            messages_sent = self.messages_collection.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": since_date}
            })
            
            # Count session participation
            sessions_participated = self.sessions_collection.count_documents({
                "participants.user_id": user_id,
                "start_time": {"$gte": since_date}
            })
            
            # Calculate collaboration score
            collaboration_score = min(100, (messages_sent * 2) + (sessions_participated * 10))
            
            return {
                "active_groups": len(group_ids),
                "messages_sent": messages_sent,
                "sessions_participated": sessions_participated,
                "collaboration_score": collaboration_score
            }
            
        except Exception as e:
            logger.error(f"Error getting user group analytics: {e}")
            return {}
    
    async def _analyze_learning_patterns(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Analyze learning patterns and habits"""
        try:
            # Get activity timeline
            activities = []
            
            # Assessment activities
            assessments = list(self.assessments_collection.find({
                "user_id": user_id,
                "created_at": {"$gte": since_date}
            }, {"created_at": 1, "subject": 1}))
            
            for assessment in assessments:
                activities.append({
                    "date": assessment["created_at"].date(),
                    "type": "assessment",
                    "subject": assessment.get("subject")
                })
            
            # Content generation activities
            content = list(self.content_collection.find({
                "user_id": user_id,
                "created_at": {"$gte": since_date}
            }, {"created_at": 1, "content_type": 1}))
            
            for content_item in content:
                activities.append({
                    "date": content_item["created_at"].date(),
                    "type": "content_generation",
                    "content_type": content_item.get("content_type")
                })
            
            # Calculate patterns
            daily_activity = defaultdict(int)
            hourly_activity = defaultdict(int)
            subject_frequency = defaultdict(int)
            
            for activity in activities:
                daily_activity[activity["date"]] += 1
                if hasattr(activity["date"], "hour"):
                    hourly_activity[activity["date"].hour] += 1
                
                if "subject" in activity:
                    subject_frequency[activity["subject"]] += 1
            
            active_days = len(daily_activity)
            avg_daily_activity = sum(daily_activity.values()) / max(active_days, 1)
            
            # Find peak activity hour
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 12
            
            # Most studied subject
            favorite_subject = max(subject_frequency.items(), key=lambda x: x[1])[0] if subject_frequency else "None"
            
            return {
                "active_days": active_days,
                "avg_daily_activities": round(avg_daily_activity, 1),
                "peak_activity_hour": peak_hour,
                "favorite_subject": favorite_subject,
                "learning_consistency": min(100, (active_days / max(since_date.days if hasattr(since_date, 'days') else 30, 1)) * 100)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
            return {}
    
    async def _calculate_performance_trends(
        self, 
        user_id: str, 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        try:
            # Get chronological assessment data
            assessments = list(self.assessments_collection.find({
                "user_id": user_id,
                "created_at": {"$gte": since_date}
            }).sort("created_at", 1))
            
            if len(assessments) < 2:
                return {
                    "trend": "insufficient_data",
                    "improvement_rate": 0,
                    "consistency": 0
                }
            
            scores = [assessment.get("final_score", 0) for assessment in assessments]
            abilities = [assessment.get("final_ability_estimate", 0) for assessment in assessments]
            
            # Calculate trend
            if len(scores) >= 3:
                recent_scores = scores[-3:]
                earlier_scores = scores[:-3] if len(scores) > 3 else scores[:1]
                
                recent_avg = sum(recent_scores) / len(recent_scores)
                earlier_avg = sum(earlier_scores) / len(earlier_scores)
                
                improvement_rate = ((recent_avg - earlier_avg) / max(earlier_avg, 1)) * 100
                
                if improvement_rate > 5:
                    trend = "improving"
                elif improvement_rate < -5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
                improvement_rate = 0
            
            # Calculate consistency (lower standard deviation = more consistent)
            consistency = 100 - min(100, np.std(scores) if len(scores) > 1 else 0)
            
            return {
                "trend": trend,
                "improvement_rate": round(improvement_rate, 2),
                "consistency": round(consistency, 2),
                "latest_score": scores[-1] if scores else 0,
                "latest_ability": abilities[-1] if abilities else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance trends: {e}")
            return {}
    
    async def _generate_learning_recommendations(
        self, 
        user_id: str, 
        assessment_stats: Dict[str, Any],
        content_stats: Dict[str, Any],
        group_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations"""
        try:
            recommendations = []
            
            # Performance-based recommendations
            if assessment_stats.get("accuracy_rate", 0) < 60:
                recommendations.append({
                    "type": "improvement",
                    "priority": "high",
                    "title": "Focus on Fundamental Skills",
                    "description": "Your current accuracy rate is below 60%. Consider reviewing basic concepts and taking practice assessments.",
                    "action": "Take more practice assessments",
                    "icon": "📚"
                })
            
            # Content generation recommendations
            if content_stats.get("total_content", 0) < 5:
                recommendations.append({
                    "type": "engagement",
                    "priority": "medium",
                    "title": "Create More Learning Content",
                    "description": "Generating your own study materials can improve understanding and retention.",
                    "action": "Use the AI Content Generator",
                    "icon": "✨"
                })
            
            # Collaboration recommendations
            if group_stats.get("active_groups", 0) == 0:
                recommendations.append({
                    "type": "collaboration",
                    "priority": "medium",
                    "title": "Join a Study Group",
                    "description": "Collaborative learning can improve your understanding and motivation.",
                    "action": "Browse and join study groups",
                    "icon": "👥"
                })
            
            # Activity recommendations
            if assessment_stats.get("total_assessments", 0) < 3:
                recommendations.append({
                    "type": "activity",
                    "priority": "medium",
                    "title": "Take Regular Assessments",
                    "description": "Regular assessment helps track your progress and identify areas for improvement.",
                    "action": "Take an adaptive assessment",
                    "icon": "🎯"
                })
            
            # Subject diversity recommendations
            subjects_studied = assessment_stats.get("subjects_studied", [])
            if len(subjects_studied) < 2:
                recommendations.append({
                    "type": "diversity",
                    "priority": "low",
                    "title": "Explore Different Subjects",
                    "description": "Studying multiple subjects can improve overall learning and critical thinking skills.",
                    "action": "Try assessments in new subjects",
                    "icon": "🌟"
                })
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating learning recommendations: {e}")
            return []
    
    # EDUCATOR ANALYTICS
    async def get_educator_dashboard(
        self,
        educator_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard for educators"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all students (in a real system, this would be filtered by class/group)
            students = list(self.users_collection.find({
                "role": {"$in": ["student"]}
            }))
            
            student_ids = [student["id"] for student in students]
            
            # Aggregate student performance
            class_performance = await self._get_class_performance_analytics(student_ids, since_date)
            
            # Subject analytics
            subject_analytics = await self._get_subject_performance_analytics(student_ids, since_date)
            
            # Engagement analytics  
            engagement_analytics = await self._get_student_engagement_analytics(student_ids, since_date)
            
            # At-risk students
            at_risk_students = await self._identify_at_risk_students(student_ids, since_date)
            
            # Progress tracking
            progress_tracking = await self._track_student_progress(student_ids, since_date)
            
            return {
                "summary": {
                    "total_students": len(students),
                    "active_students": class_performance.get("active_students", 0),
                    "avg_class_performance": class_performance.get("average_performance", 0),
                    "at_risk_count": len(at_risk_students)
                },
                "class_performance": class_performance,
                "subject_analytics": subject_analytics,
                "engagement_analytics": engagement_analytics,
                "at_risk_students": at_risk_students,
                "progress_tracking": progress_tracking,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting educator dashboard: {e}")
            return {"error": str(e)}
    
    async def _get_class_performance_analytics(
        self, 
        student_ids: List[str], 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Get class-wide performance analytics"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": {"$in": student_ids},
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "avg_score": {"$avg": "$final_score"},
                        "assessment_count": {"$sum": 1},
                        "latest_assessment": {"$max": "$created_at"}
                    }
                }
            ]
            
            results = list(self.assessments_collection.aggregate(pipeline))
            
            if not results:
                return {
                    "active_students": 0,
                    "average_performance": 0,
                    "performance_distribution": {},
                    "top_performers": [],
                    "needs_attention": []
                }
            
            active_students = len(results)
            all_scores = [result["avg_score"] for result in results]
            average_performance = sum(all_scores) / len(all_scores)
            
            # Performance distribution
            distribution = {
                "excellent": len([s for s in all_scores if s >= 90]),
                "good": len([s for s in all_scores if 70 <= s < 90]),
                "satisfactory": len([s for s in all_scores if 50 <= s < 70]),
                "needs_improvement": len([s for s in all_scores if s < 50])
            }
            
            # Top performers (top 20%)
            sorted_results = sorted(results, key=lambda x: x["avg_score"], reverse=True)
            top_count = max(1, len(sorted_results) // 5)
            top_performers = sorted_results[:top_count]
            
            # Students needing attention (bottom 20%)
            needs_attention = sorted_results[-top_count:]
            
            return {
                "active_students": active_students,
                "average_performance": round(average_performance, 2),
                "performance_distribution": distribution,
                "top_performers": [{"user_id": tp["_id"], "avg_score": round(tp["avg_score"], 2)} for tp in top_performers],
                "needs_attention": [{"user_id": na["_id"], "avg_score": round(na["avg_score"], 2)} for na in needs_attention]
            }
            
        except Exception as e:
            logger.error(f"Error getting class performance analytics: {e}")
            return {}
    
    async def _get_subject_performance_analytics(
        self, 
        student_ids: List[str], 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Get performance analytics by subject"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": {"$in": student_ids},
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$subject",
                        "avg_score": {"$avg": "$final_score"},
                        "assessment_count": {"$sum": 1},
                        "student_count": {"$addToSet": "$user_id"}
                    }
                },
                {
                    "$project": {
                        "subject": "$_id",
                        "avg_score": 1,
                        "assessment_count": 1,
                        "student_count": {"$size": "$student_count"}
                    }
                }
            ]
            
            results = list(self.assessments_collection.aggregate(pipeline))
            
            subject_data = {}
            for result in results:
                subject = result["subject"]
                subject_data[subject] = {
                    "avg_score": round(result["avg_score"], 2),
                    "assessment_count": result["assessment_count"],
                    "student_count": result["student_count"]
                }
            
            return subject_data
            
        except Exception as e:
            logger.error(f"Error getting subject performance analytics: {e}")
            return {}
    
    async def _get_student_engagement_analytics(
        self, 
        student_ids: List[str], 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Get student engagement analytics"""
        try:
            # Assessment engagement
            assessment_engagement = self.assessments_collection.count_documents({
                "user_id": {"$in": student_ids},
                "created_at": {"$gte": since_date}
            })
            
            # Content generation engagement
            content_engagement = self.content_collection.count_documents({
                "user_id": {"$in": student_ids},
                "created_at": {"$gte": since_date}
            })
            
            # Group participation
            group_participation = self.messages_collection.count_documents({
                "user_id": {"$in": student_ids},
                "timestamp": {"$gte": since_date}
            })
            
            return {
                "total_assessments": assessment_engagement,
                "total_content_generated": content_engagement,
                "total_group_messages": group_participation,
                "engagement_score": min(100, (assessment_engagement * 2) + content_engagement + (group_participation * 0.5))
            }
            
        except Exception as e:
            logger.error(f"Error getting student engagement analytics: {e}")
            return {}
    
    async def _identify_at_risk_students(
        self, 
        student_ids: List[str], 
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """Identify students who may be at risk"""
        try:
            at_risk_students = []
            
            for student_id in student_ids:
                # Get recent assessments
                recent_assessments = list(self.assessments_collection.find({
                    "user_id": student_id,
                    "created_at": {"$gte": since_date}
                }).sort("created_at", -1).limit(3))
                
                if not recent_assessments:
                    # No recent activity
                    at_risk_students.append({
                        "user_id": student_id,
                        "risk_type": "inactive",
                        "description": "No recent assessment activity",
                        "priority": "medium"
                    })
                    continue
                
                # Check performance decline
                if len(recent_assessments) >= 2:
                    scores = [assessment["final_score"] for assessment in recent_assessments]
                    if scores[0] < scores[-1] - 20:  # Recent score is 20 points lower
                        at_risk_students.append({
                            "user_id": student_id,
                            "risk_type": "declining_performance",
                            "description": f"Performance dropped from {scores[-1]:.1f} to {scores[0]:.1f}",
                            "priority": "high"
                        })
                
                # Check consistently low performance
                avg_score = sum(assessment["final_score"] for assessment in recent_assessments) / len(recent_assessments)
                if avg_score < 50:
                    at_risk_students.append({
                        "user_id": student_id,
                        "risk_type": "low_performance",
                        "description": f"Average score: {avg_score:.1f}%",
                        "priority": "high"
                    })
            
            return at_risk_students
            
        except Exception as e:
            logger.error(f"Error identifying at-risk students: {e}")
            return []
    
    async def _track_student_progress(
        self, 
        student_ids: List[str], 
        since_date: datetime
    ) -> Dict[str, Any]:
        """Track overall student progress"""
        try:
            # Get assessment data over time
            pipeline = [
                {
                    "$match": {
                        "user_id": {"$in": student_ids},
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "user_id": "$user_id",
                            "week": {"$week": "$created_at"}
                        },
                        "avg_weekly_score": {"$avg": "$final_score"},
                        "assessment_count": {"$sum": 1}
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.week",
                        "avg_class_score": {"$avg": "$avg_weekly_score"},
                        "active_students": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            
            weekly_progress = list(self.assessments_collection.aggregate(pipeline))
            
            return {
                "weekly_progress": weekly_progress,
                "trend": "improving" if len(weekly_progress) >= 2 and 
                        weekly_progress[-1]["avg_class_score"] > weekly_progress[0]["avg_class_score"] 
                        else "stable"
            }
            
        except Exception as e:
            logger.error(f"Error tracking student progress: {e}")
            return {}