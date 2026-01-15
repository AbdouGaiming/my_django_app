"""
Profile Normalizer Service
Validates onboarding answers and maps to canonical enums/taxonomy.
"""
import hashlib
import json
from profiles.models import LearnerProfile


class ProfileNormalizer:
    """Normalizes and validates learner profile data."""
    
    # Canonical taxonomy for subjects
    SUBJECT_TAXONOMY = {
        'python': ['python', 'py', 'python3'],
        'javascript': ['javascript', 'js', 'node', 'nodejs'],
        'web_development': ['web', 'html', 'css', 'frontend', 'backend'],
        'data_science': ['data science', 'data analysis', 'analytics'],
        'machine_learning': ['machine learning', 'ml', 'ai', 'deep learning'],
        'databases': ['sql', 'database', 'mysql', 'postgresql', 'mongodb'],
    }
    
    # Level mapping
    LEVEL_MAPPING = {
        'beginner': LearnerProfile.BEGINNER,
        'novice': LearnerProfile.BEGINNER,
        'intermediate': LearnerProfile.INTERMEDIATE,
        'advanced': LearnerProfile.ADVANCED,
        'expert': LearnerProfile.EXPERT,
    }
    
    def normalize(self, profile: LearnerProfile) -> dict:
        """
        Normalize profile data and return canonical representation.
        
        Returns:
            dict: Normalized profile data with:
                - subject_canonical: Normalized subject name
                - level_canonical: Normalized level
                - profile_hash: Hash for reproducibility
        """
        normalized = {
            'subject_original': profile.subject,
            'subject_canonical': self._normalize_subject(profile.subject),
            'level_canonical': self._normalize_level(profile.level),
            'weekly_hours': profile.weekly_hours,
            'deadline': profile.deadline.isoformat() if profile.deadline else None,
            'language': profile.language,
            'goals': profile.goals,
            'preferences': profile.preferences,
        }
        
        # Generate hash for reproducibility
        normalized['profile_hash'] = self._generate_hash(normalized)
        
        return normalized
    
    def _normalize_subject(self, subject: str) -> str:
        """Map subject to canonical taxonomy."""
        subject_lower = subject.lower().strip()
        
        for canonical, aliases in self.SUBJECT_TAXONOMY.items():
            if subject_lower in aliases or canonical in subject_lower:
                return canonical
        
        # Return original if no match (custom subject)
        return subject_lower.replace(' ', '_')
    
    def _normalize_level(self, level: str) -> str:
        """Map level to canonical enum."""
        level_lower = level.lower().strip()
        return self.LEVEL_MAPPING.get(level_lower, LearnerProfile.BEGINNER)
    
    def _generate_hash(self, data: dict) -> str:
        """Generate SHA-256 hash of normalized profile."""
        # Remove hash field if present to avoid recursion
        data_copy = {k: v for k, v in data.items() if k != 'profile_hash'}
        json_str = json.dumps(data_copy, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def validate(self, profile: LearnerProfile) -> list:
        """
        Validate profile data.
        
        Returns:
            list: List of validation errors (empty if valid)
        """
        errors = []
        
        if not profile.subject or len(profile.subject.strip()) < 2:
            errors.append("Subject must be at least 2 characters")
        
        if profile.weekly_hours < 1:
            errors.append("Weekly hours must be at least 1")
        
        if profile.weekly_hours > 80:
            errors.append("Weekly hours cannot exceed 80")
        
        if profile.deadline:
            from datetime import date
            if profile.deadline < date.today():
                errors.append("Deadline cannot be in the past")
        
        return errors
