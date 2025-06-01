#!/usr/bin/env python
"""
Simple test script to validate WorkSchedule API fixes
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee, Department
from attendance.models import WorkSchedule, TimeEntry, Timesheet

User = get_user_model()

def test_workschedule_fields():
    """Test WorkSchedule model structure"""
    print("TESTING WORKSCHEDULE MODEL STRUCTURE")
    print("=" * 50)
    
    # Check model fields
    workschedule_fields = [field.name for field in WorkSchedule._meta.fields]
    print(f"WorkSchedule fields: {workschedule_fields}")
    
    # Check if 'employee' field exists
    has_employee_field = 'employee' in workschedule_fields
    has_department_field = 'department' in workschedule_fields
    
    print(f"Has 'employee' field: {has_employee_field}")
    print(f"Has 'department' field: {has_department_field}")
    
    if not has_employee_field and has_department_field:
        print("SUCCESS: Model structure is correct!")
    else:
        print("WARNING: Model structure might have issues")

def test_filtering():
    """Test filtering capabilities"""
    print("\nTESTING FILTERING")
    print("=" * 50)
    
    try:
        # Test valid filters
        dept_filter = WorkSchedule.objects.filter(department__isnull=False)
        active_filter = WorkSchedule.objects.filter(is_active=True)
        type_filter = WorkSchedule.objects.filter(schedule_type='standard')
        
        print(f"Department filter works: {dept_filter.count()} results")
        print(f"Active filter works: {active_filter.count()} results") 
        print(f"Type filter works: {type_filter.count()} results")
        
        print("SUCCESS: All valid filters work!")
        
    except Exception as e:
        print(f"ERROR in valid filtering: {e}")
    
    try:
        # Test invalid filter (should fail)
        WorkSchedule.objects.filter(employee__isnull=False)
        print("WARNING: Employee filter worked (it shouldn't!)")
    except Exception as e:
        print(f"SUCCESS: Employee filter correctly fails ({type(e).__name__})")

def test_data():
    """Test current data"""
    print("\nTESTING CURRENT DATA")
    print("=" * 50)
    
    departments = Department.objects.all()
    workschedules = WorkSchedule.objects.all()
    employees = Employee.objects.all()
    
    print(f"Departments: {departments.count()}")
    print(f"WorkSchedules: {workschedules.count()}")
    print(f"Employees: {employees.count()}")
    
    if workschedules.exists():
        for schedule in workschedules:
            print(f"  Schedule: {schedule.name} -> Dept: {schedule.department}")

if __name__ == "__main__":
    print("ATTENDANCE API VALIDATION")
    print("=" * 60)
    
    test_workschedule_fields()
    test_filtering()
    test_data()
    
    print("\nTEST COMPLETED!")
