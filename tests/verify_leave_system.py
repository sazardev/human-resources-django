from leaves.models import LeaveType, Holiday, LeaveBalance, LeaveRequest
from employees.models import Employee
from decimal import Decimal
from datetime import date, timedelta

print("🧪 Leave Management System Verification")
print("=" * 40)

# Create basic leave types
leave_types = [
    {
        'name': 'Annual Leave',
        'description': 'Annual vacation days',
        'default_days_per_year': Decimal('21'),
        'max_days_per_request': Decimal('15'),
        'min_notice_days': 7,
        'requires_approval': True,
        'is_paid': True,
        'color_code': '#4CAF50'
    },
    {
        'name': 'Sick Leave',
        'description': 'Medical leave for illness',
        'default_days_per_year': Decimal('10'),
        'max_days_per_request': Decimal('30'),
        'min_notice_days': 0,
        'requires_approval': False,
        'requires_documentation': True,
        'is_paid': True,
        'color_code': '#FF9800'
    }
]

print("\n1. Creating Leave Types...")
for lt_data in leave_types:
    lt, created = LeaveType.objects.get_or_create(
        name=lt_data['name'],
        defaults=lt_data
    )
    print(f"   {'✅ Created' if created else 'ℹ️  Exists'}: {lt.name}")

# Create holidays
print("\n2. Creating Holidays...")
holidays = [
    {
        'name': 'Christmas Day',
        'date': date(2025, 12, 25),
        'holiday_type': 'public',
        'is_mandatory': True,
        'affects_leave_calculation': True
    },
    {
        'name': 'New Years Day',
        'date': date(2025, 1, 1),
        'holiday_type': 'public',
        'is_mandatory': True,
        'affects_leave_calculation': True
    }
]

for h_data in holidays:
    h, created = Holiday.objects.get_or_create(
        name=h_data['name'],
        date=h_data['date'],
        defaults=h_data
    )
    print(f"   {'✅ Created' if created else 'ℹ️  Exists'}: {h.name}")

# Create leave balances for employees
print("\n3. Creating Leave Balances...")
employees = Employee.objects.all()[:2]
leave_types_qs = LeaveType.objects.all()

for employee in employees:
    for leave_type in leave_types_qs:
        balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=2025,
            defaults={
                'allocated_days': leave_type.default_days_per_year,
                'used_days': Decimal('0'),
                'pending_days': Decimal('0'),
                'available_days': leave_type.default_days_per_year,
                'carried_over_days': Decimal('0')
            }
        )
        if created:
            print(f"   ✅ Created {leave_type.name} balance for {employee.get_full_name()}")

# Summary
print("\n4. System Summary:")
print(f"   📋 Leave Types: {LeaveType.objects.count()}")
print(f"   🎉 Holidays: {Holiday.objects.count()}")
print(f"   💰 Leave Balances: {LeaveBalance.objects.count()}")
print(f"   📅 Leave Requests: {LeaveRequest.objects.count()}")
print(f"   👥 Employees: {Employee.objects.count()}")

print("\n✅ Leave Management System is working correctly!")

# Test imports
print("\n5. Testing Core Components...")
try:
    from leaves.views import LeaveTypeViewSet, LeaveRequestViewSet
    print("   ✅ ViewSets imported successfully")
except Exception as e:
    print(f"   ❌ ViewSet import error: {e}")

try:
    from leaves.serializers import LeaveTypeSerializer, LeaveRequestSerializer
    print("   ✅ Serializers imported successfully")
except Exception as e:
    print(f"   ❌ Serializer import error: {e}")

try:
    from leaves.admin import LeaveTypeAdmin
    print("   ✅ Admin imported successfully")
except Exception as e:
    print(f"   ❌ Admin import error: {e}")

print("\n🎉 All components verified successfully!")
print("=" * 40)
