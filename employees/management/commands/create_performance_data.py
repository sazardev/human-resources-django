from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from employees.models import Employee, PerformanceReview, PerformanceGoal, PerformanceNote


class Command(BaseCommand):
    help = 'Create sample performance data for testing'

    def handle(self, *args, **options):
        """Create sample performance reviews, goals, and notes"""
        
        self.stdout.write("Creating sample performance data...")
        
        # Get all employees and users
        employees = Employee.objects.all()
        users = User.objects.all()
        
        if not employees.exists():
            self.stdout.write(self.style.ERROR("No employees found. Please run the sample data script first."))
            return
        
        # Create admin user if doesn't exist (for reviews)
        admin_user, created = User.objects.get_or_create(
            username='hr_admin',
            defaults={
                'first_name': 'HR',
                'last_name': 'Administrator',
                'email': 'hr@company.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created HR admin user: {admin_user.username}"))
        
        # Performance Reviews
        self.stdout.write("Creating performance reviews...")
        review_count = 0
        
        for i, employee in enumerate(employees):
            # Create annual review for each employee
            review_date = date.today() - timedelta(days=30 + i*10)
            period_start = review_date - timedelta(days=365)
            period_end = review_date - timedelta(days=1)
            
            review, created = PerformanceReview.objects.get_or_create(
                employee=employee,
                review_period_start=period_start,
                review_period_end=period_end,
                defaults={
                    'reviewer': admin_user,
                    'review_type': 'annual',
                    'review_date': review_date,
                    'status': 'completed',
                    'overall_rating': 3 + (i % 3),  # Ratings 3, 4, 5
                    'technical_skills': 3 + (i % 3),
                    'communication': 4 if i % 2 == 0 else 3,
                    'teamwork': 4,
                    'leadership': 3 + (i % 2) if i < 3 else None,  # Some don't have leadership
                    'problem_solving': 3 + (i % 3),
                    'adaptability': 4,
                    'strengths': f"Excellent performance in {employee.position}. Strong technical skills and team collaboration.",
                    'areas_for_improvement': "Continue developing leadership skills and exploring new technologies.",
                    'goals_for_next_period': "Focus on skill development and taking on more challenging projects.",
                    'reviewer_comments': f"Great work this year. {employee.first_name} has shown consistent growth.",
                    'promotion_recommendation': i % 3 == 0,
                    'salary_increase_recommendation': i % 2 == 0,
                    'training_recommendations': "Leadership training, advanced technical courses"
                }
            )
            if created:
                review_count += 1
                self.stdout.write(f"  Created review for {employee.full_name}")
        
        # Performance Goals
        self.stdout.write("Creating performance goals...")
        goal_count = 0
        
        goal_templates = [
            {
                'title': 'Complete Advanced Training Course',
                'description': 'Complete advanced technical training course in your field',
                'category': 'skill_development',
                'priority': 'high',
                'success_criteria': 'Successfully complete course with certification',
                'days_from_now': 90
            },
            {
                'title': 'Lead Cross-functional Project',
                'description': 'Lead a project involving multiple departments',
                'category': 'leadership',
                'priority': 'medium',
                'success_criteria': 'Successfully deliver project on time and within scope',
                'days_from_now': 120
            },
            {
                'title': 'Improve Customer Satisfaction Score',
                'description': 'Work on improving customer satisfaction metrics',
                'category': 'performance',
                'priority': 'high',
                'success_criteria': 'Achieve 90% customer satisfaction score',
                'days_from_now': 60
            },
            {
                'title': 'Mentor Junior Team Member',
                'description': 'Provide mentorship and guidance to a junior colleague',
                'category': 'leadership',
                'priority': 'medium',
                'success_criteria': 'Mentee shows measurable improvement in performance',
                'days_from_now': 180
            },
            {
                'title': 'Process Improvement Initiative',
                'description': 'Identify and implement a process improvement',
                'category': 'project',
                'priority': 'medium',
                'success_criteria': 'Achieve 15% efficiency improvement in chosen process',
                'days_from_now': 150
            }
        ]
        
        for i, employee in enumerate(employees):
            # Create 2-3 goals per employee
            for j in range(2 + (i % 2)):  # 2 or 3 goals
                template = goal_templates[(i + j) % len(goal_templates)]
                
                start_date = date.today() - timedelta(days=30)
                target_date = start_date + timedelta(days=template['days_from_now'])
                
                # Vary the status and progress
                if j == 0:
                    status = 'completed'
                    progress = 100
                    completed_date = target_date - timedelta(days=10)
                elif j == 1:
                    status = 'in_progress'
                    progress = 40 + (i * 10) % 60  # 40-90%
                    completed_date = None
                else:
                    status = 'pending'
                    progress = 0
                    completed_date = None
                
                goal, created = PerformanceGoal.objects.get_or_create(
                    employee=employee,
                    title=f"{template['title']} - {employee.first_name}",
                    defaults={
                        'description': template['description'],
                        'category': template['category'],
                        'priority': template['priority'],
                        'start_date': start_date,
                        'target_date': target_date,
                        'completed_date': completed_date,
                        'status': status,
                        'progress_percentage': progress,
                        'success_criteria': template['success_criteria'],
                        'measurable_outcomes': f"Specific metrics for {employee.first_name}'s {template['title'].lower()}",
                        'progress_notes': f"Good progress on this goal. {employee.first_name} is on track." if progress > 0 else None,
                        'created_by': admin_user,
                        'review': PerformanceReview.objects.filter(employee=employee).first()
                    }
                )
                if created:
                    goal_count += 1
                    self.stdout.write(f"  Created goal '{goal.title}' for {employee.full_name}")
        
        # Performance Notes
        self.stdout.write("Creating performance notes...")
        note_count = 0
        
        note_templates = [
            {
                'note_type': 'achievement',
                'title': 'Excellent Project Delivery',
                'content': 'Successfully delivered project ahead of schedule with exceptional quality.'
            },
            {
                'note_type': 'observation',
                'title': 'Strong Team Collaboration',
                'content': 'Observed excellent collaboration skills during team meetings and project work.'
            },
            {
                'note_type': 'feedback',
                'title': 'Areas for Growth',
                'content': 'Discussed opportunities for professional development and skill enhancement.'
            },
            {
                'note_type': 'recognition',
                'title': 'Outstanding Customer Service',
                'content': 'Received positive feedback from client regarding exceptional service delivery.'
            },
            {
                'note_type': 'coaching',
                'title': 'Leadership Development',
                'content': 'Provided coaching on leadership techniques and management best practices.'
            }
        ]
        
        for i, employee in enumerate(employees):
            # Create 2-4 notes per employee
            for j in range(2 + (i % 3)):  # 2-4 notes
                template = note_templates[(i + j) % len(note_templates)]
                
                note_date = date.today() - timedelta(days=j*15 + i*5)
                
                note, created = PerformanceNote.objects.get_or_create(
                    employee=employee,
                    title=f"{template['title']} - {employee.first_name}",
                    date_observed=note_date,
                    defaults={
                        'author': admin_user,
                        'note_type': template['note_type'],
                        'content': template['content'],
                        'is_private': j % 3 == 0,  # Some notes are private
                        'goal': PerformanceGoal.objects.filter(employee=employee).first() if j == 0 else None,
                        'review': PerformanceReview.objects.filter(employee=employee).first() if j == 1 else None
                    }
                )
                if created:
                    note_count += 1
                    self.stdout.write(f"  Created note '{note.title}' for {employee.full_name}")
        
        self.stdout.write(self.style.SUCCESS(f"\nSample performance data creation completed!"))
        self.stdout.write(self.style.SUCCESS(f"Created {review_count} performance reviews"))
        self.stdout.write(self.style.SUCCESS(f"Created {goal_count} performance goals"))
        self.stdout.write(self.style.SUCCESS(f"Created {note_count} performance notes"))
        
        # Display summary statistics
        self.stdout.write(f"\nDatabase Summary:")
        self.stdout.write(f"Total Employees: {Employee.objects.count()}")
        self.stdout.write(f"Total Performance Reviews: {PerformanceReview.objects.count()}")
        self.stdout.write(f"Total Performance Goals: {PerformanceGoal.objects.count()}")
        self.stdout.write(f"Total Performance Notes: {PerformanceNote.objects.count()}")
