from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PayrollPeriod, TaxBracket, DeductionType, BonusType,
    Payslip, PayslipDeduction, PayslipBonus, CompensationHistory,
    PayrollConfiguration
)


@admin.register(PayrollConfiguration)
class PayrollConfigurationAdmin(admin.ModelAdmin):
    list_display = ['id', 'default_country', 'tax_year', 'default_overtime_rate', 'working_days_per_month']
    fieldsets = (        ('General Settings', {
            'fields': ('default_country', 'tax_year', 'working_days_per_month', 'working_hours_per_day')
        }),('Overtime Settings', {
            'fields': ('default_overtime_rate', 'overtime_threshold_hours')
        }),
        ('Leave Integration', {
            'fields': ('integrate_with_leave_management',)
        }),        ('Approval Settings', {
            'fields': ('require_payroll_approval',)
        }),
        ('Numbering Format', {
            'fields': ('payslip_number_prefix', 'payslip_number_format')
        }),
    )


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'status', 'total_employees', 'total_amount', 'created_at']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Period Information', {
            'fields': ('name', 'description', 'start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_employees(self, obj):
        return obj.payslips.count()
    total_employees.short_description = 'Total Employees'
    
    def total_amount(self, obj):
        total = obj.payslips.aggregate(total=models.Sum('net_salary'))['total'] or 0
        return f"${total:,.2f}"
    total_amount.short_description = 'Total Net Amount'


@admin.register(TaxBracket)
class TaxBracketAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'year', 'min_amount', 'max_amount', 'tax_rate', 'is_active']
    list_filter = ['country', 'year', 'is_active']
    search_fields = ['name', 'country']
    ordering = ['country', 'year', 'min_amount']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'year')
        }),
        ('Tax Calculation', {
            'fields': ('min_amount', 'max_amount', 'tax_rate', 'fixed_amount')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(DeductionType)
class DeductionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'calculation_method', 'default_amount', 'is_mandatory', 'is_pre_tax', 'is_active']
    list_filter = ['calculation_method', 'is_mandatory', 'is_pre_tax', 'is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'code')
        }),
        ('Calculation', {
            'fields': ('calculation_method', 'default_amount')
        }),
        ('Settings', {
            'fields': ('is_mandatory', 'is_pre_tax', 'is_active')
        }),
    )


@admin.register(BonusType)
class BonusTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'calculation_method', 'default_amount', 'is_taxable', 'is_active']
    list_filter = ['calculation_method', 'is_taxable', 'is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'code')
        }),
        ('Calculation', {
            'fields': ('calculation_method', 'default_amount')
        }),
        ('Settings', {
            'fields': ('is_taxable', 'is_active')
        }),
    )


class PayslipDeductionInline(admin.TabularInline):
    model = PayslipDeduction
    extra = 0
    readonly_fields = ['calculation_base']


class PayslipBonusInline(admin.TabularInline):
    model = PayslipBonus
    extra = 0


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = [
        'payslip_number', 'employee_name', 'payroll_period', 'gross_salary', 
        'net_salary', 'status', 'payment_method', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payroll_period', 'created_at']
    search_fields = [
        'payslip_number', 'employee__first_name', 'employee__last_name', 
        'employee__employee_id'
    ]
    readonly_fields = [
        'payslip_number', 'total_deductions', 'total_bonuses', 
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    inlines = [PayslipDeductionInline, PayslipBonusInline]
    
    fieldsets = (
        ('Employee & Period', {
            'fields': ('employee', 'payroll_period', 'payslip_number')
        }),
        ('Salary Information', {
            'fields': (
                'base_salary', 'overtime_hours', 'overtime_amount',
                'gross_salary', 'net_salary'
            )
        }),
        ('Calculations', {
            'fields': (
                'total_deductions', 'total_bonuses', 'tax_amount', 
                'unpaid_leave_days'
            )
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_date', 'payment_reference')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__first_name'
    
    def gross_salary(self, obj):
        return f"${obj.gross_salary:,.2f}"
    gross_salary.short_description = 'Gross Salary'
    gross_salary.admin_order_field = 'gross_salary'
    
    def net_salary(self, obj):
        return f"${obj.net_salary:,.2f}"
    net_salary.short_description = 'Net Salary'
    net_salary.admin_order_field = 'net_salary'


@admin.register(CompensationHistory)
class CompensationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'employee_name', 'change_type', 'previous_salary', 'new_salary', 
        'salary_change', 'effective_date', 'created_at'
    ]
    list_filter = ['change_type', 'effective_date', 'created_at']
    search_fields = [
        'employee__first_name', 'employee__last_name', 
        'employee__employee_id', 'reason'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Salary Change', {
            'fields': ('change_type', 'previous_salary', 'new_salary', 'effective_date')
        }),
        ('Details', {
            'fields': ('reason',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__first_name'
    
    def previous_salary(self, obj):
        return f"${obj.previous_salary:,.2f}"
    previous_salary.short_description = 'Previous Salary'
    previous_salary.admin_order_field = 'previous_salary'
    
    def new_salary(self, obj):
        return f"${obj.new_salary:,.2f}"
    new_salary.short_description = 'New Salary'
    new_salary.admin_order_field = 'new_salary'
    
    def salary_change(self, obj):
        change = obj.new_salary - obj.previous_salary
        if change > 0:
            return format_html('<span style="color: green;">+${:,.2f}</span>', change)
        elif change < 0:
            return format_html('<span style="color: red;">${:,.2f}</span>', change)
        else:
            return '$0.00'
    salary_change.short_description = 'Change'
