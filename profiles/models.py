from django.db import models
from django.conf import settings


class LearnerProfile(models.Model):
    """Extended profile for learners with learning preferences and goals."""
    
    # Level choices
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'
    
    LEVEL_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (EXPERT, 'Expert'),
    ]
    
    # Age range choices
    AGE_UNDER_18 = 'under_18'
    AGE_18_24 = '18_24'
    AGE_25_34 = '25_34'
    AGE_35_44 = '35_44'
    AGE_45_54 = '45_54'
    AGE_55_PLUS = '55_plus'
    
    AGE_CHOICES = [
        (AGE_UNDER_18, 'Under 18'),
        (AGE_18_24, '18-24'),
        (AGE_25_34, '25-34'),
        (AGE_35_44, '35-44'),
        (AGE_45_54, '45-54'),
        (AGE_55_PLUS, '55+'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learner_profile'
    )
    
    # Learning subject and level
    subject = models.CharField(max_length=200, help_text="Main subject to learn")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=BEGINNER)
    
    # Goals and preferences
    goals = models.TextField(blank=True, help_text="Learning goals and objectives")
    preferences = models.JSONField(default=dict, blank=True, help_text="Learning preferences as JSON")
    
    # Time constraints
    weekly_hours = models.PositiveIntegerField(default=5, help_text="Hours available per week")
    deadline = models.DateField(null=True, blank=True, help_text="Target completion date")
    
    # Demographics
    language = models.CharField(max_length=10, default='en', help_text="Preferred language code")
    age_range = models.CharField(max_length=20, choices=AGE_CHOICES, blank=True)
    
    # Onboarding status
    onboarding_complete = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Learner Profile'
        verbose_name_plural = 'Learner Profiles'
    
    def __str__(self):
        return f"LearnerProfile for {self.user.email} - {self.subject}"


class ClarifyingQuestion(models.Model):
    """Stores clarifying questions asked during onboarding."""
    
    QUESTION_TYPES = [
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Free Text'),
        ('scale', 'Scale (1-10)'),
    ]
    
    learner_profile = models.ForeignKey(
        LearnerProfile,
        on_delete=models.CASCADE,
        related_name='clarifying_questions'
    )
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='text')
    options = models.JSONField(default=list, blank=True, help_text="Options for choice questions")
    
    # Order in which question was asked
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Answer(models.Model):
    """Stores answers to clarifying questions."""
    
    question = models.OneToOneField(
        ClarifyingQuestion,
        on_delete=models.CASCADE,
        related_name='answer'
    )
    
    answer_text = models.TextField()
    confidence = models.FloatField(default=1.0, help_text="Confidence score 0-1")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer to Q{self.question.order}: {self.answer_text[:50]}..."
