from django.contrib import admin
from .models import Employee, Department, PerformanceReview, PerformanceGoal, PerformanceNote


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


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'reviewer', 'review_type', 'review_date', 
        'overall_rating', 'status', 'created_at'
    ]
    list_filter = [
        'review_type', 'status', 'overall_rating', 'review_date', 
        'promotion_recommendation', 'salary_increase_recommendation'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'reviewer__username', 'reviewer__first_name', 'reviewer__last_name'
    ]
    date_hierarchy = 'review_date'
    ordering = ['-review_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'reviewer', 'review_type', 'status')
        }),
        ('Review Period', {
            'fields': ('review_period_start', 'review_period_end', 'review_date')
        }),
        ('Ratings', {
            'fields': (
                'overall_rating', 'technical_skills', 'communication', 
                'teamwork', 'leadership', 'problem_solving', 'adaptability'
            )
        }),
        ('Feedback', {
            'fields': (
                'strengths', 'areas_for_improvement', 'goals_for_next_period',
                'reviewer_comments', 'employee_comments'
            )
        }),
        ('Recommendations', {
            'fields': (
                'promotion_recommendation', 'salary_increase_recommendation',
                'training_recommendations'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PerformanceGoal)
class PerformanceGoalAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'employee', 'category', 'priority', 'status', 
        'progress_percentage', 'target_date', 'created_by'
    ]
    list_filter = [
        'category', 'priority', 'status', 'start_date', 'target_date',
        'created_by'
    ]
    search_fields = [
        'title', 'description', 'employee__first_name', 'employee__last_name',
        'employee__employee_id', 'created_by__username'
    ]
    list_editable = ['status', 'progress_percentage']
    date_hierarchy = 'target_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'title', 'description', 'category', 'priority')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_date', 'completed_date')
        }),
        ('Progress', {
            'fields': ('status', 'progress_percentage', 'progress_notes')
        }),
        ('Success Criteria', {
            'fields': ('success_criteria', 'measurable_outcomes', 'completion_notes')
        }),
        ('Review Information', {
            'fields': ('created_by', 'review')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PerformanceNote)
class PerformanceNoteAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'employee', 'author', 'note_type', 
        'date_observed', 'is_private', 'created_at'
    ]
    list_filter = [
        'note_type', 'is_private', 'date_observed', 'author'
    ]
    search_fields = [
        'title', 'content', 'employee__first_name', 'employee__last_name',
        'employee__employee_id', 'author__username'
    ]
    date_hierarchy = 'date_observed'
    ordering = ['-date_observed']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'author', 'note_type', 'title', 'date_observed')
        }),
        ('Content', {
            'fields': ('content', 'is_private')
        }),
        ('Associations', {
            'fields': ('goal', 'review'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
