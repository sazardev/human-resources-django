from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import User, UserSession, LoginAttempt


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, BaseUserAdmin):
    """
    Admin configuration for User model with history tracking
    """
    list_display = [
        'email', 'username', 'full_name', 'employee_id', 
        'department', 'is_active', 'is_email_verified', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_email_verified',
        'department', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'employee_id']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Información de Login', {
            'fields': ('username', 'email', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone', 'date_of_birth', 'bio', 'profile_picture')
        }),
        ('Información de Empleado', {
            'fields': ('employee_id', 'hire_date', 'department', 'position')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Verificación y Seguridad', {
            'fields': ('is_email_verified', 'last_login', 'last_login_ip')
        }),
        ('Fechas Importantes', {
            'fields': ('date_joined', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        ('Información Básica', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Información Adicional', {
            'classes': ('wide',),
            'fields': ('phone', 'employee_id', 'department', 'position'),
        }),
    )
    
    readonly_fields = ['date_joined', 'updated_at', 'last_login', 'last_login_ip']

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Nombre Completo'


@admin.register(UserSession)
class UserSessionAdmin(SimpleHistoryAdmin):
    """
    Admin configuration for UserSession model with history tracking
    """
    list_display = [
        'user_email', 'ip_address', 'status_display', 
        'created_at', 'session_duration', 'ended_at', 'logout_type'
    ]
    list_filter = ['is_active', 'logout_type', 'created_at', 'last_activity']
    search_fields = ['user__email', 'ip_address', 'user_agent']
    ordering = ['-created_at']
    readonly_fields = [
        'session_key', 'user_agent', 'created_at', 'last_activity', 
        'ended_at', 'logout_type', 'session_duration'
    ]
    
    fieldsets = (
        ('Información de Sesión', {
            'fields': ('user', 'session_key', 'is_active')
        }),
        ('Información de Conexión', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity', 'ended_at', 'session_duration')
        }),
        ('Información de Cierre', {
            'fields': ('logout_type',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email del Usuario'
    
    def status_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">🟢 ACTIVA</span>')
        else:
            color = 'orange' if obj.logout_type == 'expired' else 'red'
            return format_html(f'<span style="color: {color}; font-weight: bold;">🔴 INACTIVA</span>')
    status_display.short_description = 'Estado'
    
    def session_duration(self, obj):
        from django.utils import timezone
        if obj.ended_at:
            duration = obj.ended_at - obj.created_at
        elif obj.is_active:
            duration = timezone.now() - obj.created_at
        else:
            duration = obj.last_activity - obj.created_at
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    session_duration.short_description = 'Duración'
    
    def has_add_permission(self, request):
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(SimpleHistoryAdmin):
    """
    Admin configuration for LoginAttempt model with history tracking
    """
    list_display = [
        'email', 'ip_address', 'success_status', 
        'attempted_at', 'failure_reason'
    ]
    list_filter = ['success', 'attempted_at']
    search_fields = ['email', 'ip_address']
    ordering = ['-attempted_at']
    readonly_fields = ['email', 'ip_address', 'user_agent', 'success', 'attempted_at', 'failure_reason']
    
    def success_status(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">✓ Exitoso</span>')
        else:
            return format_html('<span style="color: red;">✗ Fallido</span>')
    success_status.short_description = 'Estado'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
