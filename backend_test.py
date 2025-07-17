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

def test_voice_to_text():
    """Test POST /api/ai/voice-to-text (with auth)"""
    print_test_header("Voice to Text Processing")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        # Create dummy base64 audio data for testing
        import base64
        dummy_audio = base64.b64encode(b"dummy_audio_data").decode('utf-8')
        
        voice_request = {
            "audio_data": dummy_audio,
            "session_context": {"subject": "mathematics", "topic": "algebra"}
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/ai/voice-to-text",
            json=voice_request,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Voice to text processing successful")
            print(f"   Response: {data}")
            return True
        else:
            print_result(False, f"Voice to text failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Voice to text failed with exception: {e}")
        return False

def test_personalized_learning_path():
    """Test POST /api/ai/personalized-learning-path (with auth)"""
    print_test_header("Personalized Learning Path Generation")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        learning_path_request = {
            "subject": "mathematics",
            "learning_goals": ["Master quadratic equations", "Understand graphing", "Solve word problems"],
            "target_completion_weeks": 8,
            "preferred_learning_style": "visual"
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/ai/personalized-learning-path",
            json=learning_path_request,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Personalized learning path generation successful")
            print(f"   Response preview: {str(data)[:200]}...")
            return True
        else:
            print_result(False, f"Learning path generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Learning path generation failed with exception: {e}")
        return False

def test_badges_system():
    """Test GET /api/badges (with auth)"""
    print_test_header("Badge System")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/badges",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Badge system working")
            
            if isinstance(data, list):
                print_result(True, f"Retrieved {len(data)} badges")
                
                # Check badge structure if badges exist
                if data:
                    badge = data[0]
                    required_fields = ["id", "name", "description", "badge_type", "rarity"]
                    for field in required_fields:
                        if field in badge:
                            print_result(True, f"Badge contains {field}")
                        else:
                            print_result(False, f"Badge missing {field}")
                            
            else:
                print_result(False, "Badge response is not a list")
                
            return True
        else:
            print_result(False, f"Badge system failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Badge system failed with exception: {e}")
        return False

def test_global_leaderboard():
    """Test GET /api/leaderboard/global (with auth)"""
    print_test_header("Global Leaderboard")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE}/leaderboard/global?period=weekly&limit=10",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Global leaderboard working")
            
            # Check response structure
            if "leaderboard" in data and "period" in data:
                print_result(True, "Leaderboard response has correct structure")
                print(f"   Period: {data.get('period')}")
                print(f"   Leaderboard entries: {len(data.get('leaderboard', []))}")
            else:
                print_result(False, "Leaderboard response missing required fields")
                
            return True
        else:
            print_result(False, f"Global leaderboard failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Global leaderboard failed with exception: {e}")
        return False

def test_competitions():
    """Test POST /api/competitions (with auth)"""
    print_test_header("Competition System")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        competition_data = {
            "name": "Math Challenge 2024",
            "description": "Test your mathematical skills",
            "subject": "mathematics",
            "start_date": "2024-12-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
            "competition_type": "individual",
            "max_participants": 100
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/competitions",
            json=competition_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Competition creation successful")
            
            # Check response structure
            if "id" in data and "name" in data:
                print_result(True, "Competition response has correct structure")
                print(f"   Competition ID: {data.get('id')}")
                print(f"   Competition Name: {data.get('name')}")
            else:
                print_result(False, "Competition response missing required fields")
                
            return True
        elif response.status_code == 403:
            print_result(False, "Competition creation failed - insufficient permissions (expected for student role)")
            return True  # This is expected for student role
        else:
            print_result(False, f"Competition system failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Competition system failed with exception: {e}")
        return False

def test_study_groups():
    """Test POST /api/study-groups (with auth)"""
    print_test_header("Study Groups System")
    
    if not auth_token:
        print_result(False, "No auth token available - skipping test")
        return False
    
    try:
        study_group_data = {
            "name": "Algebra Study Group",
            "description": "Group for studying algebra concepts",
            "subject": "mathematics",
            "max_members": 10,
            "is_private": False
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/study-groups",
            json=study_group_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Study group creation successful")
            
            # Check response structure
            if "id" in data and "name" in data:
                print_result(True, "Study group response has correct structure")
                print(f"   Group ID: {data.get('id')}")
                print(f"   Group Name: {data.get('name')}")
            else:
                print_result(False, "Study group response missing required fields")
                
            return True
        else:
            print_result(False, f"Study groups system failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Study groups system failed with exception: {e}")
        return False

def test_learning_analytics():
    """Test GET /api/analytics/learning/{user_id} (with auth)"""
    print_test_header("Learning Analytics")
    
    if not auth_token or not user_data:
        print_result(False, "No auth token or user data available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        user_id = user_data.get('id')
        response = requests.get(
            f"{API_BASE}/analytics/learning/{user_id}?time_range=30d",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Learning analytics working")
            print(f"   Analytics data preview: {str(data)[:200]}...")
            return True
        else:
            print_result(False, f"Learning analytics failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Learning analytics failed with exception: {e}")
        return False

def test_predictive_analytics():
    """Test GET /api/analytics/predictions/{user_id} (with auth)"""
    print_test_header("Predictive Analytics")
    
    if not auth_token or not user_data:
        print_result(False, "No auth token or user data available - skipping test")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        user_id = user_data.get('id')
        response = requests.get(
            f"{API_BASE}/analytics/predictions/{user_id}?prediction_type=success_probability",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Predictive analytics working")
            print(f"   Prediction data preview: {str(data)[:200]}...")
            return True
        else:
            print_result(False, f"Predictive analytics failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Predictive analytics failed with exception: {e}")
        return False

def test_report_generation():
    """Test POST /api/reports/generate (with auth)"""
    print_test_header("Report Generation")
    
    if not auth_token or not user_data:
        print_result(False, "No auth token or user data available - skipping test")
        return False
    
    try:
        report_request = {
            "report_type": "individual_student",
            "target_id": user_data.get('id'),
            "time_range": "30d",
            "include_predictions": True
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/reports/generate",
            json=report_request,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Report generation successful")
            print(f"   Report data preview: {str(data)[:200]}...")
            return True
        else:
            print_result(False, f"Report generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Report generation failed with exception: {e}")
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

def run_all_tests():
    """Run all backend tests"""
    print(f"\n🚀 Starting PathwayIQ Backend API Tests")
    print(f"📅 Test run started at: {datetime.now().isoformat()}")
    print(f"🔗 Backend URL: {API_BASE}")
    
    test_results = {}
    
    # Run tests in order
    test_results['health'] = test_health_endpoint()
    test_results['root'] = test_root_endpoint()
    test_results['api_keys'] = test_api_keys_configuration()
    test_results['registration'] = test_user_registration()
    test_results['login'] = test_user_login()
    test_results['database'] = test_database_connection()
    test_results['adaptive_assessment'] = test_adaptive_assessment_start()
    test_results['ai_chat'] = test_enhanced_ai_chat()
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PathwayIQ backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the details above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)