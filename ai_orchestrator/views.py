"""
DRF ViewSets for AI Orchestrator App
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIJob
from .serializers import (
    AIJobSerializer,
    AIJobCreateSerializer,
    AIJobStatusSerializer,
    GenerateRoadmapRequestSerializer,
    GenerateRoadmapResponseSerializer,
    ClarifyingQuestionResponseSerializer,
)
from .services import AIOrchestrator, generate_roadmap_for_profile


class AIJobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI Job operations (read-only)."""
    
    serializer_class = AIJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AIJob.objects.filter(profile__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get job status."""
        job = self.get_object()
        return Response({
            'status': job.status,
            'progress': job.progress,
            'current_stage': job.current_stage,
            'message': job.error_message if job.status == AIJob.FAILED else None,
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a pending/running job."""
        job = self.get_object()
        
        if job.status not in [AIJob.PENDING, AIJob.RUNNING]:
            return Response(
                {'error': 'Can only cancel pending or running jobs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel Celery task if exists
        if job.celery_task_id:
            from celery.result import AsyncResult
            AsyncResult(job.celery_task_id).revoke()
        
        job.status = AIJob.CANCELLED
        job.save()
        
        return Response({'success': True, 'status': job.status})


class GenerateRoadmapView(APIView):
    """API view for generating roadmaps."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate a roadmap for a profile."""
        serializer = GenerateRoadmapRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        profile_id = serializer.validated_data['profile_id']
        async_mode = serializer.validated_data.get('async_mode', True)
        
        from profiles.models import LearnerProfile
        profile = LearnerProfile.objects.get(id=profile_id, user=request.user)
        
        if async_mode:
            # Create async job
            job = AIJob.objects.create(
                profile=profile,
                status=AIJob.PENDING,
                current_stage='queued',
            )
            
            # Trigger Celery task
            from .tasks import generate_roadmap_task
            task = generate_roadmap_task.delay(str(job.id))
            
            job.celery_task_id = task.id
            job.save()
            
            return Response({
                'success': True,
                'job_id': str(job.id),
                'message': 'Roadmap generation started'
            }, status=status.HTTP_202_ACCEPTED)
        else:
            # Synchronous generation
            result = generate_roadmap_for_profile(profile)
            
            if result.get('clarifying_questions'):
                # Need more info
                return Response({
                    'success': True,
                    'clarifying_questions': result['clarifying_questions'],
                    'errors': result.get('errors', []),
                })
            
            if result.get('roadmap'):
                return Response({
                    'success': True,
                    'roadmap_id': str(result['roadmap'].id),
                    'errors': result.get('errors', []),
                    'warnings': result.get('warnings', []),
                })
            
            return Response({
                'success': False,
                'errors': result.get('errors', ['Unknown error']),
            }, status=status.HTTP_400_BAD_REQUEST)


class EstimateTimeView(APIView):
    """API view for estimating completion time."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Estimate time to complete learning journey."""
        profile_id = request.data.get('profile_id')
        
        if not profile_id:
            return Response(
                {'error': 'profile_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from profiles.models import LearnerProfile
        
        try:
            profile = LearnerProfile.objects.get(
                id=profile_id,
                user=request.user
            )
        except LearnerProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        orchestrator = AIOrchestrator(profile)
        estimate = orchestrator.estimate_completion_time()
        
        return Response(estimate)


class ValidateRoadmapView(APIView):
    """API view for validating a roadmap."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Validate a roadmap structure."""
        roadmap_id = request.data.get('roadmap_id')
        
        if not roadmap_id:
            return Response(
                {'error': 'roadmap_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from roadmaps.models import Roadmap
        from .services import Validator
        
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
        
        validator = Validator()
        is_valid, errors, warnings = validator.validate_roadmap(roadmap)
        
        return Response({
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
        })

