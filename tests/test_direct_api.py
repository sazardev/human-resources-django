#!/usr/bin/env python
"""
Direct test of Django HR Attendance API endpoints.
"""
import os
import sys
import django

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from employees.models import Employee, Department
from attendance.models import WorkSchedule, TimeEntry, Timesheet
import json

def test_models():
    """Test that models are working correctly."""
    print("=== Testing Models ===")
    
    # Test Department
    departments = Department.objects.all()
    print(f"Found {departments.count()} departments")
    for dept in departments:
        print(f"  - {dept.name}")
    
    # Test Employees
    employees = Employee.objects.all()
    print(f"Found {employees.count()} employees")
    for emp in employees:
        print(f"  - {emp.user.get_full_name()} ({emp.employee_id})")
    
    # Test WorkSchedules
    schedules = WorkSchedule.objects.all()
    print(f"Found {schedules.count()} work schedules")
    for schedule in schedules:
        print(f"  - {schedule.name} (Dept: {schedule.department.name})")
        print(f"    Type: {schedule.schedule_type}, Active: {schedule.is_active}")
        print(f"    Time: {schedule.start_time} - {schedule.end_time}")
    
    # Test TimeEntries
    time_entries = TimeEntry.objects.all()
    print(f"Found {time_entries.count()} time entries")
    for entry in time_entries[:5]:  # Show first 5
        print(f"  - {entry.employee.user.get_full_name()} on {entry.date}")
    
    return True

def test_api_endpoints():
    """Test API endpoints directly."""
    print("\n=== Testing API Endpoints ===")
    
    # Create test client
    client = Client()
    
    # Test without authentication (should fail)
    response = client.get('/api/attendance/workschedules/')
    print(f"Unauthenticated request to /api/attendance/workschedules/: {response.status_code}")
    
    # Get first user for authentication
    user = User.objects.first()
    if user:
        client.force_login(user)
        print(f"Authenticated as: {user.username}")
        
        # Test WorkSchedule endpoints
        response = client.get('/api/attendance/workschedules/')
        print(f"GET /api/attendance/workschedules/: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data)} work schedules")
        else:
            print(f"  Error: {response.content}")
        
        # Test filtering
        if Department.objects.exists():
            dept = Department.objects.first()
            response = client.get(f'/api/attendance/workschedules/?department={dept.id}')
            print(f"GET /api/attendance/workschedules/?department={dept.id}: {response.status_code}")
        
        # Test search
        response = client.get('/api/attendance/workschedules/?search=schedule')
        print(f"GET /api/attendance/workschedules/?search=schedule: {response.status_code}")
        
        # Test TimeEntry endpoints
        response = client.get('/api/attendance/timeentries/')
        print(f"GET /api/attendance/timeentries/: {response.status_code}")
        
        # Test Timesheet endpoints
        response = client.get('/api/attendance/timesheets/')
        print(f"GET /api/attendance/timesheets/: {response.status_code}")
        
    else:
        print("No users found in database!")
    
    return True

def main():
    """Main test function."""
    print("Django HR Attendance System - API Test")
    print("=" * 50)
    
    try:
        # Test models first
        test_models()
        
        # Test API endpoints
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("Tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
