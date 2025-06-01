"""
URL configuration for attendance app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkScheduleViewSet,
    TimeEntryViewSet,
    TimesheetViewSet,
    OvertimeRequestViewSet,
    AttendanceReportViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'schedules', WorkScheduleViewSet, basename='workschedule')
router.register(r'time-entries', TimeEntryViewSet, basename='timeentry')
router.register(r'timesheets', TimesheetViewSet, basename='timesheet')
router.register(r'overtime-requests', OvertimeRequestViewSet, basename='overtimerequest')
router.register(r'reports', AttendanceReportViewSet, basename='attendancereport')

app_name = 'attendance'

urlpatterns = [
    path('', include(router.urls)),
]
