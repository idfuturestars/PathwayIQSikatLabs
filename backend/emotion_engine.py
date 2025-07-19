"""
Enhanced Emotional Intelligence Analysis Engine for IDFS PathwayIQ™ powered by SikatLabs™

This module handles advanced AI personalization and emotional intelligence including:
- Emotional state detection and analysis
- Mood-based learning adaptation
- Stress and anxiety recognition
- Motivational state assessment
- Personalized emotional support
- Learning style adaptation based on emotional patterns
- Empathetic AI interactions
- Emotional learning journey tracking
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pymongo import MongoClient
import uuid
import json
import re
from enum import Enum
import statistics
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionalState(str, Enum):
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    CURIOUS = "curious"
    OVERWHELMED = "overwhelmed"
    MOTIVATED = "motivated"
    DISCOURAGED = "discouraged"
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    NEUTRAL = "neutral"

class MoodCategory(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class LearningEmotionalProfile(str, Enum):
    RESILIENT_LEARNER = "resilient_learner"
    ANXIOUS_PERFECTIONIST = "anxious_perfectionist"
    CONFIDENT_EXPLORER = "confident_explorer"
    SENSITIVE_ACHIEVER = "sensitive_achiever"
    STEADY_PERFORMER = "steady_performer"
    VOLATILE_TALENT = "volatile_talent"

class EmotionalSupportType(str, Enum):
    ENCOURAGEMENT = "encouragement"
    REASSURANCE = "reassurance"
    CELEBRATION = "celebration"
    MOTIVATION = "motivation"
    STRESS_RELIEF = "stress_relief"
    CONFIDENCE_BUILDING = "confidence_building"
    PATIENCE_SUPPORT = "patience_support"

class EmotionEngine:
    def __init__(self):
        """Initialize the Enhanced Emotional Intelligence Analysis Engine"""
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable is required")
        
        db_name = os.environ.get('DB_NAME', 'idfs_pathwayiq_database')
        
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        
        # Collections for emotional intelligence
        self.users_collection = self.db.users
        self.emotional_states_collection = self.db.emotional_states
        self.emotional_profiles_collection = self.db.emotional_profiles
        self.ai_interactions_collection = self.db.ai_interactions
        self.emotional_interventions_collection = self.db.emotional_interventions
        self.mood_tracking_collection = self.db.mood_tracking
        
        # Emotional keyword patterns
        self.emotion_patterns = self._load_emotion_patterns()
        
        logger.info("Enhanced Emotional Intelligence Analysis Engine initialized successfully")

    def analyze_emotional_state(self, user_id: str, text_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze emotional state from text input (chat, speech transcription, etc.)"""
        try:
            # Detect primary emotions
            detected_emotions = self._detect_emotions_from_text(text_input)
            
            # Analyze sentiment and intensity
            sentiment_analysis = self._analyze_sentiment(text_input)
            
            # Get context-aware analysis
            contextual_factors = self._analyze_contextual_factors(context or {})
            
            # Get user's emotional history for pattern analysis
            emotional_history = self._get_user_emotional_history(user_id, days=30)
            
            # Determine primary emotional state
            primary_emotion = self._determine_primary_emotion(
                detected_emotions, sentiment_analysis, contextual_factors
            )
            
            emotional_analysis = {
                "user_id": user_id,
                "analysis_id": str(uuid.uuid4()),
                "text_analyzed": text_input,
                "primary_emotion": primary_emotion,
                "detected_emotions": detected_emotions,
                "sentiment_analysis": sentiment_analysis,
                "emotional_intensity": self._calculate_emotional_intensity(detected_emotions, sentiment_analysis),
                "mood_category": self._categorize_mood(primary_emotion, sentiment_analysis),
                "contextual_factors": contextual_factors,
                "emotional_indicators": {
                    "stress_level": self._assess_stress_level(detected_emotions, sentiment_analysis),
                    "confidence_level": self._assess_confidence_level(detected_emotions, text_input),
                    "motivation_level": self._assess_motivation_level(detected_emotions, text_input),
                    "engagement_level": self._assess_engagement_level(detected_emotions, contextual_factors),
                    "frustration_markers": self._detect_frustration_markers(text_input)
                },
                "pattern_analysis": {
                    "compared_to_baseline": self._compare_to_baseline(user_id, primary_emotion),
                    "recent_trend": self._analyze_recent_emotional_trend(emotional_history),
                    "emotional_stability": self._assess_emotional_stability(emotional_history)
                },
                "learning_impact": {
                    "predicted_performance_impact": self._predict_performance_impact(primary_emotion),
                    "attention_forecast": self._forecast_attention_level(primary_emotion),
                    "retention_likelihood": self._estimate_retention_impact(primary_emotion)
                },
                "timestamp": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=6)  # Emotional states change relatively quickly
            }

            # Store emotional state for tracking
            self._store_emotional_state(user_id, emotional_analysis)

            # Generate personalized response recommendations
            emotional_analysis["ai_response_recommendations"] = self._generate_ai_response_recommendations(
                primary_emotion, emotional_analysis["emotional_indicators"]
            )

            # Check if intervention is needed
            intervention_needed = self._assess_intervention_need(emotional_analysis)
            if intervention_needed:
                emotional_analysis["intervention_recommendations"] = self._generate_intervention_recommendations(
                    user_id, emotional_analysis
                )

            return {
                "success": True,
                "emotional_analysis": emotional_analysis
            }

        except Exception as e:
            logger.error(f"Error analyzing emotional state: {str(e)}")
            return {"error": "Failed to analyze emotional state"}

    def generate_empathetic_response(self, user_id: str, user_message: str, emotional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate empathetic AI response based on user's emotional state"""
        try:
            # Analyze current emotional state if not provided
            if not emotional_context:
                emotional_analysis = self.analyze_emotional_state(user_id, user_message)
                if "error" in emotional_analysis:
                    return emotional_analysis
                emotional_context = emotional_analysis["emotional_analysis"]

            # Get user's learning and emotional profile
            user_profile = self._get_user_emotional_profile(user_id)
            
            # Generate contextually appropriate response
            empathetic_response = {
                "response_id": str(uuid.uuid4()),
                "user_id": user_id,
                "primary_emotion_detected": emotional_context.get("primary_emotion", EmotionalState.NEUTRAL),
                "response_strategy": self._select_response_strategy(emotional_context, user_profile),
                "empathetic_elements": {
                    "emotional_acknowledgment": self._generate_emotional_acknowledgment(emotional_context),
                    "supportive_language": self._select_supportive_language(emotional_context),
                    "encouragement_level": self._determine_encouragement_level(emotional_context),
                    "personalization_elements": self._add_personalization_elements(user_id, user_profile)
                },
                "response_content": {
                    "main_message": self._generate_main_response(user_message, emotional_context, user_profile),
                    "emotional_support": self._generate_emotional_support(emotional_context),
                    "learning_guidance": self._generate_learning_guidance(emotional_context, user_profile),
                    "next_steps": self._suggest_next_steps(emotional_context, user_profile)
                },
                "adaptation_factors": {
                    "tone_adjustment": self._adjust_tone_for_emotion(emotional_context["primary_emotion"]),
                    "complexity_level": self._adjust_complexity_for_state(emotional_context),
                    "pacing_recommendation": self._recommend_pacing(emotional_context),
                    "interaction_style": self._adapt_interaction_style(user_profile)
                },
                "follow_up_recommendations": {
                    "check_in_timing": self._recommend_check_in_timing(emotional_context),
                    "emotional_support_resources": self._recommend_support_resources(emotional_context),
                    "learning_adjustments": self._recommend_learning_adjustments(emotional_context)
                },
                "generated_at": datetime.now()
            }

            # Log the interaction for learning and improvement
            self._log_ai_interaction(user_id, user_message, empathetic_response)

            return {
                "success": True,
                "empathetic_response": empathetic_response
            }

        except Exception as e:
            logger.error(f"Error generating empathetic response: {str(e)}")
            return {"error": "Failed to generate empathetic response"}

    def track_emotional_journey(self, user_id: str, time_period: int = 30) -> Dict[str, Any]:
        """Track and analyze user's emotional journey over time"""
        try:
            # Get emotional states over time period
            cutoff_date = datetime.now() - timedelta(days=time_period)
            emotional_states = list(self.emotional_states_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_date}
            }).sort("timestamp", 1))

            if not emotional_states:
                return {"error": "No emotional data available for this time period"}

            # Analyze emotional journey
            emotional_journey = {
                "user_id": user_id,
                "analysis_period_days": time_period,
                "total_interactions": len(emotional_states),
                "emotional_timeline": self._create_emotional_timeline(emotional_states),
                "pattern_analysis": {
                    "most_frequent_emotions": self._analyze_frequent_emotions(emotional_states),
                    "emotional_volatility": self._calculate_emotional_volatility(emotional_states),
                    "positive_negative_ratio": self._calculate_sentiment_ratio(emotional_states),
                    "stress_patterns": self._identify_stress_patterns(emotional_states),
                    "confidence_trends": self._analyze_confidence_trends(emotional_states)
                },
                "learning_correlations": {
                    "emotion_performance_correlation": self._correlate_emotion_performance(user_id, emotional_states),
                    "mood_engagement_patterns": self._analyze_mood_engagement_patterns(user_id, emotional_states),
                    "emotional_learning_efficiency": self._assess_emotional_learning_efficiency(user_id, emotional_states)
                },
                "growth_indicators": {
                    "emotional_resilience_development": self._assess_resilience_development(emotional_states),
                    "stress_management_improvement": self._assess_stress_management_improvement(emotional_states),
                    "confidence_building_progress": self._assess_confidence_building_progress(emotional_states)
                },
                "personalized_insights": {
                    "emotional_strengths": self._identify_emotional_strengths(emotional_states),
                    "areas_for_emotional_development": self._identify_emotional_development_areas(emotional_states),
                    "optimal_learning_conditions": self._identify_optimal_learning_conditions(user_id, emotional_states),
                    "emotional_triggers": self._identify_emotional_triggers(emotional_states)
                },
                "recommendations": {
                    "emotional_intelligence_activities": self._recommend_ei_activities(emotional_states),
                    "stress_management_techniques": self._recommend_stress_management(emotional_states),
                    "confidence_building_strategies": self._recommend_confidence_strategies(emotional_states),
                    "learning_environment_optimizations": self._recommend_environment_optimizations(emotional_states)
                },
                "generated_at": datetime.now()
            }

            return {
                "success": True,
                "emotional_journey": emotional_journey
            }

        except Exception as e:
            logger.error(f"Error tracking emotional journey: {str(e)}")
            return {"error": "Failed to track emotional journey"}

    def create_emotional_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """Create comprehensive emotional learning profile for a user"""
        try:
            # Get comprehensive user data
            user = self.users_collection.find_one({"id": user_id})
            if not user:
                return {"error": "User not found"}

            # Get emotional history
            emotional_states = list(self.emotional_states_collection.find({"user_id": user_id}))
            ai_interactions = list(self.ai_interactions_collection.find({"user_id": user_id}))

            # Create emotional learning profile
            emotional_profile = {
                "user_id": user_id,
                "profile_id": str(uuid.uuid4()),
                "profile_type": self._determine_emotional_learning_type(emotional_states),
                "emotional_characteristics": {
                    "dominant_emotions": self._identify_dominant_emotions(emotional_states),
                    "emotional_range": self._calculate_emotional_range(emotional_states),
                    "emotional_stability_score": self._calculate_stability_score(emotional_states),
                    "stress_tolerance": self._assess_stress_tolerance(emotional_states),
                    "resilience_level": self._assess_resilience_level(emotional_states)
                },
                "learning_preferences": {
                    "optimal_emotional_states": self._identify_optimal_states_for_learning(user_id, emotional_states),
                    "preferred_support_types": self._identify_preferred_support(ai_interactions),
                    "feedback_sensitivity": self._assess_feedback_sensitivity(emotional_states),
                    "motivation_drivers": self._identify_motivation_drivers(emotional_states, ai_interactions),
                    "challenge_tolerance": self._assess_challenge_tolerance(emotional_states)
                },
                "emotional_intelligence_metrics": {
                    "self_awareness_score": self._calculate_self_awareness_score(ai_interactions),
                    "emotional_regulation_score": self._calculate_regulation_score(emotional_states),
                    "empathy_indicators": self._assess_empathy_indicators(ai_interactions),
                    "social_skills_assessment": self._assess_social_skills(user_id),
                    "overall_ei_score": 0.0  # Will be calculated from components
                },
                "personalization_recommendations": {
                    "ai_interaction_style": self._recommend_ai_interaction_style(emotional_states, ai_interactions),
                    "content_delivery_preferences": self._recommend_content_delivery(emotional_states),
                    "feedback_approach": self._recommend_feedback_approach(emotional_states),
                    "support_timing": self._recommend_support_timing(emotional_states),
                    "learning_environment_setup": self._recommend_learning_environment(emotional_states)
                },
                "development_plan": {
                    "emotional_growth_goals": self._set_emotional_growth_goals(emotional_states),
                    "skill_development_priorities": self._prioritize_skill_development(emotional_states),
                    "intervention_strategies": self._design_intervention_strategies(emotional_states),
                    "progress_milestones": self._define_progress_milestones(emotional_states)
                },
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "next_review_date": datetime.now() + timedelta(days=30)
            }

            # Calculate overall EI score
            ei_components = emotional_profile["emotional_intelligence_metrics"]
            emotional_profile["emotional_intelligence_metrics"]["overall_ei_score"] = statistics.mean([
                ei_components["self_awareness_score"],
                ei_components["emotional_regulation_score"],
                ei_components["empathy_indicators"],
                ei_components["social_skills_assessment"]
            ])

            # Store emotional profile
            self._store_emotional_profile(user_id, emotional_profile)

            return {
                "success": True,
                "emotional_learning_profile": emotional_profile
            }

        except Exception as e:
            logger.error(f"Error creating emotional learning profile: {str(e)}")
            return {"error": "Failed to create emotional learning profile"}

    def provide_emotional_intervention(self, user_id: str, intervention_type: EmotionalSupportType, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide targeted emotional intervention and support"""
        try:
            # Get user's current emotional state and profile
            user_profile = self._get_user_emotional_profile(user_id)
            recent_emotional_state = self._get_recent_emotional_state(user_id)

            # Design intervention based on type and context
            intervention = {
                "intervention_id": str(uuid.uuid4()),
                "user_id": user_id,
                "intervention_type": intervention_type,
                "context": context or {},
                "intervention_content": self._design_intervention_content(intervention_type, user_profile, recent_emotional_state),
                "delivery_strategy": {
                    "timing": self._optimize_intervention_timing(user_profile, recent_emotional_state),
                    "duration": self._determine_intervention_duration(intervention_type),
                    "intensity": self._adjust_intervention_intensity(user_profile, recent_emotional_state),
                    "personalization_level": self._set_personalization_level(user_profile)
                },
                "expected_outcomes": {
                    "primary_goal": self._define_primary_intervention_goal(intervention_type),
                    "success_metrics": self._define_success_metrics(intervention_type),
                    "timeline_expectations": self._set_timeline_expectations(intervention_type, user_profile)
                },
                "follow_up_plan": {
                    "check_in_schedule": self._create_check_in_schedule(intervention_type),
                    "progress_monitoring": self._design_progress_monitoring(intervention_type),
                    "adjustment_triggers": self._define_adjustment_triggers(intervention_type, user_profile)
                },
                "resources_provided": {
                    "techniques": self._provide_coping_techniques(intervention_type, user_profile),
                    "exercises": self._suggest_emotional_exercises(intervention_type),
                    "learning_materials": self._recommend_learning_materials(intervention_type),
                    "support_contacts": self._provide_support_contacts(intervention_type)
                },
                "implemented_at": datetime.now()
            }

            # Log intervention for tracking effectiveness
            self._log_emotional_intervention(user_id, intervention)

            return {
                "success": True,
                "emotional_intervention": intervention
            }

        except Exception as e:
            logger.error(f"Error providing emotional intervention: {str(e)}")
            return {"error": "Failed to provide emotional intervention"}

    # Helper methods for emotional analysis
    def _load_emotion_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load emotion detection patterns"""
        return {
            "confidence": {
                "positive": ["confident", "sure", "certain", "know I can", "got this", "ready", "prepared"],
                "negative": ["not sure", "uncertain", "doubt", "worried", "scared", "don't know if"]
            },
            "frustration": {
                "indicators": ["frustrated", "annoyed", "stuck", "can't figure", "doesn't make sense", 
                             "giving up", "too hard", "impossible", "why won't", "stupid"]
            },
            "excitement": {
                "indicators": ["excited", "love this", "amazing", "awesome", "cool", "interesting", 
                             "want to learn", "can't wait", "fun", "enjoying"]
            },
            "anxiety": {
                "indicators": ["nervous", "anxious", "worried", "stressed", "overwhelmed", "scared", 
                             "pressure", "afraid", "panic", "tense"]
            },
            "motivation": {
                "positive": ["motivated", "determined", "going to", "will", "committed", "focused"],
                "negative": ["unmotivated", "don't want", "bored", "tired", "lazy", "pointless"]
            }
        }

    def _detect_emotions_from_text(self, text: str) -> Dict[str, float]:
        """Detect emotions from text using pattern matching"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            if isinstance(patterns, dict):
                if "positive" in patterns and "negative" in patterns:
                    # Handle bidirectional emotions (like confidence)
                    positive_matches = sum(1 for pattern in patterns["positive"] if pattern in text_lower)
                    negative_matches = sum(1 for pattern in patterns["negative"] if pattern in text_lower)
                    emotion_scores[emotion] = max(0, positive_matches - negative_matches) / max(len(text.split()), 1)
                else:
                    # Handle unidirectional emotions
                    matches = sum(1 for pattern_list in patterns.values() for pattern in pattern_list if pattern in text_lower)
                    emotion_scores[emotion] = matches / max(len(text.split()), 1)
            else:
                # Handle simple pattern lists
                matches = sum(1 for pattern in patterns if pattern in text_lower)
                emotion_scores[emotion] = matches / max(len(text.split()), 1)
        
        return emotion_scores

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        # Simplified sentiment analysis
        positive_words = ["good", "great", "love", "like", "enjoy", "happy", "easy", "clear", "understand"]
        negative_words = ["bad", "hate", "dislike", "hard", "difficult", "confusing", "frustrated", "angry"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            polarity = "positive"
            intensity = min(1.0, (positive_count - negative_count) / max(len(text.split()), 1))
        elif negative_count > positive_count:
            polarity = "negative"
            intensity = min(1.0, (negative_count - positive_count) / max(len(text.split()), 1))
        else:
            polarity = "neutral"
            intensity = 0.0
        
        return {
            "polarity": polarity,
            "intensity": intensity,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }

    def _analyze_contextual_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contextual factors that might influence emotion"""
        return {
            "assessment_performance": context.get("recent_performance", None),
            "time_of_day": context.get("time_of_day", None),
            "session_length": context.get("session_length", None),
            "difficulty_level": context.get("difficulty_level", None),
            "previous_interactions": context.get("previous_interactions", [])
        }

    def _determine_primary_emotion(self, detected_emotions: Dict[str, float], sentiment: Dict[str, Any], context: Dict[str, Any]) -> EmotionalState:
        """Determine the primary emotional state"""
        # Find the emotion with highest score
        if not detected_emotions:
            return EmotionalState.NEUTRAL
        
        primary_emotion_key = max(detected_emotions, key=detected_emotions.get)
        
        # Map detected emotion keys to EmotionalState enum
        emotion_mapping = {
            "confidence": EmotionalState.CONFIDENT,
            "frustration": EmotionalState.FRUSTRATED,
            "excitement": EmotionalState.EXCITED,
            "anxiety": EmotionalState.ANXIOUS,
            "motivation": EmotionalState.MOTIVATED
        }
        
        return emotion_mapping.get(primary_emotion_key, EmotionalState.NEUTRAL)

    def _calculate_emotional_intensity(self, emotions: Dict[str, float], sentiment: Dict[str, Any]) -> float:
        """Calculate overall emotional intensity"""
        emotion_intensity = max(emotions.values()) if emotions else 0.0
        sentiment_intensity = sentiment.get("intensity", 0.0)
        return (emotion_intensity + sentiment_intensity) / 2

    def _categorize_mood(self, primary_emotion: EmotionalState, sentiment: Dict[str, Any]) -> MoodCategory:
        """Categorize overall mood"""
        positive_emotions = {EmotionalState.CONFIDENT, EmotionalState.EXCITED, EmotionalState.MOTIVATED, EmotionalState.CURIOUS}
        negative_emotions = {EmotionalState.FRUSTRATED, EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED, EmotionalState.DISCOURAGED}
        
        if primary_emotion in positive_emotions and sentiment.get("polarity") == "positive":
            return MoodCategory.POSITIVE
        elif primary_emotion in negative_emotions and sentiment.get("polarity") == "negative":
            return MoodCategory.NEGATIVE
        elif sentiment.get("polarity") == "neutral" and primary_emotion == EmotionalState.NEUTRAL:
            return MoodCategory.NEUTRAL
        else:
            return MoodCategory.MIXED

    # Additional helper methods with simplified implementations
    def _assess_stress_level(self, emotions: Dict[str, float], sentiment: Dict[str, Any]) -> float:
        """Assess stress level (0-1 scale)"""
        stress_indicators = emotions.get("anxiety", 0) + emotions.get("frustration", 0)
        return min(1.0, stress_indicators * 2)

    def _assess_confidence_level(self, emotions: Dict[str, float], text: str) -> float:
        """Assess confidence level (0-1 scale)"""
        return min(1.0, emotions.get("confidence", 0) * 2)

    def _assess_motivation_level(self, emotions: Dict[str, float], text: str) -> float:
        """Assess motivation level (0-1 scale)"""
        return min(1.0, emotions.get("motivation", 0) * 2)

    def _assess_engagement_level(self, emotions: Dict[str, float], context: Dict[str, Any]) -> float:
        """Assess engagement level"""
        engagement_score = emotions.get("excitement", 0) + emotions.get("curiosity", 0)
        return min(1.0, engagement_score)

    def _detect_frustration_markers(self, text: str) -> List[str]:
        """Detect specific frustration markers in text"""
        frustration_patterns = self.emotion_patterns.get("frustration", {}).get("indicators", [])
        detected_markers = [pattern for pattern in frustration_patterns if pattern in text.lower()]
        return detected_markers

    def _get_user_emotional_history(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get user's emotional history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return list(self.emotional_states_collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff_date}
        }).sort("timestamp", -1))

    def _store_emotional_state(self, user_id: str, emotional_analysis: Dict[str, Any]):
        """Store emotional state analysis"""
        try:
            emotional_state_doc = {
                "user_id": user_id,
                "analysis_id": emotional_analysis["analysis_id"],
                "primary_emotion": emotional_analysis["primary_emotion"],
                "mood_category": emotional_analysis["mood_category"],
                "emotional_intensity": emotional_analysis["emotional_intensity"],
                "stress_level": emotional_analysis["emotional_indicators"]["stress_level"],
                "confidence_level": emotional_analysis["emotional_indicators"]["confidence_level"],
                "timestamp": emotional_analysis["timestamp"],
                "raw_analysis": emotional_analysis
            }
            
            self.emotional_states_collection.insert_one(emotional_state_doc)
            
        except Exception as e:
            logger.error(f"Error storing emotional state: {str(e)}")

    def _generate_ai_response_recommendations(self, primary_emotion: EmotionalState, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response recommendations based on emotional state"""
        recommendations = {
            "tone": "neutral",
            "empathy_level": "medium",
            "encouragement": "moderate",
            "specific_strategies": []
        }
        
        if primary_emotion == EmotionalState.FRUSTRATED:
            recommendations.update({
                "tone": "patient_and_understanding",
                "empathy_level": "high",
                "encouragement": "gentle",
                "specific_strategies": ["break_down_problem", "offer_alternative_approach", "validate_feelings"]
            })
        elif primary_emotion == EmotionalState.CONFIDENT:
            recommendations.update({
                "tone": "supportive_and_challenging",
                "empathy_level": "medium",
                "encouragement": "motivational",
                "specific_strategies": ["provide_advanced_challenge", "celebrate_progress", "set_higher_goals"]
            })
        elif primary_emotion == EmotionalState.ANXIOUS:
            recommendations.update({
                "tone": "calm_and_reassuring",
                "empathy_level": "high",
                "encouragement": "confidence_building",
                "specific_strategies": ["provide_reassurance", "break_into_small_steps", "emphasize_previous_successes"]
            })
        
        return recommendations

    def _assess_intervention_need(self, emotional_analysis: Dict[str, Any]) -> bool:
        """Assess if emotional intervention is needed"""
        stress_level = emotional_analysis["emotional_indicators"]["stress_level"]
        primary_emotion = emotional_analysis["primary_emotion"]
        
        # Intervention needed for high stress or negative emotional states
        return (stress_level > 0.7 or 
                primary_emotion in [EmotionalState.OVERWHELMED, EmotionalState.DISCOURAGED] or
                emotional_analysis["emotional_intensity"] > 0.8)

    def _generate_intervention_recommendations(self, user_id: str, emotional_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate intervention recommendations"""
        return [
            {
                "type": "immediate_support",
                "title": "Take a Break",
                "description": "Consider taking a 5-10 minute break to reset your emotional state",
                "urgency": "high"
            },
            {
                "type": "learning_adjustment",
                "title": "Adjust Learning Approach",
                "description": "Let's try a different learning method that might be less stressful",
                "urgency": "medium"
            }
        ]

    # Simplified implementations for remaining methods
    def _get_user_emotional_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user's emotional profile"""
        profile = self.emotional_profiles_collection.find_one({"user_id": user_id})
        return profile if profile else {"profile_type": LearningEmotionalProfile.STEADY_PERFORMER}

    def _compare_to_baseline(self, user_id: str, current_emotion: EmotionalState) -> str:
        """Compare current emotion to user's baseline"""
        return "within_normal_range"  # Simplified

    def _analyze_recent_emotional_trend(self, emotional_history: List[Dict]) -> str:
        """Analyze recent emotional trend"""
        return "stable"  # Simplified

    def _assess_emotional_stability(self, emotional_history: List[Dict]) -> float:
        """Assess emotional stability score"""
        return 0.7  # Simplified

    def _predict_performance_impact(self, emotion: EmotionalState) -> str:
        """Predict how emotion will impact performance"""
        positive_emotions = {EmotionalState.CONFIDENT, EmotionalState.MOTIVATED, EmotionalState.FOCUSED}
        return "positive" if emotion in positive_emotions else "neutral"

    def _forecast_attention_level(self, emotion: EmotionalState) -> str:
        """Forecast attention level based on emotion"""
        focused_emotions = {EmotionalState.FOCUSED, EmotionalState.CURIOUS, EmotionalState.MOTIVATED}
        return "high" if emotion in focused_emotions else "moderate"

    def _estimate_retention_impact(self, emotion: EmotionalState) -> str:
        """Estimate retention impact"""
        return "positive" if emotion in {EmotionalState.EXCITED, EmotionalState.CURIOUS} else "neutral"

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Enhanced Emotional Intelligence Analysis Engine database connection closed")