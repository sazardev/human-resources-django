from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date


class Department(models.Model):
    """Department model for organizing employees"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    """Employee model for human resources management"""
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Employment Information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    employment_status = models.CharField(
        max_length=20, 
        choices=EMPLOYMENT_STATUS_CHOICES, 
        default='active'
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Address Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, default='Mexico')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def latest_performance_review(self):
        """Get the most recent performance review"""
        return self.performance_reviews.order_by('-review_date').first()
    
    @property
    def average_performance_rating(self):
        """Calculate average performance rating from all reviews"""
        reviews = self.performance_reviews.all()
        if reviews:
            total_rating = sum(review.overall_rating for review in reviews)
            return round(total_rating / len(reviews), 2)
        return None
    
    @property
    def active_goals(self):
        """Get active performance goals"""
        return self.performance_goals.filter(
            status__in=['in_progress', 'pending']
        ).order_by('-created_at')

    class Meta:
        ordering = ['employee_id']


class PerformanceReview(models.Model):
    """Performance review model for tracking employee evaluations"""
    
    REVIEW_TYPE_CHOICES = [
        ('annual', 'Annual Review'),
        ('semi_annual', 'Semi-Annual Review'),
        ('quarterly', 'Quarterly Review'),
        ('probationary', 'Probationary Review'),
        ('project_based', 'Project-Based Review'),
    ]
    
    RATING_CHOICES = [
        (1, 'Needs Improvement'),
        (2, 'Below Expectations'), 
        (3, 'Meets Expectations'),
        (4, 'Exceeds Expectations'),
        (5, 'Outstanding'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    review_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Ratings
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    technical_skills = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Technical competency and job-specific skills"
    )
    communication = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Verbal, written, and interpersonal communication"
    )
    teamwork = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Collaboration and team contribution"
    )
    leadership = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Leadership qualities and initiative",
        null=True, blank=True
    )
    problem_solving = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Analytical thinking and problem resolution"
    )
    adaptability = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Flexibility and adaptation to change"
    )
    
    # Comments and Feedback
    strengths = models.TextField(help_text="Employee's key strengths and accomplishments")
    areas_for_improvement = models.TextField(help_text="Areas where employee can improve")
    goals_for_next_period = models.TextField(help_text="Goals and objectives for next review period")
    reviewer_comments = models.TextField(blank=True, null=True, help_text="Additional reviewer comments")
    employee_comments = models.TextField(blank=True, null=True, help_text="Employee's response and comments")
    
    # Recommendations
    promotion_recommendation = models.BooleanField(default=False)
    salary_increase_recommendation = models.BooleanField(default=False)
    training_recommendations = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_review_type_display()} ({self.review_date})"
    
    @property
    def average_rating(self):
        """Calculate average rating excluding leadership if null"""
        ratings = [
            self.technical_skills,
            self.communication,
            self.teamwork,
            self.problem_solving,
            self.adaptability
        ]
        if self.leadership:
            ratings.append(self.leadership)
        
        return round(sum(ratings) / len(ratings), 2)
    
    class Meta:
        ordering = ['-review_date']
        unique_together = [['employee', 'review_period_start', 'review_period_end']]


class PerformanceGoal(models.Model):
    """Performance goals and objectives for employees"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    CATEGORY_CHOICES = [
        ('performance', 'Performance'),
        ('skill_development', 'Skill Development'),
        ('leadership', 'Leadership'),
        ('project', 'Project'),
        ('behavior', 'Behavior'),
        ('career', 'Career Development'),
    ]
    
    # Basic Information
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Timeline
    start_date = models.DateField(default=date.today)
    target_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    # Status and Progress
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )
    
    # Success Criteria and Metrics
    success_criteria = models.TextField(help_text="Define what success looks like")
    measurable_outcomes = models.TextField(
        blank=True, null=True,
        help_text="Specific, measurable outcomes or KPIs"
    )
      # Comments and Notes
    progress_notes = models.TextField(blank=True, null=True, help_text="Progress notes and updates")
    completion_notes = models.TextField(blank=True, null=True, help_text="Notes upon completion")
    
    # Review Information
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='created_goals',
        help_text="Who created this goal"
    )
    review = models.ForeignKey(
        PerformanceReview, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='goals',
        help_text="Associated performance review"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if goal is overdue"""
        return (
            self.status not in ['completed', 'cancelled'] and 
            self.target_date < date.today()
        )
    
    @property
    def days_remaining(self):
        """Calculate days remaining until target date"""
        if self.status in ['completed', 'cancelled']:
            return 0
        delta = self.target_date - date.today()
        return delta.days
    
    def save(self, *args, **kwargs):
        # Auto-update status based on progress and dates
        if self.progress_percentage == 100 and self.status != 'completed':
            self.status = 'completed'
            if not self.completed_date:
                self.completed_date = date.today()
        elif self.is_overdue and self.status not in ['completed', 'cancelled']:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class PerformanceNote(models.Model):
    """Notes and observations about employee performance"""
    
    NOTE_TYPE_CHOICES = [
        ('observation', 'Observation'),
        ('achievement', 'Achievement'),
        ('concern', 'Concern'),
        ('feedback', 'Feedback'),
        ('recognition', 'Recognition'),
        ('coaching', 'Coaching'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_notes')
    note_type = models.CharField(max_length=15, choices=NOTE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_observed = models.DateField(default=date.today)
    is_private = models.BooleanField(
        default=False,
        help_text="Private notes are only visible to HR and managers"
    )
    
    # Optional associations
    goal = models.ForeignKey(
        PerformanceGoal, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='notes',
        help_text="Associated performance goal"
    )
    review = models.ForeignKey(
        PerformanceReview, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='notes',
        help_text="Associated performance review"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title} ({self.get_note_type_display()})"
    
    class Meta:
        ordering = ['-date_observed']
