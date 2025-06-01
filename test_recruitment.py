#!/usr/bin/env python3
"""
Test script for the Recruitment & Selection system
Tests all API endpoints and core functionality
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Add the Django project path to sys.path
django_project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(django_project_path)

# Setup Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'human_resources.settings'
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from employees.models import Department, Employee
from recruitment.models import (
    JobPosting, Candidate, Application, CandidateDocument,
    InterviewRound, Interview, InterviewEvaluation, OfferLetter,
    RecruitmentPipeline
)

User = get_user_model()

class RecruitmentTester:
    """Comprehensive tester for recruitment system"""
    
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://127.0.0.1:8000'
        self.api_base = '/api/recruitment'
        self.token = None
        self.user = None
        self.department = None
        self.employee = None
        
    def setup_test_data(self):
        """Create test data for recruitment testing"""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.user, created = User.objects.get_or_create(
            username='recruiter_test',
            defaults={
                'email': 'recruiter@test.com',
                'first_name': 'Test',
                'last_name': 'Recruiter',
                'is_active': True
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
          # Create test department
        self.department, _ = Department.objects.get_or_create(
            name='Human Resources',
            defaults={
                'description': 'HR Department for testing'
            }
        )
          # Create test employee profile
        self.employee, _ = Employee.objects.get_or_create(
            user=self.user,
            defaults={
                'employee_id': 'HR001',
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'department': self.department,
                'position': 'Senior Recruiter',
                'hire_date': datetime.now().date(),
                'employment_status': 'active'
            }        )
        
        print(f"✅ Created test user: {self.user.username}")
        print(f"✅ Created test department: {self.department.name}")
        print(f"✅ Created test employee: {self.employee.employee_id}")
    
    def authenticate(self):
        """Authenticate test user"""
        print("\n🔐 Authenticating user...")
        
        response = self.client.post('/api/auth/login/', {
            'email': 'recruiter@test.com',
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
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}
    
    def test_job_postings(self):
        """Test job posting APIs"""
        print("\n📋 Testing Job Postings...")
        
        # Test creating job posting
        job_data = {
            'title': 'Senior Software Engineer',
            'department': self.department.id,
            'description': 'We are looking for a senior software engineer...',
            'responsibilities': 'Lead development teams, mentor junior developers...',
            'requirements': 'Bachelor\'s degree in Computer Science, 5+ years experience...',
            'job_type': 'full_time',
            'experience_level': 'senior',
            'location': 'San Francisco, CA',
            'salary_min': 120000,
            'salary_max': 180000,
            'positions_available': 2,
            'priority_level': 'high',
            'remote_work_allowed': True
        }
        
        response = self.client.post(
            f'{self.api_base}/job-postings/',
            data=json.dumps(job_data),
            content_type='application/json',
            **self.get_headers()
        )
        
        if response.status_code == 201:
            job_posting = response.json()
            print(f"✅ Created job posting: {job_posting['job_id']}")
            
            # Test publishing job
            publish_response = self.client.post(
                f"{self.api_base}/job-postings/{job_posting['id']}/publish/",
                **self.get_headers()
            )
            
            if publish_response.status_code == 200:
                print("✅ Published job posting")
            else:
                print(f"❌ Failed to publish job posting: {publish_response.status_code}")
            
            # Test getting job applications
            apps_response = self.client.get(
                f"{self.api_base}/job-postings/{job_posting['id']}/applications/",
                **self.get_headers()
            )
            
            if apps_response.status_code == 200:
                print("✅ Retrieved job applications")
            else:
                print(f"❌ Failed to get job applications: {apps_response.status_code}")
            
            return job_posting
        else:
            print(f"❌ Failed to create job posting: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return None
    
    def test_candidates(self):
        """Test candidate APIs"""
        print("\n👤 Testing Candidates...")
        
        # Test creating candidate
        candidate_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1-555-0123',
            'current_position': 'Software Engineer',
            'current_company': 'Tech Corp',
            'years_of_experience': 5.5,
            'city': 'San Francisco',
            'state': 'CA',
            'country': 'United States',
            'source': 'linkedin',
            'salary_expectation': 150000,
            'willing_to_relocate': True,
            'requires_visa_sponsorship': False,
            'linkedin_url': 'https://linkedin.com/in/johndoe',
            'portfolio_url': 'https://johndoe.dev',
            'github_url': 'https://github.com/johndoe'
        }
        
        response = self.client.post(
            f'{self.api_base}/candidates/',
            data=json.dumps(candidate_data),
            content_type='application/json',
            **self.get_headers()
        )
        
        if response.status_code == 201:
            candidate = response.json()
            print(f"✅ Created candidate: {candidate['candidate_id']}")
            
            # Test getting candidate profile
            profile_response = self.client.get(
                f"{self.api_base}/candidates/{candidate['id']}/profile/",
                **self.get_headers()
            )
            
            if profile_response.status_code == 200:
                print("✅ Retrieved candidate profile")
            else:
                print(f"❌ Failed to get candidate profile: {profile_response.status_code}")
            
            return candidate
        else:
            print(f"❌ Failed to create candidate: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return None
    
    def test_applications(self, job_posting, candidate):
        """Test application APIs"""
        if not job_posting or not candidate:
            print("\n❌ Skipping application tests - missing job posting or candidate")
            return None
            
        print("\n📝 Testing Applications...")
        
        # Test creating application
        application_data = {
            'candidate': candidate['id'],
            'job_posting': job_posting['id'],
            'cover_letter': 'I am very interested in this position...',
            'initial_score': 8,
            'assigned_recruiter': self.user.id
        }
        
        response = self.client.post(
            f'{self.api_base}/applications/',
            data=json.dumps(application_data),
            content_type='application/json',
            **self.get_headers()
        )
        
        if response.status_code == 201:
            application = response.json()
            print(f"✅ Created application: {application['application_id']}")
            
            # Test updating application status
            status_response = self.client.post(
                f"{self.api_base}/applications/{application['id']}/update_status/",
                data=json.dumps({
                    'status': 'screening',
                    'notes': 'Initial screening passed'
                }),
                content_type='application/json',
                **self.get_headers()
            )
            
            if status_response.status_code == 200:
                print("✅ Updated application status")
            else:
                print(f"❌ Failed to update application status: {status_response.status_code}")
            
            return application
        else:
            print(f"❌ Failed to create application: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return None
    
    def test_interview_rounds(self, job_posting):
        """Test interview round APIs"""
        if not job_posting:
            print("\n❌ Skipping interview round tests - missing job posting")
            return None
            
        print("\n🎯 Testing Interview Rounds...")
        
        # Test creating interview round
        round_data = {
            'job_posting': job_posting['id'],
            'name': 'Technical Screening',
            'round_type': 'technical_video',
            'sequence_order': 1,
            'duration_minutes': 90,
            'is_mandatory': True,
            'is_technical': True,
            'description': 'Technical assessment via video call',
            'required_interviewers': 2,
            'minimum_score_to_pass': 7.0
        }
        
        response = self.client.post(
            f'{self.api_base}/interview-rounds/',
            data=json.dumps(round_data),
            content_type='application/json',
            **self.get_headers()
        )
        
        if response.status_code == 201:
            interview_round = response.json()
            print(f"✅ Created interview round: {interview_round['name']}")
            return interview_round
        else:
            print(f"❌ Failed to create interview round: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return None
    
    def test_interviews(self, application, interview_round):
        """Test interview APIs"""
        if not application or not interview_round:
            print("\n❌ Skipping interview tests - missing application or interview round")
            return None
            
        print("\n🎤 Testing Interviews...")
        
        # Test scheduling interview
        interview_data = {
            'application': application['id'],
            'interview_round': interview_round['id'],
            'scheduled_start': (datetime.now() + timedelta(days=7)).isoformat(),
            'scheduled_end': (datetime.now() + timedelta(days=7, hours=1.5)).isoformat(),
            'primary_interviewer': self.user.id,
            'meeting_type': 'video_call',
            'meeting_link': 'https://zoom.us/j/123456789',
            'preparation_notes': 'Review candidate\'s portfolio before interview'
        }
        
        response = self.client.post(
            f'{self.api_base}/interviews/',
            data=json.dumps(interview_data),
            content_type='application/json',
            **self.get_headers()
        )
        
        if response.status_code == 201:
            interview = response.json()
            print(f"✅ Scheduled interview: {interview['interview_id']}")
            
            # Test starting interview
            start_response = self.client.post(
                f"{self.api_base}/interviews/{interview['id']}/start_interview/",
                **self.get_headers()
            )
            
            if start_response.status_code == 200:
                print("✅ Started interview")
            else:
                print(f"❌ Failed to start interview: {start_response.status_code}")
            
            return interview
        else:
            print(f"❌ Failed to schedule interview: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            return None
    
    def test_dashboard(self):
        """Test recruitment dashboard"""
        print("\n📊 Testing Dashboard...")
        
        response = self.client.get(
            f'{self.api_base}/pipeline/dashboard/',
            **self.get_headers()
        )
        
        if response.status_code == 200:
            dashboard_data = response.json()
            print("✅ Retrieved dashboard data")
            print(f"   Active Jobs: {dashboard_data.get('total_active_jobs', 0)}")
            print(f"   Applications This Month: {dashboard_data.get('total_applications_this_month', 0)}")
            print(f"   Scheduled Interviews: {dashboard_data.get('total_interviews_scheduled', 0)}")
        else:
            print(f"❌ Failed to get dashboard data: {response.status_code}")
    
    def run_all_tests(self):
        """Run all recruitment system tests"""
        print("🚀 Starting Recruitment System Tests")
        print("=" * 50)
        
        # Setup
        self.setup_test_data()
        
        # Authenticate
        if not self.authenticate():
            print("❌ Cannot continue without authentication")
            return
        
        # Test each module
        job_posting = self.test_job_postings()
        candidate = self.test_candidates()
        application = self.test_applications(job_posting, candidate)
        interview_round = self.test_interview_rounds(job_posting)
        interview = self.test_interviews(application, interview_round)
        
        # Test dashboard
        self.test_dashboard()
        
        print("\n" + "=" * 50)
        print("🎉 Recruitment System Tests Completed!")
        
        # Summary
        print(f"\n📋 Job Postings: {'✅' if job_posting else '❌'}")
        print(f"👤 Candidates: {'✅' if candidate else '❌'}")
        print(f"📝 Applications: {'✅' if application else '❌'}")
        print(f"🎯 Interview Rounds: {'✅' if interview_round else '❌'}")
        print(f"🎤 Interviews: {'✅' if interview else '❌'}")

if __name__ == '__main__':
    tester = RecruitmentTester()
    tester.run_all_tests()
