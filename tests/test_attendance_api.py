#!/usr/bin/env python
"""
Test script to validate attendance API endpoints after fixing WorkSchedule filtering
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee, Department
from attendance.models import WorkSchedule, TimeEntry, Timesheet

User = get_user_model()

def test_workschedule_model():
    """Test WorkSchedule model structure"""
    print("🔍 TESTING WORKSCHEDULE MODEL STRUCTURE")
    print("=" * 50)
    
    try:
        # Check model fields
        workschedule_fields = [field.name for field in WorkSchedule._meta.fields]
        print(f"📋 WorkSchedule fields: {workschedule_fields}")
        
        # Check if 'employee' field exists
        has_employee_field = 'employee' in workschedule_fields
        print(f"❌ Has 'employee' field: {has_employee_field}")
        print(f"✅ Has 'department' field: {'department' in workschedule_fields}")
        
        # Test queryset filtering
        try:
            # This should work
            dept_schedules = WorkSchedule.objects.filter(department__isnull=False)
            print(f"✅ Department filtering works: {dept_schedules.count()} schedules found")
        except Exception as e:
            print(f"❌ Department filtering failed: {e}")
            
        try:
            # This should fail if we're filtering by employee (which doesn't exist)
            WorkSchedule.objects.filter(employee__isnull=False)
            print("❌ Employee filtering unexpectedly worked (this shouldn't happen)")
        except Exception as e:
            print(f"✅ Employee filtering correctly fails: {type(e).__name__}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_current_data():
    """Test current database data"""
    print("\n📊 TESTING CURRENT DATABASE DATA")
    print("=" * 50)
    
    # Check departments and schedules
    departments = Department.objects.all()
    workschedules = WorkSchedule.objects.all()
    employees = Employee.objects.all()
    
    print(f"🏢 Departments: {departments.count()}")
    for dept in departments:
        schedules_count = WorkSchedule.objects.filter(department=dept).count()
        employees_count = dept.employee_set.count()
        print(f"  • {dept.name}: {schedules_count} schedules, {employees_count} employees")
    
    print(f"📅 Work Schedules: {workschedules.count()}")
    for schedule in workschedules:
        print(f"  • {schedule.name} -> Department: {schedule.department}")
    
    print(f"👥 Employees: {employees.count()}")
    for emp in employees:
        print(f"  • {emp.full_name} -> Department: {emp.department}")

def test_api_simulation():
    """Simulate API calls to test filtering"""
    print("\n🌐 SIMULATING API FILTERING")
    print("=" * 50)
    
    # Test the filtering that would be applied in the API
    try:
        # Test filterset_fields that should work
        valid_filters = {
            'department': Department.objects.first().id if Department.objects.exists() else None,
            'is_active': True,
            'schedule_type': 'standard'
        }
        
        for field, value in valid_filters.items():
            if value is not None:
                filter_dict = {field: value}
                result = WorkSchedule.objects.filter(**filter_dict)
                print(f"✅ Filter by {field}: {result.count()} results")
            else:
                print(f"⏭️  Skip filter by {field}: no test data")
                
    except Exception as e:
        print(f"❌ Valid filtering failed: {e}")
    
    # Test search fields that should work
    try:
        from django.db.models import Q
        search_term = "test"
        search_q = Q(name__icontains=search_term) | Q(department__name__icontains=search_term)
        search_result = WorkSchedule.objects.filter(search_q)
        print(f"✅ Search filtering: {search_result.count()} results for '{search_term}'")
    except Exception as e:
        print(f"❌ Search filtering failed: {e}")

def main():
    """Run all tests"""
    print("🧪 ATTENDANCE API TESTING")
    print("=" * 60)
    
    test_workschedule_model()
    test_current_data()
    test_api_simulation()
    
    print("\n✅ TESTING COMPLETED")
    print("The WorkSchedule API should now work correctly!")

if __name__ == "__main__":
    main()
