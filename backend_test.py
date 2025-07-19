#!/usr/bin/env python3
"""
PathwayIQ Backend API Testing Suite
Tests all backend endpoints and verifies PathwayIQ branding
"""

import requests
import json
import os
import sys
import base64
from datetime import datetime
import uuid

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BACKEND_URL = get_backend_url()
if not BACKEND_URL:
    print("❌ Could not get REACT_APP_BACKEND_URL from frontend/.env")
    sys.exit(1)

API_BASE = f"{BACKEND_URL}/api"
print(f"🔗 Testing PathwayIQ API at: {API_BASE}")

# Test data
TEST_USER_DATA = {
    "username": f"pathwayiq_student_{uuid.uuid4().hex[:8]}",
    "email": f"student_{uuid.uuid4().hex[:8]}@pathwayiq.edu",
    "password": "PathwayIQ2024!",
    "full_name": "PathwayIQ Test Student"
}

# Global variables for auth
auth_token = None
user_data = None

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    status = "✅" if success else "❌"
    print(f"{status} {message}")
    if details:
        print(f"   Details: {details}")

def test_health_endpoint():
    """Test GET /api/health"""
    print_test_header("Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Health endpoint is working")
            print(f"   Response: {data}")
            
            # Check for proper response structure
            if "status" in data and data["status"] == "healthy":
                print_result(True, "Health status is 'healthy'")
            else:
                print_result(False, "Health status is not 'healthy'", data)
                
            return True
        else:
            print_result(False, f"Health check failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Health check failed with exception: {e}")
        return False

def test_root_endpoint():
    """Test GET /api/"""
    print_test_header("Root API Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Root endpoint is working")
            print(f"   Response: {data}")
            
            # Check for PathwayIQ branding
            message = data.get("message", "")
            if "PathwayIQ" in message:
                print_result(True, "PathwayIQ branding found in response")
            else:
                print_result(False, "PathwayIQ branding NOT found in response", message)
                
            # Check for version info
            if "version" in data:
                print_result(True, f"Version info present: {data['version']}")
            else:
                print_result(False, "Version info missing")
                
            return True
        else:
            print_result(False, f"Root endpoint failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Root endpoint failed with exception: {e}")
        return False

def test_user_registration():
    """Test POST /api/auth/register"""
    print_test_header("User Registration")
    global auth_token, user_data
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=TEST_USER_DATA,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User registration successful")
            
            # Check response structure
            required_fields = ["access_token", "token_type", "user"]
            for field in required_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
                    return False
            
            # Store auth token for subsequent tests
            auth_token = data["access_token"]
            user_data = data["user"]
            
            # Verify user data
            if user_data.get("username") == TEST_USER_DATA["username"]:
                print_result(True, "Username matches registration data")
            else:
                print_result(False, "Username mismatch")
                
            if user_data.get("email") == TEST_USER_DATA["email"]:
                print_result(True, "Email matches registration data")
            else:
                print_result(False, "Email mismatch")
                
            print(f"   User ID: {user_data.get('id')}")
            print(f"   User Level: {user_data.get('level', 1)}")
            print(f"   User XP: {user_data.get('xp', 0)}")
            
            return True
        else:
            print_result(False, f"Registration failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Registration failed with exception: {e}")
        return False

