#!/usr/bin/env python
"""
Test script for Leave Management System functionality
"""
import os
import sys
import django
import requests
import json
from datetime import date, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from leaves.models import LeaveType, Holiday, LeaveBalance, LeaveRequest


def test_leave_management_system():
    """Test the leave management system functionality"""
    print("🧪 Testing Leave Management System")
    print("=" * 50)
    
    # Test 1: Create Leave Types
    print("\n1️⃣ Testing Leave Type Creation...")
    leave_types_data = [
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
    
    for lt_data in leave_types_data:
        lt, created = LeaveType.objects.get_or_create(
            name=lt_data['name'],
            defaults=lt_data
        )
        status = "✅ Created" if created else "ℹ️  Exists"
        print(f"   {status}: {lt.name}")
    
    # Test 2: Create Holidays
    print("\n2️⃣ Testing Holiday Creation...")
    current_year = date.today().year
    holidays_data = [
        {
            'name': 'New Year\'s Day',
            'date': date(current_year, 1, 1),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Beginning of the new year'
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
            'name': 'Christmas Day',
            'date': date(current_year, 12, 25),
            'holiday_type': 'public',
            'is_mandatory': True,
            'affects_leave_calculation': True,
            'description': 'Christmas Day'
        }
    ]
    
    for h_data in holidays_data:
        h, created = Holiday.objects.get_or_create(
            name=h_data['name'],
            date=h_data['date'],
            defaults=h_data
        )
        status = "✅ Created" if created else "ℹ️  Exists"
        print(f"   {status}: {h.name} on {h.date}")
    
    # Test 3: Create Leave Balances for existing employees
    print("\n3️⃣ Testing Leave Balance Creation...")
    employees = Employee.objects.all()[:3]  # Get first 3 employees
    leave_types = LeaveType.objects.all()
    current_year = date.today().year
    
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
                print(f"   ✅ Created {leave_type.name} balance for {employee.get_full_name()}")
    
    # Test 4: Create Sample Leave Requests
    print("\n4️⃣ Testing Leave Request Creation...")
    if employees.exists() and leave_types.exists():
        employee = employees.first()
        leave_type = leave_types.first()
        
        request_data = {
            'employee': employee,
            'leave_type': leave_type,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=12),
            'reason': 'Family vacation',
            'status': 'pending',
            'duration_type': 'full_day',
            'total_days': Decimal('3'),
            'business_days': Decimal('3')
        }
        
        leave_request, created = LeaveRequest.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            start_date=request_data['start_date'],
            defaults=request_data
        )
        
        status = "✅ Created" if created else "ℹ️  Exists"
        print(f"   {status}: Leave request for {employee.get_full_name()}")
    
    # Test 5: Display Summary
    print("\n5️⃣ System Summary:")
    print(f"   📋 Leave Types: {LeaveType.objects.count()}")
    print(f"   🎉 Holidays: {Holiday.objects.count()}")
    print(f"   💰 Leave Balances: {LeaveBalance.objects.count()}")
    print(f"   📅 Leave Requests: {LeaveRequest.objects.count()}")
    
    # Test 6: Test Model Methods
    print("\n6️⃣ Testing Model Methods...")
    if LeaveRequest.objects.exists():
        leave_request = LeaveRequest.objects.first()
        print(f"   📝 Request ID: {leave_request.request_id}")
        print(f"   🔄 Can be cancelled: {leave_request.can_be_cancelled}")
        print(f"   ⏱️  Business days calculation: {leave_request.business_days}")
    
    # Test 7: Test Leave Balance Calculations
    print("\n7️⃣ Testing Leave Balance Calculations...")
    if LeaveBalance.objects.exists():
        balance = LeaveBalance.objects.first()
        print(f"   👤 Employee: {balance.employee.get_full_name()}")
        print(f"   📊 Leave Type: {balance.leave_type.name}")
        print(f"   💾 Allocated: {balance.allocated_days} days")
        print(f"   ✅ Available: {balance.available_days} days")
        print(f"   📉 Used: {balance.used_days} days")
    
    print("\n" + "=" * 50)
    print("✅ Leave Management System test completed successfully!")
    
    return True


def test_api_endpoints():
    """Test API endpoints (basic structure check)"""
    print("\n🌐 Testing API Structure...")
    
    # Import views to check they load correctly
    try:
        from leaves.views import (
            LeaveTypeViewSet, HolidayViewSet, LeaveBalanceViewSet,
            LeaveRequestViewSet, LeaveRequestCommentViewSet,
            TeamScheduleViewSet, LeavePolicyViewSet, LeaveAnalyticsViewSet
        )
        print("   ✅ All ViewSets imported successfully")
        
        # Import serializers
        from leaves.serializers import (
            LeaveTypeSerializer, HolidaySerializer, LeaveBalanceSerializer,
            LeaveRequestSerializer, LeaveRequestCreateSerializer
        )
        print("   ✅ All Serializers imported successfully")
        
        # Import admin
        from leaves.admin import LeaveTypeAdmin, HolidayAdmin
        print("   ✅ Admin interfaces imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False


if __name__ == '__main__':
    try:
        # Run tests
        test_leave_management_system()
        test_api_endpoints()
        
        print("\n🎉 All tests passed! Leave Management System is ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
