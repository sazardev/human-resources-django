#!/usr/bin/env python
"""
Test script to verify Dynamic Field Selection is working across all apps
Tests the ?fields= and ?exclude= functionality for leaves and payroll apps
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from django.contrib.auth import authenticate
from django.test import Client
from employees.models import Employee
from leaves.models import LeaveType, LeaveRequest, LeaveBalance
from payroll.models import PayrollPeriod, TaxBracket, Payslip


def test_dynamic_fields_api():
    """Test dynamic field selection via HTTP API"""
    
    base_url = 'http://127.0.0.1:8000/api'
    
    print("🧪 TESTING DYNAMIC FIELD SELECTION ACROSS ALL APPS")
    print("=" * 60)
    
    # Test data for different endpoints
    test_endpoints = [
        # Leaves app endpoints
        {
            'name': 'Leaves - LeaveTypes',
            'url': f'{base_url}/leaves/leave-types/',
            'fields_test': 'id,name,description',
            'exclude_test': 'created_at,updated_at,color_code'
        },
        {
            'name': 'Leaves - LeaveRequests', 
            'url': f'{base_url}/leaves/leave-requests/',
            'fields_test': 'id,employee,status,start_date',
            'exclude_test': 'created_at,updated_at,comments'
        },
        {
            'name': 'Leaves - LeaveBalances',
            'url': f'{base_url}/leaves/leave-balances/',
            'fields_test': 'id,employee,leave_type,current_balance',
            'exclude_test': 'created_at,updated_at,carry_over_balance'
        },
        
        # Payroll app endpoints
        {
            'name': 'Payroll - PayrollPeriods',
            'url': f'{base_url}/payroll/payroll-periods/',
            'fields_test': 'id,name,start_date,end_date',
            'exclude_test': 'created_at,updated_at,description'
        },
        {
            'name': 'Payroll - TaxBrackets',
            'url': f'{base_url}/payroll/tax-brackets/',
            'fields_test': 'id,name,min_income,max_income',
            'exclude_test': 'created_at,updated_at,description'
        },
        {
            'name': 'Payroll - Payslips',
            'url': f'{base_url}/payroll/payslips/',
            'fields_test': 'id,employee,payroll_period,gross_salary',
            'exclude_test': 'created_at,updated_at,calculation_notes'
        },
        
        # Employees for comparison (already working)
        {
            'name': 'Employees - Employees',
            'url': f'{base_url}/employees/employees/',
            'fields_test': 'id,first_name,last_name,email',
            'exclude_test': 'created_at,updated_at,phone'
        }
    ]
    
    results = []
    
    for endpoint in test_endpoints:
        print(f"\n🔍 Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            # Test 1: Fields selection
            fields_url = f"{endpoint['url']}?fields={endpoint['fields_test']}"
            print(f"   Fields test: ?fields={endpoint['fields_test']}")
            
            response = requests.get(fields_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    first_item = data['results'][0]
                    expected_fields = set(endpoint['fields_test'].split(','))
                    actual_fields = set(first_item.keys())
                    
                    if expected_fields.issubset(actual_fields):
                        print(f"   ✅ Fields selection WORKING")
                        fields_status = "✅ PASS"
                    else:
                        print(f"   ❌ Fields selection FAILED")
                        print(f"      Expected: {expected_fields}")
                        print(f"      Got: {actual_fields}")
                        fields_status = "❌ FAIL"
                else:
                    print(f"   ⚠️  No data to test fields selection")
                    fields_status = "⚠️ NO DATA"
            else:
                print(f"   ❌ HTTP Error {response.status_code}")
                fields_status = f"❌ HTTP {response.status_code}"
            
            # Test 2: Exclude selection  
            exclude_url = f"{endpoint['url']}?exclude={endpoint['exclude_test']}"
            print(f"   Exclude test: ?exclude={endpoint['exclude_test']}")
            
            response = requests.get(exclude_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    first_item = data['results'][0]
                    excluded_fields = set(endpoint['exclude_test'].split(','))
                    actual_fields = set(first_item.keys())
                    
                    if excluded_fields.isdisjoint(actual_fields):
                        print(f"   ✅ Exclude selection WORKING")
                        exclude_status = "✅ PASS"
                    else:
                        print(f"   ❌ Exclude selection FAILED")
                        print(f"      Should exclude: {excluded_fields}")
                        print(f"      But found: {excluded_fields & actual_fields}")
                        exclude_status = "❌ FAIL"
                else:
                    print(f"   ⚠️  No data to test exclude selection")
                    exclude_status = "⚠️ NO DATA"
            else:
                print(f"   ❌ HTTP Error {response.status_code}")
                exclude_status = f"❌ HTTP {response.status_code}"
            
            results.append({
                'endpoint': endpoint['name'],
                'fields_status': fields_status,
                'exclude_status': exclude_status
            })
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
            results.append({
                'endpoint': endpoint['name'],
                'fields_status': "❌ CONNECTION ERROR",
                'exclude_status': "❌ CONNECTION ERROR"
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DYNAMIC FIELDS TEST SUMMARY")
    print("=" * 60)
    
    for result in results:
        print(f"• {result['endpoint']}")
        print(f"  Fields:  {result['fields_status']}")
        print(f"  Exclude: {result['exclude_status']}")
    
    # Overall status
    all_pass = all(
        'PASS' in result['fields_status'] and 'PASS' in result['exclude_status']
        for result in results
    )
    
    print("\n" + "=" * 60)
    if all_pass:
        print("🎉 ALL TESTS PASSED! Dynamic field selection working across all apps!")
    else:
        print("⚠️  Some tests failed or have issues. Check details above.")
    print("=" * 60)
    
    return results


def test_nested_field_selection():
    """Test nested field selection like department.name"""
    
    print("\n🔗 TESTING NESTED FIELD SELECTION")
    print("=" * 40)
    
    base_url = 'http://127.0.0.1:8000/api'
    
    # Test nested fields
    nested_tests = [
        {
            'name': 'Employees with Department Name',
            'url': f'{base_url}/employees/employees/?fields=id,first_name,department.name',
            'expected_nested': 'department'
        },
        {
            'name': 'Leave Requests with Employee Name',
            'url': f'{base_url}/leaves/leave-requests/?fields=id,status,employee.first_name',
            'expected_nested': 'employee'
        }
    ]
    
    for test in nested_tests:
        print(f"\n🔍 {test['name']}")
        try:
            response = requests.get(test['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    first_item = data['results'][0]
                    if test['expected_nested'] in first_item:
                        print("   ✅ Nested field selection WORKING")
                    else:
                        print("   ❌ Nested field not found")
                else:
                    print("   ⚠️  No data to test")
            else:
                print(f"   ❌ HTTP Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Dynamic Field Selection Test")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check server availability
    try:
        response = requests.get('http://127.0.0.1:8000/api/', timeout=5)
        print(f"✅ Server is running (HTTP {response.status_code})")
    except:
        print("❌ Server is not running on http://127.0.0.1:8000")
        print("   Please start the Django development server first")
        sys.exit(1)
    
    # Run tests
    test_dynamic_fields_api()
    test_nested_field_selection()
    
    print(f"\n🏁 Test completed at {datetime.now().strftime('%H:%M:%S')}")
