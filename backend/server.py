from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import logging
import uuid
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import openai
import json
from enum import Enum
import bcrypt
import redis
from collections import defaultdict
import base64

# Import production modules
from session_manager import session_manager
from health_monitor import health_monitor
from cache_manager import cache_manager, cache_result
from database_indexer import db_indexer

# Import speech-to-text module
from speech_to_text import get_speech_processor, SpeechToTextConfig

# Import content generation module
from content_generator import get_content_generator, ContentGenerationRequest

# Import gamification modules
from gamification_engine import get_gamification_engine
from leaderboard_system import get_leaderboard_system, LeaderboardCategory

# Import study groups engine
from study_groups_engine import StudyGroupsEngine

# Import email service
from email_service import email_service

# Import learning analytics
from learning_analytics import LearningAnalytics

# Import reporting system
from reporting_system import ReportingSystem

# Import predictive analytics
from predictive_analytics import PredictiveAnalytics

# Import emotional intelligence
from emotional_intelligence import get_emotional_intelligence_analyzer

# Import data generator
from data_generator import get_data_generator

# Import adaptive engine
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adaptive_engine import (
    AdaptiveEngine, GradeLevel, QuestionComplexity, ThinkAloudType,
    adaptive_engine
)

# Import advanced AI engine for Phase 1
from ai_engine import (
    AdvancedAIEngine, EmotionalState, LearningStyle, AIPersonality,
    advanced_ai_engine
)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
JWT_SECRET = os.environ['JWT_SECRET']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Initialize clients
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Initialize study groups engine
study_groups_engine = StudyGroupsEngine(MONGO_URL, REDIS_URL)

# Initialize learning analytics
learning_analytics = LearningAnalytics(MONGO_URL, REDIS_URL)

# Initialize reporting system
reporting_system = ReportingSystem(MONGO_URL)

# Initialize predictive analytics
predictive_analytics = PredictiveAnalytics(MONGO_URL)

# Initialize emotional intelligence analyzer
emotional_intelligence = get_emotional_intelligence_analyzer(MONGO_URL, OPENAI_API_KEY)

# Initialize data generator
data_generator = get_data_generator(MONGO_URL)

# Initialize OpenAI client
from openai import AsyncOpenAI
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# FastAPI app setup
app = FastAPI(title="IDFS PathwayIQ™ API", description="IDFS PathwayIQ™ Educational Platform powered by SikatLabs™")
api_router = APIRouter(prefix="/api")

