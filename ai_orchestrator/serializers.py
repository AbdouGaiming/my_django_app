"""
DRF Serializers for AI Orchestrator App
"""
from rest_framework import serializers
from .models import AIJob


class AIJobSerializer(serializers.ModelSerializer):
    """Serializer for AIJob model."""
    
    profile_subject = serializers.CharField(source='profile.subject', read_only=True)
    roadmap_title = serializers.CharField(source='roadmap.title', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AIJob
        fields = [
            'id',
            'profile',
            'profile_subject',
            'roadmap',
            'roadmap_title',
            'status',
            'progress',
            'current_stage',
            'error_message',
            'celery_task_id',
            'duration_seconds',
            'created_at',
            'started_at',
            'completed_at',
        ]
        read_only_fields = ['id', 'celery_task_id', 'duration_seconds', 'created_at', 'started_at', 'completed_at']
    
    def get_duration_seconds(self, obj):
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class AIJobCreateSerializer(serializers.Serializer):
    """Serializer for triggering a new AI job."""
    
    profile_id = serializers.UUIDField()
    
    def validate_profile_id(self, value):
        from profiles.models import LearnerProfile
        request = self.context.get('request')
        
        try:
            profile = LearnerProfile.objects.get(id=value, user=request.user)
        except LearnerProfile.DoesNotExist:
            raise serializers.ValidationError("Profile not found")
        
        # Check if there's already a pending job for this profile
        pending = AIJob.objects.filter(
            profile=profile,
            status__in=[AIJob.PENDING, AIJob.RUNNING]
        ).exists()
        
        if pending:
            raise serializers.ValidationError("A job is already running for this profile")
        
        return value


class AIJobStatusSerializer(serializers.Serializer):
    """Serializer for job status updates."""
    
    status = serializers.CharField()
    progress = serializers.IntegerField()
    current_stage = serializers.CharField()
    message = serializers.CharField(required=False)


class GenerateRoadmapRequestSerializer(serializers.Serializer):
    """Serializer for roadmap generation request."""
    
    profile_id = serializers.UUIDField()
    async_mode = serializers.BooleanField(default=True)
    
    def validate_profile_id(self, value):
        from profiles.models import LearnerProfile
        request = self.context.get('request')
        
        try:
            LearnerProfile.objects.get(id=value, user=request.user)
        except LearnerProfile.DoesNotExist:
            raise serializers.ValidationError("Profile not found")
        
        return value


class GenerateRoadmapResponseSerializer(serializers.Serializer):
    """Serializer for roadmap generation response."""
    
    success = serializers.BooleanField()
    job_id = serializers.UUIDField(required=False)
    roadmap_id = serializers.UUIDField(required=False)
    clarifying_questions = serializers.ListField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)


class ClarifyingQuestionResponseSerializer(serializers.Serializer):
    """Serializer for clarifying questions from AI."""
    
    id = serializers.UUIDField()
    question_text = serializers.CharField()
    question_type = serializers.CharField()
    options = serializers.ListField(required=False)
    is_required = serializers.BooleanField()


class PipelineStageSerializer(serializers.Serializer):
    """Serializer for pipeline stage info."""
    
    stage_name = serializers.CharField()
    stage_number = serializers.IntegerField()
    total_stages = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['pending', 'running', 'completed', 'failed'])
    duration_ms = serializers.IntegerField(required=False)
