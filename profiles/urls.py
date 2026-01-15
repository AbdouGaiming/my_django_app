"""
URL Configuration for Profiles App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearnerProfileViewSet, ClarifyingQuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'profiles', LearnerProfileViewSet, basename='learnerprofile')
router.register(r'questions', ClarifyingQuestionViewSet, basename='clarifyingquestion')
router.register(r'answers', AnswerViewSet, basename='answer')

app_name = 'profiles'

urlpatterns = [
    path('', include(router.urls)),
]
