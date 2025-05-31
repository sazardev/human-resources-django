from rest_framework import viewsets, status, filters, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Sum, Count, Prefetch
from datetime import date, timedelta, datetime
from decimal import Decimal

from .models import (
    LeaveType, 
    Holiday, 
    LeaveBalance, 
    LeaveRequest, 
    LeaveRequestComment, 
    TeamSchedule, 
    LeavePolicy
)
from .serializers import (
    LeaveTypeSerializer,
    HolidaySerializer,
    LeaveBalanceSerializer,
    LeaveRequestSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestCommentSerializer,
    TeamScheduleSerializer,
    LeavePolicySerializer,
    LeaveCalendarSerializer,
    LeaveSummarySerializer,
    LeaveApprovalSerializer
)
from employees.mixins import OptimizedQueryMixin
from employees.models import Employee


class LeaveTypeViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing leave types with optimized queries and dynamic field selection
    """
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'requires_approval', 'is_paid', 'carry_over_type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'default_days_per_year', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active leave types"""
        active_types = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_types, many=True)
        return Response(serializer.data)


class HolidayViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing holidays with optimized queries and dynamic field selection
    """
    queryset = Holiday.objects.select_related().prefetch_related('departments')
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['holiday_type', 'is_mandatory', 'affects_leave_calculation']
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'name', 'created_at']
    ordering = ['date']

    @action(detail=False, methods=['get'])
    def current_year(self, request):
        """Get holidays for current year"""
        current_year = timezone.now().year
        holidays = self.queryset.filter(date__year=current_year)
        serializer = self.get_serializer(holidays, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming holidays in next 90 days"""
        today = timezone.now().date()
        future_date = today + timedelta(days=90)
        holidays = self.queryset.filter(date__range=[today, future_date])
        serializer = self.get_serializer(holidays, many=True)
        return Response(serializer.data)


class LeaveBalanceViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing leave balances with optimized queries and dynamic field selection
    """
    queryset = LeaveBalance.objects.select_related('employee', 'leave_type')
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'leave_type', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['year', 'employee', 'available_days', 'created_at']
    ordering = ['-year', 'employee']

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # If user is not superuser or HR, show only their own balances
        if not (user.is_superuser or hasattr(user, 'employee_profile')):
            return queryset.none()
        
        if not user.is_superuser:
            # Regular employees can only see their own balances
            if hasattr(user, 'employee_profile'):
                queryset = queryset.filter(employee=user.employee_profile)
        
        return queryset

    @action(detail=False, methods=['get'])
    def my_balances(self, request):
        """Get current user's leave balances"""
        if not hasattr(request.user, 'employee_profile'):
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        current_year = timezone.now().year
        balances = self.queryset.filter(
            employee=request.user.employee_profile,
            year=current_year
        )
        serializer = self.get_serializer(balances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_balance(self, request):
        """Get employees with low leave balances"""
        threshold = Decimal(request.query_params.get('threshold', '5'))
        low_balances = self.queryset.filter(
            available_days__lte=threshold,
            year=timezone.now().year
        )
        serializer = self.get_serializer(low_balances, many=True)
        return Response(serializer.data)


class LeaveRequestViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing leave requests with optimized queries and dynamic field selection
    """
    queryset = LeaveRequest.objects.select_related(
        'employee', 'leave_type', 'approved_by'
    ).prefetch_related(
        Prefetch('comments', queryset=LeaveRequestComment.objects.select_related('commented_by'))
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'leave_type', 'employee__department', 'duration_type']
    search_fields = ['request_id', 'employee__first_name', 'employee__last_name', 'reason']
    ordering_fields = ['start_date', 'submitted_at', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # If user is not authenticated or has no employee profile
        if not hasattr(user, 'employee_profile'):
            return queryset.none()
        
        # Superuser can see all requests
        if user.is_superuser:
            return queryset
        
        # Regular employees can see their own requests and requests they need to approve
        employee = user.employee_profile
        return queryset.filter(
            Q(employee=employee) |  # Own requests
            Q(employee__department=employee.department)  # Department requests for approval
        )

    def perform_create(self, serializer):
        """Set employee to current user when creating request"""
        if hasattr(self.request.user, 'employee_profile'):
            serializer.save(employee=self.request.user.employee_profile)
        else:
            raise serializers.ValidationError("Employee profile not found")

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's leave requests"""
        if not hasattr(request.user, 'employee_profile'):
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        requests = self.queryset.filter(employee=request.user.employee_profile)
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get requests pending approval for manager"""
        if not hasattr(request.user, 'employee_profile'):
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Get requests from same department with pending status
        employee = request.user.employee_profile
        pending_requests = self.queryset.filter(
            employee__department=employee.department,
            status='pending'
        ).exclude(employee=employee)
        
        page = self.paginate_queryset(pending_requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request"""
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LeaveApprovalSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            comment = serializer.validated_data.get('comment', '')
            
            if action == 'approve':
                leave_request.status = 'approved'
                leave_request.approved_by = request.user.employee_profile
                leave_request.approved_at = timezone.now()
            else:
                leave_request.status = 'rejected'
                leave_request.rejection_reason = comment
            
            leave_request.save()
            
            # Add comment if provided
            if comment:
                LeaveRequestComment.objects.create(
                    leave_request=leave_request,
                    commented_by=request.user.employee_profile,
                    comment=comment,
                    is_internal=True
                )
            
            return Response({
                'message': f'Leave request {action}d successfully',
                'status': leave_request.status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a leave request"""
        leave_request = self.get_object()
        
        # Check if user can cancel this request
        if leave_request.employee != request.user.employee_profile:
            return Response(
                {'error': 'You can only cancel your own requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not leave_request.can_be_cancelled:
            return Response(
                {'error': 'This request cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'cancelled'
        leave_request.save()
        
        return Response({'message': 'Leave request cancelled successfully'})

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get leave calendar data for a specific month/year"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        # Get first and last day of month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get leave requests for the month
        requests = self.queryset.filter(
            start_date__lte=last_day,
            end_date__gte=first_day,
            status='approved'
        )
        
        # Get holidays for the month
        holidays = Holiday.objects.filter(
            date__range=[first_day, last_day]
        )
        
        calendar_data = []
        current_date = first_day
        
        while current_date <= last_day:
            day_requests = requests.filter(
                start_date__lte=current_date,
                end_date__gte=current_date
            )
            day_holidays = holidays.filter(date=current_date)
            
            calendar_data.append({
                'date': current_date,
                'leave_requests': LeaveRequestSerializer(day_requests, many=True).data,
                'holidays': HolidaySerializer(day_holidays, many=True).data,
                'is_weekend': current_date.weekday() >= 5,
                'employees_on_leave_count': day_requests.count()
            })
            
            current_date += timedelta(days=1)
        
        return Response(calendar_data)


class LeaveRequestCommentViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing leave request comments
    """
    queryset = LeaveRequestComment.objects.select_related('leave_request', 'commented_by')
    serializer_class = LeaveRequestCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_internal', 'leave_request']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not hasattr(user, 'employee_profile'):
            return queryset.none()
        
        # Show comments for requests user has access to
        employee = user.employee_profile
        return queryset.filter(
            Q(leave_request__employee=employee) |  # Own request comments
            Q(leave_request__employee__department=employee.department)  # Department comments
        )

    def perform_create(self, serializer):
        """Set commented_by to current user"""
        if hasattr(self.request.user, 'employee_profile'):
            serializer.save(commented_by=self.request.user.employee_profile)


class TeamScheduleViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing team schedules and leave conflicts
    """
    queryset = TeamSchedule.objects.select_related('department').prefetch_related('employees_on_leave')
    serializer_class = TeamScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['department', 'is_critical']
    ordering = ['date', 'department']

    @action(detail=False, methods=['get'])
    def critical_dates(self, request):
        """Get dates with critical leave coverage"""
        critical_schedules = self.queryset.filter(is_critical=True)
        serializer = self.get_serializer(critical_schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def department_schedule(self, request):
        """Get schedule for specific department"""
        department_id = request.query_params.get('department')
        if not department_id:
            return Response(
                {'error': 'Department ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        schedules = self.queryset.filter(department_id=department_id)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)


class LeavePolicyViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing leave policies
    """
    queryset = LeavePolicy.objects.select_related('department')
    serializer_class = LeavePolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'department', 'probation_leave_allowed']
    search_fields = ['name', 'description']
    ordering = ['-effective_from']

    @action(detail=False, methods=['get'])
    def active_policies(self, request):
        """Get currently active policies"""
        today = timezone.now().date()
        active_policies = self.queryset.filter(
            is_active=True,
            effective_from__lte=today
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=today)
        )
        serializer = self.get_serializer(active_policies, many=True)
        return Response(serializer.data)


class LeaveAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for leave analytics and reporting
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get leave dashboard data"""
        if not hasattr(request.user, 'employee_profile'):
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        employee = request.user.employee_profile
        current_year = timezone.now().year
        
        # Get user's leave balances
        balances = LeaveBalance.objects.filter(
            employee=employee,
            year=current_year
        ).select_related('leave_type')
        
        # Get pending requests
        pending_requests = LeaveRequest.objects.filter(
            employee=employee,
            status='pending'
        ).select_related('leave_type')
        
        # Get recent requests (last 3 months)
        three_months_ago = timezone.now() - timedelta(days=90)
        recent_requests = LeaveRequest.objects.filter(
            employee=employee,
            created_at__gte=three_months_ago
        ).select_related('leave_type')[:10]
        
        # Calculate totals
        total_pending_days = pending_requests.aggregate(
            total=Sum('total_days')
        )['total'] or Decimal('0')
        
        total_used_this_year = LeaveRequest.objects.filter(
            employee=employee,
            status='approved',
            start_date__year=current_year
        ).aggregate(total=Sum('total_days'))['total'] or Decimal('0')
        
        summary_data = {
            'employee': employee,
            'leave_balances': balances,
            'pending_requests': pending_requests,
            'recent_requests': recent_requests,
            'total_pending_days': total_pending_days,
            'total_used_days_this_year': total_used_this_year
        }
        
        serializer = LeaveSummarySerializer(summary_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def department_summary(self, request):
        """Get department leave summary"""
        if not hasattr(request.user, 'employee_profile'):
            return Response({'error': 'Employee profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        department = request.user.employee_profile.department
        if not department:
            return Response({'error': 'No department assigned'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        current_year = timezone.now().year
        
        # Department statistics
        dept_employees = Employee.objects.filter(department=department)
        total_employees = dept_employees.count()
        
        # Leave requests summary
        dept_requests = LeaveRequest.objects.filter(
            employee__department=department,
            start_date__year=current_year
        )
        
        pending_count = dept_requests.filter(status='pending').count()
        approved_count = dept_requests.filter(status='approved').count()
        rejected_count = dept_requests.filter(status='rejected').count()
        
        # Total leave days used
        total_days_used = dept_requests.filter(
            status='approved'
        ).aggregate(total=Sum('total_days'))['total'] or Decimal('0')
        
        return Response({
            'department': department.name,
            'total_employees': total_employees,
            'requests_summary': {
                'pending': pending_count,
                'approved': approved_count,
                'rejected': rejected_count,
                'total': dept_requests.count()
            },
            'total_days_used': total_days_used,
            'average_days_per_employee': total_days_used / total_employees if total_employees > 0 else 0
        })
