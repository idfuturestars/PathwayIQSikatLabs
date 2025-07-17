#!/usr/bin/env python3
"""
TIER 1 CRITICAL: PathwayIQ Backend Authentication Testing Suite
Tests authentication system with demo credentials as requested in review
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

def test_backend_accessibility():
    """Test if backend is accessible"""
    print_test_header("TIER 1 CRITICAL: Backend Accessibility")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Backend is accessible")
            print(f"   Response: {data}")
            
            if "status" in data and data["status"] == "healthy":
                print_result(True, "Backend health status is 'healthy'")
            else:
                print_result(False, "Backend health status is not 'healthy'", data)
                
            return True
        else:
            print_result(False, f"Backend accessibility failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Backend accessibility failed with exception: {e}")
        print("🔍 DIAGNOSIS: Backend server is not responding or network connectivity issue")
        return False

def test_login_endpoint_exists():
    """Test if login endpoint exists"""
    print_test_header("TIER 1 CRITICAL: Login Endpoint Existence")
    
    try:
        # Test with invalid data to see if endpoint exists
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": "test", "password": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # Any response other than 404 means endpoint exists
        if response.status_code != 404:
            print_result(True, f"Login endpoint exists (status: {response.status_code})")
            return True
        else:
            print_result(False, "Login endpoint not found (404)")
            print("🔍 DIAGNOSIS: /api/auth/login endpoint is not configured")
            return False
            
    except Exception as e:
        print_result(False, f"Login endpoint test failed with exception: {e}")
        return False

def test_demo_login():
    """Test POST /api/auth/login with demo credentials - TIER 1 CRITICAL TEST"""
    print_test_header("TIER 1 CRITICAL: Demo Login Test")
    global auth_token, user_data
    
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
                print("🔧 SOLUTION: Create demo user in database with email 'demo@idfs-pathwayiq.com' and password 'demo123'")
            elif response.status_code == 404:
                print("🔍 DIAGNOSIS: Login endpoint not found - check API routing")
                print("🔧 SOLUTION: Verify /api/auth/login endpoint is properly configured in backend")
            elif response.status_code == 500:
                print("🔍 DIAGNOSIS: Server error - check database connection and backend logs")
                print("🔧 SOLUTION: Check MongoDB connection and backend server logs")
            
            return False
            
    except Exception as e:
        print_result(False, f"Demo login failed with exception: {e}")
        print("🔍 DIAGNOSIS: Network connectivity issue or backend server not responding")
        return False

def test_jwt_token_validation():
    """Test JWT token validation and user session management"""
    print_test_header("TIER 1 CRITICAL: JWT Token Validation")
    
    if not auth_token:
        print_result(False, "No auth token available - demo login must succeed first")
        return False
    
    try:
        # Test accessing protected endpoint with token
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
            print_result(True, "JWT token validation successful")
            
            # Verify user data consistency
            if data.get("id") == user_data.get("id"):
                print_result(True, "User session data consistency verified")
            else:
                print_result(False, "User session data inconsistency detected")
                
            # Test token format
            token_parts = auth_token.split('.')
            if len(token_parts) == 3:
                print_result(True, "JWT token has correct 3-part structure")
            else:
                print_result(False, f"JWT token has incorrect structure: {len(token_parts)} parts")
            
            return True
        elif response.status_code == 401:
            print_result(False, "JWT token validation failed - token is invalid or expired")
            print("🔍 DIAGNOSIS: JWT token is not being validated properly")
            return False
        else:
            print_result(False, f"JWT validation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"JWT validation failed with exception: {e}")
        return False

def test_database_connectivity():
    """Test database connectivity through user data retrieval"""
    print_test_header("TIER 1 CRITICAL: Database Connectivity")
    
    if not auth_token:
        print_result(False, "No auth token available - cannot test database connectivity")
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
            print_result(True, "Database connectivity working - user data retrieved")
            
            # Verify data consistency
            if data.get("id") == user_data.get("id"):
                print_result(True, "Database data consistency verified")
            else:
                print_result(False, "Database data inconsistency detected")
                
            if data.get("email") == user_data.get("email"):
                print_result(True, "Email consistency verified in database")
            else:
                print_result(False, "Email mismatch in database")
                
            return True
        else:
            print_result(False, f"Database connectivity test failed with status {response.status_code}", response.text)
            print("🔍 DIAGNOSIS: Database connection issue or user data not found")
            return False
            
    except Exception as e:
        print_result(False, f"Database connectivity test failed with exception: {e}")
        return False

def test_invalid_login_credentials():
    """Test login with invalid credentials to verify error handling"""
    print_test_header("TIER 1 CRITICAL: Invalid Credentials Handling")
    
    try:
        # Test with invalid credentials
        invalid_login_data = {
            "email": "nonexistent@pathwayiq.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=invalid_login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 401:
            print_result(True, "Invalid credentials properly rejected with 401 status")
            
            # Check error message
            try:
                error_data = response.json()
                if "detail" in error_data:
                    print_result(True, f"Error message provided: {error_data['detail']}")
                else:
                    print_result(False, "No error detail provided in response")
            except:
                print_result(False, "Error response is not valid JSON")
                
            return True
        else:
            print_result(False, f"Invalid credentials should return 401, got {response.status_code}")
            print("🔍 DIAGNOSIS: Authentication error handling is not working properly")
            return False
            
    except Exception as e:
        print_result(False, f"Invalid login test failed with exception: {e}")
        return False

def test_user_session_management():
    """Test user session management with multiple requests"""
    print_test_header("TIER 1 CRITICAL: User Session Management")
    
    if not auth_token:
        print_result(False, "No auth token available - cannot test session management")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Make multiple requests to test session persistence
        for i in range(3):
            response = requests.get(
                f"{API_BASE}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print_result(False, f"Session management failed on request {i+1}")
                return False
        
        print_result(True, "User session management working - multiple requests successful")
        return True
        
    except Exception as e:
        print_result(False, f"Session management test failed with exception: {e}")
        return False

def run_critical_authentication_tests():
    """Run critical authentication tests in priority order"""
    print(f"\n🚨 TIER 1 CRITICAL: PathwayIQ Authentication System Diagnosis")
    print(f"📅 Test run started at: {datetime.now().isoformat()}")
    print(f"🔗 Backend URL: {API_BASE}")
    print(f"🎯 Target: Demo credentials demo@idfs-pathwayiq.com / demo123")
    
    test_results = {}
    
    # Run tests in critical priority order
    test_results['backend_accessibility'] = test_backend_accessibility()
    test_results['login_endpoint_exists'] = test_login_endpoint_exists()
    test_results['demo_login'] = test_demo_login()
    test_results['jwt_validation'] = test_jwt_token_validation()
    test_results['database_connectivity'] = test_database_connectivity()
    test_results['invalid_credentials'] = test_invalid_login_credentials()
    test_results['session_management'] = test_user_session_management()
    
    # Print summary
    print(f"\n{'='*60}")
    print("🚨 TIER 1 CRITICAL TEST RESULTS")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    # Critical analysis
    if test_results.get('demo_login', False):
        print("🎉 TIER 1 CRITICAL SUCCESS: Demo login is working!")
        print("✅ Authentication system is functional")
        print("✅ JWT token generation is working")
        print("✅ Database connectivity is established")
    else:
        print("🚨 TIER 1 CRITICAL FAILURE: Demo login is NOT working!")
        
        if not test_results.get('backend_accessibility', False):
            print("❌ ROOT CAUSE: Backend server is not accessible")
        elif not test_results.get('login_endpoint_exists', False):
            print("❌ ROOT CAUSE: Login endpoint is not configured")
        else:
            print("❌ ROOT CAUSE: Demo user credentials are invalid or user doesn't exist")
    
    return passed == total

if __name__ == "__main__":
    success = run_critical_authentication_tests()
    sys.exit(0 if success else 1)