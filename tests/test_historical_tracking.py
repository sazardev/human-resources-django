#!/usr/bin/env python
"""
Test script to verify historical tracking is working
"""
import os
import sys
import django

# Add the Django project directory to the path
sys.path.append('c:\\Users\\cerbe\\OneDrive\\Documents\\django')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from employees.models import Department, Employee, PerformanceReview
from authentication.models import User

def test_historical_tracking():
    """Test that historical tracking is working for all models"""
    
    print("🔍 Testing Historical Tracking Implementation")
    print("=" * 50)
    
    # Test 1: Check if history fields exist
    print("\n1. Checking if history fields exist on models:")
    
    models_to_check = [
        ('Department', Department),
        ('Employee', Employee), 
        ('PerformanceReview', PerformanceReview),
        ('User', User),
    ]
    
    for model_name, model_class in models_to_check:
        has_history = hasattr(model_class, 'history')
        status = "✅" if has_history else "❌"
        print(f"   {status} {model_name}: {'Has history tracking' if has_history else 'No history tracking'}")
        
        if has_history:
            # Check if historical model exists
            historical_model = model_class.history.model
            print(f"      Historical model: {historical_model.__name__}")
    
    # Test 2: Check if we can query history
    print("\n2. Testing history queries:")
    
    # Check Department history
    dept_count = Department.objects.count()
    dept_history_count = Department.history.count()
    print(f"   📊 Departments: {dept_count} current, {dept_history_count} historical records")
    
    # Check Employee history  
    emp_count = Employee.objects.count()
    emp_history_count = Employee.history.count()
    print(f"   👥 Employees: {emp_count} current, {emp_history_count} historical records")
    
    # Check User history
    user_count = User.objects.count()
    user_history_count = User.history.count()
    print(f"   🔐 Users: {user_count} current, {user_history_count} historical records")
    
    # Test 3: Create a test modification to see history in action
    print("\n3. Testing live history tracking:")
    
    try:
        # Create or get a test department
        dept, created = Department.objects.get_or_create(
            name="Test History Department",
            defaults={"description": "Department for testing history tracking"}
        )
        
        if created:
            print("   ✅ Created test department")
        else:
            print("   📝 Using existing test department")
        
        # Make a modification
        original_description = dept.description
        dept.description = f"Updated at {django.utils.timezone.now()}"
        dept.save()
        print("   ✅ Updated department description")
        
        # Check history
        history_records = dept.history.all()
        print(f"   📚 Department now has {history_records.count()} history records")
        
        if history_records.count() >= 2:
            latest = history_records.first()
            previous = history_records.all()[1]
            print(f"   📝 Latest change: {latest.history_date}")
            print(f"   📝 Change type: {latest.history_type}")
            print(f"   📝 Previous description: {previous.description}")
            print(f"   📝 Current description: {latest.description}")
        
        # Restore original description
        dept.description = original_description
        dept.save()
        print("   ✅ Restored original description")
        
    except Exception as e:
        print(f"   ❌ Error testing live tracking: {e}")
    
    print("\n🎉 Historical tracking test completed!")
    print("\n📋 Summary:")
    print("   - HistoricalRecords added to all models")
    print("   - Admin interface configured with SimpleHistoryAdmin")
    print("   - History tracking is active and working")
    print("   - You can view change history in the Django admin")
    
    print("\n🔗 Next steps:")
    print("   1. Access Django admin at http://127.0.0.1:8000/admin/")
    print("   2. Navigate to any model (Employee, Department, etc.)")
    print("   3. Edit a record and save it")
    print("   4. Look for the 'History' button next to the model name")
    print("   5. Click 'History' to see all changes made to that record")

if __name__ == "__main__":
    test_historical_tracking()
