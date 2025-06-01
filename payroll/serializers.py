from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date
from .models import (
    PayrollPeriod, TaxBracket, DeductionType, BonusType, 
    Payslip, PayslipDeduction, PayslipBonus, CompensationHistory,
    PayrollConfiguration
)
from employees.models import Employee, PerformanceReview
from employees.mixins import SelectableFieldsSerializer

User = get_user_model()


class PayrollPeriodSerializer(SelectableFieldsSerializer):
    """Serializer for PayrollPeriod model with dynamic field selection"""
    
    total_employees = serializers.ReadOnlyField()
    is_editable = serializers.ReadOnlyField()
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'name', 'start_date', 'end_date', 'pay_date', 'frequency', 'status',
            'total_gross_amount', 'total_net_amount', 'total_deductions',
            'processed_by', 'processed_by_name', 'processed_date',
            'total_employees', 'is_editable', 'created_at', 'updated_at'
        ]
        read_only_fields = ['processed_date', 'total_gross_amount', 'total_net_amount', 'total_deductions']

    def validate(self, data):
        """Validate payroll period dates"""
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        
        if data['pay_date'] < data['end_date']:
            raise serializers.ValidationError("Pay date must be on or after the end date")
        
        return data


class TaxBracketSerializer(SelectableFieldsSerializer):
    """Serializer for TaxBracket model with dynamic field selection"""
    
    tax_rate_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = TaxBracket
        fields = [
            'id', 'name', 'country', 'year', 'min_amount', 'max_amount',
            'tax_rate', 'tax_rate_percentage', 'fixed_amount', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_tax_rate_percentage(self, obj):
        """Convert tax rate to percentage"""
        return float(obj.tax_rate) * 100

    def validate(self, data):
        """Validate tax bracket amounts"""
        if data.get('max_amount') and data['min_amount'] >= data['max_amount']:
            raise serializers.ValidationError("Min amount must be less than max amount")
        
        if data['tax_rate'] < 0 or data['tax_rate'] > 1:
            raise serializers.ValidationError("Tax rate must be between 0 and 1")
        
        return data


class DeductionTypeSerializer(SelectableFieldsSerializer):
    """Serializer for DeductionType model with dynamic field selection"""
    
    default_amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DeductionType
        fields = [
            'id', 'name', 'description', 'calculation_method', 'default_amount',
            'default_amount_display', 'is_mandatory', 'is_pre_tax', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_default_amount_display(self, obj):
        """Format default amount based on calculation method"""
        if obj.calculation_method == 'percentage':
            return f"{float(obj.default_amount) * 100:.2f}%"
        else:
            return f"${obj.default_amount:.2f}"


class BonusTypeSerializer(SelectableFieldsSerializer):
    """Serializer for BonusType model with dynamic field selection"""
    
    default_amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = BonusType
        fields = [
            'id', 'name', 'description', 'calculation_method', 'default_amount',
            'default_amount_display', 'is_taxable', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_default_amount_display(self, obj):
        """Format default amount based on calculation method"""
        if obj.calculation_method == 'percentage':
            return f"{float(obj.default_amount) * 100:.2f}%"
        else:
            return f"${obj.default_amount:.2f}"


class PayslipDeductionSerializer(SelectableFieldsSerializer):
    """Serializer for PayslipDeduction model with dynamic field selection"""
    
    deduction_type_name = serializers.CharField(source='deduction_type.name', read_only=True)
    calculation_method = serializers.CharField(source='deduction_type.calculation_method', read_only=True)
    
    class Meta:
        model = PayslipDeduction
        fields = [
            'id', 'deduction_type', 'deduction_type_name', 'calculation_method',
            'amount', 'calculation_base', 'description', 'created_at', 'updated_at'
        ]


class PayslipBonusSerializer(SelectableFieldsSerializer):
    """Serializer for PayslipBonus model with dynamic field selection"""
    
    bonus_type_name = serializers.CharField(source='bonus_type.name', read_only=True)
    calculation_method = serializers.CharField(source='bonus_type.calculation_method', read_only=True)
    performance_review_id = serializers.IntegerField(source='performance_review.id', read_only=True)
    
    class Meta:
        model = PayslipBonus
        fields = [
            'id', 'bonus_type', 'bonus_type_name', 'calculation_method',
            'amount', 'calculation_base', 'description', 'performance_review',
            'performance_review_id', 'created_at', 'updated_at'
        ]


class PayslipSerializer(SelectableFieldsSerializer):
    """Serializer for Payslip model with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    employee_department = serializers.CharField(source='employee.department.name', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    # Properties
    daily_salary = serializers.ReadOnlyField()
    overtime_pay = serializers.ReadOnlyField()
    leave_deduction = serializers.ReadOnlyField()
    
    # Related objects
    deductions = PayslipDeductionSerializer(many=True, read_only=True)
    bonuses = PayslipBonusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'employee_position',
            'employee_department', 'payroll_period', 'payroll_period_name',
            'payslip_number', 'status', 'base_salary', 'hours_worked',
            'overtime_hours', 'overtime_rate', 'unpaid_leave_days',
            'gross_salary', 'total_bonuses', 'total_deductions', 'tax_amount',
            'net_salary', 'payment_method', 'payment_reference', 'payment_date',
            'approved_by', 'approved_by_name', 'approved_date', 'notes',
            'employee_notes', 'daily_salary', 'overtime_pay', 'leave_deduction',
            'deductions', 'bonuses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['payslip_number', 'approved_date']

    def validate(self, data):
        """Validate payslip data"""
        if data.get('overtime_hours', 0) < 0:
            raise serializers.ValidationError("Overtime hours cannot be negative")
        
        if data.get('unpaid_leave_days', 0) < 0:
            raise serializers.ValidationError("Unpaid leave days cannot be negative")
        
        if data.get('base_salary', 0) <= 0:
            raise serializers.ValidationError("Base salary must be greater than zero")
        
        return data


class PayslipSummarySerializer(SelectableFieldsSerializer):
    """Lightweight serializer for payslip summaries with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'employee_name', 'employee_id', 'payroll_period_name',
            'payslip_number', 'status', 'base_salary', 'gross_salary',
            'net_salary', 'payment_date', 'created_at'
        ]


class CompensationHistorySerializer(SelectableFieldsSerializer):
    """Serializer for CompensationHistory model with dynamic field selection"""
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    performance_review_id = serializers.IntegerField(source='performance_review.id', read_only=True)
    
    # Properties
    salary_change_amount = serializers.ReadOnlyField()
    salary_change_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = CompensationHistory
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'change_type',
            'effective_date', 'previous_salary', 'new_salary', 'currency',
            'reason', 'approved_by', 'approved_by_name', 'performance_review',
            'performance_review_id', 'supporting_documents', 'salary_change_amount',
            'salary_change_percentage', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate compensation history data"""
        if data.get('new_salary', 0) <= 0:
            raise serializers.ValidationError("New salary must be greater than zero")
        
        if data.get('previous_salary') and data['previous_salary'] < 0:
            raise serializers.ValidationError("Previous salary cannot be negative")
        
        effective_date = data.get('effective_date')
        if effective_date and effective_date > date.today():
            raise serializers.ValidationError("Effective date cannot be in the future")
        
        return data


class PayrollConfigurationSerializer(SelectableFieldsSerializer):
    """Serializer for PayrollConfiguration model with dynamic field selection"""
    
    class Meta:
        model = PayrollConfiguration
        fields = [
            'id', 'working_days_per_month', 'working_hours_per_day',
            'overtime_threshold_hours', 'default_overtime_rate', 'default_country',
            'tax_year', 'integrate_with_leave_management', 'payslip_number_prefix',
            'payslip_number_format', 'require_payroll_approval', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate payroll configuration"""
        if data.get('working_days_per_month', 0) <= 0:
            raise serializers.ValidationError("Working days per month must be greater than zero")
        
        if data.get('working_hours_per_day', 0) <= 0:
            raise serializers.ValidationError("Working hours per day must be greater than zero")
        
        if data.get('overtime_threshold_hours', 0) < 0:
            raise serializers.ValidationError("Overtime threshold hours cannot be negative")
        
        if data.get('default_overtime_rate', 0) < 1:
            raise serializers.ValidationError("Default overtime rate must be at least 1.0")
        
        return data


# Employee extension serializers for payroll integration
class EmployeePayrollSerializer(SelectableFieldsSerializer):
    """Serializer for Employee model with payroll-specific fields and dynamic field selection"""
    
    current_salary = serializers.DecimalField(source='salary', max_digits=10, decimal_places=2, read_only=True)
    latest_payslip = PayslipSummarySerializer(source='payslips.first', read_only=True)
    total_compensation_changes = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'position',
            'department', 'employment_status', 'hire_date', 'current_salary',
            'latest_payslip', 'total_compensation_changes'
        ]
    
    def get_total_compensation_changes(self, obj):
        """Get count of compensation changes"""
        return obj.compensation_history.count()


class PayrollReportSerializer(serializers.Serializer):
    """Serializer for payroll reports"""
    
    period_name = serializers.CharField()
    total_employees = serializers.IntegerField()
    total_gross_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_taxes = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_bonuses = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Department breakdown
    department_breakdown = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    
    # Status breakdown
    status_breakdown = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )


class PayslipCalculationSerializer(serializers.Serializer):
    """Serializer for payslip calculation requests"""
    
    employee_id = serializers.IntegerField()
    payroll_period_id = serializers.IntegerField()
    override_base_salary = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    overtime_hours = serializers.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    unpaid_leave_days = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    additional_bonuses = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )
    additional_deductions = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )

    def validate_employee_id(self, value):
        """Validate employee exists"""
        try:
            Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found")
        return value

    def validate_payroll_period_id(self, value):
        """Validate payroll period exists"""
        try:
            PayrollPeriod.objects.get(id=value)
        except PayrollPeriod.DoesNotExist:
            raise serializers.ValidationError("Payroll period not found")
        return value
