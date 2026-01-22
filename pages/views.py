from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count

from roadmaps.models import Roadmap, RoadmapStep
from profiles.models import LearnerProfile
from ai_orchestrator.services.llm_service import llm_service


def home_view(request):
    """Render the home page."""
    if request.user.is_authenticated:
        # Check if user has a profile and has completed onboarding
        try:
            profile = LearnerProfile.objects.get(user=request.user)
            if profile.onboarding_complete:
                return redirect('dashboard')
        except LearnerProfile.DoesNotExist:
            pass
        return redirect('profiles:choose_language')
    return render(request, 'home.html')


@login_required
def dashboard_view(request):
    """Render the dashboard page."""
    user = request.user
    
    # NEW: Check onboarding status
    try:
        profile = LearnerProfile.objects.get(user=user)
        if not profile.onboarding_complete:
            return redirect('profiles:choose_language')
    except LearnerProfile.DoesNotExist:
        # Create empty profile to initiate onboarding
        LearnerProfile.objects.create(user=user)
        return redirect('profiles:choose_language')

    roadmaps = Roadmap.objects.filter(user=user).select_related('learner_profile').prefetch_related('steps').order_by('-created_at')[:5]
    
    # Calculate stats
    active_roadmaps_count = Roadmap.objects.filter(user=user, status=Roadmap.STATUS_ACTIVE).count()
    completed_steps = RoadmapStep.objects.filter(roadmap__user=user, status=RoadmapStep.STATUS_COMPLETED)
    completed_steps_count = completed_steps.count()
    hours_invested = completed_steps.aggregate(total=Sum('estimated_hours'))['total'] or 0
    
    # Calculate overall progress
    total_steps = RoadmapStep.objects.filter(roadmap__user=user).count()
    overall_progress = int((completed_steps_count / total_steps) * 100) if total_steps else 0
    
    # Add progress percentage to each roadmap
    for roadmap in roadmaps:
        total = roadmap.steps.count()
        completed = roadmap.steps.filter(status=RoadmapStep.STATUS_COMPLETED).count()
        roadmap.progress_percentage = int((completed / total) * 100) if total else 0
    
    context = {
        'roadmaps': roadmaps,
        'active_roadmaps_count': active_roadmaps_count,
        'completed_steps_count': completed_steps_count,
        'hours_invested': hours_invested,
        'overall_progress': overall_progress,
    }
    return render(request, 'dashboard.html', context)


@login_required
def my_roadmaps_view(request):
    """List all user's roadmaps."""
    user = request.user
    status_filter = request.GET.get('status', 'all')
    
    roadmaps = Roadmap.objects.filter(user=user).prefetch_related('steps').order_by('-created_at')
    
    if status_filter == 'active':
        roadmaps = roadmaps.filter(status=Roadmap.STATUS_ACTIVE)
    elif status_filter == 'completed':
        roadmaps = roadmaps.filter(status=Roadmap.STATUS_COMPLETED)
    elif status_filter == 'archived':
        roadmaps = roadmaps.filter(status=Roadmap.STATUS_ARCHIVED)
    
    # Add progress percentage to each roadmap
    for roadmap in roadmaps:
        total = roadmap.steps.count()
        completed = roadmap.steps.filter(status=RoadmapStep.STATUS_COMPLETED).count()
        roadmap.progress_percentage = int((completed / total) * 100) if total else 0
    
    context = {
        'roadmaps': roadmaps,
        'status': status_filter,
    }
    return render(request, 'roadmaps/my_roadmaps.html', context)


@login_required
def create_roadmap_view(request):
    """Create a new roadmap using AI - Redirect to the new onboarding wizard."""
    try:
        profile = LearnerProfile.objects.get(user=request.user)
        if not profile.onboarding_complete:
            return redirect('profiles:choose_language')
    except LearnerProfile.DoesNotExist:
        return redirect('profiles:choose_language')
        
    # If they completed onboarding but clicked create roadmap, 
    # we can either let them use the old form or restart the wizard.
    # For now, let's just use the wizard for everything new.
    return redirect('profiles:choose_language')

