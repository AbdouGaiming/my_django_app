from django.db import models
from django.conf import settings


class AIJob(models.Model):
    """Tracks AI pipeline jobs (async processing)."""
    
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    JOB_GENERATE_ROADMAP = 'generate_roadmap'
    JOB_REGENERATE_ROADMAP = 'regenerate_roadmap'
    JOB_FETCH_RESOURCES = 'fetch_resources'
    JOB_GENERATE_QUESTIONS = 'generate_questions'
    
    JOB_TYPE_CHOICES = [
        (JOB_GENERATE_ROADMAP, 'Generate Roadmap'),
        (JOB_REGENERATE_ROADMAP, 'Regenerate Roadmap'),
        (JOB_FETCH_RESOURCES, 'Fetch Resources'),
        (JOB_GENERATE_QUESTIONS, 'Generate Questions'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_jobs'
    )
    
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, blank=True)
    
    # Progress tracking (0-100)
    progress = models.PositiveIntegerField(default=0)
    progress_message = models.CharField(max_length=200, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    # Celery task tracking
    celery_task_id = models.CharField(max_length=64, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Job'
        verbose_name_plural = 'AI Jobs'
    
    def __str__(self):
        return f"{self.job_type} for {self.user.email} ({self.status})"
