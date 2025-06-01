"""
Django admin configuration for attendance app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    WorkSchedule, TimeEntry, Timesheet,
    AttendanceReport, OvertimeRequest
)


@admin.register(WorkSchedule)
class WorkScheduleAdmin(SimpleHistoryAdmin):
    """Admin interface for WorkSchedule model."""
    
    list_display = [
        'name', 'department_link', 'schedule_type', 'monday_start', 
        'monday_end', 'is_active', 'hours_per_week'
    ]
    list_filter = [
        'is_active', 'department', 'schedule_type', 'created_at'
    ]
    search_fields = [
        'name', 'department__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'schedule_type', 'department', 'is_active')
        }),
        ('Schedule Details', {
            'fields': (
                'monday_start', 'monday_end', 'tuesday_start', 'tuesday_end',
                'wednesday_start', 'wednesday_end', 'thursday_start', 'thursday_end', 
                'friday_start', 'friday_end', 'saturday_start', 'saturday_end',
                'sunday_start', 'sunday_end', 'daily_overtime_threshold'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def department_link(self, obj):
        """Create link to department admin page."""
        if obj.department:
            url = reverse('admin:employees_department_change', args=[obj.department.pk])
            return format_html('<a href="{}">{}</a>', url, obj.department)
        return '-'
    department_link.short_description = 'Department'

    def hours_per_week(self, obj):
        """Calculate total hours per week."""
        # Simplified calculation based on Monday schedule
        if obj.monday_start and obj.monday_end:
            daily_hours = (obj.monday_end.hour - obj.monday_start.hour)
            return daily_hours * 5
        return '-'
    hours_per_week.short_description = 'Weekly Hours'


@admin.register(TimeEntry)
class TimeEntryAdmin(SimpleHistoryAdmin):
    """Admin interface for TimeEntry model."""
    
    list_display = [
        'employee_link', 'clock_in', 'clock_out', 
        'duration', 'entry_type', 'status', 'is_overtime_calc'
    ]
    list_filter = [
        'entry_type', 'status', 'clock_in',
        'employee__department'
    ]
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'employee__employee_id', 'notes'
    ]
    readonly_fields = ['hours_worked', 'created_at', 'updated_at']
    date_hierarchy = 'clock_in'
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'entry_type', 'status')
        }),
        ('Time Information', {
            'fields': (
                'clock_in', 'clock_out', 'hours_worked',
                'break_duration'
            )
        }),
        ('Location & Notes', {
            'fields': (
                'clock_in_location', 'clock_out_location', 'notes'
            ),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_comments'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def employee_link(self, obj):
        """Create link to employee admin page."""
        if obj.employee:
            url = reverse('admin:employees_employee_change', args=[obj.employee.pk])
            return format_html('<a href="{}">{}</a>', url, obj.employee)
        return '-'
    employee_link.short_description = 'Employee'

    def duration(self, obj):
        """Display formatted duration."""
        if obj.clock_in and obj.clock_out:
            duration = obj.clock_out - obj.clock_in
            hours = duration.total_seconds() / 3600
            hours_int = int(hours)
            minutes = int((hours - hours_int) * 60)
            return f"{hours_int}h {minutes}m"
        return '-'
    duration.short_description = 'Duration'

    def is_overtime_calc(self, obj):
        """Calculate if this entry is overtime."""
        if obj.clock_in and obj.clock_out:
            duration = obj.clock_out - obj.clock_in
            hours = duration.total_seconds() / 3600
            return hours > 8  # Simplified overtime calculation
        return False
    is_overtime_calc.short_description = 'Overtime'
    is_overtime_calc.boolean = True

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'employee__user', 'employee__department', 'approved_by'
        )


@admin.register(Timesheet)
class TimesheetAdmin(SimpleHistoryAdmin):
    """Admin interface for Timesheet model."""
    
    list_display = [
        'employee_link', 'week_start', 'total_hours', 'regular_hours',
        'overtime_hours', 'status', 'submitted_at'
    ]
    list_filter = [
        'status', 'week_start', 'employee__department', 'submitted_at'
    ]
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'employee__employee_id'
    ]
    readonly_fields = [
        'total_hours', 'regular_hours', 'overtime_hours',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'week_start'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'week_start', 'status')
        }),
        ('Hours Summary', {
            'fields': ('total_hours', 'regular_hours', 'overtime_hours')
        }),
        ('Approval Workflow', {
            'fields': (
                'submitted_at', 'approved_by', 'approved_at', 'approval_comments'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def employee_link(self, obj):
        """Create link to employee admin page."""
        if obj.employee:
            url = reverse('admin:employees_employee_change', args=[obj.employee.pk])
            return format_html('<a href="{}">{}</a>', url, obj.employee)
        return '-'
    employee_link.short_description = 'Employee'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'employee__user', 'employee__department', 'approved_by'
        )


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(SimpleHistoryAdmin):
    """Admin interface for OvertimeRequest model."""
    
    list_display = [
        'employee_link', 'requested_date', 'estimated_hours', 'status',
        'created_at', 'approved_by'
    ]
    list_filter = [
        'status', 'requested_date', 'employee__department', 'created_at'
    ]
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'employee__employee_id', 'reason'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'requested_date'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('employee', 'requested_date', 'estimated_hours', 'reason', 'status')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at', 'approval_comments'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def employee_link(self, obj):
        """Create link to employee admin page."""
        if obj.employee:
            url = reverse('admin:employees_employee_change', args=[obj.employee.pk])
            return format_html('<a href="{}">{}</a>', url, obj.employee)
        return '-'
    employee_link.short_description = 'Employee'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'employee__user', 'employee__department', 'approved_by'
        )


@admin.register(AttendanceReport)
class AttendanceReportAdmin(SimpleHistoryAdmin):
    """Admin interface for AttendanceReport model."""
    
    list_display = [
        'title', 'employee_link', 'department_link', 'report_type',
        'start_date', 'end_date', 'generated_at'
    ]
    list_filter = [
        'report_type', 'start_date', 'department', 'generated_at'
    ]
    search_fields = [
        'title', 'employee__user__first_name', 'employee__user__last_name',
        'employee__employee_id', 'department__name'
    ]
    readonly_fields = ['generated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Report Configuration', {
            'fields': ('title', 'report_type', 'employee', 'department')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Data & Export', {
            'fields': ('report_data', 'file'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('generated_by', 'generated_at'),
            'classes': ('collapse',)
        })
    )

    def employee_link(self, obj):
        """Create link to employee admin page."""
        if obj.employee:
            url = reverse('admin:employees_employee_change', args=[obj.employee.pk])
            return format_html('<a href="{}">{}</a>', url, obj.employee)
        return '-'
    employee_link.short_description = 'Employee'

    def department_link(self, obj):
        """Create link to department admin page."""
        if obj.department:
            url = reverse('admin:employees_department_change', args=[obj.department.pk])
            return format_html('<a href="{}">{}</a>', url, obj.department)
        return '-'
    department_link.short_description = 'Department'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'employee__user', 'employee__department', 'department'
        )
