"""
URL configuration for my_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from pages.views import (
    home_view, 
    dashboard_view, 
    my_roadmaps_view, 
    create_roadmap_view,
    roadmap_detail_view,
    step_detail_view,
    profile_view,
)

# Suppress Chrome DevTools 404
def devtools_view(request):
    return HttpResponse(status=204)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Template-based auth (no namespace for simple URL names)
    path('accounts/', include('accounts.urls')),
    
    # Dashboard and main pages
    path('dashboard/', dashboard_view, name='dashboard'),
    path('roadmaps/', my_roadmaps_view, name='my_roadmaps'),
    path('roadmaps/create/', create_roadmap_view, name='create_roadmap'),
    path('roadmaps/<int:roadmap_id>/', roadmap_detail_view, name='roadmap_detail'),
    path('roadmaps/<int:roadmap_id>/steps/<int:step_id>/', step_detail_view, name='step_detail'),
    path('profile/', profile_view, name='profile'),
    
    # API endpoints
    path('api/profiles/', include('profiles.urls', namespace='profiles')),
    path('api/roadmaps/', include('roadmaps.urls', namespace='roadmaps')),
    path('api/resources/', include('resources.urls', namespace='resources')),
    path('api/assessments/', include('assessments.urls', namespace='assessments')),
    path('api/telemetry/', include('telemetry.urls', namespace='telemetry')),
    path('api/ai/', include('ai_orchestrator.urls', namespace='ai_orchestrator')),
    
    # Suppress Chrome DevTools warning
    path('.well-known/appspecific/com.chrome.devtools.json', devtools_view),
    
    # Home
    path('', home_view, name='home'),
]
