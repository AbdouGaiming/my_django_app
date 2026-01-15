"""
URL Configuration for Telemetry App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserActivityViewSet,
    ProgressSnapshotViewSet,
    ErrorLogViewSet,
    AnalyticsViewSet,
)

router = DefaultRouter()
router.register(r'activities', UserActivityViewSet, basename='useractivity')
router.register(r'progress', ProgressSnapshotViewSet, basename='progresssnapshot')
router.register(r'errors', ErrorLogViewSet, basename='errorlog')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

app_name = 'telemetry'

urlpatterns = [
    path('', include(router.urls)),
]
