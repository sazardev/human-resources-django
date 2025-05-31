from django.contrib import admin
from .models import Employee, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    ordering = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'first_name', 'last_name', 'email', 
        'department', 'position', 'employment_status', 'hire_date'
    ]
    list_filter = ['department', 'employment_status', 'hire_date', 'created_at']
    search_fields = [
        'employee_id', 'first_name', 'last_name', 'email', 
        'position', 'user__username'
    ]
    list_editable = ['employment_status']
    ordering = ['employee_id']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Employment Information', {
            'fields': ('user', 'department', 'position', 'hire_date', 'employment_status', 'salary')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
