#!/usr/bin/env python
"""
Simple test script to debug dynamic field selection
"""
import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.request import Request
from employees.models import Employee
from employees.serializers import EmployeeSerializer


def test_field_selection():
    """Test dynamic field selection functionality"""
    print("🔍 Debugging Dynamic Field Selection\n")
    
    # Get an employee
    employee = Employee.objects.first()
    if not employee:
        print("❌ No employees found. Create some data first.")
        return
    
    # Test 1: Normal serialization (all fields)
    print("📋 Test 1: Normal serialization (all fields)")
    factory = RequestFactory()
    request = factory.get('/api/employees/')
    drf_request = Request(request)
    
    serializer = EmployeeSerializer(employee, context={'request': drf_request})
    data = serializer.data
    print(f"   All fields: {list(data.keys())}")
    print(f"   Total fields: {len(data.keys())}")
    print()
    
    # Test 2: Field selection
    print("📋 Test 2: Field selection with ?fields=id,first_name,last_name")
    request = factory.get('/api/employees/?fields=id,first_name,last_name')
    drf_request = Request(request)
    
    # Debug the request
    print(f"   Request query params: {drf_request.query_params}")
    print(f"   Fields parameter: {drf_request.query_params.get('fields')}")
    
    serializer = EmployeeSerializer(employee, context={'request': drf_request})
    
    # Debug the serializer initialization
    print(f"   Serializer fields after init: {list(serializer.fields.keys())}")
    
    data = serializer.data
    print(f"   Filtered fields: {list(data.keys())}")
    print(f"   Total fields: {len(data.keys())}")
    print()
    
    # Test 3: Field exclusion
    print("📋 Test 3: Field exclusion with ?exclude=salary,address")
    request = factory.get('/api/employees/?exclude=salary,address')
    drf_request = Request(request)
    
    serializer = EmployeeSerializer(employee, context={'request': drf_request})
    data = serializer.data
    print(f"   Fields after exclusion: {list(data.keys())}")
    has_excluded = any(field in data.keys() for field in ['salary', 'address'])
    print(f"   Contains excluded fields: {has_excluded}")
    print()


if __name__ == "__main__":
    test_field_selection()
