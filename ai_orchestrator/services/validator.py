"""
Validator Service
Enforces roadmap constraints and validates structure.
"""
from typing import List, Dict, Tuple
from datetime import timedelta


class Validator:
    """Validates roadmap structure and constraints."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_roadmap(self, roadmap) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validations on a roadmap.
        
        Args:
            roadmap: The roadmap to validate
            
        Returns:
            tuple: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        steps = list(roadmap.steps.order_by('sequence'))
        
        if not steps:
            self.errors.append("Roadmap has no steps")
            return False, self.errors, self.warnings
        
        # Run all validation checks
        self._validate_prerequisite_ordering(steps)
        self._validate_time_budget(steps, roadmap)
        self._validate_no_empty_steps(steps)
        self._validate_sequence_continuity(steps)
        self._validate_resources_coverage(steps)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_prerequisite_ordering(self, steps: List) -> None:
        """Ensure prerequisites appear before dependent steps."""
        step_sequences = {step.id: step.sequence for step in steps}
        
        for step in steps:
            prereqs = step.prerequisites.all()
            for prereq in prereqs:
                if prereq.id not in step_sequences:
                    self.errors.append(
                        f"Step '{step.title}' has prerequisite '{prereq.title}' not in roadmap"
                    )
                elif step_sequences[prereq.id] >= step.sequence:
                    self.errors.append(
                        f"Step '{step.title}' (seq {step.sequence}) has prerequisite "
                        f"'{prereq.title}' (seq {prereq.sequence}) that appears later or same position"
                    )
    
    def _validate_time_budget(self, steps: List, roadmap) -> None:
        """Validate total time stays within budget."""
        total_minutes = sum(int(step.estimated_hours * 60) for step in steps)
        
        # Get learner profile to check weekly hours and deadline
        try:
            profile = roadmap.learner_profile
            weekly_minutes = profile.weekly_hours * 60
            
            if profile.deadline:
                from django.utils import timezone
                days_until_deadline = (profile.deadline - timezone.now().date()).days
                weeks_until_deadline = max(1, days_until_deadline / 7)
                available_minutes = weekly_minutes * weeks_until_deadline
                
                if total_minutes > available_minutes:
                    self.errors.append(
                        f"Roadmap requires {total_minutes // 60} hours but only "
                        f"{available_minutes // 60} hours available before deadline"
                    )
            
            # Calculate recommended weekly commitment
            estimated_weeks = total_minutes / weekly_minutes if weekly_minutes else float('inf')
            if estimated_weeks > 52:
                self.warnings.append(
                    f"Roadmap would take approximately {estimated_weeks:.1f} weeks at "
                    f"{profile.weekly_hours} hours/week"
                )
        except Exception:
            # No profile attached, skip time budget validation
            pass
    
    def _validate_no_empty_steps(self, steps: List) -> None:
        """Ensure no steps are empty or missing key content."""
        for step in steps:
            if not step.title or len(step.title.strip()) < 3:
                self.errors.append(f"Step {step.sequence} has empty or invalid title")
            
            if not step.description or len(step.description.strip()) < 5:
                self.warnings.append(f"Step '{step.title}' has minimal content description")
            
            if step.estimated_hours <= 0:
                self.errors.append(f"Step '{step.title}' has invalid duration")
    
    def _validate_sequence_continuity(self, steps: List) -> None:
        """Ensure step sequences are continuous (no gaps)."""
        sequences = sorted(step.sequence for step in steps)
        expected = list(range(sequences[0], sequences[-1] + 1))
        
        if sequences != expected:
            missing = set(expected) - set(sequences)
            if missing:
                self.warnings.append(f"Sequence gaps at positions: {sorted(missing)}")
    
    def _validate_resources_coverage(self, steps: List) -> None:
        """Check that steps have attached resources."""
        steps_without_resources = []
        
        for step in steps:
            # Use step_resources related name instead of resources
            if step.step_resources.count() == 0:
                steps_without_resources.append(step.title)
        
        if steps_without_resources:
            self.warnings.append(
                f"{len(steps_without_resources)} steps have no resources attached"
            )
    
    def validate_profile_completeness(self, profile) -> Tuple[bool, List[str]]:
        """
        Validate that a learner profile has enough info to generate roadmap.
        
        Args:
            profile: LearnerProfile to validate
            
        Returns:
            tuple: (is_complete, missing_fields)
        """
        missing = []
        
        if not profile.subject:
            missing.append("subject")
        if not profile.current_level:
            missing.append("current_level")
        if not profile.goals:
            missing.append("goals")
        if not profile.weekly_hours or profile.weekly_hours <= 0:
            missing.append("weekly_hours")
        
        return len(missing) == 0, missing
    
    def validate_step_update(self, step, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate step update doesn't break constraints.
        
        Args:
            step: Existing step
            data: Update data
            
        Returns:
            tuple: (is_valid, errors)
        """
        errors = []
        
        if 'sequence' in data:
            new_seq = data['sequence']
            # Check if moving would break prerequisites
            for prereq in step.prerequisites.all():
                if prereq.sequence >= new_seq:
                    errors.append(
                        f"Cannot move step before its prerequisite '{prereq.title}'"
                    )
        
        if 'estimated_duration' in data:
            if data['estimated_duration'] <= 0:
                errors.append("Duration must be positive")
        
        return len(errors) == 0, errors


class RoadmapSchema:
    """JSON Schema definitions for roadmap export."""
    
    CURRENT_VERSION = "1.0"
    
    SCHEMA = {
        "1.0": {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "status": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sequence": {"type": "integer"},
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "estimated_duration": {"type": "integer"},
                            "prerequisites": {"type": "array", "items": {"type": "integer"}},
                            "resources": {"type": "array"}
                        }
                    }
                }
            }
        }
    }
    
    @classmethod
    def validate_json(cls, data: Dict, version: str = None) -> Tuple[bool, List[str]]:
        """
        Validate JSON export against schema.
        
        Note: This is a simplified validation. For production,
        use jsonschema library.
        """
        version = version or cls.CURRENT_VERSION
        errors = []
        
        if version not in cls.SCHEMA:
            errors.append(f"Unknown schema version: {version}")
            return False, errors
        
        # Basic structure validation
        required_fields = ['version', 'id', 'title', 'steps']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if 'steps' in data and isinstance(data['steps'], list):
            for i, step in enumerate(data['steps']):
                if 'sequence' not in step:
                    errors.append(f"Step {i} missing 'sequence'")
                if 'title' not in step:
                    errors.append(f"Step {i} missing 'title'")
        
        return len(errors) == 0, errors
