"""
Resource Retriever Service
Searches and ranks resources from catalog for roadmap steps.
"""
from typing import List, Dict
from resources.models import Resource, ResourceLink
from roadmaps.models import RoadmapStep, StepResource


class ResourceRetriever:
    """Retrieves and ranks learning resources for roadmap steps."""
    
    def search(self, query: str, filters: Dict = None) -> List[Resource]:
        """
        Search for resources matching query.
        
        Args:
            query: Search query (topic/keyword)
            filters: Optional filters (difficulty, type, language)
            
        Returns:
            list: Matching resources sorted by quality
        """
        queryset = Resource.objects.filter(is_active=True)
        
        # Text search in title, description, and tags
        queryset = queryset.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(tags__contains=[query])
        )
        
        # Apply filters
        if filters:
            if 'difficulty' in filters:
                queryset = queryset.filter(difficulty=filters['difficulty'])
            if 'resource_type' in filters:
                queryset = queryset.filter(resource_type=filters['resource_type'])
            if 'language' in filters:
                queryset = queryset.filter(language=filters['language'])
            if 'is_free' in filters:
                queryset = queryset.filter(is_free=filters['is_free'])
        
        # Order by quality score
        return queryset.order_by('-quality_score', '-upvotes')[:10]
    
    def rank_for_step(self, resources: List[Resource], step: RoadmapStep, profile_preferences: Dict = None) -> List[Resource]:
        """
        Rank resources by fit for a specific step.
        
        Args:
            resources: List of candidate resources
            step: The roadmap step to match
            profile_preferences: User preferences for resource types
            
        Returns:
            list: Resources sorted by fit score
        """
        scored_resources = []
        
        for resource in resources:
            score = self._calculate_fit_score(resource, step, profile_preferences)
            scored_resources.append((resource, score))
        
        # Sort by score descending
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        
        return [r[0] for r in scored_resources]
    
    def _calculate_fit_score(self, resource: Resource, step: RoadmapStep, preferences: Dict = None) -> float:
        """Calculate how well a resource fits a step."""
        score = 0.0
        
        # Base quality score (0-0.3)
        score += resource.quality_score * 0.3
        
        # Title/topic match (0-0.3)
        step_keywords = step.title.lower().split()
        title_match = sum(1 for kw in step_keywords if kw in resource.title.lower())
        score += min(title_match / len(step_keywords), 1.0) * 0.3
        
        # Difficulty match (0-0.2)
        # Assuming step sequence correlates with difficulty
        if step.sequence <= 2 and resource.difficulty == Resource.BEGINNER:
            score += 0.2
        elif 2 < step.sequence <= 5 and resource.difficulty == Resource.INTERMEDIATE:
            score += 0.2
        elif step.sequence > 5 and resource.difficulty == Resource.ADVANCED:
            score += 0.2
        
        # User preference match (0-0.2)
        if preferences:
            preferred_types = preferences.get('resource_types', [])
            if resource.resource_type in preferred_types:
                score += 0.2
        
        return score
    
    def attach_resources_to_step(self, step: RoadmapStep, resources: List[Resource], max_resources: int = 3) -> None:
        """
        Attach top resources to a roadmap step.
        
        Args:
            step: The roadmap step
            resources: Ranked list of resources
            max_resources: Maximum resources to attach
        """
        for i, resource in enumerate(resources[:max_resources]):
            StepResource.objects.create(
                step=step,
                resource=resource,
                order=i,
                is_required=(i == 0),  # First resource is required
            )
    
    def populate_roadmap_resources(self, roadmap, profile_preferences: Dict = None) -> int:
        """
        Populate all steps in a roadmap with resources.
        
        Args:
            roadmap: The roadmap to populate
            profile_preferences: User preferences
            
        Returns:
            int: Total number of resources attached
        """
        total_attached = 0
        
        for step in roadmap.steps.all():
            # Search for resources matching step topics
            query = step.title
            resources = self.search(query)
            
            if resources:
                ranked = self.rank_for_step(resources, step, profile_preferences)
                self.attach_resources_to_step(step, ranked)
                total_attached += min(len(ranked), 3)
        
        return total_attached


# Import models at module level to avoid circular imports
from django.db import models
