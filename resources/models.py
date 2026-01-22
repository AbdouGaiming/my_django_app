from django.db import models


class Resource(models.Model):
    """Curated learning resource with quality signals."""
    
    # Difficulty levels
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    
    DIFFICULTY_CHOICES = [
        (BEGINNER, 'Beginner / مبتدئ'),
        (INTERMEDIATE, 'Intermediate / متوسط'),
        (ADVANCED, 'Advanced / متقدم'),
    ]
    
    # Resource types - Extended for better learning resources
    VIDEO = 'video'
    YOUTUBE_TUTORIAL = 'youtube_tutorial'
    YOUTUBE_PLAYLIST = 'youtube_playlist'
    YOUTUBE_CHANNEL = 'youtube_channel'
    ARTICLE = 'article'
    COURSE = 'course'
    BOOK = 'book'
    EBOOK = 'ebook'
    PDF = 'pdf'
    TUTORIAL = 'tutorial'
    DOCUMENTATION = 'documentation'
    EXERCISE = 'exercise'
    PROJECT = 'project'
    GITHUB_REPO = 'github_repo'
    
    TYPE_CHOICES = [
        (VIDEO, 'Video / فيديو'),
        (YOUTUBE_TUTORIAL, 'YouTube Tutorial / درس يوتيوب'),
        (YOUTUBE_PLAYLIST, 'YouTube Playlist / قائمة تشغيل'),
        (YOUTUBE_CHANNEL, 'YouTube Channel / قناة يوتيوب'),
        (ARTICLE, 'Article / مقال'),
        (COURSE, 'Course / دورة'),
        (BOOK, 'Book / كتاب'),
        (EBOOK, 'E-Book / كتاب إلكتروني'),
        (PDF, 'PDF Document / مستند PDF'),
        (TUTORIAL, 'Tutorial / درس'),
        (DOCUMENTATION, 'Documentation / توثيق'),
        (EXERCISE, 'Exercise / تمرين'),
        (PROJECT, 'Project / مشروع'),
        (GITHUB_REPO, 'GitHub Repository'),
    ]
    
    # Language choices matching Algeria
    LANGUAGE_CHOICES = [
        ('ar', 'العربية (Arabic)'),
        ('ar_dz', 'الدارجة الجزائرية (Algerian)'),
        ('fr', 'Français (French)'),
        ('en', 'English'),
        ('multi', 'Multilingual / متعدد اللغات'),
    ]
    
    title = models.CharField(max_length=300)
    title_ar = models.CharField(max_length=300, blank=True, help_text="Arabic title")
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True, help_text="Arabic description")
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=ARTICLE)
    
    # Provider information
    provider = models.CharField(max_length=100, blank=True, help_text="e.g., YouTube, Coursera, Medium")
    author = models.CharField(max_length=200, blank=True)
    channel_name = models.CharField(max_length=200, blank=True, help_text="YouTube channel name")
    
    # Difficulty and duration
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=BEGINNER)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated time in minutes")
    video_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of videos in playlist")
    page_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of pages for books")
    
    # Language and tags
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='ar')
    tags = models.JSONField(default=list, blank=True, help_text="List of topic tags")
    skills_covered = models.JSONField(default=list, blank=True, help_text="Skills taught by this resource")
    
    # Quality signals
    quality_score = models.FloatField(default=0.5, help_text="Quality score 0-1")
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0, help_text="YouTube views or similar")
    
    # Metadata
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_arabic_friendly = models.BooleanField(default=False, help_text="Good for Arabic speakers")
    has_subtitles = models.BooleanField(default=False, help_text="Has Arabic/French subtitles")
    
    # Algerian market relevance
    algeria_relevant = models.BooleanField(default=True, help_text="Relevant for Algerian job market")
    
    # Book specific
    isbn = models.CharField(max_length=20, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    
    # YouTube specific
    youtube_video_id = models.CharField(max_length=20, blank=True, help_text="YouTube video ID")
    youtube_playlist_id = models.CharField(max_length=50, blank=True, help_text="YouTube playlist ID")
    youtube_channel_id = models.CharField(max_length=50, blank=True, help_text="YouTube channel ID")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-quality_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    def get_youtube_url(self):
        """Get the YouTube URL for this resource."""
        if self.youtube_video_id:
            return f"https://www.youtube.com/watch?v={self.youtube_video_id}"
        elif self.youtube_playlist_id:
            return f"https://www.youtube.com/playlist?list={self.youtube_playlist_id}"
        elif self.youtube_channel_id:
            return f"https://www.youtube.com/channel/{self.youtube_channel_id}"
        return None


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
