"""
URL Configuration for Assessments App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, AssessmentAttemptViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'attempts', AssessmentAttemptViewSet, basename='assessmentattempt')

app_name = 'assessments'

urlpatterns = [
    path('', include(router.urls)),
]
