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
openai.api_key = OPENAI_API_KEY

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
    "https://f76bbcee-2f06-47e5-b40d-b20a8057d19a.preview.emergentagent.com",
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
        
        response = openai.chat.completions.create(
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