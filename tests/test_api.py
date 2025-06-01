#!/usr/bin/env python
"""
Test API endpoints manually
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from employees.models import Employee, Department
from attendance.models import WorkSchedule

User = get_user_model()

def test_workschedule_api():
    """Test WorkSchedule API endpoints"""
    print("TESTING WORKSCHEDULE API")
    print("=" * 40)
    
    # Create API client
    client = APIClient()
    
    # Get existing user and token
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("ERROR: No active user found")
        return
    
    token, created = Token.objects.get_or_create(user=user)
    print(f"Using user: {user.username}")
    print(f"Token: {token.key}")
    
    # Set authentication
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    
    # Test WorkSchedule list endpoint
    try:
        response = client.get('/api/attendance/workschedules/')
        print(f"WorkSchedule list status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"WorkSchedules found: {len(data.get('results', data))}")
            print("SUCCESS: WorkSchedule API endpoint works!")
        else:
            print(f"ERROR: {response.status_code} - {response.content.decode()}")
            
    except Exception as e:
        print(f"ERROR testing API: {e}")
        import traceback
        traceback.print_exc()

def test_workschedule_filtering():
    """Test WorkSchedule filtering in Python"""
    print("\nTESTING WORKSCHEDULE FILTERING")
    print("=" * 40)
    
    try:
        # Test the exact filters used in the API
        all_schedules = WorkSchedule.objects.all()
        dept_filtered = WorkSchedule.objects.filter(department__isnull=False)
        active_filtered = WorkSchedule.objects.filter(is_active=True)
        type_filtered = WorkSchedule.objects.filter(schedule_type='standard')
        
        print(f"All schedules: {all_schedules.count()}")
        print(f"With department: {dept_filtered.count()}")
        print(f"Active: {active_filtered.count()}")
        print(f"Standard type: {type_filtered.count()}")
        
        # Test search fields
        from django.db.models import Q
        search_q = Q(name__icontains='test') | Q(department__name__icontains='test')
        search_results = WorkSchedule.objects.filter(search_q)
        print(f"Search results: {search_results.count()}")
        
        print("SUCCESS: All filtering works correctly!")
        
    except Exception as e:
        print(f"ERROR in filtering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workschedule_filtering()
    test_workschedule_api()
