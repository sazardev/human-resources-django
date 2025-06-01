from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Avg, Count, Q
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime
import logging

from .models import (
    PayrollPeriod, TaxBracket, DeductionType, BonusType,
    Payslip, PayslipDeduction, PayslipBonus, CompensationHistory,
    PayrollConfiguration
)
from .serializers import (
    PayrollPeriodSerializer, TaxBracketSerializer, DeductionTypeSerializer,
    BonusTypeSerializer, PayslipSerializer, PayslipSummarySerializer,
    PayslipDeductionSerializer, PayslipBonusSerializer, CompensationHistorySerializer,
    PayrollConfigurationSerializer, EmployeePayrollSerializer, PayrollReportSerializer,
    PayslipCalculationSerializer
)
from employees.models import Employee, PerformanceReview
from leaves.models import LeaveRequest

logger = logging.getLogger(__name__)


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payroll periods"""
    
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'frequency', 'year']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'pay_date', 'created_at']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(start_date__year=year)
        
        # Filter by month
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(start_date__month=month)
        
        return queryset

    @action(detail=True, methods=['post'])
    def process_payroll(self, request, pk=None):
        """Process payroll for this period"""
        payroll_period = self.get_object()
        
        if payroll_period.status != 'draft':
            return Response(
                {'error': 'Only draft payroll periods can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Update status
                payroll_period.status = 'processing'
                payroll_period.processed_by = request.user
                payroll_period.processed_date = timezone.now()
                payroll_period.save()
                
                # Generate payslips for all active employees
                active_employees = Employee.objects.filter(employment_status='active')
                created_count = 0
                
                for employee in active_employees:
                    # Check if payslip already exists
                    if not Payslip.objects.filter(
                        employee=employee, 
                        payroll_period=payroll_period
                    ).exists():
                        # Create payslip
                        payslip_number = self._generate_payslip_number(
                            payroll_period, employee
                        )
                        
                        Payslip.objects.create(
                            employee=employee,
                            payroll_period=payroll_period,
                            payslip_number=payslip_number,
                            base_salary=employee.salary or Decimal('0'),
                            status='draft'
                        )
                        created_count += 1
                
                # Update status to processed
                payroll_period.status = 'processed'
                payroll_period.save()
                
                return Response({
                    'message': f'Payroll processed successfully. Created {created_count} payslips.',
                    'payslips_created': created_count
                })
                
        except Exception as e:
            logger.error(f"Error processing payroll: {str(e)}")
            return Response(
                {'error': f'Error processing payroll: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def finalize_payroll(self, request, pk=None):
        """Finalize payroll period (lock from further changes)"""
        payroll_period = self.get_object()
        
        if payroll_period.status != 'processed':
            return Response(
                {'error': 'Only processed payroll periods can be finalized'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check that all payslips are approved
        pending_payslips = payroll_period.payslips.exclude(status='approved')
        if pending_payslips.exists():
            return Response(
                {'error': f'{pending_payslips.count()} payslips are not approved yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payroll_period.status = 'finalized'
        payroll_period.save()
        
        return Response({'message': 'Payroll period finalized successfully'})

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get payroll period summary"""
        payroll_period = self.get_object()
        
        payslips = payroll_period.payslips.all()
        
        summary = {
            'period_name': payroll_period.name,
            'total_employees': payslips.count(),
            'total_gross_amount': payslips.aggregate(
                total=Sum('gross_salary')
            )['total'] or Decimal('0'),
            'total_net_amount': payslips.aggregate(
                total=Sum('net_salary')
            )['total'] or Decimal('0'),
            'total_deductions': payslips.aggregate(
                total=Sum('total_deductions')
            )['total'] or Decimal('0'),
            'total_taxes': payslips.aggregate(
                total=Sum('tax_amount')
            )['total'] or Decimal('0'),
            'total_bonuses': payslips.aggregate(
                total=Sum('total_bonuses')
            )['total'] or Decimal('0'),
            'average_salary': payslips.aggregate(
                avg=Avg('gross_salary')
            )['avg'] or Decimal('0'),
            'status_breakdown': list(
                payslips.values('status').annotate(count=Count('status'))
            ),
            'department_breakdown': list(
                payslips.values('employee__department__name')
                .annotate(
                    count=Count('employee'),
                    total_gross=Sum('gross_salary'),
                    total_net=Sum('net_salary')
                )
            )
        }
        
        serializer = PayrollReportSerializer(summary)
        return Response(serializer.data)

    def _generate_payslip_number(self, payroll_period, employee):
        """Generate unique payslip number"""
        config = PayrollConfiguration.objects.first()
        if not config:
            prefix = 'PAY'
            format_str = '{prefix}{year}{month:02d}{sequence:04d}'
        else:
            prefix = config.payslip_number_prefix
            format_str = config.payslip_number_format
        
        # Get sequence number
        existing_count = Payslip.objects.filter(
            payroll_period=payroll_period
        ).count()
        
        return format_str.format(
            prefix=prefix,
            year=payroll_period.start_date.year,
            month=payroll_period.start_date.month,
            sequence=existing_count + 1,
            employee_id=employee.employee_id
        )


class TaxBracketViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tax brackets"""
    
    queryset = TaxBracket.objects.all()
    serializer_class = TaxBracketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['country', 'year', 'is_active']
    search_fields = ['name', 'country']
    ordering_fields = ['country', 'year', 'min_amount']
    ordering = ['country', 'year', 'min_amount']

    @action(detail=False, methods=['post'])
    def calculate_tax(self, request):
        """Calculate tax for a given amount"""
        amount = request.data.get('amount')
        country = request.data.get('country', 'Mexico')
        year = request.data.get('year', timezone.now().year)
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount))
        except:
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get applicable tax brackets
        brackets = TaxBracket.objects.filter(
            country=country,
            year=year,
            is_active=True
        ).order_by('min_amount')
        
        total_tax = Decimal('0')
        tax_breakdown = []
        
        for bracket in brackets:
            if amount <= bracket.min_amount:
                break
            
            # Calculate taxable amount in this bracket
            bracket_max = bracket.max_amount or amount
            taxable_in_bracket = min(amount, bracket_max) - bracket.min_amount
            
            if taxable_in_bracket > 0:
                bracket_tax = (taxable_in_bracket * bracket.tax_rate) + bracket.fixed_amount
                total_tax += bracket_tax
                
                tax_breakdown.append({
                    'bracket': str(bracket),
                    'taxable_amount': taxable_in_bracket,
                    'tax_rate': bracket.tax_rate,
                    'tax_amount': bracket_tax
                })
        
        return Response({
            'gross_amount': amount,
            'total_tax': total_tax,
            'net_amount': amount - total_tax,
            'effective_tax_rate': total_tax / amount if amount > 0 else 0,
            'tax_breakdown': tax_breakdown
        })


class DeductionTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing deduction types"""
    
    queryset = DeductionType.objects.all()
    serializer_class = DeductionTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['calculation_method', 'is_mandatory', 'is_pre_tax', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def mandatory(self, request):
        """Get all mandatory deductions"""
        mandatory_deductions = self.get_queryset().filter(is_mandatory=True, is_active=True)
        serializer = self.get_serializer(mandatory_deductions, many=True)
        return Response(serializer.data)


class BonusTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bonus types"""
    
    queryset = BonusType.objects.all()
    serializer_class = BonusTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['calculation_method', 'is_taxable', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class PayslipViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payslips"""
    
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'employee__department']
    search_fields = ['payslip_number', 'employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['payslip_number', 'created_at', 'net_salary', 'payment_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter queryset based on user permissions and query parameters"""
        queryset = super().get_queryset()
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee__id=employee_id)
        
        # Filter by payroll period
        period_id = self.request.query_params.get('payroll_period_id')
        if period_id:
            queryset = queryset.filter(payroll_period__id=period_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(payroll_period__start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payroll_period__end_date__lte=end_date)
        
        return queryset

    def get_serializer_class(self):
        """Use summary serializer for list view"""
        if self.action == 'list':
            return PayslipSummarySerializer
        return PayslipSerializer

    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate payslip amounts"""
        payslip = self.get_object()
        
        if payslip.status not in ['draft', 'calculated']:
            return Response(
                {'error': 'Only draft or calculated payslips can be recalculated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Calculate gross salary
                gross_salary = payslip.calculate_gross_salary()
                
                # Calculate leave deductions if integration is enabled
                config = PayrollConfiguration.objects.first()
                if config and config.integrate_with_leave_management:
                    unpaid_leave = self._calculate_unpaid_leave(payslip)
                    payslip.unpaid_leave_days = unpaid_leave
                
                # Apply mandatory deductions
                self._apply_mandatory_deductions(payslip)
                
                # Calculate taxes
                tax_amount = self._calculate_taxes(payslip, gross_salary)
                
                # Update payslip
                payslip.gross_salary = gross_salary
                payslip.tax_amount = tax_amount
                payslip.net_salary = payslip.calculate_net_salary()
                payslip.status = 'calculated'
                payslip.save()
                
                return Response({
                    'message': 'Payslip calculated successfully',
                    'payslip': PayslipSerializer(payslip).data
                })
                
        except Exception as e:
            logger.error(f"Error calculating payslip: {str(e)}")
            return Response(
                {'error': f'Error calculating payslip: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve payslip"""
        payslip = self.get_object()
        
        if payslip.status != 'calculated':
            return Response(
                {'error': 'Only calculated payslips can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payslip.status = 'approved'
        payslip.approved_by = request.user
        payslip.approved_date = timezone.now()
        payslip.save()
        
        return Response({'message': 'Payslip approved successfully'})

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payslip as paid"""
        payslip = self.get_object()
        
        if payslip.status != 'approved':
            return Response(
                {'error': 'Only approved payslips can be marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_reference = request.data.get('payment_reference', '')
        payment_date = request.data.get('payment_date', date.today())
        
        payslip.status = 'paid'
        payslip.payment_reference = payment_reference
        payslip.payment_date = payment_date
        payslip.save()
        
        return Response({'message': 'Payslip marked as paid successfully'})

    @action(detail=True, methods=['post'])
    def add_bonus(self, request, pk=None):
        """Add bonus to payslip"""
        payslip = self.get_object()
        
        if payslip.status not in ['draft', 'calculated']:
            return Response(
                {'error': 'Cannot add bonus to approved/paid payslips'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PayslipBonusSerializer(data=request.data)
        if serializer.is_valid():
            bonus = serializer.save(payslip=payslip)
            
            # Update payslip total bonuses
            payslip.total_bonuses = payslip.bonuses.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            payslip.save()
            
            return Response(PayslipBonusSerializer(bonus).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_deduction(self, request, pk=None):
        """Add deduction to payslip"""
        payslip = self.get_object()
        
        if payslip.status not in ['draft', 'calculated']:
            return Response(
                {'error': 'Cannot add deduction to approved/paid payslips'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PayslipDeductionSerializer(data=request.data)
        if serializer.is_valid():
            deduction = serializer.save(payslip=payslip)
            
            # Update payslip total deductions
            payslip.total_deductions = payslip.deductions.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            payslip.save()
            
            return Response(PayslipDeductionSerializer(deduction).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _calculate_unpaid_leave(self, payslip):
        """Calculate unpaid leave days for the payroll period"""
        # Get approved leave requests for the period that are unpaid
        leave_requests = LeaveRequest.objects.filter(
            employee=payslip.employee,
            status='approved',
            leave_type__is_paid=False,
            start_date__lte=payslip.payroll_period.end_date,
            end_date__gte=payslip.payroll_period.start_date
        )
        
        total_unpaid_days = Decimal('0')
        for leave in leave_requests:
            # Calculate overlap with payroll period
            overlap_start = max(leave.start_date, payslip.payroll_period.start_date)
            overlap_end = min(leave.end_date, payslip.payroll_period.end_date)
            
            if overlap_start <= overlap_end:
                overlap_days = (overlap_end - overlap_start).days + 1
                total_unpaid_days += Decimal(str(overlap_days))
        
        return total_unpaid_days

    def _apply_mandatory_deductions(self, payslip):
        """Apply mandatory deductions to payslip"""
        mandatory_deductions = DeductionType.objects.filter(
            is_mandatory=True, is_active=True
        )
        
        for deduction_type in mandatory_deductions:
            # Check if deduction already exists
            if not PayslipDeduction.objects.filter(
                payslip=payslip, deduction_type=deduction_type
            ).exists():
                
                # Calculate amount based on method
                if deduction_type.calculation_method == 'fixed':
                    amount = deduction_type.default_amount
                elif deduction_type.calculation_method == 'percentage':
                    amount = payslip.base_salary * deduction_type.default_amount
                else:
                    amount = Decimal('0')  # Tax calculations handled separately
                
                PayslipDeduction.objects.create(
                    payslip=payslip,
                    deduction_type=deduction_type,
                    amount=amount,
                    calculation_base=payslip.base_salary
                )
        
        # Update total deductions
        payslip.total_deductions = payslip.deductions.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

    def _calculate_taxes(self, payslip, gross_salary):
        """Calculate tax amount for payslip"""
        config = PayrollConfiguration.objects.first()
        country = config.default_country if config else 'Mexico'
        year = config.tax_year if config else timezone.now().year
        
        # Get applicable tax brackets
        brackets = TaxBracket.objects.filter(
            country=country,
            year=year,
            is_active=True
        ).order_by('min_amount')
        
        total_tax = Decimal('0')
        
        for bracket in brackets:
            if gross_salary <= bracket.min_amount:
                break
            
            # Calculate taxable amount in this bracket
            bracket_max = bracket.max_amount or gross_salary
            taxable_in_bracket = min(gross_salary, bracket_max) - bracket.min_amount
            
            if taxable_in_bracket > 0:
                bracket_tax = (taxable_in_bracket * bracket.tax_rate) + bracket.fixed_amount
                total_tax += bracket_tax
        
        return total_tax


class CompensationHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing compensation history"""
    
    queryset = CompensationHistory.objects.all()
    serializer_class = CompensationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['change_type', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason']
    ordering_fields = ['effective_date', 'new_salary', 'created_at']
    ordering = ['-effective_date']

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee__id=employee_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(effective_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(effective_date__lte=end_date)
        
        return queryset

    def perform_create(self, serializer):
        """Auto-update employee salary when creating compensation history"""
        compensation = serializer.save()
        
        # Update employee's current salary
        employee = compensation.employee
        employee.salary = compensation.new_salary
        employee.save()

    @action(detail=False, methods=['get'])
    def salary_trends(self, request):
        """Get salary trends analysis"""
        # Get salary changes by type
        trends = CompensationHistory.objects.values('change_type').annotate(
            count=Count('id'),
            avg_change=Avg('new_salary') - Avg('previous_salary'),
            total_amount=Sum('new_salary') - Sum('previous_salary')
        )
        
        return Response(list(trends))


class PayrollConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payroll configuration"""
    
    queryset = PayrollConfiguration.objects.all()
    serializer_class = PayrollConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current configuration (create default if none exists)"""
        config = PayrollConfiguration.objects.first()
        if not config:
            config = PayrollConfiguration.objects.create()
        
        serializer = self.get_serializer(config)
        return Response(serializer.data)


class PayrollAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for payroll analytics and reports"""
    
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get payroll dashboard data"""
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        # Current month stats
        current_period = PayrollPeriod.objects.filter(
            start_date__year=current_year,
            start_date__month=current_month
        ).first()
        
        # Overall stats
        total_employees = Employee.objects.filter(employment_status='active').count()
        total_payslips = Payslip.objects.count()
        
        # Recent payslips
        recent_payslips = Payslip.objects.select_related(
            'employee', 'payroll_period'
        ).order_by('-created_at')[:10]
        
        # Salary distribution
        salary_stats = Employee.objects.filter(
            employment_status='active'
        ).aggregate(
            min_salary=Min('salary'),
            max_salary=Max('salary'),
            avg_salary=Avg('salary'),
            total_payroll=Sum('salary')
        )
        
        return Response({
            'current_period': PayrollPeriodSerializer(current_period).data if current_period else None,
            'total_employees': total_employees,
            'total_payslips': total_payslips,
            'recent_payslips': PayslipSummarySerializer(recent_payslips, many=True).data,
            'salary_stats': salary_stats
        })

    @action(detail=False, methods=['get'])
    def payroll_summary(self, request):
        """Get payroll summary by period"""
        period_id = request.query_params.get('period_id')
        if not period_id:
            return Response(
                {'error': 'period_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            period = PayrollPeriod.objects.get(id=period_id)
        except PayrollPeriod.DoesNotExist:
            return Response(
                {'error': 'Payroll period not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get summary data
        payslips = period.payslips.all()
        
        summary = {
            'period': PayrollPeriodSerializer(period).data,
            'total_employees': payslips.count(),
            'total_gross': payslips.aggregate(Sum('gross_salary'))['gross_salary__sum'] or 0,
            'total_net': payslips.aggregate(Sum('net_salary'))['net_salary__sum'] or 0,
            'total_deductions': payslips.aggregate(Sum('total_deductions'))['total_deductions__sum'] or 0,
            'total_taxes': payslips.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0,
            'status_breakdown': list(
                payslips.values('status').annotate(count=Count('status'))
            ),
            'department_breakdown': list(
                payslips.values('employee__department__name')
                .annotate(
                    count=Count('employee'),
                    gross_total=Sum('gross_salary'),
                    net_total=Sum('net_salary')
                )
            )
        }
        
        return Response(summary)
