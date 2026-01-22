"""
DRF Serializers for Roadmaps App
"""
from rest_framework import serializers
from .models import Roadmap, RoadmapStep, StepResource


class StepResourceSerializer(serializers.ModelSerializer):
    """Serializer for StepResource model."""
    
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    resource_type = serializers.CharField(source='resource.resource_type', read_only=True)
    resource_url = serializers.URLField(source='resource.url', read_only=True)
    
    class Meta:
        model = StepResource
        fields = [
            'id',
            'resource',
            'resource_title',
            'resource_type',
            'resource_url',
            'order',
            'is_required',
        ]
        read_only_fields = ['id']


class RoadmapStepSerializer(serializers.ModelSerializer):
    """Serializer for RoadmapStep model."""
    
    resources = StepResourceSerializer(source='step_resources', many=True, read_only=True)
    prerequisite_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=RoadmapStep.objects.all(),
        source='prerequisites',
        required=False
    )
    is_completed = serializers.SerializerMethodField()
    estimated_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = RoadmapStep
        fields = [
            'id',
            'roadmap',
            'sequence',
            'title',
            'description',
            'estimated_hours',
            'estimated_duration',
            'objectives',
            'status',
            'is_completed',
            'prerequisites',
            'prerequisite_ids',
            'resources',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'roadmap', 'resources', 'created_at', 'updated_at']
    
    def get_is_completed(self, obj):
        return obj.status == RoadmapStep.STATUS_COMPLETED
    
    def get_estimated_duration(self, obj):
        return int(obj.estimated_hours * 60)


class RoadmapStepDetailSerializer(RoadmapStepSerializer):
    """Detailed serializer with full prerequisite info."""
    
    prerequisites = RoadmapStepSerializer(many=True, read_only=True)


class RoadmapListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for roadmap lists."""
    
    step_count = serializers.IntegerField(source='steps.count', read_only=True)
    completed_steps = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Roadmap
        fields = [
            'id',
            'title',
            'status',
            'step_count',
            'completed_steps',
            'progress_percentage',
            'created_at',
        ]
    
    def get_completed_steps(self, obj):
        return obj.steps.filter(status=RoadmapStep.STATUS_COMPLETED).count()
    
    def get_progress_percentage(self, obj):
        total = obj.steps.count()
        if total == 0:
            return 0
        completed = obj.steps.filter(status=RoadmapStep.STATUS_COMPLETED).count()
        return int((completed / total) * 100)


class RoadmapSerializer(serializers.ModelSerializer):
    """Full serializer for Roadmap model."""
    
    steps = RoadmapStepSerializer(many=True, read_only=True)
    profile_subject = serializers.CharField(source='learner_profile.subject', read_only=True)
    
    class Meta:
        model = Roadmap
        fields = [
            'id',
            'learner_profile',
            'profile_subject',
            'title',
            'description',
            'status',
            'schema_version',
            'steps',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'learner_profile', 'schema_version', 'steps', 'created_at', 'updated_at']


class RoadmapCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating roadmap (triggered by AI pipeline)."""
    
    class Meta:
        model = Roadmap
        fields = ['title', 'description']
    
    def create(self, validated_data):
        request = self.context.get('request')
        profile_id = self.context.get('profile_id')
        
        from profiles.models import LearnerProfile
        profile = LearnerProfile.objects.get(id=profile_id, user=request.user)
        
        validated_data['learner_profile'] = profile
        validated_data['user'] = request.user
        return super().create(validated_data)


class RoadmapExportSerializer(serializers.Serializer):
    """Serializer for roadmap JSON export."""
    
    version = serializers.CharField()
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    steps = serializers.ListField()


class StepCompletionSerializer(serializers.Serializer):
    """Serializer for marking step as complete."""
    
    is_completed = serializers.BooleanField()
    mastery_score = serializers.IntegerField(required=False, min_value=0, max_value=100)
    notes = serializers.CharField(required=False, allow_blank=True)


class BulkStepUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating step sequence."""
    
    step_order = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of {step_id, new_sequence}"
    )
