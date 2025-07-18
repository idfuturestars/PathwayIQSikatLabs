#!/usr/bin/env python3
"""
Focused AI Content Generation Testing
Tests the AI content generation functionality with better error handling
"""

import requests
import json
import os
import sys
from datetime import datetime

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

def test_content_generation_with_debug(auth_token):
    """Test content generation with detailed debugging"""
    
    print("🤖 Testing AI Content Generation with Debug Info")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Simple quiz generation with minimal data
    print("\n📝 Test 1: Simple Quiz Generation")
    quiz_request = {
        "content_type": "quiz",
        "subject": "Math",
        "topic": "Addition",
        "difficulty_level": "beginner",
        "target_audience": "5th grade students",
        "length": "short"
    }
    
    try:
        print(f"   Sending request to: {API_BASE}/content-generation/generate")
        print(f"   Request data: {json.dumps(quiz_request, indent=2)}")
        
        response = requests.post(
            f"{API_BASE}/content-generation/generate",
            json=quiz_request,
            headers=headers,
            timeout=60  # Longer timeout
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Quiz generation successful!")
            print(f"   Generated content ID: {data.get('id')}")
            print(f"   Title: {data.get('title')}")
            print(f"   Quality score: {data.get('quality_score')}")
            return True
        else:
            print(f"❌ Quiz generation failed")
            print(f"   Response text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - OpenAI API may be slow")
        return False
    except Exception as e:
        print(f"❌ Quiz generation error: {e}")
        return False

def test_openai_connectivity():
    """Test if OpenAI API key is working"""
    print("\n🔑 Testing OpenAI API Connectivity")
    
    try:
        # Check if OpenAI key is configured
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
            
        if 'OPENAI_API_KEY=' in env_content:
            for line in env_content.split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"')
                    if key and len(key) > 20:
                        print(f"✅ OpenAI API key is configured (length: {len(key)})")
                        print(f"   Key starts with: {key[:10]}...")
                        return True
                    else:
                        print("❌ OpenAI API key is empty or too short")
                        return False
        else:
            print("❌ OpenAI API key not found in .env")
            return False
            
    except Exception as e:
        print(f"❌ Error checking OpenAI key: {e}")
        return False

def main():
    print("🚀 AI Content Generation Focused Testing")
    print(f"🔗 Backend URL: {API_BASE}")
    
    # Test OpenAI connectivity first
    if not test_openai_connectivity():
        print("❌ OpenAI API key issue - content generation will fail")
        return False
    
    # Login
    auth_token = test_demo_login()
    if not auth_token:
        print("❌ Cannot proceed without authentication")
        return False
    
    print("✅ Demo login successful")
    
    # Test content generation
    success = test_content_generation_with_debug(auth_token)
    
    if success:
        print("\n🎉 AI Content Generation is working!")
        return True
    else:
        print("\n❌ AI Content Generation has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)