from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Employee, Department, PerformanceReview, PerformanceGoal, PerformanceNote
from .mixins import SelectableFieldsSerializer

User = get_user_model()


class DepartmentSerializer(SelectableFieldsSerializer):
    """Serializer for Department model with dynamic field selection"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(SelectableFieldsSerializer):
    """Serializer for User model with dynamic field selection"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class EmployeeSerializer(SelectableFieldsSerializer):
    """Serializer for Employee model with dynamic field selection"""
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


class EmployeeCreateSerializer(SelectableFieldsSerializer):
    """Serializer for creating new employees with dynamic field selection"""
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


class PerformanceReviewSerializer(SelectableFieldsSerializer):
    """Serializer for PerformanceReview model with dynamic field selection"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    reviewer = UserSerializer(read_only=True)
    reviewer_id = serializers.IntegerField(write_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'employee', 'employee_id', 'reviewer', 'reviewer_id',
            'review_type', 'review_type_display', 'review_period_start', 'review_period_end',
            'review_date', 'status', 'status_display', 'overall_rating',
            'technical_skills', 'communication', 'teamwork', 'leadership',
            'problem_solving', 'adaptability', 'average_rating',
            'strengths', 'areas_for_improvement', 'goals_for_next_period',
            'reviewer_comments', 'employee_comments', 'promotion_recommendation',
            'salary_increase_recommendation', 'training_recommendations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Validate review data"""
        if data['review_period_start'] >= data['review_period_end']:
            raise serializers.ValidationError(
                "Review period start date must be before end date."
            )
        return data


class PerformanceGoalSerializer(SelectableFieldsSerializer):
    """Serializer for PerformanceGoal model with dynamic field selection"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True)
    review = PerformanceReviewSerializer(read_only=True)
    review_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Display fields
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    # Computed fields
    is_overdue = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PerformanceGoal
        fields = [
            'id', 'employee', 'employee_id', 'title', 'description',
            'category', 'category_display', 'priority', 'priority_display',
            'start_date', 'target_date', 'completed_date', 'status', 'status_display',
            'progress_percentage', 'success_criteria', 'measurable_outcomes',
            'progress_notes', 'completion_notes', 'created_by', 'created_by_id',
            'review', 'review_id', 'is_overdue', 'days_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_date']

    def validate(self, data):
        """Validate goal data"""
        if data['start_date'] > data['target_date']:
            raise serializers.ValidationError(
                "Start date must be before or equal to target date."
            )
        return data


class PerformanceNoteSerializer(SelectableFieldsSerializer):
    """Serializer for PerformanceNote model with dynamic field selection"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)
    goal = PerformanceGoalSerializer(read_only=True)
    goal_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    review = PerformanceReviewSerializer(read_only=True)
    review_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)
    
    class Meta:
        model = PerformanceNote
        fields = [
            'id', 'employee', 'employee_id', 'author', 'author_id',
            'note_type', 'note_type_display', 'title', 'content',
            'date_observed', 'is_private', 'goal', 'goal_id',
            'review', 'review_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmployeePerformanceSerializer(SelectableFieldsSerializer):
    """Comprehensive serializer for employee performance overview with dynamic field selection"""
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    latest_performance_review = PerformanceReviewSerializer(read_only=True)
    average_performance_rating = serializers.FloatField(read_only=True)
    active_goals = PerformanceGoalSerializer(many=True, read_only=True)
    recent_notes = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'employee_id', 'full_name', 'email',
            'department', 'position', 'hire_date', 'employment_status',
            'latest_performance_review', 'average_performance_rating',
            'active_goals', 'recent_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_recent_notes(self, obj):
        """Get recent performance notes (last 10)"""
        recent_notes = obj.performance_notes.order_by('-date_observed')[:10]
        return PerformanceNoteSerializer(recent_notes, many=True).data
