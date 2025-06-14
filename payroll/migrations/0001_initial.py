# Generated by Django 5.2.1 on 2025-06-01 02:38

import datetime
import django.core.validators
import django.db.models.deletion
import simple_history.models
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0002_historicaldepartment_historicalemployee_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BonusType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('calculation_method', models.CharField(choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Salary'), ('performance', 'Performance Based')], max_length=15)),
                ('default_amount', models.DecimalField(decimal_places=4, default=0, help_text='Default amount or percentage', max_digits=10)),
                ('is_taxable', models.BooleanField(default=True, help_text='Whether this bonus is subject to taxes')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DeductionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('calculation_method', models.CharField(choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage'), ('tax', 'Tax Calculation')], max_length=15)),
                ('default_amount', models.DecimalField(decimal_places=4, default=0, help_text='Default amount or percentage (e.g., 0.05 for 5%)', max_digits=10)),
                ('is_mandatory', models.BooleanField(default=False, help_text='Whether this deduction is mandatory for all employees')),
                ('is_pre_tax', models.BooleanField(default=False, help_text='Whether this deduction is calculated before taxes')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PayrollConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('working_days_per_month', models.PositiveIntegerField(default=30)),
                ('working_hours_per_day', models.PositiveIntegerField(default=8)),
                ('overtime_threshold_hours', models.DecimalField(decimal_places=2, default=40, help_text='Hours per week before overtime kicks in', max_digits=5)),
                ('default_overtime_rate', models.DecimalField(decimal_places=2, default=Decimal('1.5'), help_text='Default overtime multiplier', max_digits=5)),
                ('default_country', models.CharField(default='Mexico', max_length=50)),
                ('tax_year', models.PositiveIntegerField(default=2025)),
                ('integrate_with_leave_management', models.BooleanField(default=True, help_text='Automatically calculate unpaid leave deductions')),
                ('payslip_number_prefix', models.CharField(default='PAY', max_length=10)),
                ('payslip_number_format', models.CharField(default='{prefix}{year}{month:02d}{sequence:04d}', help_text='Format: {prefix}{year}{month:02d}{sequence:04d}', max_length=50)),
                ('require_payroll_approval', models.BooleanField(default=True, help_text='Require manager approval before processing payroll')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Payroll Configuration',
                'verbose_name_plural': 'Payroll Configurations',
            },
        ),
        migrations.CreateModel(
            name='TaxBracket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g., 'Mexico Income Tax 2024'", max_length=100)),
                ('country', models.CharField(default='Mexico', max_length=50)),
                ('year', models.PositiveIntegerField(default=2025)),
                ('min_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Leave blank for highest bracket', max_digits=12, null=True)),
                ('tax_rate', models.DecimalField(decimal_places=4, help_text='Tax rate as decimal (e.g., 0.1 for 10%)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('fixed_amount', models.DecimalField(decimal_places=2, default=0, help_text='Fixed tax amount for this bracket', max_digits=12)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['country', 'year', 'min_amount'],
            },
        ),
        migrations.CreateModel(
            name='CompensationHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('hire', 'Initial Hire'), ('promotion', 'Promotion'), ('adjustment', 'Salary Adjustment'), ('bonus', 'One-time Bonus'), ('demotion', 'Demotion'), ('correction', 'Correction')], max_length=15)),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('previous_salary', models.DecimalField(blank=True, decimal_places=2, help_text='Previous salary amount', max_digits=10, null=True)),
                ('new_salary', models.DecimalField(decimal_places=2, help_text='New salary amount', max_digits=10)),
                ('currency', models.CharField(default='MXN', max_length=10)),
                ('reason', models.TextField(help_text='Reason for the change')),
                ('supporting_documents', models.TextField(blank=True, help_text='References to supporting documents')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_compensation_changes', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compensation_history', to='employees.employee')),
                ('performance_review', models.ForeignKey(blank=True, help_text='Performance review that triggered this change', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='compensation_changes', to='employees.performancereview')),
            ],
            options={
                'verbose_name_plural': 'Compensation histories',
                'ordering': ['-effective_date', 'employee'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalBonusType',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('calculation_method', models.CharField(choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Salary'), ('performance', 'Performance Based')], max_length=15)),
                ('default_amount', models.DecimalField(decimal_places=4, default=0, help_text='Default amount or percentage', max_digits=10)),
                ('is_taxable', models.BooleanField(default=True, help_text='Whether this bonus is subject to taxes')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical bonus type',
                'verbose_name_plural': 'historical bonus types',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalCompensationHistory',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('hire', 'Initial Hire'), ('promotion', 'Promotion'), ('adjustment', 'Salary Adjustment'), ('bonus', 'One-time Bonus'), ('demotion', 'Demotion'), ('correction', 'Correction')], max_length=15)),
                ('effective_date', models.DateField(default=datetime.date.today)),
                ('previous_salary', models.DecimalField(blank=True, decimal_places=2, help_text='Previous salary amount', max_digits=10, null=True)),
                ('new_salary', models.DecimalField(decimal_places=2, help_text='New salary amount', max_digits=10)),
                ('currency', models.CharField(default='MXN', max_length=10)),
                ('reason', models.TextField(help_text='Reason for the change')),
                ('supporting_documents', models.TextField(blank=True, help_text='References to supporting documents')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('approved_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='employees.employee')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('performance_review', models.ForeignKey(blank=True, db_constraint=False, help_text='Performance review that triggered this change', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='employees.performancereview')),
            ],
            options={
                'verbose_name': 'historical compensation history',
                'verbose_name_plural': 'historical Compensation histories',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalDeductionType',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('calculation_method', models.CharField(choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage'), ('tax', 'Tax Calculation')], max_length=15)),
                ('default_amount', models.DecimalField(decimal_places=4, default=0, help_text='Default amount or percentage (e.g., 0.05 for 5%)', max_digits=10)),
                ('is_mandatory', models.BooleanField(default=False, help_text='Whether this deduction is mandatory for all employees')),
                ('is_pre_tax', models.BooleanField(default=False, help_text='Whether this deduction is calculated before taxes')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical deduction type',
                'verbose_name_plural': 'historical deduction types',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPayrollConfiguration',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('working_days_per_month', models.PositiveIntegerField(default=30)),
                ('working_hours_per_day', models.PositiveIntegerField(default=8)),
                ('overtime_threshold_hours', models.DecimalField(decimal_places=2, default=40, help_text='Hours per week before overtime kicks in', max_digits=5)),
                ('default_overtime_rate', models.DecimalField(decimal_places=2, default=Decimal('1.5'), help_text='Default overtime multiplier', max_digits=5)),
                ('default_country', models.CharField(default='Mexico', max_length=50)),
                ('tax_year', models.PositiveIntegerField(default=2025)),
                ('integrate_with_leave_management', models.BooleanField(default=True, help_text='Automatically calculate unpaid leave deductions')),
                ('payslip_number_prefix', models.CharField(default='PAY', max_length=10)),
                ('payslip_number_format', models.CharField(default='{prefix}{year}{month:02d}{sequence:04d}', help_text='Format: {prefix}{year}{month:02d}{sequence:04d}', max_length=50)),
                ('require_payroll_approval', models.BooleanField(default=True, help_text='Require manager approval before processing payroll')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Payroll Configuration',
                'verbose_name_plural': 'historical Payroll Configurations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPayrollPeriod',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g., 'December 2024' or 'Q4 2024'", max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('pay_date', models.DateField(help_text='When employees will be paid')),
                ('frequency', models.CharField(choices=[('weekly', 'Weekly'), ('bi_weekly', 'Bi-Weekly'), ('semi_monthly', 'Semi-Monthly'), ('monthly', 'Monthly')], default='monthly', max_length=15)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('processing', 'Processing'), ('processed', 'Processed'), ('finalized', 'Finalized'), ('cancelled', 'Cancelled')], default='draft', max_length=15)),
                ('total_gross_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total gross amount for all employees', max_digits=12)),
                ('total_net_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total net amount after deductions', max_digits=12)),
                ('total_deductions', models.DecimalField(decimal_places=2, default=0, help_text='Total deductions for all employees', max_digits=12)),
                ('processed_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('processed_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical payroll period',
                'verbose_name_plural': 'historical payroll periods',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalTaxBracket',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g., 'Mexico Income Tax 2024'", max_length=100)),
                ('country', models.CharField(default='Mexico', max_length=50)),
                ('year', models.PositiveIntegerField(default=2025)),
                ('min_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Leave blank for highest bracket', max_digits=12, null=True)),
                ('tax_rate', models.DecimalField(decimal_places=4, help_text='Tax rate as decimal (e.g., 0.1 for 10%)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('fixed_amount', models.DecimalField(decimal_places=2, default=0, help_text='Fixed tax amount for this bracket', max_digits=12)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical tax bracket',
                'verbose_name_plural': 'historical tax brackets',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='PayrollPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g., 'December 2024' or 'Q4 2024'", max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('pay_date', models.DateField(help_text='When employees will be paid')),
                ('frequency', models.CharField(choices=[('weekly', 'Weekly'), ('bi_weekly', 'Bi-Weekly'), ('semi_monthly', 'Semi-Monthly'), ('monthly', 'Monthly')], default='monthly', max_length=15)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('processing', 'Processing'), ('processed', 'Processed'), ('finalized', 'Finalized'), ('cancelled', 'Cancelled')], default='draft', max_length=15)),
                ('total_gross_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total gross amount for all employees', max_digits=12)),
                ('total_net_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total net amount after deductions', max_digits=12)),
                ('total_deductions', models.DecimalField(decimal_places=2, default=0, help_text='Total deductions for all employees', max_digits=12)),
                ('processed_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_payrolls', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-start_date'],
                'unique_together': {('start_date', 'end_date', 'frequency')},
            },
        ),
        migrations.CreateModel(
            name='HistoricalPayslip',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('payslip_number', models.CharField(db_index=True, max_length=50)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('calculated', 'Calculated'), ('approved', 'Approved'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='draft', max_length=15)),
                ('base_salary', models.DecimalField(decimal_places=2, help_text='Base salary for this period', max_digits=10)),
                ('hours_worked', models.DecimalField(decimal_places=2, default=0, help_text='Total hours worked in period', max_digits=6)),
                ('overtime_hours', models.DecimalField(decimal_places=2, default=0, help_text='Overtime hours worked', max_digits=6)),
                ('overtime_rate', models.DecimalField(decimal_places=2, default=Decimal('1.5'), help_text='Overtime multiplier (e.g., 1.5 for time and a half)', max_digits=5)),
                ('unpaid_leave_days', models.DecimalField(decimal_places=2, default=0, help_text='Days of unpaid leave to deduct', max_digits=5)),
                ('gross_salary', models.DecimalField(decimal_places=2, default=0, help_text='Total gross salary before deductions', max_digits=10)),
                ('total_bonuses', models.DecimalField(decimal_places=2, default=0, help_text='Total bonuses for this period', max_digits=10)),
                ('total_deductions', models.DecimalField(decimal_places=2, default=0, help_text='Total deductions', max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total tax amount', max_digits=10)),
                ('net_salary', models.DecimalField(decimal_places=2, default=0, help_text='Final amount to be paid', max_digits=10)),
                ('payment_method', models.CharField(choices=[('bank_transfer', 'Bank Transfer'), ('check', 'Check'), ('cash', 'Cash'), ('direct_deposit', 'Direct Deposit')], default='bank_transfer', max_length=20)),
                ('payment_reference', models.CharField(blank=True, help_text='Payment reference number or transaction ID', max_length=100)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, help_text='Internal notes')),
                ('employee_notes', models.TextField(blank=True, help_text='Notes visible to employee')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('approved_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='employees.employee')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('payroll_period', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payroll.payrollperiod')),
            ],
            options={
                'verbose_name': 'historical payslip',
                'verbose_name_plural': 'historical payslips',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Payslip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payslip_number', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('calculated', 'Calculated'), ('approved', 'Approved'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='draft', max_length=15)),
                ('base_salary', models.DecimalField(decimal_places=2, help_text='Base salary for this period', max_digits=10)),
                ('hours_worked', models.DecimalField(decimal_places=2, default=0, help_text='Total hours worked in period', max_digits=6)),
                ('overtime_hours', models.DecimalField(decimal_places=2, default=0, help_text='Overtime hours worked', max_digits=6)),
                ('overtime_rate', models.DecimalField(decimal_places=2, default=Decimal('1.5'), help_text='Overtime multiplier (e.g., 1.5 for time and a half)', max_digits=5)),
                ('unpaid_leave_days', models.DecimalField(decimal_places=2, default=0, help_text='Days of unpaid leave to deduct', max_digits=5)),
                ('gross_salary', models.DecimalField(decimal_places=2, default=0, help_text='Total gross salary before deductions', max_digits=10)),
                ('total_bonuses', models.DecimalField(decimal_places=2, default=0, help_text='Total bonuses for this period', max_digits=10)),
                ('total_deductions', models.DecimalField(decimal_places=2, default=0, help_text='Total deductions', max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, help_text='Total tax amount', max_digits=10)),
                ('net_salary', models.DecimalField(decimal_places=2, default=0, help_text='Final amount to be paid', max_digits=10)),
                ('payment_method', models.CharField(choices=[('bank_transfer', 'Bank Transfer'), ('check', 'Check'), ('cash', 'Cash'), ('direct_deposit', 'Direct Deposit')], default='bank_transfer', max_length=20)),
                ('payment_reference', models.CharField(blank=True, help_text='Payment reference number or transaction ID', max_length=100)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, help_text='Internal notes')),
                ('employee_notes', models.TextField(blank=True, help_text='Notes visible to employee')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_payslips', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payslips', to='employees.employee')),
                ('payroll_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payslips', to='payroll.payrollperiod')),
            ],
            options={
                'ordering': ['-payroll_period__start_date', 'employee__employee_id'],
                'unique_together': {('employee', 'payroll_period')},
            },
        ),
        migrations.CreateModel(
            name='HistoricalPayslipDeduction',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('calculation_base', models.DecimalField(blank=True, decimal_places=2, help_text='Base amount used for percentage calculations', max_digits=10, null=True)),
                ('description', models.TextField(blank=True, help_text='Additional details about this deduction')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('deduction_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payroll.deductiontype')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('payslip', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payroll.payslip')),
            ],
            options={
                'verbose_name': 'historical payslip deduction',
                'verbose_name_plural': 'historical payslip deductions',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPayslipBonus',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('calculation_base', models.DecimalField(blank=True, decimal_places=2, help_text='Base amount used for percentage calculations', max_digits=10, null=True)),
                ('description', models.TextField(blank=True, help_text='Additional details about this bonus')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('bonus_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payroll.bonustype')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('performance_review', models.ForeignKey(blank=True, db_constraint=False, help_text='Performance review that triggered this bonus', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='employees.performancereview')),
                ('payslip', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payroll.payslip')),
            ],
            options={
                'verbose_name': 'historical payslip bonus',
                'verbose_name_plural': 'historical payslip bonuss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='PayslipBonus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('calculation_base', models.DecimalField(blank=True, decimal_places=2, help_text='Base amount used for percentage calculations', max_digits=10, null=True)),
                ('description', models.TextField(blank=True, help_text='Additional details about this bonus')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bonus_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payslip_bonuses', to='payroll.bonustype')),
                ('payslip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonuses', to='payroll.payslip')),
                ('performance_review', models.ForeignKey(blank=True, help_text='Performance review that triggered this bonus', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linked_bonuses', to='employees.performancereview')),
            ],
            options={
                'ordering': ['payslip', 'bonus_type'],
            },
        ),
        migrations.CreateModel(
            name='PayslipDeduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('calculation_base', models.DecimalField(blank=True, decimal_places=2, help_text='Base amount used for percentage calculations', max_digits=10, null=True)),
                ('description', models.TextField(blank=True, help_text='Additional details about this deduction')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deduction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payslip_deductions', to='payroll.deductiontype')),
                ('payslip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='payroll.payslip')),
            ],
            options={
                'ordering': ['payslip', 'deduction_type'],
            },
        ),
    ]
