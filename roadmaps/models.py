from django.db import models
from django.conf import settings
import json
import hashlib
from datetime import datetime


class Roadmap(models.Model):
    """Learning roadmap generated for a user."""
    
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ARCHIVED, 'Archived'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmaps'
    )
    
    learner_profile = models.ForeignKey(
        'profiles.LearnerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roadmaps'
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    
    # Time estimates
    total_estimated_hours = models.FloatField(default=0)
    completed_hours = models.FloatField(default=0)
    
    # Generation metadata
    schema_version = models.CharField(max_length=10, default='1.0')
    model_versions = models.JSONField(default=dict, blank=True, help_text="LLM and embedding model versions used")
    input_profile_hash = models.CharField(max_length=64, blank=True, help_text="Hash of input profile for reproducibility")
    
    # User customization flags
    is_pinned = models.BooleanField(default=False, help_text="User pinned this roadmap")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def calculate_progress(self):
        """Calculate completion percentage."""
        total_steps = self.steps.count()
        if total_steps == 0:
            return 0
        completed_steps = self.steps.filter(status=RoadmapStep.STATUS_COMPLETED).count()
        return round((completed_steps / total_steps) * 100, 1)
    
    def to_json(self):
        """Export roadmap as versioned JSON."""
        return {
            "schema_version": self.schema_version,
            "generated_at": datetime.now().isoformat(),
            "model_versions": self.model_versions,
            "input_profile_hash": self.input_profile_hash,
            "roadmap": {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "status": self.status,
                "total_estimated_hours": self.total_estimated_hours,
                "progress_percent": self.calculate_progress(),
                "steps": [step.to_json() for step in self.steps.all()],
            }
        }


class RoadmapStep(models.Model):
    """Individual step in a learning roadmap."""
    
    STATUS_LOCKED = 'locked'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_SKIPPED = 'skipped'
    
    STATUS_CHOICES = [
        (STATUS_LOCKED, 'Locked'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_SKIPPED, 'Skipped'),
    ]
    
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    objectives = models.JSONField(default=list, blank=True, help_text="Learning objectives for this step")
    
    # Sequencing
    sequence = models.PositiveIntegerField(default=0, help_text="Order in the roadmap")
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='unlocks'
    )
    
    # Time tracking
    estimated_hours = models.FloatField(default=1.0)
    actual_hours = models.FloatField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_LOCKED)
    
    # User customization
    is_pinned = models.BooleanField(default=False, help_text="User pinned this step (won't regenerate)")
    user_notes = models.TextField(blank=True)
    
    # Mastery check
    mastery_check_passed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sequence']
        unique_together = ['roadmap', 'sequence']
    
    def __str__(self):
        return f"Step {self.sequence}: {self.title}"
    
    def to_json(self):
        """Export step as JSON."""
        return {
            "id": self.id,
            "sequence": self.sequence,
            "title": self.title,
            "description": self.description,
            "objectives": self.objectives,
            "estimated_hours": self.estimated_hours,
            "status": self.status,
            "is_pinned": self.is_pinned,
            "resources": [
                {
                    "id": sr.resource.id,
                    "title": sr.resource.title,
                    "type": sr.resource.resource_type,
                    "url": sr.resource.links.filter(is_primary=True).first().url if sr.resource.links.exists() else None,
                }
                for sr in self.step_resources.all()
            ]
        }


class StepResource(models.Model):
    """Links resources to roadmap steps with ordering."""
    
    step = models.ForeignKey(
        RoadmapStep,
        on_delete=models.CASCADE,
        related_name='step_resources'
    )
    resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.CASCADE,
        related_name='step_usages'
    )
    
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False, help_text="User pinned this resource")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['step', 'resource']
    
    def __str__(self):
        return f"{self.resource.title} for Step {self.step.sequence}"
