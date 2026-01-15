"""
URL Configuration for AI Orchestrator App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIJobViewSet,
    GenerateRoadmapView,
    EstimateTimeView,
    ValidateRoadmapView,
)

router = DefaultRouter()
router.register(r'jobs', AIJobViewSet, basename='aijob')

app_name = 'ai_orchestrator'

urlpatterns = [
    path('', include(router.urls)),
    path('generate/', GenerateRoadmapView.as_view(), name='generate-roadmap'),
    path('estimate/', EstimateTimeView.as_view(), name='estimate-time'),
    path('validate/', ValidateRoadmapView.as_view(), name='validate-roadmap'),
]
