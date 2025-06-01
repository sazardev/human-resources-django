from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    verbose_name = 'Time & Attendance'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import attendance.signals
