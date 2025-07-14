"""
Adaptive Assessment Engine for StarGuide SkillScan™
Supports K-PhD+ level adaptive questioning with ML-powered difficulty adjustment
"""

import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

class GradeLevel(str, Enum):
    """Educational grade levels from K through PhD+"""
    KINDERGARTEN = "kindergarten"  # Ages 5-6
    GRADE_1 = "grade_1"           # Ages 6-7
    GRADE_2 = "grade_2"           # Ages 7-8
    GRADE_3 = "grade_3"           # Ages 8-9
    GRADE_4 = "grade_4"           # Ages 9-10
    GRADE_5 = "grade_5"           # Ages 10-11
    GRADE_6 = "grade_6"           # Ages 11-12
    GRADE_7 = "grade_7"           # Ages 12-13
    GRADE_8 = "grade_8"           # Ages 13-14
    GRADE_9 = "grade_9"           # Ages 14-15
    GRADE_10 = "grade_10"         # Ages 15-16
    GRADE_11 = "grade_11"         # Ages 16-17
    GRADE_12 = "grade_12"         # Ages 17-18
    UNDERGRADUATE = "undergraduate"  # Ages 18-22
    GRADUATE = "graduate"            # Ages 22-26
    DOCTORAL = "doctoral"            # Ages 24-30
    POSTDOCTORAL = "postdoctoral"    # Ages 28+
    PROFESSIONAL = "professional"    # Any age, professional development

class QuestionComplexity(str, Enum):
    """Question complexity levels mapped to cognitive load"""
    BASIC = "basic"                    # Simple recall, recognition
    COMPREHENSION = "comprehension"    # Understanding, explanation
    APPLICATION = "application"        # Apply knowledge to new situations
    ANALYSIS = "analysis"              # Break down, examine relationships
    SYNTHESIS = "synthesis"            # Combine elements, create new
    EVALUATION = "evaluation"          # Judge, critique, assess
    RESEARCH = "research"              # Original investigation, innovation

class ThinkAloudType(str, Enum):
    """Types of think-aloud responses"""
    REASONING = "reasoning"           # Explain thought process
    STRATEGY = "strategy"             # Describe approach/method
    CONFIDENCE = "confidence"         # Rate certainty level
    DIFFICULTY = "difficulty"         # Assess question difficulty
    CONNECTIONS = "connections"       # Link to prior knowledge

@dataclass
class AbilityEstimate:
    """Student's estimated ability in a subject/topic"""
    subject: str
    topic: str
    ability_score: float  # 0.0 to 1.0
    confidence_interval: Tuple[float, float]
    num_questions: int
    last_updated: datetime
    grade_level_estimate: GradeLevel

@dataclass
class AdaptiveSession:
    """Tracks an adaptive assessment session"""
    session_id: str
    user_id: str
    subject: str
    start_time: datetime
    current_ability_estimate: float
    questions_asked: List[str]
    responses: List[Dict]
    ai_help_usage: List[Dict]  # Track AI assistance
    think_aloud_responses: List[Dict]
    session_type: str  # "diagnostic", "practice", "challenge"

