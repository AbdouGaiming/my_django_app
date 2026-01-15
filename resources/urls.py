"""
URL Configuration for Resources App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet, ResourceLinkViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'links', ResourceLinkViewSet, basename='resourcelink')

app_name = 'resources'

urlpatterns = [
    path('', include(router.urls)),
]
