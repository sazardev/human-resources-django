from leaves.models import LeaveType, Holiday
from decimal import Decimal
from datetime import date

# Create Annual Leave
lt1, created = LeaveType.objects.get_or_create(
    name='Annual Leave',
    defaults={
        'description': 'Annual vacation days',
        'default_days_per_year': Decimal('21'),
        'max_days_per_request': Decimal('15'),
        'min_notice_days': 7,
        'requires_approval': True,
        'is_paid': True,
        'color_code': '#4CAF50'
    }
)
print(f'Annual Leave: {"created" if created else "exists"}')

# Create Sick Leave
lt2, created = LeaveType.objects.get_or_create(
    name='Sick Leave',
    defaults={
        'description': 'Medical leave for illness',
        'default_days_per_year': Decimal('10'),
        'max_days_per_request': Decimal('30'),
        'min_notice_days': 0,
        'requires_approval': False,
        'requires_documentation': True,
        'is_paid': True,
        'color_code': '#FF9800'
    }
)
print(f'Sick Leave: {"created" if created else "exists"}')

# Create Personal Leave
lt3, created = LeaveType.objects.get_or_create(
    name='Personal Leave',
    defaults={
        'description': 'Personal days for urgent matters',
        'default_days_per_year': Decimal('5'),
        'max_days_per_request': Decimal('3'),
        'min_notice_days': 1,
        'requires_approval': True,
        'is_paid': True,
        'color_code': '#2196F3'
    }
)
print(f'Personal Leave: {"created" if created else "exists"}')

# Create holidays
h1, created = Holiday.objects.get_or_create(
    name='Christmas Day',
    date=date(2025, 12, 25),
    defaults={
        'holiday_type': 'public',
        'is_mandatory': True,
        'affects_leave_calculation': True,
        'description': 'Christmas Day'
    }
)
print(f'Christmas Day: {"created" if created else "exists"}')

h2, created = Holiday.objects.get_or_create(
    name='New Years Day',
    date=date(2025, 1, 1),
    defaults={
        'holiday_type': 'public',
        'is_mandatory': True,
        'affects_leave_calculation': True,
        'description': 'New Year Day'
    }
)
print(f'New Years Day: {"created" if created else "exists"}')

print(f'Total Leave Types: {LeaveType.objects.count()}')
print(f'Total Holidays: {Holiday.objects.count()}')
