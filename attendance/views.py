"""
Attendance app views for time tracking and management.
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Sum, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from employees.mixins import DynamicFieldsMixin
from employees.models import Employee
from .models import (
    WorkSchedule, TimeEntry, Timesheet, 
    AttendanceReport, OvertimeRequest
)
from .serializers import (
    WorkScheduleSerializer, TimeEntrySerializer, TimesheetSerializer,
    AttendanceReportSerializer, OvertimeRequestSerializer,
    TimeEntryCreateSerializer
)


class WorkScheduleViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing work schedules.
    Provides CRUD operations and schedule management features.
    """
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['department', 'is_active', 'schedule_type']
    search_fields = ['name', 'department__name']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter schedules based on user permissions."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # If user has employee profile, they can see schedules for their department
        if hasattr(user, 'employee_profile') and user.employee_profile.department:
            if not user.is_staff:
                return queryset.filter(department=user.employee_profile.department)
        
        return queryset

    @action(detail=False, methods=['get'])
    def current_schedule(self, request):
        """Get current active schedule for the authenticated user."""
        if not hasattr(request.user, 'employee_profile'):
            return Response(
                {'error': 'No employee profile found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = request.user.employee_profile
        if not employee.department:
            return Response(
                {'error': 'Employee has no department assigned'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        schedule = WorkSchedule.objects.filter(
            department=employee.department,
            is_active=True
        ).first()
        
        if schedule:
            serializer = self.get_serializer(schedule)
            return Response(serializer.data)
        
        return Response(
            {'message': 'No active schedule found for your department'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class TimeEntryViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing time entries (clock in/out).
    Provides time tracking functionality with validation.
    """
    queryset = TimeEntry.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'entry_type', 'status']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering_fields = ['clock_in_time', 'clock_out_time', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TimeEntryCreateSerializer
        return TimeEntrySerializer

    def get_queryset(self):
        """Filter time entries based on user permissions."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Apply date filtering if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(clock_in_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(clock_in_time__date__lte=end_date)
        
        # If user has employee profile, filter to their entries
        if hasattr(user, 'employee') and not user.is_staff:
            queryset = queryset.filter(employee=user.employee)
        
        return queryset

    @action(detail=False, methods=['post'])
    def clock_in(self, request):
        """Clock in the authenticated user."""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'No employee profile found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = request.user.employee
        
        # Check if already clocked in
        active_entry = TimeEntry.objects.filter(
            employee=employee,
            clock_out_time__isnull=True
        ).first()
        
        if active_entry:
            return Response(
                {'error': 'Already clocked in'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new time entry
        data = request.data.copy()
        data['employee'] = employee.id
        data['entry_type'] = 'regular'
        
        serializer = TimeEntryCreateSerializer(data=data)
        if serializer.is_valid():
            time_entry = serializer.save()
            response_serializer = TimeEntrySerializer(time_entry)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clock_out(self, request):
        """Clock out the authenticated user."""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'No employee profile found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = request.user.employee
        
        # Find active time entry
        active_entry = TimeEntry.objects.filter(
            employee=employee,
            clock_out_time__isnull=True
        ).first()
        
        if not active_entry:
            return Response(
                {'error': 'No active clock-in found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update with clock out time
        active_entry.clock_out_time = timezone.now()
        if 'location' in request.data:
            active_entry.clock_out_location = request.data['location']
        if 'notes' in request.data:
            active_entry.notes = request.data['notes']
        
        active_entry.save()
        
        serializer = TimeEntrySerializer(active_entry)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def current_status(self, request):
        """Get current clock status for the authenticated user."""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'No employee profile found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = request.user.employee
        active_entry = TimeEntry.objects.filter(
            employee=employee,
            clock_out_time__isnull=True
        ).first()
        
        if active_entry:
            serializer = TimeEntrySerializer(active_entry)
            return Response({
                'status': 'clocked_in',
                'entry': serializer.data
            })
        
        return Response({'status': 'clocked_out'})


class TimesheetViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing timesheets.
    Provides weekly time aggregation and approval workflow.
    """
    queryset = Timesheet.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'status', 'week_start']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['week_start', 'created_at']
    ordering = ['-week_start']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        return TimesheetSerializer

    def get_queryset(self):
        """Filter timesheets based on user permissions."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # If user has employee profile and is not staff, show only their timesheets
        if hasattr(user, 'employee') and not user.is_staff:
            queryset = queryset.filter(employee=user.employee)
        
        return queryset

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit timesheet for approval."""
        timesheet = self.get_object()
        
        if timesheet.status != 'draft':
            return Response(
                {'error': 'Only draft timesheets can be submitted'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timesheet.status = 'pending'
        timesheet.submitted_at = timezone.now()
        timesheet.save()
        
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve timesheet (managers only)."""
        timesheet = self.get_object()
        
        if timesheet.status != 'pending':
            return Response(
                {'error': 'Only pending timesheets can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timesheet.status = 'approved'
        timesheet.approved_at = timezone.now()
        timesheet.approved_by = request.user
        timesheet.save()
        
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject timesheet with comments."""
        timesheet = self.get_object()
        
        if timesheet.status != 'pending':
            return Response(
                {'error': 'Only pending timesheets can be rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timesheet.status = 'rejected'
        timesheet.approval_comments = request.data.get('comments', '')
        timesheet.save()
        
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)


class OvertimeRequestViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing overtime requests.
    Provides pre-approval workflow for overtime work.
    """
    queryset = OvertimeRequest.objects.all()
    serializer_class = OvertimeRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'status', 'date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    ordering_fields = ['date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter overtime requests based on user permissions."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # If user has employee profile and is not staff, show only their requests
        if hasattr(user, 'employee') and not user.is_staff:
            queryset = queryset.filter(employee=user.employee)
        
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve overtime request."""
        overtime_request = self.get_object()
        
        if overtime_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        overtime_request.status = 'approved'
        overtime_request.approved_by = request.user
        overtime_request.approved_at = timezone.now()
        overtime_request.save()
        
        serializer = self.get_serializer(overtime_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject overtime request with comments."""
        overtime_request = self.get_object()
        
        if overtime_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        overtime_request.status = 'rejected'
        overtime_request.approval_comments = request.data.get('comments', '')
        overtime_request.save()
        
        serializer = self.get_serializer(overtime_request)
        return Response(serializer.data)


class AttendanceReportViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing attendance reports.
    Provides flexible reporting capabilities.
    """
    queryset = AttendanceReport.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'department', 'report_type']
    search_fields = ['name', 'employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        return AttendanceReportSerializer

    def get_queryset(self):
        """Filter reports based on user permissions."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # If user has employee profile and is not staff, show only their reports
        if hasattr(user, 'employee') and not user.is_staff:
            queryset = queryset.filter(employee=user.employee)
        
        return queryset

    @action(detail=False, methods=['post'])
    def generate_summary(self, request):
        """Generate attendance summary for specified period."""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        employee_id = request.data.get('employee_id')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build query
        queryset = TimeEntry.objects.filter(
            clock_in_time__date__gte=start_date,
            clock_in_time__date__lte=end_date,
            clock_out_time__isnull=False
        )
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        elif hasattr(request.user, 'employee') and not request.user.is_staff:
            queryset = queryset.filter(employee=request.user.employee)
        
        # Calculate summary statistics
        total_entries = queryset.count()
        total_hours = queryset.aggregate(
            total=Sum('hours_worked')
        )['total'] or 0
        
        avg_hours = queryset.aggregate(
            avg=Avg('hours_worked')
        )['avg'] or 0
        
        overtime_entries = queryset.filter(is_overtime=True)
        overtime_hours = overtime_entries.aggregate(
            total=Sum('hours_worked')
        )['total'] or 0
        
        summary = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'statistics': {
                'total_entries': total_entries,
                'total_hours': float(total_hours),
                'average_hours_per_day': float(avg_hours),
                'overtime_entries': overtime_entries.count(),
                'overtime_hours': float(overtime_hours)
            }
        }
        
        return Response(summary)
