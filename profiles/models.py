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
    
    # Language choices - Algeria focused
    ARABIC = 'ar'
    FRENCH = 'fr'
    ENGLISH = 'en'
    DARIJA = 'ar_dz'  # Algerian Arabic dialect
    
    LANGUAGE_CHOICES = [
        (ARABIC, 'العربية (Arabic)'),
        (FRENCH, 'Français (French)'),
        (ENGLISH, 'English'),
        (DARIJA, 'الدارجة الجزائرية (Algerian Dialect)'),
    ]
    
    # Age range choices
    AGE_UNDER_18 = 'under_18'
    AGE_18_24 = '18_24'
    AGE_25_34 = '25_34'
    AGE_35_44 = '35_44'
    AGE_45_54 = '45_54'
    AGE_55_PLUS = '55_plus'
    
    AGE_CHOICES = [
        (AGE_UNDER_18, 'Under 18 / أقل من 18'),
        (AGE_18_24, '18-24'),
        (AGE_25_34, '25-34'),
        (AGE_35_44, '35-44'),
        (AGE_45_54, '45-54'),
        (AGE_55_PLUS, '55+ / +55'),
    ]
    
    # Algerian regions (Wilayas)
    WILAYA_CHOICES = [
        ('alger', 'Alger'),
        ('oran', 'Oran'),
        ('constantine', 'Constantine'),
        ('annaba', 'Annaba'),
        ('setif', 'Sétif'),
        ('blida', 'Blida'),
        ('batna', 'Batna'),
        ('djelfa', 'Djelfa'),
        ('tlemcen', 'Tlemcen'),
        ('bejaia', 'Béjaïa'),
        ('tizi_ouzou', 'Tizi Ouzou'),
        ('ouargla', 'Ouargla'),
        ('other', 'Other / أخرى'),
    ]
    
    # Education level
    EDUCATION_CHOICES = [
        ('primary', 'Primary School / ابتدائي'),
        ('middle', 'Middle School / متوسط'),
        ('secondary', 'Secondary School / ثانوي'),
        ('bac', 'Baccalauréat / باكالوريا'),
        ('licence', 'Licence (L1-L3)'),
        ('master', 'Master (M1-M2)'),
        ('doctorate', 'Doctorate / دكتوراه'),
        ('self_taught', 'Self-taught / تعلم ذاتي'),
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
    
    # Language and Demographics - Algeria focused
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default=ARABIC, help_text="Preferred language")
    age_range = models.CharField(max_length=20, choices=AGE_CHOICES, blank=True)
    wilaya = models.CharField(max_length=50, choices=WILAYA_CHOICES, blank=True, help_text="Region in Algeria")
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True, help_text="Education level")
    
    # Employment status for job matching
    is_student = models.BooleanField(default=False, help_text="Currently a student")
    is_employed = models.BooleanField(default=False, help_text="Currently employed")
    seeking_job = models.BooleanField(default=True, help_text="Looking for job opportunities")
    
    # Onboarding status
    onboarding_complete = models.BooleanField(default=False)
    questions_answered = models.BooleanField(default=False, help_text="Has answered initial questions")
    
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
        ('yes_no', 'Yes/No'),
    ]
    
    # Categories for organizing questions
    CATEGORY_CHOICES = [
        ('background', 'Background / الخلفية'),
        ('goals', 'Goals / الأهداف'),
        ('preferences', 'Preferences / التفضيلات'),
        ('availability', 'Availability / التوفر'),
        ('job_market', 'Job Market / سوق العمل'),
    ]
    
    learner_profile = models.ForeignKey(
        LearnerProfile,
        on_delete=models.CASCADE,
        related_name='clarifying_questions'
    )
    
    # Multilingual question text
    question_text = models.TextField(help_text="Question in user's preferred language")
    question_text_ar = models.TextField(blank=True, help_text="Arabic version")
    question_text_fr = models.TextField(blank=True, help_text="French version")
    question_text_en = models.TextField(blank=True, help_text="English version")
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='background')
    options = models.JSONField(default=list, blank=True, help_text="Options for choice questions (multilingual)")
    
    # Metadata
    is_required = models.BooleanField(default=True, help_text="Must answer to proceed")
    is_answered = models.BooleanField(default=False)
    target_field = models.CharField(max_length=50, blank=True, null=True, help_text="Profile field to update with answer")
    
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
    answer_data = models.JSONField(default=dict, blank=True, help_text="Structured answer data")
    confidence = models.FloatField(default=1.0, help_text="Confidence score 0-1")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer to Q{self.question.order}: {self.answer_text[:50]}..."


