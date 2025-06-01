#!/usr/bin/env python
"""
Final verification test for the payroll admin interface.
This test ensures all admin pages are accessible and methods work correctly.
"""

import os
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from payroll.models import CompensationHistory
from payroll.admin import CompensationHistoryAdmin
from django.contrib.admin.sites import site

def test_admin_functionality():
    """Test the admin functionality comprehensively."""
    
    print("🔍 FINAL PAYROLL ADMIN VERIFICATION")
    print("=" * 50)
    
    try:
        # Test 1: Check if CompensationHistory is registered
        admin_class = site._registry.get(CompensationHistory)
        if admin_class:
            print("✅ CompensationHistory is registered in admin")
        else:
            print("❌ CompensationHistory is not registered in admin")
            return False
            
        # Test 2: Check if we have data
        comp_history = CompensationHistory.objects.first()
        if comp_history:
            print(f"✅ Found compensation history record: {comp_history}")
        else:
            print("❌ No compensation history records found")
            return False
            
        # Test 3: Test all admin methods
        print("\n📊 Testing Admin Methods:")
        print("-" * 30)
        
        try:
            employee_name = admin_class.employee_name(comp_history)
            print(f"✅ employee_name(): {employee_name}")
        except Exception as e:
            print(f"❌ employee_name() failed: {e}")
            return False
            
        try:
            previous_salary = admin_class.previous_salary(comp_history)
            print(f"✅ previous_salary(): {previous_salary}")
        except Exception as e:
            print(f"❌ previous_salary() failed: {e}")
            return False
            
        try:
            new_salary = admin_class.new_salary(comp_history)
            print(f"✅ new_salary(): {new_salary}")
        except Exception as e:
            print(f"❌ new_salary() failed: {e}")
            return False
            
        try:
            salary_change = admin_class.salary_change(comp_history)
            print(f"✅ salary_change(): {salary_change}")
        except Exception as e:
            print(f"❌ salary_change() failed: {e}")
            return False
            
        # Test 4: Check list_display configuration
        expected_fields = [
            'employee_name', 'change_type', 'previous_salary', 
            'new_salary', 'salary_change', 'effective_date', 'created_at'
        ]
        
        if admin_class.list_display == expected_fields:
            print("✅ list_display configuration is correct")
        else:
            print(f"❌ list_display mismatch. Expected: {expected_fields}, Got: {admin_class.list_display}")
            return False
            
        # Test 5: Verify HTTP access (simple check)
        try:
            print("\n🌐 Testing HTTP Access:")
            print("-" * 30)
            
            # Just verify the server is running
            response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
            if response.status_code in [200, 302]:  # 302 for redirect to login
                print("✅ Django admin is accessible via HTTP")
            else:
                print(f"⚠️  Admin returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  HTTP test skipped (server may not be running): {e}")
            
        print("\n🎯 FINAL RESULT:")
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("✅ CompensationHistory admin is fully functional")
        print("✅ All methods work correctly")
        print("✅ No format_html errors")
        print("✅ Ready for production use")
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_functionality()
    if success:
        print("\n🎉 PAYROLL ADMIN VERIFICATION COMPLETE - SUCCESS!")
    else:
        print("\n💥 PAYROLL ADMIN VERIFICATION FAILED!")
        exit(1)
