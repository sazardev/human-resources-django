from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    """
    Extended User model with additional fields for HR system
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Profile fields
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # HR specific fields
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    
    # Account management
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'auth_user_extended'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_full_name(self):
        return self.full_name
    
    def is_password_reset_token_valid(self):
        """Check if password reset token is still valid (24 hours)"""
        if not self.password_reset_token_created:
            return False
        
        expiration_time = self.password_reset_token_created + timezone.timedelta(hours=24)
        return timezone.now() < expiration_time


class UserSession(models.Model):
    """
    Track user sessions for security purposes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    logout_type = models.CharField(
        max_length=20, 
        choices=[
            ('manual', 'Logout Manual'),
            ('expired', 'Sesión Expirada'),
            ('forced', 'Logout Forzado'),
            ('password_change', 'Cambio de Contraseña'),
        ],
        null=True, 
        blank=True
    )
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-last_activity']
    
    def __str__(self):
        status = "Activa" if self.is_active else "Inactiva"
        return f"{self.user.email} - {self.ip_address} ({status})"
    
    def end_session(self, logout_type='manual'):
        """Finalizar la sesión"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.logout_type = logout_type
        self.save(update_fields=['is_active', 'ended_at', 'logout_type'])
    
    @property
    def duration(self):
        """Duración de la sesión"""
        end_time = self.ended_at or timezone.now()
        return end_time - self.created_at
    
    @property
    def is_expired(self):
        """Verificar si la sesión ha expirado (24 horas)"""
        return timezone.now() - self.last_activity > timezone.timedelta(hours=24)


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-attempted_at']
    
    def __str__(self):
        status = "Exitoso" if self.success else "Fallido"
        return f"{self.email} - {status} ({self.attempted_at})"
