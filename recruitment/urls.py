from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()

# Main ViewSets
router.register(r'job-postings', views.JobPostingViewSet, basename='jobposting')
router.register(r'candidates', views.CandidateViewSet, basename='candidate')
router.register(r'applications', views.ApplicationViewSet, basename='application')
router.register(r'documents', views.CandidateDocumentViewSet, basename='candidatedocument')
router.register(r'interview-rounds', views.InterviewRoundViewSet, basename='interviewround')
router.register(r'interviews', views.InterviewViewSet, basename='interview')
router.register(r'evaluations', views.InterviewEvaluationViewSet, basename='interviewevaluation')
router.register(r'offers', views.OfferLetterViewSet, basename='offerletter')
router.register(r'pipeline', views.RecruitmentPipelineViewSet, basename='recruitmentpipeline')

# Simple ViewSets for dropdowns
router.register(r'simple/job-postings', views.JobPostingSimpleViewSet, basename='jobposting-simple')
router.register(r'simple/candidates', views.CandidateSimpleViewSet, basename='candidate-simple')
router.register(r'simple/applications', views.ApplicationSimpleViewSet, basename='application-simple')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
