#!/usr/bin/env python
"""
Simple authentication test
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_registration():
    """Test user registration"""
    print("Testing Registration...")
    
    url = f"{BASE_URL}/register/"
    data = {
        "username": "testuser2",
        "email": "testuser2@example.com", 
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            return response.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting Login...")
    
    url = f"{BASE_URL}/login/"
    data = {
        "email": "testuser2@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Simple Authentication Test\n")
    
    # Test registration first
    reg_result = test_registration()
    
    # Then test login
    login_result = test_login()
    
    if login_result:
        print("✅ Authentication flow working!")
    else:
        print("❌ Authentication flow failed!")
