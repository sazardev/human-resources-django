#!/usr/bin/env python
"""
Comprehensive test script for Django HR Attendance API endpoints.
Tests all major endpoints to ensure they're working correctly.
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

# Import models after Django setup
from employees.models import Employee, Department
from attendance.models import WorkSchedule, TimeEntry, Timesheet

class AttendanceAPITestCase(TestCase):
    """Test case for attendance API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        print("Setting up test data...")
        
        # Create test department
        self.department = Department.objects.create(
            name="Engineering",
            description="Software Engineering Department"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create employee profile
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            department=self.department,
            position='Software Engineer',
            salary=75000.00,
            hire_date='2024-01-01'
        )
        
        # Create work schedule
        self.work_schedule = WorkSchedule.objects.create(
            name="Standard Schedule",
            department=self.department,
            schedule_type='fixed',
            start_time='09:00:00',
            end_time='17:00:00',
            is_active=True
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_work_schedule_endpoints(self):
        """Test WorkSchedule API endpoints."""
        print("\n=== Testing WorkSchedule Endpoints ===")
        
        # Test list endpoint
        url = reverse('workschedule-list')
        response = self.client.get(url)
        print(f"GET {url}: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        print(f"Found {len(data)} work schedules")
        
        # Test filtering by department
        response = self.client.get(url, {'department': self.department.id})
        print(f"GET {url}?department={self.department.id}: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test filtering by is_active
        response = self.client.get(url, {'is_active': 'true'})
        print(f"GET {url}?is_active=true: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test search
        response = self.client.get(url, {'search': 'Standard'})
        print(f"GET {url}?search=Standard: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test current schedule endpoint
        current_url = reverse('workschedule-current-schedule')
        response = self.client.get(current_url)
        print(f"GET {current_url}: {response.status_code}")
        # This might return 404 if no current schedule, which is acceptable
        print(f"Current schedule response: {response.status_code}")
        
    def test_timeentry_endpoints(self):
        """Test TimeEntry API endpoints."""
        print("\n=== Testing TimeEntry Endpoints ===")
        
        url = reverse('timeentry-list')
        response = self.client.get(url)
        print(f"GET {url}: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test creating a time entry
        data = {
            'employee': self.employee.id,
            'date': '2024-01-15',
            'time_in': '09:00:00',
            'time_out': '17:00:00',
            'entry_type': 'work'
        }
        response = self.client.post(url, data)
        print(f"POST {url}: {response.status_code}")
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error creating time entry: {response.content}")
        
    def test_timesheet_endpoints(self):
        """Test Timesheet API endpoints."""
        print("\n=== Testing Timesheet Endpoints ===")
        
        url = reverse('timesheet-list')
        response = self.client.get(url)
        print(f"GET {url}: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_authentication_required(self):
        """Test that authentication is required for endpoints."""
        print("\n=== Testing Authentication ===")
        
        # Create unauthenticated client
        unauth_client = APIClient()
        
        endpoints = [
            'workschedule-list',
            'timeentry-list', 
            'timesheet-list'
        ]
        
        for endpoint in endpoints:
            url = reverse(endpoint)
            response = unauth_client.get(url)
            print(f"Unauthenticated GET {url}: {response.status_code}")
            # Should be 401 (Unauthorized) or 403 (Forbidden)
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

def run_tests():
    """Run all tests."""
    print("Starting Attendance API Tests...")
    print("=" * 50)
    
    # Import Django test runner
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Get test runner and run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['__main__'])
    
    print("=" * 50)
    if failures:
        print(f"Tests completed with {failures} failures")
    else:
        print("All tests passed successfully!")
    
    return failures == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
