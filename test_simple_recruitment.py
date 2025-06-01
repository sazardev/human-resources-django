#!/usr/bin/env python
"""
Simple recruitment system test to verify basic functionality
"""
import os
import sys
import django
import json
from datetime import date, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from employees.models import Department, Employee
from recruitment.models import JobPosting, Candidate, Application

User = get_user_model()

class SimpleRecruitmentTester:
    """Simple recruitment system functionality tester"""
    
    def __init__(self):
        self.client = Client()
        self.token = None
        self.user = None
        
    def setup_test_data(self):
        """Create minimal test data"""
        print("🔧 Setting up test data...")
        
        # Create department
        self.department, created = Department.objects.get_or_create(
            name='Test Department',
            defaults={'description': 'Test department for recruitment'}
        )
        print(f"✅ Department: {self.department.name}")
        
        # Create user
        self.user, created = User.objects.get_or_create(
            email='simple.tester@test.com',
            defaults={
                'username': 'simpletester',
                'first_name': 'Simple',
                'last_name': 'Tester',
                'password': 'testpass123'
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        print(f"✅ User: {self.user.email}")
        
        # Create employee profile
        self.employee, created = Employee.objects.get_or_create(
            user=self.user,
            defaults={
                'employee_id': 'SIMPL001',
                'first_name': 'Simple',
                'last_name': 'Tester',
                'email': 'simple.tester@test.com',
                'department': self.department,
                'position': 'Test Recruiter',
                'hire_date': date.today(),
                'employment_status': 'active'
            }
        )
        print(f"✅ Employee: {self.employee.employee_id}")
        
    def authenticate(self):
        """Authenticate user"""
        print("\n🔐 Authenticating...")
        response = self.client.post('/api/auth/login/', {
            'email': 'simple.tester@test.com',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access', data.get('token'))
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}
    
    def test_job_posting_crud(self):
        """Test job posting CRUD operations"""
        print("\n📋 Testing Job Posting CRUD...")
        
        # Create job posting
        job_data = {
            'title': 'Simple Test Job',
            'department': self.department.id,
            'hiring_manager': self.employee.id,
            'description': 'A simple test job posting',
            'responsibilities': 'Test responsibilities',
            'requirements': 'Test requirements',
            'experience_level': 'entry',
            'job_type': 'full_time',
            'location': 'Test Location',
            'status': 'active'
        }
        
        response = self.client.post(
            '/api/recruitment/job-postings/',
            data=json.dumps(job_data),
            content_type='application/json',
            **self.get_headers()
        )
        
        if response.status_code == 201:
            job = response.json()
            print(f"✅ Created job posting: {job['title']} ({job['job_id']})")
            return job
        else:
            print(f"❌ Failed to create job posting: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return None
    
    def test_direct_model_creation(self):
        """Test creating models directly without API"""
        print("\n🔧 Testing direct model creation...")
        
        # Create job posting directly
        job_posting = JobPosting.objects.create(
            title='Direct Test Job',
            department=self.department,
            hiring_manager=self.employee,
            description='A job created directly in models',
            responsibilities='Direct responsibilities',
            requirements='Direct requirements',
            experience_level='entry',
            job_type='full_time',
            location='Direct Location',
            status='active'
        )
        print(f"✅ Created job posting directly: {job_posting.title} ({job_posting.job_id})")
        
        # Create candidate directly
        candidate = Candidate.objects.create(
            first_name='Direct',
            last_name='Candidate',
            email='direct.candidate@test.com',
            phone='+1-555-0100',
            current_position='Test Position',
            current_company='Test Company',
            years_of_experience=3.0,
            source='website'
        )
        print(f"✅ Created candidate directly: {candidate.full_name} ({candidate.candidate_id})")
        
        # Create application directly
        application = Application.objects.create(
            candidate=candidate,
            job_posting=job_posting,
            status='applied',
            cover_letter='Test cover letter'
        )
        print(f"✅ Created application directly: {application.application_id}")
        
        return {
            'job_posting': job_posting,
            'candidate': candidate,
            'application': application
        }
    
    def test_api_endpoints(self):
        """Test basic API endpoint access"""
        print("\n🌐 Testing API endpoints...")
        
        endpoints = [
            '/api/recruitment/job-postings/',
            '/api/recruitment/candidates/',
            '/api/recruitment/applications/',
            '/api/recruitment/pipeline/dashboard/'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint, **self.get_headers())
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {endpoint}: {len(data)} items")
                elif isinstance(data, dict):
                    print(f"✅ {endpoint}: {len(data)} keys")
                else:
                    print(f"✅ {endpoint}: Response received")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
    
    def run_test(self):
        """Run the complete test"""
        print("🚀 Starting Simple Recruitment System Test")
        print("=" * 50)
        
        self.setup_test_data()
        
        if not self.authenticate():
            return
        
        # Test direct model creation first
        models_data = self.test_direct_model_creation()
        
        # Test API endpoints
        self.test_api_endpoints()
        
        # Test job posting API
        job = self.test_job_posting_crud()
        
        print("\n" + "=" * 50)
        print("🎉 Simple Recruitment System Test Completed!")
        
        # Print summary
        job_count = JobPosting.objects.count()
        candidate_count = Candidate.objects.count()
        application_count = Application.objects.count()
        
        print(f"📊 Database Summary:")
        print(f"   Job Postings: {job_count}")
        print(f"   Candidates: {candidate_count}")
        print(f"   Applications: {application_count}")

if __name__ == '__main__':
    tester = SimpleRecruitmentTester()
    tester.run_test()
