#!/usr/bin/env python
"""
Script to create sample data for the Leave Management System
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, Department
from leaves.models import (
    LeaveType, Holiday, LeaveBalance, LeaveRequest, 
    LeaveRequestComment, TeamSchedule, LeavePolicy
)


def create_leave_types():
    """Create common leave types"""
    leave_types_data = [
        {
            'name': 'Annual Leave',
            'description': 'Annual vacation days',
            'default_days_per_year': Decimal('21'),
            'max_days_per_request': Decimal('15'),
            'min_notice_days': 7,
            'requires_approval': True,
            'requires_documentation': False,
            'is_paid': True,
            'carry_over_type': 'partial',
            'max_carry_over_days': Decimal('5'),
            'carry_over_expiry_months': 3,
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
            'carry_over_type': 'none',
            'color_code': '#FF9800'
        },
        {
            'name': 'Personal Leave',
            'description': 'Personal days for urgent matters',
            'default_days_per_year': Decimal('5'),
            'max_days_per_request': Decimal('3'),
            'min_notice_days': 1,
            'requires_approval': True,
            'requires_documentation': False,
            'is_paid': True,
            'carry_over_type': 'none',
            'color_code': '#2196F3'
        },
        {
            'name': 'Maternity Leave',
            'description': 'Maternity leave for new mothers',
            'default_days_per_year': Decimal('90'),
            'max_days_per_request': Decimal('90'),
            'min_notice_days': 30,
            'requires_approval': True,
            'requires_documentation': True,
            'is_paid': True,
            'carry_over_type': 'none',
            'color_code': '#E91E63'
        },
        {
            'name': 'Paternity Leave',
            'description': 'Paternity leave for new fathers',
            'default_days_per_year': Decimal('14'),
            'max_days_per_request': Decimal('14'),
            'min_notice_days': 30,
            'requires_approval': True,
            'requires_documentation': True,
            'is_paid': True,
            'carry_over_type': 'none',
            'color_code': '#9C27B0'
        },
        {
            'name': 'Bereavement Leave',
            'description': 'Leave for family bereavement',
            'default_days_per_year': Decimal('3'),
            'max_days_per_request': Decimal('5'),
            'min_notice_days': 0,
            'requires_approval': True,
            'requires_documentation': True,
            'is_paid': True,
            'carry_over_type': 'none',
            'color_code': '#607D8B'
        },
        {
            'name': 'Study Leave',
            'description': 'Educational leave for professional development',
            'default_days_per_year': Decimal('5'),
            'max_days_per_request': Decimal('10'),
            'min_notice_days': 14,
            'requires_approval': True,
            'requires_documentation': True,
            'is_paid': False,
            'carry_over_type': 'full',
            'color_code': '#795548'
        }
    ]
    
    for leave_type_data in leave_types_data:
        leave_type, created = LeaveType.objects.get_or_create(
            name=leave_type_data['name'],
            defaults=leave_type_data
        )
        if created:
            print(f"✅ Created leave type: {leave_type.name}")
        else:
            print(f"ℹ️  Leave type already exists: {leave_type.name}")


def create_holidays():
    """Create sample holidays for current and next year"""
    current_year = date.today().year
    
    holidays_data = [
        # Current year holidays
        {
            'name': 'New Year\'s Day',
            'date': date(current_year, 1, 1),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Beginning of the new year'
        },
        {
            'name': 'Martin Luther King Jr. Day',
            'date': date(current_year, 1, 15),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Federal holiday honoring MLK Jr.'
        },
        {
            'name': 'Presidents Day',
            'date': date(current_year, 2, 19),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Federal holiday honoring US Presidents'
        },
        {
            'name': 'Memorial Day',
            'date': date(current_year, 5, 27),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Honoring fallen military personnel'
        },
        {
            'name': 'Independence Day',
            'date': date(current_year, 7, 4),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'US Independence Day'
        },
        {
            'name': 'Labor Day',
            'date': date(current_year, 9, 2),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Labor Day celebration'
        },
        {
            'name': 'Columbus Day',
            'date': date(current_year, 10, 14),
            'holiday_type': 'public',
            'is_mandatory': False,
            'affects_leave_calculation': True,
            'description': 'Columbus Day'
        },
        {
            'name': 'Veterans Day',
            'date': date(current_year, 11, 11),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Honoring military veterans'
        },
        {
            'name': 'Thanksgiving',
            'date': date(current_year, 11, 28),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Thanksgiving Day'
        },
        {
            'name': 'Christmas Day',
            'date': date(current_year, 12, 25),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Christmas Day'
        },
        # Company specific holidays
        {
            'name': 'Company Founding Day',
            'date': date(current_year, 6, 15),
            'holiday_type': 'company',
            'is_mandatory': False,
            'affects_leave_calculation': False,
            'description': 'Annual company celebration'
        },
        {
            'name': 'Black Friday',
            'date': date(current_year, 11, 29),
            'holiday_type': 'company',
            'is_mandatory': False,
            'affects_leave_calculation': False,
            'description': 'Optional company holiday'
        }
    ]
    
    for holiday_data in holidays_data:
        holiday, created = Holiday.objects.get_or_create(
            name=holiday_data['name'],
            date=holiday_data['date'],
            defaults=holiday_data
        )
        if created:
            print(f"✅ Created holiday: {holiday.name} on {holiday.date}")
        else:
            print(f"ℹ️  Holiday already exists: {holiday.name}")


def create_leave_policies():
    """Create leave policies for different departments"""
    departments = Department.objects.all()
    
    if not departments.exists():
        print("❌ No departments found. Please create departments first.")
        return
    
    policy_data = {
        'name': 'Standard Leave Policy',
        'description': 'Standard company leave policy for all employees',
        'is_active': True,
        'effective_from': date.today(),
        'probation_leave_allowed': False,
        'weekend_count_as_leave': False,
        'holiday_count_as_leave': False,
        'min_notice_hours': 24,
        'max_consecutive_days': Decimal('30'),
        'require_coverage_plan': True
    }
    
    for department in departments:
        policy, created = LeavePolicy.objects.get_or_create(
            name=f"{policy_data['name']} - {department.name}",
            department=department,
            defaults=policy_data
        )
        if created:
            print(f"✅ Created leave policy for {department.name}")
        else:
            print(f"ℹ️  Leave policy already exists for {department.name}")


def create_leave_balances():
    """Create leave balances for all employees"""
    employees = Employee.objects.all()
    leave_types = LeaveType.objects.filter(is_active=True)
    current_year = date.today().year
    
    if not employees.exists():
        print("❌ No employees found. Please create employees first.")
        return
    
    if not leave_types.exists():
        print("❌ No leave types found. Creating leave types first.")
        create_leave_types()
        leave_types = LeaveType.objects.filter(is_active=True)
    
    for employee in employees:
        for leave_type in leave_types:
            balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                year=current_year,
                defaults={
                    'allocated_days': leave_type.default_days_per_year,
                    'used_days': Decimal('0'),
                    'pending_days': Decimal('0'),
                    'available_days': leave_type.default_days_per_year,
                    'carried_over_days': Decimal('0')
                }
            )
            if created:
                print(f"✅ Created {leave_type.name} balance for {employee.get_full_name()}")


def create_sample_leave_requests():
    """Create sample leave requests with different statuses"""
    employees = Employee.objects.all()[:5]  # Get first 5 employees
    leave_types = LeaveType.objects.filter(is_active=True)
    
    if not employees.exists():
        print("❌ No employees found. Please create employees first.")
        return
    
    # Sample requests data
    requests_data = [
        {
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'reason': 'Family vacation trip',
            'status': 'pending',
            'duration_type': 'full_day'
        },
        {
            'start_date': date.today() + timedelta(days=20),
            'end_date': date.today() + timedelta(days=21),
            'reason': 'Doctor appointment and recovery',
            'status': 'approved',
            'duration_type': 'full_day'
        },
        {
            'start_date': date.today() + timedelta(days=5),
            'end_date': date.today() + timedelta(days=5),
            'reason': 'Personal matter',
            'status': 'pending',
            'duration_type': 'half_day'
        },
        {
            'start_date': date.today() - timedelta(days=5),
            'end_date': date.today() - timedelta(days=3),
            'reason': 'Sudden illness',
            'status': 'approved',
            'duration_type': 'full_day'
        },
        {
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=35),
            'reason': 'Extended vacation',
            'status': 'rejected',
            'duration_type': 'full_day'
        }
    ]
    
    for i, employee in enumerate(employees):
        if i < len(requests_data):
            request_data = requests_data[i]
            leave_type = leave_types[i % leave_types.count()]
            
            # Calculate business days
            start_date = request_data['start_date']
            end_date = request_data['end_date']
            total_days = Decimal(str((end_date - start_date).days + 1))
            
            if request_data['duration_type'] == 'half_day':
                total_days = Decimal('0.5')
            
            leave_request, created = LeaveRequest.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                defaults={
                    'reason': request_data['reason'],
                    'status': request_data['status'],
                    'duration_type': request_data['duration_type'],
                    'total_days': total_days,
                    'business_days': total_days,
                    'submitted_at': date.today()
                }
            )
            
            if created:
                print(f"✅ Created leave request for {employee.get_full_name()}: {leave_type.name}")
                
                # Add comments for some requests
                if request_data['status'] == 'approved':
                    LeaveRequestComment.objects.create(
                        leave_request=leave_request,
                        commented_by=employee,
                        comment="Request approved. Enjoy your time off!",
                        is_internal=False
                    )
                elif request_data['status'] == 'rejected':
                    LeaveRequestComment.objects.create(
                        leave_request=leave_request,
                        commented_by=employee,
                        comment="Request rejected due to team coverage requirements.",
                        is_internal=True
                    )


def main():
    """Main function to create all sample data"""
    print("🚀 Creating Leave Management Sample Data...")
    print("=" * 50)
    
    try:
        # Create leave types
        print("\n📋 Creating Leave Types...")
        create_leave_types()
        
        # Create holidays
        print("\n🎉 Creating Holidays...")
        create_holidays()
        
        # Create leave policies
        print("\n📝 Creating Leave Policies...")
        create_leave_policies()
        
        # Create leave balances
        print("\n💰 Creating Leave Balances...")
        create_leave_balances()
        
        # Create sample leave requests
        print("\n📅 Creating Sample Leave Requests...")
        create_sample_leave_requests()
        
        print("\n" + "=" * 50)
        print("✅ Leave Management sample data created successfully!")
        
        # Print summary
        print("\n📊 Summary:")
        print(f"   Leave Types: {LeaveType.objects.count()}")
        print(f"   Holidays: {Holiday.objects.count()}")
        print(f"   Leave Policies: {LeavePolicy.objects.count()}")
        print(f"   Leave Balances: {LeaveBalance.objects.count()}")
        print(f"   Leave Requests: {LeaveRequest.objects.count()}")
        print(f"   Leave Comments: {LeaveRequestComment.objects.count()}")
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
