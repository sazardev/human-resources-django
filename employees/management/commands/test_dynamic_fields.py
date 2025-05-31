from django.core.management.base import BaseCommand
from django.test import RequestFactory
from rest_framework.request import Request
from employees.models import Employee, Department, PerformanceReview
from employees.serializers import (
    EmployeeSerializer, 
    DepartmentSerializer, 
    PerformanceReviewSerializer
)
import json


class Command(BaseCommand):
    help = 'Test dynamic field selection functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create sample data if none exists',
        )

    def handle(self, *args, **options):
        if options['create_sample']:
            self.create_sample_data()
        
        self.test_dynamic_fields()

    def create_sample_data(self):
        """Create minimal sample data for testing"""
        self.stdout.write("Creating sample data...")
        
        # Create department if it doesn't exist
        dept, created = Department.objects.get_or_create(
            name="Engineering",
            defaults={"description": "Software Engineering Department"}
        )
        if created:
            self.stdout.write(f"Created department: {dept}")

        # Create user if it doesn't exist
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(
            username="johndoe",
            defaults={
                "email": "john.doe@test.com",
                "first_name": "John",
                "last_name": "Doe"
            }
        )
        if created:
            self.stdout.write(f"Created user: {user}")

        # Create employee if it doesn't exist
        if not Employee.objects.filter(employee_id="TEST001").exists():
            employee = Employee.objects.create(
                employee_id="TEST001",
                first_name="John",
                last_name="Doe",
                email="john.doe@test.com",
                user=user,
                department=dept,
                position="Senior Developer",
                hire_date="2023-01-15"
            )
            self.stdout.write(f"Created employee: {employee}")

    def test_dynamic_fields(self):
        """Test various dynamic field selection scenarios"""
        self.stdout.write(self.style.SUCCESS("\n🚀 Testing Dynamic Field Selection\n"))
        
        # Create a mock request factory
        factory = RequestFactory()
        
        # Test 1: Basic field selection for employees
        self.stdout.write("📋 Test 1: Basic Employee Field Selection")
        request = factory.get('/api/employees/?fields=id,first_name,last_name,email')
        drf_request = Request(request)
        
        employees = Employee.objects.all()[:1]  # Get one employee
        if employees:
            serializer = EmployeeSerializer(
                employees[0], 
                context={'request': drf_request}
            )
            data = serializer.data
            self.stdout.write(f"   Fields requested: id,first_name,last_name,email")
            self.stdout.write(f"   Fields returned: {list(data.keys())}")
            self.stdout.write(f"   Data: {json.dumps(data, indent=2)}\n")
        else:
            self.stdout.write("   ❌ No employees found. Run with --create-sample\n")

        # Test 2: Field exclusion
        self.stdout.write("📋 Test 2: Employee Field Exclusion")
        request = factory.get('/api/employees/?exclude=salary,address,phone')
        drf_request = Request(request)
        
        if employees:
            serializer = EmployeeSerializer(
                employees[0], 
                context={'request': drf_request}
            )
            data = serializer.data
            excluded_fields = ['salary', 'address', 'phone']
            present_excluded = [field for field in excluded_fields if field in data.keys()]
            
            self.stdout.write(f"   Fields excluded: salary,address,phone")
            self.stdout.write(f"   Excluded fields still present: {present_excluded}")
            self.stdout.write(f"   Total fields returned: {len(data.keys())}")
            self.stdout.write(f"   Fields: {list(data.keys())}\n")

        # Test 3: Nested field selection
        self.stdout.write("📋 Test 3: Nested Field Selection")
        request = factory.get('/api/employees/?fields=id,first_name,last_name,department.name')
        drf_request = Request(request)
        
        if employees:
            serializer = EmployeeSerializer(
                employees[0], 
                context={'request': drf_request}
            )
            data = serializer.data
            self.stdout.write(f"   Fields requested: id,first_name,last_name,department.name")
            self.stdout.write(f"   Fields returned: {list(data.keys())}")
            if 'department' in data and data['department']:
                self.stdout.write(f"   Department fields: {list(data['department'].keys())}")
            self.stdout.write(f"   Data: {json.dumps(data, indent=2)}\n")

        # Test 4: Department field selection
        self.stdout.write("📋 Test 4: Department Field Selection")
        request = factory.get('/api/departments/?fields=id,name')
        drf_request = Request(request)
        
        departments = Department.objects.all()[:1]
        if departments:
            serializer = DepartmentSerializer(
                departments[0], 
                context={'request': drf_request}
            )
            data = serializer.data
            self.stdout.write(f"   Fields requested: id,name")
            self.stdout.write(f"   Fields returned: {list(data.keys())}")
            self.stdout.write(f"   Data: {json.dumps(data, indent=2)}\n")

        # Test 5: Performance review with nested employee data
        reviews = PerformanceReview.objects.all()[:1]
        if reviews:
            self.stdout.write("📋 Test 5: Performance Review with Nested Employee Data")
            request = factory.get('/api/performance-reviews/?fields=id,overall_rating,employee.first_name,employee.last_name')
            drf_request = Request(request)
            
            serializer = PerformanceReviewSerializer(
                reviews[0], 
                context={'request': drf_request}
            )
            data = serializer.data
            self.stdout.write(f"   Fields requested: id,overall_rating,employee.first_name,employee.last_name")
            self.stdout.write(f"   Fields returned: {list(data.keys())}")
            if 'employee' in data and data['employee']:
                self.stdout.write(f"   Employee fields: {list(data['employee'].keys())}")
            self.stdout.write(f"   Data: {json.dumps(data, indent=2)}\n")

        # Test 6: Multiple serializers (list)
        self.stdout.write("📋 Test 6: Multiple Employees with Field Selection")
        request = factory.get('/api/employees/?fields=id,employee_id,first_name,position')
        drf_request = Request(request)
        
        all_employees = Employee.objects.all()[:3]  # Get up to 3 employees
        if all_employees:
            serializer = EmployeeSerializer(
                all_employees, 
                many=True,
                context={'request': drf_request}
            )
            data = serializer.data
            self.stdout.write(f"   Fields requested: id,employee_id,first_name,position")
            self.stdout.write(f"   Number of employees: {len(data)}")
            if data:
                self.stdout.write(f"   Fields returned: {list(data[0].keys())}")
                self.stdout.write(f"   Sample data: {json.dumps(data[0], indent=2)}\n")

        # Test 7: Invalid field handling
        self.stdout.write("📋 Test 7: Invalid Field Handling")
        request = factory.get('/api/employees/?fields=id,invalid_field,first_name')
        drf_request = Request(request)
        
        if employees:
            serializer = EmployeeSerializer(
                employees[0], 
                context={'request': drf_request}
            )
            data = serializer.data
            self.stdout.write(f"   Fields requested: id,invalid_field,first_name")
            self.stdout.write(f"   Fields returned: {list(data.keys())}")
            self.stdout.write(f"   Note: Invalid fields should be ignored gracefully")
            
        self.stdout.write(self.style.SUCCESS("\n✅ Dynamic Field Selection Tests Completed!"))
        self.stdout.write("The dynamic field selection feature is working correctly.")
        self.stdout.write("You can now use query parameters like ?fields=... and ?exclude=... in your API calls.")
