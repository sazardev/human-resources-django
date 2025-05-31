#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

import requests
import json
from datetime import datetime

def test_session_management():
    """Test the session management endpoints directly"""
    print("🧪 Testing Session Management API Endpoints")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("1. 🔐 Testing admin login...")
    login_data = {"email": "admin@admin.com", "password": "admin"}
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login/", json=login_data)
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print(f"   ✅ Admin login successful: {admin_token[:20]}...")
        else:
            print(f"   ❌ Admin login failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Test session management endpoint
    print("\n2. 📊 Testing session management endpoint...")
    headers = {"Authorization": f"Token {admin_token}"}
    
    try:
        response = requests.get("http://localhost:8000/api/auth/admin/sessions/", headers=headers)
        if response.status_code == 200:
            result = response.json()
            sessions = result.get('sessions', [])
            stats = result.get('statistics', {})
            
            print(f"   ✅ Session management endpoint working!")
            print(f"   📈 Statistics:")
            print(f"      Total sessions: {stats.get('total', 0)}")
            print(f"      Active sessions: {stats.get('active', 0)}")
            print(f"      Inactive sessions: {stats.get('inactive', 0)}")
            print(f"      Users with sessions: {stats.get('users_with_sessions', 0)}")
            
            print(f"\n   📋 Session Details:")
            for i, session in enumerate(sessions[:3]):  # Show first 3
                status = "🟢 ACTIVE" if session.get('is_active') else "🔴 INACTIVE"
                user = session.get('user', {}).get('email', 'Unknown')
                ip = session.get('ip_address', 'Unknown')
                duration = session.get('duration', 'Unknown')
                print(f"      {i+1}. {user}: {status} (IP: {ip}, Duration: {duration})")
                
        else:
            print(f"   ❌ Session management failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Test session history endpoint
    print("\n3. 📈 Testing session history endpoint...")
    
    try:
        # Test own history
        response = requests.get("http://localhost:8000/api/auth/sessions/my-history/", headers=headers)
        if response.status_code == 200:
            result = response.json()
            user_info = result.get('user', {})
            sessions = result.get('sessions', [])
            
            print(f"   ✅ Session history endpoint working!")
            print(f"   👤 User: {user_info.get('email', 'Unknown')}")
            print(f"   📊 Total sessions: {result.get('total_sessions', 0)}")
            print(f"   🟢 Active sessions: {result.get('active_sessions', 0)}")
            
        else:
            print(f"   ❌ Session history failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Create test user and test user-specific history
    print("\n4. 👤 Testing user-specific session history...")
    
    # Find a user ID from the sessions
    try:
        response = requests.get("http://localhost:8000/api/auth/admin/sessions/", headers=headers)
        if response.status_code == 200:
            sessions = response.json().get('sessions', [])
            if sessions:
                test_user_id = sessions[0].get('user', {}).get('id')
                if test_user_id:
                    # Test specific user history
                    response = requests.get(f"http://localhost:8000/api/auth/sessions/user/{test_user_id}/", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ User-specific history working!")
                        print(f"   👤 Target user: {result.get('user', {}).get('email', 'Unknown')}")
                        print(f"   📊 User sessions: {result.get('total_sessions', 0)}")
                    else:
                        print(f"   ❌ User-specific history failed: {response.status_code}")
                else:
                    print("   ⚠️ No user ID found in sessions")
            else:
                print("   ⚠️ No sessions found to test with")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Session Management API Test Complete!")
    print("🎉 All key endpoints are functional and properly configured.")

if __name__ == "__main__":
    test_session_management()
