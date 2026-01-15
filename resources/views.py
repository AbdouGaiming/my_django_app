"""
DRF ViewSets for Resources App
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Resource, ResourceLink
from .serializers import (
    ResourceSerializer,
    ResourceListSerializer,
    ResourceCreateSerializer,
    ResourceLinkSerializer,
    ResourceVoteSerializer,
    ResourceSearchSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for all, write only for admins."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for Resource CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['quality_score', 'created_at', 'title']
    ordering = ['-quality_score']
    
    def get_queryset(self):
        """Return active resources with optional filtering."""
        queryset = Resource.objects.filter(is_active=True)
        
        # Filter by resource_type
        resource_type = self.request.query_params.get('type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by is_free
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ResourceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ResourceCreateSerializer
        return ResourceSerializer
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a resource."""
        resource = self.get_object()
        serializer = ResourceVoteSerializer(data=request.data)
        
        if serializer.is_valid():
            vote = serializer.validated_data['vote']
            
            if vote == 'up':
                resource.upvotes += 1
            else:
                resource.downvotes += 1
            
            # Recalculate quality score
            total_votes = resource.upvotes + resource.downvotes
            if total_votes > 0:
                resource.quality_score = resource.upvotes / total_votes
            resource.save()
            
            return Response({
                'success': True,
                'upvotes': resource.upvotes,
                'downvotes': resource.downvotes,
                'quality_score': resource.quality_score
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for resources."""
        serializer = ResourceSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            queryset = Resource.objects.filter(is_active=True)
            data = serializer.validated_data
            
            if data.get('query'):
                query = data['query']
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            
            if data.get('resource_type'):
                queryset = queryset.filter(resource_type=data['resource_type'])
            
            if data.get('difficulty'):
                queryset = queryset.filter(difficulty=data['difficulty'])
            
            if data.get('is_free') is not None:
                queryset = queryset.filter(is_free=data['is_free'])
            
            if data.get('language'):
                queryset = queryset.filter(language=data['language'])
            
            if data.get('tags'):
                for tag in data['tags']:
                    queryset = queryset.filter(tags__contains=[tag])
            
            queryset = queryset.order_by('-quality_score')[:50]
            
            result_serializer = ResourceListSerializer(queryset, many=True)
            return Response({
                'count': len(result_serializer.data),
                'results': result_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def links(self, request, pk=None):
        """Get additional links for a resource."""
        resource = self.get_object()
        links = ResourceLink.objects.filter(resource=resource)
        serializer = ResourceLinkSerializer(links, many=True)
        return Response(serializer.data)


class ResourceLinkViewSet(viewsets.ModelViewSet):
    """ViewSet for ResourceLink operations."""
    
    serializer_class = ResourceLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        return ResourceLink.objects.filter(resource__is_active=True)

