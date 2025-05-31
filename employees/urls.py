from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'performance-reviews', views.PerformanceReviewViewSet)
router.register(r'performance-goals', views.PerformanceGoalViewSet)
router.register(r'performance-notes', views.PerformanceNoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
