#!/usr/bin/env python
"""
Test script to verify Groq API integration for roadmap generation
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_site.settings')
django.setup()

from ai_orchestrator.services.llm_service import llm_service

print("=" * 60)
print("Testing Groq API Roadmap Generation")
print("=" * 60)

# Test profile data
profile_data = {
    'subject': 'Python Programming',
    'current_level': 'beginner',
    'goals': 'I want to become a backend developer and build web applications',
    'weekly_hours': 10,
    'deadline': None,
    'preferred_resources': ['video', 'interactive', 'project'],
}

print("\n📋 Profile Data:")
print(f"  Subject: {profile_data['subject']}")
print(f"  Level: {profile_data['current_level']}")
print(f"  Weekly Hours: {profile_data['weekly_hours']}")
print(f"  Goals: {profile_data['goals']}")

print("\n🚀 Generating roadmap with Llama 3.3...")
roadmap_data = llm_service.generate_roadmap(profile_data)

if roadmap_data:
    print("\n✅ SUCCESS! Roadmap generated:")
    print(f"  Title: {roadmap_data.get('title')}")
    print(f"  Description: {roadmap_data.get('description', '')[:100]}...")
    print(f"  Estimated Total Hours: {roadmap_data.get('estimated_total_hours')}")
    print(f"  Number of Steps: {len(roadmap_data.get('steps', []))}")
    
    print("\n📚 Steps:")
    for i, step in enumerate(roadmap_data.get('steps', [])[:3], 1):
        print(f"  {i}. {step.get('title')} ({step.get('estimated_hours')}h)")
        print(f"     {step.get('description', '')[:80]}...")
    
    if len(roadmap_data.get('steps', [])) > 3:
        print(f"  ... and {len(roadmap_data.get('steps', [])) - 3} more steps")
    
    print("\n✅ API Integration is working perfectly!")
else:
    print("\n❌ FAILED: No roadmap data returned")
    print("Check the logs above for error details")

print("\n" + "=" * 60)
