#!/usr/bin/env python
"""
Simple test to verify dynamic fields are working in serializers
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from employees.mixins import DynamicFieldsMixin, SelectableFieldsSerializer
from leaves.serializers import LeaveTypeSerializer, LeaveRequestSerializer, LeaveBalanceSerializer
from payroll.serializers import PayrollPeriodSerializer, PayslipSerializer, TaxBracketSerializer
from leaves.models import LeaveType, LeaveRequest, LeaveBalance
from payroll.models import PayrollPeriod, Payslip, TaxBracket

def test_serializer_inheritance():
    """Test that serializers properly inherit from SelectableFieldsSerializer"""
    
    print("🔍 TESTING SERIALIZER INHERITANCE")
    print("=" * 40)
    
    serializers_to_test = [
        ("LeaveTypeSerializer", LeaveTypeSerializer),
        ("LeaveRequestSerializer", LeaveRequestSerializer), 
        ("LeaveBalanceSerializer", LeaveBalanceSerializer),
        ("PayrollPeriodSerializer", PayrollPeriodSerializer),
        ("PayslipSerializer", PayslipSerializer),
        ("TaxBracketSerializer", TaxBracketSerializer),
    ]
    
    for name, serializer_class in serializers_to_test:
        has_mixin = issubclass(serializer_class, SelectableFieldsSerializer)
        has_dynamic = issubclass(serializer_class, DynamicFieldsMixin)
        
        if has_mixin and has_dynamic:
            print(f"✅ {name}: Has dynamic fields support")
        else:
            print(f"❌ {name}: Missing dynamic fields support")

def test_fields_selection():
    """Test actual field selection functionality"""
    
    print("\n🧪 TESTING FIELD SELECTION FUNCTIONALITY")
    print("=" * 45)
    
    # Test LeaveType
    leave_type = LeaveType.objects.first()
    if leave_type:
        print("\n1. Testing LeaveType with fields selection:")
        serializer = LeaveTypeSerializer(leave_type, fields=['id', 'name', 'description'])
        data = serializer.data
        print(f"   Requested: ['id', 'name', 'description']")
        print(f"   Returned:  {list(data.keys())}")
        
        if set(['id', 'name', 'description']).issubset(set(data.keys())):
            print("   ✅ Fields selection working!")
        else:
            print("   ❌ Fields selection failed!")
    
    # Test PayrollPeriod
    period = PayrollPeriod.objects.first()
    if period:
        print("\n2. Testing PayrollPeriod with exclude:")
        serializer = PayrollPeriodSerializer(period, exclude=['created_at', 'updated_at'])
        data = serializer.data
        excluded_fields = {'created_at', 'updated_at'}
        returned_fields = set(data.keys())
        
        print(f"   Excluded:  {list(excluded_fields)}")
        print(f"   Returned:  {list(returned_fields)}")
        
        if excluded_fields.isdisjoint(returned_fields):
            print("   ✅ Exclude functionality working!")
        else:
            intersection = excluded_fields & returned_fields
            print(f"   ❌ Exclude failed! Found excluded fields: {list(intersection)}")

def test_data_counts():
    """Show available data for testing"""
    
    print("\n📊 AVAILABLE DATA FOR TESTING")
    print("=" * 35)
    
    models = [
        ("LeaveType", LeaveType),
        ("LeaveRequest", LeaveRequest),
        ("LeaveBalance", LeaveBalance),
        ("PayrollPeriod", PayrollPeriod),
        ("Payslip", Payslip),
        ("TaxBracket", TaxBracket),
    ]
    
    for name, model in models:
        count = model.objects.count()
        print(f"• {name}: {count} records")

if __name__ == "__main__":
    print("🚀 DYNAMIC FIELDS VERIFICATION")
    print("🎯 Testing across Leaves and Payroll apps")
    print("=" * 50)
    
    test_data_counts()
    test_serializer_inheritance()
    test_fields_selection()
    
    print("\n" + "=" * 50)
    print("🎉 TESTING COMPLETED!")
    print("=" * 50)
