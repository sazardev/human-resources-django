#!/usr/bin/env python
"""
Complete authentication system test
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

class AuthenticationTester:
    def __init__(self):
        self.token = None
        self.session_cookies = None
    
    def test_registration(self):
        """Test user registration"""
        print("🔐 Testing Registration...")
        
        url = f"{BASE_URL}/register/"
        data = {
            "username": "completetest",
            "email": "completetest@example.com", 
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Complete",
            "last_name": "Test",
            "phone": "+1234567890"
        }
        
        try:
            response = requests.post(url, json=data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ Registration successful!")
                print(f"   User ID: {result.get('user', {}).get('id')}")
                print(f"   Username: {result.get('user', {}).get('username')}")
                return result
            else:
                print(f"   ❌ Registration failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def test_login(self):
        """Test user login"""
        print("\n🔑 Testing Login...")
        
        url = f"{BASE_URL}/login/"
        data = {
            "email": "completetest@example.com",
            "password": "testpass123"
        }
        
        try:
            response = requests.post(url, json=data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('token')
                self.session_cookies = response.cookies
                print(f"   ✅ Login successful!")
                print(f"   Token: {self.token[:20]}..." if self.token else "   No token received")
                print(f"   Session cookies: {len(self.session_cookies)} cookies")
                return result
            else:
                print(f"   ❌ Login failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def test_profile(self):
        """Test profile retrieval"""
        print("\n👤 Testing Profile...")
        
        if not self.token:
            print("   ❌ No token available for authentication")
            return None
            
        url = f"{BASE_URL}/profile/"
        headers = {"Authorization": f"Token {self.token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Profile retrieved successfully!")
                print(f"   Email: {result.get('email')}")
                print(f"   Name: {result.get('first_name')} {result.get('last_name')}")
                return result
            else:
                print(f"   ❌ Profile retrieval failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def test_profile_update(self):
        """Test profile update"""
        print("\n✏️ Testing Profile Update...")
        
        if not self.token:
            print("   ❌ No token available for authentication")
            return None
            
        url = f"{BASE_URL}/profile/"
        headers = {"Authorization": f"Token {self.token}"}
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+9876543210"
        }
        
        try:
            response = requests.patch(url, json=data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Profile updated successfully!")
                print(f"   Updated name: {result.get('first_name')} {result.get('last_name')}")
                print(f"   Updated phone: {result.get('phone')}")
                return result
            else:
                print(f"   ❌ Profile update failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def test_password_change(self):
        """Test password change"""
        print("\n🔒 Testing Password Change...")
        
        if not self.token:
            print("   ❌ No token available for authentication")
            return None
            
        url = f"{BASE_URL}/change-password/"
        headers = {"Authorization": f"Token {self.token}"}
        data = {
            "old_password": "testpass123",
            "new_password": "newtestpass123",
            "new_password_confirm": "newtestpass123"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Password changed successfully!")
                return result
            else:
                print(f"   ❌ Password change failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def test_sessions(self):
        """Test user sessions retrieval"""
        print("\n📱 Testing User Sessions...")
        
        if not self.token:
            print("   ❌ No token available for authentication")
            return None
            
        url = f"{BASE_URL}/sessions/"
        headers = {"Authorization": f"Token {self.token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Sessions retrieved successfully!")
                print(f"   Active sessions: {len(result.get('results', []))}")
                for session in result.get('results', [])[:3]:  # Show first 3
                    print(f"   - Session: {session.get('session_key', 'N/A')[:10]}... (Active: {session.get('is_active')})")
                return result
            else:
                print(f"   ❌ Sessions retrieval failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def test_logout(self):
        """Test user logout"""
        print("\n🚪 Testing Logout...")
        
        url = f"{BASE_URL}/logout/"
        headers = {}
        
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        
        try:
            response = requests.post(url, headers=headers, cookies=self.session_cookies)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Logout successful!")
                self.token = None
                self.session_cookies = None
                return result
            else:
                print(f"   ❌ Logout failed: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Complete Authentication System Test\n")
        print("="*60)
        
        # Test registration
        registration_result = self.test_registration()
        
        # Test login
        login_result = self.test_login()
        
        # Test profile operations
        profile_result = self.test_profile()
        update_result = self.test_profile_update()
        
        # Test password change
        password_result = self.test_password_change()
        
        # Test sessions
        sessions_result = self.test_sessions()
        
        # Test logout
        logout_result = self.test_logout()
        
        # Summary
        print("\n" + "="*60)
        print("📊 Test Summary:")
        tests = [
            ("Registration", registration_result),
            ("Login", login_result),
            ("Profile Retrieval", profile_result),
            ("Profile Update", update_result),
            ("Password Change", password_result),
            ("Sessions", sessions_result),
            ("Logout", logout_result)
        ]
        
        passed = 0
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Tests passed: {passed}/{len(tests)}")
        
        if passed == len(tests):
            print("🎉 All authentication tests passed! Authentication system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the detailed output above.")

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_all_tests()
