#!/usr/bin/env python
"""
Simple script to create essential leave management data
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from leaves.models import LeaveType, Holiday
from employees.models import Employee, Department

def create_basic_leave_types():
    """Create basic leave types"""
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
        },
        {
            'name': 'Personal Leave',
            'description': 'Personal days for urgent matters',
            'default_days_per_year': Decimal('5'),
            'max_days_per_request': Decimal('3'),
            'min_notice_days': 1,
            'requires_approval': True,
            'is_paid': True,
            'color_code': '#2196F3'
        }
    ]
    
    for lt_data in leave_types:
        lt, created = LeaveType.objects.get_or_create(
            name=lt_data['name'],
            defaults=lt_data
        )
        if created:
            print(f"Created: {lt.name}")

def create_basic_holidays():
    """Create basic holidays"""
    current_year = date.today().year
    holidays = [
        {
            'name': 'New Year\'s Day',
            'date': date(current_year, 1, 1),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True
        },
        {
            'name': 'Independence Day',
            'date': date(current_year, 7, 4),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True
        },
        {
            'name': 'Christmas Day',
            'date': date(current_year, 12, 25),
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
        if created:
            print(f"Created holiday: {h.name}")

if __name__ == '__main__':
    print("Creating basic leave management data...")
    create_basic_leave_types()
    create_basic_holidays()
    print("Done!")
