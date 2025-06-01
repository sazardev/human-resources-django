from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    JobPosting, Candidate, Application, CandidateDocument,
    InterviewRound, Interview, InterviewEvaluation, OfferLetter,
    RecruitmentPipeline
)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = [
        'job_id', 'title', 'department', 'status', 'job_type', 
        'experience_level', 'application_count', 'is_featured', 
        'posted_date', 'created_at'
    ]
    list_filter = [
        'status', 'job_type', 'experience_level', 'department', 
        'is_featured', 'remote_work_allowed', 'priority_level'
    ]
    search_fields = [
        'title', 'job_id', 'description', 'requirements', 'keywords'
    ]
    readonly_fields = ['job_id', 'application_count', 'is_open', 'salary_range_display']
    filter_horizontal = ['assigned_recruiters']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('job_id', 'title', 'department', 'hiring_manager')
        }),
        ('Job Details', {
            'fields': ('description', 'responsibilities', 'requirements', 'preferred_qualifications')
        }),
        ('Employment Details', {
            'fields': (
                ('job_type', 'experience_level'),
                ('salary_min', 'salary_max', 'salary_currency'),
                'salary_range_display'
            )
        }),
        ('Location & Work Arrangement', {
            'fields': ('location', 'remote_work_allowed', 'travel_required')
        }),
        ('Posting Management', {
            'fields': (
                ('status', 'priority_level'),
                ('posted_date', 'closing_date'),
                ('application_deadline', 'max_applications'),
                'is_featured'
            )
        }),
        ('Application Settings', {
            'fields': ('application_email', 'application_url', 'positions_available')
        }),
        ('Assignment & Marketing', {
            'fields': ('assigned_recruiters', 'keywords')
        }),
        ('Statistics', {
            'fields': ('application_count', 'is_open'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department', 'hiring_manager')

    def save_model(self, request, obj, form, change):
        if not change and not obj.posted_date and obj.status == 'active':
            from django.utils import timezone
            obj.posted_date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_id', 'full_name', 'email', 'current_position', 
        'years_of_experience', 'source', 'is_active', 'blacklisted',
        'total_applications', 'created_at'
    ]
    list_filter = [
        'source', 'is_active', 'blacklisted', 'willing_to_relocate',
        'requires_visa_sponsorship', 'country'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'candidate_id',
        'current_position', 'current_company', 'tags'
    ]
    readonly_fields = ['candidate_id', 'full_name', 'total_applications']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'candidate_id',
                ('first_name', 'last_name', 'full_name'),
                ('email', 'phone')
            )
        }),
        ('Professional Information', {
            'fields': (
                ('current_position', 'current_company'),
                'years_of_experience'
            )
        }),
        ('Contact Information', {
            'fields': (
                'address',
                ('city', 'state', 'postal_code'),
                'country'
            )
        }),
        ('Online Presence', {
            'fields': ('linkedin_url', 'portfolio_url', 'github_url')
        }),
        ('Recruitment Information', {
            'fields': (
                ('source', 'referrer'),
                ('availability_date', 'salary_expectation'),
                ('willing_to_relocate', 'requires_visa_sponsorship')
            )
        }),
        ('Internal Notes', {
            'fields': ('recruiter_notes', 'tags')
        }),
        ('Status', {
            'fields': (
                ('is_active', 'blacklisted'),
                'blacklist_reason',
                'total_applications'
            )
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('referrer')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_id', 'candidate_name', 'job_title', 'status',
        'overall_score', 'screening_completed', 'assigned_recruiter',
        'applied_date', 'days_since_applied'
    ]
    list_filter = [
        'status', 'screening_completed', 'job_posting__department',
        'job_posting__job_type', 'assigned_recruiter'
    ]
    search_fields = [
        'application_id', 'candidate__first_name', 'candidate__last_name',
        'job_posting__title', 'cover_letter'
    ]
    readonly_fields = [
        'application_id', 'applied_date', 'last_activity_date',
        'days_since_applied', 'current_stage', 'is_active'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'application_id',
                ('candidate', 'job_posting'),
                'applied_date'
            )
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'status')
        }),
        ('Scoring & Evaluation', {
            'fields': (
                ('initial_score', 'overall_score'),
                ('screening_completed', 'screening_notes'),
                'interview_stage'
            )
        }),
        ('Assignment', {
            'fields': ('assigned_recruiter',)
        }),
        ('Decision Information', {
            'fields': ('rejection_reason', 'rejection_feedback', 'hired_date')
        }),
        ('Internal Notes', {
            'fields': ('recruiter_notes', 'hiring_manager_notes')
        }),
        ('Timeline', {
            'fields': (
                'last_activity_date', 'days_since_applied',
                'current_stage', 'is_active'
            ),
            'classes': ('collapse',)
        })
    )

    def candidate_name(self, obj):
        return obj.candidate.full_name
    candidate_name.short_description = 'Candidate'
    candidate_name.admin_order_field = 'candidate__first_name'

    def job_title(self, obj):
        return obj.job_posting.title
    job_title.short_description = 'Job'
    job_title.admin_order_field = 'job_posting__title'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate', 'job_posting', 'assigned_recruiter'
        )


