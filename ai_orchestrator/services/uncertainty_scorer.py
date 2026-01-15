"""
Uncertainty Scorer Service
Decides if 0-3 follow-up questions are needed based on profile completeness.
"""
from profiles.models import LearnerProfile, ClarifyingQuestion


class UncertaintyScorer:
    """Calculates uncertainty score and generates clarifying questions."""
    
    # Maximum number of follow-up questions (hard cap)
    MAX_QUESTIONS = 3
    
    # Weights for different profile aspects
    WEIGHTS = {
        'subject_specificity': 0.3,
        'level_confidence': 0.2,
        'goals_clarity': 0.25,
        'time_constraints': 0.15,
        'preferences_complete': 0.1,
    }
    
    def calculate_uncertainty(self, profile: LearnerProfile) -> float:
        """
        Calculate overall uncertainty score (0-1, higher = more uncertain).
        
        Returns:
            float: Uncertainty score between 0 and 1
        """
        scores = {
            'subject_specificity': self._score_subject(profile),
            'level_confidence': self._score_level(profile),
            'goals_clarity': self._score_goals(profile),
            'time_constraints': self._score_time(profile),
            'preferences_complete': self._score_preferences(profile),
        }
        
        # Weighted average (inverted: high score = low uncertainty)
        certainty = sum(
            scores[key] * self.WEIGHTS[key] 
            for key in scores
        )
        
        return 1 - certainty
    
    def get_required_questions_count(self, uncertainty: float) -> int:
        """
        Determine how many clarifying questions to ask.
        
        Args:
            uncertainty: Score between 0 and 1
            
        Returns:
            int: Number of questions (0-3)
        """
        if uncertainty < 0.2:
            return 0
        elif uncertainty < 0.4:
            return 1
        elif uncertainty < 0.6:
            return 2
        else:
            return self.MAX_QUESTIONS
    
    def generate_questions(self, profile: LearnerProfile, count: int) -> list:
        """
        Generate clarifying questions based on profile gaps.
        
        Returns:
            list: List of question dictionaries
        """
        questions = []
        
        # Prioritize questions based on what's missing
        if count > 0 and self._score_subject(profile) < 0.7:
            questions.append({
                'question_text': f"You want to learn '{profile.subject}'. Could you be more specific about what aspects interest you most?",
                'question_type': 'text',
                'options': [],
                'priority': 1,
            })
        
        if count > len(questions) and self._score_level(profile) < 0.7:
            questions.append({
                'question_text': "How would you describe your current experience with this subject?",
                'question_type': 'single_choice',
                'options': [
                    "Complete beginner - never studied this before",
                    "Some exposure - watched videos or read articles",
                    "Basic understanding - completed a course or tutorial",
                    "Intermediate - built small projects",
                    "Advanced - have professional experience",
                ],
                'priority': 2,
            })
        
        if count > len(questions) and self._score_goals(profile) < 0.7:
            questions.append({
                'question_text': "What do you want to achieve after completing this learning path?",
                'question_type': 'multiple_choice',
                'options': [
                    "Career change / new job",
                    "Skill upgrade for current role",
                    "Personal project / hobby",
                    "Academic requirement",
                    "Teaching others",
                ],
                'priority': 3,
            })
        
        if count > len(questions) and self._score_preferences(profile) < 0.7:
            questions.append({
                'question_text': "What type of learning resources do you prefer?",
                'question_type': 'multiple_choice',
                'options': [
                    "Video tutorials",
                    "Written articles / documentation",
                    "Interactive exercises",
                    "Project-based learning",
                    "Books / structured courses",
                ],
                'priority': 4,
            })
        
        # Sort by priority and return up to count
        questions.sort(key=lambda x: x['priority'])
        return questions[:count]
    
    def _score_subject(self, profile: LearnerProfile) -> float:
        """Score subject specificity (0-1)."""
        if not profile.subject:
            return 0.0
        
        # Longer, more specific subjects score higher
        length_score = min(len(profile.subject) / 50, 1.0)
        
        # Check for common generic terms
        generic_terms = ['programming', 'coding', 'technology', 'computer']
        is_generic = any(term in profile.subject.lower() for term in generic_terms)
        
        return length_score * (0.5 if is_generic else 1.0)
    
    def _score_level(self, profile: LearnerProfile) -> float:
        """Score level confidence (0-1)."""
        # If level is explicitly set (not default), higher confidence
        return 0.8 if profile.level != LearnerProfile.BEGINNER else 0.5
    
    def _score_goals(self, profile: LearnerProfile) -> float:
        """Score goals clarity (0-1)."""
        if not profile.goals:
            return 0.0
        return min(len(profile.goals) / 200, 1.0)
    
    def _score_time(self, profile: LearnerProfile) -> float:
        """Score time constraints clarity (0-1)."""
        score = 0.5  # Base score for having weekly_hours
        
        if profile.deadline:
            score += 0.3
        
        if profile.weekly_hours >= 5:
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_preferences(self, profile: LearnerProfile) -> float:
        """Score preferences completeness (0-1)."""
        if not profile.preferences:
            return 0.0
        
        # More preference keys = more complete
        return min(len(profile.preferences) / 5, 1.0)
