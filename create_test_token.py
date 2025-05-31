#!/usr/bin/env python
"""
Create a test user and get authentication token for API testing
"""
import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_test_user_and_token():
    """Create a test user and return the authentication token"""
    # Create or get test user
    username = "test_api_user"
    email = "test@example.com"
    password = "testpass123"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Test',
            'last_name': 'User',
            'is_staff': False,
            'is_superuser': False
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Created test user: {username}")
    else:
        print(f"✅ Test user already exists: {username}")
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    if created:
        print(f"✅ Created new token for user: {username}")
    else:
        print(f"✅ Using existing token for user: {username}")
    
    print(f"\n🔑 Authentication Token: {token.key}")
    print(f"👤 Username: {username}")
    print(f"🔒 Password: {password}")
    print(f"📧 Email: {email}")
    
    print(f"\n📝 Update your test script with:")
    print(f"AUTH_TOKEN = '{token.key}'")
    
    return token.key

if __name__ == "__main__":
    token = create_test_user_and_token()
