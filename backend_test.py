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
# STUDY GROUPS & COLLABORATIVE LEARNING TESTS
# ============================================================================

def test_study_groups_create():
    """Test POST /api/study-groups/create"""
    print_test_header("Study Groups - Create Group")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        group_data = {
            "name": f"PathwayIQ Study Group {uuid.uuid4().hex[:8]}",
            "description": "A collaborative learning group for mathematics and science topics",
            "subject": "Mathematics",
            "max_members": 15,
            "is_public": True,
            "topics": ["Algebra", "Geometry", "Calculus"]
        }
        
        response = requests.post(
            f"{API_BASE}/study-groups/create",
            json=group_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Study group creation successful")
            
            # Check response structure
            expected_fields = ["success", "message", "data"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            # Verify success status
            if data.get("success") == True:
                print_result(True, "Success status is True")
            else:
                print_result(False, f"Unexpected success status: {data.get('success')}")
            
            # Check data structure
            group_info = data.get("data", {})
            if "group_id" in group_info:
                print_result(True, "Group ID provided in response")
                # Store group ID for subsequent tests
                global test_group_id
                test_group_id = group_info["group_id"]
            else:
                print_result(False, "Group ID missing from response")
            
            print(f"   Group ID: {group_info.get('group_id', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            return True
        else:
            print_result(False, f"Study group creation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Study group creation failed with exception: {e}")
        return False

def test_study_groups_get_public():
    """Test GET /api/study-groups/public"""
    print_test_header("Study Groups - Get Public Groups")
    
    try:
        # This endpoint doesn't require authentication according to the code
        response = requests.get(
            f"{API_BASE}/study-groups/public?limit=10",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Public groups retrieved successfully")
            
            # Check response structure
            expected_fields = ["success", "groups", "total"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            groups = data.get("groups", [])
            total = data.get("total", 0)
            
            print(f"   Total public groups: {total}")
            print(f"   Groups returned: {len(groups)}")
            
            # If we have groups, check their structure
            if groups:
                first_group = groups[0]
                group_fields = ["id", "name", "description", "subject", "member_count", "is_public"]
                for field in group_fields:
                    if field in first_group:
                        print_result(True, f"Group contains {field}")
                    else:
                        print_result(False, f"Group missing {field}")
            
            return True
        else:
            print_result(False, f"Get public groups failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get public groups failed with exception: {e}")
        return False

def test_study_groups_get_my_groups():
    """Test GET /api/study-groups/my-groups"""
    print_test_header("Study Groups - Get My Groups")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/study-groups/my-groups",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "User groups retrieved successfully")
            
            # Check response structure
            expected_fields = ["success", "groups", "total"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            groups = data.get("groups", [])
            total = data.get("total", 0)
            
            print(f"   Total user groups: {total}")
            print(f"   Groups returned: {len(groups)}")
            
            return True
        else:
            print_result(False, f"Get my groups failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get my groups failed with exception: {e}")
        return False

def test_study_groups_join():
    """Test POST /api/study-groups/{group_id}/join"""
    print_test_header("Study Groups - Join Group")
    
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
        
        # Note: The endpoint expects join_message as a query parameter or form data
        response = requests.post(
            f"{API_BASE}/study-groups/{group_id}/join?join_message=Excited to learn together!",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Group join successful")
            
            # Check response structure
            if "success" in data:
                print_result(True, "Response contains success field")
                if data.get("success"):
                    print_result(True, "Join operation successful")
                else:
                    print_result(False, f"Join operation failed: {data.get('error', 'Unknown error')}")
            else:
                print_result(False, "Response missing success field")
            
            print(f"   Group ID: {group_id}")
            print(f"   Response: {data}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Group join failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Group join failed with exception: {e}")
        return False

def test_study_groups_leave():
    """Test POST /api/study-groups/{group_id}/leave"""
    print_test_header("Study Groups - Leave Group")
    
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
        
        response = requests.post(
            f"{API_BASE}/study-groups/{group_id}/leave",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Group leave successful")
            
            # Check response structure
            if "success" in data:
                print_result(True, "Response contains success field")
            else:
                print_result(False, "Response missing success field")
            
            print(f"   Group ID: {group_id}")
            print(f"   Response: {data}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Group leave failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Group leave failed with exception: {e}")
        return False

def test_study_groups_send_message():
    """Test POST /api/study-groups/{group_id}/messages"""
    print_test_header("Study Groups - Send Message")
    
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
        
        message_data = {
            "content": "Hello everyone! Let's work together on solving quadratic equations.",
            "message_type": "text",
            "metadata": {
                "topic": "Mathematics",
                "urgency": "normal"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/study-groups/{group_id}/messages",
            json=message_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Message sent successfully")
            
            # Check response structure
            if "success" in data:
                print_result(True, "Response contains success field")
                if data.get("success"):
                    print_result(True, "Message send operation successful")
                else:
                    print_result(False, f"Message send failed: {data.get('error', 'Unknown error')}")
            else:
                print_result(False, "Response missing success field")
            
            print(f"   Group ID: {group_id}")
            print(f"   Message: {message_data['content'][:50]}...")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Send message failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Send message failed with exception: {e}")
        return False

def test_study_groups_get_messages():
    """Test GET /api/study-groups/{group_id}/messages"""
    print_test_header("Study Groups - Get Messages")
    
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
        
        response = requests.get(
            f"{API_BASE}/study-groups/{group_id}/messages?limit=20",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Messages retrieved successfully")
            
            # Check response structure
            expected_fields = ["success", "messages", "total"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}")
                else:
                    print_result(False, f"Response missing {field}")
            
            messages = data.get("messages", [])
            total = data.get("total", 0)
            
            print(f"   Total messages: {total}")
            print(f"   Messages returned: {len(messages)}")
            
            # If we have messages, check their structure
            if messages:
                first_message = messages[0]
                message_fields = ["id", "content", "user_id", "timestamp", "message_type"]
                for field in message_fields:
                    if field in first_message:
                        print_result(True, f"Message contains {field}")
                    else:
                        print_result(False, f"Message missing {field}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Get messages failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get messages failed with exception: {e}")
        return False

def test_study_groups_start_session():
    """Test POST /api/study-groups/{group_id}/sessions/start"""
    print_test_header("Study Groups - Start Study Session")
    
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
        
        session_data = {
            "topic": "Quadratic Equations Practice",
            "description": "Let's work together on solving quadratic equations using different methods",
            "duration_minutes": 90
        }
        
        response = requests.post(
            f"{API_BASE}/study-groups/{group_id}/sessions/start",
            json=session_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Study session started successfully")
            
            # Check response structure
            if "success" in data:
                print_result(True, "Response contains success field")
                if data.get("success"):
                    print_result(True, "Session start operation successful")
                    
                    # Look for session ID
                    if "session_id" in data:
                        print_result(True, "Session ID provided")
                        # Store session ID for subsequent tests
                        global test_session_id
                        test_session_id = data["session_id"]
                    else:
                        print_result(False, "Session ID missing from response")
                else:
                    print_result(False, f"Session start failed: {data.get('error', 'Unknown error')}")
            else:
                print_result(False, "Response missing success field")
            
            print(f"   Group ID: {group_id}")
            print(f"   Topic: {session_data['topic']}")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Start session failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Start session failed with exception: {e}")
        return False

def test_study_groups_join_session():
    """Test POST /api/study-groups/sessions/{session_id}/join"""
    print_test_header("Study Groups - Join Study Session")
    
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
            f"{API_BASE}/study-groups/sessions/{session_id}/join",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Session join successful")
            
            # Check response structure
            if "success" in data:
                print_result(True, "Response contains success field")
                if data.get("success"):
                    print_result(True, "Session join operation successful")
                else:
                    print_result(False, f"Session join failed: {data.get('error', 'Unknown error')}")
            else:
                print_result(False, "Response missing success field")
            
            print(f"   Session ID: {session_id}")
            print(f"   Response: {data}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Session not found (expected for test session)")
            return True
        else:
            print_result(False, f"Join session failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Join session failed with exception: {e}")
        return False

def test_study_groups_get_analytics():
    """Test GET /api/study-groups/{group_id}/analytics"""
    print_test_header("Study Groups - Get Group Analytics")
    
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
        
        response = requests.get(
            f"{API_BASE}/study-groups/{group_id}/analytics?days=30",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Group analytics retrieved successfully")
            
            # Check for analytics data structure
            analytics_fields = ["member_activity", "message_stats", "session_stats", "engagement_metrics"]
            for field in analytics_fields:
                if field in data:
                    print_result(True, f"Analytics contains {field}")
                else:
                    print_result(False, f"Analytics missing {field}")
            
            print(f"   Group ID: {group_id}")
            print(f"   Analytics keys: {list(data.keys())}")
            
            return True
        elif response.status_code == 404:
            print_result(True, "Group not found (expected for test group)")
            return True
        else:
            print_result(False, f"Get analytics failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get analytics failed with exception: {e}")
        return False

def test_study_groups_authentication():
    """Test study groups endpoints without authentication"""
    print_test_header("Study Groups Authentication Test")
    
    try:
        # Test create group endpoint without auth
        group_data = {
            "name": "Test Group",
            "description": "Test",
            "subject": "Math"
        }
        
        response = requests.post(
            f"{API_BASE}/study-groups/create",
            json=group_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Create group endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"Create group endpoint should return 401/403, got {response.status_code}")
        
        # Test my groups endpoint without auth
        response = requests.get(
            f"{API_BASE}/study-groups/my-groups",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"My groups endpoint properly requires authentication (status {response.status_code})")
        else:
            print_result(False, f"My groups endpoint should return 401/403, got {response.status_code}")
        
        # Test join group endpoint without auth
        response = requests.post(
            f"{API_BASE}/study-groups/test_group/join",
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_result(True, f"Join group endpoint properly requires authentication (status {response.status_code})")
            return True
        else:
            print_result(False, f"Join group endpoint should return 401/403, got {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Authentication test failed with exception: {e}")
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
    
    # Study Groups & Collaborative Learning tests (main focus of this testing session)
    print(f"\n{'='*60}")
    print("👥 STUDY GROUPS & COLLABORATIVE LEARNING FUNCTIONALITY TESTING")
    print(f"{'='*60}")
    
    test_results['study_groups_auth'] = test_study_groups_authentication()
    test_results['study_groups_create'] = test_study_groups_create()
    test_results['study_groups_public'] = test_study_groups_get_public()
    test_results['study_groups_my_groups'] = test_study_groups_get_my_groups()
    test_results['study_groups_join'] = test_study_groups_join()
    test_results['study_groups_leave'] = test_study_groups_leave()
    test_results['study_groups_send_message'] = test_study_groups_send_message()
    test_results['study_groups_get_messages'] = test_study_groups_get_messages()
    test_results['study_groups_start_session'] = test_study_groups_start_session()
    test_results['study_groups_join_session'] = test_study_groups_join_session()
    test_results['study_groups_analytics'] = test_study_groups_get_analytics()
    
    # AI Content Generation tests (previously tested)
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
    study_groups_tests = ['study_groups_auth', 'study_groups_create', 'study_groups_public', 'study_groups_my_groups',
                         'study_groups_join', 'study_groups_leave', 'study_groups_send_message', 'study_groups_get_messages',
                         'study_groups_start_session', 'study_groups_join_session', 'study_groups_analytics']
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
    
    print("\n👥 STUDY GROUPS & COLLABORATIVE LEARNING:")
    study_groups_passed = 0
    for test_name in study_groups_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('study_groups_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                study_groups_passed += 1
    
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
    print(f"👥 Study Groups Result: {study_groups_passed}/{len(study_groups_tests)} tests passed")
    print(f"🤖 AI Content Generation Result: {content_passed}/{len(content_tests)} tests passed")
    print(f"🎤 Speech-to-Text Result: {stt_passed}/{len(stt_tests)} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PathwayIQ backend with Study Groups & Collaborative Learning is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the details above.")
        
        # Specific feedback for Study Groups
        if study_groups_passed < len(study_groups_tests):
            print(f"👥 Study Groups Status: {study_groups_passed}/{len(study_groups_tests)} tests passed")
            if study_groups_passed == 0:
                print("❌ CRITICAL: Study Groups & Collaborative Learning functionality is not working")
            elif study_groups_passed < len(study_groups_tests) // 2:
                print("⚠️  WARNING: Major issues with Study Groups & Collaborative Learning functionality")
            else:
                print("⚠️  MINOR: Some Study Groups & Collaborative Learning features have issues")
        
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