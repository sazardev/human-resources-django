from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal
from simple_history.models import HistoricalRecords

User = get_user_model()


class LeaveType(models.Model):
    """Model for different types of leave (vacation, sick, personal, etc.)"""
    
    CARRY_OVER_CHOICES = [
        ('none', 'No Carry Over'),
        ('partial', 'Partial Carry Over'),
        ('full', 'Full Carry Over'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=7, default='#3498db', help_text="Hex color for calendar display")
    
    # Leave allocation and rules
    default_days_per_year = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    max_days_per_request = models.PositiveIntegerField(
        default=30,
        help_text="Maximum consecutive days that can be requested"
    )
    min_notice_days = models.PositiveIntegerField(
        default=1,
        help_text="Minimum days of advance notice required"
    )
    
    # Carry over rules
    carry_over_type = models.CharField(
        max_length=10,
        choices=CARRY_OVER_CHOICES,
        default='none'
    )
    max_carry_over_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    carry_over_expiry_months = models.PositiveIntegerField(
        default=12,
        help_text="Months after which carried over leave expires"
    )
    
    # Business rules
    requires_approval = models.BooleanField(default=True)
    requires_documentation = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Holiday(models.Model):
    """Model for company holidays and observances"""
    
    HOLIDAY_TYPE_CHOICES = [
        ('public', 'Public Holiday'),
        ('company', 'Company Holiday'),
        ('observance', 'Observance'),
        ('floating', 'Floating Holiday'),
    ]
    
    name = models.CharField(max_length=100)
    date = models.DateField()
    holiday_type = models.CharField(
        max_length=15,
        choices=HOLIDAY_TYPE_CHOICES,
        default='public'
    )
    description = models.TextField(blank=True, null=True)
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Whether this holiday is mandatory for all employees"
    )
    affects_leave_calculation = models.BooleanField(
        default=True,
        help_text="Whether this holiday affects leave day calculations"
    )
    
    # Location/Department specific holidays
    departments = models.ManyToManyField(
        'employees.Department',
        blank=True,
        help_text="Leave empty for company-wide holidays"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.date})"

    class Meta:
        ordering = ['date']
        unique_together = ['name', 'date']


class LeaveBalance(models.Model):
    """Model for tracking employee leave balances"""
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    year = models.PositiveIntegerField(default=timezone.now().year)
    
    # Balance tracking
    allocated_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    pending_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    carried_over_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    @property
    def available_days(self):
        """Calculate available leave days"""
        return self.allocated_days + self.carried_over_days - self.used_days - self.pending_days

    @property
    def total_allocated(self):
        """Total allocated days including carry over"""
        return self.allocated_days + self.carried_over_days

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} ({self.year})"

    class Meta:
        ordering = ['-year', 'employee', 'leave_type']
        unique_together = ['employee', 'leave_type', 'year']


