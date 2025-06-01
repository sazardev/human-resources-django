from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date, timedelta
from employees.models import Employee, Department
from simple_history.models import HistoricalRecords

User = get_user_model()


class WorkSchedule(models.Model):
    """Define work schedules for employees or departments"""
    
    SCHEDULE_TYPE_CHOICES = [
        ('standard', 'Standard (Mon-Fri)'),
        ('shift', 'Shift Work'),
        ('flexible', 'Flexible Hours'),
        ('custom', 'Custom Schedule'),
    ]
    
    name = models.CharField(max_length=100)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES, default='standard')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    
    # Standard schedule settings
    monday_start = models.TimeField(default='09:00')
    monday_end = models.TimeField(default='17:00')
    tuesday_start = models.TimeField(default='09:00')
    tuesday_end = models.TimeField(default='17:00')
    wednesday_start = models.TimeField(default='09:00')
    wednesday_end = models.TimeField(default='17:00')
    thursday_start = models.TimeField(default='09:00')
    thursday_end = models.TimeField(default='17:00')
    friday_start = models.TimeField(default='09:00')
    friday_end = models.TimeField(default='17:00')
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    sunday_start = models.TimeField(null=True, blank=True)
    sunday_end = models.TimeField(null=True, blank=True)
    
    # Break settings
    lunch_break_duration = models.DurationField(default=timedelta(hours=1))
    break_duration = models.DurationField(default=timedelta(minutes=15))
    
    # Overtime settings
    daily_overtime_threshold = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('8.00'),
        help_text="Hours per day before overtime applies"
    )
    weekly_overtime_threshold = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('40.00'),
        help_text="Hours per week before overtime applies"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_schedule_type_display()})"
    
    @property
    def standard_daily_hours(self):
        """Calculate standard daily hours for Monday-Friday"""
        if self.schedule_type == 'standard':
            monday_hours = self._calculate_daily_hours(self.monday_start, self.monday_end)
            return monday_hours
        return Decimal('8.00')
    
    def _calculate_daily_hours(self, start_time, end_time):
        """Calculate hours between start and end time"""
        if not start_time or not end_time:
            return Decimal('0.00')
        
        start_datetime = datetime.combine(date.today(), start_time)
        end_datetime = datetime.combine(date.today(), end_time)
        
        # Handle overnight shifts
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        hours = duration.total_seconds() / 3600
        return Decimal(str(round(hours, 2)))


