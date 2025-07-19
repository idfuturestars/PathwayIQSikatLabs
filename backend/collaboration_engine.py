"""
Study Groups & Collaborative Learning Engine for IDFS PathwayIQ™ powered by SikatLabs™

This module handles collaborative learning features including:
- Study group creation and management
- Peer-to-peer learning activities
- Group discussions and forums
- Collaborative projects and assignments
- Social learning features
- Group performance analytics
- Mentoring and peer support systems
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
import uuid
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroupType(str, Enum):
    STUDY_GROUP = "study_group"
    PROJECT_TEAM = "project_team"
    DISCUSSION_FORUM = "discussion_forum"
    PEER_SUPPORT = "peer_support"
    MENTORING_CIRCLE = "mentoring_circle"

class GroupStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PRIVATE = "private"

class MembershipRole(str, Enum):
    OWNER = "owner"
    MODERATOR = "moderator"
    MEMBER = "member"
    OBSERVER = "observer"

class ActivityType(str, Enum):
    DISCUSSION = "discussion"
    STUDY_SESSION = "study_session"
    QUIZ_COLLABORATION = "quiz_collaboration"
    PEER_REVIEW = "peer_review"
    GROUP_PROJECT = "group_project"
    MENTORING_SESSION = "mentoring_session"

class CollaborationEngine:
    def __init__(self):
        """Initialize the Collaboration Engine with database connection"""
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable is required")
        
        db_name = os.environ.get('DB_NAME', 'idfs_pathwayiq_database')
        
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        
        # Collections for collaboration features
        self.users_collection = self.db.users
        self.groups_collection = self.db.study_groups
        self.memberships_collection = self.db.group_memberships
        self.activities_collection = self.db.group_activities
        self.discussions_collection = self.db.group_discussions
        self.projects_collection = self.db.group_projects
        
        logger.info("Collaboration Engine initialized successfully")

    def create_study_group(self, creator_id: str, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new study group"""
        try:
            # Validate creator exists
            creator = self.users_collection.find_one({"user_id": creator_id})
            if not creator:
                return {"error": "Creator not found"}

            group_id = str(uuid.uuid4())
            
            # Create group document
            group_doc = {
                "group_id": group_id,
                "name": group_data.get("name", "New Study Group"),
                "description": group_data.get("description", ""),
                "subject": group_data.get("subject", "general"),
                "group_type": GroupType(group_data.get("group_type", GroupType.STUDY_GROUP)),
                "status": GroupStatus.ACTIVE,
                "creator_id": creator_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "settings": {
                    "max_members": group_data.get("max_members", 10),
                    "is_public": group_data.get("is_public", True),
                    "allow_member_invites": group_data.get("allow_member_invites", True),
                    "require_approval": group_data.get("require_approval", False),
                    "enable_discussions": group_data.get("enable_discussions", True),
                    "enable_projects": group_data.get("enable_projects", True)
                },
                "tags": group_data.get("tags", []),
                "learning_objectives": group_data.get("learning_objectives", []),
                "schedule": group_data.get("schedule", {}),
                "member_count": 1,
                "activity_count": 0,
                "last_activity": datetime.now()
            }

            # Insert group
            self.groups_collection.insert_one(group_doc)

            # Add creator as owner
            membership_doc = {
                "membership_id": str(uuid.uuid4()),
                "group_id": group_id,
                "user_id": creator_id,
                "role": MembershipRole.OWNER,
                "joined_at": datetime.now(),
                "status": "active",
                "contributions": {
                    "posts": 0,
                    "discussions_started": 0,
                    "projects_created": 0,
                    "peer_reviews": 0
                },
                "permissions": {
                    "can_invite": True,
                    "can_moderate": True,
                    "can_manage_settings": True,
                    "can_archive": True
                }
            }

            self.memberships_collection.insert_one(membership_doc)

            return {
                "success": True,
                "group_id": group_id,
                "group": group_doc,
                "message": f"Study group '{group_doc['name']}' created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating study group: {str(e)}")
            return {"error": "Failed to create study group"}

    def join_study_group(self, user_id: str, group_id: str, join_request: Dict[str, Any] = None) -> Dict[str, Any]:
        """Join a study group"""
        try:
            # Validate user and group exist
            user = self.users_collection.find_one({"id": user_id})
            group = self.groups_collection.find_one({"group_id": group_id})
            
            if not user:
                return {"error": "User not found"}
            if not group:
                return {"error": "Group not found"}

            # Check if user is already a member
            existing_membership = self.memberships_collection.find_one({
                "group_id": group_id,
                "user_id": user_id
            })
            
            if existing_membership:
                return {"error": "User is already a member of this group"}

            # Check group capacity
            if group["member_count"] >= group["settings"]["max_members"]:
                return {"error": "Group is at maximum capacity"}

            # Create membership
            membership_id = str(uuid.uuid4())
            
            membership_doc = {
                "membership_id": membership_id,
                "group_id": group_id,
                "user_id": user_id,
                "role": MembershipRole.MEMBER,
                "joined_at": datetime.now(),
                "status": "pending" if group["settings"]["require_approval"] else "active",
                "join_message": join_request.get("message", "") if join_request else "",
                "contributions": {
                    "posts": 0,
                    "discussions_started": 0,
                    "projects_created": 0,
                    "peer_reviews": 0
                },
                "permissions": {
                    "can_invite": group["settings"]["allow_member_invites"],
                    "can_moderate": False,
                    "can_manage_settings": False,
                    "can_archive": False
                }
            }

            self.memberships_collection.insert_one(membership_doc)

            # Update group member count if approved
            if membership_doc["status"] == "active":
                self.groups_collection.update_one(
                    {"group_id": group_id},
                    {
                        "$inc": {"member_count": 1},
                        "$set": {"updated_at": datetime.now(), "last_activity": datetime.now()}
                    }
                )

            # Log activity
            self._log_group_activity(group_id, user_id, ActivityType.DISCUSSION, {
                "action": "joined_group",
                "user_name": user.get("username", "Unknown")
            })

            return {
                "success": True,
                "membership_id": membership_id,
                "status": membership_doc["status"],
                "message": "Successfully joined the group" if membership_doc["status"] == "active" else "Join request submitted for approval"
            }

        except Exception as e:
            logger.error(f"Error joining study group: {str(e)}")
            return {"error": "Failed to join study group"}

    def get_user_groups(self, user_id: str, status: str = "active") -> Dict[str, Any]:
        """Get all groups a user belongs to"""
        try:
            # Get user's memberships
            memberships = list(self.memberships_collection.find({
                "user_id": user_id,
                "status": status
            }))

            groups = []
            for membership in memberships:
                # Get group details
                group = self.groups_collection.find_one({"group_id": membership["group_id"]})
                if group:
                    # Add membership info to group
                    group["user_role"] = membership["role"]
                    group["joined_at"] = membership["joined_at"]
                    group["contributions"] = membership["contributions"]
                    
                    # Remove MongoDB ObjectId for JSON serialization
                    if "_id" in group:
                        del group["_id"]
                    
                    groups.append(group)

            return {
                "success": True,
                "groups": groups,
                "total_groups": len(groups)
            }

        except Exception as e:
            logger.error(f"Error getting user groups: {str(e)}")
            return {"error": "Failed to retrieve user groups"}

    def get_group_details(self, group_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get detailed information about a study group"""
        try:
            group = self.groups_collection.find_one({"group_id": group_id})
            if not group:
                return {"error": "Group not found"}

            # Remove MongoDB ObjectId
            if "_id" in group:
                del group["_id"]

            # Get group members
            memberships = list(self.memberships_collection.find({"group_id": group_id}))
            
            members = []
            for membership in memberships:
                user = self.users_collection.find_one({"user_id": membership["user_id"]})
                if user:
                    members.append({
                        "user_id": membership["user_id"],
                        "username": user.get("username", "Unknown"),
                        "role": membership["role"],
                        "joined_at": membership["joined_at"],
                        "contributions": membership["contributions"],
                        "status": membership["status"]
                    })

            # Get recent activities
            recent_activities = list(self.activities_collection.find(
                {"group_id": group_id}
            ).sort("timestamp", -1).limit(10))

            # Remove MongoDB ObjectIds
            for activity in recent_activities:
                if "_id" in activity:
                    del activity["_id"]

            # Check if user is a member (if user_id provided)
            user_membership = None
            if user_id:
                user_membership = self.memberships_collection.find_one({
                    "group_id": group_id,
                    "user_id": user_id
                })

            return {
                "success": True,
                "group": group,
                "members": members,
                "recent_activities": recent_activities,
                "user_membership": user_membership,
                "is_member": user_membership is not None
            }

        except Exception as e:
            logger.error(f"Error getting group details: {str(e)}")
            return {"error": "Failed to retrieve group details"}

    def search_groups(self, search_params: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Search for study groups based on criteria"""
        try:
            query = {"status": GroupStatus.ACTIVE}
            
            # Build search query
            if search_params.get("name"):
                query["name"] = {"$regex": search_params["name"], "$options": "i"}
            
            if search_params.get("subject"):
                query["subject"] = search_params["subject"]
            
            if search_params.get("group_type"):
                query["group_type"] = search_params["group_type"]
            
            if search_params.get("tags"):
                query["tags"] = {"$in": search_params["tags"]}
            
            if search_params.get("is_public") is not None:
                query["settings.is_public"] = search_params["is_public"]

            # Execute search
            groups = list(self.groups_collection.find(query).limit(50))

            # Remove MongoDB ObjectIds and add additional info
            for group in groups:
                if "_id" in group:
                    del group["_id"]
                
                # Add membership status if user_id provided
                if user_id:
                    membership = self.memberships_collection.find_one({
                        "group_id": group["group_id"],
                        "user_id": user_id
                    })
                    group["user_is_member"] = membership is not None
                    group["user_role"] = membership["role"] if membership else None

            return {
                "success": True,
                "groups": groups,
                "total_results": len(groups),
                "search_params": search_params
            }

        except Exception as e:
            logger.error(f"Error searching groups: {str(e)}")
            return {"error": "Failed to search groups"}

    def create_discussion(self, group_id: str, user_id: str, discussion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a discussion in a study group"""
        try:
            # Verify user is a group member
            membership = self.memberships_collection.find_one({
                "group_id": group_id,
                "user_id": user_id,
                "status": "active"
            })
            
            if not membership:
                return {"error": "User is not a member of this group"}

            discussion_id = str(uuid.uuid4())
            
            discussion_doc = {
                "discussion_id": discussion_id,
                "group_id": group_id,
                "created_by": user_id,
                "title": discussion_data.get("title", "New Discussion"),
                "content": discussion_data.get("content", ""),
                "category": discussion_data.get("category", "general"),
                "tags": discussion_data.get("tags", []),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "reply_count": 0,
                "like_count": 0,
                "view_count": 0,
                "is_pinned": False,
                "is_locked": False,
                "last_reply_at": None,
                "last_reply_by": None
            }

            self.discussions_collection.insert_one(discussion_doc)

            # Update user contributions
            self.memberships_collection.update_one(
                {"membership_id": membership["membership_id"]},
                {"$inc": {"contributions.discussions_started": 1}}
            )

            # Update group activity
            self.groups_collection.update_one(
                {"group_id": group_id},
                {
                    "$inc": {"activity_count": 1},
                    "$set": {"last_activity": datetime.now()}
                }
            )

            # Log activity
            self._log_group_activity(group_id, user_id, ActivityType.DISCUSSION, {
                "action": "created_discussion",
                "discussion_title": discussion_doc["title"]
            })

            return {
                "success": True,
                "discussion_id": discussion_id,
                "discussion": discussion_doc,
                "message": "Discussion created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating discussion: {str(e)}")
            return {"error": "Failed to create discussion"}

    def get_group_discussions(self, group_id: str, user_id: str = None, limit: int = 20) -> Dict[str, Any]:
        """Get discussions for a study group"""
        try:
            # Verify access if user_id provided
            if user_id:
                membership = self.memberships_collection.find_one({
                    "group_id": group_id,
                    "user_id": user_id,
                    "status": "active"
                })
                
                if not membership:
                    return {"error": "Access denied"}

            # Get discussions
            discussions = list(self.discussions_collection.find(
                {"group_id": group_id}
            ).sort("created_at", -1).limit(limit))

            # Remove MongoDB ObjectIds and add user info
            for discussion in discussions:
                if "_id" in discussion:
                    del discussion["_id"]
                
                # Get creator info
                creator = self.users_collection.find_one({"user_id": discussion["created_by"]})
                discussion["created_by_name"] = creator.get("username", "Unknown") if creator else "Unknown"

            return {
                "success": True,
                "discussions": discussions,
                "total_discussions": len(discussions)
            }

        except Exception as e:
            logger.error(f"Error getting group discussions: {str(e)}")
            return {"error": "Failed to retrieve discussions"}

    def create_group_project(self, group_id: str, creator_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a collaborative project in a study group"""
        try:
            # Verify user is a group member with appropriate permissions
            membership = self.memberships_collection.find_one({
                "group_id": group_id,
                "user_id": creator_id,
                "status": "active"
            })
            
            if not membership:
                return {"error": "User is not a member of this group"}

            project_id = str(uuid.uuid4())
            
            project_doc = {
                "project_id": project_id,
                "group_id": group_id,
                "created_by": creator_id,
                "title": project_data.get("title", "New Project"),
                "description": project_data.get("description", ""),
                "objectives": project_data.get("objectives", []),
                "due_date": project_data.get("due_date"),
                "status": "active",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "team_members": [creator_id],  # Creator is automatically part of the team
                "tasks": [],
                "resources": project_data.get("resources", []),
                "deliverables": project_data.get("deliverables", []),
                "collaboration_tools": project_data.get("collaboration_tools", []),
                "progress": {
                    "completion_percentage": 0,
                    "tasks_completed": 0,
                    "tasks_total": 0,
                    "milestones_reached": 0
                }
            }

            self.projects_collection.insert_one(project_doc)

            # Update user contributions
            self.memberships_collection.update_one(
                {"membership_id": membership["membership_id"]},
                {"$inc": {"contributions.projects_created": 1}}
            )

            # Log activity
            self._log_group_activity(group_id, creator_id, ActivityType.GROUP_PROJECT, {
                "action": "created_project",
                "project_title": project_doc["title"]
            })

            return {
                "success": True,
                "project_id": project_id,
                "project": project_doc,
                "message": "Project created successfully"
            }

        except Exception as e:
            logger.error(f"Error creating group project: {str(e)}")
            return {"error": "Failed to create project"}

    def get_group_projects(self, group_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get all projects for a study group"""
        try:
            # Verify access if user_id provided
            if user_id:
                membership = self.memberships_collection.find_one({
                    "group_id": group_id,
                    "user_id": user_id,
                    "status": "active"
                })
                
                if not membership:
                    return {"error": "Access denied"}

            # Get projects
            projects = list(self.projects_collection.find({"group_id": group_id}))

            # Remove MongoDB ObjectIds and add additional info
            for project in projects:
                if "_id" in project:
                    del project["_id"]
                
                # Get creator info
                creator = self.users_collection.find_one({"user_id": project["created_by"]})
                project["created_by_name"] = creator.get("username", "Unknown") if creator else "Unknown"
                
                # Add team member names
                team_member_names = []
                for member_id in project["team_members"]:
                    member = self.users_collection.find_one({"user_id": member_id})
                    if member:
                        team_member_names.append(member.get("username", "Unknown"))
                project["team_member_names"] = team_member_names

            return {
                "success": True,
                "projects": projects,
                "total_projects": len(projects)
            }

        except Exception as e:
            logger.error(f"Error getting group projects: {str(e)}")
            return {"error": "Failed to retrieve projects"}

    def get_collaboration_analytics(self, group_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get analytics for collaboration in a study group"""
        try:
            # Verify access if user_id provided
            if user_id:
                membership = self.memberships_collection.find_one({
                    "group_id": group_id,
                    "user_id": user_id,
                    "status": "active"
                })
                
                if not membership:
                    return {"error": "Access denied"}

            # Get group info
            group = self.groups_collection.find_one({"group_id": group_id})
            if not group:
                return {"error": "Group not found"}

            # Get member analytics
            members = list(self.memberships_collection.find({"group_id": group_id, "status": "active"}))
            
            # Get activity analytics
            activities = list(self.activities_collection.find({"group_id": group_id}))
            discussions = list(self.discussions_collection.find({"group_id": group_id}))
            projects = list(self.projects_collection.find({"group_id": group_id}))

            # Calculate analytics
            analytics = {
                "group_overview": {
                    "group_id": group_id,
                    "group_name": group["name"],
                    "total_members": len(members),
                    "total_activities": len(activities),
                    "total_discussions": len(discussions),
                    "total_projects": len(projects),
                    "group_age_days": (datetime.now() - group["created_at"]).days,
                    "last_activity": group.get("last_activity")
                },
                "member_engagement": {
                    "active_members": len([m for m in members if m["status"] == "active"]),
                    "top_contributors": self._get_top_contributors(members, 5),
                    "average_contributions_per_member": self._calculate_average_contributions(members)
                },
                "activity_breakdown": {
                    "discussions_per_week": self._calculate_activity_frequency(discussions, "weekly"),
                    "projects_active": len([p for p in projects if p["status"] == "active"]),
                    "recent_activity_trend": self._analyze_activity_trend(activities, 30)
                },
                "collaboration_quality": {
                    "peer_interaction_score": self._calculate_peer_interaction_score(group_id),
                    "knowledge_sharing_index": self._calculate_knowledge_sharing_index(discussions),
                    "project_completion_rate": self._calculate_project_completion_rate(projects)
                },
                "generated_at": datetime.now()
            }

            return {
                "success": True,
                "analytics": analytics
            }

        except Exception as e:
            logger.error(f"Error getting collaboration analytics: {str(e)}")
            return {"error": "Failed to retrieve collaboration analytics"}

    def _log_group_activity(self, group_id: str, user_id: str, activity_type: ActivityType, details: Dict[str, Any]):
        """Log an activity in the group"""
        try:
            activity_doc = {
                "activity_id": str(uuid.uuid4()),
                "group_id": group_id,
                "user_id": user_id,
                "activity_type": activity_type,
                "details": details,
                "timestamp": datetime.now()
            }
            
            self.activities_collection.insert_one(activity_doc)
            
        except Exception as e:
            logger.error(f"Error logging group activity: {str(e)}")

    def _get_top_contributors(self, members: List[Dict], limit: int) -> List[Dict]:
        """Get top contributors based on their contributions"""
        try:
            # Calculate contribution scores
            for member in members:
                contributions = member.get("contributions", {})
                score = (
                    contributions.get("posts", 0) * 1 +
                    contributions.get("discussions_started", 0) * 3 +
                    contributions.get("projects_created", 0) * 5 +
                    contributions.get("peer_reviews", 0) * 2
                )
                member["contribution_score"] = score

            # Sort and return top contributors
            top_contributors = sorted(members, key=lambda x: x.get("contribution_score", 0), reverse=True)
            
            # Get user names
            result = []
            for member in top_contributors[:limit]:
                user = self.users_collection.find_one({"user_id": member["user_id"]})
                result.append({
                    "user_id": member["user_id"],
                    "username": user.get("username", "Unknown") if user else "Unknown",
                    "contribution_score": member["contribution_score"],
                    "contributions": member.get("contributions", {})
                })

            return result

        except Exception as e:
            logger.error(f"Error getting top contributors: {str(e)}")
            return []

    def _calculate_average_contributions(self, members: List[Dict]) -> Dict[str, float]:
        """Calculate average contributions per member"""
        if not members:
            return {}

        total_posts = sum(m.get("contributions", {}).get("posts", 0) for m in members)
        total_discussions = sum(m.get("contributions", {}).get("discussions_started", 0) for m in members)
        total_projects = sum(m.get("contributions", {}).get("projects_created", 0) for m in members)
        total_reviews = sum(m.get("contributions", {}).get("peer_reviews", 0) for m in members)

        member_count = len(members)
        
        return {
            "avg_posts": round(total_posts / member_count, 2),
            "avg_discussions": round(total_discussions / member_count, 2),
            "avg_projects": round(total_projects / member_count, 2),
            "avg_peer_reviews": round(total_reviews / member_count, 2)
        }

    def _calculate_activity_frequency(self, items: List[Dict], frequency: str) -> float:
        """Calculate activity frequency (per week/month)"""
        if not items:
            return 0.0

        # Get the date range
        dates = [item["created_at"] for item in items if "created_at" in item]
        if not dates:
            return 0.0

        oldest_date = min(dates)
        newest_date = max(dates)
        
        if frequency == "weekly":
            weeks = max(1, (newest_date - oldest_date).days / 7)
            return round(len(items) / weeks, 2)
        elif frequency == "monthly":
            months = max(1, (newest_date - oldest_date).days / 30)
            return round(len(items) / months, 2)
        
        return 0.0

    def _analyze_activity_trend(self, activities: List[Dict], days: int) -> str:
        """Analyze activity trend over the last N days"""
        if not activities:
            return "insufficient_data"

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_activities = [a for a in activities if a.get("timestamp", datetime.now()) >= cutoff_date]
        
        if len(recent_activities) == 0:
            return "inactive"
        elif len(recent_activities) > len(activities) * 0.7:
            return "increasing"
        elif len(recent_activities) < len(activities) * 0.3:
            return "decreasing"
        else:
            return "stable"

    def _calculate_peer_interaction_score(self, group_id: str) -> float:
        """Calculate a score representing peer interaction quality"""
        try:
            # This is a simplified calculation
            # In a full implementation, you would analyze discussion replies, 
            # project collaborations, peer reviews, etc.
            
            discussions = list(self.discussions_collection.find({"group_id": group_id}))
            projects = list(self.projects_collection.find({"group_id": group_id}))
            
            interaction_score = 0.0
            
            # Score based on discussions with replies
            discussion_score = sum(min(d.get("reply_count", 0) * 0.1, 1.0) for d in discussions)
            
            # Score based on collaborative projects
            project_score = sum(len(p.get("team_members", [])) * 0.2 for p in projects)
            
            # Combine scores (max score is 5.0)
            interaction_score = min(discussion_score + project_score, 5.0)
            
            return round(interaction_score, 2)

        except Exception as e:
            logger.error(f"Error calculating peer interaction score: {str(e)}")
            return 0.0

    def _calculate_knowledge_sharing_index(self, discussions: List[Dict]) -> float:
        """Calculate an index representing knowledge sharing quality"""
        if not discussions:
            return 0.0

        # Simple calculation based on discussion engagement
        total_score = 0.0
        for discussion in discussions:
            view_score = min(discussion.get("view_count", 0) * 0.01, 0.5)
            reply_score = min(discussion.get("reply_count", 0) * 0.1, 1.0)
            like_score = min(discussion.get("like_count", 0) * 0.05, 0.5)
            
            total_score += view_score + reply_score + like_score

        # Normalize to 0-5 scale
        knowledge_index = min(total_score / max(len(discussions), 1), 5.0)
        return round(knowledge_index, 2)

    def _calculate_project_completion_rate(self, projects: List[Dict]) -> float:
        """Calculate project completion rate"""
        if not projects:
            return 0.0

        completed_projects = len([p for p in projects if p.get("status") == "completed"])
        completion_rate = (completed_projects / len(projects)) * 100
        
        return round(completion_rate, 2)

    def leave_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Leave a study group"""
        try:
            # Find membership
            membership = self.memberships_collection.find_one({
                "group_id": group_id,
                "user_id": user_id,
                "status": "active"
            })
            
            if not membership:
                return {"error": "User is not a member of this group"}

            # Check if user is the owner
            if membership["role"] == MembershipRole.OWNER:
                # Transfer ownership or archive group logic would go here
                return {"error": "Group owner cannot leave. Transfer ownership first."}

            # Remove membership
            self.memberships_collection.delete_one({"membership_id": membership["membership_id"]})

            # Update group member count
            self.groups_collection.update_one(
                {"group_id": group_id},
                {
                    "$inc": {"member_count": -1},
                    "$set": {"updated_at": datetime.now()}
                }
            )

            # Log activity
            self._log_group_activity(group_id, user_id, ActivityType.DISCUSSION, {
                "action": "left_group"
            })

            return {
                "success": True,
                "message": "Successfully left the group"
            }

        except Exception as e:
            logger.error(f"Error leaving group: {str(e)}")
            return {"error": "Failed to leave group"}

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Collaboration Engine database connection closed")