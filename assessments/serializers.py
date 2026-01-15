"""
DRF Serializers for Assessments App
"""
from rest_framework import serializers
from .models import Assessment, AssessmentAttempt


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model."""
    
    step_title = serializers.CharField(source='step.title', read_only=True)
    attempts_count = serializers.IntegerField(source='attempts.count', read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id',
            'step',
            'step_title',
            'title',
            'description',
            'assessment_type',
            'questions',
            'passing_score',
            'max_attempts',
            'time_limit',
            'attempts_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'attempts_count', 'created_at', 'updated_at']


class AssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for assessment lists."""
    
    step_title = serializers.CharField(source='step.title', read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id',
            'title',
            'assessment_type',
            'step_title',
            'passing_score',
            'is_active',
        ]


class AssessmentAttemptSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentAttempt model."""
    
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    passed = serializers.SerializerMethodField()
    
    class Meta:
        model = AssessmentAttempt
        fields = [
            'id',
            'assessment',
            'assessment_title',
            'user',
            'score',
            'passed',
            'responses',
            'started_at',
            'completed_at',
            'time_spent',
        ]
        read_only_fields = ['id', 'user', 'passed', 'started_at', 'time_spent']
    
    def get_passed(self, obj):
        if obj.score is None:
            return None
        return obj.score >= obj.assessment.passing_score


class AssessmentSubmitSerializer(serializers.Serializer):
    """Serializer for submitting assessment responses."""
    
    responses = serializers.DictField(
        help_text="Dict of question_id: answer"
    )
    
    def validate_responses(self, value):
        if not value:
            raise serializers.ValidationError("Responses cannot be empty")
        return value


class AttemptStartSerializer(serializers.Serializer):
    """Serializer for starting an assessment attempt."""
    
    assessment_id = serializers.UUIDField()


class AttemptResultSerializer(serializers.Serializer):
    """Serializer for assessment attempt results."""
    
    attempt_id = serializers.UUIDField()
    score = serializers.IntegerField()
    passed = serializers.BooleanField()
    correct_count = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    feedback = serializers.DictField(required=False)
    can_retry = serializers.BooleanField()
    attempts_remaining = serializers.IntegerField()
