"""
Enhanced Emotional Intelligence Analysis System
Advanced AI-powered personalization and emotional state analysis
"""
import os
import uuid
import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from pymongo import MongoClient
import openai
from textblob import TextBlob
import re
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class EmotionalIntelligenceAnalyzer:
    def __init__(self, mongo_url: str, openai_api_key: str):
        self.client = MongoClient(mongo_url)
        db_name = os.getenv('DB_NAME', 'idfs_pathwayiq_database')
        self.db = self.client[db_name]
        
        # Initialize OpenAI
        from openai import AsyncOpenAI
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        
        # Collections
        self.users_collection = self.db.users
        self.assessments_collection = self.db.assessments
        self.speech_sessions_collection = self.db.speech_sessions
        self.messages_collection = self.db.group_messages
        self.emotional_profiles_collection = self.db.emotional_profiles
        self.learning_recommendations_collection = self.db.learning_recommendations
        
        # Emotional categories
        self.emotion_categories = {
            "confidence": ["confident", "sure", "certain", "positive", "optimistic"],
            "anxiety": ["nervous", "worried", "anxious", "stressed", "uncertain"],
            "frustration": ["frustrated", "annoyed", "confused", "stuck", "difficult"],
            "engagement": ["interested", "excited", "curious", "motivated", "focused"],
            "satisfaction": ["happy", "pleased", "satisfied", "accomplished", "proud"],
            "fatigue": ["tired", "exhausted", "bored", "unmotivated", "lazy"]
        }
        
        # Learning style indicators
        self.learning_style_indicators = {
            "visual": ["see", "look", "picture", "diagram", "chart", "visual"],
            "auditory": ["hear", "listen", "sound", "explain", "discuss", "talk"],
            "kinesthetic": ["do", "practice", "hands-on", "try", "experiment", "move"],
            "reading": ["read", "write", "text", "notes", "study", "research"]
        }
        
        # Cognitive load indicators
        self.cognitive_load_patterns = {
            "low": ["easy", "simple", "clear", "obvious", "straightforward"],
            "medium": ["thinking", "considering", "working", "processing"],
            "high": ["complex", "difficult", "overwhelming", "confused", "struggling"],
            "overload": ["too much", "can't", "impossible", "giving up", "lost"]
        }
    
    # EMOTIONAL ANALYSIS
    async def analyze_emotional_state(
        self,
        user_id: str,
        text_input: str,
        context: str = "general",
        source: str = "assessment"
    ) -> Dict[str, Any]:
        """Analyze emotional state from text input"""
        try:
            # Basic sentiment analysis
            blob = TextBlob(text_input)
            sentiment_polarity = blob.sentiment.polarity
            sentiment_subjectivity = blob.sentiment.subjectivity
            
            # Emotion classification using keywords
            emotions = self._classify_emotions_from_text(text_input)
            
            # Learning style detection
            learning_style = self._detect_learning_style(text_input)
            
            # Cognitive load assessment
            cognitive_load = self._assess_cognitive_load(text_input)
            
            # Advanced AI analysis using OpenAI
            ai_analysis = await self._get_ai_emotional_analysis(text_input, context)
            
            # Compile comprehensive analysis
            emotional_state = {
                "analysis_id": str(uuid.uuid4()),
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "source": source,
                "context": context,
                "raw_text": text_input,
                
                # Basic sentiment
                "sentiment": {
                    "polarity": round(sentiment_polarity, 3),  # -1 to 1
                    "subjectivity": round(sentiment_subjectivity, 3),  # 0 to 1
                    "classification": self._classify_sentiment(sentiment_polarity)
                },
                
                # Emotional categories
                "emotions": emotions,
                "dominant_emotion": max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral",
                
                # Learning insights
                "learning_style_indicators": learning_style,
                "cognitive_load": cognitive_load,
                
                # AI-powered analysis
                "ai_insights": ai_analysis,
                
                # Confidence scores
                "confidence_scores": {
                    "sentiment": min(1.0, abs(sentiment_polarity) + sentiment_subjectivity),
                    "emotion": max(emotions.values()) if emotions else 0.1,
                    "learning_style": max(learning_style.values()) if learning_style else 0.1,
                    "overall": self._calculate_overall_confidence(emotions, learning_style, sentiment_polarity)
                }
            }
            
            # Store analysis
            self.emotional_profiles_collection.insert_one(emotional_state)
            
            return {
                "success": True,
                "emotional_analysis": emotional_state
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotional state: {e}")
            return {"error": str(e)}
    
    async def get_user_emotional_profile(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive emotional profile for a user"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get recent emotional analyses
            analyses = list(
                self.emotional_profiles_collection
                .find({
                    "user_id": user_id,
                    "timestamp": {"$gte": since_date}
                })
                .sort("timestamp", -1)
            )
            
            if not analyses:
                return {
                    "user_id": user_id,
                    "profile": "No emotional data available",
                    "recommendations": ["Take more assessments to build emotional profile"]
                }
            
            # Aggregate emotional patterns
            emotional_trends = self._analyze_emotional_trends(analyses)
            
            # Detect learning preferences
            learning_preferences = self._aggregate_learning_preferences(analyses)
            
            # Identify stress patterns
            stress_patterns = self._identify_stress_patterns(analyses)
            
            # Generate personalized recommendations
            recommendations = await self._generate_personalized_recommendations(
                user_id, emotional_trends, learning_preferences, stress_patterns
            )
            
            # Calculate emotional intelligence metrics
            ei_metrics = self._calculate_emotional_intelligence_metrics(analyses)
            
            profile = {
                "user_id": user_id,
                "profile_generated_at": datetime.utcnow().isoformat(),
                "analysis_period_days": days,
                "total_analyses": len(analyses),
                
                # Emotional patterns
                "emotional_trends": emotional_trends,
                "dominant_emotions": self._get_dominant_emotions(analyses),
                "emotional_stability": self._calculate_emotional_stability(analyses),
                
                # Learning insights
                "learning_preferences": learning_preferences,
                "preferred_learning_style": max(learning_preferences.items(), key=lambda x: x[1])[0] if learning_preferences else "balanced",
                
                # Stress and cognitive load
                "stress_patterns": stress_patterns,
                "cognitive_load_tendency": self._get_cognitive_load_tendency(analyses),
                
                # Emotional intelligence metrics
                "emotional_intelligence": ei_metrics,
                
                # Personalized recommendations
                "recommendations": recommendations,
                
                # Performance correlations
                "emotion_performance_correlation": await self._correlate_emotions_with_performance(user_id, analyses)
            }
            
            return {
                "success": True,
                "profile": profile
            }
            
        except Exception as e:
            logger.error(f"Error getting user emotional profile: {e}")
            return {"error": str(e)}
    
    # HELPER METHODS (abbreviated due to length - full implementation would include all helper methods)
    def _classify_emotions_from_text(self, text: str) -> Dict[str, float]:
        """Classify emotions based on keyword analysis"""
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in self.emotion_categories.items():
            score = 0
            for keyword in keywords:
                occurrences = len(re.findall(rf'\b{keyword}\b', text_lower))
                score += occurrences
            
            if len(text_lower.split()) > 0:
                emotions[emotion] = score / len(text_lower.split())
            else:
                emotions[emotion] = 0
        
        return emotions
    
    def _detect_learning_style(self, text: str) -> Dict[str, float]:
        """Detect learning style preferences from text"""
        text_lower = text.lower()
        learning_styles = {}
        
        for style, indicators in self.learning_style_indicators.items():
            score = 0
            for indicator in indicators:
                occurrences = len(re.findall(rf'\b{indicator}\b', text_lower))
                score += occurrences
            
            if len(text_lower.split()) > 0:
                learning_styles[style] = score / len(text_lower.split())
            else:
                learning_styles[style] = 0
        
        return learning_styles
    
    def _assess_cognitive_load(self, text: str) -> Dict[str, Any]:
        """Assess cognitive load from text indicators"""
        text_lower = text.lower()
        load_scores = {}
        
        for load_level, patterns in self.cognitive_load_patterns.items():
            score = 0
            for pattern in patterns:
                occurrences = len(re.findall(rf'{pattern}', text_lower))
                score += occurrences
            load_scores[load_level] = score
        
        dominant_load = max(load_scores.items(), key=lambda x: x[1])[0] if load_scores else "medium"
        
        return {
            "level": dominant_load,
            "scores": load_scores,
            "complexity_indicators": len(re.findall(r'[,;:]', text)),
            "uncertainty_markers": len(re.findall(r'\b(maybe|perhaps|might|could|unsure)\b', text_lower))
        }
    
    async def _get_ai_emotional_analysis(self, text: str, context: str) -> Dict[str, Any]:
        """Get advanced emotional analysis using OpenAI"""
        try:
            prompt = f"""
            Analyze the emotional state and learning psychology of a student based on their response during a {context}.
            
            Student response: "{text}"
            
            Please provide analysis in the following JSON format:
            {{
                "emotional_state": "primary emotion detected",
                "confidence_level": "high/medium/low assessment confidence",
                "learning_engagement": "engaged/neutral/disengaged",
                "stress_indicators": ["list", "of", "stress", "signs"],
                "motivation_level": "high/medium/low",
                "comprehension_indicators": "understanding level observed",
                "recommended_support": ["specific", "recommendations"],
                "personality_insights": "brief personality observations"
            }}
            
            Focus on educational psychology and learning context. Be supportive and constructive.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an educational psychologist specializing in student emotional intelligence and learning analytics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            try:
                ai_analysis = json.loads(content)
            except json.JSONDecodeError:
                ai_analysis = {
                    "emotional_state": "neutral",
                    "confidence_level": "low",
                    "learning_engagement": "neutral",
                    "raw_response": content
                }
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"Error getting AI emotional analysis: {e}")
            return {
                "emotional_state": "unknown",
                "confidence_level": "low",
                "error": "AI analysis unavailable"
            }
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment polarity into categories"""
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_overall_confidence(
        self, 
        emotions: Dict[str, float], 
        learning_style: Dict[str, float], 
        sentiment_polarity: float
    ) -> float:
        """Calculate overall confidence in the analysis"""
        emotion_confidence = max(emotions.values()) if emotions else 0.1
        style_confidence = max(learning_style.values()) if learning_style else 0.1
        sentiment_confidence = abs(sentiment_polarity)
        
        return min(1.0, (emotion_confidence + style_confidence + sentiment_confidence) / 3)
    
    def _analyze_emotional_trends(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Analyze emotional trends from multiple analyses"""
        emotion_timeline = []
        sentiment_timeline = []
        
        for analysis in analyses:
            emotion_timeline.append({
                "timestamp": analysis["timestamp"].isoformat(),
                "emotion": analysis.get("dominant_emotion", "neutral"),
                "intensity": max(analysis.get("emotions", {}).values()) if analysis.get("emotions") else 0
            })
            
            sentiment_timeline.append({
                "timestamp": analysis["timestamp"].isoformat(),
                "polarity": analysis.get("sentiment", {}).get("polarity", 0)
            })
        
        return {
            "emotion_timeline": emotion_timeline,
            "sentiment_timeline": sentiment_timeline,
            "volatility": self._calculate_emotional_volatility(analyses)
        }
    
    def _aggregate_learning_preferences(self, analyses: List[Dict]) -> Dict[str, float]:
        """Aggregate learning style preferences"""
        style_totals = defaultdict(float)
        count = 0
        
        for analysis in analyses:
            style_indicators = analysis.get("learning_style_indicators", {})
            for style, score in style_indicators.items():
                style_totals[style] += score
            count += 1
        
        if count > 0:
            return {style: total / count for style, total in style_totals.items()}
        else:
            return {}
    
    def _identify_stress_patterns(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Identify patterns of stress and anxiety"""
        stress_indicators = []
        
        for analysis in analyses:
            emotions = analysis.get("emotions", {})
            stress_level = emotions.get("anxiety", 0) + emotions.get("frustration", 0)
            
            if stress_level > 0.1:
                stress_indicators.append({
                    "timestamp": analysis["timestamp"].isoformat(),
                    "stress_level": stress_level,
                    "context": analysis.get("context", "unknown")
                })
        
        return {
            "stress_incidents": stress_indicators,
            "stress_frequency": len(stress_indicators) / len(analyses) if analyses else 0
        }
    
    async def _generate_personalized_recommendations(
        self,
        user_id: str,
        emotional_trends: Dict[str, Any],
        learning_preferences: Dict[str, float],
        stress_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        if stress_patterns["stress_frequency"] > 0.3:
            recommendations.append({
                "category": "stress_management",
                "priority": "high",
                "title": "Stress Reduction Strategies",
                "suggestions": [
                    "Practice deep breathing exercises",
                    "Break study sessions into shorter intervals",
                    "Create a calm study environment"
                ]
            })
        
        return recommendations
    
    def _calculate_emotional_intelligence_metrics(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Calculate emotional intelligence metrics"""
        if not analyses:
            return {"overall_score": 0, "components": {}}
        
        # Simplified EI calculation
        emotion_recognition = 0.7  # Placeholder
        self_regulation = 0.6
        motivation_score = 0.8
        social_awareness = 0.5
        
        components = {
            "self_awareness": emotion_recognition,
            "self_regulation": self_regulation,
            "motivation": motivation_score,
            "social_awareness": social_awareness
        }
        
        overall_score = sum(components.values()) / len(components)
        
        return {
            "overall_score": round(overall_score, 2),
            "components": components,
            "level": "medium" if overall_score > 0.6 else "developing"
        }
    
    def _get_dominant_emotions(self, analyses: List[Dict]) -> Dict[str, int]:
        """Get most common emotions"""
        emotion_counter = Counter()
        
        for analysis in analyses:
            dominant_emotion = analysis.get("dominant_emotion", "neutral")
            emotion_counter[dominant_emotion] += 1
        
        return dict(emotion_counter.most_common(5))
    
    def _calculate_emotional_stability(self, analyses: List[Dict]) -> float:
        """Calculate emotional stability score"""
        if len(analyses) < 3:
            return 0.5
        
        sentiment_scores = [
            analysis.get("sentiment", {}).get("polarity", 0) 
            for analysis in analyses
        ]
        
        std_dev = np.std(sentiment_scores) if len(sentiment_scores) > 1 else 0
        stability = max(0, 1 - (std_dev / 2))
        
        return round(stability, 2)
    
    def _get_cognitive_load_tendency(self, analyses: List[Dict]) -> str:
        """Get user's cognitive load tendency"""
        load_levels = [
            analysis.get("cognitive_load", {}).get("level", "medium")
            for analysis in analyses
        ]
        
        load_counter = Counter(load_levels)
        most_common = load_counter.most_common(1)
        
        return most_common[0][0] if most_common else "medium"
    
    async def _correlate_emotions_with_performance(self, user_id: str, analyses: List[Dict]) -> Dict[str, Any]:
        """Correlate emotional states with learning performance"""
        try:
            # Simplified correlation analysis
            return {
                "insights": ["Need more data to analyze emotion-performance correlation"]
            }
        except Exception as e:
            logger.error(f"Error correlating emotions with performance: {e}")
            return {"insights": ["Correlation analysis unavailable"]}
    
    def _calculate_emotional_volatility(self, analyses: List[Dict]) -> float:
        """Calculate emotional volatility"""
        if len(analyses) < 3:
            return 0
        
        emotions = [analysis.get("dominant_emotion", "neutral") for analysis in analyses]
        changes = sum(1 for i in range(1, len(emotions)) if emotions[i] != emotions[i-1])
        
        return changes / (len(emotions) - 1) if len(emotions) > 1 else 0

# Initialize the emotional intelligence analyzer
def get_emotional_intelligence_analyzer(mongo_url: str, openai_api_key: str) -> EmotionalIntelligenceAnalyzer:
    """Get or create emotional intelligence analyzer instance"""
    return EmotionalIntelligenceAnalyzer(mongo_url, openai_api_key)