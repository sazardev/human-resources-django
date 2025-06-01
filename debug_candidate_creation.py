#!/usr/bin/env python
"""
Debug script to test candidate creation and identify API issues
"""
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from recruitment.models import Candidate
from recruitment.serializers import CandidateSerializer
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import json

User = get_user_model()

def test_direct_model_creation():
    """Test creating candidate directly with model"""
    print("=== Testing Direct Model Creation ===")
    
    try:
        candidate = Candidate.objects.create(
            first_name="Test",
            last_name="Candidate",
            email="test.candidate@example.com",
            phone="555-1234",
            source="website"
        )
        print(f"✓ Successfully created candidate: {candidate}")
        print(f"  - ID: {candidate.id}")
        print(f"  - Candidate ID: {candidate.candidate_id}")
        print(f"  - Full Name: {candidate.full_name}")
        return candidate
    except Exception as e:
        print(f"✗ Error creating candidate: {e}")
        return None

def test_serializer_validation():
    """Test candidate serializer validation"""
    print("\n=== Testing Serializer Validation ===")
    
    candidate_data = {
        'first_name': 'Serializer',
        'last_name': 'Test',
        'email': 'serializer.test@example.com',
        'phone': '555-5678',
        'source': 'linkedin'
    }
    
    serializer = CandidateSerializer(data=candidate_data)
    
    if serializer.is_valid():
        try:
            candidate = serializer.save()
            print(f"✓ Successfully created candidate via serializer: {candidate}")
            return candidate
        except Exception as e:
            print(f"✗ Error saving candidate via serializer: {e}")
    else:
        print(f"✗ Serializer validation errors: {serializer.errors}")
    
    return None

def create_test_user():
    """Create a test user for API authentication"""
    print("\n=== Creating Test User ===")
    
    try:
        # Check if user already exists
        user = User.objects.filter(username='testuser').first()
        if user:
            print(f"✓ Using existing test user: {user.username}")
        else:
            user = User.objects.create_user(
                username='testuser',
                email='testuser@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            print(f"✓ Created new test user: {user.username}")
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        print(f"✓ Token: {token.key}")
        return user, token
        
    except Exception as e:
        print(f"✗ Error creating test user: {e}")
        return None, None

def test_api_endpoint():
    """Test the API endpoint for candidate creation"""
    print("\n=== Testing API Endpoint ===")
    
    user, token = create_test_user()
    if not user or not token:
        print("✗ Cannot test API without valid user/token")
        return
    
    client = APIClient()
    
    # Test without authentication
    print("\n--- Testing without authentication ---")
    response = client.post('/api/recruitment/candidates/', {
        'first_name': 'API',
        'last_name': 'Test',
        'email': 'api.test@example.com',
        'source': 'website'
    })
    print(f"Response status: {response.status_code}")
    if response.status_code != 201:
        print(f"Response data: {response.data}")
    
    # Test with token authentication
    print("\n--- Testing with token authentication ---")
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    response = client.post('/api/recruitment/candidates/', {
        'first_name': 'API',
        'last_name': 'Authenticated',
        'email': 'api.auth@example.com',
        'source': 'website'
    })
    print(f"Response status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Successfully created candidate via API")
        print(f"Response data: {json.dumps(response.data, indent=2)}")
    else:
        print(f"✗ API creation failed")
        print(f"Response data: {response.data}")
    
    # Test with missing required fields
    print("\n--- Testing with missing required fields ---")
    response = client.post('/api/recruitment/candidates/', {
        'first_name': 'Incomplete'
        # Missing last_name, email
    })
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")

def main():
    """Main test function"""
    print("Django Recruitment API Debug Script")
    print("=" * 50)
    
    # Clean up any existing test data
    print("Cleaning up existing test data...")
    Candidate.objects.filter(email__contains='example.com').delete()
    
    # Test direct model creation
    candidate1 = test_direct_model_creation()
    
    # Test serializer validation
    candidate2 = test_serializer_validation()
    
    # Test API endpoint
    test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("Debug tests completed!")

if __name__ == '__main__':
    main()
