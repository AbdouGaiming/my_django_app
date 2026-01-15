"""
URL Configuration for Roadmaps App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoadmapViewSet, RoadmapStepViewSet, StepResourceViewSet

router = DefaultRouter()
router.register(r'roadmaps', RoadmapViewSet, basename='roadmap')
router.register(r'steps', RoadmapStepViewSet, basename='roadmapstep')
router.register(r'step-resources', StepResourceViewSet, basename='stepresource')

app_name = 'roadmaps'

urlpatterns = [
    path('', include(router.urls)),
]
