from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from simple_history.models import HistoricalRecords
import uuid

User = get_user_model()


class JobPosting(models.Model):
    """Job posting model for recruitment process"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('principal', 'Principal'),
        ('executive', 'Executive'),
    ]
    
    # Basic Information
    job_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    department = models.ForeignKey('employees.Department', on_delete=models.CASCADE, related_name='job_postings')
    hiring_manager = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_job_postings')
    
    # Job Details
    description = models.TextField(help_text="Detailed job description")
    responsibilities = models.TextField(help_text="Key responsibilities and duties")
    requirements = models.TextField(help_text="Required qualifications and skills")
    preferred_qualifications = models.TextField(blank=True, null=True, help_text="Preferred but not required qualifications")
    
    # Employment Details
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    
    # Location
    location = models.CharField(max_length=200)
    remote_work_allowed = models.BooleanField(default=False)
    travel_required = models.CharField(max_length=50, blank=True, null=True)
    
    # Posting Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    posted_date = models.DateTimeField(null=True, blank=True)
    closing_date = models.DateTimeField(null=True, blank=True)
    
    # Application Settings
    application_deadline = models.DateTimeField(null=True, blank=True)
    max_applications = models.IntegerField(null=True, blank=True, help_text="Maximum number of applications to accept")
    application_email = models.EmailField(blank=True, null=True)
    application_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    
    # Internal Information
    positions_available = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    priority_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Recruiter Assignment
    assigned_recruiters = models.ManyToManyField(User, blank=True, related_name='assigned_job_postings')
    
    # SEO and Marketing
    keywords = models.TextField(blank=True, null=True, help_text="SEO keywords for job boards")
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.job_id:
            self.job_id = self._generate_job_id()
        super().save(*args, **kwargs)

    def _generate_job_id(self):
        """Generate unique job ID"""
        import random
        import string
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"JOB{year}{random_part}"

    def clean(self):
        super().clean()
        if self.salary_min and self.salary_max and self.salary_min > self.salary_max:
            raise ValidationError("Minimum salary cannot be greater than maximum salary")
        
        if self.application_deadline and self.application_deadline < timezone.now():
            raise ValidationError("Application deadline cannot be in the past")

    @property
    def application_count(self):
        """Get total number of applications"""
        return self.applications.count()

    @property
    def is_open(self):
        """Check if position is open for applications"""
        return self.status == 'active' and (
            not self.application_deadline or self.application_deadline > timezone.now()
        )

    @property
    def salary_range_display(self):
        """Display salary range as formatted string"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+"
        return "Not specified"

    def __str__(self):
        return f"{self.job_id} - {self.title} ({self.department.name})"

    class Meta:
        ordering = ['-created_at']


