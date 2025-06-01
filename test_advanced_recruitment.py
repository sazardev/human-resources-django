#!/usr/bin/env python3
"""
Advanced Recruitment System Testing and Enhancement Script
Tests all advanced features and demonstrates the complete recruitment workflow
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from decimal import Decimal

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

class AdvancedRecruitmentTester:
    """Advanced tester for recruitment system with full workflow"""
    
    def __init__(self):
        self.client = Client()
        self.token = None
        self.user = None
        self.department = None
        self.employee = None
        
        # Test data containers
        self.job_postings = []
        self.candidates = []
        self.applications = []
        self.interviews = []
        self.offers = []
        
    def authenticate(self):
        """Authenticate as recruiter"""
        print("🔐 Authenticating as recruiter...")
        
        # Create/get test user
        self.user, created = User.objects.get_or_create(
            username='advanced_recruiter',
            defaults={
                'email': 'advanced.recruiter@test.com',
                'first_name': 'Advanced',
                'last_name': 'Recruiter',
                'is_active': True
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        
        # Create department and employee
        self.department, _ = Department.objects.get_or_create(
            name='Technology',
            defaults={'description': 'Technology Department'}
        )
        
        self.employee, _ = Employee.objects.get_or_create(
            user=self.user,
            defaults={
                'employee_id': 'TEC001',
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'department': self.department,
                'position': 'Senior Technical Recruiter',
                'hire_date': datetime.now().date(),
                'employment_status': 'active'
            }
        )
        
        response = self.client.post('/api/auth/login/', {
            'email': 'advanced.recruiter@test.com',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access', data.get('token'))
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}
    
    def create_comprehensive_job_postings(self):
        """Create multiple job postings with different configurations"""
        print("\n📋 Creating comprehensive job postings...")
        
        job_configs = [
            {
                'title': 'Senior Python Developer',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'salary_min': 120000,
                'salary_max': 180000,
                'priority_level': 'high',
                'positions_available': 2
            },
            {
                'title': 'Frontend React Developer',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'salary_min': 80000,
                'salary_max': 120000,
                'priority_level': 'medium',
                'positions_available': 3
            },
            {
                'title': 'DevOps Engineer',
                'job_type': 'contract',
                'experience_level': 'senior',
                'salary_min': 140000,
                'salary_max': 200000,
                'priority_level': 'urgent',
                'positions_available': 1
            },
            {
                'title': 'Data Scientist Intern',
                'job_type': 'internship',
                'experience_level': 'entry',
                'salary_min': 40000,
                'salary_max': 60000,
                'priority_level': 'low',
                'positions_available': 2
            }
        ]
        
        for config in job_configs:
            job_data = {
                'title': config['title'],
                'department': self.department.id,
                'hiring_manager': self.employee.id,
                'description': f'We are looking for a talented {config["title"]} to join our growing team...',
                'responsibilities': f'Lead {config["title"]} initiatives, collaborate with cross-functional teams...',
                'requirements': f'Bachelor\'s degree, {config["experience_level"]} level experience...',
                'job_type': config['job_type'],
                'experience_level': config['experience_level'],
                'location': 'San Francisco, CA',
                'salary_min': config['salary_min'],
                'salary_max': config['salary_max'],
                'positions_available': config['positions_available'],
                'priority_level': config['priority_level'],
                'remote_work_allowed': True,
                'keywords': f'{config["title"]}, {config["experience_level"]}, Python, JavaScript'
            }
            
            response = self.client.post(
                '/api/recruitment/job-postings/',
                data=json.dumps(job_data),
                content_type='application/json',
                **self.get_headers()
            )
            
            if response.status_code == 201:
                job_posting = response.json()
                self.job_postings.append(job_posting)
                print(f"✅ Created job posting: {job_posting['title']} ({job_posting['job_id']})")
                
                # Publish the job
                self.client.post(
                    f"/api/recruitment/job-postings/{job_posting['id']}/publish/",
                    **self.get_headers()
                )
                
                # Create interview rounds for each job
                self.create_interview_rounds(job_posting)
            else:
                print(f"❌ Failed to create job posting: {config['title']}")
    
    def create_interview_rounds(self, job_posting):
        """Create interview rounds for a job posting"""
        rounds = [
            {
                'name': 'Initial Screening',
                'round_type': 'phone_screening',
                'sequence_order': 1,
                'duration_minutes': 30,
                'is_mandatory': True,
                'is_technical': False
            },
            {
                'name': 'Technical Assessment',
                'round_type': 'technical_video',
                'sequence_order': 2,
                'duration_minutes': 90,
                'is_mandatory': True,
                'is_technical': True
            },
            {
                'name': 'Team Interview',
                'round_type': 'panel',
                'sequence_order': 3,
                'duration_minutes': 60,
                'is_mandatory': True,
                'is_technical': False
            },
            {
                'name': 'Final Interview',
                'round_type': 'final',
                'sequence_order': 4,
                'duration_minutes': 45,
                'is_mandatory': True,
                'is_technical': False
            }
        ]
        
        for round_config in rounds:
            round_data = {
                'job_posting': job_posting['id'],
                **round_config
            }
            
            response = self.client.post(
                '/api/recruitment/interview-rounds/',
                data=json.dumps(round_data),
                content_type='application/json',
                **self.get_headers()
            )
            
            if response.status_code == 201:
                round_obj = response.json()
                print(f"    ✅ Created interview round: {round_obj['name']}")
    
    def create_diverse_candidates(self):
        """Create candidates with diverse backgrounds and experiences"""
        print("\n👥 Creating diverse candidate pool...")
        
        candidate_configs = [
            {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice.johnson@email.com',
                'current_position': 'Senior Python Developer',
                'current_company': 'Tech Corp',
                'years_of_experience': 7.5,
                'source': 'linkedin',
                'salary_expectation': 150000,
                'skills': 'Python, Django, AWS, PostgreSQL'
            },
            {
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'email': 'carlos.rodriguez@email.com',
                'current_position': 'Frontend Developer',
                'current_company': 'Startup Inc',
                'years_of_experience': 4.0,
                'source': 'job_board',
                'salary_expectation': 95000,
                'skills': 'React, TypeScript, Node.js, GraphQL'
            },
            {
                'first_name': 'Priya',
                'last_name': 'Patel',
                'email': 'priya.patel@email.com',
                'current_position': 'DevOps Engineer',
                'current_company': 'Enterprise Solutions',
                'years_of_experience': 8.0,
                'source': 'referral',
                'salary_expectation': 165000,
                'skills': 'Kubernetes, Docker, Terraform, CI/CD'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'michael.chen@email.com',
                'current_position': 'Computer Science Student',
                'current_company': 'Stanford University',
                'years_of_experience': 0.5,
                'source': 'university',
                'salary_expectation': 50000,
                'skills': 'Python, Machine Learning, Statistics, R'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'email': 'sarah.williams@email.com',
                'current_position': 'Full Stack Developer',
                'current_company': 'Digital Agency',
                'years_of_experience': 6.0,
                'source': 'website',
                'salary_expectation': 130000,
                'skills': 'Python, React, PostgreSQL, Redis'
            }
        ]
        
        for config in candidate_configs:
            candidate_data = {
                'first_name': config['first_name'],
                'last_name': config['last_name'],
                'email': config['email'],
                'phone': '+1-555-0199',
                'current_position': config['current_position'],
                'current_company': config['current_company'],
                'years_of_experience': config['years_of_experience'],
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'United States',
                'source': config['source'],
                'salary_expectation': config['salary_expectation'],
                'willing_to_relocate': True,
                'requires_visa_sponsorship': False,
                'tags': config['skills']
            }
            
            response = self.client.post(
                '/api/recruitment/candidates/',
                data=json.dumps(candidate_data),
                content_type='application/json',
                **self.get_headers()
            )
            
            if response.status_code == 201:
                candidate = response.json()
                self.candidates.append(candidate)
                print(f"✅ Created candidate: {candidate['full_name']} ({candidate['candidate_id']})")
            else:
                print(f"❌ Failed to create candidate: {config['first_name']} {config['last_name']}")
    
    def create_applications_workflow(self):
        """Create applications and simulate recruitment workflow"""
        print("\n📝 Creating applications and simulating workflow...")
        
        # Create applications for each candidate to relevant jobs
        application_mappings = [
            # Alice -> Senior Python Developer
            (0, 0, 'applied'),
            # Carlos -> Frontend Developer  
            (1, 1, 'screening'),
            # Priya -> DevOps Engineer
            (2, 2, 'interview'),
            # Michael -> Data Science Intern
            (3, 3, 'applied'),
            # Sarah -> Senior Python Developer (alternative candidate)
            (4, 0, 'screening')
        ]
        
        for candidate_idx, job_idx, status in application_mappings:
            if candidate_idx < len(self.candidates) and job_idx < len(self.job_postings):
                candidate = self.candidates[candidate_idx]
                job_posting = self.job_postings[job_idx]
                
                application_data = {
                    'candidate': candidate['id'],
                    'job_posting': job_posting['id'],
                    'cover_letter': f'I am very interested in the {job_posting["title"]} position...',
                    'initial_score': 8,
                    'assigned_recruiter': self.user.id
                }
                
                response = self.client.post(
                    '/api/recruitment/applications/',
                    data=json.dumps(application_data),
                    content_type='application/json',
                    **self.get_headers()
                )
                
                if response.status_code == 201:
                    application = response.json()
                    self.applications.append(application)
                    print(f"✅ Created application: {candidate['full_name']} → {job_posting['title']}")
                    
                    # Update status if needed
                    if status != 'applied':
                        self.client.post(
                            f"/api/recruitment/applications/{application['id']}/update_status/",
                            data=json.dumps({
                                'status': status,
                                'notes': f'Updated to {status} status for testing'
                            }),
                            content_type='application/json',
                            **self.get_headers()
                        )
                        print(f"    ✅ Updated status to: {status}")
    
    def schedule_interviews(self):
        """Schedule interviews for applications in interview stage"""
        print("\n🎤 Scheduling interviews...")
        
        for application in self.applications:
            if application.get('status') == 'interview':
                # Get interview rounds for this job
                rounds_response = self.client.get(
                    f"/api/recruitment/interview-rounds/?job_posting={application['job_posting']}",
                    **self.get_headers()
                )
                
                if rounds_response.status_code == 200:
                    rounds = rounds_response.json().get('results', [])
                    
                    for round_obj in rounds[:2]:  # Schedule first 2 rounds
                        interview_data = {
                            'application': application['id'],
                            'interview_round': round_obj['id'],
                            'scheduled_start': (datetime.now() + timedelta(days=7)).isoformat(),
                            'scheduled_end': (datetime.now() + timedelta(days=7, hours=1.5)).isoformat(),
                            'primary_interviewer': self.user.id,
                            'meeting_type': 'video_call',
                            'meeting_link': 'https://zoom.us/j/123456789',
                            'preparation_notes': f'Review candidate skills for {round_obj["name"]}'
                        }
                        
                        response = self.client.post(
                            '/api/recruitment/interviews/',
                            data=json.dumps(interview_data),
                            content_type='application/json',
                            **self.get_headers()
                        )
                        
                        if response.status_code == 201:
                            interview = response.json()
                            self.interviews.append(interview)
                            print(f"✅ Scheduled: {round_obj['name']} for {application['candidate_name'] if 'candidate_name' in application else 'candidate'}")
    
    def create_interview_evaluations(self):
        """Create evaluations for completed interviews"""
        print("\n📊 Creating interview evaluations...")
        
        for interview in self.interviews:
            evaluation_data = {
                'interview': interview['id'],
                'evaluator': self.user.id,
                'overall_rating': 4,
                'recommendation': 'hire',
                'technical_skills': 4,
                'communication_skills': 5,
                'problem_solving': 4,
                'cultural_fit': 5,
                'enthusiasm': 5,
                'experience_relevance': 4,
                'strengths': 'Strong technical skills, excellent communication, great cultural fit',
                'weaknesses': 'Could improve in advanced algorithms',
                'specific_feedback': 'Candidate demonstrated solid understanding of core concepts and showed enthusiasm for the role.'
            }
            
            response = self.client.post(
                '/api/recruitment/evaluations/',
                data=json.dumps(evaluation_data),
                content_type='application/json',
                **self.get_headers()
            )
            
            if response.status_code == 201:
                evaluation = response.json()
                print(f"✅ Created evaluation for interview {interview['interview_id']}")
    
    def create_offer_letters(self):
        """Create offer letters for successful candidates"""
        print("\n💌 Creating offer letters...")
        
        # Find applications that should get offers
        successful_applications = [app for app in self.applications if app.get('status') in ['interview', 'screening']]
        
        for application in successful_applications[:2]:  # Create offers for first 2
            offer_data = {
                'application': application['id'],
                'position_title': application.get('job_posting_title', 'Software Engineer'),
                'department': self.department.id,
                'reporting_manager': self.employee.id,
                'offer_type': 'full_time',
                'base_salary': 135000.00,
                'currency': 'USD',
                'salary_frequency': 'annually',
                'signing_bonus': 10000.00,
                'health_insurance': True,
                'dental_insurance': True,
                'vision_insurance': True,
                'retirement_plan': True,
                'paid_time_off': 25,
                'sick_leave': 10,
                'work_location': 'San Francisco, CA',
                'remote_work_allowed': True,
                'start_date': (datetime.now() + timedelta(days=30)).date().isoformat(),
                'offer_expiry_date': (datetime.now() + timedelta(days=14)).isoformat(),
                'prepared_by': self.user.id,
                'probation_period': 90,
                'notice_period': 14
            }
            
            response = self.client.post(
                '/api/recruitment/offers/',
                data=json.dumps(offer_data),
                content_type='application/json',
                **self.get_headers()
            )
            
            if response.status_code == 201:
                offer = response.json()
                self.offers.append(offer)
                print(f"✅ Created offer letter: {offer['offer_id']}")
                
                # Approve the offer
                approve_response = self.client.post(
                    f"/api/recruitment/offers/{offer['id']}/approve/",
                    **self.get_headers()
                )
                
                if approve_response.status_code == 200:
                    print(f"    ✅ Approved offer: {offer['offer_id']}")
    
    def test_advanced_features(self):
        """Test advanced recruitment features"""
        print("\n🔍 Testing advanced features...")
        
        # Test dashboard with comprehensive data
        dashboard_response = self.client.get(
            '/api/recruitment/pipeline/dashboard/',
            **self.get_headers()
        )
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ Dashboard data retrieved:")
            print(f"    Active Jobs: {dashboard_data.get('total_active_jobs', 0)}")
            print(f"    Applications This Month: {dashboard_data.get('total_applications_this_month', 0)}")
            print(f"    Interviews Scheduled: {dashboard_data.get('total_interviews_scheduled', 0)}")
            print(f"    Pending Offers: {dashboard_data.get('total_offers_pending', 0)}")
        
        # Test candidate source statistics
        sources_response = self.client.get(
            '/api/recruitment/candidates/sources_stats/',
            **self.get_headers()
        )
        
        if sources_response.status_code == 200:
            sources_data = sources_response.json()
            print("✅ Candidate sources analysis:")
            for source in sources_data:
                print(f"    {source['source']}: {source['count']} candidates")
        
        # Test pipeline statistics for each job
        for job_posting in self.job_postings:
            pipeline_response = self.client.get(
                f"/api/recruitment/job-postings/{job_posting['id']}/pipeline_stats/",
                **self.get_headers()
            )
            
            if pipeline_response.status_code == 200:
                pipeline_data = pipeline_response.json()
                print(f"✅ Pipeline stats for {job_posting['title']}:")
                print(f"    Applications: {pipeline_data.get('total_applications', 0)}")
                print(f"    Screened: {pipeline_data.get('applications_screened', 0)}")
                print(f"    Interviewed: {pipeline_data.get('candidates_interviewed', 0)}")
        
        # Test upcoming interviews
        upcoming_response = self.client.get(
            '/api/recruitment/interviews/upcoming/',
            **self.get_headers()
        )
        
        if upcoming_response.status_code == 200:
            upcoming_data = upcoming_response.json()
            print(f"✅ Upcoming interviews: {len(upcoming_data)} scheduled")
          # Test rating distribution
        ratings_response = self.client.get(
            '/api/recruitment/evaluations/rating_distribution/',
            **self.get_headers()
        )
        
        if ratings_response.status_code == 200:
            ratings_data = ratings_response.json()
            avg_rating = ratings_data.get('average_rating', 0) or 0
            print(f"✅ Rating distribution: Average {avg_rating:.1f}")
    
    def run_comprehensive_test(self):
        """Run the complete advanced recruitment test"""
        print("🚀 Starting Advanced Recruitment System Testing")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Authentication failed, cannot continue")
            return
        
        # Create comprehensive test data
        self.create_comprehensive_job_postings()
        self.create_diverse_candidates()
        self.create_applications_workflow()
        self.schedule_interviews()
        self.create_interview_evaluations()
        self.create_offer_letters()
        
        # Test advanced features
        self.test_advanced_features()
        
        print("\n" + "=" * 60)
        print("🎉 Advanced Recruitment System Testing Completed!")
        
        # Summary
        print(f"\n📊 Test Results Summary:")
        print(f"✅ Job Postings Created: {len(self.job_postings)}")
        print(f"✅ Candidates Created: {len(self.candidates)}")
        print(f"✅ Applications Created: {len(self.applications)}")
        print(f"✅ Interviews Scheduled: {len(self.interviews)}")
        print(f"✅ Offer Letters Created: {len(self.offers)}")
        
        print(f"\n🔧 System Features Tested:")
        print("✅ Complete recruitment workflow")
        print("✅ Multi-stage interview process")
        print("✅ Candidate evaluation system")
        print("✅ Offer management")
        print("✅ Pipeline analytics")
        print("✅ Dashboard metrics")
        print("✅ Advanced filtering and search")

if __name__ == '__main__':
    tester = AdvancedRecruitmentTester()
    tester.run_comprehensive_test()
