"""
URL Configuration for Profiles App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LearnerProfileViewSet, 
    ClarifyingQuestionViewSet, 
    AnswerViewSet,
    ChooseLanguageView,
    OnboardingWizardView,
)

router = DefaultRouter()
router.register(r'profiles', LearnerProfileViewSet, basename='learnerprofile')
router.register(r'questions', ClarifyingQuestionViewSet, basename='clarifyingquestion')
router.register(r'answers', AnswerViewSet, basename='answer')

app_name = 'profiles'

urlpatterns = [
    # Template views for onboarding wizard
    path('start/', ChooseLanguageView.as_view(), name='choose_language'),
    path('start/onboarding/', ChooseLanguageView.as_view(), name='start_onboarding'),
    path('onboarding/', OnboardingWizardView.as_view(), name='onboarding_wizard'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
