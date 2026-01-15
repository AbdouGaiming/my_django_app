"""
AI Pipeline Orchestrator
Coordinates the full AI pipeline for roadmap generation.
"""
from typing import Dict, Optional
from django.db import transaction

from .profile_normalizer import ProfileNormalizer
from .uncertainty_scorer import UncertaintyScorer
from .roadmap_planner import RoadmapPlanner
from .resource_retriever import ResourceRetriever
from .validator import Validator


class AIOrchestrator:
    """
    Main orchestrator for the AI pipeline.
    
    Pipeline steps:
    1. Normalize profile data
    2. Score uncertainty and generate clarifying questions if needed
    3. Plan roadmap structure
    4. Retrieve and attach resources
    5. Validate final roadmap
    """
    
    def __init__(self, profile):
        self.profile = profile
        self.normalizer = ProfileNormalizer()
        self.uncertainty_scorer = UncertaintyScorer()
        self.planner = RoadmapPlanner()
        self.retriever = ResourceRetriever()
        self.validator = Validator()
        
        self.errors = []
        self.warnings = []
    
    def run_full_pipeline(self) -> Dict:
        """
        Execute the complete AI pipeline.
        
        Returns:
            dict: Pipeline result with roadmap or clarifying questions
        """
        result = {
            'success': False,
            'stage': None,
            'roadmap': None,
            'clarifying_questions': None,
            'errors': [],
            'warnings': [],
        }
        
        try:
            # Stage 1: Normalize profile
            result['stage'] = 'normalize'
            normalized = self.normalizer.normalize(self.profile)
            if not normalized.get('valid', False):
                result['errors'] = normalized.get('errors', [])
                return result
            
            # Stage 2: Check uncertainty
            result['stage'] = 'uncertainty'
            uncertainty = self.uncertainty_scorer.calculate_uncertainty(self.profile)
            
            if uncertainty > 0.5:
                # Need clarifying questions
                questions = self.uncertainty_scorer.generate_questions(
                    self.profile,
                    self.uncertainty_scorer.get_required_questions_count(uncertainty)
                )
                result['clarifying_questions'] = questions
                result['success'] = True
                result['stage'] = 'needs_clarification'
                return result
            
            # Stage 3: Plan roadmap
            result['stage'] = 'planning'
            plan = self.planner.plan(self.profile)
            
            if not plan.get('steps'):
                result['errors'].append("Failed to generate roadmap plan")
                return result
            
            # Stage 4: Create roadmap with steps
            result['stage'] = 'creating'
            with transaction.atomic():
                roadmap = self.planner.create_roadmap(self.profile, plan)
                
                # Stage 5: Attach resources
                result['stage'] = 'resources'
                preferences = self._get_resource_preferences()
                self.retriever.populate_roadmap_resources(roadmap, preferences)
                
                # Stage 6: Validate
                result['stage'] = 'validation'
                is_valid, errors, warnings = self.validator.validate_roadmap(roadmap)
                
                if not is_valid:
                    result['errors'] = errors
                    result['warnings'] = warnings
                    # Don't fail on validation errors, just report
                
                result['roadmap'] = roadmap
                result['warnings'].extend(warnings)
                result['success'] = True
                result['stage'] = 'complete'
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def _get_resource_preferences(self) -> Dict:
        """Extract resource preferences from profile."""
        preferences = {}
        
        if hasattr(self.profile, 'preferences') and self.profile.preferences:
            prefs = self.profile.preferences
            if 'resource_types' in prefs:
                preferences['resource_types'] = prefs['resource_types']
        
        return preferences
    
    def process_clarifying_answers(self, answers: list) -> 'AIOrchestrator':
        """
        Process answers to clarifying questions and update profile.
        
        Args:
            answers: List of Answer model instances
            
        Returns:
            self: For method chaining
        """
        from profiles.models import Answer
        
        for answer in answers:
            question = answer.question
            
            # Update profile based on answer field
            if question.target_field and hasattr(self.profile, question.target_field):
                setattr(self.profile, question.target_field, answer.answer_text)
        
        self.profile.save()
        return self
    
    def generate_roadmap_json(self, roadmap) -> Dict:
        """
        Export roadmap as JSON for external use.
        
        Args:
            roadmap: Roadmap model instance
            
        Returns:
            dict: JSON-serializable roadmap data
        """
        return roadmap.to_json()
    
    def estimate_completion_time(self) -> Dict:
        """
        Estimate how long the learning journey will take.
        
        Returns:
            dict: Time estimates in various units
        """
        if not hasattr(self.profile, 'weekly_hours'):
            return {'error': 'Profile missing weekly_hours'}
        
        # Get plan without creating roadmap
        plan = self.planner.plan(self.profile)
        total_minutes = plan.get('total_duration', 0)
        
        weekly_minutes = self.profile.weekly_hours * 60
        
        weeks = total_minutes / weekly_minutes if weekly_minutes else 0
        
        return {
            'total_hours': total_minutes / 60,
            'weeks': round(weeks, 1),
            'months': round(weeks / 4, 1),
            'weekly_commitment': self.profile.weekly_hours,
        }


def generate_roadmap_for_profile(profile) -> Dict:
    """
    Convenience function to generate roadmap for a profile.
    
    Args:
        profile: LearnerProfile instance
        
    Returns:
        dict: Pipeline result
    """
    orchestrator = AIOrchestrator(profile)
    return orchestrator.run_full_pipeline()
