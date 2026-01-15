from django.db import models
from django.conf import settings


class Assessment(models.Model):
    """Mastery check assessment for a roadmap step."""
    
    TYPE_QUIZ = 'quiz'
    TYPE_PROJECT = 'project'
    TYPE_SELF_ASSESSMENT = 'self_assessment'
    
    TYPE_CHOICES = [
        (TYPE_QUIZ, 'Quiz'),
        (TYPE_PROJECT, 'Project'),
        (TYPE_SELF_ASSESSMENT, 'Self Assessment'),
    ]
    
    step = models.ForeignKey(
        'roadmaps.RoadmapStep',
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SELF_ASSESSMENT)
    
    # Passing criteria
    passing_score = models.PositiveIntegerField(default=70, help_text="Minimum score to pass (0-100)")
    
    # Questions/tasks stored as JSON
    content = models.JSONField(default=list, help_text="Quiz questions or project requirements")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.assessment_type})"


class AssessmentAttempt(models.Model):
    """User's attempt at an assessment."""
    
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_PASSED = 'passed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PASSED, 'Passed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_attempts'
    )
    
    # Responses stored as JSON
    responses = models.JSONField(default=dict)
    
    score = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.assessment.title} ({self.status})"
