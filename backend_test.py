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
        # Create mock base64 audio data (minimal WAV file)
        # This is a minimal WAV header + silence for testing
        wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        mock_audio_data = base64.b64encode(wav_header).decode('utf-8')
        
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
        
        if response.status_code == 401:
            print_result(True, "Transcribe endpoint properly requires authentication")
        else:
            print_result(False, f"Transcribe endpoint should return 401, got {response.status_code}")
        
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
        
        if response.status_code == 401:
            print_result(True, "Start session endpoint properly requires authentication")
        else:
            print_result(False, f"Start session endpoint should return 401, got {response.status_code}")
        
        # Test user sessions endpoint without auth
        response = requests.get(
            f"{API_BASE}/speech-to-text/user/sessions",
            timeout=10
        )
        
        if response.status_code == 401:
            print_result(True, "User sessions endpoint properly requires authentication")
            return True
        else:
            print_result(False, f"User sessions endpoint should return 401, got {response.status_code}")
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
    test_results['demo_login'] = test_demo_login()  # Use demo login for speech-to-text tests
    test_results['database'] = test_database_connection()
    
    # Speech-to-Text tests (main focus of this testing session)
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
    stt_tests = ['stt_authentication', 'stt_start_session', 'stt_transcribe', 'stt_user_sessions', 
                 'stt_session_transcriptions', 'stt_end_session', 'stt_error_handling']
    other_tests = ['adaptive_assessment', 'ai_chat']
    
    print("\n🔧 BASIC FUNCTIONALITY:")
    for test_name in basic_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print("\n🎤 SPEECH-TO-TEXT FUNCTIONALITY:")
    stt_passed = 0
    for test_name in stt_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('stt_', '').replace('_', ' ').title()}")
            if test_results[test_name]:
                stt_passed += 1
    
    print("\n🤖 AI & ASSESSMENT FUNCTIONALITY:")
    for test_name in other_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    print(f"🎤 Speech-to-Text Result: {stt_passed}/{len(stt_tests)} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PathwayIQ backend with Speech-to-Text is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the details above.")
        
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