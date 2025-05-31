from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from .models import Employee, Department
from .serializers import (
    EmployeeSerializer, 
    EmployeeCreateSerializer, 
    DepartmentSerializer,
    UserSerializer
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
