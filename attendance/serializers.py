from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime, date, timedelta
from decimal import Decimal
from .models import (
    WorkSchedule, TimeEntry, Timesheet, AttendanceReport, OvertimeRequest
)
from employees.models import Employee, Department
from employees.mixins import SelectableFieldsSerializer

User = get_user_model()


class WorkScheduleSerializer(SelectableFieldsSerializer):
    """Serializer for WorkSchedule model with dynamic field selection"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    standard_daily_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'name', 'schedule_type', 'department', 'department_name',
            'monday_start', 'monday_end', 'tuesday_start', 'tuesday_end',
            'wednesday_start', 'wednesday_end', 'thursday_start', 'thursday_end',
            'friday_start', 'friday_end', 'saturday_start', 'saturday_end',
            'sunday_start', 'sunday_end', 'lunch_break_duration', 'break_duration',
            'daily_overtime_threshold', 'weekly_overtime_threshold',
            'standard_daily_hours', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate work schedule data"""
        # Check that start times are before end times
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            start_field = f'{day}_start'
            end_field = f'{day}_end'
            
            start_time = data.get(start_field)
            end_time = data.get(end_field)
            
            if start_time and end_time and start_time >= end_time:
                raise serializers.ValidationError(
                    f"{day.capitalize()} start time must be before end time"
                )
        
        # Validate overtime thresholds
        daily_threshold = data.get('daily_overtime_threshold')
        if daily_threshold and daily_threshold <= 0:
            raise serializers.ValidationError("Daily overtime threshold must be greater than 0")
        
        weekly_threshold = data.get('weekly_overtime_threshold')
        if weekly_threshold and weekly_threshold <= 0:
            raise serializers.ValidationError("Weekly overtime threshold must be greater than 0")
        
        return data


class TimeEntrySerializer(SelectableFieldsSerializer):
    """Serializer for TimeEntry model with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    adjusted_by_name = serializers.CharField(source='adjusted_by.get_full_name', read_only=True)
    
    # Computed fields
    hours_worked = serializers.ReadOnlyField()
    regular_hours = serializers.ReadOnlyField()
    overtime_hours = serializers.ReadOnlyField()
    is_overtime = serializers.ReadOnlyField()
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'entry_type', 'entry_type_display',
            'clock_in', 'clock_out', 'break_duration', 'clock_in_location', 'clock_out_location',
            'ip_address', 'status', 'status_display', 'approved_by', 'approved_by_name',
            'approved_at', 'original_hours', 'adjusted_hours', 'adjustment_reason',
            'adjusted_by', 'adjusted_by_name', 'notes', 'is_remote_work', 'project_code',
            'hours_worked', 'regular_hours', 'overtime_hours', 'is_overtime',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_at']
    
    def validate(self, data):
        """Validate time entry data"""
        clock_in = data.get('clock_in')
        clock_out = data.get('clock_out')
        
        if clock_out and clock_in and clock_out <= clock_in:
            raise serializers.ValidationError("Clock out time must be after clock in time")
        
        # Don't allow future clock-in times
        if clock_in and clock_in > datetime.now(clock_in.tzinfo):
            raise serializers.ValidationError("Clock in time cannot be in the future")
        
        # Validate adjusted hours
        adjusted_hours = data.get('adjusted_hours')
        if adjusted_hours and adjusted_hours < 0:
            raise serializers.ValidationError("Adjusted hours cannot be negative")
        
        if adjusted_hours and adjusted_hours > 24:
            raise serializers.ValidationError("Adjusted hours cannot exceed 24 hours per day")
        
        return data


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating time entries (clock in)"""
    
    class Meta:
        model = TimeEntry
        fields = [
            'employee', 'entry_type', 'clock_in_location', 'is_remote_work',
            'project_code', 'notes'
        ]
    
    def create(self, validated_data):
        """Create time entry with automatic clock_in timestamp"""
        validated_data['clock_in'] = datetime.now()
        if 'request' in self.context:
            request = self.context['request']
            validated_data['ip_address'] = self.get_client_ip(request)
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TimesheetSerializer(SelectableFieldsSerializer):
    """Serializer for Timesheet model with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    # Computed fields
    time_entries = TimeEntrySerializer(many=True, read_only=True)
    missing_days = serializers.ReadOnlyField()
    is_editable = serializers.ReadOnlyField()
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Timesheet
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'week_start', 'week_end',
            'total_hours', 'regular_hours', 'overtime_hours', 'break_hours',
            'status', 'status_display', 'submitted_at', 'approved_by', 'approved_by_name',
            'approved_at', 'rejection_reason', 'employee_notes', 'manager_notes',
            'time_entries', 'missing_days', 'is_editable', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'submitted_at', 'approved_at', 'week_end']
    
    def validate(self, data):
        """Validate timesheet data"""
        week_start = data.get('week_start')
        
        # Ensure week_start is a Monday
        if week_start and week_start.weekday() != 0:
            raise serializers.ValidationError("Week start must be a Monday")
        
        # Don't allow future weeks
        if week_start and week_start > date.today():
            raise serializers.ValidationError("Cannot create timesheet for future weeks")
        
        return data


class TimesheetSummarySerializer(SelectableFieldsSerializer):
    """Lightweight serializer for timesheet summaries"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Timesheet
        fields = [
            'id', 'employee_name', 'employee_id', 'week_start', 'week_end',
            'total_hours', 'regular_hours', 'overtime_hours', 'status', 'status_display',
            'submitted_at', 'approved_at'
        ]