def test_demo_login():
    """Test POST /api/auth/login with demo credentials - TIER 1 CRITICAL TEST"""
    print_test_header("TIER 1 CRITICAL: Demo Login Test")
    
    try:
        # Test with demo credentials from review request
        demo_login_data = {
            "email": "demo@idfs-pathwayiq.com",
            "password": "demo123"
        }
        
        print(f"🔑 Testing demo credentials: {demo_login_data['email']} / {demo_login_data['password']}")
        
        start_time = datetime.now()
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=demo_login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Response time: {response_time:.3f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Demo login successful in {response_time:.3f}s")
            
            # Check response structure
            required_fields = ["access_token", "token_type", "user"]
            for field in required_fields:
                if field in data:
                    print_result(True, f"Demo login response contains {field}")
                else:
                    print_result(False, f"Demo login response missing {field}")
                    return False
            
            # Verify token type
            if data.get("token_type") == "bearer":
                print_result(True, "Token type is 'bearer'")
            else:
                print_result(False, f"Unexpected token type: {data.get('token_type')}")
            
            # Verify JWT token format
            token = data.get("access_token", "")
            if token and len(token.split('.')) == 3:
                print_result(True, "JWT token has correct format (3 parts)")
            else:
                print_result(False, "JWT token format is invalid")
            
            # Verify user data
            user = data.get("user", {})
            if user.get("email") == demo_login_data["email"]:
                print_result(True, "User email matches demo credentials")
            else:
                print_result(False, f"User email mismatch: expected {demo_login_data['email']}, got {user.get('email')}")
            
            # Store demo auth token for subsequent tests
            global auth_token, user_data
            auth_token = data["access_token"]
            user_data = data["user"]
            
            print(f"   Demo User ID: {user_data.get('id')}")
            print(f"   Demo User Level: {user_data.get('level', 1)}")
            print(f"   Demo User XP: {user_data.get('xp', 0)}")
            print(f"   Demo User Role: {user_data.get('role', 'unknown')}")
            
            return True
        else:
            print_result(False, f"Demo login failed with status {response.status_code}", response.text)
            
            # Additional debugging for failed demo login
            if response.status_code == 401:
                print("🔍 DIAGNOSIS: Demo credentials are invalid or demo user doesn't exist in database")
            elif response.status_code == 404:
                print("🔍 DIAGNOSIS: Login endpoint not found - check API routing")
            elif response.status_code == 500:
                print("🔍 DIAGNOSIS: Server error - check database connection and backend logs")
            
            return False
            
    except Exception as e:
        print_result(False, f"Demo login failed with exception: {e}")
        print("🔍 DIAGNOSIS: Network connectivity issue or backend server not responding")
        return False

def test_user_login():
    """Test POST /api/auth/login with registered user"""
    print_test_header("User Login (Registered User)")
    
    try:
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User login successful")
            
            # Check response structure
            required_fields = ["access_token", "token_type", "user"]
            for field in required_fields:
                if field in data:
                    print_result(True, f"Login response contains {field}")
                else:
                    print_result(False, f"Login response missing {field}")
                    return False
            
            # Verify token type
            if data.get("token_type") == "bearer":
                print_result(True, "Token type is 'bearer'")
            else:
                print_result(False, f"Unexpected token type: {data.get('token_type')}")
                
            return True
        else:
            print_result(False, f"Login failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Login failed with exception: {e}")
        return False

def test_adaptive_assessment_start():
    """Test GET /api/adaptive-assessment/start (with auth)"""
    print_test_header("Adaptive Assessment Start")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        # First test the POST endpoint for starting assessment
        assessment_config = {
            "subject": "mathematics",
            "target_grade_level": "grade_8",
            "assessment_type": "diagnostic",
            "enable_think_aloud": True,
            "enable_ai_help_tracking": True,
            "max_questions": 10
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/adaptive-assessment/start",
            json=assessment_config,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Adaptive assessment start successful")
            
            # Check response structure
            expected_fields = ["session_id", "initial_ability_estimate", "estimated_grade_level", "config"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Initial Ability: {data.get('initial_ability_estimate')}")
            print(f"   Grade Level: {data.get('estimated_grade_level')}")
            
            return True
        else:
            print_result(False, f"Adaptive assessment start failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Adaptive assessment start failed with exception: {e}")
        return False

def test_enhanced_ai_chat():
    """Test POST /api/ai/enhanced-chat (with auth)"""
    print_test_header("Enhanced AI Chat")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        chat_request = {
            "message": "Hello PathwayIQ! Can you help me understand quadratic equations?",
            "emotional_context": "curious",
            "learning_style": "visual",
            "ai_personality": "encouraging"
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/ai/enhanced-chat",
            json=chat_request,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Enhanced AI chat successful")
            
            # Check for PathwayIQ branding in AI response
            response_text = str(data)
            if "PathwayIQ" in response_text:
                print_result(True, "PathwayIQ branding found in AI response")
            else:
                print_result(False, "PathwayIQ branding NOT found in AI response")
            
            print(f"   AI Response preview: {str(data)[:200]}...")
            
            return True
        else:
            print_result(False, f"Enhanced AI chat failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Enhanced AI chat failed with exception: {e}")
        return False

def test_database_connection():
    """Test database connection by checking user creation"""
    print_test_header("Database Connection Test")
    
    if not user_data:
        print_result(False, "No user data available - cannot test database")
        return False
    
    try:
        # Test getting current user info (requires database lookup)
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Database connection working - user data retrieved")
            
            # Verify data consistency
            if data.get("id") == user_data.get("id"):
                print_result(True, "User ID consistency verified")
            else:
                print_result(False, "User ID mismatch between registration and retrieval")
                
            if data.get("email") == user_data.get("email"):
                print_result(True, "Email consistency verified")
            else:
                print_result(False, "Email mismatch between registration and retrieval")
                
            return True
        else:
            print_result(False, f"Database test failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Database test failed with exception: {e}")
        return False

def test_api_keys_configuration():
    """Test API keys configuration by checking AI functionality"""
    print_test_header("API Keys Configuration Test")
    
    # Check if backend .env file has required API keys
    try:
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
            
        required_keys = ['OPENAI_API_KEY', 'JWT_SECRET', 'MONGO_URL', 'DB_NAME']
        for key in required_keys:
            if key in env_content and f'{key}=' in env_content:
                # Check if key has a value
                for line in env_content.split('\n'):
                    if line.startswith(f'{key}='):
                        value = line.split('=', 1)[1].strip().strip('"')
                        if value and value != 'your_key_here':
                            print_result(True, f"{key} is configured")
                        else:
                            print_result(False, f"{key} is empty or placeholder")
                        break
            else:
                print_result(False, f"{key} is missing from configuration")
        
        # Verify database name is idfs_pathwayiq_database
        if 'DB_NAME="idfs_pathwayiq_database"' in env_content:
            print_result(True, "Database name is correctly set to 'idfs_pathwayiq_database'")
        else:
            print_result(False, "Database name is not set to 'idfs_pathwayiq_database'")
            
        return True
        
    except Exception as e:
        print_result(False, f"API keys configuration test failed: {e}")
        return False

def test_speech_to_text_start_session():
    """Test POST /api/speech-to-text/start-session"""
    print_test_header("Speech-to-Text Start Session")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        session_request = {
            "assessment_id": f"test_assessment_{uuid.uuid4().hex[:8]}",
            "question_id": f"test_question_{uuid.uuid4().hex[:8]}",
            "language": "en",
            "enable_analysis": True
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/start-session",
            json=session_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Think-aloud session started successfully")
            
            # Check response structure
            expected_fields = ["session_id", "status", "message", "instructions"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify session status
            if data.get("status") == "active":
                print_result(True, "Session status is 'active'")
            else:
                print_result(False, f"Unexpected session status: {data.get('status')}")
            
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Instructions: {data.get('instructions', '')[:100]}...")
            
            # Store session ID for subsequent tests
            global test_session_id
            test_session_id = data.get('session_id')
            
            return True
        else:
            print_result(False, f"Start session failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Start session failed with exception: {e}")
        return False

def test_speech_to_text_transcribe():
    """Test POST /api/speech-to-text/transcribe with mock audio data"""
    print_test_header("Speech-to-Text Transcribe")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        # Create mock base64 audio data (longer WAV file for OpenAI minimum requirement)
        # Create a 0.2 second WAV file with silence
        sample_rate = 44100
        duration = 0.2  # seconds
        samples = int(sample_rate * duration)
        
        # WAV header for 16-bit mono audio
        wav_header = b'RIFF'
        wav_header += (36 + samples * 2).to_bytes(4, 'little')  # File size
        wav_header += b'WAVE'
        wav_header += b'fmt '
        wav_header += (16).to_bytes(4, 'little')  # Subchunk1Size
        wav_header += (1).to_bytes(2, 'little')   # AudioFormat (PCM)
        wav_header += (1).to_bytes(2, 'little')   # NumChannels (mono)
        wav_header += sample_rate.to_bytes(4, 'little')  # SampleRate
        wav_header += (sample_rate * 2).to_bytes(4, 'little')  # ByteRate
        wav_header += (2).to_bytes(2, 'little')   # BlockAlign
        wav_header += (16).to_bytes(2, 'little')  # BitsPerSample
        wav_header += b'data'
        wav_header += (samples * 2).to_bytes(4, 'little')  # Subchunk2Size
        
        # Add silence data (zeros)
        silence_data = b'\x00\x00' * samples
        wav_data = wav_header + silence_data
        
        mock_audio_data = base64.b64encode(wav_data).decode('utf-8')
        
        transcribe_request = {
            "audio_data": mock_audio_data,
            "assessment_id": f"test_assessment_{uuid.uuid4().hex[:8]}",
            "session_id": f"test_session_{uuid.uuid4().hex[:8]}",
            "language": "en",
            "context_prompt": "This is a think-aloud assessment for mathematics problem solving."
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/transcribe",
            json=transcribe_request,
            headers=headers,
            timeout=30  # Longer timeout for OpenAI API
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Audio transcription successful")
            
            # Check response structure
            expected_fields = ["id", "text", "confidence", "processing_time", "created_at"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Check if think-aloud analysis is present
            if "think_aloud_analysis" in data and data["think_aloud_analysis"]:
                print_result(True, "Think-aloud analysis included in response")
                analysis = data["think_aloud_analysis"]
                if isinstance(analysis, dict):
                    analysis_keys = ["strategy", "confidence", "metacognition"]
                    for key in analysis_keys:
                        if key in analysis:
                            print_result(True, f"Analysis contains {key}")
                        else:
                            print_result(False, f"Analysis missing {key}")
            else:
                print_result(True, "Think-aloud analysis not present (expected for minimal audio)")
            
            print(f"   Transcription ID: {data.get('id')}")
            print(f"   Text: {data.get('text', 'No text')}")
            print(f"   Confidence: {data.get('confidence', 0)}")
            print(f"   Processing Time: {data.get('processing_time', 0):.3f}s")
            
            return True
        else:
            print_result(False, f"Transcription failed with status {response.status_code}", response.text)
            # Check for specific error types
            if response.status_code == 400:
                print("🔍 DIAGNOSIS: Invalid audio data or request format")
            elif response.status_code == 500:
                print("🔍 DIAGNOSIS: Server error - check OpenAI API key and backend logs")
            return False
            
    except Exception as e:
        print_result(False, f"Transcription failed with exception: {e}")
        return False

def test_speech_to_text_get_user_sessions():
    """Test GET /api/speech-to-text/user/sessions"""
    print_test_header("Speech-to-Text Get User Sessions")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/speech-to-text/user/sessions?limit=10",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User sessions retrieved successfully")
            
            # Check response structure
            expected_fields = ["sessions", "total"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            sessions = data.get("sessions", [])
            total = data.get("total", 0)
            
            print(f"   Total sessions: {total}")
            print(f"   Sessions returned: {len(sessions)}")
            
            # If we have sessions, check their structure
            if sessions:
                session = sessions[0]
                session_fields = ["id", "user_id", "assessment_id", "created_at", "status"]
                for field in session_fields:
                    if field in session:
                        print_result(True, f"Session contains {field}")
                    else:
                        print_result(False, f"Session missing {field}")
            
            return True
        else:
            print_result(False, f"Get user sessions failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get user sessions failed with exception: {e}")
        return False

def test_speech_to_text_session_transcriptions():
    """Test GET /api/speech-to-text/session/{session_id}/transcriptions"""
    print_test_header("Speech-to-Text Session Transcriptions")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    # Use test session ID if available, otherwise create a dummy one
    session_id = globals().get('test_session_id', f'test_session_{uuid.uuid4().hex[:8]}')
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/speech-to-text/session/{session_id}/transcriptions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Session transcriptions retrieved successfully")
            
            # Check response structure
            expected_fields = ["session_id", "transcriptions", "total_transcriptions"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            transcriptions = data.get("transcriptions", [])
            total = data.get("total_transcriptions", 0)
            
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Total transcriptions: {total}")
            print(f"   Transcriptions returned: {len(transcriptions)}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Session not found (expected for test session)")
            return True
        else:
            print_result(False, f"Get session transcriptions failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get session transcriptions failed with exception: {e}")
        return False

def test_speech_to_text_end_session():
    """Test POST /api/speech-to-text/session/{session_id}/end"""
    print_test_header("Speech-to-Text End Session")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    # Use test session ID if available, otherwise create a dummy one
    session_id = globals().get('test_session_id', f'test_session_{uuid.uuid4().hex[:8]}')
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/session/{session_id}/end",
            headers=headers,
            timeout=15  # Longer timeout for summary generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Session ended successfully")
            
            # Check response structure
            expected_fields = ["session_id", "status", "summary", "total_transcriptions", "message"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify session status
            if data.get("status") == "completed":
                print_result(True, "Session status is 'completed'")
            else:
                print_result(False, f"Unexpected session status: {data.get('status')}")
            
            # Check summary structure if present
            summary = data.get("summary")
            if summary and isinstance(summary, dict):
                summary_keys = ["overall_strategy", "confidence_progression", "learning_insights"]
                for key in summary_keys:
                    if key in summary:
                        print_result(True, f"Summary contains {key}")
                    else:
                        print_result(False, f"Summary missing {key}")
            
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Total transcriptions: {data.get('total_transcriptions', 0)}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Session not found (expected for test session)")
            return True
        else:
            print_result(False, f"End session failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"End session failed with exception: {e}")
        return False

def test_speech_to_text_authentication():
    """Test speech-to-text endpoints without authentication"""
    print_test_header("Speech-to-Text Authentication Test")
    
    try:
        # Test transcribe endpoint without auth
        transcribe_request = {
            "audio_data": "dGVzdA==",  # base64 "test"
            "assessment_id": "test",
            "session_id": "test",
            "language": "en"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/transcribe",
            json=transcribe_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Transcribe endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Transcribe endpoint should return 401/403, got {response.status_code}")
        
        # Test start session endpoint without auth
        session_request = {
            "assessment_id": "test",
            "question_id": "test",
            "language": "en"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/start-session",
            json=session_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Start session endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Start session endpoint should return 401/403, got {response.status_code}")
        
        # Test user sessions endpoint without auth
        response = requests.get(
            f"{API_BASE}/speech-to-text/user/sessions",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"User sessions endpoint properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"User sessions endpoint should return 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Authentication test failed with exception: {e}")
        return False

def test_speech_to_text_error_handling():
    """Test speech-to-text error handling"""
    print_test_header("Speech-to-Text Error Handling")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with invalid audio data
        invalid_request = {
            "audio_data": "invalid_base64_data",
            "assessment_id": "test",
            "session_id": "test",
            "language": "en"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/transcribe",
            json=invalid_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [400, 422, 500]:
            print_result(True, f"Invalid audio data properly rejected with status {response.status_code}")
        else:
            print_result(False, f"Invalid audio data should be rejected, got {response.status_code}")
        
        # Test with missing required fields
        incomplete_request = {
            "audio_data": "dGVzdA==",
            # Missing assessment_id, session_id
            "language": "en"
        }
        
        response = requests.post(
            f"{API_BASE}/speech-to-text/transcribe",
            json=incomplete_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [400, 422]:
            print_result(True, f"Missing required fields properly rejected with status {response.status_code}")
        else:
            print_result(False, f"Missing required fields should be rejected, got {response.status_code}")
        
        # Test with invalid session ID for transcriptions
        response = requests.get(
            f"{API_BASE}/speech-to-text/session/invalid_session_id/transcriptions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 404:
            print_result(True, "Invalid session ID properly returns 404")
            return True
        else:
            print_result(False, f"Invalid session ID should return 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error handling test failed with exception: {e}")
        return False

# ============================================================================
# AI CONTENT GENERATION TESTS
# ============================================================================

def test_content_generation_get_content_types():
    """Test GET /api/content-generation/content-types"""
    print_test_header("Content Generation - Get Content Types")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/content-generation/content-types",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Content types retrieved successfully")
            
            # Check response structure
            if "content_types" in data:
                print_result(True, "Response contains content_types")
                
                content_types = data["content_types"]
                expected_types = ["quiz", "lesson", "explanation", "practice_problems", "study_guide", "flashcards"]
                
                for expected_type in expected_types:
                    found = any(ct.get("id") == expected_type for ct in content_types)
                    if found:
                        print_result(True, f"Content type '{expected_type}' available")
                    else:
                        print_result(False, f"Content type '{expected_type}' missing")
                
                # Check structure of first content type
                if content_types:
                    first_type = content_types[0]
                    required_fields = ["id", "name", "description", "icon"]
                    for field in required_fields:
                        if field in first_type:
                            print_result(True, f"Content type contains {field}")
                        else:
                            print_result(False, f"Content type missing {field}")
                
                print(f"   Total content types: {len(content_types)}")
                return True
            else:
                print_result(False, "Response missing content_types")
                return False
        else:
            print_result(False, f"Get content types failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get content types failed with exception: {e}")
        return False

def test_content_generation_quiz():
    """Test POST /api/content-generation/generate for quiz generation"""
    print_test_header("Content Generation - Quiz Generation")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        quiz_request = {
            "content_type": "quiz",
            "subject": "Mathematics",
            "topic": "Quadratic Equations",
            "difficulty_level": "intermediate",
            "learning_objectives": [
                "Solve quadratic equations using factoring",
                "Apply the quadratic formula",
                "Identify the discriminant"
            ],
            "target_audience": "8th grade students",
            "length": "medium",
            "personalization_enabled": True,
            "context_prompt": "Create an engaging quiz with real-world applications"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=quiz_request,
            headers=headers,
            timeout=30  # Longer timeout for AI generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Quiz generation successful")
            
            # Check response structure
            expected_fields = ["id", "content_type", "subject", "topic", "title", "content", "metadata", "created_at", "quality_score"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify content type
            if data.get("content_type") == "quiz":
                print_result(True, "Content type is 'quiz'")
            else:
                print_result(False, f"Unexpected content type: {data.get('content_type')}")
            
            # Verify subject and topic
            if data.get("subject") == "Mathematics":
                print_result(True, "Subject matches request")
            else:
                print_result(False, f"Subject mismatch: {data.get('subject')}")
                
            if data.get("topic") == "Quadratic Equations":
                print_result(True, "Topic matches request")
            else:
                print_result(False, f"Topic mismatch: {data.get('topic')}")
            
            # Check content structure
            content = data.get("content", {})
            if isinstance(content, dict):
                print_result(True, "Content is properly structured as dictionary")
                
                # Look for quiz-specific fields
                quiz_fields = ["questions", "instructions", "total_questions"]
                for field in quiz_fields:
                    if field in content:
                        print_result(True, f"Quiz content contains {field}")
                    else:
                        print_result(False, f"Quiz content missing {field}")
            else:
                print_result(False, "Content is not properly structured")
            
            # Check quality score
            quality_score = data.get("quality_score", 0)
            if 0 <= quality_score <= 1:
                print_result(True, f"Quality score is valid: {quality_score}")
            else:
                print_result(False, f"Invalid quality score: {quality_score}")
            
            print(f"   Generated Content ID: {data.get('id')}")
            print(f"   Title: {data.get('title', 'No title')}")
            print(f"   Quality Score: {quality_score}")
            
            # Store content ID for subsequent tests
            global test_content_id
            test_content_id = data.get('id')
            
            return True
        else:
            print_result(False, f"Quiz generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Quiz generation failed with exception: {e}")
        return False

def test_content_generation_lesson():
    """Test POST /api/content-generation/generate for lesson generation"""
    print_test_header("Content Generation - Lesson Generation")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        lesson_request = {
            "content_type": "lesson",
            "subject": "Science",
            "topic": "Photosynthesis",
            "difficulty_level": "beginner",
            "learning_objectives": [
                "Understand the process of photosynthesis",
                "Identify the inputs and outputs",
                "Explain the importance to life on Earth"
            ],
            "target_audience": "6th grade students",
            "length": "short",
            "personalization_enabled": True
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=lesson_request,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Lesson generation successful")
            
            # Verify content type
            if data.get("content_type") == "lesson":
                print_result(True, "Content type is 'lesson'")
            else:
                print_result(False, f"Unexpected content type: {data.get('content_type')}")
            
            # Check lesson-specific content
            content = data.get("content", {})
            if isinstance(content, dict):
                lesson_fields = ["introduction", "main_content", "activities", "summary"]
                for field in lesson_fields:
                    if field in content:
                        print_result(True, f"Lesson content contains {field}")
                    else:
                        print_result(False, f"Lesson content missing {field}")
            
            print(f"   Lesson Title: {data.get('title', 'No title')}")
            print(f"   Subject: {data.get('subject')}")
            print(f"   Topic: {data.get('topic')}")
            
            return True
        else:
            print_result(False, f"Lesson generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Lesson generation failed with exception: {e}")
        return False

def test_content_generation_explanation():
    """Test POST /api/content-generation/generate for explanation generation"""
    print_test_header("Content Generation - Explanation Generation")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        explanation_request = {
            "content_type": "explanation",
            "subject": "History",
            "topic": "World War II",
            "difficulty_level": "advanced",
            "learning_objectives": [
                "Understand the causes of World War II",
                "Analyze key events and turning points",
                "Evaluate the impact on global politics"
            ],
            "target_audience": "high school students",
            "length": "medium"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=explanation_request,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Explanation generation successful")
            
            # Verify content type
            if data.get("content_type") == "explanation":
                print_result(True, "Content type is 'explanation'")
            else:
                print_result(False, f"Unexpected content type: {data.get('content_type')}")
            
            # Check explanation-specific content
            content = data.get("content", {})
            if isinstance(content, dict):
                explanation_fields = ["main_explanation", "key_points", "examples"]
                for field in explanation_fields:
                    if field in content:
                        print_result(True, f"Explanation content contains {field}")
                    else:
                        print_result(False, f"Explanation content missing {field}")
            
            print(f"   Explanation Title: {data.get('title', 'No title')}")
            
            return True
        else:
            print_result(False, f"Explanation generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Explanation generation failed with exception: {e}")
        return False

def test_content_generation_get_user_content():
    """Test GET /api/content-generation/user-content"""
    print_test_header("Content Generation - Get User Content")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/content-generation/user-content?limit=10",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User content retrieved successfully")
            
            # Check response structure
            expected_fields = ["contents", "total"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            contents = data.get("contents", [])
            total = data.get("total", 0)
            
            print(f"   Total user content: {total}")
            print(f"   Contents returned: {len(contents)}")
            
            # If we have content, check structure
            if contents:
                first_content = contents[0]
                content_fields = ["id", "content_type", "subject", "topic", "title", "created_at", "quality_score"]
                for field in content_fields:
                    if field in first_content:
                        print_result(True, f"Content item contains {field}")
                    else:
                        print_result(False, f"Content item missing {field}")
            
            return True
        else:
            print_result(False, f"Get user content failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get user content failed with exception: {e}")
        return False

def test_content_generation_get_content_by_id():
    """Test GET /api/content-generation/content/{content_id}"""
    print_test_header("Content Generation - Get Content By ID")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    # Use test content ID if available, otherwise create a dummy one
    content_id = globals().get('test_content_id', f'test_content_{uuid.uuid4().hex[:8]}')
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/content-generation/content/{content_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Content retrieved by ID successfully")
            
            # Check response structure
            expected_fields = ["id", "content_type", "subject", "topic", "title", "content", "metadata", "created_at", "quality_score", "usage_count"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify content ID matches
            if data.get("id") == content_id:
                print_result(True, "Content ID matches request")
            else:
                print_result(False, f"Content ID mismatch: expected {content_id}, got {data.get('id')}")
            
            # Check usage count increment
            usage_count = data.get("usage_count", 0)
            if usage_count >= 1:
                print_result(True, f"Usage count incremented: {usage_count}")
            else:
                print_result(False, f"Usage count not incremented: {usage_count}")
            
            print(f"   Content ID: {data.get('id')}")
            print(f"   Title: {data.get('title', 'No title')}")
            print(f"   Usage Count: {usage_count}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Content not found (expected for test content)")
            return True
        else:
            print_result(False, f"Get content by ID failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get content by ID failed with exception: {e}")
        return False

def test_content_generation_regenerate():
    """Test POST /api/content-generation/regenerate/{content_id}"""
    print_test_header("Content Generation - Regenerate Content")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    # Use test content ID if available, otherwise create a dummy one
    content_id = globals().get('test_content_id', f'test_content_{uuid.uuid4().hex[:8]}')
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/regenerate/{content_id}",
            headers=headers,
            timeout=30  # Longer timeout for AI generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Content regeneration successful")
            
            # Check response structure (should be same as generate)
            expected_fields = ["id", "content_type", "subject", "topic", "title", "content", "metadata", "created_at", "quality_score"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify new content ID (should be different from original)
            new_content_id = data.get("id")
            if new_content_id and new_content_id != content_id:
                print_result(True, "New content ID generated for regenerated content")
            else:
                print_result(False, "Content ID should be different for regenerated content")
            
            print(f"   Original Content ID: {content_id}")
            print(f"   New Content ID: {new_content_id}")
            print(f"   Regenerated Title: {data.get('title', 'No title')}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Content not found for regeneration (expected for test content)")
            return True
        else:
            print_result(False, f"Content regeneration failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Content regeneration failed with exception: {e}")
        return False

def test_content_generation_authentication():
    """Test content generation endpoints without authentication"""
    print_test_header("Content Generation Authentication Test")
    
    try:
        # Test generate endpoint without auth
        generate_request = {
            "content_type": "quiz",
            "subject": "Math",
            "topic": "Test",
            "difficulty_level": "beginner"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=generate_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Generate endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Generate endpoint should return 401/403, got {response.status_code}")
        
        # Test content types endpoint without auth
        response = requests.get(
            f"{API_BASE}/content-generation/content-types",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Content types endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Content types endpoint should return 401/403, got {response.status_code}")
        
        # Test user content endpoint without auth
        response = requests.get(
            f"{API_BASE}/content-generation/user-content",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"User content endpoint properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"User content endpoint should return 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Authentication test failed with exception: {e}")
        return False

def test_content_generation_error_handling():
    """Test content generation error handling"""
    print_test_header("Content Generation Error Handling")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with invalid content type
        invalid_request = {
            "content_type": "invalid_type",
            "subject": "Math",
            "topic": "Test",
            "difficulty_level": "beginner"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=invalid_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [400, 422, 500]:
            print_result(True, f"Invalid content type properly rejected with status {response.status_code}")
        else:
            print_result(False, f"Invalid content type should be rejected, got {response.status_code}")
        
        # Test with missing required fields
        incomplete_request = {
            "content_type": "quiz",
            # Missing subject, topic
            "difficulty_level": "beginner"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=incomplete_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [400, 422]:
            print_result(True, f"Missing required fields properly rejected with status {response.status_code}")
        else:
            print_result(False, f"Missing required fields should be rejected, got {response.status_code}")
        
        # Test with invalid content ID
        response = requests.get(
            f"{API_BASE}/content-generation/content/invalid_content_id",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 404:
            print_result(True, "Invalid content ID properly returns 404")
            return True
        else:
            print_result(False, f"Invalid content ID should return 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error handling test failed with exception: {e}")
        return False

# ============================================================================
# PHASE 2 BACKEND FEATURE TESTS - COLLABORATION, PREDICTIVE, EMOTION
# ============================================================================

def test_collaboration_create_study_group():
    """Test POST /api/collaboration/groups/create"""
    print_test_header("Collaboration - Create Study Group")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        group_data = {
            "name": "PathwayIQ Math Study Group",
            "description": "A collaborative group for learning advanced mathematics",
            "subject": "mathematics",
            "group_type": "study_group",
            "max_members": 15,
            "is_public": True,
            "allow_member_invites": True,
            "require_approval": False,
            "enable_discussions": True,
            "enable_projects": True,
            "tags": ["algebra", "calculus", "problem-solving"],
            "learning_objectives": [
                "Master quadratic equations",
                "Understand calculus fundamentals",
                "Improve problem-solving skills"
            ]
        }
        
        response = requests.post(
            f"{API_BASE}/collaboration/groups/create",
            json=group_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Study group created successfully")
            
            # Check response structure
            expected_fields = ["success", "group_id", "group", "message"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify group data
            if data.get("success"):
                print_result(True, "Success flag is True")
            else:
                print_result(False, "Success flag is False")
            
            group = data.get("group", {})
            if group.get("name") == group_data["name"]:
                print_result(True, "Group name matches request")
            else:
                print_result(False, f"Group name mismatch: expected {group_data['name']}, got {group.get('name')}")
            
            print(f"   Group ID: {data.get('group_id')}")
            print(f"   Group Name: {group.get('name')}")
            print(f"   Subject: {group.get('subject')}")
            
            # Store group ID for subsequent tests
            global test_group_id
            test_group_id = data.get('group_id')
            
            return True
        else:
            print_result(False, f"Create study group failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Create study group failed with exception: {e}")
        return False

def test_collaboration_get_user_groups():
    """Test GET /api/collaboration/groups/user"""
    print_test_header("Collaboration - Get User Groups")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/collaboration/groups/user?status=active",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User groups retrieved successfully")
            
            # Check response structure
            expected_fields = ["success", "groups", "total_groups"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            groups = data.get("groups", [])
            total_groups = data.get("total_groups", 0)
            
            print(f"   Total groups: {total_groups}")
            print(f"   Groups returned: {len(groups)}")
            
            # If we have groups, check their structure
            if groups:
                first_group = groups[0]
                group_fields = ["group_id", "name", "subject", "user_role", "joined_at"]
                for field in group_fields:
                    if field in first_group:
                        print_result(True, f"Group contains {field}")
                    else:
                        print_result(False, f"Group missing {field}")
            
            return True
        else:
            print_result(False, f"Get user groups failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get user groups failed with exception: {e}")
        return False

def test_collaboration_search_groups():
    """Test GET /api/collaboration/groups/search"""
    print_test_header("Collaboration - Search Groups")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test search by subject
        response = requests.get(
            f"{API_BASE}/collaboration/groups/search?subject=mathematics",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Group search successful")
            
            # Check response structure
            expected_fields = ["success", "groups", "total_results", "search_params"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            groups = data.get("groups", [])
            total_results = data.get("total_results", 0)
            
            print(f"   Search results: {total_results}")
            print(f"   Groups returned: {len(groups)}")
            
            return True
        else:
            print_result(False, f"Search groups failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Search groups failed with exception: {e}")
        return False

def test_collaboration_create_discussion():
    """Test POST /api/collaboration/groups/{group_id}/discussions"""
    print_test_header("Collaboration - Create Discussion")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    # Use test group ID if available, otherwise create a dummy one
    group_id = globals().get('test_group_id', f'test_group_{uuid.uuid4().hex[:8]}')
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        discussion_data = {
            "title": "Quadratic Equations Discussion",
            "content": "Let's discuss different methods for solving quadratic equations. What's your favorite approach?",
            "category": "mathematics",
            "tags": ["quadratic", "algebra", "problem-solving"]
        }
        
        response = requests.post(
            f"{API_BASE}/collaboration/groups/{group_id}/discussions",
            json=discussion_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Discussion created successfully")
            
            # Check response structure
            expected_fields = ["success", "discussion_id", "discussion", "message"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            discussion = data.get("discussion", {})
            if discussion.get("title") == discussion_data["title"]:
                print_result(True, "Discussion title matches request")
            else:
                print_result(False, "Discussion title mismatch")
            
            print(f"   Discussion ID: {data.get('discussion_id')}")
            print(f"   Title: {discussion.get('title')}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Create discussion failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Create discussion failed with exception: {e}")
        return False

def test_predictive_learning_outcomes():
    """Test GET /api/predictive/learning-outcomes"""
    print_test_header("Predictive Analytics - Learning Outcomes")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/predictive/learning-outcomes?prediction_horizon=30",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Learning outcomes prediction successful")
            
            # Check response structure
            expected_fields = ["success", "predictions"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            predictions = data.get("predictions", {})
            if isinstance(predictions, dict):
                print_result(True, "Predictions data is properly structured")
                
                # Check for prediction components
                prediction_fields = ["user_id", "prediction_horizon", "performance_forecast", "skill_development"]
                for field in prediction_fields:
                    if field in predictions:
                        print_result(True, f"Predictions contain {field}")
                    else:
                        print_result(False, f"Predictions missing {field}")
            
            print(f"   User ID: {predictions.get('user_id', 'N/A')}")
            print(f"   Prediction Horizon: {predictions.get('prediction_horizon', 'N/A')} days")
            
            return True
        else:
            print_result(False, f"Learning outcomes prediction failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Learning outcomes prediction failed with exception: {e}")
        return False

def test_predictive_risk_assessment():
    """Test GET /api/predictive/risk-assessment"""
    print_test_header("Predictive Analytics - Risk Assessment")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/predictive/risk-assessment",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Risk assessment successful")
            
            # Check response structure
            expected_fields = ["success", "risk_assessment"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            risk_assessment = data.get("risk_assessment", {})
            if isinstance(risk_assessment, dict):
                print_result(True, "Risk assessment data is properly structured")
                
                # Check for risk assessment components
                risk_fields = ["user_id", "overall_risk_level", "risk_factors", "intervention_recommendations"]
                for field in risk_fields:
                    if field in risk_assessment:
                        print_result(True, f"Risk assessment contains {field}")
                    else:
                        print_result(False, f"Risk assessment missing {field}")
            
            print(f"   User ID: {risk_assessment.get('user_id', 'N/A')}")
            print(f"   Risk Level: {risk_assessment.get('overall_risk_level', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Risk assessment failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Risk assessment failed with exception: {e}")
        return False

def test_predictive_skill_mastery():
    """Test POST /api/predictive/skill-mastery"""
    print_test_header("Predictive Analytics - Skill Mastery")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        skills_request = ["algebra", "geometry", "calculus"]
        
        response = requests.post(
            f"{API_BASE}/predictive/skill-mastery",
            json=skills_request,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Skill mastery prediction successful")
            
            # Check response structure
            expected_fields = ["success", "skill_mastery_predictions"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            predictions = data.get("skill_mastery_predictions", {})
            if isinstance(predictions, dict):
                print_result(True, "Skill mastery predictions properly structured")
                
                # Check for prediction components
                prediction_fields = ["user_id", "skills_analyzed", "mastery_timeline", "recommendations"]
                for field in prediction_fields:
                    if field in predictions:
                        print_result(True, f"Predictions contain {field}")
                    else:
                        print_result(False, f"Predictions missing {field}")
            
            print(f"   Skills analyzed: {len(predictions.get('skills_analyzed', []))}")
            
            return True
        else:
            print_result(False, f"Skill mastery prediction failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Skill mastery prediction failed with exception: {e}")
        return False

def test_emotion_analyze():
    """Test POST /api/emotion/analyze"""
    print_test_header("Emotional Intelligence - Analyze Emotional State")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with different emotional contexts
        test_texts = [
            "I'm really excited about learning calculus! This is so interesting and I can't wait to solve more problems.",
            "I'm feeling frustrated with these algebra problems. They seem too difficult and I don't understand the concepts.",
            "I'm confident that I can master these mathematical concepts with practice and dedication."
        ]
        
        for i, text_input in enumerate(test_texts):
            response = requests.post(
                f"{API_BASE}/emotion/analyze",
                json={"text_input": text_input, "context": {"session_type": "learning"}},
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Emotional analysis successful for text {i+1}")
                
                # Check response structure
                expected_fields = ["success", "emotional_analysis"]
                for field in expected_fields:
                    if field in data:
                        print_result(True, f"Response contains {field}")
                    else:
                        print_result(False, f"Response missing {field}")
                
                analysis = data.get("emotional_analysis", {})
                if isinstance(analysis, dict):
                    print_result(True, "Emotional analysis properly structured")
                    
                    # Check for analysis components
                    analysis_fields = ["user_id", "primary_emotion", "emotional_intensity", "mood_category", "emotional_indicators"]
                    for field in analysis_fields:
                        if field in analysis:
                            print_result(True, f"Analysis contains {field}")
                        else:
                            print_result(False, f"Analysis missing {field}")
                
                print(f"   Primary Emotion: {analysis.get('primary_emotion', 'N/A')}")
                print(f"   Mood Category: {analysis.get('mood_category', 'N/A')}")
                print(f"   Emotional Intensity: {analysis.get('emotional_intensity', 'N/A')}")
                
            else:
                print_result(False, f"Emotional analysis failed for text {i+1} with status {response.status_code}", response.text)
                return False
        
        return True
            
    except Exception as e:
        print_result(False, f"Emotional analysis failed with exception: {e}")
        return False

def test_emotion_empathetic_response():
    """Test POST /api/emotion/empathetic-response"""
    print_test_header("Emotional Intelligence - Generate Empathetic Response")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        user_message = "I'm struggling with these math problems and feeling really overwhelmed. I don't think I'm smart enough for this."
        
        response = requests.post(
            f"{API_BASE}/emotion/empathetic-response",
            json={"user_message": user_message},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Empathetic response generated successfully")
            
            # Check response structure
            expected_fields = ["success", "empathetic_response"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            empathetic_response = data.get("empathetic_response", {})
            if isinstance(empathetic_response, dict):
                print_result(True, "Empathetic response properly structured")
                
                # Check for response components
                response_fields = ["response_id", "user_id", "primary_emotion_detected", "response_strategy", "response_content"]
                for field in response_fields:
                    if field in empathetic_response:
                        print_result(True, f"Response contains {field}")
                    else:
                        print_result(False, f"Response missing {field}")
            
            print(f"   Detected Emotion: {empathetic_response.get('primary_emotion_detected', 'N/A')}")
            print(f"   Response Strategy: {empathetic_response.get('response_strategy', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Empathetic response failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Empathetic response failed with exception: {e}")
        return False

def test_emotion_journey():
    """Test GET /api/emotion/journey"""
    print_test_header("Emotional Intelligence - Track Emotional Journey")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/emotion/journey?time_period=30",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Emotional journey tracking successful")
            
            # Check response structure
            expected_fields = ["success", "emotional_journey"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            journey = data.get("emotional_journey", {})
            if isinstance(journey, dict):
                print_result(True, "Emotional journey properly structured")
                
                # Check for journey components
                journey_fields = ["user_id", "analysis_period_days", "total_interactions", "pattern_analysis"]
                for field in journey_fields:
                    if field in journey:
                        print_result(True, f"Journey contains {field}")
                    else:
                        print_result(False, f"Journey missing {field}")
            
            print(f"   Analysis Period: {journey.get('analysis_period_days', 'N/A')} days")
            print(f"   Total Interactions: {journey.get('total_interactions', 'N/A')}")
            
            return True
        else:
            # Check if it's a "no data" error which is acceptable
            if response.status_code == 404 or "No emotional data" in response.text:
                print_result(True, "No emotional data available (expected for new user)")
                return True
            else:
                print_result(False, f"Emotional journey tracking failed with status {response.status_code}", response.text)
                return False
            
    except Exception as e:
        print_result(False, f"Emotional journey tracking failed with exception: {e}")
        return False

def test_emotion_profile():
    """Test GET /api/emotion/profile"""
    print_test_header("Emotional Intelligence - Get Emotional Learning Profile")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/emotion/profile",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Emotional learning profile retrieved successfully")
            
            # Check response structure
            expected_fields = ["success", "emotional_learning_profile"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            profile = data.get("emotional_learning_profile", {})
            if isinstance(profile, dict):
                print_result(True, "Emotional profile properly structured")
                
                # Check for profile components
                profile_fields = ["user_id", "profile_type", "emotional_characteristics", "learning_preferences"]
                for field in profile_fields:
                    if field in profile:
                        print_result(True, f"Profile contains {field}")
                    else:
                        print_result(False, f"Profile missing {field}")
            
            print(f"   Profile Type: {profile.get('profile_type', 'N/A')}")
            print(f"   User ID: {profile.get('user_id', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Emotional profile retrieval failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Emotional profile retrieval failed with exception: {e}")
        return False

def test_collaboration_authentication():
    """Test collaboration endpoints without authentication"""
    print_test_header("Collaboration Authentication Test")
    
    try:
        # Test create group endpoint without auth
        group_data = {"name": "Test Group", "subject": "test"}
        
        response = requests.post(
            f"{API_BASE}/collaboration/groups/create",
            json=group_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Create group endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Create group endpoint should return 401/403, got {response.status_code}")
        
        # Test get user groups endpoint without auth
        response = requests.get(
            f"{API_BASE}/collaboration/groups/user",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Get user groups endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Get user groups endpoint should return 401/403, got {response.status_code}")
        
        # Test search groups endpoint without auth
        response = requests.get(
            f"{API_BASE}/collaboration/groups/search",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Search groups endpoint properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"Search groups endpoint should return 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Collaboration authentication test failed with exception: {e}")
        return False

def test_predictive_authentication():
    """Test predictive analytics endpoints without authentication"""
    print_test_header("Predictive Analytics Authentication Test")
    
    try:
        # Test learning outcomes endpoint without auth
        response = requests.get(
            f"{API_BASE}/predictive/learning-outcomes",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Learning outcomes endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Learning outcomes endpoint should return 401/403, got {response.status_code}")
        
        # Test risk assessment endpoint without auth
        response = requests.get(
            f"{API_BASE}/predictive/risk-assessment",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Risk assessment endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Risk assessment endpoint should return 401/403, got {response.status_code}")
        
        # Test skill mastery endpoint without auth
        response = requests.post(
            f"{API_BASE}/predictive/skill-mastery",
            json=["test"],
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Skill mastery endpoint properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"Skill mastery endpoint should return 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Predictive authentication test failed with exception: {e}")
        return False

def test_emotion_authentication():
    """Test emotional intelligence endpoints without authentication"""
    print_test_header("Emotional Intelligence Authentication Test")
    
    try:
        # Test emotion analyze endpoint without auth
        response = requests.post(
            f"{API_BASE}/emotion/analyze",
            json={"text_input": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Emotion analyze endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Emotion analyze endpoint should return 401/403, got {response.status_code}")
        
        # Test empathetic response endpoint without auth
        response = requests.post(
            f"{API_BASE}/emotion/empathetic-response",
            json={"user_message": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Empathetic response endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Empathetic response endpoint should return 401/403, got {response.status_code}")
        
        # Test emotional journey endpoint without auth
        response = requests.get(
            f"{API_BASE}/emotion/journey",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Emotional journey endpoint properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"Emotional journey endpoint should return 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Emotion authentication test failed with exception: {e}")
        return False

# ============================================================================
# ANALYTICS AND REPORTING TESTS - PHASE 2 IMPLEMENTATION
# ============================================================================

def test_analytics_user_performance():
    """Test GET /api/analytics/user/performance"""
    print_test_header("Analytics - User Performance")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with different time periods
        time_periods = ["7d", "30d", "90d"]
        
        for period in time_periods:
            response = requests.get(
                f"{API_BASE}/analytics/user/performance?time_period={period}",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"User performance analytics retrieved for {period}")
                
                # Check response structure
                expected_fields = ["user_id", "time_period", "performance_metrics", "learning_analytics", "skill_progress"]
                for field in expected_fields:
                    if field in data:
                        print_result(True, f"Response contains {field}")
                    else:
                        print_result(False, f"Response missing {field}")
                
                # Verify time period matches
                if data.get("time_period") == period:
                    print_result(True, f"Time period matches request: {period}")
                else:
                    print_result(False, f"Time period mismatch: expected {period}, got {data.get('time_period')}")
                
                print(f"   Time Period: {period}")
                print(f"   User ID: {data.get('user_id', 'N/A')}")
                
            else:
                print_result(False, f"User performance analytics failed for {period} with status {response.status_code}", response.text)
                return False
        
        return True
        
    except Exception as e:
        print_result(False, f"User performance analytics failed with exception: {e}")
        return False

def test_analytics_dashboard():
    """Test GET /api/analytics/dashboard"""
    print_test_header("Analytics - Dashboard")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/analytics/dashboard?time_period=30d",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Analytics dashboard retrieved successfully")
            
            # Check response structure
            expected_fields = ["user_id", "dashboard_data", "learning_insights", "recommendations", "progress_summary"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Dashboard contains {field}")
                else:
                    print_result(False, f"Dashboard missing {field}")
            
            # Check dashboard data structure
            dashboard_data = data.get("dashboard_data", {})
            if isinstance(dashboard_data, dict):
                dashboard_fields = ["overall_progress", "recent_activity", "skill_breakdown", "engagement_metrics"]
                for field in dashboard_fields:
                    if field in dashboard_data:
                        print_result(True, f"Dashboard data contains {field}")
                    else:
                        print_result(False, f"Dashboard data missing {field}")
            
            print(f"   User ID: {data.get('user_id', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Analytics dashboard failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Analytics dashboard failed with exception: {e}")
        return False

def test_analytics_class():
    """Test GET /api/analytics/class (requires teacher/admin role)"""
    print_test_header("Analytics - Class Analytics")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/analytics/class",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Class analytics retrieved successfully")
            
            # Check response structure
            expected_fields = ["class_id", "class_analytics", "student_performance", "engagement_summary"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Class analytics contains {field}")
                else:
                    print_result(False, f"Class analytics missing {field}")
            
            return True
        elif response.status_code == 403:
            print_result(True, "Class analytics properly requires teacher/admin role (403 Forbidden)")
            return True
        else:
            print_result(False, f"Class analytics failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Class analytics failed with exception: {e}")
        return False

def test_analytics_snapshot():
    """Test POST /api/analytics/snapshot"""
    print_test_header("Analytics - Store Snapshot")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/analytics/snapshot",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Analytics snapshot stored successfully")
            
            # Check response structure
            expected_fields = ["snapshot_id", "user_id", "timestamp", "analytics_data"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Snapshot response contains {field}")
                else:
                    print_result(False, f"Snapshot response missing {field}")
            
            print(f"   Snapshot ID: {data.get('snapshot_id', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Analytics snapshot failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Analytics snapshot failed with exception: {e}")
        return False

def test_analytics_history():
    """Test GET /api/analytics/history"""
    print_test_header("Analytics - History")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/analytics/history?days=30",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Analytics history retrieved successfully")
            
            # Check response structure
            expected_fields = ["user_id", "history_data", "time_range", "snapshots"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"History response contains {field}")
                else:
                    print_result(False, f"History response missing {field}")
            
            snapshots = data.get("snapshots", [])
            print(f"   Historical snapshots: {len(snapshots)}")
            print(f"   Time range: {data.get('time_range', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Analytics history failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Analytics history failed with exception: {e}")
        return False

def test_reports_student_progress():
    """Test POST /api/reports/student-progress"""
    print_test_header("Reports - Student Progress")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with current user as student_id
        student_id = user_data.get('id', 'test_student') if user_data else 'test_student'
        
        # Test both PDF and CSV formats
        formats = ["pdf", "csv"]
        
        for format_type in formats:
            response = requests.post(
                f"{API_BASE}/reports/student-progress?format={format_type}&date_range=30d",
                json={"student_id": student_id},
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Student progress report generated successfully ({format_type})")
                
                # Check response structure
                expected_fields = ["report_id", "format", "student_id", "generated_at", "report_data"]
                for field in expected_fields:
                    if field in data:
                        print_result(True, f"Report response contains {field}")
                    else:
                        print_result(False, f"Report response missing {field}")
                
                # Verify format matches
                if data.get("format") == format_type:
                    print_result(True, f"Report format matches request: {format_type}")
                else:
                    print_result(False, f"Format mismatch: expected {format_type}, got {data.get('format')}")
                
                print(f"   Report ID: {data.get('report_id', 'N/A')}")
                print(f"   Format: {format_type}")
                
            elif response.status_code == 403:
                print_result(True, f"Student progress report properly requires appropriate permissions (403 Forbidden)")
            else:
                print_result(False, f"Student progress report failed for {format_type} with status {response.status_code}", response.text)
                return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Student progress report failed with exception: {e}")
        return False

def test_reports_class_performance():
    """Test POST /api/reports/class-performance"""
    print_test_header("Reports - Class Performance")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/reports/class-performance?format=pdf",
            headers=headers,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Class performance report generated successfully")
            
            # Check response structure
            expected_fields = ["report_id", "format", "class_id", "generated_at", "report_data"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Class report contains {field}")
                else:
                    print_result(False, f"Class report missing {field}")
            
            print(f"   Report ID: {data.get('report_id', 'N/A')}")
            
            return True
        elif response.status_code == 403:
            print_result(True, "Class performance report properly requires teacher/admin role (403 Forbidden)")
            return True
        else:
            print_result(False, f"Class performance report failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Class performance report failed with exception: {e}")
        return False

def test_reports_assessment_analysis():
    """Test POST /api/reports/assessment-analysis"""
    print_test_header("Reports - Assessment Analysis")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/reports/assessment-analysis?format=csv&date_range=30d",
            headers=headers,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Assessment analysis report generated successfully")
            
            # Check response structure
            expected_fields = ["report_id", "format", "date_range", "generated_at", "report_data"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Assessment report contains {field}")
                else:
                    print_result(False, f"Assessment report missing {field}")
            
            print(f"   Report ID: {data.get('report_id', 'N/A')}")
            print(f"   Date Range: {data.get('date_range', 'N/A')}")
            
            return True
        elif response.status_code == 403:
            print_result(True, "Assessment analysis report properly requires appropriate permissions (403 Forbidden)")
            return True
        else:
            print_result(False, f"Assessment analysis report failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Assessment analysis report failed with exception: {e}")
        return False

def test_reports_templates():
    """Test GET /api/reports/templates"""
    print_test_header("Reports - Get Templates")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/reports/templates",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Report templates retrieved successfully")
            
            # Check response structure
            expected_fields = ["templates", "total"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Templates response contains {field}")
                else:
                    print_result(False, f"Templates response missing {field}")
            
            templates = data.get("templates", [])
            print(f"   Available templates: {len(templates)}")
            
            # Check template structure if available
            if templates:
                template = templates[0]
                template_fields = ["id", "name", "description", "format", "category"]
                for field in template_fields:
                    if field in template:
                        print_result(True, f"Template contains {field}")
                    else:
                        print_result(False, f"Template missing {field}")
            
            return True
        elif response.status_code == 403:
            print_result(True, "Report templates properly requires educator access (403 Forbidden)")
            return True
        else:
            print_result(False, f"Report templates failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Report templates failed with exception: {e}")
        return False

def test_reports_educator():
    """Test GET /api/reports/educator"""
    print_test_header("Reports - Get Educator Reports")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/reports/educator?limit=10",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Educator reports retrieved successfully")
            
            # Check response structure
            expected_fields = ["reports", "total", "educator_id"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Educator reports contains {field}")
                else:
                    print_result(False, f"Educator reports missing {field}")
            
            reports = data.get("reports", [])
            print(f"   Educator reports: {len(reports)}")
            
            # Check report structure if available
            if reports:
                report = reports[0]
                report_fields = ["id", "title", "format", "created_at", "status"]
                for field in report_fields:
                    if field in report:
                        print_result(True, f"Report contains {field}")
                    else:
                        print_result(False, f"Report missing {field}")
            
            return True
        elif response.status_code == 403:
            print_result(True, "Educator reports properly requires educator access (403 Forbidden)")
            return True
        else:
            print_result(False, f"Educator reports failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Educator reports failed with exception: {e}")
        return False

def test_reports_delete():
    """Test DELETE /api/reports/{report_id}"""
    print_test_header("Reports - Delete Report")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Use a test report ID
        test_report_id = f"test_report_{uuid.uuid4().hex[:8]}"
        
        response = requests.delete(
            f"{API_BASE}/reports/{test_report_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Report deletion successful")
            
            # Check response structure
            expected_fields = ["success", "message", "report_id"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Delete response contains {field}")
                else:
                    print_result(False, f"Delete response missing {field}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Report not found (expected for test report)")
            return True
        elif response.status_code == 403:
            print_result(True, "Report deletion properly requires appropriate permissions (403 Forbidden)")
            return True
        else:
            print_result(False, f"Report deletion failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Report deletion failed with exception: {e}")
        return False

def test_analytics_authentication():
    """Test analytics endpoints without authentication"""
    print_test_header("Analytics Authentication Test")
    
    try:
        # Test analytics endpoints without auth
        endpoints = [
            "/analytics/user/performance",
            "/analytics/dashboard", 
            "/analytics/class",
            "/analytics/history"
        ]
        
        for endpoint in endpoints:
            response = requests.get(
                f"{API_BASE}{endpoint}",
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                print_result(True, f"{endpoint} properly requires authentication (status {response.status_code})")
            else:
                print_result(False, f"{endpoint} should return 401/403, got {response.status_code}")
                return False
        
        # Test POST endpoints
        post_endpoints = ["/analytics/snapshot"]
        
        for endpoint in post_endpoints:
            response = requests.post(
                f"{API_BASE}{endpoint}",
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                print_result(True, f"{endpoint} properly requires authentication (status {response.status_code})")
            else:
                print_result(False, f"{endpoint} should return 401/403, got {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Analytics authentication test failed with exception: {e}")
        return False

def test_reports_authentication():
    """Test reporting endpoints without authentication"""
    print_test_header("Reports Authentication Test")
    
    try:
        # Test GET endpoints without auth
        get_endpoints = [
            "/reports/templates",
            "/reports/educator"
        ]
        
        for endpoint in get_endpoints:
            response = requests.get(
                f"{API_BASE}{endpoint}",
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                print_result(True, f"{endpoint} properly requires authentication (status {response.status_code})")
            else:
                print_result(False, f"{endpoint} should return 401/403, got {response.status_code}")
                return False
        
        # Test POST endpoints without auth
        post_endpoints = [
            "/reports/student-progress",
            "/reports/class-performance", 
            "/reports/assessment-analysis"
        ]
        
        for endpoint in post_endpoints:
            response = requests.post(
                f"{API_BASE}{endpoint}",
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                print_result(True, f"{endpoint} properly requires authentication (status {response.status_code})")
            else:
                print_result(False, f"{endpoint} should return 401/403, got {response.status_code}")
                return False
        
        # Test DELETE endpoint without auth
        response = requests.delete(
            f"{API_BASE}/reports/test_report",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"/reports/{{report_id}} properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"/reports/{{report_id}} should return 401/403, got {response.status_code}")
            return False
        
    except Exception as e:
        print_result(False, f"Reports authentication test failed with exception: {e}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print(f"\n🚀 Starting PathwayIQ Backend API Tests")
    print(f"📅 Test run started at: {datetime.now().isoformat()}")
    print(f"🔗 Backend URL: {API_BASE}")
    
    test_results = {}
    
    # Run basic tests first
    test_results['health'] = test_health_endpoint()
    test_results['root'] = test_root_endpoint()
    test_results['api_keys'] = test_api_keys_configuration()
    
    # Authentication tests
    test_results['demo_login'] = test_demo_login()  # Use demo login for all tests
    test_results['database'] = test_database_connection()
    
    # PHASE 2: ANALYTICS AND REPORTING TESTS (MAIN FOCUS)
    print(f"\n{'='*60}")
    print("📊 PHASE 2: ANALYTICS AND REPORTING FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    # Analytics endpoints
    test_results['analytics_auth'] = test_analytics_authentication()
    test_results['analytics_user_performance'] = test_analytics_user_performance()
    test_results['analytics_dashboard'] = test_analytics_dashboard()
    test_results['analytics_class'] = test_analytics_class()
    test_results['analytics_snapshot'] = test_analytics_snapshot()
    test_results['analytics_history'] = test_analytics_history()
    
    # Reporting endpoints
    test_results['reports_auth'] = test_reports_authentication()
    test_results['reports_student_progress'] = test_reports_student_progress()
    test_results['reports_class_performance'] = test_reports_class_performance()
    test_results['reports_assessment_analysis'] = test_reports_assessment_analysis()
    test_results['reports_templates'] = test_reports_templates()
    test_results['reports_educator'] = test_reports_educator()
    test_results['reports_delete'] = test_reports_delete()
    
    # PHASE 2: COLLABORATION, PREDICTIVE, AND EMOTIONAL INTELLIGENCE TESTS
    print(f"\n{'='*60}")
    print("🤝 PHASE 2: COLLABORATION & SOCIAL LEARNING FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    # Collaboration endpoints
    test_results['collaboration_auth'] = test_collaboration_authentication()
    test_results['collaboration_create_group'] = test_collaboration_create_study_group()
    test_results['collaboration_user_groups'] = test_collaboration_get_user_groups()
    test_results['collaboration_search'] = test_collaboration_search_groups()
    test_results['collaboration_discussion'] = test_collaboration_create_discussion()
    
    print(f"\n{'='*60}")
    print("🔮 PHASE 2: PREDICTIVE ANALYTICS FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    # Predictive analytics endpoints
    test_results['predictive_auth'] = test_predictive_authentication()
    test_results['predictive_outcomes'] = test_predictive_learning_outcomes()
    test_results['predictive_risk'] = test_predictive_risk_assessment()
    test_results['predictive_skills'] = test_predictive_skill_mastery()
    
    print(f"\n{'='*60}")
    print("🧠 PHASE 2: EMOTIONAL INTELLIGENCE FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    # Emotional intelligence endpoints
    test_results['emotion_auth'] = test_emotion_authentication()
    test_results['emotion_analyze'] = test_emotion_analyze()
    test_results['emotion_empathetic'] = test_emotion_empathetic_response()
    test_results['emotion_journey'] = test_emotion_journey()
    test_results['emotion_profile'] = test_emotion_profile()
    
    # AI Content Generation tests (main focus of this testing session)
    print(f"\n{'='*60}")
    print("🤖 AI CONTENT GENERATION FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    test_results['content_auth'] = test_content_generation_authentication()
    test_results['content_types'] = test_content_generation_get_content_types()
    test_results['content_quiz'] = test_content_generation_quiz()
    test_results['content_lesson'] = test_content_generation_lesson()
    test_results['content_explanation'] = test_content_generation_explanation()
    test_results['content_user_content'] = test_content_generation_get_user_content()
    test_results['content_by_id'] = test_content_generation_get_content_by_id()
    test_results['content_regenerate'] = test_content_generation_regenerate()
    test_results['content_error_handling'] = test_content_generation_error_handling()
    
    # Speech-to-Text tests (previously tested)
    print(f"\n{'='*60}")
    print("🎤 SPEECH-TO-TEXT FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    test_results['stt_authentication'] = test_speech_to_text_authentication()
    test_results['stt_start_session'] = test_speech_to_text_start_session()
    test_results['stt_transcribe'] = test_speech_to_text_transcribe()
    test_results['stt_user_sessions'] = test_speech_to_text_get_user_sessions()
    test_results['stt_session_transcriptions'] = test_speech_to_text_session_transcriptions()
    test_results['stt_end_session'] = test_speech_to_text_end_session()
    test_results['stt_error_handling'] = test_speech_to_text_error_handling()
    
    # Additional tests
    test_results['adaptive_assessment'] = test_adaptive_assessment_start()
    test_results['ai_chat'] = test_enhanced_ai_chat()
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    # Group results by category
    basic_tests = ['health', 'root', 'api_keys', 'demo_login', 'database']
    analytics_tests = ['analytics_auth', 'analytics_user_performance', 'analytics_dashboard', 'analytics_class', 'analytics_snapshot', 'analytics_history']
    reporting_tests = ['reports_auth', 'reports_student_progress', 'reports_class_performance', 'reports_assessment_analysis', 'reports_templates', 'reports_educator', 'reports_delete']
    collaboration_tests = ['collaboration_auth', 'collaboration_create_group', 'collaboration_user_groups', 'collaboration_search', 'collaboration_discussion']
    predictive_tests = ['predictive_auth', 'predictive_outcomes', 'predictive_risk', 'predictive_skills']
    emotion_tests = ['emotion_auth', 'emotion_analyze', 'emotion_empathetic', 'emotion_journey', 'emotion_profile']
    content_tests = ['content_auth', 'content_types', 'content_quiz', 'content_lesson', 'content_explanation', 
                     'content_user_content', 'content_by_id', 'content_regenerate', 'content_error_handling']
    stt_tests = ['stt_authentication', 'stt_start_session', 'stt_transcribe', 'stt_user_sessions', 
                 'stt_session_transcriptions', 'stt_end_session', 'stt_error_handling']
    other_tests = ['adaptive_assessment', 'ai_chat']
    
    print("\n🔧 BASIC FUNCTIONALITY:")
    for test_name in basic_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print("\n📊 ANALYTICS FUNCTIONALITY (PHASE 2):")
    analytics_passed = 0
    for test_name in analytics_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('analytics_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                analytics_passed += 1
    
    print("\n📋 REPORTING FUNCTIONALITY (PHASE 2):")
    reporting_passed = 0
    for test_name in reporting_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('reports_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                reporting_passed += 1
    
    print("\n🤝 COLLABORATION FUNCTIONALITY (PHASE 2):")
    collaboration_passed = 0
    for test_name in collaboration_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('collaboration_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                collaboration_passed += 1
    
    print("\n🔮 PREDICTIVE ANALYTICS FUNCTIONALITY (PHASE 2):")
    predictive_passed = 0
    for test_name in predictive_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('predictive_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                predictive_passed += 1
    
    print("\n🧠 EMOTIONAL INTELLIGENCE FUNCTIONALITY (PHASE 2):")
    emotion_passed = 0
    for test_name in emotion_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('emotion_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                emotion_passed += 1
    
    print("\n🤖 AI CONTENT GENERATION FUNCTIONALITY:")
    content_passed = 0
    for test_name in content_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('content_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                content_passed += 1
    
    print("\n🎤 SPEECH-TO-TEXT FUNCTIONALITY:")
    stt_passed = 0
    for test_name in stt_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('stt_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                stt_passed += 1
    
    print("\n🧠 AI & ASSESSMENT FUNCTIONALITY:")
    for test_name in other_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    print(f"📊 Analytics Result: {analytics_passed}/{len(analytics_tests)} tests passed")
    print(f"📋 Reporting Result: {reporting_passed}/{len(reporting_tests)} tests passed")
    print(f"🤖 AI Content Generation Result: {content_passed}/{len(content_tests)} tests passed")
    print(f"🎤 Speech-to-Text Result: {stt_passed}/{len(stt_tests)} tests passed")
    
    # Calculate Phase 2 success rate
    phase2_passed = analytics_passed + reporting_passed
    phase2_total = len(analytics_tests) + len(reporting_tests)
    
    print(f"\n🎯 PHASE 2 SUCCESS RATE: {phase2_passed}/{phase2_total} ({phase2_passed/phase2_total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! PathwayIQ backend with Phase 2 Analytics & Reporting is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the details above.")
        
        # Specific feedback for Phase 2 features
        if phase2_passed < phase2_total:
            print(f"📊 Phase 2 Analytics & Reporting Status: {phase2_passed}/{phase2_total} tests passed")
            if phase2_passed == 0:
                print("❌ CRITICAL: Phase 2 Analytics & Reporting functionality is not working")
            elif phase2_passed < phase2_total // 2:
                print("⚠️  WARNING: Major issues with Phase 2 Analytics & Reporting functionality")
            else:
                print("⚠️  MINOR: Some Phase 2 Analytics & Reporting features have issues")
        
        # Specific feedback for AI content generation
        if content_passed < len(content_tests):
            print(f"🤖 AI Content Generation Status: {content_passed}/{len(content_tests)} tests passed")
            if content_passed == 0:
                print("❌ CRITICAL: AI Content Generation functionality is not working")
            elif content_passed < len(content_tests) // 2:
                print("⚠️  WARNING: Major issues with AI Content Generation functionality")
            else:
                print("⚠️  MINOR: Some AI Content Generation features have issues")
        
        # Specific feedback for speech-to-text
        if stt_passed < len(stt_tests):
            print(f"🎤 Speech-to-Text Status: {stt_passed}/{len(stt_tests)} tests passed")
            if stt_passed == 0:
                print("❌ CRITICAL: Speech-to-Text functionality is not working")
            elif stt_passed < len(stt_tests) // 2:
                print("⚠️  WARNING: Major issues with Speech-to-Text functionality")
            else:
                print("⚠️  MINOR: Some Speech-to-Text features have issues")
        
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)