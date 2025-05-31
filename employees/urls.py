from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet)
router.register(r'departments', views.DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
