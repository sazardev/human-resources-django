"""
Test Django attendance endpoints using shell commands
"""
# Test WorkSchedule model
from attendance.models import WorkSchedule
from employees.models import Employee, Department
from django.contrib.auth.models import User

print("=== WorkSchedule Model Test ===")
schedules = WorkSchedule.objects.all()
print(f"Total WorkSchedules: {schedules.count()}")
for schedule in schedules:
    print(f"  - {schedule.name}: {schedule.department.name} ({schedule.schedule_type})")

print("\n=== User and Employee Test ===")
users = User.objects.all()
print(f"Total Users: {users.count()}")
for user in users[:3]:  # Show first 3
    print(f"  - {user.username}: {user.get_full_name()}")
    try:
        employee = user.employee_profile
        print(f"    Employee: {employee.employee_id} in {employee.department.name}")
    except Exception as e:
        print(f"    No employee profile: {e}")

print("\n=== Department Test ===")
departments = Department.objects.all()
print(f"Total Departments: {departments.count()}")
for dept in departments:
    print(f"  - {dept.name}: {dept.employees.count()} employees")

print("\n=== API Endpoint Structure Test ===")
# Test that ViewSets are importable
try:
    from attendance.views import WorkScheduleViewSet
    print("✓ WorkScheduleViewSet imported successfully")
    
    # Check filterset_fields
    viewset = WorkScheduleViewSet()
    print(f"  filterset_fields: {getattr(viewset, 'filterset_fields', 'Not set')}")
    print(f"  search_fields: {getattr(viewset, 'search_fields', 'Not set')}")
    print(f"  ordering_fields: {getattr(viewset, 'ordering_fields', 'Not set')}")
    
except Exception as e:
    print(f"✗ Error importing WorkScheduleViewSet: {e}")

try:
    from attendance.views import TimeEntryViewSet
    print("✓ TimeEntryViewSet imported successfully")
except Exception as e:
    print(f"✗ Error importing TimeEntryViewSet: {e}")

try:
    from attendance.views import TimesheetViewSet
    print("✓ TimesheetViewSet imported successfully")
except Exception as e:
    print(f"✗ Error importing TimesheetViewSet: {e}")

print("\n=== Test Complete ===")
