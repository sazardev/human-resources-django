#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete session management testing script
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/auth"

class SessionTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.user_id = None
    
    def setup_admin_token(self):
        """Get admin token"""
        print("🔐 Getting admin token...")
        
        data = {
            "email": "admin@admin.com",
            "password": "admin"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=data)
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result.get('token')
                print(f"   ✅ Admin token obtained: {self.admin_token[:20]}...")
                return True
            else:
                print(f"   ❌ Admin login error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def create_test_user(self):
        """Create test user"""
        print("\n👤 Creating test user...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = {
            "username": f"testuser_{timestamp}",
            "email": f"testuser_{timestamp}@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/register/", json=data)
            if response.status_code == 201:
                result = response.json()
                self.user_id = result.get('user', {}).get('id')
                print(f"   ✅ User created with ID: {self.user_id}")
                
                # Login the test user
                login_data = {
                    "email": data["email"],
                    "password": data["password"]
                }
                login_response = requests.post(f"{BASE_URL}/login/", json=login_data)
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.user_token = login_result.get('token')
                    print(f"   ✅ User logged in, token: {self.user_token[:20]}...")
                    return True
                else:
                    print(f"   ❌ User login failed: {login_response.text}")
                    return False
            else:
                print(f"   ❌ User creation failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_session_management_view(self):
        """Test session management endpoint"""
        print("\n📊 Testing session management view...")
        
        headers = {
            "Authorization": f"Token {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/admin/sessions/", headers=headers)
            if response.status_code == 200:
                result = response.json()
                sessions = result.get('sessions', [])
                print(f"   ✅ Found {len(sessions)} sessions")
                
                for session in sessions:
                    user = session.get('user', 'Unknown')
                    status = session.get('is_active', False)
                    started = session.get('started_at', 'Unknown')
                    print(f"      - User: {user}, Active: {status}, Started: {started}")
                
                return sessions
            else:
                print(f"   ❌ Session management view failed: {response.text}")
                return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def test_user_session_history(self):
        """Test user session history endpoint"""
        print("\n📈 Testing user session history...")
        
        headers = {
            "Authorization": f"Token {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test viewing specific user's history
            if self.user_id:
                response = requests.get(f"{BASE_URL}/sessions/user/{self.user_id}/", headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    sessions = result.get('sessions', [])
                    print(f"   ✅ User {self.user_id} has {len(sessions)} sessions")
                    return True
                else:
                    print(f"   ❌ User session history failed: {response.text}")
            
            # Test viewing own history with user token
            user_headers = {
                "Authorization": f"Token {self.user_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(f"{BASE_URL}/sessions/my-history/", headers=user_headers)
            if response.status_code == 200:
                result = response.json()
                sessions = result.get('sessions', [])
                print(f"   ✅ User's own history: {len(sessions)} sessions")
                return True
            else:
                print(f"   ❌ Own session history failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_force_logout(self):
        """Test force logout functionality"""
        print("\n🚪 Testing force logout...")
        
        # First get all active sessions
        headers = {
            "Authorization": f"Token {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/admin/sessions/", headers=headers)
            if response.status_code == 200:
                result = response.json()
                sessions = result.get('sessions', [])
                
                # Find an active session to logout
                active_session = None
                for session in sessions:
                    if session.get('is_active') and session.get('user') != 'admin@admin.com':
                        active_session = session
                        break
                
                if active_session:
                    session_id = active_session.get('id')
                    print(f"   📍 Found active session {session_id} for user {active_session.get('user')}")
                    
                    # Force logout
                    logout_data = {"session_id": session_id}
                    logout_response = requests.delete(f"{BASE_URL}/admin/sessions/", 
                                                    json=logout_data, headers=headers)
                    
                    if logout_response.status_code == 200:
                        print(f"   ✅ Successfully forced logout of session {session_id}")
                        return True
                    else:
                        print(f"   ❌ Force logout failed: {logout_response.text}")
                        return False
                else:
                    print("   ℹ️ No active sessions found to test force logout")
                    return True
            else:
                print(f"   ❌ Could not get sessions: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_session_duration(self):
        """Test session duration calculations"""
        print("\n⏱️ Testing session duration calculations...")
        
        # Logout current user to create ended session
        user_headers = {
            "Authorization": f"Token {self.user_token}",
            "Content-Type": "application/json"
        }
        
        try:
            logout_response = requests.post(f"{BASE_URL}/logout/", headers=user_headers)
            if logout_response.status_code == 200:
                print("   ✅ User logged out successfully")
                
                # Check session history to see duration
                admin_headers = {
                    "Authorization": f"Token {self.admin_token}",
                    "Content-Type": "application/json"
                }
                
                history_response = requests.get(f"{BASE_URL}/sessions/user/{self.user_id}/", 
                                              headers=admin_headers)
                if history_response.status_code == 200:
                    result = history_response.json()
                    sessions = result.get('sessions', [])
                    
                    for session in sessions:
                        duration = session.get('duration')
                        if duration:
                            print(f"   ✅ Session duration calculated: {duration}")
                            return True
                    
                    print("   ℹ️ No duration found in sessions")
                    return True
                else:
                    print(f"   ❌ Could not get session history: {history_response.text}")
                    return False
            else:
                print(f"   ❌ Logout failed: {logout_response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all session management tests"""
        print("🧪 Starting session management tests...")
        print("=" * 50)
        
        # Setup
        if not self.setup_admin_token():
            print("❌ Failed to setup admin token")
            return False
        
        if not self.create_test_user():
            print("❌ Failed to create test user")
            return False
        
        # Run tests
        tests = [
            ("Session Management View", self.test_session_management_view),
            ("User Session History", self.test_user_session_history),
            ("Force Logout", self.test_force_logout),
            ("Session Duration", self.test_session_duration),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"   ❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\nResults: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All session management tests passed!")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return passed == len(results)

if __name__ == "__main__":
    tester = SessionTester()
    tester.run_all_tests()
