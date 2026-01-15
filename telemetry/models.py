from django.db import models
from django.conf import settings


class UserActivity(models.Model):
    """Tracks user activity for analytics and personalization."""
    
    ACTION_VIEW = 'view'
    ACTION_START = 'start'
    ACTION_COMPLETE = 'complete'
    ACTION_SKIP = 'skip'
    ACTION_BOOKMARK = 'bookmark'
    ACTION_RATE = 'rate'
    
    ACTION_CHOICES = [
        (ACTION_VIEW, 'View'),
        (ACTION_START, 'Start'),
        (ACTION_COMPLETE, 'Complete'),
        (ACTION_SKIP, 'Skip'),
        (ACTION_BOOKMARK, 'Bookmark'),
        (ACTION_RATE, 'Rate'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Generic content reference
    content_type = models.CharField(max_length=50, help_text="e.g., roadmap, step, resource")
    content_id = models.PositiveIntegerField()
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    
    # Session tracking
    session_id = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.action} on {self.content_type}:{self.content_id}"


class ProgressSnapshot(models.Model):
    """Daily snapshot of user progress for trend analysis."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_snapshots'
    )
    
    roadmap = models.ForeignKey(
        'roadmaps.Roadmap',
        on_delete=models.CASCADE,
        related_name='progress_snapshots'
    )
    
    date = models.DateField()
    
    # Progress metrics
    steps_completed = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=0)
    hours_spent = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'roadmap', 'date']
    
    def __str__(self):
        return f"{self.user.email} - {self.roadmap.title} - {self.date}"


class ErrorLog(models.Model):
    """Logs errors for debugging and monitoring."""
    
    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_ERROR = 'error'
    SEVERITY_CRITICAL = 'critical'
    
    SEVERITY_CHOICES = [
        (SEVERITY_INFO, 'Info'),
        (SEVERITY_WARNING, 'Warning'),
        (SEVERITY_ERROR, 'Error'),
        (SEVERITY_CRITICAL, 'Critical'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_logs'
    )
    
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_ERROR)
    message = models.TextField()
    traceback = models.TextField(blank=True)
    
    # Context
    request_id = models.CharField(max_length=64, blank=True)
    endpoint = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.severity}] {self.message[:50]}..."
