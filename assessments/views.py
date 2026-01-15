"""
DRF ViewSets for Assessments App
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Assessment, AssessmentAttempt
from .serializers import (
    AssessmentSerializer,
    AssessmentListSerializer,
    AssessmentAttemptSerializer,
    AssessmentSubmitSerializer,
    AttemptStartSerializer,
    AttemptResultSerializer,
)


class AssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assessment CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter assessments to user's roadmap steps."""
        return Assessment.objects.filter(
            step__roadmap__profile__user=self.request.user,
            is_active=True
        ).select_related('step')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssessmentListSerializer
        return AssessmentSerializer
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start an assessment attempt."""
        assessment = self.get_object()
        
        # Check max attempts
        attempt_count = AssessmentAttempt.objects.filter(
            assessment=assessment,
            user=request.user
        ).count()
        
        if assessment.max_attempts and attempt_count >= assessment.max_attempts:
            return Response(
                {'error': f'Maximum attempts ({assessment.max_attempts}) reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new attempt
        attempt = AssessmentAttempt.objects.create(
            assessment=assessment,
            user=request.user,
        )
        
        return Response({
            'attempt_id': str(attempt.id),
            'questions': assessment.questions,
            'time_limit': assessment.time_limit,
            'started_at': attempt.started_at,
        })
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit assessment responses."""
        assessment = self.get_object()
        serializer = AssessmentSubmitSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get active attempt
        attempt = AssessmentAttempt.objects.filter(
            assessment=assessment,
            user=request.user,
            completed_at__isnull=True
        ).order_by('-started_at').first()
        
        if not attempt:
            return Response(
                {'error': 'No active attempt found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check time limit
        if assessment.time_limit:
            elapsed = (timezone.now() - attempt.started_at).total_seconds() / 60
            if elapsed > assessment.time_limit:
                attempt.completed_at = timezone.now()
                attempt.score = 0
                attempt.save()
                return Response(
                    {'error': 'Time limit exceeded'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Score the attempt
        responses = serializer.validated_data['responses']
        score, feedback = self._score_responses(assessment, responses)
        
        # Update attempt
        attempt.responses = responses
        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.time_spent = int((attempt.completed_at - attempt.started_at).total_seconds() / 60)
        attempt.save()
        
        # Check if passed
        passed = score >= assessment.passing_score
        attempts_remaining = None
        if assessment.max_attempts:
            attempt_count = AssessmentAttempt.objects.filter(
                assessment=assessment,
                user=request.user
            ).count()
            attempts_remaining = max(0, assessment.max_attempts - attempt_count)
        
        # Log activity
        from telemetry.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            activity_type='assessment_completed',
            description=f"Completed assessment: {assessment.title}",
            metadata={
                'assessment_id': str(assessment.id),
                'score': score,
                'passed': passed
            }
        )
        
        return Response({
            'attempt_id': str(attempt.id),
            'score': score,
            'passed': passed,
            'correct_count': feedback.get('correct_count', 0),
            'total_questions': feedback.get('total_questions', 0),
            'feedback': feedback,
            'can_retry': not passed and (attempts_remaining is None or attempts_remaining > 0),
            'attempts_remaining': attempts_remaining,
        })
    
    def _score_responses(self, assessment, responses):
        """Score responses against correct answers."""
        questions = assessment.questions or []
        correct = 0
        feedback = {}
        
        for q in questions:
            q_id = str(q.get('id', ''))
            user_answer = responses.get(q_id)
            correct_answer = q.get('correct_answer')
            
            if user_answer == correct_answer:
                correct += 1
                feedback[q_id] = {'correct': True}
            else:
                feedback[q_id] = {'correct': False, 'correct_answer': correct_answer}
        
        total = len(questions)
        score = int((correct / total) * 100) if total > 0 else 0
        
        feedback['correct_count'] = correct
        feedback['total_questions'] = total
        
        return score, feedback


class AssessmentAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing assessment attempts (read-only)."""
    
    serializer_class = AssessmentAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AssessmentAttempt.objects.filter(
            user=self.request.user
        ).select_related('assessment')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent attempts."""
        attempts = self.get_queryset().order_by('-started_at')[:10]
        serializer = self.get_serializer(attempts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's assessment statistics."""
        attempts = self.get_queryset()
        completed = attempts.filter(completed_at__isnull=False)
        
        total_attempts = completed.count()
        passed_attempts = completed.filter(score__gte=70).count()  # Assuming 70% is passing
        
        avg_score = 0
        if total_attempts > 0:
            avg_score = sum(a.score or 0 for a in completed) / total_attempts
        
        return Response({
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'failed_attempts': total_attempts - passed_attempts,
            'pass_rate': int((passed_attempts / total_attempts) * 100) if total_attempts else 0,
            'average_score': round(avg_score, 1),
        })

