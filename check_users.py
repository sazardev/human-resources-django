#!/usr/bin/env python
"""
Check existing users and test authentication
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_users():
    """Check what users exist in the database"""
    print("🔍 Checking existing users...")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"- ID: {user.id}, Email: {user.email}, Username: {user.username}, Active: {user.is_active}")
    print()

def create_test_user():
    """Create a test user for authentication testing"""
    print("👤 Creating test user...")
    
    # Check if test user already exists
    if User.objects.filter(email='test@example.com').exists():
        print("Test user already exists")
        user = User.objects.get(email='test@example.com')
    else:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created test user: {user.email}")
    
    return user

def test_login_endpoint():
    """Test the login endpoint"""
    print("🔐 Testing login endpoint...")
    
    # Test data
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Django server is running")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_registration_endpoint():
    """Test the registration endpoint"""
    print("📝 Testing registration endpoint...")
    
    # Test data
    registration_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass123',
        'password2': 'newpass123',
        'first_name': 'New',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/auth/register/',
            json=registration_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("❌ Registration failed!")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Django server is running")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Authentication Testing Script\n")
    
    # Check existing users
    check_users()
    
    # Create test user
    test_user = create_test_user()
    
    print("\n" + "="*50 + "\n")
    
    # Test registration
    test_registration_endpoint()
    
    print("\n" + "-"*50 + "\n")
    
    # Test login
    test_login_endpoint()
