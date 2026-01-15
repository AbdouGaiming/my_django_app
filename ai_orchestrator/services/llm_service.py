"""
LLM Service - Integration with Groq API for Llama models
"""
import json
import requests
from typing import Dict, List, Optional
from django.conf import settings


class LLMService:
    """Service for interacting with Groq's Llama API."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GROQ_API_KEY', '')
        self.model = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.api_url = getattr(settings, 'GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    
    def _make_request(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """Make a request to the Groq API."""
        if not self.api_key:
            print("ERROR: GROQ_API_KEY is not configured")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        
        try:
            print(f"Making LLM request to {self.api_url}...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"LLM response received: {len(content)} characters")
            return content
        except requests.exceptions.RequestException as e:
            print(f"LLM API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None
        except (KeyError, IndexError) as e:
            print(f"LLM Response Parse Error: {e}")
            print(f"Response data: {data if 'data' in locals() else 'No data'}")
            return None
    
    def generate_roadmap(self, profile_data: Dict) -> Optional[Dict]:
        """
        Generate a learning roadmap using the LLM.
        
        Args:
            profile_data: Dictionary containing learner profile information
            
        Returns:
            Dictionary with roadmap structure or None on failure
        """
        system_prompt = """You are an expert learning path designer. Given a learner's profile, 
create a detailed, personalized learning roadmap. Return your response as valid JSON with the following structure:
{
    "title": "Learning Path Title",
    "description": "Brief description of the learning path",
    "estimated_total_hours": number,
    "steps": [
        {
            "sequence": number,
            "title": "Step Title",
            "description": "Detailed step description",
            "objectives": ["objective1", "objective2"],
            "topics": ["topic1", "topic2"],
            "estimated_hours": number,
            "mastery_check": "How to verify mastery of this step",
            "resources_keywords": ["keyword1", "keyword2"]
        }
    ]
}
Make the roadmap practical, achievable, and tailored to the learner's level and time constraints."""

        user_prompt = f"""Create a learning roadmap for a learner with the following profile:

Subject: {profile_data.get('subject', 'Unknown')}
Current Level: {profile_data.get('current_level', 'Beginner')}
Learning Goals: {profile_data.get('goals', 'Learn the fundamentals')}
Weekly Hours Available: {profile_data.get('weekly_hours', 5)} hours
Deadline: {profile_data.get('deadline', 'No specific deadline')}
Preferred Resources: {profile_data.get('preferred_resources', 'Any')}
Age Range: {profile_data.get('age_range', 'Adult')}
Language: {profile_data.get('language', 'English')}

Generate a comprehensive, step-by-step learning roadmap as JSON."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        print(f"Generating roadmap for: {profile_data.get('subject')}")
        response = self._make_request(messages, temperature=0.7, max_tokens=3000)
        
        if not response:
            print("No response from LLM")
            return None
        
        # Try to parse the JSON response
        try:
            # Extract JSON from the response (in case there's extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                roadmap = json.loads(json_str)
                print(f"Successfully parsed roadmap with {len(roadmap.get('steps', []))} steps")
                return roadmap
            else:
                print("No JSON object found in response")
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Response preview: {response[:500]}")
            return None
        
        return None
    
    def generate_clarifying_questions(self, profile_data: Dict, num_questions: int = 3) -> List[Dict]:
        """
        Generate clarifying questions for incomplete profile.
        
        Args:
            profile_data: Current profile information
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        system_prompt = """You are a learning consultant. Generate clarifying questions to better understand 
a learner's needs. Return your response as a JSON array with the following structure:
[
    {
        "question": "The question text",
        "question_type": "text|single_choice|multiple_choice|scale",
        "options": ["option1", "option2"] or null if text type,
        "required": true/false,
        "order": number
    }
]"""

        user_prompt = f"""Based on this learner profile, generate {num_questions} clarifying questions to better understand their learning needs:

Subject: {profile_data.get('subject', 'Unknown')}
Current Level: {profile_data.get('current_level', 'Unknown')}
Goals: {profile_data.get('goals', 'Not specified')}

Generate questions that will help create a more personalized learning path."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_request(messages, temperature=0.8, max_tokens=1000)
        
        if not response:
            return []
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            return []
        
        return []
    
    def enhance_step_description(self, step_data: Dict, context: str = "") -> str:
        """
        Enhance a roadmap step description using LLM.
        
        Args:
            step_data: The step information
            context: Additional context about the roadmap
            
        Returns:
            Enhanced description string
        """
        prompt = f"""Enhance this learning step description to be more helpful and actionable:

Step Title: {step_data.get('title', '')}
Current Description: {step_data.get('description', '')}
Topics: {', '.join(step_data.get('topics', []))}
Context: {context}

Provide an enhanced description that includes:
1. What the learner will learn
2. Why it's important
3. Prerequisites (if any)
4. Key takeaways

Keep it concise but informative (2-3 paragraphs max)."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, temperature=0.6, max_tokens=500)
        return response or step_data.get('description', '')
    
    def suggest_resources(self, topic: str, level: str = "beginner", resource_type: str = "any") -> List[Dict]:
        """
        Suggest learning resources for a topic.
        
        Args:
            topic: The topic to find resources for
            level: Learner level (beginner, intermediate, advanced)
            resource_type: Type of resource (video, article, course, book, any)
            
        Returns:
            List of suggested resources
        """
        system_prompt = """You are a learning resource curator. Suggest high-quality, free or 
affordable learning resources. Return as JSON array:
[
    {
        "title": "Resource title",
        "type": "video|article|course|book|tutorial|documentation",
        "url": "URL if known, or 'search: search terms' if not",
        "description": "Brief description",
        "difficulty": "beginner|intermediate|advanced",
        "estimated_time": "Estimated time to complete"
    }
]"""

        user_prompt = f"""Suggest 5 learning resources for:
Topic: {topic}
Level: {level}
Preferred Type: {resource_type}

Focus on well-known, reputable sources like official documentation, popular YouTube channels, Coursera, edX, freeCodeCamp, etc."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_request(messages, temperature=0.7, max_tokens=1500)
        
        if not response:
            return []
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            return []
        
        return []


# Singleton instance
llm_service = LLMService()
