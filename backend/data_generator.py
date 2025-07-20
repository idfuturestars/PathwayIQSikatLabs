"""
Data Population System for PathwayIQ ML Model Optimization
Uses OpenAI, Claude (Anthropic), and Google Cloud APIs to generate realistic educational data
"""
import os
import json
import uuid
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import numpy as np

# AI SDK imports
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel
    import vertexai
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)

class EducationalDataGenerator:
    def __init__(self, mongo_url: str):
        self.client = MongoClient(mongo_url)
        db_name = os.getenv('DB_NAME', 'idfs_pathwayiq_database')
        self.db = self.client[db_name]
        
        # Initialize AI clients
        self.openai_client = None
        self.claude_client = None
        self.gemini_model = None
        
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if CLAUDE_AVAILABLE and os.getenv('CLAUDE_API_KEY'):
            self.claude_client = anthropic.AsyncAnthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        
        if GOOGLE_CLOUD_AVAILABLE and os.getenv('GOOGLE_CLOUD_PROJECT'):
            try:
                vertexai.init(project=os.getenv('GOOGLE_CLOUD_PROJECT'), location='us-central1')
                self.gemini_model = GenerativeModel("gemini-pro")
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI: {e}")
        
        # Data generation parameters
        self.subjects = ["mathematics", "science", "english", "history", "computer_science", "physics", "chemistry", "biology"]
        self.assessment_types = ["adaptive", "standard", "quiz", "midterm", "final"]
        self.content_types = ["quiz", "lesson", "explanation", "practice_problems", "study_guide", "flashcards"]
        
        # Student personas for realistic data
        self.student_personas = [
            {"learning_style": "visual", "performance_level": "high", "engagement": "high"},
            {"learning_style": "auditory", "performance_level": "medium", "engagement": "medium"},
            {"learning_style": "kinesthetic", "performance_level": "low", "engagement": "low"},
            {"learning_style": "reading", "performance_level": "high", "engagement": "medium"},
            {"learning_style": "visual", "performance_level": "medium", "engagement": "high"}
        ]
    
    async def generate_comprehensive_dataset(
        self,
        num_users: int = 100,
        num_assessments_per_user: int = 20,
        num_content_per_user: int = 10,
        num_groups: int = 20
    ) -> Dict[str, Any]:
        """Generate comprehensive educational dataset for ML training"""
        try:
            logger.info(f"Starting comprehensive data generation: {num_users} users, {num_assessments_per_user} assessments each")
            
            results = {
                "users_generated": 0,
                "assessments_generated": 0,
                "content_generated": 0,
                "groups_generated": 0,
                "speech_sessions_generated": 0,
                "emotional_profiles_generated": 0,
                "errors": []
            }
            
            # Generate users
            users = await self._generate_synthetic_users(num_users)
            results["users_generated"] = len(users)
            
            # Generate assessments for each user
            for user in users:
                try:
                    user_assessments = await self._generate_user_assessments(
                        user["id"], num_assessments_per_user
                    )
                    results["assessments_generated"] += len(user_assessments)
                    
                    # Generate content for user
                    user_content = await self._generate_user_content(
                        user["id"], num_content_per_user
                    )
                    results["content_generated"] += len(user_content)
                    
                    # Generate emotional profiles
                    emotional_profiles = await self._generate_emotional_profiles(user["id"])
                    results["emotional_profiles_generated"] += len(emotional_profiles)
                    
                    # Generate speech sessions
                    speech_sessions = await self._generate_speech_sessions(user["id"])
                    results["speech_sessions_generated"] += len(speech_sessions)
                    
                except Exception as e:
                    logger.error(f"Error generating data for user {user['id']}: {e}")
                    results["errors"].append(f"User {user['id']}: {str(e)}")
            
            # Generate study groups
            groups = await self._generate_study_groups(num_groups, [u["id"] for u in users])
            results["groups_generated"] = len(groups)
            
            logger.info(f"Data generation complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive data generation: {e}")
            return {"error": str(e)}
    
    async def _generate_synthetic_users(self, count: int) -> List[Dict[str, Any]]:
        """Generate synthetic users using AI"""
        users = []
        
        for i in range(count):
            try:
                # Select random persona
                persona = random.choice(self.student_personas)
                
                # Generate user data using AI
                user_data = await self._generate_user_with_ai(persona, i)
                
                # Create user document
                user_doc = {
                    "id": str(uuid.uuid4()),
                    "username": user_data.get("username", f"student{i+1:03d}"),
                    "email": user_data.get("email", f"student{i+1:03d}@pathwayiq.demo"),
                    "role": "student",
                    "level": random.randint(1, 10),
                    "xp": random.randint(0, 5000),
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    "profile": {
                        "learning_style": persona["learning_style"],
                        "performance_level": persona["performance_level"],
                        "engagement_level": persona["engagement"],
                        "subjects_interested": random.sample(self.subjects, random.randint(2, 5))
                    },
                    "generated_by": "ai_data_generator",
                    "is_synthetic": True
                }
                
                # Insert user into database
                self.db.users.insert_one(user_doc)
                users.append(user_doc)
                
            except Exception as e:
                logger.error(f"Error generating user {i}: {e}")
                continue
        
        return users
    
    async def _generate_user_with_ai(self, persona: Dict[str, str], index: int) -> Dict[str, Any]:
        """Generate user details using AI"""
        try:
            if self.openai_client:
                return await self._generate_user_openai(persona, index)
            elif self.claude_client:
                return await self._generate_user_claude(persona, index)
            elif self.gemini_model:
                return await self._generate_user_gemini(persona, index)
            else:
                # Fallback to rule-based generation
                return {
                    "username": f"student_{persona['learning_style']}_{index:03d}",
                    "email": f"student_{index:03d}@pathwayiq.demo"
                }
        except Exception as e:
            logger.error(f"Error generating user with AI: {e}")
            return {
                "username": f"student{index:03d}",
                "email": f"student{index:03d}@pathwayiq.demo"
            }
    
    async def _generate_user_openai(self, persona: Dict[str, str], index: int) -> Dict[str, Any]:
        """Generate user using OpenAI"""
        try:
            prompt = f"""
            Generate a realistic student profile with the following characteristics:
            - Learning style: {persona['learning_style']}
            - Performance level: {persona['performance_level']}
            - Engagement level: {persona['engagement']}
            
            Return a JSON object with:
            - username (realistic, no spaces)
            - email (realistic student email)
            - full_name (realistic name)
            
            Make it realistic for an educational platform.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data generator for educational platforms. Generate realistic student profiles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"username": f"student{index:03d}", "email": f"student{index:03d}@pathwayiq.demo"}
                
        except Exception as e:
            logger.error(f"OpenAI user generation error: {e}")
            return {"username": f"student{index:03d}", "email": f"student{index:03d}@pathwayiq.demo"}
    
    async def _generate_user_claude(self, persona: Dict[str, str], index: int) -> Dict[str, Any]:
        """Generate user using Claude"""
        try:
            prompt = f"""
            Create a realistic student profile JSON with these traits:
            - Learning style: {persona['learning_style']}
            - Performance: {persona['performance_level']}
            - Engagement: {persona['engagement']}
            
            Format: {{"username": "realistic_name", "email": "student@demo.com", "full_name": "First Last"}}
            """
            
            message = await self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"username": f"student{index:03d}", "email": f"student{index:03d}@pathwayiq.demo"}
                
        except Exception as e:
            logger.error(f"Claude user generation error: {e}")
            return {"username": f"student{index:03d}", "email": f"student{index:03d}@pathwayiq.demo"}
    
    async def _generate_user_gemini(self, persona: Dict[str, str], index: int) -> Dict[str, Any]:
        """Generate user using Gemini"""
        try:
            prompt = f"""
            Generate a student profile JSON for:
            Learning style: {persona['learning_style']}
            Performance: {persona['performance_level']}
            Engagement: {persona['engagement']}
            
            Return JSON: {{"username": "name", "email": "email@demo.com"}}
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"username": f"student{index:03d}", "email": f"student{index:03d}@pathwayiq.demo"}
                
        except Exception as e:
            logger.error(f"Gemini user generation error: {e}")
            return {"username": f"student{index:03d}", "email": f"student{index:03d}@pathwayiq.demo"}
    
    async def _generate_user_assessments(self, user_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate realistic assessment data for a user"""
        assessments = []
        
        # Get user profile to influence assessment generation
        user = self.db.users.find_one({"id": user_id})
        if not user:
            return assessments
        
        performance_level = user.get("profile", {}).get("performance_level", "medium")
        learning_style = user.get("profile", {}).get("learning_style", "visual")
        
        # Base score ranges by performance level
        score_ranges = {
            "high": (80, 95),
            "medium": (60, 80),
            "low": (40, 70)
        }
        
        base_min, base_max = score_ranges.get(performance_level, (60, 80))
        
        for i in range(count):
            try:
                subject = random.choice(self.subjects)
                assessment_type = random.choice(self.assessment_types)
                
                # Generate realistic performance with some variance
                base_score = random.uniform(base_min, base_max)
                # Add some random variance (±10 points)
                final_score = max(0, min(100, base_score + random.uniform(-10, 10)))
                
                # Questions answered/correct based on score
                questions_answered = random.randint(15, 30)
                questions_correct = int(questions_answered * (final_score / 100))
                
                assessment_doc = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "subject": subject,
                    "assessment_type": assessment_type,
                    "final_score": round(final_score, 1),
                    "final_ability_estimate": round(final_score / 10, 2),  # 0-10 scale
                    "questions_answered": questions_answered,
                    "questions_correct": questions_correct,
                    "time_taken": random.randint(300, 3600),  # 5 minutes to 1 hour
                    "created_at": datetime.utcnow() - timedelta(
                        days=random.randint(0, 180),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    ),
                    "metadata": {
                        "learning_style": learning_style,
                        "performance_level": performance_level,
                        "device": random.choice(["desktop", "mobile", "tablet"])
                    },
                    "generated_by": "ai_data_generator",
                    "is_synthetic": True
                }
                
                # Insert assessment
                self.db.assessments.insert_one(assessment_doc)
                assessments.append(assessment_doc)
                
            except Exception as e:
                logger.error(f"Error generating assessment {i} for user {user_id}: {e}")
                continue
        
        return assessments
    
    async def _generate_user_content(self, user_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate content generation records for a user"""
        content_records = []
        
        for i in range(count):
            try:
                content_type = random.choice(self.content_types)
                subject = random.choice(self.subjects)
                
                content_doc = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "content_type": content_type,
                    "subject": subject,
                    "prompt": f"Generate {content_type} for {subject}",
                    "generated_content": f"Sample {content_type} content for {subject}",
                    "quality_score": random.uniform(7.0, 9.5),
                    "usage_count": random.randint(1, 10),
                    "created_at": datetime.utcnow() - timedelta(
                        days=random.randint(0, 90),
                        hours=random.randint(0, 23)
                    ),
                    "generated_by": "ai_data_generator",
                    "is_synthetic": True
                }
                
                self.db.content_generation.insert_one(content_doc)
                content_records.append(content_doc)
                
            except Exception as e:
                logger.error(f"Error generating content {i} for user {user_id}: {e}")
                continue
        
        return content_records
    
    async def _generate_emotional_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate emotional analysis profiles for a user"""
        profiles = []
        
        emotions = ["confidence", "anxiety", "frustration", "engagement", "satisfaction", "fatigue"]
        contexts = ["assessment", "study", "group_work", "think_aloud"]
        
        for i in range(random.randint(10, 25)):  # 10-25 emotional analyses per user
            try:
                # Generate realistic emotional state
                dominant_emotion = random.choice(emotions)
                emotion_scores = {emotion: random.uniform(0, 0.3) for emotion in emotions}
                emotion_scores[dominant_emotion] = random.uniform(0.4, 0.8)  # Make dominant
                
                profile_doc = {
                    "analysis_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "timestamp": datetime.utcnow() - timedelta(
                        days=random.randint(0, 60),
                        hours=random.randint(0, 23)
                    ),
                    "source": "synthetic_generation",
                    "context": random.choice(contexts),
                    "raw_text": f"Sample emotional analysis text showing {dominant_emotion}",
                    "sentiment": {
                        "polarity": random.uniform(-0.5, 0.5),
                        "subjectivity": random.uniform(0.3, 0.8),
                        "classification": random.choice(["positive", "neutral", "negative"])
                    },
                    "emotions": emotion_scores,
                    "dominant_emotion": dominant_emotion,
                    "learning_style_indicators": {
                        "visual": random.uniform(0, 0.3),
                        "auditory": random.uniform(0, 0.3),
                        "kinesthetic": random.uniform(0, 0.3),
                        "reading": random.uniform(0, 0.3)
                    },
                    "cognitive_load": {
                        "level": random.choice(["low", "medium", "high"]),
                        "scores": {
                            "low": random.randint(0, 5),
                            "medium": random.randint(0, 5),
                            "high": random.randint(0, 5)
                        }
                    },
                    "ai_insights": {
                        "emotional_state": dominant_emotion,
                        "confidence_level": random.choice(["low", "medium", "high"]),
                        "learning_engagement": random.choice(["engaged", "neutral", "disengaged"])
                    },
                    "generated_by": "ai_data_generator",
                    "is_synthetic": True
                }
                
                self.db.emotional_profiles.insert_one(profile_doc)
                profiles.append(profile_doc)
                
            except Exception as e:
                logger.error(f"Error generating emotional profile {i} for user {user_id}: {e}")
                continue
        
        return profiles
    
    async def _generate_speech_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate speech-to-text session records"""
        sessions = []
        
        for i in range(random.randint(5, 15)):  # 5-15 speech sessions per user
            try:
                session_doc = {
                    "session_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "transcript": f"This is a sample think-aloud transcript for session {i+1}. The student is working through a problem and expressing their thought process.",
                    "ai_analysis": {
                        "thinking_patterns": ["analytical", "methodical", "creative"],
                        "confidence_level": random.choice(["low", "medium", "high"]),
                        "understanding_indicators": random.choice(["strong", "moderate", "weak"])
                    },
                    "created_at": datetime.utcnow() - timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23)
                    ),
                    "duration_seconds": random.randint(120, 600),  # 2-10 minutes
                    "word_count": random.randint(50, 300),
                    "generated_by": "ai_data_generator",
                    "is_synthetic": True
                }
                
                self.db.speech_sessions.insert_one(session_doc)
                sessions.append(session_doc)
                
            except Exception as e:
                logger.error(f"Error generating speech session {i} for user {user_id}: {e}")
                continue
        
        return sessions
    
    async def _generate_study_groups(self, count: int, user_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate study group records"""
        groups = []
        
        for i in range(count):
            try:
                group_members = random.sample(user_ids, random.randint(3, 8))
                creator_id = group_members[0]
                
                group_doc = {
                    "group_id": str(uuid.uuid4()),
                    "name": f"Study Group {i+1}: {random.choice(self.subjects).title()}",
                    "description": f"Collaborative learning group for {random.choice(self.subjects)}",
                    "subject": random.choice(self.subjects),
                    "created_by": creator_id,
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                    "max_members": random.randint(5, 15),
                    "current_members": len(group_members),
                    "is_public": random.choice([True, False]),
                    "is_active": True,
                    "topics": random.sample(["homework", "test_prep", "project_work", "concept_review"], 2),
                    "generated_by": "ai_data_generator",
                    "is_synthetic": True
                }
                
                self.db.study_groups.insert_one(group_doc)
                
                # Create group members
                for member_id in group_members:
                    member_doc = {
                        "group_id": group_doc["group_id"],
                        "user_id": member_id,
                        "role": "admin" if member_id == creator_id else "member",
                        "joined_at": group_doc["created_at"] + timedelta(days=random.randint(0, 7)),
                        "is_active": True,
                        "generated_by": "ai_data_generator",
                        "is_synthetic": True
                    }
                    self.db.group_members.insert_one(member_doc)
                
                # Generate some group messages
                for msg_i in range(random.randint(5, 20)):
                    message_doc = {
                        "message_id": str(uuid.uuid4()),
                        "group_id": group_doc["group_id"],
                        "user_id": random.choice(group_members),
                        "content": f"Sample group message {msg_i+1} about {group_doc['subject']}",
                        "message_type": "text",
                        "timestamp": group_doc["created_at"] + timedelta(
                            days=random.randint(0, 30),
                            hours=random.randint(0, 23)
                        ),
                        "generated_by": "ai_data_generator",
                        "is_synthetic": True
                    }
                    self.db.group_messages.insert_one(message_doc)
                
                groups.append(group_doc)
                
            except Exception as e:
                logger.error(f"Error generating study group {i}: {e}")
                continue
        
        return groups

# Initialize data generator
def get_data_generator(mongo_url: str) -> EducationalDataGenerator:
    """Get or create educational data generator instance"""
    return EducationalDataGenerator(mongo_url)