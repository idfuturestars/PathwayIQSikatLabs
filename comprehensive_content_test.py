#!/usr/bin/env python3
"""
Comprehensive AI Content Generation Testing
Tests all content generation endpoints with proper timeouts
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
API_BASE = f"{BACKEND_URL}/api"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    status = "✅" if success else "❌"
    print(f"{status} {message}")
    if details:
        print(f"   Details: {details}")

def test_demo_login():
    """Login with demo credentials"""
    try:
        demo_login_data = {
            "email": "demo@idfs-pathwayiq.com",
            "password": "demo123"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=demo_login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"❌ Demo login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Demo login error: {e}")
        return None

def test_content_types(auth_token):
    """Test GET /api/content-generation/content-types"""
    print_test_header("Content Generation - Get Content Types")
    
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
            
            content_types = data.get("content_types", [])
            expected_types = ["quiz", "lesson", "explanation", "practice_problems", "study_guide", "flashcards"]
            
            for expected_type in expected_types:
                found = any(ct.get("id") == expected_type for ct in content_types)
                print_result(found, f"Content type '{expected_type}' available")
            
            print(f"   Total content types: {len(content_types)}")
            return True
        else:
            print_result(False, f"Get content types failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get content types failed with exception: {e}")
        return False

def test_quiz_generation(auth_token):
    """Test quiz generation"""
    print_test_header("AI Content Generation - Quiz")
    
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
                "Apply the quadratic formula"
            ],
            "target_audience": "8th grade students",
            "length": "medium"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=quiz_request,
            headers=headers,
            timeout=90  # Longer timeout for AI generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Quiz generation successful")
            
            # Check response structure
            required_fields = ["id", "content_type", "subject", "topic", "title", "content", "quality_score"]
            for field in required_fields:
                print_result(field in data, f"Response contains {field}")
            
            # Check content structure
            content = data.get("content", {})
            if isinstance(content, dict):
                quiz_fields = ["questions", "instructions", "total_questions"]
                for field in quiz_fields:
                    print_result(field in content, f"Quiz content contains {field}")
            
            print(f"   Generated Content ID: {data.get('id')}")
            print(f"   Title: {data.get('title')}")
            print(f"   Quality Score: {data.get('quality_score')}")
            
            # Store content ID for later tests
            global test_content_id
            test_content_id = data.get('id')
            
            return True
        else:
            print_result(False, f"Quiz generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Quiz generation failed with exception: {e}")
        return False

def test_lesson_generation(auth_token):
    """Test lesson generation"""
    print_test_header("AI Content Generation - Lesson")
    
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
                "Identify inputs and outputs"
            ],
            "target_audience": "6th grade students",
            "length": "short"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=lesson_request,
            headers=headers,
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Lesson generation successful")
            
            # Check content type
            print_result(data.get("content_type") == "lesson", "Content type is 'lesson'")
            
            # Check lesson content structure
            content = data.get("content", {})
            if isinstance(content, dict):
                lesson_fields = ["introduction", "main_content", "activities"]
                for field in lesson_fields:
                    print_result(field in content, f"Lesson content contains {field}")
            
            print(f"   Lesson Title: {data.get('title')}")
            print(f"   Subject: {data.get('subject')}")
            print(f"   Topic: {data.get('topic')}")
            
            return True
        else:
            print_result(False, f"Lesson generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Lesson generation failed with exception: {e}")
        return False

def test_explanation_generation(auth_token):
    """Test explanation generation"""
    print_test_header("AI Content Generation - Explanation")
    
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
            "target_audience": "high school students",
            "length": "medium"
        }
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=explanation_request,
            headers=headers,
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Explanation generation successful")
            
            print_result(data.get("content_type") == "explanation", "Content type is 'explanation'")
            
            content = data.get("content", {})
            if isinstance(content, dict):
                explanation_fields = ["main_explanation", "key_points"]
                for field in explanation_fields:
                    print_result(field in content, f"Explanation content contains {field}")
            
            print(f"   Explanation Title: {data.get('title')}")
            
            return True
        else:
            print_result(False, f"Explanation generation failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Explanation generation failed with exception: {e}")
        return False

def test_user_content(auth_token):
    """Test GET /api/content-generation/user-content"""
    print_test_header("Content Generation - Get User Content")
    
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
            
            contents = data.get("contents", [])
            total = data.get("total", 0)
            
            print(f"   Total user content: {total}")
            print(f"   Contents returned: {len(contents)}")
            
            if contents:
                first_content = contents[0]
                content_fields = ["id", "content_type", "subject", "topic", "title"]
                for field in content_fields:
                    print_result(field in first_content, f"Content item contains {field}")
            
            return True
        else:
            print_result(False, f"Get user content failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get user content failed with exception: {e}")
        return False

def test_content_by_id(auth_token):
    """Test GET /api/content-generation/content/{content_id}"""
    print_test_header("Content Generation - Get Content By ID")
    
    # Use test content ID if available
    content_id = globals().get('test_content_id')
    if not content_id:
        print_result(True, "No content ID available from previous tests - skipping")
        return True
    
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
            
            required_fields = ["id", "content_type", "title", "content", "usage_count"]
            for field in required_fields:
                print_result(field in data, f"Response contains {field}")
            
            print(f"   Content ID: {data.get('id')}")
            print(f"   Title: {data.get('title')}")
            print(f"   Usage Count: {data.get('usage_count', 0)}")
            
            return True
        else:
            print_result(False, f"Get content by ID failed with status {response.status_code}", response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Get content by ID failed with exception: {e}")
        return False

def main():
    print("🚀 Comprehensive AI Content Generation Testing")
    print(f"🔗 Backend URL: {API_BASE}")
    print(f"📅 Test run started at: {datetime.now().isoformat()}")
    
    # Login
    auth_token = test_demo_login()
    if not auth_token:
        print("❌ Cannot proceed without authentication")
        return False
    
    print("✅ Demo login successful")
    
    # Run all tests
    test_results = {}
    test_results['content_types'] = test_content_types(auth_token)
    test_results['quiz_generation'] = test_quiz_generation(auth_token)
    test_results['lesson_generation'] = test_lesson_generation(auth_token)
    test_results['explanation_generation'] = test_explanation_generation(auth_token)
    test_results['user_content'] = test_user_content(auth_token)
    test_results['content_by_id'] = test_content_by_id(auth_token)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 AI CONTENT GENERATION TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI Content Generation tests passed!")
        return True
    else:
        print("⚠️  Some AI Content Generation tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)