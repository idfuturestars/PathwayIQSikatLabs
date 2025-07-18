"""
Speech-to-Text Module for Think-Aloud Assessments
Using OpenAI Whisper API for high-accuracy transcription
"""

import os
import tempfile
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import base64
import aiofiles
from openai import AsyncOpenAI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class SpeechToTextConfig(BaseModel):
    """Configuration for speech-to-text processing"""
    language: str = "en"  # Language code (en, es, fr, etc.)
    model: str = "whisper-1"  # OpenAI Whisper model
    temperature: float = 0.1  # Lower temperature for more focused output
    prompt: Optional[str] = None  # Optional context prompt

class TranscriptionSegment(BaseModel):
    """Individual transcription segment"""
    id: str
    text: str
    start_time: float
    end_time: float
    confidence: Optional[float] = None
    speaker: Optional[str] = None

class TranscriptionResult(BaseModel):
    """Complete transcription result"""
    id: str = None
    user_id: str
    assessment_id: str
    session_id: str
    text: str
    segments: List[TranscriptionSegment] = []
    language: str
    duration: float
    confidence: float
    created_at: datetime
    processing_time: float
    think_aloud_analysis: Optional[Dict[str, Any]] = None

class SpeechToTextProcessor:
    """Main speech-to-text processor using OpenAI Whisper"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.supported_formats = ['mp3', 'wav', 'webm', 'ogg', 'm4a']
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for OpenAI
        
    async def process_audio_file(
        self, 
        audio_data: bytes, 
        user_id: str, 
        assessment_id: str, 
        session_id: str,
        config: SpeechToTextConfig = None
    ) -> TranscriptionResult:
        """Process audio file and return transcription"""
        
        if config is None:
            config = SpeechToTextConfig()
            
        start_time = datetime.now()
        
        try:
            # Validate audio size
            if len(audio_data) > self.max_file_size:
                raise ValueError(f"Audio file too large: {len(audio_data)} bytes (max: {self.max_file_size})")
            
            # Create temporary file for OpenAI processing
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Process with OpenAI Whisper
                transcription_response = await self._transcribe_with_whisper(
                    temp_file_path, config
                )
                
                # Extract text and metadata
                transcription_text = transcription_response.text
                
                # Create transcription result
                result = TranscriptionResult(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    assessment_id=assessment_id,
                    session_id=session_id,
                    text=transcription_text,
                    language=config.language,
                    duration=0.0,  # We'll calculate this if needed
                    confidence=0.95,  # OpenAI doesn't provide confidence scores
                    created_at=datetime.now(timezone.utc),
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
                
                # Analyze think-aloud content
                if transcription_text:
                    result.think_aloud_analysis = await self._analyze_think_aloud(
                        transcription_text, user_id
                    )
                
                # Store in database
                await self._store_transcription(result)
                
                logger.info(f"Transcription completed for user {user_id} in {result.processing_time:.2f}s")
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Speech-to-text processing error: {str(e)}")
            raise
    
    async def _transcribe_with_whisper(self, file_path: str, config: SpeechToTextConfig) -> Any:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # Read file synchronously for OpenAI API
            with open(file_path, 'rb') as audio_file:
                transcription = await openai_client.audio.transcriptions.create(
                    model=config.model,
                    file=audio_file,
                    response_format="text",
                    language=config.language,
                    temperature=config.temperature,
                    prompt=config.prompt
                )
                return transcription
                
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            raise
    
    async def _analyze_think_aloud(self, text: str, user_id: str) -> Dict[str, Any]:
        """Analyze think-aloud content for learning insights"""
        try:
            # Use OpenAI to analyze the think-aloud content
            analysis_prompt = f"""
            Analyze this student's think-aloud response for learning insights:
            
            Text: "{text}"
            
            Provide analysis in the following categories:
            1. Problem-solving strategy used
            2. Confidence level (1-5 scale)
            3. Metacognitive awareness (1-5 scale)
            4. Areas of confusion or uncertainty
            5. Learning style indicators
            6. Emotional state indicators
            
            Return your analysis in JSON format with these keys:
            - strategy: string
            - confidence: number (1-5)
            - metacognition: number (1-5)
            - confusion_areas: array of strings
            - learning_style: string
            - emotional_state: string
            - key_insights: array of strings
            """
            
            response = await openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an educational psychology expert analyzing student think-aloud responses."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Think-aloud analysis error: {str(e)}")
            return {
                "strategy": "unable_to_analyze",
                "confidence": 3,
                "metacognition": 3,
                "confusion_areas": [],
                "learning_style": "unknown",
                "emotional_state": "neutral",
                "key_insights": ["Analysis unavailable due to processing error"]
            }
    
    async def _store_transcription(self, result: TranscriptionResult):
        """Store transcription result in database"""
        try:
            await self.db.transcriptions.insert_one(result.dict())
            logger.info(f"Stored transcription {result.id} for user {result.user_id}")
        except Exception as e:
            logger.error(f"Database storage error: {str(e)}")
            raise
    
    async def get_transcription_by_session(self, session_id: str) -> List[TranscriptionResult]:
        """Get all transcriptions for a session"""
        try:
            cursor = self.db.transcriptions.find({"session_id": session_id})
            transcriptions = await cursor.to_list(length=None)
            return [TranscriptionResult(**t) for t in transcriptions]
        except Exception as e:
            logger.error(f"Error retrieving transcriptions: {str(e)}")
            return []
    
    async def get_user_transcriptions(self, user_id: str, limit: int = 50) -> List[TranscriptionResult]:
        """Get recent transcriptions for a user"""
        try:
            cursor = self.db.transcriptions.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            transcriptions = await cursor.to_list(length=None)
            return [TranscriptionResult(**t) for t in transcriptions]
        except Exception as e:
            logger.error(f"Error retrieving user transcriptions: {str(e)}")
            return []
    
    async def process_real_time_audio(
        self, 
        audio_chunks: List[bytes], 
        user_id: str, 
        assessment_id: str, 
        session_id: str,
        config: SpeechToTextConfig = None
    ) -> TranscriptionResult:
        """Process multiple audio chunks for real-time transcription"""
        
        # Combine audio chunks
        combined_audio = b''.join(audio_chunks)
        
        # Process as single file
        return await self.process_audio_file(
            combined_audio, user_id, assessment_id, session_id, config
        )

# Global processor instance
speech_processor = None

def get_speech_processor(db: AsyncIOMotorDatabase) -> SpeechToTextProcessor:
    """Get speech processor instance"""
    global speech_processor
    if speech_processor is None:
        speech_processor = SpeechToTextProcessor(db)
    return speech_processor