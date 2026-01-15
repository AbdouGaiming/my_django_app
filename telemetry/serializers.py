"""
DRF Serializers for Telemetry App
"""
from rest_framework import serializers
from .models import UserActivity, ProgressSnapshot, ErrorLog


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""
    
    class Meta:
        model = UserActivity
        fields = [
            'id',
            'user',
            'activity_type',
            'description',
            'metadata',
            'ip_address',
            'user_agent',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'ip_address', 'user_agent', 'created_at']


class UserActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer for logging user activity."""
    
    class Meta:
        model = UserActivity
        fields = [
            'activity_type',
            'description',
            'metadata',
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['ip_address'] = self._get_client_ip(request)
        validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        return super().create(validated_data)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class ProgressSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for ProgressSnapshot model."""
    
    roadmap_title = serializers.CharField(source='roadmap.title', read_only=True)
    
    class Meta:
        model = ProgressSnapshot
        fields = [
            'id',
            'user',
            'roadmap',
            'roadmap_title',
            'steps_completed',
            'total_steps',
            'percentage',
            'time_spent_minutes',
            'snapshot_date',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'percentage', 'created_at']


class ProgressSummarySerializer(serializers.Serializer):
    """Serializer for user progress summary."""
    
    total_roadmaps = serializers.IntegerField()
    completed_roadmaps = serializers.IntegerField()
    in_progress_roadmaps = serializers.IntegerField()
    total_steps_completed = serializers.IntegerField()
    total_time_spent_hours = serializers.FloatField()
    current_streak_days = serializers.IntegerField()
    longest_streak_days = serializers.IntegerField()
    recent_activity = UserActivitySerializer(many=True)


class ErrorLogSerializer(serializers.ModelSerializer):
    """Serializer for ErrorLog model."""
    
    class Meta:
        model = ErrorLog
        fields = [
            'id',
            'user',
            'error_type',
            'message',
            'traceback',
            'metadata',
            'resolved',
            'resolved_at',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ErrorLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for logging errors from frontend."""
    
    class Meta:
        model = ErrorLog
        fields = [
            'error_type',
            'message',
            'metadata',
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for analytics dashboard data."""
    
    daily_active_users = serializers.IntegerField()
    weekly_active_users = serializers.IntegerField()
    monthly_active_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    roadmaps_created_today = serializers.IntegerField()
    steps_completed_today = serializers.IntegerField()
    error_count_today = serializers.IntegerField()
    activity_by_type = serializers.DictField()
