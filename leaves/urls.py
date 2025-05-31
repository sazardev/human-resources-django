from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeaveTypeViewSet,
    HolidayViewSet,
    LeaveBalanceViewSet,
    LeaveRequestViewSet,
    LeaveRequestCommentViewSet,
    TeamScheduleViewSet,
    LeavePolicyViewSet,
    LeaveAnalyticsViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'leave-types', LeaveTypeViewSet, basename='leavetype')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leavebalance')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leaverequest')
router.register(r'leave-comments', LeaveRequestCommentViewSet, basename='leaverequestcomment')
router.register(r'team-schedules', TeamScheduleViewSet, basename='teamschedule')
router.register(r'leave-policies', LeavePolicyViewSet, basename='leavepolicy')
router.register(r'analytics', LeaveAnalyticsViewSet, basename='leaveanalytics')

# URL patterns
urlpatterns = [
    path('api/leaves/', include(router.urls)),
]

app_name = 'leaves'
