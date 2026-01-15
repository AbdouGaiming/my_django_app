"""
DRF Serializers for Resources App
"""
from rest_framework import serializers
from .models import Resource, ResourceLink


class ResourceLinkSerializer(serializers.ModelSerializer):
    """Serializer for ResourceLink model."""
    
    class Meta:
        model = ResourceLink
        fields = [
            'id',
            'resource',
            'link_type',
            'url',
            'title',
            'description',
        ]
        read_only_fields = ['id']


class ResourceSerializer(serializers.ModelSerializer):
    """Full serializer for Resource model."""
    
    links = ResourceLinkSerializer(many=True, read_only=True)
    vote_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'description',
            'url',
            'resource_type',
            'difficulty',
            'estimated_duration',
            'language',
            'is_free',
            'quality_score',
            'upvotes',
            'downvotes',
            'vote_score',
            'tags',
            'is_active',
            'links',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'quality_score', 'upvotes', 'downvotes', 'created_at', 'updated_at']
    
    def get_vote_score(self, obj):
        return obj.upvotes - obj.downvotes


class ResourceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for resource lists."""
    
    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'resource_type',
            'difficulty',
            'is_free',
            'quality_score',
            'url',
        ]


class ResourceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating resources."""
    
    class Meta:
        model = Resource
        fields = [
            'title',
            'description',
            'url',
            'resource_type',
            'difficulty',
            'estimated_duration',
            'language',
            'is_free',
            'tags',
        ]


class ResourceVoteSerializer(serializers.Serializer):
    """Serializer for voting on a resource."""
    
    vote = serializers.ChoiceField(choices=['up', 'down'])


class ResourceSearchSerializer(serializers.Serializer):
    """Serializer for resource search parameters."""
    
    query = serializers.CharField(required=False, allow_blank=True)
    resource_type = serializers.ChoiceField(
        choices=Resource.TYPE_CHOICES,
        required=False
    )
    difficulty = serializers.ChoiceField(
        choices=Resource.DIFFICULTY_CHOICES,
        required=False
    )
    is_free = serializers.BooleanField(required=False)
    language = serializers.CharField(required=False, max_length=10)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
