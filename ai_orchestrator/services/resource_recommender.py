"""
Resource Recommender Service
Recommends YouTube tutorials, playlists, books, and other learning resources
with focus on Arabic, French, and English content for Algerian learners.
"""
from typing import List, Dict, Optional
from resources.models import Resource, ResourceLink


class ResourceRecommender:
    """
    Recommends quality learning resources including:
    - YouTube tutorials and playlists (Arabic, French, English)
    - Books and e-books
    - Online courses
    - Practice projects
    """
    
    # Curated YouTube channels for Arabic speakers
    ARABIC_YOUTUBE_CHANNELS = {
        'programming': [
            {
                'channel_name': 'Elzero Web School',
                'channel_id': 'UCSNkfKl4cU-55Nm-ovsvOHQ',
                'language': 'ar',
                'quality_score': 0.95,
                'description': 'أفضل قناة عربية لتعلم البرمجة وتطوير الويب',
                'topics': ['html', 'css', 'javascript', 'python', 'web_development'],
            },
            {
                'channel_name': 'Codezilla',
                'channel_id': 'UCCIshBAXYckZIq3mBv8LKcA',
                'language': 'ar',
                'quality_score': 0.9,
                'description': 'شروحات برمجية بالعربي بطريقة سهلة',
                'topics': ['python', 'javascript', 'data_science', 'web_development'],
            },
            {
                'channel_name': 'محمد الشريف - Mohamed El Sherif',
                'channel_id': 'UCNjIU06L4dKhbexLh1WBL8Q',
                'language': 'ar',
                'quality_score': 0.85,
                'description': 'دورات برمجية متكاملة',
                'topics': ['python', 'django', 'web_development'],
            },
            {
                'channel_name': 'The Coding Bus',
                'channel_id': 'UCPBnk7HGLzN2vKPVw6J7J6A',
                'language': 'ar',
                'quality_score': 0.85,
                'description': 'تعلم البرمجة خطوة بخطوة',
                'topics': ['python', 'javascript', 'mobile_development'],
            },
        ],
        'data_science': [
            {
                'channel_name': 'Big Data Arabic',
                'channel_id': 'UCT0ry_4dUxiQkwJ4gJQsD-Q',
                'language': 'ar',
                'quality_score': 0.9,
                'description': 'علوم البيانات والذكاء الاصطناعي بالعربي',
                'topics': ['data_science', 'machine_learning', 'python', 'sql'],
            },
        ],
    }
    
    # Curated YouTube playlists
    YOUTUBE_PLAYLISTS = {
        'python': [
            {
                'title': 'Python Tutorial - Full Course for Beginners',
                'title_ar': 'دورة بايثون كاملة للمبتدئين',
                'playlist_id': 'PLDoPjvoNmBAyE_gei5d18qkfIe-Z8mocs',
                'channel_name': 'Elzero Web School',
                'language': 'ar',
                'video_count': 150,
                'duration_minutes': 1200,
                'quality_score': 0.95,
                'difficulty': 'beginner',
            },
            {
                'title': 'Learn Python - freeCodeCamp',
                'title_ar': 'تعلم بايثون - freeCodeCamp',
                'playlist_id': 'PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB',
                'channel_name': 'freeCodeCamp',
                'language': 'en',
                'video_count': 50,
                'duration_minutes': 600,
                'quality_score': 0.9,
                'difficulty': 'beginner',
            },
            {
                'title': 'Python pour les débutants',
                'title_ar': 'بايثون للمبتدئين (فرنسي)',
                'playlist_id': 'PLrSOXFDHBtfHg8fWBd7sKPxEmahwyVBkC',
                'channel_name': 'Graven',
                'language': 'fr',
                'video_count': 30,
                'duration_minutes': 400,
                'quality_score': 0.85,
                'difficulty': 'beginner',
            },
        ],
        'javascript': [
            {
                'title': 'JavaScript Tutorial - Elzero Web School',
                'title_ar': 'دورة جافاسكريبت كاملة',
                'playlist_id': 'PLDoPjvoNmBAx3kiplQR_oeDqLDBUDYwVv',
                'channel_name': 'Elzero Web School',
                'language': 'ar',
                'video_count': 188,
                'duration_minutes': 1500,
                'quality_score': 0.95,
                'difficulty': 'beginner',
            },
            {
                'title': 'JavaScript Full Course',
                'title_ar': 'دورة جافاسكريبت كاملة (إنجليزي)',
                'playlist_id': 'PL0Zuz27SZ-6Oi6xNtL_fwCrwpuqylMsgT',
                'channel_name': 'Dave Gray',
                'language': 'en',
                'video_count': 40,
                'duration_minutes': 800,
                'quality_score': 0.9,
                'difficulty': 'beginner',
            },
        ],
        'web_development': [
            {
                'title': 'Complete Web Development Course',
                'title_ar': 'دورة تطوير الويب الكاملة',
                'playlist_id': 'PLDoPjvoNmBAzHSjcR-HnW9tnxyuye8KbF',
                'channel_name': 'Elzero Web School',
                'language': 'ar',
                'video_count': 300,
                'duration_minutes': 2400,
                'quality_score': 0.95,
                'difficulty': 'beginner',
            },
            {
                'title': 'HTML & CSS Full Course',
                'title_ar': 'دورة HTML و CSS كاملة',
                'playlist_id': 'PLDoPjvoNmBAw47QWq6W-tzj-9duQHV7Gg',
                'channel_name': 'Elzero Web School',
                'language': 'ar',
                'video_count': 88,
                'duration_minutes': 700,
                'quality_score': 0.95,
                'difficulty': 'beginner',
            },
        ],
        'data_science': [
            {
                'title': 'Data Science Full Course',
                'title_ar': 'دورة علوم البيانات الكاملة',
                'playlist_id': 'PLeo1K3hjS3us_ELKYSj_Fth2tIEkdKXvV',
                'channel_name': 'codebasics',
                'language': 'en',
                'video_count': 45,
                'duration_minutes': 900,
                'quality_score': 0.9,
                'difficulty': 'beginner',
            },
        ],
        'react': [
            {
                'title': 'React JS Tutorial',
                'title_ar': 'دورة React JS',
                'playlist_id': 'PLDoPjvoNmBAw_t_XWUFbBX-c9MafPk9ji',
                'channel_name': 'Elzero Web School',
                'language': 'ar',
                'video_count': 80,
                'duration_minutes': 600,
                'quality_score': 0.95,
                'difficulty': 'intermediate',
            },
        ],
        'django': [
            {
                'title': 'Django Full Course',
                'title_ar': 'دورة Django كاملة',
                'playlist_id': 'PL2z1gXAKH9c3XUn2HYMWRbAon4z6AQ4CL',
                'channel_name': 'Traversy Media',
                'language': 'en',
                'video_count': 25,
                'duration_minutes': 500,
                'quality_score': 0.9,
                'difficulty': 'intermediate',
            },
        ],
    }
    
    # Recommended books
    RECOMMENDED_BOOKS = {
        'python': [
            {
                'title': 'Automate the Boring Stuff with Python',
                'title_ar': 'أتمتة المهام المملة باستخدام بايثون',
                'author': 'Al Sweigart',
                'language': 'en',
                'is_free': True,
                'url': 'https://automatetheboringstuff.com/',
                'difficulty': 'beginner',
                'quality_score': 0.95,
                'page_count': 500,
                'description': 'Best free book for Python beginners',
                'description_ar': 'أفضل كتاب مجاني للمبتدئين في بايثون',
            },
            {
                'title': 'Python Crash Course',
                'title_ar': 'دورة بايثون السريعة',
                'author': 'Eric Matthes',
                'language': 'en',
                'is_free': False,
                'difficulty': 'beginner',
                'quality_score': 0.9,
                'page_count': 544,
                'description': 'Hands-on project-based introduction',
                'description_ar': 'مقدمة عملية قائمة على المشاريع',
            },
            {
                'title': 'تعلم البرمجة بلغة بايثون',
                'title_ar': 'تعلم البرمجة بلغة بايثون',
                'author': 'أكاديمية حسوب',
                'language': 'ar',
                'is_free': True,
                'url': 'https://academy.hsoub.com/programming/python/',
                'difficulty': 'beginner',
                'quality_score': 0.85,
                'description_ar': 'كتاب عربي مجاني لتعلم بايثون',
            },
        ],
        'javascript': [
            {
                'title': 'Eloquent JavaScript',
                'title_ar': 'جافاسكريبت البليغة',
                'author': 'Marijn Haverbeke',
                'language': 'en',
                'is_free': True,
                'url': 'https://eloquentjavascript.net/',
                'difficulty': 'beginner',
                'quality_score': 0.95,
                'page_count': 450,
                'description': 'Deep dive into JavaScript',
                'description_ar': 'غوص عميق في جافاسكريبت',
            },
            {
                'title': 'JavaScript: The Good Parts',
                'title_ar': 'جافاسكريبت: الأجزاء الجيدة',
                'author': 'Douglas Crockford',
                'language': 'en',
                'is_free': False,
                'difficulty': 'intermediate',
                'quality_score': 0.9,
                'page_count': 176,
            },
        ],
        'web_development': [
            {
                'title': 'HTML & CSS: Design and Build Websites',
                'title_ar': 'HTML و CSS: تصميم وبناء المواقع',
                'author': 'Jon Duckett',
                'language': 'en',
                'is_free': False,
                'difficulty': 'beginner',
                'quality_score': 0.9,
                'page_count': 490,
                'description': 'Visual guide to web development',
                'description_ar': 'دليل بصري لتطوير الويب',
            },
        ],
        'data_science': [
            {
                'title': 'Python for Data Analysis',
                'title_ar': 'بايثون لتحليل البيانات',
                'author': 'Wes McKinney',
                'language': 'en',
                'is_free': False,
                'difficulty': 'intermediate',
                'quality_score': 0.9,
                'page_count': 550,
            },
            {
                'title': 'Hands-On Machine Learning',
                'title_ar': 'التعلم الآلي العملي',
                'author': 'Aurélien Géron',
                'language': 'en',
                'is_free': False,
                'difficulty': 'intermediate',
                'quality_score': 0.95,
                'page_count': 850,
            },
        ],
    }
    
    def __init__(self, language: str = 'ar'):
        self.language = language
    
    def get_youtube_playlists(self, subject: str, difficulty: str = None, limit: int = 5) -> List[Dict]:
        """
        Get recommended YouTube playlists for a subject.
        
        Args:
            subject: Learning subject
            difficulty: Optional difficulty filter
            limit: Maximum number of results
            
        Returns:
            list: Playlist recommendations
        """
        subject_key = subject.lower().replace(' ', '_')
        playlists = self.YOUTUBE_PLAYLISTS.get(subject_key, [])
        
        # Sort by language preference (user's language first)
        language_priority = {self.language: 0, 'ar': 1, 'en': 2, 'fr': 3}
        playlists.sort(key=lambda x: (language_priority.get(x.get('language', 'en'), 99), -x.get('quality_score', 0)))
        
        # Filter by difficulty if specified
        if difficulty:
            playlists = [p for p in playlists if p.get('difficulty') == difficulty]
        
        # Add YouTube URLs
        for playlist in playlists:
            playlist['url'] = f"https://www.youtube.com/playlist?list={playlist['playlist_id']}"
        
        return playlists[:limit]
    
    def get_youtube_channels(self, subject: str, limit: int = 3) -> List[Dict]:
        """
        Get recommended YouTube channels for a subject.
        
        Args:
            subject: Learning subject
            limit: Maximum number of results
            
        Returns:
            list: Channel recommendations
        """
        category = 'programming'
        subject_lower = subject.lower()
        if 'data' in subject_lower or 'machine' in subject_lower:
            category = 'data_science'
        
        channels = self.ARABIC_YOUTUBE_CHANNELS.get(category, [])
        
        # Filter by relevant topics
        subject_key = subject.lower().replace(' ', '_')
        relevant_channels = []
        for channel in channels:
            if subject_key in channel.get('topics', []) or any(t in subject_key for t in channel.get('topics', [])):
                channel['url'] = f"https://www.youtube.com/channel/{channel['channel_id']}"
                relevant_channels.append(channel)
        
        # If no specific match, return all channels
        if not relevant_channels:
            for channel in channels:
                channel['url'] = f"https://www.youtube.com/channel/{channel['channel_id']}"
            relevant_channels = channels
        
        return relevant_channels[:limit]
    
    def get_books(self, subject: str, difficulty: str = None, free_only: bool = False, limit: int = 5) -> List[Dict]:
        """
        Get recommended books for a subject.
        
        Args:
            subject: Learning subject
            difficulty: Optional difficulty filter
            free_only: Only return free books
            limit: Maximum number of results
            
        Returns:
            list: Book recommendations
        """
        subject_key = subject.lower().replace(' ', '_')
        books = self.RECOMMENDED_BOOKS.get(subject_key, [])
        
        # Filter by difficulty
        if difficulty:
            books = [b for b in books if b.get('difficulty') == difficulty]
        
        # Filter by free
        if free_only:
            books = [b for b in books if b.get('is_free', False)]
        
        # Sort by language preference and quality
        language_priority = {self.language: 0, 'ar': 1, 'en': 2, 'fr': 3}
        books.sort(key=lambda x: (language_priority.get(x.get('language', 'en'), 99), -x.get('quality_score', 0)))
        
        return books[:limit]

    def get_localized_resources(self, subject: str, language: str = 'ar', limit: int = 6) -> List[Dict]:
        """
        Get a flattened list of localized resources for templates.
        
        Args:
            subject: Learning subject
            language: Preferred language
            limit: Maximum number of resources to return
        
        Returns:
            list: Resource dictionaries with title, url, resource_type
        """
        # Update language preference for sorting
        self.language = language or self.language

        resources: List[Dict] = []

        # Add playlists
        playlists = self.get_youtube_playlists(subject, limit=limit)
        for playlist in playlists:
            title = playlist.get('title')
            if self.language in ['ar', 'ar_dz'] and playlist.get('title_ar'):
                title = playlist.get('title_ar')
            resources.append({
                'title': title,
                'url': playlist.get('url', ''),
                'resource_type': 'youtube',
                'language': playlist.get('language', 'en'),
            })

        # Add books (free first, then paid)
        books = self.get_books(subject, free_only=True, limit=limit) + self.get_books(subject, free_only=False, limit=limit)
        for book in books:
            title = book.get('title')
            if self.language in ['ar', 'ar_dz'] and book.get('title_ar'):
                title = book.get('title_ar')
            resources.append({
                'title': title,
                'url': book.get('url', ''),
                'resource_type': 'book',
                'language': book.get('language', 'en'),
            })

        # Trim to limit and remove empty URLs
        filtered = [r for r in resources if r.get('url')]
        return filtered[:limit]
    
    def get_all_resources(self, subject: str, difficulty: str = None, language_pref: List[str] = None) -> Dict:
        """
        Get all types of resources for a subject.
        
        Args:
            subject: Learning subject
            difficulty: Optional difficulty filter
            language_pref: Preferred languages for content
            
        Returns:
            dict: All resource types
        """
        if language_pref:
            # Update language preference for filtering
            self.language = language_pref[0] if language_pref else self.language
        
        return {
            'youtube_playlists': self.get_youtube_playlists(subject, difficulty, limit=5),
            'youtube_channels': self.get_youtube_channels(subject, limit=3),
            'books': self.get_books(subject, difficulty, limit=5),
            'free_books': self.get_books(subject, difficulty, free_only=True, limit=3),
        }
    
    def sync_to_database(self, subject: str = None):
        """
        Sync resources to the database.
        
        Args:
            subject: Optional subject filter (syncs all if None)
        """
        subjects = [subject] if subject else list(self.YOUTUBE_PLAYLISTS.keys())
        
        for subj in subjects:
            # Sync YouTube playlists
            for playlist in self.YOUTUBE_PLAYLISTS.get(subj, []):
                resource, created = Resource.objects.update_or_create(
                    youtube_playlist_id=playlist['playlist_id'],
                    defaults={
                        'title': playlist['title'],
                        'title_ar': playlist.get('title_ar', ''),
                        'resource_type': 'youtube_playlist',
                        'provider': 'YouTube',
                        'channel_name': playlist.get('channel_name', ''),
                        'language': playlist.get('language', 'en'),
                        'difficulty': playlist.get('difficulty', 'beginner'),
                        'video_count': playlist.get('video_count'),
                        'duration_minutes': playlist.get('duration_minutes'),
                        'quality_score': playlist.get('quality_score', 0.8),
                        'is_free': True,
                        'tags': [subj],
                        'skills_covered': [subj],
                        'is_arabic_friendly': playlist.get('language') == 'ar',
                    }
                )
                
                # Add link
                if created or not resource.links.exists():
                    ResourceLink.objects.create(
                        resource=resource,
                        url=f"https://www.youtube.com/playlist?list={playlist['playlist_id']}",
                        is_primary=True,
                    )
            
            # Sync books
            for book in self.RECOMMENDED_BOOKS.get(subj, []):
                resource, created = Resource.objects.update_or_create(
                    title=book['title'],
                    resource_type='book',
                    defaults={
                        'title_ar': book.get('title_ar', ''),
                        'description': book.get('description', ''),
                        'description_ar': book.get('description_ar', ''),
                        'provider': 'Book',
                        'author': book.get('author', ''),
                        'language': book.get('language', 'en'),
                        'difficulty': book.get('difficulty', 'beginner'),
                        'page_count': book.get('page_count'),
                        'quality_score': book.get('quality_score', 0.8),
                        'is_free': book.get('is_free', False),
                        'tags': [subj],
                        'skills_covered': [subj],
                    }
                )
                
                if book.get('url') and (created or not resource.links.exists()):
                    ResourceLink.objects.create(
                        resource=resource,
                        url=book['url'],
                        is_primary=True,
                    )
    
    def format_resource_for_display(self, resource: Dict, language: str = 'ar') -> str:
        """
        Format a resource for display in the user's language.
        
        Args:
            resource: Resource data
            language: Display language
            
        Returns:
            str: Formatted string
        """
        title = resource.get(f'title_{language}') or resource.get('title_ar') or resource.get('title', '')
        url = resource.get('url', '')
        
        if language == 'ar':
            return f"📚 {title}\n🔗 {url}"
        elif language == 'fr':
            return f"📚 {title}\n🔗 {url}"
        else:
            return f"📚 {title}\n🔗 {url}"


def get_resources_for_subject(subject: str, language: str = 'ar') -> Dict:
    """
    Convenience function to get all resources for a subject.
    
    Args:
        subject: Learning subject
        language: User's preferred language
        
    Returns:
        dict: All resources organized by type
    """
    recommender = ResourceRecommender(language)
    return recommender.get_all_resources(subject)