@admin.register(CandidateDocument)
class CandidateDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'candidate_name', 'document_type', 'version',
        'file_size_display', 'is_confidential', 'uploaded_at'
    ]
    list_filter = ['document_type', 'is_confidential', 'uploaded_at']
    search_fields = ['title', 'description', 'candidate__first_name', 'candidate__last_name']
    readonly_fields = ['file_size', 'file_size_display', 'uploaded_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('candidate', 'document_type'),
                'title', 'file'
            )
        }),
        ('File Information', {
            'fields': (
                ('file_size', 'file_size_display'),
                'mime_type', 'is_confidential'
            )
        }),
        ('Version Control', {
            'fields': (
                ('version', 'previous_version'),
                'uploaded_by'
            )
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def candidate_name(self, obj):
        return obj.candidate.full_name
    candidate_name.short_description = 'Candidate'
    candidate_name.admin_order_field = 'candidate__first_name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('candidate', 'uploaded_by')


@admin.register(InterviewRound)
class InterviewRoundAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'job_posting_title', 'round_type', 'sequence_order',
        'duration_minutes', 'is_mandatory', 'is_technical', 'is_active'
    ]
    list_filter = ['round_type', 'is_mandatory', 'is_technical', 'is_active']
    search_fields = ['name', 'description', 'job_posting__title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'job_posting',
                ('name', 'round_type'),
                'sequence_order'
            )
        }),
        ('Configuration', {
            'fields': (
                'duration_minutes',
                ('is_mandatory', 'is_technical'),
                'required_interviewers'
            )
        }),
        ('Instructions', {
            'fields': (
                'description',
                'interviewer_instructions',
                'candidate_instructions'
            )
        }),
        ('Requirements', {
            'fields': ('minimum_score_to_pass',)
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

    def job_posting_title(self, obj):
        return obj.job_posting.title
    job_posting_title.short_description = 'Job Posting'
    job_posting_title.admin_order_field = 'job_posting__title'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job_posting')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = [
        'interview_id', 'candidate_name', 'job_title', 'interview_round_name',
        'scheduled_start', 'status', 'meeting_type', 'primary_interviewer'
    ]
    list_filter = [
        'status', 'meeting_type', 'scheduled_start', 'primary_interviewer',
        'application__job_posting__department'
    ]
    search_fields = [
        'interview_id', 'application__candidate__first_name',
        'application__candidate__last_name', 'application__job_posting__title'
    ]
    readonly_fields = [
        'interview_id', 'duration_scheduled', 'duration_actual', 'is_overdue'
    ]
    filter_horizontal = ['additional_interviewers']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'interview_id',
                ('application', 'interview_round')
            )
        }),
        ('Scheduling', {
            'fields': (
                ('scheduled_start', 'scheduled_end'),
                ('actual_start', 'actual_end'),
                ('duration_scheduled', 'duration_actual')
            )
        }),
        ('Meeting Details', {
            'fields': (
                'meeting_type', 'location',
                ('meeting_link', 'meeting_id'),
                'meeting_password'
            )
        }),
        ('Participants', {
            'fields': ('primary_interviewer', 'additional_interviewers')
        }),
        ('Status & Notes', {
            'fields': (
                'status', 'preparation_notes', 'special_instructions'
            )
        }),
        ('Communication', {
            'fields': (
                ('invitation_sent', 'reminder_sent'),
                'confirmation_received'
            )
        }),
        ('Rescheduling', {
            'fields': (
                ('reschedule_count', 'reschedule_reason'),
            ),
            'classes': ('collapse',)
        }),
        ('Status Checks', {
            'fields': ('is_overdue',),
            'classes': ('collapse',)
        })
    )

    def candidate_name(self, obj):
        return obj.application.candidate.full_name
    candidate_name.short_description = 'Candidate'

    def job_title(self, obj):
        return obj.application.job_posting.title
    job_title.short_description = 'Job'

    def interview_round_name(self, obj):
        return obj.interview_round.name
    interview_round_name.short_description = 'Round'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'application__candidate', 'application__job_posting',
            'interview_round', 'primary_interviewer'
        )


