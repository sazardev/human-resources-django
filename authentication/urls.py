from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Password reset
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
      # Session management
    path('sessions/', views.UserSessionsView.as_view(), name='user-sessions'),
    path('admin/sessions/', views.SessionManagementView.as_view(), name='admin-sessions'),
    path('admin/sessions/<int:session_id>/', views.SessionManagementView.as_view(), name='admin-session-detail'),
    path('sessions/user/<int:user_id>/', views.UserSessionHistoryView.as_view(), name='user-session-history'),
    path('sessions/my-history/', views.UserSessionHistoryView.as_view(), name='my-session-history'),
    
    # Security info
    path('security-info/', views.user_security_info, name='user-security-info'),
    path('verify-email/', views.verify_email, name='verify-email'),
]
