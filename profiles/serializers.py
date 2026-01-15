"""
DRF Serializers for Profiles App
"""
from rest_framework import serializers
from .models import LearnerProfile, ClarifyingQuestion, Answer


class LearnerProfileSerializer(serializers.ModelSerializer):
    """Serializer for LearnerProfile model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = LearnerProfile
        fields = [
            'id',
            'user',
            'user_email',
            'subject',
            'current_level',
            'goals',
            'preferences',
            'weekly_hours',
            'deadline',
            'language',
            'age_range',
            'is_complete',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'user_email', 'is_complete', 'created_at', 'updated_at']


class LearnerProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new LearnerProfile."""
    
    class Meta:
        model = LearnerProfile
        fields = [
            'subject',
            'current_level',
            'goals',
            'preferences',
            'weekly_hours',
            'deadline',
            'language',
            'age_range',
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class ClarifyingQuestionSerializer(serializers.ModelSerializer):
    """Serializer for ClarifyingQuestion model."""
    
    class Meta:
        model = ClarifyingQuestion
        fields = [
            'id',
            'profile',
            'question_text',
            'question_type',
            'options',
            'target_field',
            'is_required',
            'order',
            'is_answered',
            'created_at',
        ]
        read_only_fields = ['id', 'is_answered', 'created_at']


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model."""
    
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            'id',
            'question',
            'question_text',
            'answer_text',
            'answer_data',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AnswerSubmitSerializer(serializers.Serializer):
    """Serializer for submitting multiple answers at once."""
    
    answers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of {question_id, answer_text/answer_data}"
    )
    
    def validate_answers(self, value):
        for answer in value:
            if 'question_id' not in answer:
                raise serializers.ValidationError("Each answer must have question_id")
            if 'answer_text' not in answer and 'answer_data' not in answer:
                raise serializers.ValidationError("Each answer must have answer_text or answer_data")
        return value


class ProfileProgressSerializer(serializers.Serializer):
    """Serializer for profile completion progress."""
    
    completeness_percentage = serializers.IntegerField()
    missing_fields = serializers.ListField(child=serializers.CharField())
    has_unanswered_questions = serializers.BooleanField()
    unanswered_count = serializers.IntegerField()
    can_generate_roadmap = serializers.BooleanField()
