#!/usr/bin/env python3
"""
PathwayIQ Backend API Testing Suite
Tests all backend endpoints and verifies PathwayIQ branding
"""

import requests
import json
import os
import sys
from datetime import datetime
import uuid
import base64

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

def test_user_login():
    """Test POST /api/auth/login"""
    print_test_header("User Login")
    
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
        
        # Verify database name is pathwayiq_database
        if 'DB_NAME="pathwayiq_database"' in env_content:
            print_result(True, "Database name is correctly set to 'pathwayiq_database'")
        else:
            print_result(False, "Database name is not set to 'pathwayiq_database'")
            
        return True
        
    except Exception as e:
        print_result(False, f"API keys configuration test failed: {e}")
        return False

def test_voice_to_text_processing():
    """Test POST /api/ai/voice-to-text - Voice processing with base64 encoded audio data"""
    print_test_header("Voice-to-Text Processing")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        # Create a simple base64 encoded audio data (mock)
        # In real scenario, this would be actual audio data
        mock_audio_data = base64.b64encode(b"mock_audio_data_for_testing").decode('utf-8')
        
        # Test with over-18 user (no parental consent needed)
        voice_request = {
            "audio_data": mock_audio_data,
            "session_context": {
                "assessment_type": "diagnostic",
                "subject": "mathematics"
            },
            "user_age": 25,
            "parental_consent": None
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/ai/voice-to-text",
            json=voice_request,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Voice-to-text processing successful for over-18 user")
            
            # Check response structure
            expected_fields = ["transcribed_text", "emotional_state", "learning_style", "confidence_score", "think_aloud_quality"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Response contains {field}: {data.get(field)}")
                else:
                    print_result(False, f"Response missing {field}")
            
            return True
        else:
            print_result(False, f"Voice-to-text processing failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Voice-to-text processing failed with exception: {e}")
        return False

def test_voice_think_aloud():
    """Test POST /api/ai/voice-think-aloud - Think-aloud specific voice processing"""
    print_test_header("Voice Think-Aloud Processing")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        # Create a simple base64 encoded audio data (mock)
        mock_audio_data = base64.b64encode(b"mock_think_aloud_audio_data").decode('utf-8')
        
        think_aloud_request = {
            "audio_data": mock_audio_data,
            "question_id": "test_question_123",
            "session_id": "test_session_456",
            "user_age": 20,
            "parental_consent": None
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/ai/voice-think-aloud",
            json=think_aloud_request,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Voice think-aloud processing successful")
            
            # Check response structure
            expected_fields = ["transcribed_text", "emotional_state", "learning_style", "confidence_score", "think_aloud_quality"]
            for field in expected_fields:
                if field in data:
                    print_result(True, f"Think-aloud response contains {field}: {data.get(field)}")
                else:
                    print_result(False, f"Think-aloud response missing {field}")
            
            return True
        else:
            print_result(False, f"Voice think-aloud processing failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Voice think-aloud processing failed with exception: {e}")
        return False

def test_gdpr_consent_verification():
    """Test POST /api/ai/consent-verification - GDPR compliance for under-18 users"""
    print_test_header("GDPR Consent Verification")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Under-18 user with parental consent
        consent_request_with_consent = {
            "user_age": 16,
            "parental_consent": True,
            "parent_email": "parent@example.com",
            "consent_timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{API_BASE}/ai/consent-verification",
            json=consent_request_with_consent,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "GDPR consent verification successful for under-18 with consent")
            
            if data.get("can_process_voice") == True:
                print_result(True, "Voice processing allowed with parental consent")
            else:
                print_result(False, "Voice processing not allowed despite parental consent")
        else:
            print_result(False, f"GDPR consent verification failed with status {response.status_code}", response.text)
            return False
        
        # Test 2: Under-18 user without parental consent (should fail)
        consent_request_no_consent = {
            "user_age": 15,
            "parental_consent": False,
            "parent_email": None
        }
        
        response = requests.post(
            f"{API_BASE}/ai/consent-verification",
            json=consent_request_no_consent,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 400:
            print_result(True, "GDPR correctly blocks under-18 users without parental consent")
        else:
            print_result(False, f"GDPR should have blocked under-18 user without consent, got status {response.status_code}")
        
        # Test 3: Over-18 user (should always work)
        consent_request_adult = {
            "user_age": 25,
            "parental_consent": False
        }
        
        response = requests.post(
            f"{API_BASE}/ai/consent-verification",
            json=consent_request_adult,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "GDPR consent verification successful for over-18 user")
            
            if data.get("can_process_voice") == True:
                print_result(True, "Voice processing allowed for adult user")
            else:
                print_result(False, "Voice processing should be allowed for adult user")
        else:
            print_result(False, f"GDPR consent verification failed for adult user with status {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"GDPR consent verification failed with exception: {e}")
        return False

def test_voice_processing_with_gdpr():
    """Test voice processing endpoints with GDPR compliance scenarios"""
    print_test_header("Voice Processing with GDPR Compliance")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        mock_audio_data = base64.b64encode(b"mock_audio_for_gdpr_test").decode('utf-8')
        
        # Test 1: Under-18 user without parental consent (should fail)
        voice_request_no_consent = {
            "audio_data": mock_audio_data,
            "session_context": {"test": "gdpr"},
            "user_age": 16,
            "parental_consent": False
        }
        
        response = requests.post(
            f"{API_BASE}/ai/voice-to-text",
            json=voice_request_no_consent,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 403:
            print_result(True, "Voice processing correctly blocked for under-18 without consent")
        else:
            print_result(False, f"Voice processing should be blocked for under-18 without consent, got status {response.status_code}")
        
        # Test 2: Under-18 user with parental consent (should work)
        voice_request_with_consent = {
            "audio_data": mock_audio_data,
            "session_context": {"test": "gdpr"},
            "user_age": 17,
            "parental_consent": True
        }
        
        response = requests.post(
            f"{API_BASE}/ai/voice-to-text",
            json=voice_request_with_consent,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            print_result(True, "Voice processing allowed for under-18 with parental consent")
        else:
            print_result(False, f"Voice processing should work for under-18 with consent, got status {response.status_code}")
        
        return True
        
    except Exception as e:
        print_result(False, f"Voice processing GDPR test failed with exception: {e}")
        return False

def test_adaptive_assessment_next_question():
    """Test GET /api/adaptive-assessment/{session_id}/next-question"""
    print_test_header("Adaptive Assessment Next Question")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # First start an assessment to get a session ID
        assessment_config = {
            "subject": "mathematics",
            "target_grade_level": "grade_8",
            "assessment_type": "diagnostic",
            "enable_think_aloud": True,
            "enable_ai_help_tracking": True,
            "max_questions": 5
        }
        
        start_response = requests.post(
            f"{API_BASE}/adaptive-assessment/start",
            json=assessment_config,
            headers=headers,
            timeout=10
        )
        
        if start_response.status_code != 200:
            print_result(False, "Could not start assessment session for next question test")
            return False
        
        session_data = start_response.json()
        session_id = session_data.get("session_id")
        
        if not session_id:
            print_result(False, "No session ID returned from assessment start")
            return False
        
        # Now test getting the next question
        response = requests.get(
            f"{API_BASE}/adaptive-assessment/{session_id}/next-question",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Next question retrieval successful")
            
            # Check if it's a question or session complete
            if data.get("session_complete"):
                print_result(True, "Session marked as complete (no more questions)")
            else:
                # Check question structure
                expected_fields = ["id", "question_text", "question_type", "options", "think_aloud_prompts"]
                for field in expected_fields:
                    if field in data:
                        print_result(True, f"Question contains {field}")
                    else:
                        print_result(False, f"Question missing {field}")
                
                print(f"   Question ID: {data.get('id')}")
                print(f"   Question Type: {data.get('question_type')}")
                print(f"   Current Ability: {data.get('current_ability_estimate')}")
            
            return True
        else:
            print_result(False, f"Next question retrieval failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Next question retrieval failed with exception: {e}")
        return False

def test_openai_api_key_configuration():
    """Test OpenAI API key configuration for voice processing"""
    print_test_header("OpenAI API Key Configuration")
    
    try:
        # Check if OpenAI API key is configured
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
        
        if 'OPENAI_API_KEY=' in env_content:
            for line in env_content.split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"')
                    if api_key and api_key.startswith('sk-') and len(api_key) > 20:
                        print_result(True, "OpenAI API key is properly configured")
                        print(f"   Key prefix: {api_key[:10]}...")
                        return True
                    else:
                        print_result(False, "OpenAI API key appears to be invalid or empty")
                        return False
        else:
            print_result(False, "OpenAI API key not found in configuration")
            return False
            
    except Exception as e:
        print_result(False, f"OpenAI API key configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print(f"\n🚀 Starting IDFS PathwayIQ™ Backend API Tests")
    print(f"📅 Test run started at: {datetime.now().isoformat()}")
    print(f"🔗 Backend URL: {API_BASE}")
    
    test_results = {}
    
    # Run basic tests first
    test_results['health'] = test_health_endpoint()
    test_results['root'] = test_root_endpoint()
    test_results['api_keys'] = test_api_keys_configuration()
    test_results['openai_key'] = test_openai_api_key_configuration()
    test_results['registration'] = test_user_registration()
    test_results['login'] = test_user_login()
    test_results['database'] = test_database_connection()
    
    # Run adaptive assessment tests
    test_results['adaptive_assessment_start'] = test_adaptive_assessment_start()
    test_results['adaptive_assessment_next'] = test_adaptive_assessment_next_question()
    
    # Run voice processing tests (main focus)
    test_results['voice_to_text'] = test_voice_to_text_processing()
    test_results['voice_think_aloud'] = test_voice_think_aloud()
    test_results['gdpr_consent'] = test_gdpr_consent_verification()
    test_results['voice_gdpr_compliance'] = test_voice_processing_with_gdpr()
    
    # Run AI chat test
    test_results['ai_chat'] = test_enhanced_ai_chat()
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 VOICE-TO-TEXT PROCESSING TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    # Categorize results
    voice_tests = ['voice_to_text', 'voice_think_aloud', 'gdpr_consent', 'voice_gdpr_compliance']
    assessment_tests = ['adaptive_assessment_start', 'adaptive_assessment_next']
    basic_tests = ['health', 'root', 'api_keys', 'openai_key', 'registration', 'login', 'database', 'ai_chat']
    
    print("\n🎤 VOICE PROCESSING TESTS:")
    for test_name in voice_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print("\n📊 ADAPTIVE ASSESSMENT TESTS:")
    for test_name in assessment_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print("\n🔧 BASIC FUNCTIONALITY TESTS:")
    for test_name in basic_tests:
        if test_name in test_results:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    # Check critical voice processing functionality
    voice_passed = sum(1 for test in voice_tests if test_results.get(test, False))
    voice_total = len(voice_tests)
    
    if voice_passed == voice_total:
        print("🎉 All voice processing tests passed! Voice-to-text functionality is working correctly.")
    else:
        print(f"⚠️  Voice processing tests: {voice_passed}/{voice_total} passed. Some voice features may not be working.")
    
    if passed == total:
        print("🎉 All tests passed! IDFS PathwayIQ™ backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the details above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)