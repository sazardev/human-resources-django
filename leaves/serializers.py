from rest_framework import serializers
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    LeaveType, 
    Holiday, 
    LeaveBalance, 
    LeaveRequest, 
    LeaveRequestComment, 
    TeamSchedule, 
    LeavePolicy
)
from employees.mixins import SelectableFieldsSerializer
from employees.serializers import EmployeeSerializer


class LeaveTypeSerializer(SelectableFieldsSerializer):
    """Serializer for LeaveType model with dynamic field selection"""
    
    class Meta:
        model = LeaveType
        fields = [
            'id', 'name', 'description', 'color_code', 'default_days_per_year',
            'max_days_per_request', 'min_notice_days', 'carry_over_type',
            'max_carry_over_days', 'carry_over_expiry_months', 'requires_approval',
            'requires_documentation', 'is_paid', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class HolidaySerializer(SelectableFieldsSerializer):
    """Serializer for Holiday model with dynamic field selection"""
    departments = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'holiday_type', 'description',
            'is_mandatory', 'affects_leave_calculation', 'departments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeaveBalanceSerializer(SelectableFieldsSerializer):
    """Serializer for LeaveBalance model with dynamic field selection"""
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    leave_type_color = serializers.CharField(source='leave_type.color_code', read_only=True)
    available_days = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    total_allocated = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'leave_type',
            'leave_type_name', 'leave_type_color', 'year', 'allocated_days',
            'used_days', 'pending_days', 'carried_over_days', 'available_days',
            'total_allocated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'available_days', 'total_allocated']


class LeaveRequestCommentSerializer(SelectableFieldsSerializer):
    """Serializer for LeaveRequestComment model with dynamic field selection"""
    commented_by_name = serializers.CharField(source='commented_by.get_full_name', read_only=True)
    
    class Meta:
        model = LeaveRequestComment
        fields = [
            'id', 'leave_request', 'commented_by', 'commented_by_name',
            'comment', 'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeaveRequestSerializer(SelectableFieldsSerializer):
    """Serializer for LeaveRequest model with dynamic field selection"""
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    leave_type_color = serializers.CharField(source='leave_type.color_code', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    is_overlapping_weekend = serializers.BooleanField(read_only=True)
    comments = LeaveRequestCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'request_id', 'employee', 'employee_name', 'employee_id',
            'leave_type', 'leave_type_name', 'leave_type_color', 'start_date',
            'end_date', 'duration_type', 'total_days', 'reason', 'emergency_contact',
            'emergency_phone', 'status', 'submitted_at', 'approved_by',
            'approved_by_name', 'approved_at', 'rejection_reason',
            'supporting_document', 'can_be_cancelled', 'is_overlapping_weekend',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'request_id', 'submitted_at', 'approved_at', 'can_be_cancelled',
            'is_overlapping_weekend', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate leave request data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        leave_type = data.get('leave_type')
        employee = data.get('employee')
        
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("Start date cannot be after end date")
            
            # Check for overlapping requests
            if employee:
                overlapping = LeaveRequest.objects.filter(
                    employee=employee,
                    status__in=['pending', 'approved'],
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )
                
                # Exclude current instance when updating
                if self.instance:
                    overlapping = overlapping.exclude(id=self.instance.id)
                
                if overlapping.exists():
                    raise serializers.ValidationError(
                        "You have overlapping leave requests for these dates"
                    )
            
            # Check minimum notice period
            if leave_type and leave_type.min_notice_days > 0:
                notice_date = timezone.now().date() + timedelta(days=leave_type.min_notice_days)
                if start_date < notice_date:
                    raise serializers.ValidationError(
                        f"Minimum {leave_type.min_notice_days} days notice required"
                    )
        
        return data

    def validate_employee(self, value):
        """Validate employee can request leave"""
        if value and value.employment_status != 'active':
            raise serializers.ValidationError("Only active employees can request leave")
        return value


class LeaveRequestCreateSerializer(LeaveRequestSerializer):
    """Serializer for creating leave requests with additional validations"""
    
    def validate(self, data):
        """Additional validations for leave request creation"""
        data = super().validate(data)
        
        employee = data.get('employee')
        leave_type = data.get('leave_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if employee and leave_type and start_date and end_date:
            # Check leave balance
            current_year = start_date.year
            try:
                balance = LeaveBalance.objects.get(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year
                )
                
                # Calculate requested days (simplified calculation)
                requested_days = (end_date - start_date).days + 1
                
                if requested_days > balance.available_days:
                    raise serializers.ValidationError(
                        f"Insufficient leave balance. Available: {balance.available_days} days, "
                        f"Requested: {requested_days} days"
                    )
            except LeaveBalance.DoesNotExist:
                raise serializers.ValidationError(
                    f"No leave balance found for {leave_type.name} in {current_year}"
                )
        
        return data


class TeamScheduleSerializer(SelectableFieldsSerializer):
    """Serializer for TeamSchedule model with dynamic field selection"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    employees_on_leave = EmployeeSerializer(many=True, read_only=True)
    leave_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = TeamSchedule
        fields = [
            'id', 'department', 'department_name', 'date', 'employees_on_leave',
            'total_employees', 'employees_on_leave_count', 'max_leave_percentage',
            'leave_percentage', 'is_critical', 'created_at', 'updated_at'
        ]
        read_only_fields = ['leave_percentage', 'created_at', 'updated_at']


class LeavePolicySerializer(SelectableFieldsSerializer):
    """Serializer for LeavePolicy model with dynamic field selection"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = LeavePolicy
        fields = [
            'id', 'name', 'description', 'blackout_dates_start',
            'blackout_dates_end', 'department', 'department_name',
            'probation_leave_allowed', 'advance_booking_months',
            'is_active', 'effective_from', 'effective_until',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeaveCalendarSerializer(serializers.Serializer):
    """Serializer for leave calendar data"""
    date = serializers.DateField()
    leave_requests = LeaveRequestSerializer(many=True, read_only=True)
    holidays = HolidaySerializer(many=True, read_only=True)
    is_weekend = serializers.BooleanField(read_only=True)
    employees_on_leave_count = serializers.IntegerField(read_only=True)


class LeaveSummarySerializer(serializers.Serializer):
    """Serializer for leave summary statistics"""
    employee = EmployeeSerializer(read_only=True)
    leave_balances = LeaveBalanceSerializer(many=True, read_only=True)
    pending_requests = LeaveRequestSerializer(many=True, read_only=True)
    recent_requests = LeaveRequestSerializer(many=True, read_only=True)
    total_pending_days = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    total_used_days_this_year = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)


class LeaveApprovalSerializer(serializers.Serializer):
    """Serializer for leave request approval/rejection"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def validate_action(self, value):
        """Validate action is valid"""
        if value not in ['approve', 'reject']:
            raise serializers.ValidationError("Action must be 'approve' or 'reject'")
        return value
