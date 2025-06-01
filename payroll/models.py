from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime
from simple_history.models import HistoricalRecords

User = get_user_model()


class PayrollPeriod(models.Model):
    """Payroll period for organizing payroll processing"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('finalized', 'Finalized'),
        ('cancelled', 'Cancelled'),
    ]
    
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-Weekly'),
        ('semi_monthly', 'Semi-Monthly'),
        ('monthly', 'Monthly'),
    ]
    
    name = models.CharField(max_length=100, help_text="e.g., 'December 2024' or 'Q4 2024'")
    start_date = models.DateField()
    end_date = models.DateField()
    pay_date = models.DateField(help_text="When employees will be paid")
    frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES, default='monthly')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    total_gross_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        help_text="Total gross amount for all employees"
    )
    total_net_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        help_text="Total net amount after deductions"
    )
    total_deductions = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        help_text="Total deductions for all employees"
    )
    
    # Processing info
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='processed_payrolls'
    )
    processed_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    @property
    def total_employees(self):
        """Get total number of employees in this payroll period"""
        return self.payslips.count()

    @property
    def is_editable(self):
        """Check if payroll period can be edited"""
        return self.status in ['draft', 'processing']

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    class Meta:
        ordering = ['-start_date']
        unique_together = ['start_date', 'end_date', 'frequency']


class TaxBracket(models.Model):
    """Tax brackets for income tax calculations"""
    
    name = models.CharField(max_length=100, help_text="e.g., 'Mexico Income Tax 2024'")
    country = models.CharField(max_length=50, default='Mexico')
    year = models.PositiveIntegerField(default=timezone.now().year)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, blank=True,
        help_text="Leave blank for highest bracket"
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Tax rate as decimal (e.g., 0.1 for 10%)"
    )
    fixed_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Fixed tax amount for this bracket"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        max_str = f" - ${self.max_amount:,.2f}" if self.max_amount else "+"
        return f"{self.name}: ${self.min_amount:,.2f}{max_str} ({self.tax_rate:.2%})"

    class Meta:
        ordering = ['country', 'year', 'min_amount']


class DeductionType(models.Model):
    """Types of deductions from salary"""
    
    CALCULATION_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
        ('tax', 'Tax Calculation'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    calculation_method = models.CharField(max_length=15, choices=CALCULATION_CHOICES)
    default_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=0,
        help_text="Default amount or percentage (e.g., 0.05 for 5%)"
    )
    is_mandatory = models.BooleanField(
        default=False,
        help_text="Whether this deduction is mandatory for all employees"
    )
    is_pre_tax = models.BooleanField(
        default=False,
        help_text="Whether this deduction is calculated before taxes"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.get_calculation_method_display()})"

    class Meta:
        ordering = ['name']


class BonusType(models.Model):
    """Types of bonuses that can be awarded"""
    
    CALCULATION_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Salary'),
        ('performance', 'Performance Based'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    calculation_method = models.CharField(max_length=15, choices=CALCULATION_CHOICES)
    default_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=0,
        help_text="Default amount or percentage"
    )
    is_taxable = models.BooleanField(
        default=True,
        help_text="Whether this bonus is subject to taxes"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.get_calculation_method_display()})"

    class Meta:
        ordering = ['name']


class Payslip(models.Model):
    """Individual payslip for an employee in a specific payroll period"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic info
    employee = models.ForeignKey(
        'employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='payslips'
    )
    payroll_period = models.ForeignKey(
        PayrollPeriod, 
        on_delete=models.CASCADE, 
        related_name='payslips'
    )
    payslip_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    
    # Salary information
    base_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Base salary for this period"
    )
    hours_worked = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        help_text="Total hours worked in period"
    )
    overtime_hours = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        help_text="Overtime hours worked"
    )
    overtime_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('1.5'),
        help_text="Overtime multiplier (e.g., 1.5 for time and a half)"
    )
    
    # Leave deductions
    unpaid_leave_days = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Days of unpaid leave to deduct"
    )
    
    # Calculated amounts
    gross_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total gross salary before deductions"
    )
    total_bonuses = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total bonuses for this period"
    )
    total_deductions = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total deductions"
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Total tax amount"
    )
    net_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Final amount to be paid"
    )
    
    # Payment tracking
    payment_method = models.CharField(
        max_length=20, 
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('check', 'Check'),
            ('cash', 'Cash'),
            ('direct_deposit', 'Direct Deposit'),
        ],
        default='bank_transfer'
    )
    payment_reference = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Payment reference number or transaction ID"
    )
    payment_date = models.DateField(null=True, blank=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='approved_payslips'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Notes and comments
    notes = models.TextField(blank=True, help_text="Internal notes")
    employee_notes = models.TextField(
        blank=True, 
        help_text="Notes visible to employee"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    @property
    def daily_salary(self):
        """Calculate daily salary based on monthly salary"""
        if self.base_salary:
            # Assuming 30 days per month for calculation
            return self.base_salary / 30
        return Decimal('0')

    @property
    def overtime_pay(self):
        """Calculate overtime pay"""
        if self.overtime_hours and self.base_salary:
            hourly_rate = self.base_salary / (30 * 8)  # Assuming 8 hours/day
            return self.overtime_hours * hourly_rate * self.overtime_rate
        return Decimal('0')

    @property
    def leave_deduction(self):
        """Calculate deduction for unpaid leave"""
        return self.unpaid_leave_days * self.daily_salary

    def calculate_gross_salary(self):
        """Calculate gross salary including overtime and bonuses"""
        gross = self.base_salary + self.overtime_pay + self.total_bonuses
        gross -= self.leave_deduction
        return gross

    def calculate_net_salary(self):
        """Calculate net salary after all deductions"""
        gross = self.calculate_gross_salary()
        return gross - self.total_deductions - self.tax_amount

    def __str__(self):
        return f"{self.payslip_number} - {self.employee.full_name} ({self.payroll_period.name})"

    class Meta:
        ordering = ['-payroll_period__start_date', 'employee__employee_id']
        unique_together = ['employee', 'payroll_period']


class PayslipDeduction(models.Model):
    """Individual deductions on a payslip"""
    
    payslip = models.ForeignKey(
        Payslip, 
        on_delete=models.CASCADE, 
        related_name='deductions'
    )
    deduction_type = models.ForeignKey(
        DeductionType, 
        on_delete=models.CASCADE,
        related_name='payslip_deductions'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    calculation_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, blank=True,
        help_text="Base amount used for percentage calculations"
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details about this deduction"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.payslip.payslip_number} - {self.deduction_type.name}: ${self.amount}"

    class Meta:
        ordering = ['payslip', 'deduction_type']


class PayslipBonus(models.Model):
    """Individual bonuses on a payslip"""
    
    payslip = models.ForeignKey(
        Payslip, 
        on_delete=models.CASCADE, 
        related_name='bonuses'
    )
    bonus_type = models.ForeignKey(
        BonusType, 
        on_delete=models.CASCADE,
        related_name='payslip_bonuses'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    calculation_base = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, blank=True,
        help_text="Base amount used for percentage calculations"
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details about this bonus"
    )
    
    # Performance linkage
    performance_review = models.ForeignKey(
        'employees.PerformanceReview',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='linked_bonuses',
        help_text="Performance review that triggered this bonus"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.payslip.payslip_number} - {self.bonus_type.name}: ${self.amount}"

    class Meta:
        ordering = ['payslip', 'bonus_type']


class CompensationHistory(models.Model):
    """Historical record of salary changes and adjustments"""
    
    CHANGE_TYPE_CHOICES = [
        ('hire', 'Initial Hire'),
        ('promotion', 'Promotion'),
        ('adjustment', 'Salary Adjustment'),
        ('bonus', 'One-time Bonus'),
        ('demotion', 'Demotion'),
        ('correction', 'Correction'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='compensation_history'
    )
    change_type = models.CharField(max_length=15, choices=CHANGE_TYPE_CHOICES)
    effective_date = models.DateField(default=date.today)
    
    # Salary information
    previous_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, blank=True,
        help_text="Previous salary amount"
    )
    new_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="New salary amount"
    )
    currency = models.CharField(max_length=10, default='MXN')
    
    # Change details
    reason = models.TextField(help_text="Reason for the change")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='approved_compensation_changes'
    )
    
    # Performance linkage
    performance_review = models.ForeignKey(
        'employees.PerformanceReview',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='compensation_changes',
        help_text="Performance review that triggered this change"
    )
    
    # Documentation
    supporting_documents = models.TextField(
        blank=True,
        help_text="References to supporting documents"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    @property
    def salary_change_amount(self):
        """Calculate the change in salary"""
        if self.previous_salary:
            return self.new_salary - self.previous_salary
        return self.new_salary

    @property
    def salary_change_percentage(self):
        """Calculate the percentage change in salary"""
        if self.previous_salary and self.previous_salary > 0:
            change = self.salary_change_amount
            return (change / self.previous_salary) * 100
        return None

    def __str__(self):
        change_str = f"${self.salary_change_amount:,.2f}"
        if self.salary_change_percentage:
            change_str += f" ({self.salary_change_percentage:+.1f}%)"
        return f"{self.employee.full_name} - {self.get_change_type_display()}: {change_str}"

    class Meta:
        ordering = ['-effective_date', 'employee']
        verbose_name_plural = "Compensation histories"


class PayrollConfiguration(models.Model):
    """Global payroll configuration settings"""
    
    # Working days configuration
    working_days_per_month = models.PositiveIntegerField(default=30)
    working_hours_per_day = models.PositiveIntegerField(default=8)
    
    # Overtime settings
    overtime_threshold_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=40,
        help_text="Hours per week before overtime kicks in"
    )
    default_overtime_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('1.5'),
        help_text="Default overtime multiplier"
    )
    
    # Tax settings
    default_country = models.CharField(max_length=50, default='Mexico')
    tax_year = models.PositiveIntegerField(default=timezone.now().year)
    
    # Leave integration
    integrate_with_leave_management = models.BooleanField(
        default=True,
        help_text="Automatically calculate unpaid leave deductions"
    )
    
    # Payroll numbering
    payslip_number_prefix = models.CharField(max_length=10, default='PAY')
    payslip_number_format = models.CharField(
        max_length=50, 
        default='{prefix}{year}{month:02d}{sequence:04d}',
        help_text="Format: {prefix}{year}{month:02d}{sequence:04d}"
    )
    
    # Approval workflow
    require_payroll_approval = models.BooleanField(
        default=True,
        help_text="Require manager approval before processing payroll"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"Payroll Configuration - {self.default_country} {self.tax_year}"

    class Meta:
        verbose_name = "Payroll Configuration"
        verbose_name_plural = "Payroll Configurations"
