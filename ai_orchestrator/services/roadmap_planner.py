"""
Roadmap Planner Service
Generates learning steps from prerequisite graph with time constraints.
"""
from datetime import date, timedelta
from typing import List, Dict
from profiles.models import LearnerProfile
from roadmaps.models import Roadmap, RoadmapStep


class RoadmapPlanner:
    """Plans learning roadmaps based on profile and constraints."""
    
    # Prerequisite graph for common subjects
    PREREQUISITE_GRAPHS = {
        'python': [
            {'id': 1, 'title': 'Python Basics', 'topics': ['syntax', 'variables', 'data types'], 'hours': 8, 'prereqs': []},
            {'id': 2, 'title': 'Control Flow', 'topics': ['if/else', 'loops', 'exceptions'], 'hours': 6, 'prereqs': [1]},
            {'id': 3, 'title': 'Functions & Modules', 'topics': ['functions', 'modules', 'packages'], 'hours': 8, 'prereqs': [2]},
            {'id': 4, 'title': 'Data Structures', 'topics': ['lists', 'dicts', 'sets', 'tuples'], 'hours': 10, 'prereqs': [3]},
            {'id': 5, 'title': 'Object-Oriented Programming', 'topics': ['classes', 'inheritance', 'polymorphism'], 'hours': 12, 'prereqs': [4]},
            {'id': 6, 'title': 'File I/O & APIs', 'topics': ['file handling', 'JSON', 'REST APIs'], 'hours': 8, 'prereqs': [4]},
            {'id': 7, 'title': 'Testing & Debugging', 'topics': ['unit tests', 'debugging', 'logging'], 'hours': 6, 'prereqs': [5]},
            {'id': 8, 'title': 'Advanced Topics', 'topics': ['decorators', 'generators', 'context managers'], 'hours': 10, 'prereqs': [5, 6]},
        ],
        'javascript': [
            {'id': 1, 'title': 'JavaScript Fundamentals', 'topics': ['syntax', 'variables', 'types'], 'hours': 8, 'prereqs': []},
            {'id': 2, 'title': 'DOM Manipulation', 'topics': ['selectors', 'events', 'forms'], 'hours': 8, 'prereqs': [1]},
            {'id': 3, 'title': 'Async JavaScript', 'topics': ['callbacks', 'promises', 'async/await'], 'hours': 10, 'prereqs': [2]},
            {'id': 4, 'title': 'Modern ES6+', 'topics': ['arrow functions', 'modules', 'classes'], 'hours': 8, 'prereqs': [3]},
            {'id': 5, 'title': 'Node.js Basics', 'topics': ['npm', 'modules', 'file system'], 'hours': 10, 'prereqs': [4]},
            {'id': 6, 'title': 'Express.js', 'topics': ['routing', 'middleware', 'REST APIs'], 'hours': 12, 'prereqs': [5]},
        ],
        'web_development': [
            {'id': 1, 'title': 'HTML Fundamentals', 'topics': ['tags', 'forms', 'semantic HTML'], 'hours': 6, 'prereqs': []},
            {'id': 2, 'title': 'CSS Basics', 'topics': ['selectors', 'box model', 'flexbox'], 'hours': 8, 'prereqs': [1]},
            {'id': 3, 'title': 'Responsive Design', 'topics': ['media queries', 'grid', 'mobile-first'], 'hours': 6, 'prereqs': [2]},
            {'id': 4, 'title': 'JavaScript for Web', 'topics': ['DOM', 'events', 'fetch API'], 'hours': 10, 'prereqs': [3]},
            {'id': 5, 'title': 'Frontend Frameworks', 'topics': ['React/Vue basics', 'components', 'state'], 'hours': 15, 'prereqs': [4]},
            {'id': 6, 'title': 'Backend Basics', 'topics': ['servers', 'databases', 'APIs'], 'hours': 12, 'prereqs': [4]},
        ],
        'data_science': [
            {'id': 1, 'title': 'Python for Data Science', 'topics': ['NumPy', 'Pandas basics'], 'hours': 12, 'prereqs': []},
            {'id': 2, 'title': 'Data Visualization', 'topics': ['Matplotlib', 'Seaborn', 'charts'], 'hours': 8, 'prereqs': [1]},
            {'id': 3, 'title': 'Statistics Fundamentals', 'topics': ['descriptive stats', 'probability', 'distributions'], 'hours': 10, 'prereqs': [1]},
            {'id': 4, 'title': 'Data Cleaning', 'topics': ['missing data', 'outliers', 'normalization'], 'hours': 8, 'prereqs': [2, 3]},
            {'id': 5, 'title': 'Exploratory Data Analysis', 'topics': ['EDA techniques', 'correlation', 'feature analysis'], 'hours': 10, 'prereqs': [4]},
            {'id': 6, 'title': 'Machine Learning Intro', 'topics': ['sklearn', 'regression', 'classification'], 'hours': 15, 'prereqs': [5]},
        ],
    }
    
    # Default graph for unknown subjects
    DEFAULT_GRAPH = [
        {'id': 1, 'title': 'Fundamentals', 'topics': ['core concepts', 'basics'], 'hours': 10, 'prereqs': []},
        {'id': 2, 'title': 'Intermediate Concepts', 'topics': ['advanced basics', 'common patterns'], 'hours': 12, 'prereqs': [1]},
        {'id': 3, 'title': 'Practical Applications', 'topics': ['hands-on practice', 'projects'], 'hours': 15, 'prereqs': [2]},
        {'id': 4, 'title': 'Advanced Topics', 'topics': ['expert techniques', 'optimization'], 'hours': 12, 'prereqs': [3]},
    ]
    
    def plan(self, profile: LearnerProfile, normalized_data: dict) -> List[Dict]:
        """
        Generate a learning plan based on profile.
        
        Returns:
            list: List of step dictionaries with sequence, titles, hours, etc.
        """
        subject = normalized_data.get('subject_canonical', 'default')
        level = normalized_data.get('level_canonical', LearnerProfile.BEGINNER)
        
        # Get prerequisite graph
        graph = self.PREREQUISITE_GRAPHS.get(subject, self.DEFAULT_GRAPH)
        
        # Filter based on level (skip beginner steps for advanced users)
        steps = self._filter_by_level(graph, level)
        
        # Adjust hours based on constraints
        steps = self._adjust_for_constraints(steps, profile)
        
        # Add metadata
        for i, step in enumerate(steps):
            step['sequence'] = i + 1
            step['objectives'] = [f"Understand {topic}" for topic in step.get('topics', [])]
        
        return steps
    
    def _filter_by_level(self, graph: List[Dict], level: str) -> List[Dict]:
        """Filter steps based on learner level."""
        if level == LearnerProfile.BEGINNER:
            return graph.copy()
        elif level == LearnerProfile.INTERMEDIATE:
            # Skip first 1-2 steps
            return graph[1:] if len(graph) > 2 else graph.copy()
        elif level == LearnerProfile.ADVANCED:
            # Skip first half
            skip = len(graph) // 2
            return graph[skip:] if skip < len(graph) else graph[-2:]
        else:  # Expert
            # Only advanced topics
            return graph[-2:] if len(graph) >= 2 else graph.copy()
    
    def _adjust_for_constraints(self, steps: List[Dict], profile: LearnerProfile) -> List[Dict]:
        """Adjust step hours based on time constraints."""
        if not profile.deadline:
            return steps
        
        # Calculate available time
        days_available = (profile.deadline - date.today()).days
        weeks_available = max(days_available / 7, 1)
        total_hours_available = weeks_available * profile.weekly_hours
        
        # Calculate current total
        current_total = sum(step['hours'] for step in steps)
        
        if current_total <= total_hours_available:
            return steps
        
        # Scale down hours proportionally
        scale_factor = total_hours_available / current_total
        for step in steps:
            step['hours'] = max(round(step['hours'] * scale_factor, 1), 1)
        
        return steps
    
    def create_roadmap(self, user, profile: LearnerProfile, steps: List[Dict], normalized_data: dict) -> Roadmap:
        """
        Create a Roadmap instance with steps.
        
        Returns:
            Roadmap: Created roadmap with steps
        """
        # Create roadmap
        roadmap = Roadmap.objects.create(
            user=user,
            learner_profile=profile,
            title=f"Learning Path: {profile.subject}",
            description=f"Personalized roadmap for learning {profile.subject}",
            total_estimated_hours=sum(step['hours'] for step in steps),
            input_profile_hash=normalized_data.get('profile_hash', ''),
            model_versions={'planner': '1.0', 'llm': 'rule-based'},
        )
        
        # Create steps
        created_steps = {}
        for step_data in steps:
            roadmap_step = RoadmapStep.objects.create(
                roadmap=roadmap,
                title=step_data['title'],
                description=f"Learn about: {', '.join(step_data.get('topics', []))}",
                objectives=step_data.get('objectives', []),
                sequence=step_data['sequence'],
                estimated_hours=step_data['hours'],
                status=RoadmapStep.STATUS_ACTIVE if step_data['sequence'] == 1 else RoadmapStep.STATUS_LOCKED,
            )
            created_steps[step_data['id']] = roadmap_step
        
        # Set prerequisites
        for step_data in steps:
            if step_data.get('prereqs'):
                step = created_steps[step_data['id']]
                for prereq_id in step_data['prereqs']:
                    if prereq_id in created_steps:
                        step.prerequisites.add(created_steps[prereq_id])
        
        return roadmap
