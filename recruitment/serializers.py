from rest_framework import serializers
from .models import (
    JobPosting, Candidate, Application, CandidateDocument,
    InterviewRound, Interview, InterviewEvaluation, OfferLetter,
    RecruitmentPipeline
)
from employees.models import Department, Employee
from django.contrib.auth import get_user_model

User = get_user_model()


class DynamicFieldsMixin:
    """Mixin to dynamically include/exclude fields based on request parameters"""
    
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            # Drop fields that are specified in the `exclude` argument.
            for field_name in exclude:
                self.fields.pop(field_name, None)


class JobPostingSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for job postings"""
    
    # Nested fields
    department_name = serializers.CharField(source='department.name', read_only=True)
    hiring_manager_name = serializers.CharField(source='hiring_manager.full_name', read_only=True)
    
    # Computed fields
    application_count = serializers.ReadOnlyField()
    is_open = serializers.ReadOnlyField()
    salary_range_display = serializers.ReadOnlyField()
    
    # Write-only fields
    assigned_recruiter_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'job_id', 'title', 'department', 'department_name',
            'hiring_manager', 'hiring_manager_name', 'description',
            'responsibilities', 'requirements', 'preferred_qualifications',
            'job_type', 'experience_level', 'salary_min', 'salary_max',
            'salary_currency', 'location', 'remote_work_allowed',
            'travel_required', 'status', 'posted_date', 'closing_date',
            'application_deadline', 'max_applications', 'application_email',
            'application_url', 'positions_available', 'priority_level',
            'assigned_recruiters', 'assigned_recruiter_ids', 'keywords',
            'is_featured', 'application_count', 'is_open',
            'salary_range_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['job_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        assigned_recruiter_ids = validated_data.pop('assigned_recruiter_ids', [])
        job_posting = JobPosting.objects.create(**validated_data)
        
        if assigned_recruiter_ids:
            recruiters = User.objects.filter(id__in=assigned_recruiter_ids)
            job_posting.assigned_recruiters.set(recruiters)
        
        return job_posting
    
    def update(self, instance, validated_data):
        assigned_recruiter_ids = validated_data.pop('assigned_recruiter_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if assigned_recruiter_ids is not None:
            recruiters = User.objects.filter(id__in=assigned_recruiter_ids)
            instance.assigned_recruiters.set(recruiters)
        
        return instance


class CandidateSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for candidates"""
    
    # Computed fields
    full_name = serializers.ReadOnlyField()
    total_applications = serializers.ReadOnlyField()
    
    # Nested fields
    referrer_name = serializers.CharField(source='referrer.full_name', read_only=True)
    
    class Meta:
        model = Candidate
        fields = [
            'id', 'candidate_id', 'first_name', 'last_name', 'email', 'phone',
            'current_position', 'current_company', 'years_of_experience',
            'address', 'city', 'state', 'postal_code', 'country',
            'linkedin_url', 'portfolio_url', 'github_url', 'source',
            'referrer', 'referrer_name', 'availability_date',
            'salary_expectation', 'willing_to_relocate',
            'requires_visa_sponsorship', 'recruiter_notes', 'tags',
            'is_active', 'blacklisted', 'blacklist_reason',
            'full_name', 'total_applications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['candidate_id', 'created_at', 'updated_at']


class ApplicationSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for job applications"""
    
    # Nested fields
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    job_title = serializers.CharField(source='job_posting.title', read_only=True)
    department_name = serializers.CharField(source='job_posting.department.name', read_only=True)
    assigned_recruiter_name = serializers.CharField(source='assigned_recruiter.get_full_name', read_only=True)
    
    # Computed fields
    days_since_applied = serializers.ReadOnlyField()
    current_stage = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_id', 'candidate', 'candidate_name',
            'candidate_email', 'job_posting', 'job_title', 'department_name',
            'applied_date', 'status', 'cover_letter', 'initial_score',
            'overall_score', 'screening_completed', 'screening_notes',
            'interview_stage', 'assigned_recruiter', 'assigned_recruiter_name',
            'rejection_reason', 'rejection_feedback', 'hired_date',
            'recruiter_notes', 'hiring_manager_notes', 'last_activity_date',
            'days_since_applied', 'current_stage', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['application_id', 'applied_date', 'last_activity_date', 'created_at', 'updated_at']


class CandidateDocumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for candidate documents"""
    
    # Computed fields
    file_size_display = serializers.ReadOnlyField()
    
    # Nested fields
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = CandidateDocument
        fields = [
            'id', 'candidate', 'candidate_name', 'document_type', 'title',
            'file', 'file_size', 'file_size_display', 'mime_type',
            'is_confidential', 'uploaded_by', 'uploaded_by_name',
            'version', 'previous_version', 'description',
            'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['file_size', 'uploaded_at', 'updated_at']


class InterviewRoundSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for interview rounds"""
    
    # Nested fields
    job_posting_title = serializers.CharField(source='job_posting.title', read_only=True)
    
    class Meta:
        model = InterviewRound
        fields = [
            'id', 'job_posting', 'job_posting_title', 'name', 'round_type',
            'sequence_order', 'duration_minutes', 'is_mandatory',
            'is_technical', 'description', 'interviewer_instructions',
            'candidate_instructions', 'required_interviewers',
            'minimum_score_to_pass', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InterviewSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for interviews"""
    
    # Nested fields
    candidate_name = serializers.CharField(source='application.candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='application.job_posting.title', read_only=True)
    interview_round_name = serializers.CharField(source='interview_round.name', read_only=True)
    primary_interviewer_name = serializers.CharField(source='primary_interviewer.get_full_name', read_only=True)
    
    # Computed fields
    duration_scheduled = serializers.ReadOnlyField()
    duration_actual = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    # Many-to-many write fields
    additional_interviewer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Interview
        fields = [
            'id', 'interview_id', 'application', 'candidate_name', 'job_title',
            'interview_round', 'interview_round_name', 'scheduled_start',
            'scheduled_end', 'actual_start', 'actual_end', 'meeting_type',
            'location', 'meeting_link', 'meeting_id', 'meeting_password',
            'primary_interviewer', 'primary_interviewer_name',
            'additional_interviewers', 'additional_interviewer_ids',
            'status', 'preparation_notes', 'special_instructions',
            'invitation_sent', 'reminder_sent', 'confirmation_received',
            'reschedule_count', 'reschedule_reason', 'duration_scheduled',
            'duration_actual', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['interview_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        additional_interviewer_ids = validated_data.pop('additional_interviewer_ids', [])
        interview = Interview.objects.create(**validated_data)
        
        if additional_interviewer_ids:
            interviewers = User.objects.filter(id__in=additional_interviewer_ids)
            interview.additional_interviewers.set(interviewers)
        
        return interview
    
    def update(self, instance, validated_data):
        additional_interviewer_ids = validated_data.pop('additional_interviewer_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if additional_interviewer_ids is not None:
            interviewers = User.objects.filter(id__in=additional_interviewer_ids)
            instance.additional_interviewers.set(interviewers)
        
        return instance


class InterviewEvaluationSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for interview evaluations"""
    
    # Nested fields
    candidate_name = serializers.CharField(source='interview.application.candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='interview.application.job_posting.title', read_only=True)
    interview_round_name = serializers.CharField(source='interview.interview_round.name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.get_full_name', read_only=True)
    
    # Computed fields
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = InterviewEvaluation
        fields = [
            'id', 'interview', 'candidate_name', 'job_title',
            'interview_round_name', 'evaluator', 'evaluator_name',
            'overall_rating', 'recommendation', 'technical_skills',
            'communication_skills', 'problem_solving', 'cultural_fit',
            'enthusiasm', 'experience_relevance', 'strengths', 'weaknesses',
            'specific_feedback', 'questions_asked', 'candidate_questions',
            'would_work_with_again', 'salary_recommendation',
            'private_notes', 'average_rating', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['submitted_at', 'updated_at']


class OfferLetterSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for offer letters"""
    
    # Nested fields
    candidate_name = serializers.CharField(source='application.candidate.full_name', read_only=True)
    candidate_email = serializers.CharField(source='application.candidate.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    reporting_manager_name = serializers.CharField(source='reporting_manager.full_name', read_only=True)
    prepared_by_name = serializers.CharField(source='prepared_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    # Computed fields
    is_expired = serializers.ReadOnlyField()
    total_compensation = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    
    # Many-to-many write fields
    additional_document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = OfferLetter
        fields = [
            'id', 'offer_id', 'application', 'candidate_name', 'candidate_email',
            'position_title', 'department', 'department_name',
            'reporting_manager', 'reporting_manager_name', 'offer_type',
            'base_salary', 'currency', 'salary_frequency', 'signing_bonus',
            'equity_percentage', 'equity_shares', 'health_insurance',
            'dental_insurance', 'vision_insurance', 'retirement_plan',
            'paid_time_off', 'sick_leave', 'work_location',
            'remote_work_allowed', 'start_date', 'status',
            'offer_expiry_date', 'prepared_by', 'prepared_by_name',
            'approved_by', 'approved_by_name', 'approved_at',
            'sent_date', 'response_date', 'probation_period',
            'notice_period', 'offer_letter_document', 'additional_documents',
            'additional_document_ids', 'special_conditions', 'internal_notes',
            'decline_reason', 'counter_offer_details', 'is_expired',
            'total_compensation', 'days_until_expiry', 'created_at', 'updated_at'
        ]
        read_only_fields = ['offer_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        additional_document_ids = validated_data.pop('additional_document_ids', [])
        offer = OfferLetter.objects.create(**validated_data)
        
        if additional_document_ids:
            documents = CandidateDocument.objects.filter(id__in=additional_document_ids)
            offer.additional_documents.set(documents)
        
        return offer
    
    def update(self, instance, validated_data):
        additional_document_ids = validated_data.pop('additional_document_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if additional_document_ids is not None:
            documents = CandidateDocument.objects.filter(id__in=additional_document_ids)
            instance.additional_documents.set(documents)
        
        return instance


class RecruitmentPipelineSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Serializer for recruitment pipeline metrics"""
    
    # Nested fields
    job_posting_title = serializers.CharField(source='job_posting.title', read_only=True)
    job_posting_status = serializers.CharField(source='job_posting.status', read_only=True)
    
    # Computed fields
    conversion_funnel = serializers.ReadOnlyField()
    
    class Meta:
        model = RecruitmentPipeline
        fields = [
            'id', 'job_posting', 'job_posting_title', 'job_posting_status',
            'total_applications', 'applications_screened', 'candidates_interviewed',
            'offers_extended', 'offers_accepted', 'positions_filled',
            'avg_time_to_screen', 'avg_time_to_interview', 'avg_time_to_offer',
            'avg_time_to_hire', 'offer_acceptance_rate', 'interview_to_offer_rate',
            'application_to_interview_rate', 'cost_per_hire', 'recruitment_cost_total',
            'top_candidate_source', 'conversion_rate_by_source', 'conversion_funnel',
            'last_updated'
        ]
        read_only_fields = ['last_updated']


# Simplified serializers for dropdown lists and nested relationships

class JobPostingSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for job posting dropdowns"""
    
    class Meta:
        model = JobPosting
        fields = ['id', 'job_id', 'title', 'status']


class CandidateSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for candidate dropdowns"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidate
        fields = ['id', 'candidate_id', 'full_name', 'email']


class ApplicationSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for application references"""
    
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job_posting.title', read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'application_id', 'candidate_name', 'job_title', 'status']


# Summary serializers for dashboard views

class RecruitmentDashboardSerializer(serializers.Serializer):
    """Serializer for recruitment dashboard metrics"""
    
    total_active_jobs = serializers.IntegerField()
    total_applications_this_month = serializers.IntegerField()
    total_interviews_scheduled = serializers.IntegerField()
    total_offers_pending = serializers.IntegerField()
    avg_time_to_hire_days = serializers.DecimalField(max_digits=5, decimal_places=1)
    top_performing_jobs = JobPostingSimpleSerializer(many=True)
    recent_applications = ApplicationSimpleSerializer(many=True)


class CandidateProfileSerializer(serializers.Serializer):
    """Comprehensive candidate profile for detailed view"""
    
    candidate = CandidateSerializer()
    applications = ApplicationSerializer(many=True)
    documents = CandidateDocumentSerializer(many=True)
    interviews = InterviewSerializer(many=True)
    
    
class JobPostingDetailSerializer(serializers.Serializer):
    """Detailed job posting with related data"""
    
    job_posting = JobPostingSerializer()
    applications = ApplicationSerializer(many=True)
    interview_rounds = InterviewRoundSerializer(many=True)
    pipeline = RecruitmentPipelineSerializer()