class TimeEntry(models.Model):
    """Individual time entry records (clock in/out)"""
    
    ENTRY_TYPE_CHOICES = [
        ('regular', 'Regular Time'),
        ('overtime', 'Overtime'),
        ('break', 'Break'),
        ('lunch', 'Lunch Break'),
        ('personal', 'Personal Time'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active (Clocked In)'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('edited', 'Manually Edited'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES, default='regular')
    
    # Time tracking
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    break_duration = models.DurationField(default=timedelta(0))
    
    # Location tracking (optional)
    clock_in_location = models.CharField(max_length=200, blank=True)
    clock_out_location = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    # Approval workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_time_entries')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Manual adjustments
    original_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    adjusted_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    adjustment_reason = models.TextField(blank=True)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='adjusted_time_entries')
    
    # Notes and metadata
    notes = models.TextField(blank=True)
    is_remote_work = models.BooleanField(default=False)
    project_code = models.CharField(max_length=50, blank=True, help_text="Optional project or task code")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-clock_in']
        indexes = [
            models.Index(fields=['employee', 'clock_in']),
            models.Index(fields=['status']),
            models.Index(fields=['entry_type']),
        ]
    
    def __str__(self):
        date_str = self.clock_in.strftime('%Y-%m-%d')
        if self.clock_out:
            return f"{self.employee.full_name} - {date_str} ({self.hours_worked}h)"
        return f"{self.employee.full_name} - {date_str} (Active)"
    
    @property
    def hours_worked(self):
        """Calculate total hours worked"""
        if not self.clock_out:
            return Decimal('0.00')
        
        duration = self.clock_out - self.clock_in
        total_seconds = duration.total_seconds()
        
        # Subtract break duration
        break_seconds = self.break_duration.total_seconds()
        work_seconds = total_seconds - break_seconds
        
        # Convert to hours
        hours = max(work_seconds / 3600, 0)
        return Decimal(str(round(hours, 2)))
    
    @property
    def is_overtime(self):
        """Check if this entry qualifies as overtime"""
        if self.adjusted_hours:
            return self.adjusted_hours > Decimal('8.00')
        return self.hours_worked > Decimal('8.00')
    
    @property
    def overtime_hours(self):
        """Calculate overtime hours"""
        total_hours = self.adjusted_hours or self.hours_worked
        if total_hours > Decimal('8.00'):
            return total_hours - Decimal('8.00')
        return Decimal('0.00')
    
    @property
    def regular_hours(self):
        """Calculate regular hours (non-overtime)"""
        total_hours = self.adjusted_hours or self.hours_worked
        return min(total_hours, Decimal('8.00'))
    
    def clean(self):
        """Validate time entry data"""
        from django.core.exceptions import ValidationError
        
        if self.clock_out and self.clock_out <= self.clock_in:
            raise ValidationError("Clock out time must be after clock in time")
        
        # Check for overlapping entries
        if self.clock_out:
            overlapping = TimeEntry.objects.filter(
                employee=self.employee,
                status__in=['active', 'completed', 'approved'],
                clock_in__lt=self.clock_out,
                clock_out__gt=self.clock_in
            ).exclude(pk=self.pk)
            
            if overlapping.exists():
                raise ValidationError("This time entry overlaps with existing entries")


class Timesheet(models.Model):
    """Weekly timesheet aggregating time entries"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='timesheets')
    week_start = models.DateField(help_text="Monday of the week")
    week_end = models.DateField(help_text="Sunday of the week")
    
    # Calculated fields
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    regular_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    break_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    
    # Status and approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_timesheets')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Notes
    employee_notes = models.TextField(blank=True, help_text="Employee comments")
    manager_notes = models.TextField(blank=True, help_text="Manager comments")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-week_start']
        unique_together = ['employee', 'week_start']
        indexes = [
            models.Index(fields=['employee', 'week_start']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - Week {self.week_start} ({self.total_hours}h)"
    
    def save(self, *args, **kwargs):
        """Auto-calculate week_end and totals before saving"""
        if self.week_start and not self.week_end:
            self.week_end = self.week_start + timedelta(days=6)
        
        super().save(*args, **kwargs)
        
        # Recalculate totals
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculate total hours from related time entries"""
        time_entries = TimeEntry.objects.filter(
            employee=self.employee,
            clock_in__date__gte=self.week_start,
            clock_in__date__lte=self.week_end,
            status__in=['completed', 'approved'],
            clock_out__isnull=False
        )
        
        total_regular = Decimal('0.00')
        total_overtime = Decimal('0.00')
        total_break = Decimal('0.00')
        
        for entry in time_entries:
            total_regular += entry.regular_hours
            total_overtime += entry.overtime_hours
            total_break += Decimal(str(entry.break_duration.total_seconds() / 3600))
        
        self.regular_hours = total_regular
        self.overtime_hours = total_overtime
        self.total_hours = total_regular + total_overtime
        self.break_hours = total_break
        
        # Save without triggering recursion
        Timesheet.objects.filter(pk=self.pk).update(
            regular_hours=self.regular_hours,
            overtime_hours=self.overtime_hours,
            total_hours=self.total_hours,
            break_hours=self.break_hours
        )
    
    @property
    def time_entries(self):
        """Get all time entries for this timesheet period"""
        return TimeEntry.objects.filter(
            employee=self.employee,
            clock_in__date__gte=self.week_start,
            clock_in__date__lte=self.week_end
        ).order_by('clock_in')
    
    @property
    def is_editable(self):
        """Check if timesheet can be edited"""
        return self.status in ['draft', 'rejected']
    
    @property
    def missing_days(self):
        """Get list of days with no time entries"""
        current_date = self.week_start
        missing = []
        
        while current_date <= self.week_end:
            # Skip weekends for standard schedules
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                has_entry = self.time_entries.filter(
                    clock_in__date=current_date
                ).exists()
                
                if not has_entry:
                    missing.append(current_date)
            
            current_date += timedelta(days=1)
        
        return missing


class AttendanceReport(models.Model):
    """Attendance summary reports"""
    
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('employee', 'Employee Report'),
        ('department', 'Department Report'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    
    # Report parameters
    start_date = models.DateField()
    end_date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    
    # Report data (JSON format for flexibility)
    report_data = models.JSONField()
    
    # File export
    file = models.FileField(upload_to='attendance_reports/', null=True, blank=True)
    
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.start_date} to {self.end_date}"


class OvertimeRequest(models.Model):
    """Overtime work requests and approvals"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_requests')
    requested_date = models.DateField()
    estimated_hours = models.DecimalField(max_digits=4, decimal_places=2)
    reason = models.TextField()
    
    # Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_overtime_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Actual vs estimated
    actual_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    time_entry = models.ForeignKey(TimeEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='overtime_request')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-requested_date']
        unique_together = ['employee', 'requested_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.requested_date} ({self.estimated_hours}h OT)"
    
    @property
    def variance_hours(self):
        """Calculate difference between estimated and actual hours"""
        if self.actual_hours:
            return self.actual_hours - self.estimated_hours
        return None
