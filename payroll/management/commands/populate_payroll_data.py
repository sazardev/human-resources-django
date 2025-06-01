from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from payroll.models import (
    PayrollConfiguration, PayrollPeriod, TaxBracket, DeductionType, 
    BonusType, Payslip, PayslipDeduction, PayslipBonus, CompensationHistory
)
from employees.models import Employee

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate payroll system with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-data',
            action='store_true',
            help='Clear existing payroll data before populating',
        )

    def handle(self, *args, **options):
        if options['clear_data']:
            self.stdout.write('Clearing existing payroll data...')
            PayrollConfiguration.objects.all().delete()
            PayrollPeriod.objects.all().delete()
            TaxBracket.objects.all().delete()
            DeductionType.objects.all().delete()
            BonusType.objects.all().delete()
            Payslip.objects.all().delete()
            CompensationHistory.objects.all().delete()

        self.stdout.write('Creating payroll configuration...')
        config = PayrollConfiguration.objects.get_or_create(
            defaults={
                'working_days_per_month': 22,
                'working_hours_per_day': 8,
                'overtime_threshold_hours': 40,
                'default_overtime_rate': Decimal('1.5'),
                'default_country': 'Mexico',
                'tax_year': timezone.now().year,
                'integrate_with_leave_management': True,
                'payslip_number_prefix': 'PAY',
                'require_payroll_approval': True,
            }
        )[0]

        self.stdout.write('Creating tax brackets for Mexico...')
        tax_brackets = [
            {
                'name': 'Mexico Income Tax Bracket 1',
                'country': 'Mexico',
                'year': timezone.now().year,
                'min_amount': Decimal('0'),
                'max_amount': Decimal('5000'),
                'tax_rate': Decimal('0.05'),
                'fixed_amount': Decimal('0'),
            },
            {
                'name': 'Mexico Income Tax Bracket 2',
                'country': 'Mexico',
                'year': timezone.now().year,
                'min_amount': Decimal('5000.01'),
                'max_amount': Decimal('15000'),
                'tax_rate': Decimal('0.10'),
                'fixed_amount': Decimal('250'),
            },
            {
                'name': 'Mexico Income Tax Bracket 3',
                'country': 'Mexico',
                'year': timezone.now().year,
                'min_amount': Decimal('15000.01'),
                'max_amount': Decimal('30000'),
                'tax_rate': Decimal('0.15'),
                'fixed_amount': Decimal('1250'),
            },
            {
                'name': 'Mexico Income Tax Bracket 4',
                'country': 'Mexico',
                'year': timezone.now().year,
                'min_amount': Decimal('30000.01'),
                'max_amount': None,
                'tax_rate': Decimal('0.25'),
                'fixed_amount': Decimal('3500'),
            },
        ]

        for bracket_data in tax_brackets:
            TaxBracket.objects.get_or_create(
                name=bracket_data['name'],
                defaults=bracket_data
            )

        self.stdout.write('Creating deduction types...')
        deduction_types = [
            {
                'name': 'Social Security (IMSS)',
                'description': 'Mexican Social Security deduction',
                'calculation_method': 'percentage',
                'default_amount': Decimal('0.0325'),  # 3.25%
                'is_mandatory': True,
                'is_pre_tax': True,
            },
            {
                'name': 'Retirement Fund (AFORE)',
                'description': 'Retirement fund contribution',
                'calculation_method': 'percentage',
                'default_amount': Decimal('0.0625'),  # 6.25%
                'is_mandatory': True,
                'is_pre_tax': True,
            },
            {
                'name': 'Health Insurance',
                'description': 'Company health insurance plan',
                'calculation_method': 'fixed',
                'default_amount': Decimal('500'),
                'is_mandatory': False,
                'is_pre_tax': True,
            },
            {
                'name': 'Meal Vouchers',
                'description': 'Employee meal voucher program',
                'calculation_method': 'fixed',
                'default_amount': Decimal('300'),
                'is_mandatory': False,
                'is_pre_tax': True,
            },
        ]

        for deduction_data in deduction_types:
            DeductionType.objects.get_or_create(
                name=deduction_data['name'],
                defaults=deduction_data
            )

        self.stdout.write('Creating bonus types...')
        bonus_types = [
            {
                'name': 'Performance Bonus',
                'description': 'Quarterly performance-based bonus',
                'calculation_method': 'performance',
                'default_amount': Decimal('0.15'),  # 15% of salary
                'is_taxable': True,
            },
            {
                'name': 'Christmas Bonus (Aguinaldo)',
                'description': 'Annual Christmas bonus - 15 days salary',
                'calculation_method': 'fixed',
                'default_amount': Decimal('15'),  # 15 days
                'is_taxable': True,
            },
            {
                'name': 'Productivity Bonus',
                'description': 'Monthly productivity bonus',
                'calculation_method': 'percentage',
                'default_amount': Decimal('0.05'),  # 5% of salary
                'is_taxable': True,
            },
            {
                'name': 'Project Completion Bonus',
                'description': 'One-time project completion bonus',
                'calculation_method': 'fixed',
                'default_amount': Decimal('2000'),
                'is_taxable': True,
            },
        ]

        for bonus_data in bonus_types:
            BonusType.objects.get_or_create(
                name=bonus_data['name'],
                defaults=bonus_data
            )

        self.stdout.write('Creating payroll periods...')
        # Create current month and previous month payroll periods
        current_date = date.today()
        current_month_start = current_date.replace(day=1)
        current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        previous_month_end = current_month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)

        periods = [
            {
                'name': f"{previous_month_start.strftime('%B %Y')} Payroll",
                'start_date': previous_month_start,
                'end_date': previous_month_end,
                'pay_date': previous_month_end + timedelta(days=5),
                'frequency': 'monthly',
                'status': 'processed',
            },
            {
                'name': f"{current_month_start.strftime('%B %Y')} Payroll",
                'start_date': current_month_start,
                'end_date': current_month_end,
                'pay_date': current_month_end + timedelta(days=5),
                'frequency': 'monthly',
                'status': 'draft',
            },
        ]

        for period_data in periods:
            PayrollPeriod.objects.get_or_create(
                name=period_data['name'],
                defaults=period_data
            )

        # Create sample payslips for employees
        self.stdout.write('Creating sample payslips...')
        employees = Employee.objects.filter(employment_status='active')[:5]  # Limit to 5 employees
        previous_period = PayrollPeriod.objects.filter(status='processed').first()
        
        if previous_period and employees.exists():
            for i, employee in enumerate(employees):
                # Create payslip
                payslip_number = f"PAY{timezone.now().year}{previous_period.start_date.month:02d}{i+1:04d}"
                
                payslip, created = Payslip.objects.get_or_create(
                    employee=employee,
                    payroll_period=previous_period,
                    defaults={
                        'payslip_number': payslip_number,
                        'status': 'paid',
                        'base_salary': employee.salary or Decimal('25000'),
                        'hours_worked': Decimal('176'),  # 22 days * 8 hours
                        'overtime_hours': Decimal('8'),
                        'overtime_rate': Decimal('1.5'),
                        'unpaid_leave_days': Decimal('0'),
                        'gross_salary': employee.salary or Decimal('25000'),
                        'total_bonuses': Decimal('1250'),  # 5% productivity bonus
                        'total_deductions': Decimal('2437.50'),  # IMSS + AFORE + Health
                        'tax_amount': Decimal('1250'),  # Simplified tax
                        'net_salary': Decimal('22562.50'),
                        'payment_method': 'bank_transfer',
                        'payment_date': previous_period.pay_date,
                    }
                )

                if created:                    # Add mandatory deductions
                    imss = DeductionType.objects.get(name='Social Security (IMSS)')
                    afore = DeductionType.objects.get(name='Retirement Fund (AFORE)')
                    health = DeductionType.objects.get(name='Health Insurance')

                    PayslipDeduction.objects.create(
                        payslip=payslip,
                        deduction_type=imss,
                        amount=payslip.base_salary * imss.default_amount,
                        calculation_base=payslip.base_salary,
                    )

                    PayslipDeduction.objects.create(
                        payslip=payslip,
                        deduction_type=afore,
                        amount=payslip.base_salary * afore.default_amount,
                        calculation_base=payslip.base_salary,
                    )

                    PayslipDeduction.objects.create(
                        payslip=payslip,
                        deduction_type=health,
                        amount=health.default_amount,
                        calculation_base=health.default_amount,
                    )                    # Add productivity bonus
                    productivity_bonus = BonusType.objects.get(name='Productivity Bonus')
                    PayslipBonus.objects.create(
                        payslip=payslip,
                        bonus_type=productivity_bonus,
                        amount=payslip.base_salary * productivity_bonus.default_amount,
                        calculation_base=payslip.base_salary,
                    )

                    self.stdout.write(f'  Created payslip for {employee.full_name}')

        # Create compensation history records
        self.stdout.write('Creating compensation history...')
        if employees.exists():
            sample_employee = employees.first()
            
            # Initial hire record
            CompensationHistory.objects.get_or_create(
                employee=sample_employee,
                change_type='hire',
                effective_date=sample_employee.hire_date,
                defaults={
                    'previous_salary': None,
                    'new_salary': sample_employee.salary or Decimal('20000'),
                    'reason': 'Initial hire',
                    'currency': 'MXN',
                }
            )

            # Promotion record
            if sample_employee.salary:
                promotion_date = sample_employee.hire_date + timedelta(days=365)
                if promotion_date <= date.today():
                    CompensationHistory.objects.get_or_create(
                        employee=sample_employee,
                        change_type='promotion',
                        effective_date=promotion_date,
                        defaults={
                            'previous_salary': Decimal('20000'),
                            'new_salary': sample_employee.salary,
                            'reason': 'Annual performance promotion',
                            'currency': 'MXN',
                        }
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated payroll system with sample data!')
        )
        
        # Print summary
        self.stdout.write('\n--- Payroll System Summary ---')
        self.stdout.write(f'Payroll Periods: {PayrollPeriod.objects.count()}')
        self.stdout.write(f'Tax Brackets: {TaxBracket.objects.count()}')
        self.stdout.write(f'Deduction Types: {DeductionType.objects.count()}')
        self.stdout.write(f'Bonus Types: {BonusType.objects.count()}')
        self.stdout.write(f'Payslips: {Payslip.objects.count()}')
        self.stdout.write(f'Compensation History: {CompensationHistory.objects.count()}')
        self.stdout.write('\nAccess the admin interface at: http://127.0.0.1:8000/admin/')
        self.stdout.write('Payroll API endpoints at: http://127.0.0.1:8000/api/payroll/')