@admin.register(InterviewEvaluation)
class InterviewEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'job_title', 'evaluator', 'overall_rating',
        'recommendation', 'average_rating', 'submitted_at'
    ]
    list_filter = [
        'recommendation', 'overall_rating', 'evaluator',
        'interview__application__job_posting__department'
    ]
    search_fields = [
        'interview__application__candidate__first_name',
        'interview__application__candidate__last_name',
        'interview__application__job_posting__title'
    ]
    readonly_fields = ['average_rating', 'submitted_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('interview', 'evaluator'),
                'submitted_at'
            )
        }),
        ('Overall Assessment', {
            'fields': (
                ('overall_rating', 'recommendation'),
                'average_rating'
            )
        }),
        ('Detailed Ratings', {
            'fields': (
                ('technical_skills', 'communication_skills'),
                ('problem_solving', 'cultural_fit'),
                ('enthusiasm', 'experience_relevance')
            )
        }),
        ('Feedback', {
            'fields': (
                'strengths', 'weaknesses', 'specific_feedback'
            )
        }),
        ('Questions & Responses', {
            'fields': ('questions_asked', 'candidate_questions')
        }),
        ('Additional Assessment', {
            'fields': (
                'would_work_with_again',
                'salary_recommendation'
            )
        }),
        ('Internal Notes', {
            'fields': ('private_notes',)
        })
    )

    def candidate_name(self, obj):
        return obj.interview.application.candidate.full_name
    candidate_name.short_description = 'Candidate'

    def job_title(self, obj):
        return obj.interview.application.job_posting.title
    job_title.short_description = 'Job'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'interview__application__candidate',
            'interview__application__job_posting',
            'evaluator'
        )


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = [
        'offer_id', 'candidate_name', 'position_title', 'base_salary',
        'status', 'offer_expiry_date', 'is_expired', 'created_at'
    ]
    list_filter = [
        'status', 'offer_type', 'department', 'currency',
        'health_insurance', 'prepared_by', 'approved_by'
    ]
    search_fields = [
        'offer_id', 'application__candidate__first_name',
        'application__candidate__last_name', 'position_title'
    ]
    readonly_fields = [
        'offer_id', 'is_expired', 'total_compensation',
        'days_until_expiry', 'created_at', 'updated_at'
    ]
    filter_horizontal = ['additional_documents']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'offer_id', 'application',
                ('position_title', 'department'),
                'reporting_manager'
            )
        }),
        ('Offer Details', {
            'fields': (
                'offer_type',
                ('base_salary', 'currency', 'salary_frequency'),
                'total_compensation'
            )
        }),
        ('Additional Compensation', {
            'fields': (
                'signing_bonus',
                ('equity_percentage', 'equity_shares')
            )
        }),
        ('Benefits Package', {
            'fields': (
                ('health_insurance', 'dental_insurance', 'vision_insurance'),
                ('retirement_plan', 'paid_time_off', 'sick_leave')
            )
        }),
        ('Work Arrangement', {
            'fields': (
                ('work_location', 'remote_work_allowed'),
                'start_date'
            )
        }),
        ('Offer Management', {
            'fields': (
                ('status', 'offer_expiry_date'),
                ('is_expired', 'days_until_expiry')
            )
        }),
        ('Approval Process', {
            'fields': (
                ('prepared_by', 'approved_by'),
                'approved_at'
            )
        }),
        ('Communication', {
            'fields': (
                ('sent_date', 'response_date'),
            )
        }),
        ('Additional Terms', {
            'fields': (
                ('probation_period', 'notice_period'),
                'special_conditions'
            )
        }),
        ('Documents', {
            'fields': ('offer_letter_document', 'additional_documents')
        }),
        ('Decline Information', {
            'fields': ('decline_reason', 'counter_offer_details'),
            'classes': ('collapse',)
        }),
        ('Internal Notes', {
            'fields': ('internal_notes',),
            'classes': ('collapse',)
        })
    )

    def candidate_name(self, obj):
        return obj.application.candidate.full_name
    candidate_name.short_description = 'Candidate'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'application__candidate', 'department', 'reporting_manager',
            'prepared_by', 'approved_by'
        )


@admin.register(RecruitmentPipeline)
class RecruitmentPipelineAdmin(admin.ModelAdmin):
    list_display = [
        'job_posting_title', 'total_applications', 'candidates_interviewed',
        'offers_extended', 'offers_accepted', 'positions_filled',
        'avg_time_to_hire', 'offer_acceptance_rate', 'last_updated'
    ]
    list_filter = [
        'job_posting__status', 'job_posting__department',
        'last_updated'
    ]
    search_fields = ['job_posting__title', 'job_posting__job_id']
    readonly_fields = [
        'conversion_funnel', 'last_updated'
    ]
    
    fieldsets = (
        ('Job Posting', {
            'fields': ('job_posting',)
        }),
        ('Pipeline Metrics', {
            'fields': (
                ('total_applications', 'applications_screened'),
                ('candidates_interviewed', 'offers_extended'),
                ('offers_accepted', 'positions_filled')
            )
        }),
        ('Time Metrics (Days)', {
            'fields': (
                ('avg_time_to_screen', 'avg_time_to_interview'),
                ('avg_time_to_offer', 'avg_time_to_hire')
            )
        }),
        ('Quality Metrics (%)', {
            'fields': (
                ('offer_acceptance_rate', 'interview_to_offer_rate'),
                'application_to_interview_rate'
            )
        }),
        ('Cost Metrics', {
            'fields': ('cost_per_hire', 'recruitment_cost_total')
        }),
        ('Source Analysis', {
            'fields': ('top_candidate_source', 'conversion_rate_by_source')
        }),
        ('Conversion Funnel', {
            'fields': ('conversion_funnel',),
            'classes': ('collapse',)
        }),
        ('Last Updated', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        })
    )

    def job_posting_title(self, obj):
        return obj.job_posting.title
    job_posting_title.short_description = 'Job Posting'
    job_posting_title.admin_order_field = 'job_posting__title'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job_posting')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Auto-update metrics when saving
        obj.update_metrics()
