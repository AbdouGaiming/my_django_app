from django.contrib import admin
from .models import (
    LearnerProfile, 
    ClarifyingQuestion, 
    Answer, 
    AlgerianCompany, 
    JobOpportunity, 
    SkillDemand
)


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'level', 'language', 'wilaya', 'onboarding_complete']
    list_filter = ['language', 'level', 'wilaya', 'onboarding_complete', 'seeking_job']
    search_fields = ['user__email', 'subject', 'goals']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ClarifyingQuestion)
class ClarifyingQuestionAdmin(admin.ModelAdmin):
    list_display = ['learner_profile', 'question_type', 'category', 'order', 'is_answered']
    list_filter = ['question_type', 'category', 'is_answered', 'is_required']
    search_fields = ['question_text', 'question_text_ar']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer_text', 'created_at']
    search_fields = ['answer_text']


@admin.register(AlgerianCompany)
class AlgerianCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_type', 'industry', 'wilaya', 'is_hiring', 'remote_friendly']
    list_filter = ['company_type', 'industry', 'wilaya', 'is_hiring', 'remote_friendly']
    search_fields = ['name', 'name_ar', 'description']


@admin.register(JobOpportunity)
class JobOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'experience_level', 'wilaya', 'is_active']
    list_filter = ['job_type', 'experience_level', 'wilaya', 'is_active', 'is_remote']
    search_fields = ['title', 'title_ar', 'description']


@admin.register(SkillDemand)
class SkillDemandAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'demand_score', 'growth_trend', 'job_count', 'category']
    list_filter = ['growth_trend', 'category']
    search_fields = ['skill_name', 'skill_name_ar']
