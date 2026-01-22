"""
Celery Tasks for AI Orchestrator
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_roadmap_task(self, job_id: str):
    """
    Async task to generate a roadmap for a profile.
    
    Args:
        job_id: UUID string of the AIJob
    """
    from .models import AIJob
    from .services import AIOrchestrator
    
    try:
        job = AIJob.objects.get(id=job_id)
    except AIJob.DoesNotExist:
        logger.error(f"AIJob {job_id} not found")
        return {'error': 'Job not found'}
    
    # Update job status
    job.status = AIJob.RUNNING
    job.started_at = timezone.now()
    job.current_stage = 'initializing'
    job.progress = 0
    job.save()
    
    try:
        profile = job.profile
        orchestrator = AIOrchestrator(profile)
        
        # Stage 1: Normalize
        job.current_stage = 'normalizing'
        job.progress = 10
        job.save()
        
        normalized = orchestrator.normalizer.normalize(profile)
        if not normalized.get('valid', False):
            raise Exception(f"Profile validation failed: {normalized.get('errors', [])}")
        
        # Stage 2: Check uncertainty
        job.current_stage = 'checking_uncertainty'
        job.progress = 25
        job.save()
        
        uncertainty = orchestrator.uncertainty_scorer.calculate_uncertainty(profile)
        
        if uncertainty > 0.5:
            # Need clarifying questions - save them and mark job as needs_clarification
            questions = orchestrator.uncertainty_scorer.generate_questions(
                profile,
                orchestrator.uncertainty_scorer.get_required_questions_count(uncertainty)
            )
            
            # Create ClarifyingQuestion objects
            from profiles.models import ClarifyingQuestion
            for i, q in enumerate(questions):
                ClarifyingQuestion.objects.create(
                    profile=profile,
                    question_text=q['question'],
                    question_type=q.get('type', 'text'),
                    options=q.get('options'),
                    target_field=q.get('field'),
                    is_required=q.get('required', True),
                    order=i,
                )
            
            job.status = AIJob.COMPLETED
            job.current_stage = 'needs_clarification'
            job.progress = 100
            job.completed_at = timezone.now()
            job.save()
            
            return {
                'success': True,
                'stage': 'needs_clarification',
                'questions_created': len(questions),
            }
        
        # Stage 3: Plan roadmap
        job.current_stage = 'planning'
        job.progress = 40
        job.save()
        
        plan = orchestrator.planner.plan(profile)
        
        if not plan.get('steps'):
            raise Exception("Failed to generate roadmap plan")
        
        # Stage 4: Create roadmap
        job.current_stage = 'creating_roadmap'
        job.progress = 60
        job.save()
        
        roadmap = orchestrator.planner.create_roadmap(profile, plan)
        job.roadmap = roadmap
        job.save()
        
        # Stage 5: Attach resources
        job.current_stage = 'attaching_resources'
        job.progress = 80
        job.save()
        
        preferences = orchestrator._get_resource_preferences()
        resources_attached = orchestrator.retriever.populate_roadmap_resources(roadmap, preferences)
        
        # Stage 6: Validate
        job.current_stage = 'validating'
        job.progress = 90
        job.save()
        
        is_valid, errors, warnings = orchestrator.validator.validate_roadmap(roadmap)
        
        # Complete
        job.status = AIJob.COMPLETED
        job.current_stage = 'completed'
        job.progress = 100
        job.completed_at = timezone.now()
        job.save()
        
        logger.info(f"Roadmap generated successfully for job {job_id}")
        
        return {
            'success': True,
            'roadmap_id': str(roadmap.id),
            'steps_created': roadmap.steps.count(),
            'resources_attached': resources_attached,
            'validation_errors': errors,
            'validation_warnings': warnings,
        }
        
    except Exception as e:
        logger.exception(f"Error in roadmap generation for job {job_id}")
        
        job.status = AIJob.FAILED
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
        
        # Retry on transient errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        return {
            'success': False,
            'error': str(e),
        }


@shared_task
def update_resource_quality_scores():
    """
    Periodic task to recalculate resource quality scores.
    Should be scheduled to run daily.
    """
    from resources.models import Resource
    
    updated = 0
    for resource in Resource.objects.filter(is_active=True):
        total_votes = resource.upvotes + resource.downvotes
        if total_votes > 0:
            new_score = resource.upvotes / total_votes
            if resource.quality_score != new_score:
                resource.quality_score = new_score
                resource.save()
                updated += 1
    
    logger.info(f"Updated quality scores for {updated} resources")
    return {'updated': updated}


@shared_task
def create_daily_progress_snapshots():
    """
    Periodic task to create daily progress snapshots for all users.
    Should be scheduled to run at end of day.
    """
    from django.contrib.auth import get_user_model
    from profiles.models import LearnerProfile
    from roadmaps.models import Roadmap
    from telemetry.models import ProgressSnapshot
    
    User = get_user_model()
    today = timezone.now().date()
    created = 0
    
    for profile in LearnerProfile.objects.all():
        roadmaps = Roadmap.objects.filter(profile=profile, status=Roadmap.ACTIVE)
        
        for roadmap in roadmaps:
            steps = roadmap.steps.all()
            total = steps.count()
            completed = steps.filter(is_completed=True).count()
            
            if total > 0:
                ProgressSnapshot.objects.create(
                    user=profile.user,
                    roadmap=roadmap,
                    steps_completed=completed,
                    total_steps=total,
                    snapshot_date=today,
                )
                created += 1
    
    logger.info(f"Created {created} progress snapshots")
    return {'created': created}


@shared_task
def cleanup_old_error_logs(days: int = 30):
    """
    Periodic task to clean up old resolved error logs.
    
    Args:
        days: Delete resolved errors older than this many days
    """
    from telemetry.models import ErrorLog
    
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = ErrorLog.objects.filter(
        resolved=True,
        resolved_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Deleted {deleted} old error logs")
    return {'deleted': deleted}


@shared_task
def send_roadmap_reminder_notifications():
    """
    Periodic task to send reminder notifications for inactive users.
    Should be scheduled daily.
    """
    from django.contrib.auth import get_user_model
    from telemetry.models import UserActivity
    from datetime import timedelta
    
    User = get_user_model()
    
    # Find users who haven't been active in 3+ days but have active roadmaps
    three_days_ago = timezone.now() - timedelta(days=3)
    
    inactive_users = []
    for user in User.objects.filter(is_active=True):
        last_activity = UserActivity.objects.filter(user=user).order_by('-created_at').first()
        
        if last_activity and last_activity.created_at < three_days_ago:
            # Check if they have active roadmaps
            from roadmaps.models import Roadmap
            has_active = Roadmap.objects.filter(
                user=user,
                status=Roadmap.STATUS_ACTIVE
            ).exists()
            
            if has_active:
                inactive_users.append(user)
    
    # TODO: Actually send notifications (email, push, etc.)
    logger.info(f"Found {len(inactive_users)} inactive users to notify")
    
    return {'users_to_notify': len(inactive_users)}