class Candidate(models.Model):
    """Candidate model for job applicants"""
    
    SOURCE_CHOICES = [
        ('website', 'Company Website'),
        ('job_board', 'Job Board'),
        ('referral', 'Employee Referral'),
        ('linkedin', 'LinkedIn'),
        ('recruitment_agency', 'Recruitment Agency'),
        ('university', 'University/Campus'),
        ('social_media', 'Social Media'),
        ('direct_contact', 'Direct Contact'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    candidate_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Professional Information
    current_position = models.CharField(max_length=100, blank=True, null=True)
    current_company = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    # Contact Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, default='United States')
    
    # Social and Professional Links
    linkedin_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    portfolio_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    github_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    
    # Recruitment Information
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='website')
    referrer = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    # Availability
    availability_date = models.DateField(null=True, blank=True, help_text="When candidate can start")
    salary_expectation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    willing_to_relocate = models.BooleanField(default=False)
    requires_visa_sponsorship = models.BooleanField(default=False)
    
    # Internal Notes
    recruiter_notes = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated tags")
    
    # Status Tracking
    is_active = models.BooleanField(default=True)
    blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.candidate_id:
            self.candidate_id = self._generate_candidate_id()
        super().save(*args, **kwargs)

    def _generate_candidate_id(self):
        """Generate unique candidate ID"""
        import random
        import string
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"CAN{year}{random_part}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def active_applications(self):
        """Get active job applications"""
        return self.applications.filter(status__in=['applied', 'screening', 'interview'])

    @property
    def total_applications(self):
        """Get total number of applications"""
        return self.applications.count()

    def __str__(self):
        return f"{self.candidate_id} - {self.full_name}"

    class Meta:
        ordering = ['-created_at']


class Application(models.Model):
    """Application model linking candidates to job postings"""
    
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Under Screening'),
        ('interview', 'Interview Stage'),
        ('reference_check', 'Reference Check'),
        ('offer_pending', 'Offer Pending'),
        ('offer_extended', 'Offer Extended'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    # Core Relationship
    application_id = models.CharField(max_length=20, unique=True, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    
    # Application Details
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    cover_letter = models.TextField(blank=True, null=True)
    
    # Scoring and Evaluation
    initial_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Initial screening score (1-10)"
    )
    overall_score = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))],
        help_text="Overall application score"
    )
    
    # Process Tracking
    screening_completed = models.BooleanField(default=False)
    screening_notes = models.TextField(blank=True, null=True)
    interview_stage = models.CharField(max_length=50, blank=True, null=True)
    
    # Assignment
    assigned_recruiter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications')
    
    # Decision Information
    rejection_reason = models.TextField(blank=True, null=True)
    rejection_feedback = models.TextField(blank=True, null=True)
    hired_date = models.DateField(null=True, blank=True)
    
    # Internal Notes
    recruiter_notes = models.TextField(blank=True, null=True)
    hiring_manager_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    last_activity_date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = self._generate_application_id()
        super().save(*args, **kwargs)

    def _generate_application_id(self):
        """Generate unique application ID"""
        import random
        import string
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"APP{year}{random_part}"

    @property
    def days_since_applied(self):
        """Calculate days since application"""
        return (timezone.now() - self.applied_date).days

    @property
    def current_stage(self):
        """Get human-readable current stage"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def is_active(self):
        """Check if application is still active"""
        return self.status in ['applied', 'screening', 'interview', 'reference_check', 'offer_pending', 'offer_extended']

    def __str__(self):
        return f"{self.application_id} - {self.candidate.full_name} → {self.job_posting.title}"

    class Meta:
        ordering = ['-applied_date']
        unique_together = ['candidate', 'job_posting']


class CandidateDocument(models.Model):
    """Document storage for candidates (resumes, portfolios, etc.)"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('resume', 'Resume/CV'),
        ('cover_letter', 'Cover Letter'),
        ('portfolio', 'Portfolio'),
        ('certificate', 'Certificate'),
        ('transcript', 'Transcript'),
        ('reference_letter', 'Reference Letter'),
        ('work_sample', 'Work Sample'),
        ('other', 'Other'),
    ]
    
    # Core Information
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='candidate_documents/')
    
    # Metadata
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Access Control
    is_confidential = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Version Control
    version = models.CharField(max_length=10, default='1.0')
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Notes
    description = models.TextField(blank=True, null=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_size_display(self):
        """Display file size in human readable format"""
        if not self.file_size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    def __str__(self):
        return f"{self.candidate.full_name} - {self.title}"

    class Meta:
        ordering = ['-uploaded_at']


class InterviewRound(models.Model):
    """Interview round configuration for job postings"""
    
    ROUND_TYPE_CHOICES = [
        ('phone_screening', 'Phone Screening'),
        ('video_screening', 'Video Screening'),
        ('technical_phone', 'Technical Phone'),
        ('technical_video', 'Technical Video'),
        ('technical_onsite', 'Technical On-site'),
        ('behavioral', 'Behavioral Interview'),
        ('panel', 'Panel Interview'),
        ('presentation', 'Presentation'),
        ('case_study', 'Case Study'),
        ('final', 'Final Interview'),
        ('culture_fit', 'Culture Fit'),
        ('executive', 'Executive Interview'),
    ]
    
    # Core Information
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='interview_rounds')
    name = models.CharField(max_length=100)
    round_type = models.CharField(max_length=20, choices=ROUND_TYPE_CHOICES)
    sequence_order = models.PositiveIntegerField(help_text="Order in the interview process")
    
    # Configuration
    duration_minutes = models.PositiveIntegerField(default=60)
    is_mandatory = models.BooleanField(default=True)
    is_technical = models.BooleanField(default=False)
    
    # Instructions
    description = models.TextField(blank=True, null=True)
    interviewer_instructions = models.TextField(blank=True, null=True)
    candidate_instructions = models.TextField(blank=True, null=True)
    
    # Requirements
    required_interviewers = models.PositiveIntegerField(default=1)
    minimum_score_to_pass = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))]
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.job_posting.title} - Round {self.sequence_order}: {self.name}"

    class Meta:
        ordering = ['job_posting', 'sequence_order']
        unique_together = ['job_posting', 'sequence_order']


