"""
AI-Powered Content Generation Module
Generates personalized learning materials, quizzes, and educational content
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from openai import AsyncOpenAI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import json

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class ContentType(str):
    """Enum for content types"""
    QUIZ = "quiz"
    LESSON = "lesson"
    EXPLANATION = "explanation"
    PRACTICE_PROBLEMS = "practice_problems"
    STUDY_GUIDE = "study_guide"
    FLASHCARDS = "flashcards"

class DifficultyLevel(str):
    """Enum for difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    content_type: str
    subject: str
    topic: str
    difficulty_level: str = DifficultyLevel.INTERMEDIATE
    learning_objectives: List[str] = []
    target_audience: str = "8th grade students"
    length: str = "medium"  # short, medium, long
    personalization_data: Optional[Dict[str, Any]] = None
    context_prompt: Optional[str] = None

class GeneratedContent(BaseModel):
    """Model for generated content"""
    id: str
    user_id: str
    content_type: str
    subject: str
    topic: str
    difficulty_level: str
    title: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    generation_time: float
    quality_score: float
    usage_count: int = 0

class AIContentGenerator:
    """Main AI content generation class"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.content_templates = {
            ContentType.QUIZ: self._generate_quiz_template,
            ContentType.LESSON: self._generate_lesson_template,
            ContentType.EXPLANATION: self._generate_explanation_template,
            ContentType.PRACTICE_PROBLEMS: self._generate_practice_problems_template,
            ContentType.STUDY_GUIDE: self._generate_study_guide_template,
            ContentType.FLASHCARDS: self._generate_flashcards_template
        }
    
    async def generate_content(
        self,
        request: ContentGenerationRequest,
        user_id: str
    ) -> GeneratedContent:
        """Generate educational content based on request"""
        
        start_time = datetime.now()
        
        try:
            # Get user learning data for personalization
            user_data = await self._get_user_learning_data(user_id)
            
            # Generate content using appropriate template
            content_generator = self.content_templates.get(request.content_type)
            if not content_generator:
                raise ValueError(f"Unsupported content type: {request.content_type}")
            
            # Generate content
            generated_content = await content_generator(request, user_data)
            
            # Calculate quality score
            quality_score = await self._assess_content_quality(generated_content, request)
            
            # Create content record
            content_record = GeneratedContent(
                id=str(uuid.uuid4()),
                user_id=user_id,
                content_type=request.content_type,
                subject=request.subject,
                topic=request.topic,
                difficulty_level=request.difficulty_level,
                title=generated_content.get("title", f"{request.topic} - {request.content_type}"),
                content=generated_content,
                metadata={
                    "learning_objectives": request.learning_objectives,
                    "target_audience": request.target_audience,
                    "length": request.length,
                    "personalization_applied": bool(user_data),
                    "generation_model": "gpt-4"
                },
                created_at=datetime.now(timezone.utc),
                generation_time=(datetime.now() - start_time).total_seconds(),
                quality_score=quality_score
            )
            
            # Store in database
            await self._store_content(content_record)
            
            logger.info(f"Content generated for user {user_id}: {content_record.id}")
            return content_record
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            raise
    
    async def _generate_quiz_template(self, request: ContentGenerationRequest, user_data: Dict) -> Dict[str, Any]:
        """Generate quiz content"""
        
        personalization_context = ""
        if user_data and user_data.get("learning_style"):
            personalization_context = f"The student prefers {user_data['learning_style']} learning style."
        
        prompt = f"""
        Generate a comprehensive quiz on {request.topic} for {request.target_audience}.
        
        Requirements:
        - Subject: {request.subject}
        - Difficulty: {request.difficulty_level}
        - Learning objectives: {', '.join(request.learning_objectives)}
        - Length: {request.length} (short=5 questions, medium=10 questions, long=15 questions)
        {personalization_context}
        
        Format the response as JSON with this structure:
        {{
            "title": "Quiz title",
            "instructions": "Clear instructions for students",
            "questions": [
                {{
                    "id": "q1",
                    "question": "Question text",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "explanation": "Explanation of the answer",
                    "points": 10,
                    "difficulty": "intermediate"
                }}
            ],
            "total_points": 100,
            "estimated_time": "15 minutes",
            "learning_objectives_covered": ["objective1", "objective2"]
        }}
        
        Include a variety of question types: multiple choice, true/false, short answer.
        Make questions engaging and educational.
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educational content creator specializing in quiz development."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_lesson_template(self, request: ContentGenerationRequest, user_data: Dict) -> Dict[str, Any]:
        """Generate lesson content"""
        
        personalization_context = ""
        if user_data:
            if user_data.get("learning_style"):
                personalization_context += f"Adapt content for {user_data['learning_style']} learning style. "
            if user_data.get("performance_areas"):
                personalization_context += f"Focus on areas where student needs improvement: {', '.join(user_data['performance_areas'])}. "
        
        prompt = f"""
        Create a comprehensive lesson on {request.topic} for {request.target_audience}.
        
        Requirements:
        - Subject: {request.subject}
        - Difficulty: {request.difficulty_level}
        - Learning objectives: {', '.join(request.learning_objectives)}
        - Length: {request.length}
        {personalization_context}
        
        Format the response as JSON with this structure:
        {{
            "title": "Lesson title",
            "introduction": "Engaging introduction",
            "learning_objectives": ["objective1", "objective2"],
            "sections": [
                {{
                    "title": "Section title",
                    "content": "Detailed content",
                    "examples": ["example1", "example2"],
                    "key_concepts": ["concept1", "concept2"]
                }}
            ],
            "summary": "Key takeaways",
            "practice_activities": ["activity1", "activity2"],
            "assessment_suggestions": ["suggestion1", "suggestion2"],
            "estimated_duration": "45 minutes",
            "materials_needed": ["material1", "material2"]
        }}
        
        Make the content engaging, clear, and educational.
        Include real-world examples and applications.
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educational content creator and curriculum designer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_explanation_template(self, request: ContentGenerationRequest, user_data: Dict) -> Dict[str, Any]:
        """Generate explanation content"""
        
        prompt = f"""
        Provide a clear, detailed explanation of {request.topic} for {request.target_audience}.
        
        Requirements:
        - Subject: {request.subject}
        - Difficulty: {request.difficulty_level}
        - Make it understandable and engaging
        - Include examples and analogies
        - Break down complex concepts into simple parts
        
        Format the response as JSON with this structure:
        {{
            "title": "Explanation title",
            "overview": "Brief overview",
            "main_explanation": "Detailed explanation",
            "key_points": ["point1", "point2"],
            "examples": [
                {{
                    "title": "Example title",
                    "description": "Example description",
                    "solution": "Step-by-step solution"
                }}
            ],
            "analogies": ["analogy1", "analogy2"],
            "common_misconceptions": ["misconception1", "misconception2"],
            "related_concepts": ["concept1", "concept2"],
            "next_steps": "What to learn next"
        }}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educator who excels at explaining complex concepts in simple terms."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_practice_problems_template(self, request: ContentGenerationRequest, user_data: Dict) -> Dict[str, Any]:
        """Generate practice problems"""
        
        prompt = f"""
        Create practice problems for {request.topic} suitable for {request.target_audience}.
        
        Requirements:
        - Subject: {request.subject}
        - Difficulty: {request.difficulty_level}
        - Length: {request.length} (short=5 problems, medium=10 problems, long=15 problems)
        - Include step-by-step solutions
        - Vary difficulty within the level
        
        Format the response as JSON with this structure:
        {{
            "title": "Practice Problems title",
            "instructions": "How to approach these problems",
            "problems": [
                {{
                    "id": "p1",
                    "problem": "Problem statement",
                    "difficulty": "intermediate",
                    "solution": "Step-by-step solution",
                    "hints": ["hint1", "hint2"],
                    "concepts_used": ["concept1", "concept2"]
                }}
            ],
            "tips": ["tip1", "tip2"],
            "estimated_time": "30 minutes"
        }}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert mathematics educator who creates engaging practice problems."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_study_guide_template(self, request: ContentGenerationRequest, user_data: Dict) -> Dict[str, Any]:
        """Generate study guide"""
        
        prompt = f"""
        Create a comprehensive study guide for {request.topic} for {request.target_audience}.
        
        Requirements:
        - Subject: {request.subject}
        - Difficulty: {request.difficulty_level}
        - Cover all important concepts
        - Include review questions
        - Provide study strategies
        
        Format the response as JSON with this structure:
        {{
            "title": "Study Guide title",
            "overview": "What this guide covers",
            "key_concepts": [
                {{
                    "concept": "Concept name",
                    "definition": "Clear definition",
                    "importance": "Why it matters",
                    "examples": ["example1", "example2"]
                }}
            ],
            "formulas": [
                {{
                    "name": "Formula name",
                    "formula": "Mathematical formula",
                    "when_to_use": "Application context"
                }}
            ],
            "review_questions": [
                {{
                    "question": "Review question",
                    "answer": "Brief answer"
                }}
            ],
            "study_strategies": ["strategy1", "strategy2"],
            "common_mistakes": ["mistake1", "mistake2"],
            "recommended_practice": "Practice suggestions"
        }}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert study skills coach and educational content creator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_flashcards_template(self, request: ContentGenerationRequest, user_data: Dict) -> Dict[str, Any]:
        """Generate flashcards"""
        
        prompt = f"""
        Create flashcards for {request.topic} suitable for {request.target_audience}.
        
        Requirements:
        - Subject: {request.subject}
        - Difficulty: {request.difficulty_level}
        - Length: {request.length} (short=10 cards, medium=20 cards, long=30 cards)
        - Include key terms, concepts, and formulas
        - Make them effective for memorization
        
        Format the response as JSON with this structure:
        {{
            "title": "Flashcards title",
            "instructions": "How to use these flashcards",
            "cards": [
                {{
                    "id": "f1",
                    "front": "Question or term",
                    "back": "Answer or definition",
                    "category": "category",
                    "difficulty": "intermediate",
                    "mnemonic": "Memory aid (optional)"
                }}
            ],
            "study_tips": ["tip1", "tip2"],
            "estimated_study_time": "20 minutes"
        }}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in creating effective study materials and flashcards."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _get_user_learning_data(self, user_id: str) -> Dict[str, Any]:
        """Get user learning data for personalization"""
        try:
            # Get user answers for performance analysis
            user_answers = await self.db.user_answers.find({"user_id": user_id}).to_list(100)
            
            # Get user profile data
            user_profile = await self.db.users.find_one({"id": user_id})
            
            # Analyze performance
            performance_data = {
                "total_questions": len(user_answers),
                "accuracy": 0,
                "strong_subjects": [],
                "weak_subjects": [],
                "learning_style": "visual",  # Default or determined from interactions
                "performance_areas": []
            }
            
            if user_answers:
                correct_answers = sum(1 for answer in user_answers if answer.get("is_correct", False))
                performance_data["accuracy"] = correct_answers / len(user_answers)
                
                # Analyze by subject
                subject_performance = {}
                for answer in user_answers:
                    # Get question to determine subject
                    question = await self.db.questions.find_one({"id": answer["question_id"]})
                    if question:
                        subject = question.get("subject", "unknown")
                        if subject not in subject_performance:
                            subject_performance[subject] = {"correct": 0, "total": 0}
                        subject_performance[subject]["total"] += 1
                        if answer.get("is_correct", False):
                            subject_performance[subject]["correct"] += 1
                
                # Determine strong and weak subjects
                for subject, stats in subject_performance.items():
                    accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
                    if accuracy > 0.8:
                        performance_data["strong_subjects"].append(subject)
                    elif accuracy < 0.6:
                        performance_data["weak_subjects"].append(subject)
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting user learning data: {str(e)}")
            return {}
    
    async def _assess_content_quality(self, content: Dict[str, Any], request: ContentGenerationRequest) -> float:
        """Assess the quality of generated content"""
        try:
            # Simple quality assessment based on content characteristics
            quality_score = 0.8  # Base score
            
            # Check for key elements
            if "title" in content:
                quality_score += 0.1
            if "learning_objectives" in content or "key_concepts" in content:
                quality_score += 0.1
            
            # Adjust based on content type
            if request.content_type == ContentType.QUIZ:
                if "questions" in content and len(content["questions"]) > 0:
                    quality_score += 0.1
            elif request.content_type == ContentType.LESSON:
                if "sections" in content and len(content["sections"]) > 0:
                    quality_score += 0.1
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {str(e)}")
            return 0.7  # Default score
    
    async def _store_content(self, content: GeneratedContent):
        """Store generated content in database"""
        try:
            await self.db.generated_content.insert_one(content.dict())
            logger.info(f"Stored content {content.id} for user {content.user_id}")
        except Exception as e:
            logger.error(f"Database storage error: {str(e)}")
            raise
    
    async def get_user_content(self, user_id: str, content_type: Optional[str] = None, limit: int = 20) -> List[GeneratedContent]:
        """Get user's generated content"""
        try:
            query = {"user_id": user_id}
            if content_type:
                query["content_type"] = content_type
            
            cursor = self.db.generated_content.find(query).sort("created_at", -1).limit(limit)
            contents = await cursor.to_list(length=None)
            return [GeneratedContent(**content) for content in contents]
        except Exception as e:
            logger.error(f"Error retrieving user content: {str(e)}")
            return []
    
    async def get_content_by_id(self, content_id: str, user_id: str) -> Optional[GeneratedContent]:
        """Get specific content by ID"""
        try:
            content = await self.db.generated_content.find_one({"id": content_id, "user_id": user_id})
            if content:
                return GeneratedContent(**content)
            return None
        except Exception as e:
            logger.error(f"Error retrieving content: {str(e)}")
            return None

# Global generator instance
content_generator = None

def get_content_generator(db: AsyncIOMotorDatabase) -> AIContentGenerator:
    """Get content generator instance"""
    global content_generator
    if content_generator is None:
        content_generator = AIContentGenerator(db)
    return content_generator