def old_create_roadmap_view(request):
    """Original create roadmap view."""
    if request.method == 'POST':
        try:
            # Get form data
            subject = request.POST.get('subject', '')
            current_level = request.POST.get('current_level', 'beginner')
            goals = request.POST.get('goals', '')
            weekly_hours = int(request.POST.get('weekly_hours', 5))
            deadline = request.POST.get('deadline') or None
            preferred_resources = request.POST.getlist('preferred_resources')
            
            print(f"\n=== Creating roadmap for {subject} ===")
            print(f"Level: {current_level}, Hours/week: {weekly_hours}")
            
            # Create or update learner profile
            profile, created = LearnerProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'subject': subject,
                    'level': current_level,
                    'goals': goals,
                    'weekly_hours': weekly_hours,
                    'deadline': deadline,
                    'preferences': {'preferred_resources': preferred_resources},
                }
            )
            print(f"Profile {'created' if created else 'updated'}: {profile.id}")
            
            # Generate roadmap with AI
            profile_data = {
                'subject': subject,
                'current_level': current_level,
                'goals': goals,
                'weekly_hours': weekly_hours,
                'deadline': str(deadline) if deadline else None,
                'preferred_resources': preferred_resources,
            }
            
            print("Calling LLM service...")
            roadmap_data = llm_service.generate_roadmap(profile_data)
            
            if roadmap_data:
                print(f"Creating roadmap from LLM data: {roadmap_data.get('title')}")
                # Create roadmap from AI response
                roadmap = Roadmap.objects.create(
                    user=request.user,
                    learner_profile=profile,
                    title=roadmap_data.get('title', f'Learning Path: {subject}'),
                    description=roadmap_data.get('description', f'Personalized roadmap for learning {subject}'),
                    total_estimated_hours=roadmap_data.get('estimated_total_hours', 0),
                    status=Roadmap.STATUS_ACTIVE,
                    model_versions={'llm': 'llama-3.3-70b-versatile'},
                )
                print(f"Roadmap created: {roadmap.id}")
                
                # Create steps
                steps_created = 0
                for step_data in roadmap_data.get('steps', []):
                    RoadmapStep.objects.create(
                        roadmap=roadmap,
                        title=step_data.get('title', 'Untitled Step'),
                        description=step_data.get('description', ''),
                        objectives=step_data.get('objectives', []),
                        sequence=step_data.get('sequence', 1),
                        estimated_hours=step_data.get('estimated_hours', 1),
                        status=RoadmapStep.STATUS_ACTIVE,
                    )
                    steps_created += 1
                
                print(f"Created {steps_created} steps")
                messages.success(request, f'Your roadmap has been created with {steps_created} steps!')
                return redirect('roadmap_detail', roadmap_id=roadmap.id)
            else:
                print("LLM failed, using fallback")
                # Fallback to rule-based generation
                from ai_orchestrator.services.roadmap_planner import RoadmapPlanner
                planner = RoadmapPlanner()
                
                normalized_data = {
                    'subject_canonical': subject.lower().replace(' ', '_'),
                    'level_canonical': current_level,
                    'profile_hash': f'{subject}_{current_level}_{weekly_hours}',
                }
                
                steps = planner.plan(profile, normalized_data)
                roadmap = planner.create_roadmap(request.user, profile, steps, normalized_data)
                
                messages.success(request, 'Your roadmap has been created successfully!')
                return redirect('roadmap_detail', roadmap_id=roadmap.id)
        except Exception as e:
            print(f"ERROR in create_roadmap_view: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Failed to create roadmap: {str(e)}')
            return redirect('create_roadmap')
    
    return render(request, 'roadmaps/create_roadmap.html')


from ai_orchestrator.services.market_analyzer import AlgerianMarketAnalyzer
from ai_orchestrator.services.resource_recommender import ResourceRecommender
from profiles.models import AlgerianCompany, JobOpportunity

@login_required
def roadmap_detail_view(request, roadmap_id):
    """View roadmap details with Algerian market insights."""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)
    steps = roadmap.steps.all().order_by('sequence').prefetch_related('step_resources__resource')
    
    # Calculate progress
    total = steps.count()
    completed = steps.filter(status=RoadmapStep.STATUS_COMPLETED).count()
    in_progress = steps.filter(status=RoadmapStep.STATUS_ACTIVE).count()
    progress_percentage = int((completed / total) * 100) if total else 0
    total_duration_hours = sum(s.estimated_hours for s in steps)
    
    # Get user profile for market context
    try:
        profile = LearnerProfile.objects.get(user=request.user)
    except LearnerProfile.DoesNotExist:
        profile = None

    # Get market insights
    market_analyzer = AlgerianMarketAnalyzer()
    market_insights = market_analyzer.get_market_insights(roadmap.title, profile.language if profile else 'ar')
    relevant_companies = market_analyzer.get_matching_companies([roadmap.title])
    
    # Get job opportunities based on matching company names
    company_names = [c.get('name', '') for c in relevant_companies]
    job_opportunities = JobOpportunity.objects.filter(
        company__name__in=company_names,
        is_active=True
    ).select_related('company')[:5]

    # Get recommended local resources
    recommender = ResourceRecommender()
    local_resources = recommender.get_localized_resources(roadmap.title, profile.language if profile else 'ar')

    # Add is_completed property to steps for template
    for step in steps:
        step.is_completed = step.status == RoadmapStep.STATUS_COMPLETED
        step.estimated_duration = int(step.estimated_hours * 60)  # Convert to minutes for template
    
    context = {
        'roadmap': roadmap,
        'steps': steps,
        'progress_percentage': progress_percentage,
        'completed_count': completed,
        'in_progress_count': in_progress,
        'total_count': total,
        'total_duration_hours': total_duration_hours,
        'market_insights': market_insights,
        'job_opportunities': job_opportunities,
        'local_resources': local_resources,
        'profile': profile,
    }
    return render(request, 'roadmaps/roadmap_detail.html', context)