class AlgerianCompany(models.Model):
    """Companies in Algeria that hire tech talent."""
    
    COMPANY_TYPES = [
        ('startup', 'Startup / شركة ناشئة'),
        ('sme', 'SME / مؤسسة صغيرة ومتوسطة'),
        ('enterprise', 'Large Enterprise / شركة كبيرة'),
        ('government', 'Government / حكومي'),
        ('multinational', 'Multinational / متعددة الجنسيات'),
        ('freelance', 'Freelance Platform / منصة عمل حر'),
    ]
    
    INDUSTRY_CHOICES = [
        ('tech', 'Technology / تكنولوجيا'),
        ('finance', 'Finance & Banking / بنوك ومالية'),
        ('telecom', 'Telecommunications / اتصالات'),
        ('energy', 'Energy & Oil / طاقة وبترول'),
        ('ecommerce', 'E-commerce / تجارة إلكترونية'),
        ('education', 'Education / تعليم'),
        ('health', 'Healthcare / صحة'),
        ('services', 'Services / خدمات'),
        ('manufacturing', 'Manufacturing / صناعة'),
    ]
    
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True, help_text="Arabic name")
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, default='sme')
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='tech')
    
    # Location
    wilaya = models.CharField(max_length=50, default='alger')
    address = models.TextField(blank=True)
    
    # Contact
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Skills they look for
    required_skills = models.JSONField(default=list, help_text="Skills this company typically needs")
    
    # Hiring info
    is_hiring = models.BooleanField(default=True)
    remote_friendly = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Algerian Companies'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_industry_display()})"


class JobOpportunity(models.Model):
    """Job opportunities in Algeria's tech market."""
    
    JOB_TYPES = [
        ('full_time', 'Full-time / دوام كامل'),
        ('part_time', 'Part-time / دوام جزئي'),
        ('contract', 'Contract / عقد'),
        ('internship', 'Internship / تدريب'),
        ('freelance', 'Freelance / عمل حر'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level / مبتدئ'),
        ('junior', 'Junior (1-2 years) / جونيور'),
        ('mid', 'Mid-level (3-5 years) / متوسط'),
        ('senior', 'Senior (5+ years) / سينيور'),
    ]
    
    company = models.ForeignKey(
        AlgerianCompany,
        on_delete=models.CASCADE,
        related_name='job_opportunities',
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True)
    
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='entry')
    
    # Requirements
    required_skills = models.JSONField(default=list, help_text="Required skills for this job")
    nice_to_have_skills = models.JSONField(default=list, help_text="Nice to have skills")
    
    # Location and salary
    wilaya = models.CharField(max_length=50, default='alger')
    is_remote = models.BooleanField(default=False)
    salary_range = models.CharField(max_length=100, blank=True, help_text="e.g., '80,000 - 120,000 DZD'")
    
    # Status
    is_active = models.BooleanField(default=True)
    application_url = models.URLField(blank=True)
    
    # Market demand
    demand_score = models.FloatField(default=0.5, help_text="Market demand score 0-1")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Job Opportunities'
        ordering = ['-demand_score', '-created_at']
    
    def __str__(self):
        company_name = self.company.name if self.company else 'Unknown'
        return f"{self.title} at {company_name}"


class SkillDemand(models.Model):
    """Tracks skill demand in the Algerian market."""
    
    skill_name = models.CharField(max_length=100, unique=True)
    skill_name_ar = models.CharField(max_length=100, blank=True)
    
    # Demand metrics
    demand_score = models.FloatField(default=0.5, help_text="Overall demand 0-1")
    growth_trend = models.CharField(max_length=20, choices=[
        ('rising', 'Rising / في ارتفاع'),
        ('stable', 'Stable / مستقر'),
        ('declining', 'Declining / في انخفاض'),
    ], default='stable')
    
    # Related info
    related_skills = models.JSONField(default=list, help_text="Related skills")
    average_salary = models.CharField(max_length=100, blank=True, help_text="Average salary in DZD")
    job_count = models.PositiveIntegerField(default=0, help_text="Number of active jobs requiring this skill")
    
    # Categories
    category = models.CharField(max_length=50, blank=True, help_text="Skill category")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Skill Demands'
        ordering = ['-demand_score']
    
    def __str__(self):
        return f"{self.skill_name} (Demand: {self.demand_score})"
