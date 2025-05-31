from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count
from datetime import date, timedelta

from .models import Employee, Department, PerformanceReview, PerformanceGoal, PerformanceNote
from .serializers import (
    EmployeeSerializer, 
    EmployeeCreateSerializer, 
    DepartmentSerializer,
    UserSerializer,
    PerformanceReviewSerializer,
    PerformanceGoalSerializer,
    PerformanceNoteSerializer,
    EmployeePerformanceSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employees
    """
    queryset = Employee.objects.select_related('user', 'department').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'employment_status', 'position']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id', 'position']
    ordering_fields = ['employee_id', 'first_name', 'last_name', 'hire_date', 'created_at']
    ordering = ['employee_id']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action == 'performance_overview':
            return EmployeePerformanceSerializer
        return EmployeeSerializer

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change employee status"""
        employee = self.get_object()
        status_value = request.data.get('status')
        
        if status_value not in dict(Employee.EMPLOYMENT_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employee.employment_status = status_value
        employee.save()
        
        serializer = self.get_serializer(employee)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get employees grouped by department"""
        department_id = request.query_params.get('department_id')
        
        if department_id:
            employees = self.queryset.filter(department_id=department_id)
        else:
            employees = self.queryset.all()
        
        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get employee statistics"""
        total_employees = self.queryset.count()
        active_employees = self.queryset.filter(employment_status='active').count()
        departments_count = Department.objects.count()
        
        stats = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': total_employees - active_employees,
            'departments_count': departments_count,
        }
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def performance_overview(self, request, pk=None):
        """Get comprehensive performance overview for an employee"""
        employee = self.get_object()
        serializer = EmployeePerformanceSerializer(employee)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance_reviews(self, request, pk=None):
        """Get all performance reviews for an employee"""
        employee = self.get_object()
        reviews = employee.performance_reviews.all()
        serializer = PerformanceReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance_goals(self, request, pk=None):
        """Get all performance goals for an employee"""
        employee = self.get_object()
        goals = employee.performance_goals.all()
        serializer = PerformanceGoalSerializer(goals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance_notes(self, request, pk=None):
        """Get all performance notes for an employee"""
        employee = self.get_object()
        notes = employee.performance_notes.all()
        serializer = PerformanceNoteSerializer(notes, many=True)
        return Response(serializer.data)


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing performance reviews
    """
    queryset = PerformanceReview.objects.select_related('employee', 'reviewer').all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'reviewer', 'review_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['review_date', 'overall_rating', 'created_at']
    ordering = ['-review_date']

    def perform_create(self, serializer):
        """Set the reviewer to the current user when creating a review"""
        serializer.save(reviewer=self.request.user)

    @action(detail=False, methods=['get'])
    def by_rating(self, request):
        """Get reviews grouped by rating"""
        rating = request.query_params.get('rating')
        if rating:
            reviews = self.queryset.filter(overall_rating=rating)
        else:
            reviews = self.queryset.all()
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get performance review statistics"""
        total_reviews = self.queryset.count()
        avg_rating = self.queryset.aggregate(Avg('overall_rating'))['overall_rating__avg']
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = self.queryset.filter(overall_rating=i).count()
            rating_distribution[f'rating_{i}'] = count
        
        stats = {
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'rating_distribution': rating_distribution,
        }
        
        return Response(stats)


class PerformanceGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing performance goals
    """
    queryset = PerformanceGoal.objects.select_related('employee', 'created_by', 'review').all()
    serializer_class = PerformanceGoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'category', 'priority', 'status', 'created_by']
    search_fields = ['title', 'description', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['target_date', 'priority', 'created_at', 'progress_percentage']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set the created_by to the current user when creating a goal"""
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue goals"""
        overdue_goals = self.queryset.filter(
            target_date__lt=date.today(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(overdue_goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get goals filtered by status"""
        status_filter = request.query_params.get('status')
        if status_filter:
            goals = self.queryset.filter(status=status_filter)
        else:
            goals = self.queryset.all()
        
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update goal progress"""
        goal = self.get_object()
        progress = request.data.get('progress_percentage')
        notes = request.data.get('progress_notes', '')
        
        if progress is not None:
            if 0 <= progress <= 100:
                goal.progress_percentage = progress
                if notes:
                    goal.progress_notes = notes
                goal.save()
                
                serializer = self.get_serializer(goal)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Progress must be between 0 and 100'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'progress_percentage is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get goal statistics"""
        total_goals = self.queryset.count()
        completed_goals = self.queryset.filter(status='completed').count()
        overdue_goals = self.queryset.filter(
            target_date__lt=date.today(),
            status__in=['pending', 'in_progress']
        ).count()
        
        avg_progress = self.queryset.aggregate(
            Avg('progress_percentage')
        )['progress_percentage__avg']
        
        stats = {
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'overdue_goals': overdue_goals,
            'in_progress_goals': self.queryset.filter(status='in_progress').count(),
            'average_progress': round(avg_progress, 2) if avg_progress else 0,
            'completion_rate': round((completed_goals / total_goals) * 100, 2) if total_goals > 0 else 0,
        }
        
        return Response(stats)


class PerformanceNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing performance notes
    """
    queryset = PerformanceNote.objects.select_related('employee', 'author', 'goal', 'review').all()
    serializer_class = PerformanceNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'author', 'note_type', 'is_private', 'goal', 'review']
    search_fields = ['title', 'content', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['date_observed', 'created_at']
    ordering = ['-date_observed']

    def perform_create(self, serializer):
        """Set the author to the current user when creating a note"""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """Filter queryset based on user permissions for private notes"""
        queryset = super().get_queryset()
        
        # If user is not superuser or HR, filter out private notes they didn't create
        if not (self.request.user.is_superuser or 
                self.request.user.groups.filter(name='HR').exists()):
            queryset = queryset.filter(
                Q(is_private=False) | Q(author=self.request.user)
            )
        
        return queryset

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get notes filtered by type"""
        note_type = request.query_params.get('type')
        if note_type:
            notes = self.get_queryset().filter(note_type=note_type)
        else:
            notes = self.get_queryset()
        
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notes (last 30 days)"""
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_notes = self.get_queryset().filter(date_observed__gte=thirty_days_ago)
        serializer = self.get_serializer(recent_notes, many=True)
        return Response(serializer.data)
