from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

# DRF Router
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'student-profiles', views.StudentProfileViewSet, basename='studentprofile')
router.register(r'teacher-profiles', views.TeacherProfileViewSet, basename='teacherprofile')
router.register(r'admin-profiles', views.AdminProfileViewSet, basename='adminprofile')

# No app_name for template URLs - they use simple names like 'login', 'logout', 'signup'

urlpatterns = [
    # Template-based views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # DRF API views
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
    
    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
