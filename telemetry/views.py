"""
DRF ViewSets for Telemetry App
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta

from .models import UserActivity, ProgressSnapshot, ErrorLog
from .serializers import (
    UserActivitySerializer,
    UserActivityCreateSerializer,
    ProgressSnapshotSerializer,
    ProgressSummarySerializer,
    ErrorLogSerializer,
    ErrorLogCreateSerializer,
    AnalyticsDashboardSerializer,
)


class UserActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for UserActivity operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserActivityCreateSerializer
        return UserActivitySerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activity."""
        activities = self.get_queryset().order_by('-created_at')[:20]
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get activity count by type."""
        counts = self.get_queryset().values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')
        return Response(list(counts))
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get activity timeline for past 30 days."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        activities = self.get_queryset().filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)


class ProgressSnapshotViewSet(viewsets.ModelViewSet):
    """ViewSet for ProgressSnapshot operations."""
    
    serializer_class = ProgressSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProgressSnapshot.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get overall progress summary."""
        from roadmaps.models import Roadmap
        
        user = request.user
        roadmaps = Roadmap.objects.filter(profile__user=user)
        
        total_roadmaps = roadmaps.count()
        completed_roadmaps = roadmaps.filter(status=Roadmap.COMPLETED).count()
        in_progress = roadmaps.filter(status=Roadmap.ACTIVE).count()
        
        # Calculate total steps completed across all roadmaps
        total_steps_completed = 0
        for roadmap in roadmaps:
            total_steps_completed += roadmap.steps.filter(is_completed=True).count()
        
        # Calculate total time spent
        total_time = ProgressSnapshot.objects.filter(user=user).aggregate(
            total=Sum('time_spent_minutes')
        )['total'] or 0
        
        # Calculate streak (days with activity)
        activities = UserActivity.objects.filter(user=user).order_by('-created_at')
        current_streak = self._calculate_streak(activities)
        
        recent_activity = UserActivity.objects.filter(user=user).order_by('-created_at')[:5]
        
        data = {
            'total_roadmaps': total_roadmaps,
            'completed_roadmaps': completed_roadmaps,
            'in_progress_roadmaps': in_progress,
            'total_steps_completed': total_steps_completed,
            'total_time_spent_hours': round(total_time / 60, 1),
            'current_streak_days': current_streak,
            'longest_streak_days': current_streak,  # Simplified
            'recent_activity': UserActivitySerializer(recent_activity, many=True).data,
        }
        
        return Response(data)
    
    def _calculate_streak(self, activities):
        """Calculate current activity streak in days."""
        if not activities.exists():
            return 0
        
        streak = 0
        current_date = timezone.now().date()
        
        activity_dates = set(a.created_at.date() for a in activities)
        
        while current_date in activity_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    @action(detail=False, methods=['post'])
    def snapshot(self, request):
        """Create a progress snapshot for a roadmap."""
        roadmap_id = request.data.get('roadmap_id')
        
        if not roadmap_id:
            return Response(
                {'error': 'roadmap_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from roadmaps.models import Roadmap
        
        try:
            roadmap = Roadmap.objects.get(
                id=roadmap_id,
                profile__user=request.user
            )
        except Roadmap.DoesNotExist:
            return Response(
                {'error': 'Roadmap not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        steps = roadmap.steps.all()
        total_steps = steps.count()
        completed_steps = steps.filter(is_completed=True).count()
        
        snapshot = ProgressSnapshot.objects.create(
            user=request.user,
            roadmap=roadmap,
            steps_completed=completed_steps,
            total_steps=total_steps,
            time_spent_minutes=request.data.get('time_spent_minutes', 0),
            snapshot_date=timezone.now().date(),
        )
        
        serializer = ProgressSnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ErrorLogViewSet(viewsets.ModelViewSet):
    """ViewSet for ErrorLog operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Admins see all, users see their own
        if self.request.user.is_staff:
            return ErrorLog.objects.all()
        return ErrorLog.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ErrorLogCreateSerializer
        return ErrorLogSerializer
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark error as resolved (admin only)."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        error = self.get_object()
        error.resolved = True
        error.resolved_at = timezone.now()
        error.save()
        
        return Response({'success': True, 'resolved_at': error.resolved_at})


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics dashboard (admin only)."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def list(self, request):
        """Get analytics dashboard data."""
        from django.contrib.auth import get_user_model
        from roadmaps.models import Roadmap, RoadmapStep
        
        User = get_user_model()
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Active users
        daily_active = UserActivity.objects.filter(
            created_at__date=today
        ).values('user').distinct().count()
        
        weekly_active = UserActivity.objects.filter(
            created_at__date__gte=week_ago
        ).values('user').distinct().count()
        
        monthly_active = UserActivity.objects.filter(
            created_at__date__gte=month_ago
        ).values('user').distinct().count()
        
        # New users today
        new_users = User.objects.filter(date_joined__date=today).count()
        
        # Roadmaps created today
        roadmaps_today = Roadmap.objects.filter(created_at__date=today).count()
        
        # Steps completed today
        steps_today = RoadmapStep.objects.filter(
            completed_at__date=today
        ).count()
        
        # Error count today
        errors_today = ErrorLog.objects.filter(
            created_at__date=today,
            resolved=False
        ).count()
        
        # Activity by type
        activity_by_type = dict(
            UserActivity.objects.filter(
                created_at__date__gte=week_ago
            ).values('activity_type').annotate(
                count=Count('id')
            ).values_list('activity_type', 'count')
        )
        
        return Response({
            'daily_active_users': daily_active,
            'weekly_active_users': weekly_active,
            'monthly_active_users': monthly_active,
            'new_users_today': new_users,
            'roadmaps_created_today': roadmaps_today,
            'steps_completed_today': steps_today,
            'error_count_today': errors_today,
            'activity_by_type': activity_by_type,
        })

