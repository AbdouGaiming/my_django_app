"""
DRF ViewSets for Roadmaps App
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import Roadmap, RoadmapStep, StepResource
from .serializers import (
    RoadmapSerializer,
    RoadmapListSerializer,
    RoadmapCreateSerializer,
    RoadmapExportSerializer,
    RoadmapStepSerializer,
    RoadmapStepDetailSerializer,
    StepResourceSerializer,
    StepCompletionSerializer,
    BulkStepUpdateSerializer,
)


class RoadmapViewSet(viewsets.ModelViewSet):
    """ViewSet for Roadmap CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter roadmaps to only show user's own roadmaps."""
        return Roadmap.objects.filter(
            profile__user=self.request.user
        ).prefetch_related('steps')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoadmapListSerializer
        elif self.action == 'create':
            return RoadmapCreateSerializer
        return RoadmapSerializer
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export roadmap as JSON."""
        roadmap = self.get_object()
        json_data = roadmap.to_json()
        return Response(json_data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft roadmap."""
        roadmap = self.get_object()
        
        if roadmap.status != Roadmap.DRAFT:
            return Response(
                {'error': 'Only draft roadmaps can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        roadmap.status = Roadmap.ACTIVE
        roadmap.save()
        
        return Response({
            'success': True,
            'status': roadmap.status
        })
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a roadmap."""
        roadmap = self.get_object()
        roadmap.status = Roadmap.ARCHIVED
        roadmap.save()
        
        return Response({
            'success': True,
            'status': roadmap.status
        })
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get roadmap statistics."""
        roadmap = self.get_object()
        steps = roadmap.steps.all()
        
        total_steps = steps.count()
        completed_steps = steps.filter(is_completed=True).count()
        total_duration = sum(s.estimated_duration for s in steps)
        completed_duration = sum(s.estimated_duration for s in steps.filter(is_completed=True))
        
        return Response({
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percentage': int((completed_steps / total_steps) * 100) if total_steps else 0,
            'total_duration_minutes': total_duration,
            'completed_duration_minutes': completed_duration,
            'remaining_duration_minutes': total_duration - completed_duration,
        })


class RoadmapStepViewSet(viewsets.ModelViewSet):
    """ViewSet for RoadmapStep CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter steps to only show user's roadmap steps."""
        return RoadmapStep.objects.filter(
            roadmap__profile__user=self.request.user
        ).select_related('roadmap').prefetch_related('prerequisites', 'resources')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RoadmapStepDetailSerializer
        return RoadmapStepSerializer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark step as completed."""
        step = self.get_object()
        serializer = StepCompletionSerializer(data=request.data)
        
        if serializer.is_valid():
            step.is_completed = serializer.validated_data['is_completed']
            if step.is_completed:
                step.completed_at = timezone.now()
            else:
                step.completed_at = None
            step.save()
            
            # Log activity
            from telemetry.models import UserActivity
            UserActivity.objects.create(
                user=request.user,
                activity_type='step_completed',
                description=f"Completed step: {step.title}",
                metadata={'step_id': str(step.id), 'roadmap_id': str(step.roadmap.id)}
            )
            
            return Response({
                'success': True,
                'is_completed': step.is_completed,
                'completed_at': step.completed_at
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_reorder(self, request):
        """Bulk update step sequences."""
        serializer = BulkStepUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                for item in serializer.validated_data['step_order']:
                    step_id = item['step_id']
                    new_sequence = item['new_sequence']
                    
                    step = get_object_or_404(
                        RoadmapStep,
                        id=step_id,
                        roadmap__profile__user=request.user
                    )
                    step.sequence = new_sequence
                    step.save()
            
            return Response({'success': True})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """Get resources for a step."""
        step = self.get_object()
        step_resources = StepResource.objects.filter(step=step).select_related('resource')
        serializer = StepResourceSerializer(step_resources, many=True)
        return Response(serializer.data)


class StepResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for StepResource operations."""
    
    serializer_class = StepResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StepResource.objects.filter(
            step__roadmap__profile__user=self.request.user
        )

