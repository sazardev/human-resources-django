#!/usr/bin/env python
"""
Temporary script to enable public API access for testing dynamic field selection
"""
import os
import sys
import django

# Add the project root to Python path  
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

# Import and monkey-patch the views to allow public access
from employees import views
from rest_framework.permissions import AllowAny

# Temporarily override permission classes
views.DepartmentViewSet.permission_classes = [AllowAny]
views.EmployeeViewSet.permission_classes = [AllowAny]
views.PerformanceReviewViewSet.permission_classes = [AllowAny]
views.PerformanceGoalViewSet.permission_classes = [AllowAny]
views.PerformanceNoteViewSet.permission_classes = [AllowAny]

print("✅ API permissions temporarily set to AllowAny for testing")
print("⚠️ Remember to revert these changes after testing!")
print("Now you can test the API endpoints without authentication")

# Keep the script running
input("Press Enter to revert permissions and exit...")

# Revert permissions
from rest_framework.permissions import IsAuthenticated
views.DepartmentViewSet.permission_classes = [IsAuthenticated]
views.EmployeeViewSet.permission_classes = [IsAuthenticated]
views.PerformanceReviewViewSet.permission_classes = [IsAuthenticated]
views.PerformanceGoalViewSet.permission_classes = [IsAuthenticated]
views.PerformanceNoteViewSet.permission_classes = [IsAuthenticated]

print("✅ Permissions reverted to IsAuthenticated")