class Interview(models.Model):
    """Individual interview scheduling and tracking"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    MEETING_TYPE_CHOICES = [
        ('in_person', 'In Person'),
        ('video_call', 'Video Call'),
        ('phone_call', 'Phone Call'),
        ('virtual_reality', 'Virtual Reality'),
    ]
    
    # Core Information
    interview_id = models.CharField(max_length=20, unique=True, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interview_round = models.ForeignKey(InterviewRound, on_delete=models.CASCADE, related_name='interviews')
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Meeting Details
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='video_call')
    location = models.CharField(max_length=200, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    meeting_password = models.CharField(max_length=50, blank=True, null=True)
    
    # Participants
    primary_interviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='primary_interviews')
    additional_interviewers = models.ManyToManyField(User, blank=True, related_name='additional_interviews')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Notes and Instructions
    preparation_notes = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Candidate Communication
    invitation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    confirmation_received = models.BooleanField(default=False)
    
    # Rescheduling
    reschedule_count = models.PositiveIntegerField(default=0)
    reschedule_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.interview_id:
            self.interview_id = self._generate_interview_id()
        super().save(*args, **kwargs)

    def _generate_interview_id(self):
        """Generate unique interview ID"""
        import random
        import string
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"INT{year}{random_part}"

    def clean(self):
        super().clean()
        if self.scheduled_start and self.scheduled_end and self.scheduled_start >= self.scheduled_end:
            raise ValidationError("Start time must be before end time")

    @property
    def duration_scheduled(self):
        """Get scheduled duration in minutes"""
        if self.scheduled_start and self.scheduled_end:
            return (self.scheduled_end - self.scheduled_start).total_seconds() / 60
        return None

    @property
    def duration_actual(self):
        """Get actual duration in minutes"""
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 60
        return None

    @property
    def is_overdue(self):
        """Check if interview is overdue"""
        return self.status == 'scheduled' and self.scheduled_end < timezone.now()

    def __str__(self):
        return f"{self.interview_id} - {self.application.candidate.full_name} ({self.interview_round.name})"

    class Meta:
        ordering = ['scheduled_start']


class InterviewEvaluation(models.Model):
    """Interview evaluation and scoring"""
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    RECOMMENDATION_CHOICES = [
        ('strong_hire', 'Strong Hire'),
        ('hire', 'Hire'),
        ('no_hire', 'No Hire'),
        ('strong_no_hire', 'Strong No Hire'),
    ]
    
    # Core Information
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name='evaluation')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_evaluations')
    
    # Overall Assessment
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES)
    
    # Detailed Ratings
    technical_skills = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    communication_skills = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    problem_solving = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    cultural_fit = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    enthusiasm = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    experience_relevance = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Detailed Feedback
    strengths = models.TextField(help_text="Candidate's key strengths")
    weaknesses = models.TextField(help_text="Areas for improvement or concerns")
    specific_feedback = models.TextField(help_text="Specific observations and examples")
    
    # Questions and Responses
    questions_asked = models.TextField(blank=True, null=True)
    candidate_questions = models.TextField(blank=True, null=True)
    
    # Additional Assessment
    would_work_with_again = models.BooleanField(null=True, blank=True)
    salary_recommendation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Internal Notes
    private_notes = models.TextField(blank=True, null=True, help_text="Internal notes not shared with candidate")
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    @property
    def average_rating(self):
        """Calculate average rating across all criteria"""
        ratings = [
            self.overall_rating,
            self.communication_skills,
            self.cultural_fit,
            self.enthusiasm,
            self.experience_relevance,
        ]
        
        # Add optional ratings if present
        if self.technical_skills:
            ratings.append(self.technical_skills)
        if self.problem_solving:
            ratings.append(self.problem_solving)
        
        return sum(ratings) / len(ratings)

    def __str__(self):
        return f"Evaluation - {self.interview.application.candidate.full_name} ({self.recommendation})"

    class Meta:
        ordering = ['-submitted_at']


class OfferLetter(models.Model):
    """Job offer management"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent to Candidate'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    OFFER_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
    ]
    
    # Core Information
    offer_id = models.CharField(max_length=20, unique=True, editable=False)
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='offer_letter')
    
    # Offer Details
    position_title = models.CharField(max_length=200)
    department = models.ForeignKey('employees.Department', on_delete=models.CASCADE)
    reporting_manager = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Compensation
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    salary_frequency = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('annually', 'Annually'),
    ], default='annually')
    
    # Additional Compensation
    signing_bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    equity_shares = models.PositiveIntegerField(null=True, blank=True)
    
    # Benefits
    health_insurance = models.BooleanField(default=True)
    dental_insurance = models.BooleanField(default=True)
    vision_insurance = models.BooleanField(default=True)
    retirement_plan = models.BooleanField(default=True)
    paid_time_off = models.PositiveIntegerField(help_text="Days per year", default=20)
    sick_leave = models.PositiveIntegerField(help_text="Days per year", default=10)
    
    # Work Arrangement
    work_location = models.CharField(max_length=200)
    remote_work_allowed = models.BooleanField(default=False)
    start_date = models.DateField()
    
    # Offer Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    offer_expiry_date = models.DateTimeField(help_text="When the offer expires")
    
    # Approval Process
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prepared_offers')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_offers')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Communication
    sent_date = models.DateTimeField(null=True, blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Terms
    probation_period = models.PositiveIntegerField(null=True, blank=True, help_text="Probation period in days")
    notice_period = models.PositiveIntegerField(default=14, help_text="Notice period in days")
    
    # Documents
    offer_letter_document = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    additional_documents = models.ManyToManyField('CandidateDocument', blank=True)
    
    # Notes
    special_conditions = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    
    # Decline Information
    decline_reason = models.TextField(blank=True, null=True)
    counter_offer_details = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.offer_id:
            self.offer_id = self._generate_offer_id()
        super().save(*args, **kwargs)

    def _generate_offer_id(self):
        """Generate unique offer ID"""
        import random
        import string
        year = timezone.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"OFF{year}{random_part}"

    @property
    def is_expired(self):
        """Check if offer has expired"""
        return self.offer_expiry_date < timezone.now()

    @property
    def total_compensation(self):
        """Calculate total compensation including bonuses"""
        total = self.base_salary
        if self.signing_bonus:
            total += self.signing_bonus
        return total

    @property
    def days_until_expiry(self):
        """Calculate days until offer expires"""
        if self.offer_expiry_date:
            return (self.offer_expiry_date.date() - timezone.now().date()).days
        return None

    def __str__(self):
        return f"{self.offer_id} - {self.application.candidate.full_name} ({self.position_title})"

    class Meta:
        ordering = ['-created_at']


class RecruitmentPipeline(models.Model):
    """Pipeline tracking and analytics for recruitment process"""
    
    # Core Information
    job_posting = models.OneToOneField(JobPosting, on_delete=models.CASCADE, related_name='pipeline')
    
    # Pipeline Metrics
    total_applications = models.PositiveIntegerField(default=0)
    applications_screened = models.PositiveIntegerField(default=0)
    candidates_interviewed = models.PositiveIntegerField(default=0)
    offers_extended = models.PositiveIntegerField(default=0)
    offers_accepted = models.PositiveIntegerField(default=0)
    positions_filled = models.PositiveIntegerField(default=0)
    
    # Time Metrics (in days)
    avg_time_to_screen = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    avg_time_to_interview = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    avg_time_to_offer = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    avg_time_to_hire = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Quality Metrics
    offer_acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    interview_to_offer_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    application_to_interview_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Cost Metrics
    cost_per_hire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recruitment_cost_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Source Analysis
    top_candidate_source = models.CharField(max_length=30, blank=True, null=True)
    conversion_rate_by_source = models.JSONField(null=True, blank=True)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()

    def update_metrics(self):
        """Recalculate all pipeline metrics"""
        applications = self.job_posting.applications.all()
        
        # Basic counts
        self.total_applications = applications.count()
        self.applications_screened = applications.filter(screening_completed=True).count()
        self.candidates_interviewed = applications.filter(interviews__isnull=False).distinct().count()
        self.offers_extended = applications.filter(offer_letter__isnull=False).count()
        self.offers_accepted = applications.filter(offer_letter__status='accepted').count()
        self.positions_filled = applications.filter(status='hired').count()
        
        # Calculate conversion rates
        if self.total_applications > 0:
            self.application_to_interview_rate = (self.candidates_interviewed / self.total_applications) * 100
            
        if self.candidates_interviewed > 0:
            self.interview_to_offer_rate = (self.offers_extended / self.candidates_interviewed) * 100
            
        if self.offers_extended > 0:
            self.offer_acceptance_rate = (self.offers_accepted / self.offers_extended) * 100
        
        self.save()

    @property
    def conversion_funnel(self):
        """Get conversion funnel data"""
        return {
            'applications': self.total_applications,
            'screened': self.applications_screened,
            'interviewed': self.candidates_interviewed,
            'offers': self.offers_extended,
            'accepted': self.offers_accepted,
            'hired': self.positions_filled,
        }

    def __str__(self):
        return f"Pipeline - {self.job_posting.title}"

    class Meta:
        ordering = ['-last_updated']