class AdaptiveEngine:
    """
    Core adaptive assessment engine using Item Response Theory (IRT)
    and Computerized Adaptive Testing (CAT) principles
    """
    
    def __init__(self):
        self.ability_estimates = {}  # user_id -> {subject -> AbilityEstimate}
        self.question_difficulties = {}  # question_id -> difficulty_params
        self.session_data = {}  # session_id -> AdaptiveSession
        
        # Grade level mapping to ability scores
        self.grade_level_mapping = {
            GradeLevel.KINDERGARTEN: (0.0, 0.1),
            GradeLevel.GRADE_1: (0.1, 0.15),
            GradeLevel.GRADE_2: (0.15, 0.2),
            GradeLevel.GRADE_3: (0.2, 0.25),
            GradeLevel.GRADE_4: (0.25, 0.3),
            GradeLevel.GRADE_5: (0.3, 0.35),
            GradeLevel.GRADE_6: (0.35, 0.4),
            GradeLevel.GRADE_7: (0.4, 0.45),
            GradeLevel.GRADE_8: (0.45, 0.5),
            GradeLevel.GRADE_9: (0.5, 0.55),
            GradeLevel.GRADE_10: (0.55, 0.6),
            GradeLevel.GRADE_11: (0.6, 0.65),
            GradeLevel.GRADE_12: (0.65, 0.7),
            GradeLevel.UNDERGRADUATE: (0.7, 0.8),
            GradeLevel.GRADUATE: (0.8, 0.9),
            GradeLevel.DOCTORAL: (0.9, 0.95),
            GradeLevel.POSTDOCTORAL: (0.95, 1.0),
            GradeLevel.PROFESSIONAL: (0.5, 1.0)  # Wide range for professionals
        }
    
    def estimate_initial_ability(self, user_age: Optional[int] = None, 
                                grade_level: Optional[GradeLevel] = None,
                                previous_performance: Optional[Dict] = None) -> float:
        """
        Estimate initial ability level for a new student
        """
        if grade_level:
            min_ability, max_ability = self.grade_level_mapping[grade_level]
            return (min_ability + max_ability) / 2
        
        if user_age:
            # Age-based estimation
            if user_age <= 6:
                return 0.05  # Kindergarten level
            elif user_age <= 18:
                # Linear progression through K-12
                return min(0.05 + (user_age - 6) * 0.055, 0.7)
            elif user_age <= 22:
                return 0.75  # Undergraduate
            elif user_age <= 26:
                return 0.85  # Graduate
            else:
                return 0.9   # Advanced
        
        # Default to middle school level if no info available
        return 0.5
    
    def calculate_question_difficulty(self, question_data: Dict) -> float:
        """
        Calculate question difficulty based on multiple factors
        """
        base_difficulty = {
            "basic": 0.2,
            "comprehension": 0.3,
            "application": 0.5,
            "analysis": 0.7,
            "synthesis": 0.8,
            "evaluation": 0.9,
            "research": 0.95
        }
        
        complexity = question_data.get('complexity', 'application')
        difficulty = base_difficulty.get(complexity, 0.5)
        
        # Adjust based on grade level
        grade_level = question_data.get('grade_level', GradeLevel.GRADE_8)
        if grade_level in self.grade_level_mapping:
            grade_min, grade_max = self.grade_level_mapping[grade_level]
            # Scale difficulty within grade level range
            difficulty = grade_min + (difficulty * (grade_max - grade_min))
        
        # Additional factors
        if question_data.get('requires_prior_knowledge', False):
            difficulty += 0.1
        
        if question_data.get('multi_step', False):
            difficulty += 0.1
        
        if question_data.get('abstract_reasoning', False):
            difficulty += 0.15
        
        return min(max(difficulty, 0.0), 1.0)
    
    def select_next_question(self, session_id: str, available_questions: List[Dict]) -> Optional[Dict]:
        """
        Select the optimal next question using CAT principles
        """
        if session_id not in self.session_data:
            return None
        
        session = self.session_data[session_id]
        current_ability = session.current_ability_estimate
        
        # Calculate information value for each question
        best_question = None
        max_information = 0
        
        for question in available_questions:
            if question['id'] in session.questions_asked:
                continue  # Skip already asked questions
            
            question_difficulty = self.calculate_question_difficulty(question)
            
            # Calculate Fisher Information (simplified IRT)
            information = self._calculate_information(current_ability, question_difficulty)
            
            if information > max_information:
                max_information = information
                best_question = question
        
        return best_question
    
    def _calculate_information(self, ability: float, difficulty: float) -> float:
        """
        Calculate Fisher Information for question selection
        """
        # Simplified 1-parameter logistic model
        prob = 1 / (1 + np.exp(-(ability - difficulty) * 1.7))
        information = prob * (1 - prob)
        return information
    
    def update_ability_estimate(self, session_id: str, question_id: str, 
                              is_correct: bool, response_time: float,
                              think_aloud_data: Optional[Dict] = None) -> float:
        """
        Update ability estimate based on response using Bayesian updating
        """
        if session_id not in self.session_data:
            return 0.5
        
        session = self.session_data[session_id]
        current_ability = session.current_ability_estimate
        
        # Get question difficulty
        question_difficulty = self.question_difficulties.get(question_id, 0.5)
        
        # Bayesian update (simplified)
        if is_correct:
            # Increase ability estimate
            adjustment = 0.1 * (1 - current_ability) * (1 - question_difficulty)
        else:
            # Decrease ability estimate
            adjustment = -0.1 * current_ability * question_difficulty
        
        # Adjust based on response time
        if response_time < 10:  # Very fast response
            adjustment *= 1.2  # More confident in the update
        elif response_time > 60:  # Slow response
            adjustment *= 0.8  # Less confident
        
        # Factor in think-aloud quality
        if think_aloud_data:
            reasoning_quality = self._assess_reasoning_quality(think_aloud_data)
            adjustment *= (0.8 + 0.4 * reasoning_quality)  # 0.8 to 1.2 multiplier
        
        new_ability = max(0.0, min(1.0, current_ability + adjustment))
        session.current_ability_estimate = new_ability
        
        return new_ability
    
    def _assess_reasoning_quality(self, think_aloud_data: Dict) -> float:
        """
        Assess the quality of think-aloud reasoning (0.0 to 1.0)
        """
        reasoning = think_aloud_data.get('reasoning', '').lower()
        
        quality_score = 0.0
        
        # Check for key reasoning indicators
        indicators = [
            'because', 'therefore', 'since', 'due to', 'as a result',
            'first', 'then', 'next', 'finally', 'step',
            'similar', 'different', 'compare', 'contrast',
            'example', 'instance', 'such as', 'like',
            'analyze', 'evaluate', 'consider', 'examine'
        ]
        
        for indicator in indicators:
            if indicator in reasoning:
                quality_score += 0.1
        
        # Length bonus (more detailed reasoning)
        if len(reasoning) > 50:
            quality_score += 0.2
        if len(reasoning) > 100:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def determine_grade_level(self, ability_score: float) -> GradeLevel:
        """
        Determine appropriate grade level based on ability score
        """
        for grade_level, (min_score, max_score) in self.grade_level_mapping.items():
            if min_score <= ability_score <= max_score:
                return grade_level
        
        # Default fallback
        if ability_score < 0.1:
            return GradeLevel.KINDERGARTEN
        elif ability_score > 0.95:
            return GradeLevel.POSTDOCTORAL
        else:
            return GradeLevel.GRADE_8
    
    def start_adaptive_session(self, user_id: str, subject: str, 
                             initial_ability: Optional[float] = None,
                             session_type: str = "diagnostic") -> str:
        """
        Start a new adaptive assessment session
        """
        session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
        
        if initial_ability is None:
            initial_ability = self.estimate_initial_ability()
        
        session = AdaptiveSession(
            session_id=session_id,
            user_id=user_id,
            subject=subject,
            start_time=datetime.now(timezone.utc),
            current_ability_estimate=initial_ability,
            questions_asked=[],
            responses=[],
            ai_help_usage=[],
            think_aloud_responses=[],
            session_type=session_type
        )
        
        self.session_data[session_id] = session
        return session_id
    
    def record_ai_assistance(self, session_id: str, assistance_type: str, 
                           question_id: str, help_content: str):
        """
        Record when student uses AI assistance during assessment
        """
        if session_id in self.session_data:
            self.session_data[session_id].ai_help_usage.append({
                'question_id': question_id,
                'assistance_type': assistance_type,
                'content': help_content,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    
    def get_session_analytics(self, session_id: str) -> Dict:
        """
        Generate comprehensive analytics for an assessment session
        """
        if session_id not in self.session_data:
            return {}
        
        session = self.session_data[session_id]
        
        # Calculate metrics
        total_questions = len(session.questions_asked)
        correct_answers = sum(1 for r in session.responses if r.get('is_correct', False))
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        ai_help_percentage = len(session.ai_help_usage) / total_questions * 100 if total_questions > 0 else 0
        
        avg_response_time = np.mean([r.get('response_time', 0) for r in session.responses]) if session.responses else 0
        
        return {
            'session_id': session_id,
            'total_questions': total_questions,
            'accuracy': accuracy,
            'final_ability_estimate': session.current_ability_estimate,
            'estimated_grade_level': self.determine_grade_level(session.current_ability_estimate).value,
            'ai_help_percentage': ai_help_percentage,
            'average_response_time': avg_response_time,
            'think_aloud_quality': np.mean([
                self._assess_reasoning_quality(ta) for ta in session.think_aloud_responses
            ]) if session.think_aloud_responses else 0,
            'session_duration': (datetime.now(timezone.utc) - session.start_time).total_seconds(),
            'learning_trajectory': self._calculate_learning_trajectory(session)
        }
    
    def _calculate_learning_trajectory(self, session: AdaptiveSession) -> List[Dict]:
        """
        Calculate learning progression throughout the session
        """
        trajectory = []
        ability_estimates = [0.5]  # Start with initial estimate
        
        for i, response in enumerate(session.responses):
            # Simulate ability progression
            if response.get('is_correct', False):
                ability_estimates.append(min(1.0, ability_estimates[-1] + 0.05))
            else:
                ability_estimates.append(max(0.0, ability_estimates[-1] - 0.03))
            
            trajectory.append({
                'question_number': i + 1,
                'ability_estimate': ability_estimates[-1],
                'question_difficulty': response.get('question_difficulty', 0.5),
                'is_correct': response.get('is_correct', False)
            })
        
        return trajectory

# Global adaptive engine instance
adaptive_engine = AdaptiveEngine()