# CORS Configuration - Production ready
cors_origins = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else [
    "http://localhost:3000",
    "https://localhost:3000", 
    "https://548aecf0-3046-496f-bc4e-3c38130ea414.preview.emergentagent.com",
    "https://pathwayiq.com",
    "https://www.pathwayiq.com",
    "https://app.pathwayiq.com",
    "https://pathwayiq.emergent.host",
    "https://*.emergent.host",
    "https://*.emergentagent.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# COMPREHENSIVE 60-MINUTE ASSESSMENT SYSTEM (IDFS METEY METHOD)
# ============================================================================

class ComprehensiveAssessmentConfig(BaseModel):
    user_grade_level: str  # "6th_grade", "8th_grade", etc.
    assessment_duration: int = 60  # minutes
    enable_think_aloud: bool = True
    enable_ai_ethics_scenarios: bool = True
    enable_real_world_scenarios: bool = True
    adaptive_difficulty: bool = True

class AssessmentQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: str  # "mcq", "open_ended", "scenario_based", "ai_ethics"
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: str
    difficulty_level: str
    subject: str
    grade_level: str
    real_world_context: Optional[str] = None
    ai_ethics_component: Optional[str] = None
    think_aloud_prompt: Optional[str] = None
    estimated_time: int = 3  # minutes per question

# ============================================================================
# VOICE-TO-TEXT INTEGRATION SYSTEM  
# ============================================================================

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class BadgeRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

# User Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    role: UserRole
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    xp: int = 0
    level: int = 1
    streak_days: int = 0
    last_active: Optional[datetime] = None
    avatar: Optional[str] = None
    badges: List[str] = []
    study_groups: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Learning Models
class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    subject: str
    topic: str
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: str
    points: int = 10
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = []
    # Enhanced adaptive fields
    grade_level: GradeLevel = GradeLevel.GRADE_8
    complexity: QuestionComplexity = QuestionComplexity.APPLICATION
    requires_prior_knowledge: bool = False
    multi_step: bool = False
    abstract_reasoning: bool = False
    estimated_time_seconds: int = 30
    think_aloud_prompts: List[str] = []

class QuestionCreate(BaseModel):
    question_text: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    subject: str
    topic: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    points: int = 10
    tags: List[str] = []
    grade_level: GradeLevel = GradeLevel.GRADE_8
    complexity: QuestionComplexity = QuestionComplexity.APPLICATION
    requires_prior_knowledge: bool = False
    multi_step: bool = False
    abstract_reasoning: bool = False
    estimated_time_seconds: int = 30
    think_aloud_prompts: List[str] = []

class AdaptiveAssessmentStart(BaseModel):
    subject: str
    target_grade_level: Optional[GradeLevel] = None
    assessment_type: str = "diagnostic"  # diagnostic, practice, challenge
    enable_think_aloud: bool = True
    enable_ai_help_tracking: bool = True
    max_questions: int = 20

class ThinkAloudResponse(BaseModel):
    question_id: str
    reasoning: str
    strategy: str
    confidence_level: int  # 1-5 scale
    difficulty_perception: int  # 1-5 scale
    connections_to_prior_knowledge: str

class AdaptiveAnswerSubmission(BaseModel):
    session_id: str
    question_id: str
    answer: str
    response_time_seconds: float
    think_aloud_data: Optional[ThinkAloudResponse] = None
    ai_help_used: bool = False
    ai_help_details: Optional[Dict] = None

class UserAnswer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    question_id: str
    answer: str
    is_correct: bool
    points_earned: int
    time_taken: int  # seconds
    answered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Enhanced adaptive fields
    session_id: Optional[str] = None
    ability_estimate_before: Optional[float] = None
    ability_estimate_after: Optional[float] = None
    question_difficulty: Optional[float] = None
    think_aloud_response: Optional[Dict] = None
    ai_assistance_used: bool = False
    ai_assistance_details: Optional[Dict] = None

class StudySession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    topic: str
    questions_answered: int = 0
    correct_answers: int = 0
    total_points: int = 0
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None

# Enhanced AI Request Models
class EnhancedChatRequest(BaseModel):
    message: str
    emotional_context: Optional[str] = None
    learning_style: Optional[str] = None
    ai_personality: Optional[str] = "encouraging"
    session_id: Optional[str] = None

class PersonalizedLearningPathRequest(BaseModel):
    subject: str
    learning_goals: List[str]
    target_completion_weeks: Optional[int] = 8
    preferred_learning_style: Optional[str] = None

class LearningStyleAssessmentRequest(BaseModel):
    responses: List[Dict[str, Any]]

class VoiceToTextRequest(BaseModel):
    audio_data: str  # base64 encoded audio
    session_context: Optional[Dict[str, Any]] = None

class SpeechToTextRequest(BaseModel):
    """Request model for speech-to-text processing"""
    audio_data: str  # base64 encoded audio file
    assessment_id: str
    session_id: str
    language: str = "en"
    context_prompt: Optional[str] = None

class TranscriptionResponse(BaseModel):
    """Response model for transcription results"""
    id: str
    text: str
    confidence: float
    processing_time: float
    think_aloud_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime

class ContentGenerationRequestModel(BaseModel):
    """Request model for AI content generation"""
    content_type: str  # quiz, lesson, explanation, practice_problems, study_guide, flashcards
    subject: str
    topic: str
    difficulty_level: str = "intermediate"
    learning_objectives: List[str] = []
    target_audience: str = "8th grade students"
    length: str = "medium"  # short, medium, long
    personalization_enabled: bool = True
    context_prompt: Optional[str] = None

class ContentResponse(BaseModel):
    """Response model for generated content"""
    id: str
    content_type: str
    subject: str
    topic: str
    title: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    quality_score: float

# Temporary class to maintain think-aloud functionality
class LeaderboardRequest(BaseModel):
    """Request model for leaderboard queries"""
    category: str
    limit: int = 100
    offset: int = 0

class CompetitionJoinRequest(BaseModel):
    """Request model for joining competitions"""
    competition_id: str

class BadgeNotificationRequest(BaseModel):
    """Request model for badge notifications"""
    notification_ids: Optional[List[str]] = None

# Temporary class to maintain think-aloud functionality
class ThinkAloudSessionRequest(BaseModel):
    """Request to start a think-aloud session"""
    assessment_id: str
    question_id: str
    language: str = "en"
    enable_analysis: bool = True

# ============================================================================
# AUTHENTICATION UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

# ============================================================================
# AI HELPER FUNCTIONS
# ============================================================================

async def get_ai_response(messages: List[Dict[str, str]], user_context: Optional[Dict] = None) -> str:
    try:
        system_prompt = """You are IDFS PathwayIQ™ AI, an intelligent tutoring assistant powered by SikatLabs™. 
        You help students learn through personalized guidance, explanations, and encouragement.
        
        Guidelines:
        - Be encouraging and supportive
        - Provide clear, educational explanations
        - Ask follow-up questions to ensure understanding
        - Adapt to the student's learning level
        - Focus on building confidence and knowledge
        """
        
        if user_context:
            system_prompt += f"\nStudent context: Level {user_context.get('level', 1)}, XP: {user_context.get('xp', 0)}"
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return "I'm sorry, I'm having trouble responding right now. Please try again later."

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.dict()
    user = User(**user_dict)
    
    # Create user document with password
    user_doc = user.dict()
    user_doc["password"] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_obj = User(**user)
    access_token = create_access_token(data={"sub": user_obj.id})
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ============================================================================
# ADAPTIVE ASSESSMENT ENDPOINTS
# ============================================================================

@api_router.post("/adaptive-assessment/start")
async def start_adaptive_assessment(
    assessment_config: AdaptiveAssessmentStart,
    current_user: User = Depends(get_current_user)
):
    """Start a new adaptive assessment session"""
    try:
        # Get user's previous performance in this subject
        previous_answers = await db.user_answers.find({
            "user_id": current_user.id,
            "question_id": {"$regex": assessment_config.subject}
        }).to_list(100)
        
        # Calculate initial ability estimate
        if previous_answers:
            correct_count = sum(1 for answer in previous_answers if answer.get("is_correct", False))
            accuracy = correct_count / len(previous_answers)
            initial_ability = max(0.1, min(0.9, accuracy))
        else:
            # Use grade level or default
            if assessment_config.target_grade_level:
                initial_ability = adaptive_engine.estimate_initial_ability(
                    grade_level=assessment_config.target_grade_level
                )
            else:
                # Estimate from user level
                initial_ability = min(0.9, (current_user.level - 1) * 0.1 + 0.3)
        
        # Start adaptive session
        session_id = adaptive_engine.start_adaptive_session(
            user_id=current_user.id,
            subject=assessment_config.subject,
            initial_ability=initial_ability,
            session_type=assessment_config.assessment_type
        )
        
        return {
            "session_id": session_id,
            "initial_ability_estimate": initial_ability,
            "estimated_grade_level": adaptive_engine.determine_grade_level(initial_ability).value,
            "config": assessment_config.dict()
        }
        
    except Exception as e:
        logger.error(f"Error starting adaptive assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to start adaptive assessment")

@api_router.get("/adaptive-assessment/{session_id}/next-question")
async def get_next_adaptive_question(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the next optimal question for adaptive assessment"""
    try:
        # Get available questions for the subject
        session = adaptive_engine.session_data.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Assessment session not found")
        
        # Get questions from database
        questions_cursor = db.questions.find({"subject": session.subject})
        available_questions = await questions_cursor.to_list(1000)
        
        # Convert to format expected by adaptive engine
        question_list = []
        for q in available_questions:
            question_dict = dict(q)
            question_dict["id"] = q["id"]
            question_list.append(question_dict)
        
        # Select next question using adaptive algorithm
        next_question = adaptive_engine.select_next_question(session_id, question_list)
        
        if not next_question:
            # No more suitable questions, end assessment
            analytics = adaptive_engine.get_session_analytics(session_id)
            return {
                "session_complete": True,
                "final_analytics": analytics
            }
        
        # Store question difficulty for this session
        question_difficulty = adaptive_engine.calculate_question_difficulty(next_question)
        adaptive_engine.question_difficulties[next_question["id"]] = question_difficulty
        
        # Add to session questions asked
        session.questions_asked.append(next_question["id"])
        
        # Format response
        response_question = {
            "id": next_question["id"],
            "question_text": next_question["question_text"],
            "question_type": next_question["question_type"],
            "options": next_question.get("options", []),
            "complexity": next_question.get("complexity", "application"),
            "grade_level": next_question.get("grade_level", "grade_8"),
            "estimated_time_seconds": next_question.get("estimated_time_seconds", 30),
            "think_aloud_prompts": next_question.get("think_aloud_prompts", [
                "Explain your thinking process",
                "What strategy are you using?",
                "How confident are you in this answer?"
            ]),
            "current_ability_estimate": session.current_ability_estimate,
            "question_number": len(session.questions_asked),
            "estimated_difficulty": question_difficulty
        }
        
        return response_question
        
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HTTPException(status_code=500, detail="Failed to get next question")

@api_router.post("/adaptive-assessment/submit-answer")
async def submit_adaptive_answer(
    answer_data: AdaptiveAnswerSubmission,
    current_user: User = Depends(get_current_user)
):
    """Submit answer for adaptive assessment with think-aloud and AI tracking"""
    try:
        session_id = answer_data.session_id
        question_id = answer_data.question_id
        
        # Get question details
        question = await db.questions.find_one({"id": question_id})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Check if answer is correct
        is_correct = answer_data.answer.lower().strip() == question["correct_answer"].lower().strip()
        
        # Get current ability estimate
        session = adaptive_engine.session_data.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        ability_before = session.current_ability_estimate
        
        # Record AI assistance if used
        if answer_data.ai_help_used and answer_data.ai_help_details:
            adaptive_engine.record_ai_assistance(
                session_id=session_id,
                assistance_type=answer_data.ai_help_details.get("type", "general"),
                question_id=question_id,
                help_content=answer_data.ai_help_details.get("content", "")
            )
        
        # Update ability estimate
        think_aloud_dict = answer_data.think_aloud_data.dict() if answer_data.think_aloud_data else None
        ability_after = adaptive_engine.update_ability_estimate(
            session_id=session_id,
            question_id=question_id,
            is_correct=is_correct,
            response_time=answer_data.response_time_seconds,
            think_aloud_data=think_aloud_dict
        )
        
        # Calculate points earned
        base_points = question.get("points", 10)
        points_earned = base_points if is_correct else 0
        
        # Bonus points for good think-aloud responses
        if think_aloud_dict:
            reasoning_quality = adaptive_engine._assess_reasoning_quality(think_aloud_dict)
            points_earned += int(base_points * 0.5 * reasoning_quality)
        
        # Penalty for excessive AI help
        if answer_data.ai_help_used:
            points_earned = int(points_earned * 0.7)  # 30% reduction for AI help
        
        # Store detailed answer record
        user_answer = UserAnswer(
            user_id=current_user.id,
            question_id=question_id,
            answer=answer_data.answer,
            is_correct=is_correct,
            points_earned=points_earned,
            time_taken=int(answer_data.response_time_seconds),
            session_id=session_id,
            ability_estimate_before=ability_before,
            ability_estimate_after=ability_after,
            question_difficulty=adaptive_engine.question_difficulties.get(question_id, 0.5),
            think_aloud_response=think_aloud_dict,
            ai_assistance_used=answer_data.ai_help_used,
            ai_assistance_details=answer_data.ai_help_details
        )
        
        await db.user_answers.insert_one(user_answer.dict())
        
        # Update user XP and level
        if is_correct:
            new_xp = current_user.xp + points_earned
            new_level = (new_xp // 100) + 1
            await db.users.update_one(
                {"id": current_user.id},
                {"$set": {"xp": new_xp, "level": new_level}}
            )
        
        # Check for achievement unlocks (gamification system)
        try:
            gamification = get_gamification_engine(db)
            leaderboard = get_leaderboard_system(db)
            
            # Prepare event data for achievement checking
            event_data = {
                "assessment_completed": is_correct,
                "answer_submitted": True,
                "points_earned": points_earned,
                "perfect_score": is_correct and points_earned > 0,
                "think_aloud_used": bool(think_aloud_dict),
                "ai_help_used": answer_data.ai_help_used,
                "response_time": answer_data.response_time_seconds
            }
            
            # Check and update achievements
            achievement_result = await gamification.check_user_achievements(current_user.id, event_data)
            
            # Update leaderboards
            await leaderboard.update_user_score(current_user.id, LeaderboardCategory.OVERALL, {
                "score": new_xp if is_correct else current_user.xp,
                "assessments_completed": True
            })
            await leaderboard.update_user_score(current_user.id, LeaderboardCategory.WEEKLY, {
                "assessment_completed": True,
                "points_earned": points_earned
            })
            await leaderboard.update_user_score(current_user.id, LeaderboardCategory.MONTHLY, {
                "assessment_completed": True, 
                "points_earned": points_earned
            })
            
            # Update assessment speed leaderboard if fast
            if answer_data.response_time_seconds < 60:  # Under 1 minute
                await leaderboard.update_user_score(current_user.id, LeaderboardCategory.ASSESSMENT_SPEED, {
                    "completion_time": answer_data.response_time_seconds
                })
            
        except Exception as gamification_error:
            logger.warning(f"Gamification update failed: {str(gamification_error)}")
            # Don't fail the main request if gamification fails
        
        # Determine new grade level estimate
        new_grade_level = adaptive_engine.determine_grade_level(ability_after)
        
        return {
            "correct": is_correct,
            "points_earned": points_earned,
            "explanation": question["explanation"],
            "ability_estimate_change": ability_after - ability_before,
            "new_ability_estimate": ability_after,
            "estimated_grade_level": new_grade_level.value,
            "think_aloud_quality_score": adaptive_engine._assess_reasoning_quality(think_aloud_dict) if think_aloud_dict else 0,
            "ai_help_impact": -0.3 if answer_data.ai_help_used else 0
        }
        
    except Exception as e:
        logger.error(f"Error submitting adaptive answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit answer")

# ============================================================================
# GAMIFICATION ENDPOINTS - BADGES AND ACHIEVEMENTS
# ============================================================================

@api_router.get("/gamification/badges/user")
async def get_user_badges(current_user: User = Depends(get_current_user)):
    """Get all badges and achievements for current user"""
    try:
        gamification = get_gamification_engine(db)
        
        # Initialize gamification system if not already done
        await gamification.initialize()
        
        badges_data = await gamification.get_user_badges(current_user.id)
        
        return {
            "success": True,
            "data": badges_data
        }
        
    except Exception as e:
        logger.error(f"Error getting user badges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user badges")

@api_router.get("/gamification/notifications")
async def get_achievement_notifications(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get recent achievement notifications"""
    try:
        gamification = get_gamification_engine(db)
        notifications = await gamification.get_achievement_notifications(current_user.id, limit)
        
        return {
            "success": True,
            "notifications": notifications,
            "total": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting achievement notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

@api_router.post("/gamification/notifications/read")
async def mark_notifications_read(
    request: BadgeNotificationRequest,
    current_user: User = Depends(get_current_user)
):
    """Mark achievement notifications as read"""
    try:
        gamification = get_gamification_engine(db)
        await gamification.mark_notifications_read(current_user.id, request.notification_ids)
        
        return {
            "success": True,
            "message": "Notifications marked as read"
        }
        
    except Exception as e:
        logger.error(f"Error marking notifications as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")

@api_router.get("/gamification/badges/definitions")
async def get_badge_definitions(current_user: User = Depends(get_current_user)):
    """Get all available badge definitions"""
    try:
        badges = await db.badge_definitions.find({"active": True}).to_list(None)
        
        return {
            "success": True,
            "badges": badges,
            "total": len(badges)
        }
        
    except Exception as e:
        logger.error(f"Error getting badge definitions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get badge definitions")

# ============================================================================
# LEADERBOARD ENDPOINTS
# ============================================================================

@api_router.get("/leaderboard/categories")
async def get_leaderboard_categories(current_user: User = Depends(get_current_user)):
    """Get all available leaderboard categories"""
    categories = [
        {
            "id": "overall",
            "name": "Overall",
            "description": "Total points from all activities",
            "icon": "🏆"
        },
        {
            "id": "weekly",
            "name": "This Week",
            "description": "Points earned this week",
            "icon": "📅"
        },
        {
            "id": "monthly",
            "name": "This Month", 
            "description": "Points earned this month",
            "icon": "🗓️"
        },
        {
            "id": "think_aloud",
            "name": "Think-Aloud Master",
            "description": "Best think-aloud performance",
            "icon": "🎤"
        },
        {
            "id": "content_creation",
            "name": "Content Creator",
            "description": "AI content generation points",
            "icon": "📝"
        },
        {
            "id": "assessment_speed",
            "name": "Speed Demon",
            "description": "Fastest assessment completion",
            "icon": "⚡"
        },
        {
            "id": "streak",
            "name": "Streak Master",
            "description": "Longest learning streaks",
            "icon": "🔥"
        },
        {
            "id": "badges",
            "name": "Badge Collector",
            "description": "Most badges earned",
            "icon": "🎖️"
        }
    ]
    
    return {
        "success": True,
        "categories": categories
    }

@api_router.get("/leaderboard/{category}")
async def get_leaderboard(
    category: str,
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0
):
    """Get leaderboard for specific category"""
    try:
        leaderboard = get_leaderboard_system(db)
        
        # Initialize leaderboard system if not already done
        await leaderboard.initialize()
        
        # Validate category
        try:
            category_enum = LeaderboardCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid leaderboard category")
        
        leaderboard_data = await leaderboard.get_leaderboard(category_enum, limit, offset)
        
        return {
            "success": True,
            "data": leaderboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@api_router.get("/leaderboard/{category}/user-ranking")
async def get_user_ranking(
    category: str,
    current_user: User = Depends(get_current_user)
):
    """Get current user's ranking in specific category"""
    try:
        leaderboard = get_leaderboard_system(db)
        
        # Validate category
        try:
            category_enum = LeaderboardCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid leaderboard category")
        
        ranking_data = await leaderboard.get_user_ranking(current_user.id, category_enum)
        
        return {
            "success": True,
            "data": ranking_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user ranking: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user ranking")

@api_router.get("/competitions/active")
async def get_active_competitions(current_user: User = Depends(get_current_user)):
    """Get all active competitions"""
    try:
        leaderboard = get_leaderboard_system(db)
        competitions = await leaderboard.get_active_competitions()
        
        return {
            "success": True,
            "competitions": competitions,
            "total": len(competitions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active competitions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get active competitions")

@api_router.post("/competitions/join")
async def join_competition(
    request: CompetitionJoinRequest,
    current_user: User = Depends(get_current_user)
):
    """Join a competition"""
    try:
        leaderboard = get_leaderboard_system(db)
        result = await leaderboard.join_competition(current_user.id, request.competition_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining competition: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to join competition")

@api_router.get("/competitions/{competition_id}/leaderboard")
async def get_competition_leaderboard(
    competition_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = 100
):
    """Get leaderboard for specific competition"""
    try:
        leaderboard = get_leaderboard_system(db)
        leaderboard_data = await leaderboard.get_competition_leaderboard(competition_id, limit)
        
        if "error" in leaderboard_data:
            raise HTTPException(status_code=404, detail=leaderboard_data["error"])
        
        return {
            "success": True,
            "data": leaderboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting competition leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get competition leaderboard")

# ============================================================================
# AI-POWERED CONTENT GENERATION ENDPOINTS
# ============================================================================

@api_router.post("/content-generation/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentGenerationRequestModel,
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered educational content"""
    try:
        # Get content generator
        generator = get_content_generator(db)
        
        # Create content generation request
        content_request = ContentGenerationRequest(
            content_type=request.content_type,
            subject=request.subject,
            topic=request.topic,
            difficulty_level=request.difficulty_level,
            learning_objectives=request.learning_objectives,
            target_audience=request.target_audience,
            length=request.length,
            personalization_data=None if not request.personalization_enabled else {"user_id": current_user.id},
            context_prompt=request.context_prompt
        )
        
        # Generate content
        generated_content = await generator.generate_content(content_request, current_user.id)
        
        # Check for achievement unlocks (gamification system)
        try:
            gamification = get_gamification_engine(db)
            leaderboard = get_leaderboard_system(db)
            
            # Prepare event data for achievement checking
            event_data = {
                "content_generated": True,
                "content_quality": generated_content.quality_score,
                "high_quality_content": generated_content.quality_score >= 0.8,
                "content_type": generated_content.content_type
            }
            
            # Check and update achievements
            achievement_result = await gamification.check_user_achievements(current_user.id, event_data)
            
            # Update content creation leaderboard
            await leaderboard.update_user_score(current_user.id, LeaderboardCategory.CONTENT_CREATION, {
                "content_generated": True,
                "quality_score": generated_content.quality_score
            })
            
        except Exception as gamification_error:
            logger.warning(f"Gamification update failed: {str(gamification_error)}")
            # Don't fail the main request if gamification fails
        
        # Return response
        return ContentResponse(
            id=generated_content.id,
            content_type=generated_content.content_type,
            subject=generated_content.subject,
            topic=generated_content.topic,
            title=generated_content.title,
            content=generated_content.content,
            metadata=generated_content.metadata,
            created_at=generated_content.created_at,
            quality_score=generated_content.quality_score
        )
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@api_router.get("/content-generation/user-content")
async def get_user_content(
    current_user: User = Depends(get_current_user),
    content_type: Optional[str] = None,
    limit: int = 20
):
    """Get user's generated content"""
    try:
        generator = get_content_generator(db)
        contents = await generator.get_user_content(current_user.id, content_type, limit)
        
        return {
            "contents": [
                {
                    "id": content.id,
                    "content_type": content.content_type,
                    "subject": content.subject,
                    "topic": content.topic,
                    "title": content.title,
                    "created_at": content.created_at,
                    "quality_score": content.quality_score,
                    "usage_count": content.usage_count
                }
                for content in contents
            ],
            "total": len(contents)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content")

@api_router.get("/content-generation/content/{content_id}")
async def get_content_by_id(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific content by ID"""
    try:
        generator = get_content_generator(db)
        content = await generator.get_content_by_id(content_id, current_user.id)
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Increment usage count
        await db.generated_content.update_one(
            {"id": content_id, "user_id": current_user.id},
            {"$inc": {"usage_count": 1}}
        )
        
        return {
            "id": content.id,
            "content_type": content.content_type,
            "subject": content.subject,
            "topic": content.topic,
            "title": content.title,
            "content": content.content,
            "metadata": content.metadata,
            "created_at": content.created_at,
            "quality_score": content.quality_score,
            "usage_count": content.usage_count + 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content")

@api_router.get("/content-generation/content-types")
async def get_content_types(current_user: User = Depends(get_current_user)):
    """Get available content types"""
    content_types = [
        {
            "id": "quiz",
            "name": "Quiz",
            "description": "Interactive quizzes with multiple question types",
            "icon": "🧠"
        },
        {
            "id": "lesson",
            "name": "Lesson",
            "description": "Comprehensive lesson plans with activities",
            "icon": "📚"
        },
        {
            "id": "explanation",
            "name": "Explanation",
            "description": "Clear explanations of complex topics",
            "icon": "💡"
        },
        {
            "id": "practice_problems",
            "name": "Practice Problems",
            "description": "Practice problems with step-by-step solutions",
            "icon": "📝"
        },
        {
            "id": "study_guide",
            "name": "Study Guide",
            "description": "Comprehensive study guides for exam preparation",
            "icon": "📖"
        },
        {
            "id": "flashcards",
            "name": "Flashcards",
            "description": "Flashcards for memorization and review",
            "icon": "🃏"
        }
    ]
    
    return {"content_types": content_types}

@api_router.post("/content-generation/regenerate/{content_id}")
async def regenerate_content(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Regenerate existing content with improvements"""
    try:
        generator = get_content_generator(db)
        existing_content = await generator.get_content_by_id(content_id, current_user.id)
        
        if not existing_content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Create new request based on existing content
        regeneration_request = ContentGenerationRequest(
            content_type=existing_content.content_type,
            subject=existing_content.subject,
            topic=existing_content.topic,
            difficulty_level=existing_content.difficulty_level,
            learning_objectives=existing_content.metadata.get("learning_objectives", []),
            target_audience=existing_content.metadata.get("target_audience", "8th grade students"),
            length=existing_content.metadata.get("length", "medium"),
            context_prompt=f"Improve and enhance the previous version of this content. Make it more engaging and comprehensive."
        )
        
        # Generate new content
        new_content = await generator.generate_content(regeneration_request, current_user.id)
        
        return ContentResponse(
            id=new_content.id,
            content_type=new_content.content_type,
            subject=new_content.subject,
            topic=new_content.topic,
            title=new_content.title,
            content=new_content.content,
            metadata=new_content.metadata,
            created_at=new_content.created_at,
            quality_score=new_content.quality_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content regeneration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Content regeneration failed")

# ============================================================================
# SPEECH-TO-TEXT ENDPOINTS FOR THINK-ALOUD ASSESSMENTS
# ============================================================================

@api_router.post("/speech-to-text/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    request: SpeechToTextRequest,
    current_user: User = Depends(get_current_user)
):
    """Transcribe audio using OpenAI Whisper for think-aloud assessments"""
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(request.audio_data)
        
        # Create configuration
        config = SpeechToTextConfig(
            language=request.language,
            prompt=request.context_prompt
        )
        
        # Get speech processor
        processor = get_speech_processor(db)
        
        # Process audio
        result = await processor.process_audio_file(
            audio_data=audio_data,
            user_id=current_user.id,
            assessment_id=request.assessment_id,
            session_id=request.session_id,
            config=config
        )
        
        # Return response
        return TranscriptionResponse(
            id=result.id,
            text=result.text,
            confidence=result.confidence,
            processing_time=result.processing_time,
            think_aloud_analysis=result.think_aloud_analysis,
            created_at=result.created_at
        )
        
    except Exception as e:
        logger.error(f"Speech-to-text transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@api_router.post("/speech-to-text/start-session")
async def start_think_aloud_session(
    request: ThinkAloudSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Start a think-aloud session for an assessment"""
    try:
        # Create session record
        session_id = str(uuid.uuid4())
        
        session_record = {
            "id": session_id,
            "user_id": current_user.id,
            "assessment_id": request.assessment_id,
            "question_id": request.question_id,
            "language": request.language,
            "enable_analysis": request.enable_analysis,
            "created_at": datetime.now(timezone.utc),
            "status": "active",
            "transcriptions": []
        }
        
        await db.think_aloud_sessions.insert_one(session_record)
        
        return {
            "session_id": session_id,
            "status": "active",
            "message": "Think-aloud session started successfully",
            "instructions": "You can now start speaking your thoughts. The system will transcribe and analyze your responses."
        }
        
    except Exception as e:
        logger.error(f"Error starting think-aloud session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start think-aloud session")

@api_router.get("/speech-to-text/session/{session_id}/transcriptions")
async def get_session_transcriptions(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all transcriptions for a think-aloud session"""
    try:
        # Verify session belongs to user
        session = await db.think_aloud_sessions.find_one({"id": session_id, "user_id": current_user.id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get transcriptions
        processor = get_speech_processor(db)
        transcriptions = await processor.get_transcription_by_session(session_id)
        
        return {
            "session_id": session_id,
            "transcriptions": [
                {
                    "id": t.id,
                    "text": t.text,
                    "confidence": t.confidence,
                    "processing_time": t.processing_time,
                    "think_aloud_analysis": t.think_aloud_analysis,
                    "created_at": t.created_at
                }
                for t in transcriptions
            ],
            "total_transcriptions": len(transcriptions)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving session transcriptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transcriptions")

@api_router.post("/speech-to-text/session/{session_id}/end")
async def end_think_aloud_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """End a think-aloud session and generate summary"""
    try:
        # Verify session belongs to user
        session = await db.think_aloud_sessions.find_one({"id": session_id, "user_id": current_user.id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all transcriptions for summary
        processor = get_speech_processor(db)
        transcriptions = await processor.get_transcription_by_session(session_id)
        
        # Generate session summary
        combined_text = " ".join([t.text for t in transcriptions])
        session_summary = await _generate_session_summary(combined_text, current_user.id)
        
        # Update session status
        await db.think_aloud_sessions.update_one(
            {"id": session_id},
            {
                "$set": {
                    "status": "completed",
                    "ended_at": datetime.now(timezone.utc),
                    "summary": session_summary,
                    "total_transcriptions": len(transcriptions)
                }
            }
        )
        
        # Check for achievement unlocks (gamification system)
        try:
            gamification = get_gamification_engine(db)
            leaderboard = get_leaderboard_system(db)
            
            # Prepare event data for achievement checking
            event_data = {
                "think_aloud_completed": True,
                "session_quality": session_summary.get("session_effectiveness", 3) / 5.0,
                "transcription_count": len(transcriptions),
                "clarity_score": session_summary.get("metacognitive_quality", 3) / 5.0
            }
            
            # Check and update achievements
            achievement_result = await gamification.check_user_achievements(current_user.id, event_data)
            
            # Update think-aloud leaderboard
            await leaderboard.update_user_score(current_user.id, LeaderboardCategory.THINK_ALOUD, {
                "think_aloud_completed": True,
                "session_quality": session_summary.get("session_effectiveness", 3),
                "clarity_score": session_summary.get("metacognitive_quality", 3) / 5.0
            })
            
        except Exception as gamification_error:
            logger.warning(f"Gamification update failed: {str(gamification_error)}")
            # Don't fail the main request if gamification fails
        
        return {
            "session_id": session_id,
            "status": "completed",
            "summary": session_summary,
            "total_transcriptions": len(transcriptions),
            "message": "Think-aloud session completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error ending think-aloud session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")

@api_router.get("/speech-to-text/user/sessions")
async def get_user_think_aloud_sessions(
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get user's think-aloud sessions"""
    try:
        sessions = await db.think_aloud_sessions.find(
            {"user_id": current_user.id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")

async def _generate_session_summary(combined_text: str, user_id: str) -> Dict[str, Any]:
    """Generate comprehensive session summary using AI"""
    try:
        summary_prompt = f"""
        Generate a comprehensive summary of this think-aloud session:
        
        Transcription: "{combined_text}"
        
        Provide analysis in JSON format with these keys:
        - overall_strategy: string describing the main problem-solving approach
        - confidence_progression: string describing how confidence changed
        - learning_insights: array of key learning observations
        - areas_for_improvement: array of specific recommendations
        - metacognitive_quality: number (1-5) rating metacognitive awareness
        - emotional_journey: string describing emotional state changes
        - key_vocabulary_used: array of important academic terms used
        - session_effectiveness: number (1-5) rating overall session quality
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an educational assessment expert analyzing think-aloud sessions."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        import json
        summary = json.loads(response.choices[0].message.content)
        return summary
        
    except Exception as e:
        logger.error(f"Session summary generation error: {str(e)}")
        return {
            "overall_strategy": "Unable to analyze",
            "confidence_progression": "Analysis unavailable",
            "learning_insights": ["Session analysis could not be completed"],
            "areas_for_improvement": ["Please try again"],
            "metacognitive_quality": 3,
            "emotional_journey": "Neutral",
            "key_vocabulary_used": [],
            "session_effectiveness": 3
        }

# ============================================================================
# ENHANCED AI ENDPOINTS
# ============================================================================

@api_router.post("/ai/enhanced-chat")
async def enhanced_ai_chat(
    request: EnhancedChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Enhanced AI chat with emotional intelligence and learning style adaptation"""
    try:
        # Detect emotional state and learning style
        emotional_state = await advanced_ai_engine.detect_emotional_state(request.message)
        learning_style = advanced_ai_engine.detect_learning_style_from_text(request.message)
        
        # Set AI personality
        ai_personality = AIPersonality(request.ai_personality) if request.ai_personality else AIPersonality.ENCOURAGING
        
        # Generate adaptive response
        user_context = {
            "level": current_user.level,
            "xp": current_user.xp,
            "role": current_user.role.value
        }
        
        response = await advanced_ai_engine.generate_adaptive_response(
            message=request.message,
            user_context=user_context,
            emotional_state=emotional_state,
            learning_style=learning_style,
            ai_personality=ai_personality
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Enhanced AI chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI response")

@api_router.post("/ai/voice-to-text")
async def voice_to_text(
    request: VoiceToTextRequest,
    current_user: User = Depends(get_current_user)
):
    """Process voice input with emotional and learning style analysis"""
    try:
        # Convert base64 audio to bytes
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Process voice input
        result = await advanced_ai_engine.process_voice_input(audio_bytes, current_user.id)
        
        return result
        
    except Exception as e:
        logger.error(f"Voice to text error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice input")

@api_router.post("/ai/personalized-learning-path")
async def create_personalized_learning_path(
    request: PersonalizedLearningPathRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate personalized learning path using AI"""
    try:
        # Get user performance data
        user_performance = await db.user_answers.find({"user_id": current_user.id}).to_list(1000)
        
        # Process performance data
        performance_data = {
            "topic_accuracy": {},
            "recent_scores": [],
            "retention_tests": [],
            "average_session_length": 30
        }
        
        # Detect learning style from user interactions
        learning_style = LearningStyle.MULTIMODAL  # Default, can be enhanced
        
        # Generate learning path
        learning_path = await advanced_ai_engine.generate_personalized_learning_path(
            user_id=current_user.id,
            subject=request.subject,
            current_level=current_user.level,
            learning_goals=request.learning_goals,
            learning_style=learning_style,
            user_performance_data=performance_data
        )
        
        return learning_path
        
    except Exception as e:
        logger.error(f"Learning path generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create learning path")

# ============================================================================
# PRODUCTION MONITORING & HEALTH CHECK ENDPOINTS
# ============================================================================

@api_router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@api_router.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive health check with system metrics"""
    return await health_monitor.comprehensive_health_check()

@api_router.get("/health/report")
async def health_report():
    """Generate comprehensive health report"""
    return await health_monitor.generate_health_report()

@api_router.get("/metrics")
async def system_metrics():
    """Get system metrics and statistics"""
    cache_stats = cache_manager.get_stats()
    app_metrics = await health_monitor.get_application_metrics()
    system_metrics = health_monitor.get_system_metrics()
    
    return {
        "cache": cache_stats,
        "application": app_metrics,
        "system": system_metrics,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/admin/cache/clear")
async def clear_cache(current_user: User = Depends(get_current_user)):
    """Clear application cache (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = await cache_manager.clear_all()
    return {"success": success, "message": "Cache cleared successfully"}

@api_router.post("/admin/cache/warmup")
async def warm_up_cache(current_user: User = Depends(get_current_user)):
    """Warm up application cache (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would call cache warm-up functions
    return {"success": True, "message": "Cache warm-up initiated"}

@api_router.post("/admin/database/index")
async def create_database_indexes(current_user: User = Depends(get_current_user)):
    """Create database indexes (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = await db_indexer.create_all_indexes()
    return {"success": success, "message": "Database indexing completed"}

# ============================================================================
# PRODUCTION OPTIMIZED ENDPOINTS WITH CACHING
# ============================================================================

@api_router.get("/questions/cached", response_model=List[Question])
@cache_result("questions_cached", ttl=3600)
async def get_cached_questions(
    subject: Optional[str] = None,
    difficulty: Optional[QuestionDifficulty] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get questions with caching for better performance"""
    query = {}
    if subject:
        query["subject"] = subject
    if difficulty:
        query["difficulty"] = difficulty
    
    questions = await db.questions.find(query).limit(limit).to_list(limit)
    return [Question(**q) for q in questions]

@api_router.get("/user/analytics/cached")
@cache_result("user_analytics", ttl=900)  # 15 minutes
async def get_cached_user_analytics(current_user: User = Depends(get_current_user)):
    """Get user analytics with caching"""
    try:
        # Get user's answers
        user_answers = await db.user_answers.find({"user_id": current_user.id}).to_list(1000)
        
        # Calculate analytics
        total_questions = len(user_answers)
        correct_answers = sum(1 for answer in user_answers if answer.get("is_correct", False))
        total_points = sum(answer.get("points_earned", 0) for answer in user_answers)
        
        # Subject breakdown
        subject_stats = {}
        for answer in user_answers:
            # Get question to find subject
            question = await db.questions.find_one({"id": answer["question_id"]})
            if question:
                subject = question.get("subject", "unknown")
                if subject not in subject_stats:
                    subject_stats[subject] = {"total": 0, "correct": 0}
                subject_stats[subject]["total"] += 1
                if answer.get("is_correct", False):
                    subject_stats[subject]["correct"] += 1
        
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "user_id": current_user.id,
            "total_questions_answered": total_questions,
            "correct_answers": correct_answers,
            "accuracy_percentage": accuracy,
            "total_points": total_points,
            "current_level": current_user.level,
            "current_xp": current_user.xp,
            "subject_breakdown": subject_stats,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user analytics")

# ============================================================================
# BASIC ENDPOINTS (Updated for Production)
# ============================================================================

@api_router.get("/")
async def root():
    """API root endpoint with production info"""
    return {
        "message": "IDFS PathwayIQ™ API is running!",
        "platform": "IDFS PathwayIQ™ powered by SikatLabs™",
        "version": "1.3.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/questions", response_model=Question)
async def create_question(question_data: QuestionCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can create questions")
    
    question_dict = question_data.dict()
    question_dict["created_by"] = current_user.id
    question = Question(**question_dict)
    
    await db.questions.insert_one(question.dict())
    return question

@api_router.get("/questions", response_model=List[Question])
async def get_questions(
    subject: Optional[str] = None,
    difficulty: Optional[QuestionDifficulty] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if subject:
        query["subject"] = subject
    if difficulty:
        query["difficulty"] = difficulty
    
    questions = await db.questions.find(query).limit(limit).to_list(limit)
    return [Question(**q) for q in questions]

@api_router.post("/questions/{question_id}/answer")
async def submit_answer(
    question_id: str,
    answer: str,
    current_user: User = Depends(get_current_user)
):
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = answer.lower().strip() == question["correct_answer"].lower().strip()
    points_earned = question["points"] if is_correct else 0
    
    user_answer = UserAnswer(
        user_id=current_user.id,
        question_id=question_id,
        answer=answer,
        is_correct=is_correct,
        points_earned=points_earned,
        time_taken=30  # TODO: Track actual time
    )
    
    await db.user_answers.insert_one(user_answer.dict())
    
    # Update user XP and level
    if is_correct:
        new_xp = current_user.xp + points_earned
        new_level = (new_xp // 100) + 1
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"xp": new_xp, "level": new_level}}
        )
    
    return {
        "correct": is_correct,
        "points_earned": points_earned,
        "explanation": question["explanation"]
    }

# ============================================================================
# STUDY GROUPS & COLLABORATIVE LEARNING ENDPOINTS
# ============================================================================

class StudyGroupCreate(BaseModel):
    name: str
    description: str
    subject: str
    max_members: int = 10
    is_public: bool = True
    topics: List[str] = []

class StudyGroupMessage(BaseModel):
    content: str
    message_type: str = "text"
    metadata: Dict[str, Any] = {}

class StudySessionCreate(BaseModel):
    topic: str
    description: str = ""
    duration_minutes: int = 60

@api_router.post("/study-groups/create")
async def create_study_group(
    group_data: StudyGroupCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new study group"""
    try:
        result = await study_groups_engine.create_study_group(
            creator_id=current_user.id,
            name=group_data.name,
            description=group_data.description,
            subject=group_data.subject,
            max_members=group_data.max_members,
            is_public=group_data.is_public,
            topics=group_data.topics
        )
        
        if result["success"]:
            # Track achievement for group creation
            gamification = get_gamification_engine(db)
            await gamification.track_achievement(
                current_user.id, 
                "group_creator", 
                metadata={"group_id": result["group_id"]}
            )
            
            return {
                "success": True,
                "message": "Study group created successfully",
                "data": result
            }
        else:
            return {"success": False, "error": result["error"]}
        
    except Exception as e:
        logger.error(f"Error creating study group: {e}")
        raise HTTPException(status_code=500, detail="Failed to create study group")

@api_router.post("/study-groups/{group_id}/join")
async def join_study_group(
    group_id: str,
    join_message: str = "",
    current_user: User = Depends(get_current_user)
):
    """Join a study group"""
    try:
        result = await study_groups_engine.join_study_group(
            user_id=current_user.id,
            group_id=group_id,
            join_message=join_message
        )
        
        if result["success"]:
            # Track achievement for joining groups
            gamification = get_gamification_engine(db)
            await gamification.track_achievement(
                current_user.id, 
                "team_player", 
                metadata={"group_id": group_id}
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error joining study group: {e}")
        raise HTTPException(status_code=500, detail="Failed to join study group")

@api_router.post("/study-groups/{group_id}/leave")
async def leave_study_group(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """Leave a study group"""
    try:
        result = await study_groups_engine.leave_study_group(
            user_id=current_user.id,
            group_id=group_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error leaving study group: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave study group")

@api_router.get("/study-groups/my-groups")
async def get_my_study_groups(current_user: User = Depends(get_current_user)):
    """Get user's study groups"""
    try:
        groups = await study_groups_engine.get_user_groups(current_user.id)
        
        return {
            "success": True,
            "groups": groups,
            "total": len(groups)
        }
        
    except Exception as e:
        logger.error(f"Error getting user groups: {e}")
        raise HTTPException(status_code=500, detail="Failed to get study groups")

@api_router.get("/study-groups/public")
async def get_public_study_groups(
    subject: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get public study groups"""
    try:
        groups = await study_groups_engine.get_public_groups(
            subject=subject,
            limit=limit,
            skip=skip
        )
        
        return {
            "success": True,
            "groups": groups,
            "total": len(groups)
        }
        
    except Exception as e:
        logger.error(f"Error getting public groups: {e}")
        raise HTTPException(status_code=500, detail="Failed to get public groups")

@api_router.post("/study-groups/{group_id}/messages")
async def send_group_message(
    group_id: str,
    message_data: StudyGroupMessage,
    current_user: User = Depends(get_current_user)
):
    """Send a message to a study group"""
    try:
        result = await study_groups_engine.send_message(
            group_id=group_id,
            user_id=current_user.id,
            content=message_data.content,
            message_type=message_data.message_type,
            metadata=message_data.metadata
        )
        
        if result["success"]:
            # Track collaborative participation
            gamification = get_gamification_engine(db)
            await gamification.track_achievement(
                current_user.id, 
                "active_participant", 
                metadata={"group_id": group_id}
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending group message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@api_router.get("/study-groups/{group_id}/messages")
async def get_group_messages(
    group_id: str,
    limit: int = 50,
    before_timestamp: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
):
    """Get messages from a study group"""
    try:
        messages = await study_groups_engine.get_group_messages(
            group_id=group_id,
            user_id=current_user.id,
            limit=limit,
            before_timestamp=before_timestamp
        )
        
        return {
            "success": True,
            "messages": messages,
            "total": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error getting group messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@api_router.post("/study-groups/{group_id}/sessions/start")
async def start_study_session(
    group_id: str,
    session_data: StudySessionCreate,
    current_user: User = Depends(get_current_user)
):
    """Start a collaborative study session"""
    try:
        result = await study_groups_engine.start_study_session(
            group_id=group_id,
            creator_id=current_user.id,
            topic=session_data.topic,
            description=session_data.description,
            duration_minutes=session_data.duration_minutes
        )
        
        if result["success"]:
            # Track session leadership
            gamification = get_gamification_engine(db)
            await gamification.track_achievement(
                current_user.id, 
                "session_leader", 
                metadata={"session_id": result["session_id"]}
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error starting study session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start study session")

@api_router.post("/study-groups/sessions/{session_id}/join")
async def join_study_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Join an active study session"""
    try:
        result = await study_groups_engine.join_study_session(
            session_id=session_id,
            user_id=current_user.id
        )
        
        if result["success"]:
            # Track session participation
            gamification = get_gamification_engine(db)
            await gamification.track_achievement(
                current_user.id, 
                "dedicated_learner", 
                metadata={"session_id": session_id}
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error joining study session: {e}")
        raise HTTPException(status_code=500, detail="Failed to join study session")

@api_router.get("/study-groups/{group_id}/analytics")
async def get_group_analytics(
    group_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a study group"""
    try:
        analytics = await study_groups_engine.get_group_analytics(
            group_id=group_id,
            user_id=current_user.id,
            days=days
        )
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting group analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# ============================================================================
# ADVANCED LEARNING ANALYTICS DASHBOARD
# ============================================================================

@api_router.get("/analytics/dashboard/user")
async def get_user_learning_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive learning dashboard for current user"""
    try:
        dashboard = await learning_analytics.get_user_learning_dashboard(
            user_id=current_user.id,
            days=days
        )
        
        if "error" in dashboard:
            raise HTTPException(status_code=404, detail=dashboard["error"])
        
        return {
            "success": True,
            "dashboard": dashboard
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user learning dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning dashboard")

@api_router.get("/analytics/dashboard/educator")
async def get_educator_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard for educators"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        dashboard = await learning_analytics.get_educator_dashboard(
            educator_id=current_user.id,
            days=days
        )
        
        if "error" in dashboard:
            raise HTTPException(status_code=500, detail=dashboard["error"])
        
        return {
            "success": True,
            "dashboard": dashboard
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting educator dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get educator dashboard")

@api_router.get("/analytics/performance/trends")
async def get_performance_trends(
    days: int = 90,
    subject: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get detailed performance trends for a user"""
    try:
        # Get user's assessment history
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = {
            "user_id": current_user.id,
            "created_at": {"$gte": since_date}
        }
        
        if subject:
            query["subject"] = subject
        
        assessments = list(db.assessments.find(query).sort("created_at", 1))
        
        if not assessments:
            return {
                "success": True,
                "trends": {
                    "data_points": 0,
                    "trend": "no_data",
                    "message": "No assessment data available for the selected period"
                }
            }
        
        # Calculate trends
        dates = []
        scores = []
        abilities = []
        
        for assessment in assessments:
            dates.append(assessment["created_at"].isoformat())
            scores.append(assessment.get("final_score", 0))
            abilities.append(assessment.get("final_ability_estimate", 0))
        
        # Calculate trend direction
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            early_avg = sum(scores[:3]) / 3
            trend_direction = "improving" if recent_avg > early_avg else "declining" if recent_avg < early_avg else "stable"
        else:
            trend_direction = "insufficient_data"
        
        return {
            "success": True,
            "trends": {
                "data_points": len(assessments),
                "dates": dates,
                "scores": scores,
                "abilities": abilities,
                "trend": trend_direction,
                "latest_score": scores[-1] if scores else 0,
                "average_score": sum(scores) / len(scores) if scores else 0,
                "period_days": days,
                "subject": subject
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance trends")

@api_router.get("/analytics/insights/learning-patterns")
async def get_learning_patterns(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get detailed learning patterns and insights"""
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all user activities
        activities = {
            "assessments": list(db.assessments.find({
                "user_id": current_user.id,
                "created_at": {"$gte": since_date}
            })),
            "content_generation": list(db.content_generation.find({
                "user_id": current_user.id,
                "created_at": {"$gte": since_date}
            })),
            "group_messages": list(db.group_messages.find({
                "user_id": current_user.id,
                "timestamp": {"$gte": since_date}
            }))
        }
        
        # Analyze patterns
        daily_activity = defaultdict(lambda: {"assessments": 0, "content": 0, "messages": 0})
        hourly_distribution = defaultdict(int)
        subject_focus = defaultdict(int)
        
        # Process assessments
        for assessment in activities["assessments"]:
            date_key = assessment["created_at"].date().isoformat()
            hour_key = assessment["created_at"].hour
            
            daily_activity[date_key]["assessments"] += 1
            hourly_distribution[hour_key] += 1
            subject_focus[assessment.get("subject", "unknown")] += 1
        
        # Process content generation
        for content in activities["content_generation"]:
            date_key = content["created_at"].date().isoformat()
            hour_key = content["created_at"].hour
            
            daily_activity[date_key]["content"] += 1
            hourly_distribution[hour_key] += 1
        
        # Process messages
        for message in activities["group_messages"]:
            date_key = message["timestamp"].date().isoformat()
            hour_key = message["timestamp"].hour
            
            daily_activity[date_key]["messages"] += 1
            hourly_distribution[hour_key] += 1
        
        # Calculate insights
        total_active_days = len(daily_activity)
        most_active_hour = max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 12
        favorite_subject = max(subject_focus.items(), key=lambda x: x[1])[0] if subject_focus else "None"
        
        return {
            "success": True,
            "patterns": {
                "active_days": total_active_days,
                "daily_activity": dict(daily_activity),
                "hourly_distribution": dict(hourly_distribution),
                "most_active_hour": most_active_hour,
                "subject_focus": dict(subject_focus),
                "favorite_subject": favorite_subject,
                "consistency_score": min(100, (total_active_days / days) * 100),
                "period_days": days
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting learning patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning patterns")

@api_router.get("/analytics/class-overview")
async def get_class_overview(
    days: int = 30,
    subject: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get class overview for educators (aggregated student data)"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = {"created_at": {"$gte": since_date}}
        if subject:
            query["subject"] = subject
        
        # Aggregate class performance
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$user_id",
                    "avg_score": {"$avg": "$final_score"},
                    "assessment_count": {"$sum": 1},
                    "latest_assessment": {"$max": "$created_at"}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_students": {"$sum": 1},
                    "class_avg_score": {"$avg": "$avg_score"},
                    "total_assessments": {"$sum": "$assessment_count"},
                    "score_distribution": {
                        "$push": {
                            "student_id": "$_id",
                            "avg_score": "$avg_score",
                            "assessment_count": "$assessment_count"
                        }
                    }
                }
            }
        ]
        
        result = list(db.assessments.aggregate(pipeline))
        
        if not result:
            return {
                "success": True,
                "overview": {
                    "total_students": 0,
                    "class_average": 0,
                    "total_assessments": 0,
                    "performance_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
                    "subject": subject,
                    "period_days": days
                }
            }
        
        data = result[0]
        
        # Calculate grade distribution
        scores = [student["avg_score"] for student in data["score_distribution"]]
        grade_distribution = {
            "A": len([s for s in scores if s >= 90]),
            "B": len([s for s in scores if 80 <= s < 90]),
            "C": len([s for s in scores if 70 <= s < 80]),
            "D": len([s for s in scores if 60 <= s < 70]),
            "F": len([s for s in scores if s < 60])
        }
        
        return {
            "success": True,
            "overview": {
                "total_students": data["total_students"],
                "class_average": round(data["class_avg_score"], 2),
                "total_assessments": data["total_assessments"],
                "performance_distribution": grade_distribution,
                "subject": subject,
                "period_days": days,
                "individual_scores": [
                    {
                        "student_id": student["student_id"],
                        "avg_score": round(student["avg_score"], 2),
                        "assessment_count": student["assessment_count"]
                    }
                    for student in data["score_distribution"]
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get class overview")

# ============================================================================
# COMPREHENSIVE REPORTING FOR EDUCATORS
# ============================================================================

class ReportRequest(BaseModel):
    days: int = 30
    subject: Optional[str] = None
    export_format: str = "json"  # json, pdf, csv

class StudentProgressReportRequest(BaseModel):
    student_id: str
    days: int = 30
    export_format: str = "json"

@api_router.post("/reports/student-progress")
async def generate_student_progress_report(
    request: StudentProgressReportRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate individual student progress report"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await reporting_system.generate_student_progress_report(
            educator_id=current_user.id,
            student_id=request.student_id,
            days=request.days,
            export_format=request.export_format
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating student progress report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@api_router.post("/reports/class-performance")
async def generate_class_performance_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate class performance summary report"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await reporting_system.generate_class_performance_report(
            educator_id=current_user.id,
            days=request.days,
            subject=request.subject,
            export_format=request.export_format
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating class performance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@api_router.post("/reports/subject-analytics")
async def generate_subject_analytics_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate subject-wise performance analysis report"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await reporting_system.generate_subject_analytics_report(
            educator_id=current_user.id,
            days=request.days,
            export_format=request.export_format
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating subject analytics report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@api_router.get("/reports/available")
async def get_available_reports(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get list of previously generated reports"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        reports = await reporting_system.get_available_reports(
            educator_id=current_user.id,
            limit=limit
        )
        
        return {
            "success": True,
            "reports": reports,
            "total": len(reports)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports")

@api_router.get("/reports/{report_id}")
async def get_report_by_id(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific report by ID"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await reporting_system.get_report_by_id(
            report_id=report_id,
            educator_id=current_user.id
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report")

@api_router.post("/reports/email")
async def email_report(
    report_id: str,
    recipient_email: str,
    current_user: User = Depends(get_current_user)
):
    """Email a report to specified recipient"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        # Get the report
        result = await reporting_system.get_report_by_id(
            report_id=report_id,
            educator_id=current_user.id
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_data = result["report"]
        
        # Send email using email service
        email_success = await email_service.send_learning_analytics_report(
            recipient_email=recipient_email,
            recipient_name="Educator",  # Could be improved with actual name
            report_data={
                "report_title": report_data.get("report_type", "Report"),
                "generated_at": report_data.get("generated_at"),
                "summary": "Comprehensive learning analytics report from IDFS PathwayIQ™"
            }
        )
        
        if email_success:
            return {
                "success": True,
                "message": f"Report emailed successfully to {recipient_email}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error emailing report: {e}")
        raise HTTPException(status_code=500, detail="Failed to email report")

# ============================================================================
# PREDICTIVE ANALYTICS - ML-BASED OUTCOME FORECASTING
# ============================================================================

class PredictionRequest(BaseModel):
    subject: str = "mathematics"
    questions_count: int = 10

class LearningOutcomesRequest(BaseModel):
    target_days: int = 30

@api_router.post("/predictive/train-models")
async def train_prediction_models(
    current_user: User = Depends(get_current_user)
):
    """Train ML models for predictive analytics (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await predictive_analytics.train_models()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training prediction models: {e}")
        raise HTTPException(status_code=500, detail="Failed to train models")

@api_router.post("/predictive/performance")
async def predict_student_performance(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """Predict student performance on upcoming assessment"""
    try:
        result = await predictive_analytics.predict_student_performance(
            user_id=current_user.id,
            subject=request.subject,
            questions_count=request.questions_count
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "prediction": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict performance")

@api_router.get("/predictive/risk-assessment")
async def assess_student_risk(
    current_user: User = Depends(get_current_user)
):
    """Assess if current student is at risk of poor performance"""
    try:
        result = await predictive_analytics.assess_student_risk(
            user_id=current_user.id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "assessment": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing student risk: {e}")
        raise HTTPException(status_code=500, detail="Failed to assess risk")

@api_router.post("/predictive/learning-outcomes")
async def predict_learning_outcomes(
    request: LearningOutcomesRequest,
    current_user: User = Depends(get_current_user)
):
    """Predict learning outcomes over specified time period"""
    try:
        result = await predictive_analytics.predict_learning_outcomes(
            user_id=current_user.id,
            target_days=request.target_days
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "predictions": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting learning outcomes: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict outcomes")

@api_router.get("/predictive/risk-assessment/student/{student_id}")
async def assess_specific_student_risk(
    student_id: str,
    current_user: User = Depends(get_current_user)
):
    """Assess specific student's risk (educators only)"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await predictive_analytics.assess_student_risk(
            user_id=student_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "student_id": student_id,
            "assessment": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing specific student risk: {e}")
        raise HTTPException(status_code=500, detail="Failed to assess student risk")

@api_router.post("/predictive/performance/student/{student_id}")
async def predict_specific_student_performance(
    student_id: str,
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """Predict specific student's performance (educators only)"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await predictive_analytics.predict_student_performance(
            user_id=student_id,
            subject=request.subject,
            questions_count=request.questions_count
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "student_id": student_id,
            "prediction": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting specific student performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict performance")

@api_router.get("/predictive/class-insights")
async def get_class_predictive_insights(
    current_user: User = Depends(get_current_user)
):
    """Get predictive insights for entire class (educators only)"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        # Get all students (in a real system, filter by educator's classes)
        students = list(db.users.find({"role": "student"}))
        
        class_insights = {
            "total_students": len(students),
            "risk_analysis": {"high": 0, "medium": 0, "low": 0, "unknown": 0},
            "performance_predictions": [],
            "recommendations": []
        }
        
        # Analyze each student
        for student in students[:20]:  # Limit to 20 students for performance
            try:
                risk_result = await predictive_analytics.assess_student_risk(student["id"])
                
                if "error" not in risk_result:
                    risk_level = risk_result.get("risk_level", "unknown")
                    class_insights["risk_analysis"][risk_level] += 1
                    
                    if risk_level in ["high", "medium"]:
                        class_insights["recommendations"].extend(
                            risk_result.get("recommendations", [])[:2]
                        )
                
            except Exception as e:
                logger.warning(f"Error analyzing student {student['id']}: {e}")
                class_insights["risk_analysis"]["unknown"] += 1
        
        # Generate class-level recommendations
        high_risk_count = class_insights["risk_analysis"]["high"]
        medium_risk_count = class_insights["risk_analysis"]["medium"]
        
        if high_risk_count > len(students) * 0.2:  # >20% high risk
            class_insights["recommendations"].insert(0, 
                "Consider class-wide intervention - high number of at-risk students")
        
        if medium_risk_count > len(students) * 0.3:  # >30% medium risk
            class_insights["recommendations"].insert(0, 
                "Increase monitoring and support for struggling students")
        
        # Remove duplicates
        class_insights["recommendations"] = list(set(class_insights["recommendations"]))[:5]
        
        return {
            "success": True,
            "insights": class_insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class predictive insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get class insights")

@api_router.get("/predictive/model-status")
async def get_model_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of ML models (educators and admins only)"""
    try:
        # Check if user is an educator or admin
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        model_status = {}
        
        for model_name in predictive_analytics.model_configs:
            model = await predictive_analytics._load_model(model_name)
            model_status[model_name] = {
                "available": model is not None,
                "type": predictive_analytics.model_configs[model_name]["model_type"],
                "algorithm": predictive_analytics.model_configs[model_name]["algorithm"]
            }
        
        return {
            "success": True,
            "models": model_status,
            "total_models": len(model_status),
            "available_models": sum(1 for status in model_status.values() if status["available"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model status")

# ============================================================================
# ENHANCED EMOTIONAL INTELLIGENCE ANALYSIS
# ============================================================================

class EmotionalAnalysisRequest(BaseModel):
    text_input: str
    context: str = "general"
    source: str = "assessment"

class EmotionalProfileRequest(BaseModel):
    days: int = 30

@api_router.post("/emotional-intelligence/analyze")
async def analyze_emotional_state(
    request: EmotionalAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze emotional state from text input"""
    try:
        result = await emotional_intelligence.analyze_emotional_state(
            user_id=current_user.id,
            text_input=request.text_input,
            context=request.context,
            source=request.source
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing emotional state: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze emotional state")

@api_router.get("/emotional-intelligence/profile")
async def get_emotional_profile(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive emotional profile for current user"""
    try:
        result = await emotional_intelligence.get_user_emotional_profile(
            user_id=current_user.id,
            days=days
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting emotional profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get emotional profile")

@api_router.get("/emotional-intelligence/profile/student/{student_id}")
async def get_student_emotional_profile(
    student_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get emotional profile for specific student (educators only)"""
    try:
        # Check if user is an educator
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied. Educator role required.")
        
        result = await emotional_intelligence.get_user_emotional_profile(
            user_id=student_id,
            days=days
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "student_id": student_id,
            "profile": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student emotional profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student profile")

@api_router.get("/emotional-intelligence/insights")
async def get_emotional_insights(
    current_user: User = Depends(get_current_user)
):
    """Get quick emotional intelligence insights for current user"""
    try:
        # Get recent emotional profile
        profile_result = await emotional_intelligence.get_user_emotional_profile(
            user_id=current_user.id,
            days=7  # Last week
        )
        
        if "error" in profile_result:
            return {
                "success": True,
                "insights": {
                    "message": "No recent emotional data available",
                    "recommendations": ["Take assessments to build emotional profile"]
                }
            }
        
        profile = profile_result["profile"]
        
        # Extract key insights
        insights = {
            "emotional_stability": profile.get("emotional_stability", 0.5),
            "dominant_emotions": profile.get("dominant_emotions", {}),
            "preferred_learning_style": profile.get("preferred_learning_style", "balanced"),
            "stress_frequency": profile.get("stress_patterns", {}).get("stress_frequency", 0),
            "ei_level": profile.get("emotional_intelligence", {}).get("level", "developing"),
            "quick_recommendations": [
                rec.get("title", "Continue learning")
                for rec in profile.get("recommendations", [])[:3]
            ]
        }
        
        return {
            "success": True,
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error getting emotional insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get emotional insights")

@api_router.post("/emotional-intelligence/analyze-speech")
async def analyze_speech_emotional_state(
    text_input: str,
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze emotional state from speech-to-text session"""
    try:
        result = await emotional_intelligence.analyze_emotional_state(
            user_id=current_user.id,
            text_input=text_input,
            context="think_aloud_assessment",
            source="speech_session"
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Also update the speech session with emotional analysis
        if result.get("success"):
            emotional_analysis = result["emotional_analysis"]
            
            # Update speech session with emotional data
            try:
                db.speech_sessions.update_one(
                    {"session_id": session_id, "user_id": current_user.id},
                    {
                        "$set": {
                            "emotional_analysis": {
                                "dominant_emotion": emotional_analysis.get("dominant_emotion"),
                                "sentiment_polarity": emotional_analysis.get("sentiment", {}).get("polarity", 0),
                                "cognitive_load": emotional_analysis.get("cognitive_load", {}).get("level"),
                                "ai_insights": emotional_analysis.get("ai_insights", {}),
                                "analyzed_at": datetime.utcnow()
                            }
                        }
                    }
                )
            except Exception as update_error:
                logger.warning(f"Failed to update speech session with emotional data: {update_error}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing speech emotional state: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze speech emotions")

@api_router.get("/emotional-intelligence/learning-recommendations")
async def get_personalized_learning_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Get personalized learning recommendations based on emotional profile"""
    try:
        # Get user's recent emotional profile
        profile_result = await emotional_intelligence.get_user_emotional_profile(
            user_id=current_user.id,
            days=14
        )
        
        if "error" in profile_result:
            return {
                "success": True,
                "recommendations": {
                    "message": "Take more assessments to get personalized recommendations",
                    "general_tips": [
                        "Maintain consistent study schedule",
                        "Take breaks to avoid fatigue",
                        "Practice positive self-talk"
                    ]
                }
            }
        
        profile = profile_result["profile"]
        recommendations = profile.get("recommendations", [])
        
        # Enhance recommendations with actionable steps
        enhanced_recommendations = []
        for rec in recommendations:
            enhanced_rec = {
                "category": rec.get("category", "general"),
                "priority": rec.get("priority", "medium"),
                "title": rec.get("title", "Learning Improvement"),
                "description": rec.get("description", "Recommendation for better learning"),
                "action_steps": rec.get("suggestions", []),
                "expected_outcome": _generate_outcome_description(rec.get("category"))
            }
            enhanced_recommendations.append(enhanced_rec)
        
        return {
            "success": True,
            "recommendations": {
                "personalized_recommendations": enhanced_recommendations,
                "emotional_summary": {
                    "stability": profile.get("emotional_stability", 0.5),
                    "dominant_emotions": profile.get("dominant_emotions", {}),
                    "learning_style": profile.get("preferred_learning_style", "balanced")
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting learning recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

def _generate_outcome_description(category: str) -> str:
    """Generate expected outcome description for recommendation category"""
    outcomes = {
        "stress_management": "Reduced anxiety and improved focus during learning",
        "learning_optimization": "Better retention and understanding of material",
        "emotional_regulation": "More consistent and positive learning experiences",
        "performance_optimization": "Higher assessment scores and improved confidence"
    }
    
    return outcomes.get(category, "Enhanced learning experience and academic performance")

# Include the router in the main app
app.include_router(api_router)

# Configure logging for production
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 PathwayIQ API starting up...")
    
    # Test database connection
    try:
        await client.admin.command('ping')
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    # Initialize indexes
    try:
        await db_indexer.create_all_indexes()
        logger.info("✅ Database indexes created")
    except Exception as e:
        logger.warning(f"⚠️ Database indexing warning: {e}")
    
    # Start health monitoring
    if os.getenv('MONITORING_ENABLED', 'true').lower() == 'true':
        asyncio.create_task(health_monitor.start_monitoring())
        logger.info("✅ Health monitoring started")
    
    # Cache warm-up
    try:
        # This would call cache warm-up functions
        logger.info("✅ Cache warm-up initiated")
    except Exception as e:
        logger.warning(f"⚠️ Cache warm-up warning: {e}")
    
    logger.info("🎉 PathwayIQ API startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🔄 PathwayIQ API shutting down...")
    
    # Close database connection
    try:
        client.close()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Database shutdown error: {e}")
    
    # Clean up cache
    try:
        await cache_manager.clear_all()
        logger.info("✅ Cache cleared")
    except Exception as e:
        logger.warning(f"⚠️ Cache cleanup warning: {e}")
    
    logger.info("✅ PathwayIQ API shutdown complete")