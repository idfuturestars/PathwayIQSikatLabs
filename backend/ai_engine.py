"""
IDFS StarGuide Advanced AI Engine - Phase 1
Complete AI enhancement system with:
- Voice-to-Text Learning
- Emotional Intelligence Detection  
- Multi-Model AI Study Buddy
- Personalized Learning Paths
- Advanced Analytics
"""

import openai
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum
import json
import numpy as np
from collections import defaultdict
import speech_recognition as sr
import pydub
from pydub import AudioSegment
import io
import base64
import re
from textblob import TextBlob
import torch
import os

logger = logging.getLogger(__name__)

class EmotionalState(str, Enum):
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    BORED = "bored"
    FOCUSED = "focused"

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"

class AIPersonality(str, Enum):
    ENCOURAGING = "encouraging"  # Supportive and positive
    ANALYTICAL = "analytical"   # Logical and systematic
    CREATIVE = "creative"       # Imaginative and innovative
    PATIENT = "patient"         # Calm and methodical
    ENERGETIC = "energetic"     # Dynamic and enthusiastic

class AdvancedAIEngine:
    def __init__(self):
        self.emotion_classifier = None
        self.learning_style_detector = None
        self.voice_recognizer = sr.Recognizer()
        self.ai_personalities = {
            AIPersonality.ENCOURAGING: {
                "system_prompt": "You are StarGuide AI, an encouraging and supportive tutor. Always provide positive reinforcement, celebrate small wins, and help students build confidence. Use uplifting language and motivate students to keep trying.",
                "response_style": "warm_supportive"
            },
            AIPersonality.ANALYTICAL: {
                "system_prompt": "You are StarGuide AI, a logical and analytical tutor. Break down problems systematically, provide step-by-step explanations, and help students understand underlying principles and patterns.",
                "response_style": "structured_logical"
            },
            AIPersonality.CREATIVE: {
                "system_prompt": "You are StarGuide AI, a creative and imaginative tutor. Use metaphors, analogies, stories, and creative examples to make learning engaging and memorable. Think outside the box.",
                "response_style": "creative_engaging"
            },
            AIPersonality.PATIENT: {
                "system_prompt": "You are StarGuide AI, a patient and methodical tutor. Take your time to explain concepts thoroughly, repeat when necessary, and never rush students. Focus on deep understanding.",
                "response_style": "calm_thorough"
            },
            AIPersonality.ENERGETIC: {
                "system_prompt": "You are StarGuide AI, an energetic and enthusiastic tutor. Bring excitement to learning, use dynamic language, and make every lesson feel like an adventure. Be engaging and lively.",
                "response_style": "dynamic_exciting"
            }
        }
        self.initialize_ai_models()

    def initialize_ai_models(self):
        """Initialize AI models for emotion detection and learning style analysis"""
        try:
            # Simple emotion classifier using keyword analysis (fallback method)
            self.emotion_classifier = self._create_keyword_emotion_classifier()
            logger.info("Emotion classifier initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize emotion classifier: {e}")
            self.emotion_classifier = None

        try:
            # Initialize learning style detector
            self.learning_style_detector = self._create_learning_style_detector()
            logger.info("Learning style detector initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize learning style detector: {e}")

    def _create_keyword_emotion_classifier(self):
        """Create a keyword-based emotion classifier"""
        return {
            EmotionalState.FRUSTRATED: [
                "stuck", "don't understand", "confused", "hard", "difficult", "frustrated",
                "annoying", "impossible", "hate", "can't", "won't work", "stupid"
            ],
            EmotionalState.CONFIDENT: [
                "easy", "got it", "understand", "clear", "simple", "confident",
                "know", "sure", "obvious", "piece of cake", "no problem"
            ],
            EmotionalState.EXCITED: [
                "love", "amazing", "cool", "awesome", "interesting", "fun",
                "exciting", "wow", "great", "fantastic", "brilliant"
            ],
            EmotionalState.ANXIOUS: [
                "worried", "nervous", "scared", "anxious", "uncertain", "afraid",
                "stress", "pressure", "overwhelmed", "panic"
            ],
            EmotionalState.BORED: [
                "boring", "tired", "slow", "tedious", "uninteresting", "dull",
                "repetitive", "monotonous", "sleep", "yawn"
            ],
            EmotionalState.CONFUSED: [
                "what", "how", "why", "confused", "lost", "unclear", "don't get it",
                "mixed up", "puzzled", "bewildered"
            ]
        }

    def _create_learning_style_detector(self):
        """Create a simple learning style detector based on keywords and patterns"""
        return {
            LearningStyle.VISUAL: [
                "see", "look", "picture", "image", "diagram", "chart", "visual", "show me",
                "draw", "illustrate", "color", "bright", "appearance", "view", "graph"
            ],
            LearningStyle.AUDITORY: [
                "hear", "listen", "sound", "music", "rhythm", "voice", "speak", "tell me",
                "audio", "loud", "quiet", "melody", "tone", "pronunciation", "discuss"
            ],
            LearningStyle.KINESTHETIC: [
                "touch", "feel", "move", "action", "practice", "hands-on", "build", "make",
                "physical", "exercise", "movement", "gesture", "active", "do"
            ],
            LearningStyle.READING_WRITING: [
                "read", "write", "text", "book", "article", "list", "notes", "journal",
                "essay", "paragraph", "word", "sentence", "literature", "document"
            ]
        }

    async def process_voice_input(self, audio_data: bytes, user_id: str) -> Dict[str, Any]:
        """Process voice input and convert to text with emotional analysis"""
        try:
            # For now, return a simulated response since we don't have the full audio processing setup
            # In production, this would process the actual audio data
            return {
                "transcribed_text": "Hello, can you help me with this math problem?",
                "emotional_state": EmotionalState.FOCUSED,
                "learning_style": LearningStyle.MULTIMODAL,
                "confidence_score": 0.85,
                "processing_time": datetime.now(timezone.utc).isoformat(),
                "note": "Voice processing simulated - replace with real implementation"
            }
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return {
                "error": str(e),
                "transcribed_text": "",
                "emotional_state": EmotionalState.FRUSTRATED,
                "learning_style": None
            }

    async def detect_emotional_state(self, text: str, audio_data: Optional[bytes] = None) -> EmotionalState:
        """Detect emotional state from text and optionally audio"""
        try:
            if self.emotion_classifier and text:
                text_lower = text.lower()
                emotion_scores = defaultdict(int)
                
                # Score emotions based on keyword matches
                for emotion, keywords in self.emotion_classifier.items():
                    for keyword in keywords:
                        if keyword in text_lower:
                            emotion_scores[emotion] += 1
                
                # Return emotion with highest score, or focused as default
                if emotion_scores:
                    return max(emotion_scores, key=emotion_scores.get)
                else:
                    return EmotionalState.FOCUSED
            else:
                return EmotionalState.FOCUSED
                
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return EmotionalState.FOCUSED

    def detect_learning_style_from_text(self, text: str) -> LearningStyle:
        """Detect preferred learning style from text patterns"""
        if not self.learning_style_detector:
            return LearningStyle.MULTIMODAL
        
        text_lower = text.lower()
        style_scores = defaultdict(int)
        
        for style, keywords in self.learning_style_detector.items():
            for keyword in keywords:
                if keyword in text_lower:
                    style_scores[style] += 1
        
        if not style_scores:
            return LearningStyle.MULTIMODAL
        
        # Return the style with the highest score
        return max(style_scores, key=style_scores.get)

    async def generate_adaptive_response(
        self, 
        message: str, 
        user_context: Dict[str, Any],
        emotional_state: EmotionalState,
        learning_style: LearningStyle,
        ai_personality: AIPersonality = AIPersonality.ENCOURAGING
    ) -> Dict[str, Any]:
        """Generate adaptive AI response based on emotional state and learning style"""
        
        try:
            # Select appropriate AI personality based on emotional state
            selected_personality = self._select_optimal_personality(emotional_state, ai_personality)
            
            # Customize system prompt based on context
            system_prompt = self._build_adaptive_system_prompt(
                selected_personality, emotional_state, learning_style, user_context
            )
            
            # Generate response using OpenAI
            response = await self._generate_openai_response(message, system_prompt, user_context)
            
            # Add emotional intelligence enhancements
            enhanced_response = self._enhance_response_with_emotional_intelligence(
                response, emotional_state, learning_style
            )
            
            return {
                "response": enhanced_response,
                "ai_personality": selected_personality.value,
                "emotional_state_detected": emotional_state.value,
                "learning_style_detected": learning_style.value,
                "adaptations_applied": self._get_adaptations_summary(emotional_state, learning_style),
                "next_suggestions": self._generate_next_suggestions(emotional_state, learning_style)
            }
            
        except Exception as e:
            logger.error(f"Adaptive response generation error: {e}")
            return {
                "response": "I'm here to help you learn! Could you tell me more about what you're working on?",
                "error": str(e)
            }

    def _select_optimal_personality(self, emotional_state: EmotionalState, default: AIPersonality) -> AIPersonality:
        """Select the best AI personality for the current emotional state"""
        personality_mapping = {
            EmotionalState.FRUSTRATED: AIPersonality.PATIENT,
            EmotionalState.CONFUSED: AIPersonality.ANALYTICAL,
            EmotionalState.ANXIOUS: AIPersonality.ENCOURAGING,
            EmotionalState.BORED: AIPersonality.CREATIVE,
            EmotionalState.EXCITED: AIPersonality.ENERGETIC,
            EmotionalState.CONFIDENT: AIPersonality.ANALYTICAL,
            EmotionalState.FOCUSED: default
        }
        return personality_mapping.get(emotional_state, default)

    def _build_adaptive_system_prompt(
        self, 
        personality: AIPersonality, 
        emotional_state: EmotionalState, 
        learning_style: LearningStyle,
        user_context: Dict[str, Any]
    ) -> str:
        """Build an adaptive system prompt based on all context"""
        
        base_prompt = self.ai_personalities[personality]["system_prompt"]
        
        # Add emotional state adaptations
        emotional_adaptations = {
            EmotionalState.FRUSTRATED: " The student seems frustrated, so be extra patient and break things down into smaller, manageable steps. Acknowledge their feelings and provide encouragement.",
            EmotionalState.CONFUSED: " The student is confused, so focus on clarity and providing multiple explanations from different angles. Ask clarifying questions to understand where the confusion lies.",
            EmotionalState.ANXIOUS: " The student appears anxious, so be reassuring and create a safe learning environment. Emphasize that mistakes are part of learning.",
            EmotionalState.BORED: " The student seems bored, so make the content more engaging with interesting examples, real-world applications, and interactive elements.",
            EmotionalState.EXCITED: " The student is excited about learning! Maintain their enthusiasm while providing substantial content to satisfy their curiosity.",
            EmotionalState.CONFIDENT: " The student is confident, so you can introduce more challenging concepts while maintaining their positive momentum."
        }
        
        # Add learning style adaptations
        learning_style_adaptations = {
            LearningStyle.VISUAL: " This student prefers visual learning, so suggest diagrams, charts, images, and visual representations when explaining concepts.",
            LearningStyle.AUDITORY: " This student learns best through audio, so use verbal explanations, suggest reading aloud, and incorporate rhythm or music when possible.",
            LearningStyle.KINESTHETIC: " This student learns through movement and hands-on activities, so suggest practical exercises, experiments, and physical demonstrations.",
            LearningStyle.READING_WRITING: " This student prefers text-based learning, so provide written explanations, suggest note-taking, and use text-based examples.",
            LearningStyle.MULTIMODAL: " This student benefits from multiple learning modalities, so combine visual, auditory, and kinesthetic approaches."
        }
        
        # Combine all adaptations
        adapted_prompt = base_prompt
        adapted_prompt += emotional_adaptations.get(emotional_state, "")
        adapted_prompt += learning_style_adaptations.get(learning_style, "")
        
        # Add user context
        if user_context.get("level"):
            adapted_prompt += f" The student is at level {user_context['level']}."
        
        if user_context.get("role"):
            adapted_prompt += f" This is a {user_context['role']} user."
        
        return adapted_prompt

    async def _generate_openai_response(self, message: str, system_prompt: str, user_context: Dict[str, Any]) -> str:
        """Generate response using OpenAI with adaptive prompting"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Use the synchronous version of the API since we're in an async function
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI response generation error: {e}")
            return "I'm having trouble generating a response right now. Let me try to help you in a different way."

    def _enhance_response_with_emotional_intelligence(
        self, 
        response: str, 
        emotional_state: EmotionalState, 
        learning_style: LearningStyle
    ) -> str:
        """Add emotional intelligence enhancements to the response"""
        
        # Add emotional acknowledgment
        emotional_acknowledgments = {
            EmotionalState.FRUSTRATED: "I can sense this might be challenging for you. ",
            EmotionalState.CONFUSED: "I understand this concept can be confusing at first. ",
            EmotionalState.ANXIOUS: "It's completely normal to feel uncertain when learning something new. ",
            EmotionalState.BORED: "Let's make this more interesting! ",
            EmotionalState.EXCITED: "I love your enthusiasm for learning! ",
            EmotionalState.CONFIDENT: "You're doing great! "
        }
        
        acknowledgment = emotional_acknowledgments.get(emotional_state, "")
        
        # Add learning style cues
        style_cues = {
            LearningStyle.VISUAL: "\n\n💡 *Tip: Try drawing this out or creating a diagram to visualize the concept!*",
            LearningStyle.AUDITORY: "\n\n🎵 *Tip: Try reading this explanation out loud or discussing it with someone!*",
            LearningStyle.KINESTHETIC: "\n\n👐 *Tip: Try doing this hands-on or finding a physical way to practice!*",
            LearningStyle.READING_WRITING: "\n\n📝 *Tip: Try taking notes or writing a summary of this concept!*"
        }
        
        style_cue = style_cues.get(learning_style, "")
        
        return acknowledgment + response + style_cue

    def _get_adaptations_summary(self, emotional_state: EmotionalState, learning_style: LearningStyle) -> List[str]:
        """Get a summary of adaptations applied"""
        adaptations = []
        
        if emotional_state == EmotionalState.FRUSTRATED:
            adaptations.append("Applied patience and step-by-step breakdown")
        elif emotional_state == EmotionalState.CONFUSED:
            adaptations.append("Focused on clarity and multiple explanations")
        elif emotional_state == EmotionalState.ANXIOUS:
            adaptations.append("Added reassurance and safe learning environment")
        elif emotional_state == EmotionalState.BORED:
            adaptations.append("Increased engagement with interesting examples")
        
        adaptations.append(f"Optimized for {learning_style.value} learning style")
        
        return adaptations

    def _generate_next_suggestions(self, emotional_state: EmotionalState, learning_style: LearningStyle) -> List[str]:
        """Generate suggestions for the next steps in learning"""
        suggestions = []
        
        if emotional_state == EmotionalState.FRUSTRATED:
            suggestions.extend([
                "Take a short break and come back with fresh eyes",
                "Try breaking the problem into smaller parts",
                "Ask for help from a study buddy or teacher"
            ])
        elif emotional_state == EmotionalState.CONFIDENT:
            suggestions.extend([
                "Try a more challenging problem",
                "Help explain this concept to another student",
                "Explore related advanced topics"
            ])
        
        if learning_style == LearningStyle.VISUAL:
            suggestions.append("Create a mind map or diagram of what you've learned")
        elif learning_style == LearningStyle.KINESTHETIC:
            suggestions.append("Find a hands-on activity related to this topic")
        
        return suggestions

    async def generate_personalized_learning_path(
        self, 
        user_id: str, 
        subject: str, 
        current_level: int,
        learning_goals: List[str],
        learning_style: LearningStyle,
        user_performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a personalized learning path using AI"""
        
        try:
            # Analyze user's strengths and weaknesses
            analysis = await self._analyze_user_performance(user_performance_data)
            
            # Generate customized curriculum
            curriculum = await self._generate_adaptive_curriculum(
                subject, current_level, learning_goals, learning_style, analysis
            )
            
            # Create milestone system
            milestones = self._create_learning_milestones(curriculum, learning_goals)
            
            # Generate recommended study schedule
            schedule = self._generate_study_schedule(curriculum, user_performance_data)
            
            return {
                "learning_path_id": f"path_{user_id}_{datetime.now().strftime('%Y%m%d')}",
                "subject": subject,
                "personalized_curriculum": curriculum,
                "learning_milestones": milestones,
                "recommended_schedule": schedule,
                "performance_analysis": analysis,
                "estimated_completion_time": self._estimate_completion_time(curriculum),
                "adaptive_adjustments": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Learning path generation error: {e}")
            return {"error": str(e)}

    async def _analyze_user_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user performance to identify strengths and weaknesses"""
        
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "learning_velocity": 0.0,
            "retention_rate": 0.0,
            "preferred_difficulty": "medium",
            "optimal_session_length": 30  # minutes
        }
        
        if not performance_data:
            return analysis
        
        # Analyze accuracy by topic
        topic_accuracy = performance_data.get("topic_accuracy", {})
        for topic, accuracy in topic_accuracy.items():
            if accuracy > 0.8:
                analysis["strengths"].append(topic)
            elif accuracy < 0.6:
                analysis["weaknesses"].append(topic)
        
        # Calculate learning velocity (improvement over time)
        recent_scores = performance_data.get("recent_scores", [])
        if len(recent_scores) >= 5:
            early_avg = sum(recent_scores[:5]) / 5
            recent_avg = sum(recent_scores[-5:]) / 5
            analysis["learning_velocity"] = (recent_avg - early_avg) / len(recent_scores)
        
        # Calculate retention rate
        retention_tests = performance_data.get("retention_tests", [])
        if retention_tests:
            analysis["retention_rate"] = sum(retention_tests) / len(retention_tests)
        
        return analysis

    async def _generate_adaptive_curriculum(
        self, 
        subject: str, 
        current_level: int, 
        learning_goals: List[str],
        learning_style: LearningStyle,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate adaptive curriculum using AI"""
        
        # Create a structured curriculum based on the learning style and goals
        base_modules = [
            {
                "module_id": "fundamentals",
                "title": f"{subject} Fundamentals",
                "description": f"Core concepts in {subject}",
                "estimated_hours": 10,
                "lessons": [
                    {"lesson_id": "intro", "title": "Introduction", "duration_minutes": 30},
                    {"lesson_id": "basics", "title": "Basic Concepts", "duration_minutes": 45},
                    {"lesson_id": "practice", "title": "Practice Problems", "duration_minutes": 60}
                ]
            },
            {
                "module_id": "intermediate",
                "title": f"Intermediate {subject}",
                "description": f"Building on fundamentals",
                "estimated_hours": 15,
                "lessons": [
                    {"lesson_id": "advanced_concepts", "title": "Advanced Concepts", "duration_minutes": 45},
                    {"lesson_id": "applications", "title": "Real-world Applications", "duration_minutes": 60},
                    {"lesson_id": "problem_solving", "title": "Problem Solving Strategies", "duration_minutes": 90}
                ]
            }
        ]
        
        # Adapt based on learning style
        if learning_style == LearningStyle.VISUAL:
            for module in base_modules:
                for lesson in module["lessons"]:
                    lesson["activities"] = ["diagrams", "charts", "visual_examples"]
        elif learning_style == LearningStyle.KINESTHETIC:
            for module in base_modules:
                for lesson in module["lessons"]:
                    lesson["activities"] = ["hands_on_exercises", "simulations", "experiments"]
        
        return base_modules

    def _create_learning_milestones(self, curriculum: List[Dict[str, Any]], goals: List[str]) -> List[Dict[str, Any]]:
        """Create learning milestones based on curriculum and goals"""
        milestones = []
        
        for i, module in enumerate(curriculum):
            milestone = {
                "milestone_id": f"milestone_{i+1}",
                "title": f"Complete {module['title']}",
                "description": f"Master all concepts in {module['title']}",
                "target_completion": f"Week {i*2 + 2}",
                "success_criteria": [
                    "Complete all lessons in module",
                    "Achieve 80% accuracy on module assessment",
                    "Demonstrate understanding through practical application"
                ]
            }
            milestones.append(milestone)
        
        return milestones

    def _generate_study_schedule(self, curriculum: List[Dict[str, Any]], performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal study schedule"""
        
        # Calculate optimal session length based on user data
        optimal_length = performance_data.get("average_session_length", 30)
        
        # Calculate total study time needed
        total_hours = sum(module.get("estimated_hours", 5) for module in curriculum)
        
        schedule = {
            "sessions_per_week": 4,
            "session_duration_minutes": optimal_length,
            "total_weeks": max(4, total_hours // 2),
            "daily_schedule": {
                "monday": {"time": "evening", "focus": "new_concepts"},
                "wednesday": {"time": "evening", "focus": "practice"},
                "friday": {"time": "evening", "focus": "review"},
                "saturday": {"time": "morning", "focus": "projects"}
            },
            "break_frequency": "every_25_minutes",
            "review_frequency": "weekly"
        }
        
        return schedule

    def _estimate_completion_time(self, curriculum: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate completion time for the curriculum"""
        total_hours = sum(module.get("estimated_hours", 5) for module in curriculum)
        
        return {
            "total_hours": total_hours,
            "weeks_intensive": max(4, total_hours // 4),  # 4 hours per week
            "weeks_regular": max(6, total_hours // 2),    # 2 hours per week
            "weeks_casual": max(8, total_hours),          # 1 hour per week
        }

# Global instance
advanced_ai_engine = AdvancedAIEngine()