"""
Management command to populate initial Algeria market data.
Run with: python manage.py populate_algeria_data
"""
from django.core.management.base import BaseCommand
from ai_orchestrator.services import AlgerianMarketAnalyzer, ResourceRecommender


class Command(BaseCommand):
    help = 'Populates initial data for Algerian companies, skill demands, and resources'
    
    def handle(self, *args, **options):
        self.stdout.write('🇩🇿 Populating Algeria market data...\n')
        
        # Populate companies and skill demands
        self.stdout.write('📊 Adding skill demands and companies...')
        analyzer = AlgerianMarketAnalyzer()
        analyzer.sync_to_database()
        self.stdout.write(self.style.SUCCESS('✓ Companies and skills added\n'))
        
        # Populate learning resources
        self.stdout.write('📚 Adding learning resources...')
        recommender = ResourceRecommender()
        for subject in ['python', 'javascript', 'web_development', 'data_science']:
            recommender.sync_to_database(subject)
            self.stdout.write(f'  ✓ {subject} resources added')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 All data populated successfully!'))
        self.stdout.write(self.style.SUCCESS('You can now start using the app with Algerian market data.'))
