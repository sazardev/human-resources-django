from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Count
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    LeaveType, 
    Holiday, 
    LeaveBalance, 
    LeaveRequest, 
    LeaveRequestComment, 
    TeamSchedule, 
    LeavePolicy
)


@admin.register(LeaveType)
class LeaveTypeAdmin(SimpleHistoryAdmin):
    """Admin interface for Leave Types"""
    list_display = [
        'name', 'default_days_per_year', 'max_days_per_request', 
        'min_notice_days', 'requires_approval', 'is_paid', 'is_active'
    ]
    list_filter = ['requires_approval', 'requires_documentation', 'is_paid', 'is_active', 'carry_over_type']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'color_code', 'is_active')
        }),
        ('Leave Allocation', {
            'fields': ('default_days_per_year', 'max_days_per_request', 'min_notice_days')
        }),
        ('Carry Over Rules', {
            'fields': ('carry_over_type', 'max_carry_over_days', 'carry_over_expiry_months'),
            'classes': ('collapse',)
        }),
        ('Business Rules', {
            'fields': ('requires_approval', 'requires_documentation', 'is_paid')
        }),
    )


@admin.register(Holiday)
class HolidayAdmin(SimpleHistoryAdmin):
    """Admin interface for Holidays"""
    list_display = [
        'name', 'date', 'holiday_type', 'is_mandatory', 
        'affects_leave_calculation', 'get_departments'
    ]
    list_filter = ['holiday_type', 'is_mandatory', 'affects_leave_calculation', 'date']
    search_fields = ['name', 'description']
    date_hierarchy = 'date'
    ordering = ['date']
    filter_horizontal = ['departments']
    
    def get_departments(self, obj):
        """Display associated departments"""
        deps = obj.departments.all()
        if deps:
            return ', '.join([dep.name for dep in deps])
        return 'All Departments'
    get_departments.short_description = 'Departments'


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(SimpleHistoryAdmin):
    """Admin interface for Leave Balances"""
    list_display = [
        'employee', 'leave_type', 'year', 'allocated_days', 
        'used_days', 'pending_days', 'available_days', 'carried_over_days'
    ]
    list_filter = ['year', 'leave_type', 'employee__department']
    search_fields = [
        'employee__first_name', 'employee__last_name', 
        'employee__employee_id', 'leave_type__name'
    ]
    ordering = ['-year', 'employee', 'leave_type']
    
    readonly_fields = ['available_days', 'total_allocated']
    
    fieldsets = (
        ('Employee & Leave Type', {
            'fields': ('employee', 'leave_type', 'year')
        }),
        ('Balance Details', {
            'fields': ('allocated_days', 'used_days', 'pending_days', 'carried_over_days')
        }),
        ('Calculated Fields', {
            'fields': ('available_days', 'total_allocated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveRequest)
class LeaveRequestAdmin(SimpleHistoryAdmin):
    """Admin interface for Leave Requests"""
    list_display = [
        'request_id', 'employee', 'leave_type', 'start_date', 
        'end_date', 'total_days', 'status', 'submitted_at'
    ]
    list_filter = [
        'status', 'leave_type', 'duration_type', 
        'employee__department', 'start_date', 'submitted_at'
    ]
    search_fields = [
        'request_id', 'employee__first_name', 'employee__last_name',
        'employee__employee_id', 'reason'
    ]
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    
    readonly_fields = ['request_id', 'submitted_at', 'approved_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'employee', 'leave_type', 'status')
        }),
        ('Leave Details', {
            'fields': ('start_date', 'end_date', 'duration_type', 'total_days', 'reason')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('Approval Information', {
            'fields': ('submitted_at', 'approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': ('supporting_document',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Bulk approve leave requests"""
        updated = 0
        for leave_request in queryset.filter(status='pending'):
            leave_request.status = 'approved'
            leave_request.approved_by = request.user.employee_profile
            leave_request.approved_at = timezone.now()
            leave_request.save()
            updated += 1
        
        self.message_user(request, f'{updated} leave requests approved.')
    approve_requests.short_description = "Approve selected leave requests"
    
    def reject_requests(self, request, queryset):
        """Bulk reject leave requests"""
        updated = 0
        for leave_request in queryset.filter(status='pending'):
            leave_request.status = 'rejected'
            leave_request.rejection_reason = 'Bulk rejection from admin'
            leave_request.save()
            updated += 1
        
        self.message_user(request, f'{updated} leave requests rejected.')
    reject_requests.short_description = "Reject selected leave requests"


class LeaveRequestCommentInline(admin.TabularInline):
    """Inline for leave request comments"""
    model = LeaveRequestComment
    extra = 1
    fields = ['commented_by', 'comment', 'is_internal']
    readonly_fields = ['created_at']


# Add the inline to LeaveRequestAdmin
LeaveRequestAdmin.inlines = [LeaveRequestCommentInline]


@admin.register(LeaveRequestComment)
class LeaveRequestCommentAdmin(SimpleHistoryAdmin):
    """Admin interface for Leave Request Comments"""
    list_display = [
        'leave_request', 'commented_by', 'comment_preview', 
        'is_internal', 'created_at'
    ]
    list_filter = ['is_internal', 'created_at']
    search_fields = [
        'leave_request__request_id', 'commented_by__first_name', 
        'commented_by__last_name', 'comment'
    ]
    ordering = ['-created_at']
    
    def comment_preview(self, obj):
        """Show preview of comment"""
        return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
    comment_preview.short_description = 'Comment Preview'


@admin.register(TeamSchedule)
class TeamScheduleAdmin(SimpleHistoryAdmin):
    """Admin interface for Team Schedules"""
    list_display = [
        'department', 'date', 'employees_on_leave_count', 
        'total_employees', 'leave_percentage_display', 'is_critical'
    ]
    list_filter = ['is_critical', 'department', 'date']
    search_fields = ['department__name']
    date_hierarchy = 'date'
    ordering = ['date', 'department']
    filter_horizontal = ['employees_on_leave']
    
    def leave_percentage_display(self, obj):
        """Display leave percentage with color coding"""
        percentage = obj.leave_percentage
        color = 'red' if obj.is_critical else 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            percentage
        )
    leave_percentage_display.short_description = 'Leave %'


@admin.register(LeavePolicy)
class LeavePolicyAdmin(SimpleHistoryAdmin):
    """Admin interface for Leave Policies"""
    list_display = [
        'name', 'department', 'is_active', 'effective_from', 
        'effective_until', 'probation_leave_allowed'
    ]
    list_filter = ['is_active', 'probation_leave_allowed', 'department']
    search_fields = ['name', 'description']
    ordering = ['-effective_from']
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('name', 'description', 'department')
        }),
        ('Blackout Periods', {
            'fields': ('blackout_dates_start', 'blackout_dates_end'),
            'classes': ('collapse',)
        }),
        ('General Settings', {
            'fields': ('probation_leave_allowed', 'advance_booking_months')
        }),
        ('Effective Period', {
            'fields': ('is_active', 'effective_from', 'effective_until')
        }),
    )


# Custom admin site configuration
admin.site.site_header = "Human Resources - Leave Management"
admin.site.site_title = "HR Leave Admin"
admin.site.index_title = "Leave Management Dashboard"
