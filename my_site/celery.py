"""
Celery Configuration for my_site project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_site.settings')

# Create Celery app
app = Celery('my_site')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Update resource quality scores daily at 2 AM
    'update-resource-scores-daily': {
        'task': 'ai_orchestrator.tasks.update_resource_quality_scores',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Create progress snapshots daily at 11:59 PM
    'create-progress-snapshots-daily': {
        'task': 'ai_orchestrator.tasks.create_daily_progress_snapshots',
        'schedule': crontab(hour=23, minute=59),
    },
    
    # Cleanup old error logs weekly on Sunday at 3 AM
    'cleanup-error-logs-weekly': {
        'task': 'ai_orchestrator.tasks.cleanup_old_error_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
        'args': (30,),  # Delete logs older than 30 days
    },
    
    # Send reminder notifications daily at 10 AM
    'send-reminders-daily': {
        'task': 'ai_orchestrator.tasks.send_roadmap_reminder_notifications',
        'schedule': crontab(hour=10, minute=0),
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
