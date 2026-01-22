"""
DRF ViewSets for Profiles App
Includes new onboarding flow with language selection and clarifying questions.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import LearnerProfile, ClarifyingQuestion, Answer, AlgerianCompany, SkillDemand
from .serializers import (
    LearnerProfileSerializer,
    LearnerProfileCreateSerializer,
    ClarifyingQuestionSerializer,
    AnswerSerializer,
    AnswerSubmitSerializer,
    ProfileProgressSerializer,
)


# ============ Template Views for Onboarding ============

class ChooseLanguageView(LoginRequiredMixin, View):
    """First step: Choose preferred language."""
    
    def get(self, request):
        return render(request, 'profiles/choose_language.html')
    
    def post(self, request):
        language = request.POST.get('language', 'ar')
        
        # Store in session for the onboarding process
        request.session['onboarding_language'] = language
        
        # Redirect to subject selection
        return redirect('profiles:onboarding_wizard')


class OnboardingWizardView(LoginRequiredMixin, View):
    """Multi-step onboarding wizard."""
    
    SUBJECTS = [
        {'value': 'python', 'icon': '🐍', 'label_ar': 'بايثون', 'label_fr': 'Python', 'label_en': 'Python', 'jobs': 45},
        {'value': 'javascript', 'icon': '⚡', 'label_ar': 'جافاسكريبت', 'label_fr': 'JavaScript', 'label_en': 'JavaScript', 'jobs': 60},
        {'value': 'web_development', 'icon': '🌐', 'label_ar': 'تطوير الويب', 'label_fr': 'Dév. Web', 'label_en': 'Web Dev', 'jobs': 80},
        {'value': 'data_science', 'icon': '📊', 'label_ar': 'علوم البيانات', 'label_fr': 'Data Science', 'label_en': 'Data Science', 'jobs': 15},
        {'value': 'mobile_development', 'icon': '📱', 'label_ar': 'تطوير الموبايل', 'label_fr': 'Dév. Mobile', 'label_en': 'Mobile Dev', 'jobs': 30},
        {'value': 'devops', 'icon': '🔧', 'label_ar': 'DevOps', 'label_fr': 'DevOps', 'label_en': 'DevOps', 'jobs': 12},
    ]
    
    def get_language(self, request):
        return request.session.get('onboarding_language', 'ar')
    
    def get_subjects_for_language(self, language):
        """Get subjects with labels in the correct language."""
        subjects = []
        for subj in self.SUBJECTS:
            lang_key = 'label_ar' if language in ['ar', 'ar_dz'] else f'label_{language}'
            subjects.append({
                'value': subj['value'],
                'icon': subj['icon'],
                'label': subj.get(lang_key, subj['label_en']),
                'jobs': subj['jobs'],
            })
        return subjects
    
    def get_page_title(self, step, language):
        titles = {
            1: {'ar': 'اختر المجال', 'fr': 'Choisir le domaine', 'en': 'Choose Field'},
            2: {'ar': 'أخبرنا عنك', 'fr': 'Parlez-nous de vous', 'en': 'Tell us about you'},
            3: {'ar': 'سوق العمل', 'fr': 'Marché du travail', 'en': 'Job Market'},
        }
        lang = language if language in ['ar', 'fr', 'en'] else 'ar'
        return titles.get(step, {}).get(lang, 'Onboarding')
    
    def get(self, request):
        language = self.get_language(request)
        current_step = int(request.GET.get('step', 1))
        total_steps = 3
        
        # Get or create profile
        profile, created = LearnerProfile.objects.get_or_create(
            user=request.user,
            defaults={'language': language, 'subject': ''}
        )
        
        context = {
            'language': language,
            'current_step': current_step,
            'total_steps': total_steps,
            'progress_percent': int((current_step - 1) / total_steps * 100),
            'page_title': self.get_page_title(current_step, language),
        }
        
        if current_step == 1:
            context['step_type'] = 'subject'
            context['subjects'] = self.get_subjects_for_language(language)
            context['selected_subject'] = profile.subject
            # If current subject is not in predefined list, treat it as custom
            subject_values = {s['value'] for s in self.SUBJECTS}
            context['custom_subject_value'] = profile.subject if profile.subject and profile.subject not in subject_values else ''
        elif current_step == 2:
            context['step_type'] = 'questions'
            # Generate questions based on subject
            from ai_orchestrator.services import QuestionGenerator

            if not profile.subject:
                return redirect(f"{request.path}?step=1")

            # Regenerate questions if subject or language changed
            prefs = profile.preferences or {}
            last_subject = prefs.get('questions_subject')
            last_language = prefs.get('questions_language')
            if last_subject != profile.subject or last_language != language:
                profile.clarifying_questions.all().delete()
            
            if not profile.clarifying_questions.exists():
                generator = QuestionGenerator(profile)
                generator.generate_questions()
            
            questions = profile.clarifying_questions.filter(is_answered=False).order_by('order')
            if not questions.exists():
                # Regenerate questions if all were answered or language/subject changed
                profile.clarifying_questions.all().delete()
                generator = QuestionGenerator(profile)
                generator.generate_questions()
                questions = profile.clarifying_questions.filter(is_answered=False).order_by('order')
            questions = questions[:5]
            # Persist generation context
            prefs['questions_subject'] = profile.subject
            prefs['questions_language'] = language
            profile.preferences = prefs
            profile.save(update_fields=['preferences'])
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    'id': q.id,
                    'text': self._get_question_text(q, language),
                    'type': q.question_type,
                    'options': q.options,
                })
            context['questions'] = formatted_questions
        elif current_step == 3:
            context['step_type'] = 'market'
            # Get market insights
            from ai_orchestrator.services import AlgerianMarketAnalyzer
            
            analyzer = AlgerianMarketAnalyzer(profile)
            context['market_insights'] = analyzer.get_market_insights(profile.subject, language)
            context['matching_companies'] = analyzer.get_matching_companies([profile.subject])[:5]
        
        return render(request, 'profiles/onboarding_wizard.html', context)
    
    def post(self, request):
        language = self.get_language(request)
        current_step = int(request.POST.get('step', 1))
        
        profile = get_object_or_404(LearnerProfile, user=request.user)
        
        if current_step == 1:
            # Save subject selection
            subject = request.POST.get('subject')
            custom_subject = request.POST.get('custom_subject', '').strip()

            if custom_subject:
                subject = custom_subject

            if not subject:
                return redirect(f"{request.path}?step=1")

            if profile.subject != subject:
                profile.clarifying_questions.all().delete()

            profile.subject = subject
            profile.language = language
            profile.save()
            
            return redirect(f"{request.path}?step=2")
            
        elif current_step == 2:
            # Save question answers
            questions = profile.clarifying_questions.filter(is_answered=False)
            
            for q in questions:
                answer_key = f'q_{q.id}'
                
                # Use getlist for multiple choice
                if q.question_type == 'multiple_choice':
                    answer_values = request.POST.getlist(answer_key)
                    answer_value = ", ".join(answer_values) if answer_values else None
                else:
                    answer_value = request.POST.get(answer_key)
                
                if answer_value:
                    Answer.objects.update_or_create(
                        question=q,
                        defaults={
                            'answer_text': answer_value,
                            'answer_data': {'raw': answer_value},
                        }
                    )
                    q.is_answered = True
                    q.save()
                    
                    # Update profile if target field exists
                    if q.target_field and hasattr(profile, q.target_field):
                        # Convert value based on question type
                        final_value = answer_value
                        if q.question_type == 'yes_no':
                            # Handle string 'yes'/'no' to boolean conversion
                            if isinstance(answer_value, str):
                                final_value = (answer_value.lower() == 'yes')
                        elif q.question_type == 'scale' and str(answer_value).isdigit():
                            final_value = int(answer_value)
                        elif q.target_field == 'weekly_hours' and str(answer_value).isdigit():
                            final_value = int(answer_value)
                            
                        setattr(profile, q.target_field, final_value)
            
            profile.questions_answered = True
            profile.save()
            
            return redirect(f"{request.path}?step=3")
            
        elif current_step == 3:
            # Final step - create roadmap
            profile.onboarding_complete = True
            profile.save()
            
            # Generate roadmap
            from ai_orchestrator.services import generate_roadmap_for_profile
            result = generate_roadmap_for_profile(profile)
            
            if result.get('roadmap'):
                # Redirect to the template-based roadmap detail view
                return redirect('roadmap_detail', roadmap_id=result['roadmap'].id)
            else:
                # Redirect to the template-based list of roadmaps
                return redirect('my_roadmaps')
        
        return redirect(request.path)
    
    def _get_question_text(self, question, language):
        """Get question text in the appropriate language."""
        if language == 'fr' and question.question_text_fr:
            return question.question_text_fr
        elif language in ['en'] and question.question_text_en:
            return question.question_text_en
        return question.question_text_ar or question.question_text


# ============ API ViewSets ============

class LearnerProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for LearnerProfile CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter profiles to only show user's own profiles."""
        return LearnerProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LearnerProfileCreateSerializer
        return LearnerProfileSerializer
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get profile completion progress."""
        profile = self.get_object()
        
        # Calculate completeness
        required_fields = ['subject', 'level', 'goals', 'weekly_hours']
        filled_fields = sum(1 for f in required_fields if getattr(profile, f))
        percentage = int((filled_fields / len(required_fields)) * 100)
        missing = [f for f in required_fields if not getattr(profile, f)]
        
        # Check clarifying questions
        unanswered_qs = ClarifyingQuestion.objects.filter(
            learner_profile=profile,
            is_answered=False
        )
        
        data = {
            'completeness_percentage': percentage,
            'missing_fields': missing,
            'has_unanswered_questions': unanswered_qs.exists(),
            'unanswered_count': unanswered_qs.count(),
            'can_generate_roadmap': percentage == 100 and not unanswered_qs.filter(is_required=True).exists(),
        }
        
        serializer = ProfileProgressSerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get clarifying questions for this profile."""
        profile = self.get_object()
        questions = ClarifyingQuestion.objects.filter(learner_profile=profile).order_by('order')
        serializer = ClarifyingQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        """Submit answers to clarifying questions."""
        profile = self.get_object()
        serializer = AnswerSubmitSerializer(data=request.data)
        
        if serializer.is_valid():
            answers_data = serializer.validated_data['answers']
            created_answers = []
            
            for ans in answers_data:
                question = get_object_or_404(
                    ClarifyingQuestion,
                    id=ans['question_id'],
                    learner_profile=profile
                )
                answer = Answer.objects.create(
                    question=question,
                    answer_text=ans.get('answer_text', ''),
                    answer_data=ans.get('answer_data'),
                )
                question.is_answered = True
                question.save()
                created_answers.append(answer)
            
            return Response({
                'success': True,
                'answers_created': len(created_answers)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def market_insights(self, request, pk=None):
        """Get market insights for this profile's subject."""
        profile = self.get_object()
        
        from ai_orchestrator.services import AlgerianMarketAnalyzer
        
        analyzer = AlgerianMarketAnalyzer(profile)
        insights = analyzer.get_market_insights(profile.subject, profile.language)
        companies = analyzer.get_matching_companies([profile.subject])
        
        return Response({
            'insights': insights,
            'companies': companies,
        })


class ClarifyingQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for ClarifyingQuestion CRUD operations."""
    
    serializer_class = ClarifyingQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter questions to only show user's profiles' questions."""
        return ClarifyingQuestion.objects.filter(
            learner_profile__user=self.request.user
        )


class AnswerViewSet(viewsets.ModelViewSet):
    """ViewSet for Answer CRUD operations."""
    
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter answers to only show user's answers."""
        return Answer.objects.filter(
            question__learner_profile__user=self.request.user
        )

