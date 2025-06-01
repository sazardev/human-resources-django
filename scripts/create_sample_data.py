#!/usr/bin/env python
"""
Script to create initial sample data for the Human Resources system.
Run this script using: python manage.py shell < create_sample_data.py
"""

from django.contrib.auth.models import User
from employees.models import Department, Employee
from django.utils import timezone
from datetime import date

print("Creating sample data for Human Resources system...")

# Create departments
departments_data = [
    {"name": "Information Technology", "description": "Manages company's technology infrastructure and software development"},
    {"name": "Human Resources", "description": "Manages employee relations, hiring, and company policies"},
    {"name": "Finance", "description": "Manages company finances, accounting, and budgeting"},
    {"name": "Marketing", "description": "Manages product marketing, advertising, and customer outreach"},
    {"name": "Sales", "description": "Manages customer relationships and revenue generation"},
]

departments = {}
for dept_data in departments_data:
    dept, created = Department.objects.get_or_create(
        name=dept_data["name"],
        defaults={"description": dept_data["description"]}
    )
    departments[dept_data["name"]] = dept
    if created:
        print(f"Created department: {dept.name}")
    else:
        print(f"Department already exists: {dept.name}")

# Create sample employees
employees_data = [
    {
        "username": "jsmith", "email": "john.smith@company.com", "password": "password123",
        "employee_id": "EMP001", "first_name": "John", "last_name": "Smith",
        "department": "Information Technology", "position": "Senior Software Engineer",
        "hire_date": date(2023, 1, 15), "salary": 95000.00
    },
    {
        "username": "mdavis", "email": "mary.davis@company.com", "password": "password123",
        "employee_id": "EMP002", "first_name": "Mary", "last_name": "Davis",
        "department": "Human Resources", "position": "HR Manager",
        "hire_date": date(2022, 6, 10), "salary": 75000.00
    },
    {
        "username": "bwilson", "email": "bob.wilson@company.com", "password": "password123",
        "employee_id": "EMP003", "first_name": "Bob", "last_name": "Wilson",
        "department": "Finance", "position": "Financial Analyst",
        "hire_date": date(2023, 9, 5), "salary": 68000.00
    },
    {
        "username": "slee", "email": "sarah.lee@company.com", "password": "password123",
        "employee_id": "EMP004", "first_name": "Sarah", "last_name": "Lee",
        "department": "Marketing", "position": "Marketing Specialist",
        "hire_date": date(2024, 2, 20), "salary": 62000.00
    },
    {
        "username": "mgarcia", "email": "miguel.garcia@company.com", "password": "password123",
        "employee_id": "EMP005", "first_name": "Miguel", "last_name": "Garcia",
        "department": "Sales", "position": "Sales Representative",
        "hire_date": date(2024, 11, 1), "salary": 55000.00
    },
]

for emp_data in employees_data:
    # Check if user already exists
    if User.objects.filter(username=emp_data["username"]).exists():
        print(f"User {emp_data['username']} already exists, skipping...")
        continue
    
    # Create user
    user = User.objects.create_user(
        username=emp_data["username"],
        email=emp_data["email"],
        first_name=emp_data["first_name"],
        last_name=emp_data["last_name"],
        password=emp_data["password"]
    )
    
    # Create employee
    employee = Employee.objects.create(
        user=user,
        employee_id=emp_data["employee_id"],
        first_name=emp_data["first_name"],
        last_name=emp_data["last_name"],
        email=emp_data["email"],
        department=departments[emp_data["department"]],
        position=emp_data["position"],
        hire_date=emp_data["hire_date"],
        salary=emp_data["salary"],
        employment_status="active",
        country="Mexico"
    )
    
    print(f"Created employee: {employee.full_name} ({employee.employee_id})")

print(f"\nSample data creation completed!")
print(f"Total departments: {Department.objects.count()}")
print(f"Total employees: {Employee.objects.count()}")
print(f"\nYou can now access the API at: http://127.0.0.1:8000/api/")
print(f"Admin interface at: http://127.0.0.1:8000/admin/")