@login_required
def step_detail_view(request, roadmap_id, step_id):
    """View step details."""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)
    step = get_object_or_404(RoadmapStep, id=step_id, roadmap=roadmap)
    
    # Handle step completion toggle
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            step.status = RoadmapStep.STATUS_COMPLETED
            step.save()
            messages.success(request, f'Step "{step.title}" marked as complete!')
        elif action == 'uncomplete':
            step.status = RoadmapStep.STATUS_ACTIVE
            step.save()
            messages.info(request, f'Step "{step.title}" marked as incomplete.')
        return redirect('roadmap_detail', roadmap_id=roadmap_id)
    
    # Get previous and next steps
    prev_step = roadmap.steps.filter(sequence__lt=step.sequence).order_by('-sequence').first()
    next_step = roadmap.steps.filter(sequence__gt=step.sequence).order_by('sequence').first()
    
    # Add is_completed property
    step.is_completed = step.status == RoadmapStep.STATUS_COMPLETED
    step.estimated_duration = int(step.estimated_hours * 60)
    
    context = {
        'roadmap': roadmap,
        'step': step,
        'prev_step': prev_step,
        'next_step': next_step,
        'resources': step.step_resources.all(),
    }
    return render(request, 'roadmaps/step_detail.html', context)


@login_required
def profile_view(request):
    """User profile and settings."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            
        elif action == 'update_preferences':
            # Store preferences (could be saved to a UserPreferences model)
            messages.success(request, 'Preferences updated successfully!')
            
        elif action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully! Please log in again.')
                return redirect('login')
                
        elif action == 'delete_account':
            request.user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')
        
        return redirect('profile')
    
    context = {
        'preferences': {
            'language': 'en',
            'default_weekly_hours': 5,
        }
    }
    return render(request, 'profile.html', context)


