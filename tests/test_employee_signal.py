#!/usr/bin/env python
"""
Test script to verify the auto-creation signal for Employee profiles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from authentication.models import User
from employees.models import Employee

def test_employee_auto_creation():
    """Test that Employee profiles are automatically created when Users are created"""
    
    print("🧪 TESTING AUTO-CREATION SIGNAL")
    print("=" * 40)
    
    # Count existing users and employees
    initial_users = User.objects.count()
    initial_employees = Employee.objects.count()
    
    print(f"📊 Initial counts:")
    print(f"   Users: {initial_users}")
    print(f"   Employees: {initial_employees}")
    
    # Create a test user
    print(f"\n👤 Creating test user...")
    test_user = User.objects.create_user(
        username='testuser123',
        email='testuser123@example.com',
        first_name='Test',
        last_name='Signal',
        password='testpass123'
    )
    
    print(f"✅ User created: {test_user.username}")
    
    # Check if Employee was auto-created
    final_users = User.objects.count()
    final_employees = Employee.objects.count()
    
    print(f"\n📊 Final counts:")
    print(f"   Users: {final_users} (+{final_users - initial_users})")
    print(f"   Employees: {final_employees} (+{final_employees - initial_employees})")
    
    # Try to get the Employee profile
    try:
        employee = Employee.objects.get(user=test_user)
        print(f"\n✅ Employee profile auto-created!")
        print(f"   Employee ID: {employee.employee_id}")
        print(f"   Name: {employee.first_name} {employee.last_name}")
        print(f"   Department: {employee.department.name}")
        print(f"   Position: {employee.position}")
        print(f"   Status: {employee.status}")
        print(f"   Email: {employee.email}")
        
        # Test if signal worked
        if final_employees == initial_employees + 1:
            print(f"\n🎉 SUCCESS: Signal is working correctly!")
        else:
            print(f"\n❌ WARNING: Employee count didn't increase as expected")
            
    except Employee.DoesNotExist:
        print(f"\n❌ ERROR: Employee profile was not auto-created")
        print(f"Signal might not be working properly")
    
    # Clean up test user (optional)
    print(f"\n🧹 Cleaning up test user...")
    test_user.delete()
    print(f"✅ Test user deleted")
    
    print(f"\n📋 Test completed!")

if __name__ == "__main__":
    test_employee_auto_creation()
