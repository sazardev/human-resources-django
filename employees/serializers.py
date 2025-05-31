from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'employee_id', 'first_name', 'last_name', 'email',
            'phone', 'department', 'department_id', 'position', 'hire_date',
            'employment_status', 'salary', 'address', 'city', 'state',
            'postal_code', 'country', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_email(self, value):
        """Validate that email is unique"""
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return value

    def validate_employee_id(self, value):
        """Validate that employee_id is unique"""
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("An employee with this ID already exists.")
        return value


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new employees"""
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'department_id', 'position', 'hire_date', 'employment_status',
            'salary', 'address', 'city', 'state', 'postal_code', 'country',
            'username', 'password'
        ]

    def create(self, validated_data):
        # Extract user data
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        department_id = validated_data.pop('department_id', None)
        
        # Create User
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password
        )
        
        # Get department if provided
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                pass
        
        # Create Employee
        employee = Employee.objects.create(
            user=user,
            department=department,
            **validated_data
        )
        
        return employee
