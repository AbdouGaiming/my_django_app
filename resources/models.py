from django.db import models


class Resource(models.Model):
    """Curated learning resource with quality signals."""
    
    # Difficulty levels
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    
    DIFFICULTY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]
    
    # Resource types
    VIDEO = 'video'
    ARTICLE = 'article'
    COURSE = 'course'
    BOOK = 'book'
    TUTORIAL = 'tutorial'
    DOCUMENTATION = 'documentation'
    EXERCISE = 'exercise'
    
    TYPE_CHOICES = [
        (VIDEO, 'Video'),
        (ARTICLE, 'Article'),
        (COURSE, 'Course'),
        (BOOK, 'Book'),
        (TUTORIAL, 'Tutorial'),
        (DOCUMENTATION, 'Documentation'),
        (EXERCISE, 'Exercise'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=ARTICLE)
    
    # Provider information
    provider = models.CharField(max_length=100, blank=True, help_text="e.g., YouTube, Coursera, Medium")
    author = models.CharField(max_length=200, blank=True)
    
    # Difficulty and duration
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=BEGINNER)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated time in minutes")
    
    # Language and tags
    language = models.CharField(max_length=10, default='en')
    tags = models.JSONField(default=list, blank=True, help_text="List of topic tags")
    
    # Quality signals
    quality_score = models.FloatField(default=0.5, help_text="Quality score 0-1")
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    
    # Metadata
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-quality_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.resource_type})"


class ResourceLink(models.Model):
    """URLs associated with a resource (may have multiple mirrors/versions)."""
    
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='links'
    )
    
    url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=True)
    is_working = models.BooleanField(default=True)
    
    last_checked = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"Link for {self.resource.title}: {self.url[:50]}..."
