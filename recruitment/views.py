from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.contrib.auth import get_user_model

from .models import (
    JobPosting, Candidate, Application, CandidateDocument,
    InterviewRound, Interview, InterviewEvaluation, OfferLetter,
    RecruitmentPipeline
)
from .serializers import (
    JobPostingSerializer, CandidateSerializer, ApplicationSerializer,
    CandidateDocumentSerializer, InterviewRoundSerializer, InterviewSerializer,
    InterviewEvaluationSerializer, OfferLetterSerializer, RecruitmentPipelineSerializer,
    JobPostingSimpleSerializer, CandidateSimpleSerializer, ApplicationSimpleSerializer,
    RecruitmentDashboardSerializer, CandidateProfileSerializer, JobPostingDetailSerializer
)

User = get_user_model()


class JobPostingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job postings"""
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department', 'job_type', 'experience_level', 'is_featured']
    search_fields = ['title', 'description', 'requirements', 'keywords']
    ordering_fields = ['created_at', 'posted_date', 'closing_date', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by recruiter if user is assigned
        if hasattr(self.request.user, 'employee_profile'):
            user_assigned = self.request.query_params.get('my_assignments', None)
            if user_assigned == 'true':
                queryset = queryset.filter(assigned_recruiters=self.request.user)
        
        return queryset

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Get applications for this job posting"""
        job_posting = self.get_object()
        applications = job_posting.applications.all()
        
        # Apply filters
        status_filter = request.query_params.get('status', None)
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        serializer = ApplicationSerializer(applications, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pipeline_stats(self, request, pk=None):
        """Get recruitment pipeline statistics"""
        job_posting = self.get_object()
        
        try:
            pipeline = job_posting.pipeline
            serializer = RecruitmentPipelineSerializer(pipeline, context={'request': request})
            return Response(serializer.data)
        except RecruitmentPipeline.DoesNotExist:
            # Create pipeline if doesn't exist
            pipeline = RecruitmentPipeline.objects.create(job_posting=job_posting)
            pipeline.update_metrics()
            serializer = RecruitmentPipelineSerializer(pipeline, context={'request': request})
            return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a job posting"""
        job_posting = self.get_object()
        
        # Create a copy
        job_posting.pk = None
        job_posting.job_id = None
        job_posting.title = f"Copy of {job_posting.title}"
        job_posting.status = 'draft'
        job_posting.posted_date = None
        job_posting.save()
        
        serializer = JobPostingSerializer(job_posting, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a job posting"""
        job_posting = self.get_object()
        
        if job_posting.status == 'draft':
            job_posting.status = 'active'
            job_posting.posted_date = timezone.now()
            job_posting.save()
            
            serializer = JobPostingSerializer(job_posting, context={'request': request})
            return Response(serializer.data)
        
        return Response(
            {'error': 'Job posting is not in draft status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for job postings"""
        queryset = self.get_queryset()
        
        total_active = queryset.filter(status='active').count()
        total_draft = queryset.filter(status='draft').count()
        total_filled = queryset.filter(status='filled').count()
        
        # Recent applications
        recent_apps = Application.objects.filter(
            job_posting__in=queryset,
            applied_date__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        return Response({
            'total_active_jobs': total_active,
            'total_draft_jobs': total_draft,
            'total_filled_jobs': total_filled,
            'applications_this_week': recent_apps,
        })


class CandidateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing candidates"""
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'is_active', 'blacklisted', 'willing_to_relocate', 'requires_visa_sponsorship']
    search_fields = ['first_name', 'last_name', 'email', 'current_position', 'current_company', 'tags']
    ordering_fields = ['created_at', 'first_name', 'last_name', 'years_of_experience']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by experience range
        min_experience = self.request.query_params.get('min_experience', None)
        max_experience = self.request.query_params.get('max_experience', None)
        
        if min_experience:
            queryset = queryset.filter(years_of_experience__gte=min_experience)
        if max_experience:
            queryset = queryset.filter(years_of_experience__lte=max_experience)
        
        return queryset

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get comprehensive candidate profile"""
        candidate = self.get_object()
        
        profile_data = {
            'candidate': CandidateSerializer(candidate, context={'request': request}).data,
            'applications': ApplicationSerializer(
                candidate.applications.all()[:10], 
                many=True, 
                context={'request': request}
            ).data,
            'documents': CandidateDocumentSerializer(
                candidate.documents.all(), 
                many=True, 
                context={'request': request}
            ).data,
            'interviews': InterviewSerializer(
                Interview.objects.filter(application__candidate=candidate)[:10],
                many=True, 
                context={'request': request}
            ).data,
        }
        
        serializer = CandidateProfileSerializer(profile_data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def blacklist(self, request, pk=None):
        """Blacklist a candidate"""
        candidate = self.get_object()
        reason = request.data.get('reason', '')
        
        candidate.blacklisted = True
        candidate.blacklist_reason = reason
        candidate.save()
        
        serializer = CandidateSerializer(candidate, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def whitelist(self, request, pk=None):
        """Remove candidate from blacklist"""
        candidate = self.get_object()
        
        candidate.blacklisted = False
        candidate.blacklist_reason = None
        candidate.save()
        
        serializer = CandidateSerializer(candidate, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sources_stats(self, request):
        """Get candidate source statistics"""
        queryset = self.get_queryset()
        
        sources = queryset.values('source').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(sources)


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications"""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job_posting', 'candidate', 'screening_completed', 'assigned_recruiter']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'job_posting__title']
    ordering_fields = ['applied_date', 'last_activity_date', 'overall_score']
    ordering = ['-applied_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by recruiter assignments
        if hasattr(self.request.user, 'employee_profile'):
            my_applications = self.request.query_params.get('my_assignments', None)
            if my_applications == 'true':
                queryset = queryset.filter(assigned_recruiter=self.request.user)
        
        return queryset

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update application status"""
        application = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status not in dict(Application.STATUS_CHOICES).keys():
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        if notes:
            application.recruiter_notes = notes
        application.save()
        
        serializer = ApplicationSerializer(application, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def schedule_interview(self, request, pk=None):
        """Schedule an interview for this application"""
        application = self.get_object()
        
        # Get interview round
        round_id = request.data.get('interview_round_id')
        if not round_id:
            return Response(
                {'error': 'interview_round_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            interview_round = InterviewRound.objects.get(id=round_id)
        except InterviewRound.DoesNotExist:
            return Response(
                {'error': 'Interview round not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create interview
        interview_data = {
            'application': application.id,
            'interview_round': interview_round.id,
            'scheduled_start': request.data.get('scheduled_start'),
            'scheduled_end': request.data.get('scheduled_end'),
            'primary_interviewer': request.data.get('primary_interviewer'),
            'meeting_type': request.data.get('meeting_type', 'video_call'),
            'preparation_notes': request.data.get('preparation_notes', ''),
        }
        
        interview_serializer = InterviewSerializer(data=interview_data, context={'request': request})
        if interview_serializer.is_valid():
            interview = interview_serializer.save()
            
            # Update application status
            application.status = 'interview'
            application.interview_stage = interview_round.name
            application.save()
            
            return Response(interview_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(interview_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def interviews(self, request, pk=None):
        """Get all interviews for this application"""
        application = self.get_object()
        interviews = application.interviews.all()
        
        serializer = InterviewSerializer(interviews, many=True, context={'request': request})
        return Response(serializer.data)


class CandidateDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing candidate documents"""
    queryset = CandidateDocument.objects.all()
    serializer_class = CandidateDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'candidate', 'is_confidential']
    search_fields = ['title', 'description', 'candidate__first_name', 'candidate__last_name']
    ordering_fields = ['uploaded_at', 'title']
    ordering = ['-uploaded_at']

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of this document"""
        original_doc = self.get_object()
        
        # Create new version
        new_version = CandidateDocument.objects.create(
            candidate=original_doc.candidate,
            document_type=original_doc.document_type,
            title=original_doc.title,
            file=request.FILES.get('file'),
            is_confidential=original_doc.is_confidential,
            uploaded_by=request.user,
            version=request.data.get('version', '2.0'),
            previous_version=original_doc,
            description=request.data.get('description', '')
        )
        
        serializer = CandidateDocumentSerializer(new_version, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InterviewRoundViewSet(viewsets.ModelViewSet):
    """ViewSet for managing interview rounds"""
    queryset = InterviewRound.objects.all()
    serializer_class = InterviewRoundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_posting', 'round_type', 'is_mandatory', 'is_technical', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['sequence_order', 'duration_minutes']
    ordering = ['job_posting', 'sequence_order']


class InterviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing interviews"""
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'meeting_type', 'primary_interviewer', 'application__job_posting']
    search_fields = ['application__candidate__first_name', 'application__candidate__last_name', 'application__job_posting__title']
    ordering_fields = ['scheduled_start', 'scheduled_end', 'created_at']
    ordering = ['-scheduled_start']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by interviewer
        if hasattr(self.request.user, 'employee_profile'):
            my_interviews = self.request.query_params.get('my_interviews', None)
            if my_interviews == 'true':
                queryset = queryset.filter(
                    Q(primary_interviewer=self.request.user) |
                    Q(additional_interviewers=self.request.user)
                ).distinct()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(scheduled_start__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_end__lte=end_date)
        
        return queryset

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an interview"""
        interview = self.get_object()
        
        new_start = request.data.get('scheduled_start')
        new_end = request.data.get('scheduled_end')
        reason = request.data.get('reason', '')
        
        if not new_start or not new_end:
            return Response(
                {'error': 'Both scheduled_start and scheduled_end are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        interview.scheduled_start = new_start
        interview.scheduled_end = new_end
        interview.reschedule_count += 1
        interview.reschedule_reason = reason
        interview.status = 'rescheduled'
        interview.save()
        
        serializer = InterviewSerializer(interview, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_interview(self, request, pk=None):
        """Mark interview as started"""
        interview = self.get_object()
        
        interview.actual_start = timezone.now()
        interview.status = 'in_progress'
        interview.save()
        
        serializer = InterviewSerializer(interview, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_interview(self, request, pk=None):
        """Mark interview as completed"""
        interview = self.get_object()
        
        interview.actual_end = timezone.now()
        interview.status = 'completed'
        interview.save()
        
        serializer = InterviewSerializer(interview, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming interviews"""
        queryset = self.get_queryset()
        
        upcoming = queryset.filter(
            scheduled_start__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('scheduled_start')
        
        serializer = InterviewSerializer(upcoming, many=True, context={'request': request})
        return Response(serializer.data)


class InterviewEvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing interview evaluations"""
    queryset = InterviewEvaluation.objects.all()
    serializer_class = InterviewEvaluationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recommendation', 'evaluator', 'interview__application__job_posting']
    search_fields = ['interview__application__candidate__first_name', 'interview__application__candidate__last_name']
    ordering_fields = ['submitted_at', 'overall_rating']
    ordering = ['-submitted_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by evaluator
        my_evaluations = self.request.query_params.get('my_evaluations', None)
        if my_evaluations == 'true':
            queryset = queryset.filter(evaluator=self.request.user)
        
        return queryset

    @action(detail=False, methods=['get'])
    def rating_distribution(self, request):
        """Get rating distribution statistics"""
        queryset = self.get_queryset()
        
        distribution = queryset.values('overall_rating').annotate(
            count=Count('id')
        ).order_by('overall_rating')
        
        avg_rating = queryset.aggregate(avg_rating=Avg('overall_rating'))
        
        return Response({
            'distribution': distribution,
            'average_rating': avg_rating['avg_rating']
        })


class OfferLetterViewSet(viewsets.ModelViewSet):
    """ViewSet for managing offer letters"""
    queryset = OfferLetter.objects.all()
    serializer_class = OfferLetterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'offer_type', 'department', 'prepared_by', 'approved_by']
    search_fields = ['application__candidate__first_name', 'application__candidate__last_name', 'position_title']
    ordering_fields = ['created_at', 'offer_expiry_date', 'base_salary']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an offer letter"""
        offer = self.get_object()
        
        if offer.status != 'pending_approval':
            return Response(
                {'error': 'Offer is not pending approval'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = 'approved'
        offer.approved_by = request.user
        offer.approved_at = timezone.now()
        offer.save()
        
        serializer = OfferLetterSerializer(offer, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_to_candidate(self, request, pk=None):
        """Send offer letter to candidate"""
        offer = self.get_object()
        
        if offer.status != 'approved':
            return Response(
                {'error': 'Offer must be approved before sending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = 'sent'
        offer.sent_date = timezone.now()
        offer.save()
        
        # Update application status
        offer.application.status = 'offer_extended'
        offer.application.save()
        
        serializer = OfferLetterSerializer(offer, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def candidate_response(self, request, pk=None):
        """Record candidate response to offer"""
        offer = self.get_object()
        response_type = request.data.get('response')  # 'accepted' or 'declined'
        
        if response_type not in ['accepted', 'declined']:
            return Response(
                {'error': 'Response must be either "accepted" or "declined"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offer.status = response_type
        offer.response_date = timezone.now()
        
        if response_type == 'declined':
            offer.decline_reason = request.data.get('decline_reason', '')
            offer.application.status = 'offer_declined'
        else:
            offer.application.status = 'offer_accepted'
        
        offer.save()
        offer.application.save()
        
        serializer = OfferLetterSerializer(offer, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_responses(self, request):
        """Get offers waiting for candidate response"""
        queryset = self.get_queryset()
        
        pending = queryset.filter(
            status='sent',
            offer_expiry_date__gte=timezone.now()
        ).order_by('offer_expiry_date')
        
        serializer = OfferLetterSerializer(pending, many=True, context={'request': request})
        return Response(serializer.data)


class RecruitmentPipelineViewSet(viewsets.ModelViewSet):
    """ViewSet for managing recruitment pipeline analytics"""
    queryset = RecruitmentPipeline.objects.all()
    serializer_class = RecruitmentPipelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['job_posting__status', 'job_posting__department']
    ordering_fields = ['last_updated', 'total_applications', 'avg_time_to_hire']
    ordering = ['-last_updated']

    @action(detail=True, methods=['post'])
    def refresh_metrics(self, request, pk=None):
        """Refresh pipeline metrics"""
        pipeline = self.get_object()
        pipeline.update_metrics()
        
        serializer = RecruitmentPipelineSerializer(pipeline, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get recruitment dashboard data"""
        # Get overall statistics
        total_active_jobs = JobPosting.objects.filter(status='active').count()
        
        # Applications this month
        this_month = timezone.now().replace(day=1)
        total_applications_this_month = Application.objects.filter(
            applied_date__gte=this_month
        ).count()
        
        # Scheduled interviews
        total_interviews_scheduled = Interview.objects.filter(
            scheduled_start__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).count()
        
        # Pending offers
        total_offers_pending = OfferLetter.objects.filter(
            status='sent',
            offer_expiry_date__gte=timezone.now()
        ).count()
        
        # Average time to hire
        pipelines = RecruitmentPipeline.objects.exclude(avg_time_to_hire__isnull=True)
        avg_time_to_hire = pipelines.aggregate(
            avg_time=Avg('avg_time_to_hire')
        )['avg_time'] or 0
        
        # Top performing jobs
        top_jobs = JobPosting.objects.filter(
            status='active'
        ).annotate(
            app_count=Count('applications')
        ).order_by('-app_count')[:5]
        
        # Recent applications
        recent_apps = Application.objects.filter(
            applied_date__gte=timezone.now() - timezone.timedelta(days=7)
        ).order_by('-applied_date')[:10]
        
        dashboard_data = {
            'total_active_jobs': total_active_jobs,
            'total_applications_this_month': total_applications_this_month,
            'total_interviews_scheduled': total_interviews_scheduled,
            'total_offers_pending': total_offers_pending,
            'avg_time_to_hire_days': avg_time_to_hire,
            'top_performing_jobs': JobPostingSimpleSerializer(top_jobs, many=True).data,
            'recent_applications': ApplicationSimpleSerializer(recent_apps, many=True).data,
        }
        
        serializer = RecruitmentDashboardSerializer(dashboard_data)
        return Response(serializer.data)


# Simple ViewSets for dropdown lists and references
class JobPostingSimpleViewSet(viewsets.ReadOnlyModelViewSet):
    """Simple ViewSet for job posting dropdowns"""
    queryset = JobPosting.objects.filter(status__in=['active', 'draft'])
    serializer_class = JobPostingSimpleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'job_id']


class CandidateSimpleViewSet(viewsets.ReadOnlyModelViewSet):
    """Simple ViewSet for candidate dropdowns"""
    queryset = Candidate.objects.filter(is_active=True, blacklisted=False)
    serializer_class = CandidateSimpleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'candidate_id']


class ApplicationSimpleViewSet(viewsets.ReadOnlyModelViewSet):
    """Simple ViewSet for application references"""
    queryset = Application.objects.all()
    serializer_class = ApplicationSimpleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['application_id', 'candidate__first_name', 'candidate__last_name']
