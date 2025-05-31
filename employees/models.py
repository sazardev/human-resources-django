from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    """Department model for organizing employees"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    """Employee model for human resources management"""
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Employment Information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    employment_status = models.CharField(
        max_length=20, 
        choices=EMPLOYMENT_STATUS_CHOICES, 
        default='active'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Address Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, default='Mexico')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['employee_id']