class LeaveRequest(models.Model):
    """Model for leave requests and applications"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    DURATION_TYPE_CHOICES = [
        ('full_day', 'Full Day'),
        ('half_day_morning', 'Half Day (Morning)'),
        ('half_day_afternoon', 'Half Day (Afternoon)'),
        ('hours', 'Specific Hours'),
    ]
    
    # Request identification
    request_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Employee and leave details
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    
    # Date and duration information
    start_date = models.DateField()
    end_date = models.DateField()
    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_TYPE_CHOICES,
        default='full_day'
    )
    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.5'))]
    )
    
    # Request details
    reason = models.TextField(help_text="Reason for leave request")
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Approval workflow
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='draft'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Documentation
    supporting_document = models.FileField(
        upload_to='leave_documents/',
        blank=True,
        null=True,
        help_text="Supporting documentation (medical certificate, etc.)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Generate request ID if not set
        if not self.request_id:
            self.request_id = self._generate_request_id()
        
        # Calculate total days if not set
        if not self.total_days:
            self.total_days = self._calculate_total_days()
        
        # Set submitted_at when status changes to pending
        if self.status == 'pending' and not self.submitted_at:
            self.submitted_at = timezone.now()
        
        super().save(*args, **kwargs)

    def _generate_request_id(self):
        """Generate unique request ID"""
        year = timezone.now().year
        count = LeaveRequest.objects.filter(
            created_at__year=year
        ).count() + 1
        return f"LR{year}{count:06d}"

    def _calculate_total_days(self):
        """Calculate total leave days based on dates and duration type"""
        if not self.start_date or not self.end_date:
            return Decimal('0')
        
        # Get business days between start and end date
        total_days = self._get_business_days_count()
        
        # Adjust based on duration type
        if self.duration_type in ['half_day_morning', 'half_day_afternoon']:
            if self.start_date == self.end_date:
                return Decimal('0.5')
            else:
                # First day is half, last day is full, middle days are full
                return total_days - Decimal('0.5')
        
        return Decimal(str(total_days))

    def _get_business_days_count(self):
        """Calculate business days excluding weekends and holidays"""
        current_date = self.start_date
        business_days = 0
        
        while current_date <= self.end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                # Check if it's not a holiday
                if not Holiday.objects.filter(
                    date=current_date,
                    affects_leave_calculation=True
                ).exists():
                    business_days += 1
            current_date += timedelta(days=1)
        
        return business_days

    def clean(self):
        """Validate leave request data"""
        super().clean()
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be after end date")
            
            # Check minimum notice period
            if self.leave_type and self.leave_type.min_notice_days > 0:
                notice_date = timezone.now().date() + timedelta(days=self.leave_type.min_notice_days)
                if self.start_date < notice_date:
                    raise ValidationError(
                        f"Minimum {self.leave_type.min_notice_days} days notice required"
                    )
            
            # Check maximum days per request
            total_days = self._calculate_total_days()
            if self.leave_type and total_days > self.leave_type.max_days_per_request:
                raise ValidationError(
                    f"Maximum {self.leave_type.max_days_per_request} days allowed per request"
                )

    @property
    def can_be_cancelled(self):
        """Check if request can be cancelled"""
        return self.status in ['pending', 'approved'] and self.start_date > timezone.now().date()

    @property
    def is_overlapping_weekend(self):
        """Check if request includes weekends"""
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() >= 5:  # Saturday or Sunday
                return True
            current_date += timedelta(days=1)
        return False

    def __str__(self):
        return f"{self.request_id} - {self.employee} ({self.leave_type.name})"

    class Meta:
        ordering = ['-created_at']


class LeaveRequestComment(models.Model):
    """Model for comments and notes on leave requests"""
    
    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    commented_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_comments'
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comments not visible to the employee"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"Comment on {self.leave_request.request_id} by {self.commented_by}"

    class Meta:
        ordering = ['-created_at']


class TeamSchedule(models.Model):
    """Model for tracking team leave schedules and conflicts"""
    
    department = models.ForeignKey(
        'employees.Department',
        on_delete=models.CASCADE,
        related_name='team_schedules'
    )
    date = models.DateField()
    employees_on_leave = models.ManyToManyField(
        'employees.Employee',
        related_name='team_schedule_dates'
    )
    total_employees = models.PositiveIntegerField(default=0)
    employees_on_leave_count = models.PositiveIntegerField(default=0)
    
    # Thresholds
    max_leave_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.0,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    
    # Status
    is_critical = models.BooleanField(
        default=False,
        help_text="True if leave percentage exceeds threshold"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    @property
    def leave_percentage(self):
        """Calculate percentage of employees on leave"""
        if self.total_employees == 0:
            return Decimal('0')
        return (Decimal(self.employees_on_leave_count) / Decimal(self.total_employees)) * Decimal('100')

    def save(self, *args, **kwargs):
        # Update critical status based on leave percentage
        self.is_critical = self.leave_percentage > self.max_leave_percentage
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.department.name} - {self.date} ({self.employees_on_leave_count}/{self.total_employees})"

    class Meta:
        ordering = ['date', 'department']
        unique_together = ['department', 'date']


class LeavePolicy(models.Model):
    """Model for company-wide leave policies and rules"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Policy rules
    blackout_dates_start = models.DateField(
        null=True,
        blank=True,
        help_text="Start of blackout period (e.g., year-end)"
    )
    blackout_dates_end = models.DateField(
        null=True,
        blank=True,
        help_text="End of blackout period"
    )
    
    # Department-specific rules
    department = models.ForeignKey(
        'employees.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Leave empty for company-wide policy"
    )
    
    # General settings
    probation_leave_allowed = models.BooleanField(
        default=False,
        help_text="Allow leave during probation period"
    )
    advance_booking_months = models.PositiveIntegerField(
        default=12,
        help_text="How far in advance can leave be booked"
    )
    
    # Active status
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(default=timezone.now)
    effective_until = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-effective_from']