class AttendanceReportSerializer(SelectableFieldsSerializer):
    """Serializer for AttendanceReport model with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = AttendanceReport
        fields = [
            'id', 'report_type', 'report_type_display', 'title', 'start_date', 'end_date',
            'employee', 'employee_name', 'department', 'department_name',
            'report_data', 'file', 'generated_by', 'generated_by_name', 'generated_at'
        ]
        read_only_fields = ['generated_at']
    
    def validate(self, data):
        """Validate report data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date must be before or equal to end date")
        
        # Don't allow reports too far in the future
        if end_date and end_date > date.today() + timedelta(days=7):
            raise serializers.ValidationError("End date cannot be more than a week in the future")
        
        return data


class OvertimeRequestSerializer(SelectableFieldsSerializer):
    """Serializer for OvertimeRequest model with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    variance_hours = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OvertimeRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'requested_date',
            'estimated_hours', 'reason', 'status', 'status_display', 'approved_by',
            'approved_by_name', 'approved_at', 'rejection_reason', 'actual_hours',
            'time_entry', 'variance_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_at']
    
    def validate(self, data):
        """Validate overtime request data"""
        requested_date = data.get('requested_date')
        estimated_hours = data.get('estimated_hours')
        
        # Don't allow requests for past dates (unless today)
        if requested_date and requested_date < date.today():
            raise serializers.ValidationError("Cannot request overtime for past dates")
        
        # Validate estimated hours
        if estimated_hours and (estimated_hours <= 0 or estimated_hours > 12):
            raise serializers.ValidationError("Estimated hours must be between 0 and 12")
        
        return data


class EmployeeAttendanceSummarySerializer(SelectableFieldsSerializer):
    """Serializer for employee attendance summary with dynamic field selection"""
    
    employee_name = serializers.CharField(source='full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    # Computed attendance fields
    total_hours_this_week = serializers.SerializerMethodField()
    total_hours_this_month = serializers.SerializerMethodField()
    overtime_hours_this_week = serializers.SerializerMethodField()
    overtime_hours_this_month = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    last_clock_in = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'employee_name', 'department_name', 'position',
            'total_hours_this_week', 'total_hours_this_month', 'overtime_hours_this_week',
            'overtime_hours_this_month', 'current_status', 'last_clock_in'
        ]
    
    def get_total_hours_this_week(self, obj):
        """Get total hours worked this week"""
        from django.utils import timezone
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        timesheet = obj.timesheets.filter(week_start=week_start).first()
        return float(timesheet.total_hours) if timesheet else 0.0
    
    def get_total_hours_this_month(self, obj):
        """Get total hours worked this month"""
        from django.utils import timezone
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        timesheets = obj.timesheets.filter(week_start__gte=month_start)
        total = sum(ts.total_hours for ts in timesheets)
        return float(total)
    
    def get_overtime_hours_this_week(self, obj):
        """Get overtime hours this week"""
        from django.utils import timezone
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        timesheet = obj.timesheets.filter(week_start=week_start).first()
        return float(timesheet.overtime_hours) if timesheet else 0.0
    
    def get_overtime_hours_this_month(self, obj):
        """Get overtime hours this month"""
        from django.utils import timezone
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        timesheets = obj.timesheets.filter(week_start__gte=month_start)
        total = sum(ts.overtime_hours for ts in timesheets)
        return float(total)
    
    def get_current_status(self, obj):
        """Get current clock in/out status"""
        active_entry = obj.time_entries.filter(
            status='active',
            clock_out__isnull=True
        ).first()
        
        if active_entry:
            return f"Clocked in since {active_entry.clock_in.strftime('%H:%M')}"
        return "Clocked out"
    
    def get_last_clock_in(self, obj):
        """Get last clock in time"""
        last_entry = obj.time_entries.filter(clock_out__isnull=False).first()
        if last_entry:
            return last_entry.clock_in
        return None


# Bulk operations serializers
class BulkTimesheetApprovalSerializer(serializers.Serializer):
    """Serializer for bulk timesheet approval"""
    
    timesheet_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_timesheet_ids(self, value):
        """Validate that all timesheet IDs exist and are approvable"""
        timesheets = Timesheet.objects.filter(id__in=value)
        
        if len(timesheets) != len(value):
            raise serializers.ValidationError("Some timesheet IDs are invalid")
        
        for timesheet in timesheets:
            if timesheet.status not in ['submitted']:
                raise serializers.ValidationError(
                    f"Timesheet {timesheet.id} is not in a state that can be approved/rejected"
                )
        
        return value


class AttendanceDashboardSerializer(serializers.Serializer):
    """Serializer for attendance dashboard data"""
    
    total_employees = serializers.IntegerField()
    currently_clocked_in = serializers.IntegerField()
    pending_timesheets = serializers.IntegerField()
    overtime_requests_pending = serializers.IntegerField()
    
    # Daily stats
    total_hours_today = serializers.DecimalField(max_digits=8, decimal_places=2)
    overtime_hours_today = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    # Weekly stats
    total_hours_this_week = serializers.DecimalField(max_digits=8, decimal_places=2)
    overtime_hours_this_week = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    # Department breakdown
    department_breakdown = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    
    # Recent activity
    recent_clock_ins = TimeEntrySerializer(many=True, read_only=True)
    recent_clock_outs = TimeEntrySerializer(many=True, read_only=True)
