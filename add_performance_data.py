import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, PerformanceGoal, PerformanceNote
from datetime import date, timedelta

# Get admin user and employees
admin_user = User.objects.get(username='hr_admin')
employees = Employee.objects.all()

print(f"Creating performance data for {employees.count()} employees...")

# Create performance goals
goal_count = 0
for i, employee in enumerate(employees):
    # Create 2 goals per employee
    goals_data = [
        {
            'title': f'Complete Training - {employee.first_name}',
            'description': 'Complete advanced technical training course',
            'category': 'skill_development',
            'priority': 'high',
            'status': 'in_progress',
            'progress_percentage': 50,
            'days_from_now': 90
        },
        {
            'title': f'Lead Project - {employee.first_name}',
            'description': 'Lead a cross-functional project',
            'category': 'leadership',
            'priority': 'medium',
            'status': 'pending',
            'progress_percentage': 10,
            'days_from_now': 120
        }
    ]
    
    for j, goal_data in enumerate(goals_data):
        goal, created = PerformanceGoal.objects.get_or_create(
            employee=employee,
            title=goal_data['title'],
            defaults={
                'description': goal_data['description'],
                'category': goal_data['category'],
                'priority': goal_data['priority'],
                'start_date': date.today() - timedelta(days=30),
                'target_date': date.today() + timedelta(days=goal_data['days_from_now']),
                'status': goal_data['status'],
                'progress_percentage': goal_data['progress_percentage'],
                'success_criteria': 'Complete successfully with measurable outcomes',
                'created_by': admin_user
            }
        )
        if created:
            goal_count += 1
            print(f"  Created goal: {goal.title}")

# Create performance notes
note_count = 0
for i, employee in enumerate(employees):
    # Create 2 notes per employee
    notes_data = [
        {
            'note_type': 'achievement',
            'title': f'Excellent Performance - {employee.first_name}',
            'content': 'Demonstrated excellent performance in recent project delivery.'
        },
        {
            'note_type': 'feedback',
            'title': f'Development Areas - {employee.first_name}',
            'content': 'Areas identified for professional development and growth.'
        }
    ]
    
    for j, note_data in enumerate(notes_data):
        note, created = PerformanceNote.objects.get_or_create(
            employee=employee,
            title=note_data['title'],
            defaults={
                'author': admin_user,
                'note_type': note_data['note_type'],
                'content': note_data['content'],
                'date_observed': date.today() - timedelta(days=j*15),
                'is_private': j % 2 == 0
            }
        )
        if created:
            note_count += 1
            print(f"  Created note: {note.title}")

print(f"\nPerformance data creation completed!")
print(f"Created {goal_count} performance goals")
print(f"Created {note_count} performance notes")

# Print summary
from employees.models import PerformanceReview
print(f"\nDatabase Summary:")
print(f"Total Employees: {Employee.objects.count()}")
print(f"Total Performance Reviews: {PerformanceReview.objects.count()}")
print(f"Total Performance Goals: {PerformanceGoal.objects.count()}")
print(f"Total Performance Notes: {PerformanceNote.objects.count()}")
