# filepath: payroll/urls.py
"""
URL configuration for payroll management system.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'payroll-periods', views.PayrollPeriodViewSet, basename='payrollperiod')
router.register(r'tax-brackets', views.TaxBracketViewSet, basename='taxbracket')
router.register(r'deduction-types', views.DeductionTypeViewSet, basename='deductiontype')
router.register(r'bonus-types', views.BonusTypeViewSet, basename='bonustype')
router.register(r'payslips', views.PayslipViewSet, basename='payslip')
router.register(r'compensation-history', views.CompensationHistoryViewSet, basename='compensationhistory')
router.register(r'payroll-configuration', views.PayrollConfigurationViewSet, basename='payrollconfiguration')
router.register(r'analytics', views.PayrollAnalyticsViewSet, basename='payrollanalytics')

app_name = 'payroll'

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
]
