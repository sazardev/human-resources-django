from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Department, Employee


class DepartmentModelTest(TestCase):
    """Test cases for Department model"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="IT Department",
            description="Information Technology Department"
        )
    
    def test_department_creation(self):
        """Test department creation"""
        self.assertEqual(self.department.name, "IT Department")
        self.assertEqual(str(self.department), "IT Department")
    
    def test_department_ordering(self):
        """Test department ordering"""
        dept2 = Department.objects.create(name="HR Department")
        departments = Department.objects.all()
        self.assertEqual(departments[0].name, "HR Department")  # Alphabetical order


class EmployeeModelTest(TestCase):
    """Test cases for Employee model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@company.com",
            first_name="John",
            last_name="Doe"
        )
        self.department = Department.objects.create(name="IT Department")
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john.doe@company.com",
            department=self.department,
            position="Software Developer",
            hire_date="2025-01-01",
            employment_status="active"
        )
    
    def test_employee_creation(self):
        """Test employee creation"""
        self.assertEqual(self.employee.employee_id, "EMP001")
        self.assertEqual(self.employee.full_name, "John Doe")
        self.assertEqual(str(self.employee), "John Doe (EMP001)")
    
    def test_employee_department_relationship(self):
        """Test employee-department relationship"""
        self.assertEqual(self.employee.department, self.department)


class EmployeeAPITest(APITestCase):
    """Test cases for Employee API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@company.com"
        )
        self.department = Department.objects.create(name="IT Department")
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john.doe@company.com",
            department=self.department,
            position="Software Developer",
            hire_date="2025-01-01",
            employment_status="active"
        )
        # Authenticate the test client
        self.client.force_authenticate(user=self.user)
    
    def test_get_employees_list(self):
        """Test GET /api/employees/"""
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_employee_detail(self):
        """Test GET /api/employees/{id}/"""
        url = reverse('employee-detail', kwargs={'pk': self.employee.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], "EMP001")
    
    def test_employee_statistics(self):
        """Test GET /api/employees/statistics/"""
        url = reverse('employee-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_employees', response.data)
        self.assertEqual(response.data['total_employees'], 1)


class DepartmentAPITest(APITestCase):
    """Test cases for Department API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.department = Department.objects.create(
            name="IT Department",
            description="Information Technology Department"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_departments_list(self):
        """Test GET /api/departments/"""
        url = reverse('department-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_department(self):
        """Test POST /api/departments/"""
        url = reverse('department-list')
        data = {
            'name': 'HR Department',
            'description': 'Human Resources Department'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)
