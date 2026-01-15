"""
DRF ViewSets for Profiles App
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404

from .models import LearnerProfile, ClarifyingQuestion, Answer
from .serializers import (
    LearnerProfileSerializer,
    LearnerProfileCreateSerializer,
    ClarifyingQuestionSerializer,
    AnswerSerializer,
    AnswerSubmitSerializer,
    ProfileProgressSerializer,
)


class LearnerProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for LearnerProfile CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter profiles to only show user's own profiles."""
        return LearnerProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LearnerProfileCreateSerializer
        return LearnerProfileSerializer
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get profile completion progress."""
        profile = self.get_object()
        
        # Calculate completeness
        required_fields = ['subject', 'current_level', 'goals', 'weekly_hours']
        filled_fields = sum(1 for f in required_fields if getattr(profile, f))
        percentage = int((filled_fields / len(required_fields)) * 100)
        missing = [f for f in required_fields if not getattr(profile, f)]
        
        # Check clarifying questions
        unanswered_qs = ClarifyingQuestion.objects.filter(
            profile=profile,
            is_answered=False
        )
        
        data = {
            'completeness_percentage': percentage,
            'missing_fields': missing,
            'has_unanswered_questions': unanswered_qs.exists(),
            'unanswered_count': unanswered_qs.count(),
            'can_generate_roadmap': percentage == 100 and not unanswered_qs.filter(is_required=True).exists(),
        }
        
        serializer = ProfileProgressSerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get clarifying questions for this profile."""
        profile = self.get_object()
        questions = ClarifyingQuestion.objects.filter(profile=profile).order_by('order')
        serializer = ClarifyingQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        """Submit answers to clarifying questions."""
        profile = self.get_object()
        serializer = AnswerSubmitSerializer(data=request.data)
        
        if serializer.is_valid():
            answers_data = serializer.validated_data['answers']
            created_answers = []
            
            for ans in answers_data:
                question = get_object_or_404(
                    ClarifyingQuestion,
                    id=ans['question_id'],
                    profile=profile
                )
                answer = Answer.objects.create(
                    question=question,
                    answer_text=ans.get('answer_text', ''),
                    answer_data=ans.get('answer_data'),
                )
                question.is_answered = True
                question.save()
                created_answers.append(answer)
            
            return Response({
                'success': True,
                'answers_created': len(created_answers)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClarifyingQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for ClarifyingQuestion CRUD operations."""
    
    serializer_class = ClarifyingQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter questions to only show user's profiles' questions."""
        return ClarifyingQuestion.objects.filter(
            profile__user=self.request.user
        )


class AnswerViewSet(viewsets.ModelViewSet):
    """ViewSet for Answer CRUD operations."""
    
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter answers to only show user's answers."""
        return Answer.objects.filter(
            question__profile__user=self.request.user
        )

