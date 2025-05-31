from django.core.management.base import BaseCommand
from authentication.models import User
from employees.models import Employee


class Command(BaseCommand):
    help = 'Test the auto-creation signal for Employee profiles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 TESTING AUTO-CREATION SIGNAL'))
        self.stdout.write('=' * 40)
        
        # Count existing users and employees
        initial_users = User.objects.count()
        initial_employees = Employee.objects.count()
        
        self.stdout.write(f'📊 Initial counts:')
        self.stdout.write(f'   Users: {initial_users}')
        self.stdout.write(f'   Employees: {initial_employees}')
        
        # Create a test user
        self.stdout.write(f'\n👤 Creating test user...')
        test_user = User.objects.create_user(
            username='testsignal456',
            email='testsignal456@example.com',
            first_name='Signal',
            last_name='Test',
            password='testpass123'
        )
        
        self.stdout.write(f'✅ User created: {test_user.username}')
        
        # Check if Employee was auto-created
        final_users = User.objects.count()
        final_employees = Employee.objects.count()
        
        self.stdout.write(f'\n📊 Final counts:')
        self.stdout.write(f'   Users: {final_users} (+{final_users - initial_users})')
        self.stdout.write(f'   Employees: {final_employees} (+{final_employees - initial_employees})')
        
        # Try to get the Employee profile
        try:
            employee = Employee.objects.get(user=test_user)
            self.stdout.write(f'\n✅ Employee profile auto-created!')
            self.stdout.write(f'   Employee ID: {employee.employee_id}')
            self.stdout.write(f'   Name: {employee.first_name} {employee.last_name}')
            self.stdout.write(f'   Department: {employee.department.name}')
            self.stdout.write(f'   Position: {employee.position}')
            self.stdout.write(f'   Status: {employee.status}')
            self.stdout.write(f'   Email: {employee.email}')
            
            # Test if signal worked
            if final_employees == initial_employees + 1:
                self.stdout.write(self.style.SUCCESS('\n🎉 SUCCESS: Signal is working correctly!'))
            else:
                self.stdout.write(self.style.WARNING('\n❌ WARNING: Employee count didn\'t increase as expected'))
                
        except Employee.DoesNotExist:
            self.stdout.write(self.style.ERROR('\n❌ ERROR: Employee profile was not auto-created'))
            self.stdout.write('Signal might not be working properly')
        
        # Clean up test user
        self.stdout.write(f'\n🧹 Cleaning up test user...')
        test_user.delete()
        self.stdout.write(f'✅ Test user deleted')
        
        self.stdout.write(self.style.SUCCESS('\n📋 Test completed!'))
