"""
Algerian Market Analyzer Service
Analyzes skill demand and job opportunities in the Algerian tech market.
"""
from typing import List, Dict, Optional
from profiles.models import SkillDemand, AlgerianCompany, JobOpportunity, LearnerProfile


class AlgerianMarketAnalyzer:
    """
    Analyzes the Algerian tech job market to provide relevant insights
    for learners about skill demand and job opportunities.
    """
    
    # Skill demand data for Algeria (can be updated from real data sources)
    SKILL_DEMAND_DATA = {
        # High demand skills in Algeria
        'python': {
            'demand_score': 0.9,
            'growth_trend': 'rising',
            'average_salary': '80,000 - 150,000 DZD',
            'related_skills': ['django', 'flask', 'pandas', 'machine_learning'],
            'job_count': 45,
            'category': 'programming',
        },
        'javascript': {
            'demand_score': 0.95,
            'growth_trend': 'rising',
            'average_salary': '70,000 - 140,000 DZD',
            'related_skills': ['react', 'vue', 'nodejs', 'typescript'],
            'job_count': 60,
            'category': 'programming',
        },
        'react': {
            'demand_score': 0.85,
            'growth_trend': 'rising',
            'average_salary': '90,000 - 160,000 DZD',
            'related_skills': ['javascript', 'typescript', 'redux', 'next.js'],
            'job_count': 35,
            'category': 'frontend',
        },
        'php': {
            'demand_score': 0.75,
            'growth_trend': 'stable',
            'average_salary': '60,000 - 120,000 DZD',
            'related_skills': ['laravel', 'wordpress', 'mysql'],
            'job_count': 40,
            'category': 'programming',
        },
        'django': {
            'demand_score': 0.7,
            'growth_trend': 'rising',
            'average_salary': '90,000 - 160,000 DZD',
            'related_skills': ['python', 'rest_api', 'postgresql'],
            'job_count': 20,
            'category': 'backend',
        },
        'data_science': {
            'demand_score': 0.65,
            'growth_trend': 'rising',
            'average_salary': '100,000 - 200,000 DZD',
            'related_skills': ['python', 'machine_learning', 'sql', 'tableau'],
            'job_count': 15,
            'category': 'data',
        },
        'mobile_development': {
            'demand_score': 0.8,
            'growth_trend': 'rising',
            'average_salary': '80,000 - 150,000 DZD',
            'related_skills': ['flutter', 'react_native', 'kotlin', 'swift'],
            'job_count': 30,
            'category': 'mobile',
        },
        'devops': {
            'demand_score': 0.6,
            'growth_trend': 'rising',
            'average_salary': '120,000 - 200,000 DZD',
            'related_skills': ['docker', 'kubernetes', 'aws', 'linux'],
            'job_count': 12,
            'category': 'infrastructure',
        },
        'cybersecurity': {
            'demand_score': 0.55,
            'growth_trend': 'rising',
            'average_salary': '130,000 - 220,000 DZD',
            'related_skills': ['networking', 'linux', 'penetration_testing'],
            'job_count': 8,
            'category': 'security',
        },
        'ui_ux_design': {
            'demand_score': 0.65,
            'growth_trend': 'stable',
            'average_salary': '70,000 - 130,000 DZD',
            'related_skills': ['figma', 'adobe_xd', 'user_research'],
            'job_count': 18,
            'category': 'design',
        },
        'sql': {
            'demand_score': 0.8,
            'growth_trend': 'stable',
            'average_salary': '60,000 - 110,000 DZD',
            'related_skills': ['postgresql', 'mysql', 'data_analysis'],
            'job_count': 50,
            'category': 'database',
        },
    }
    
    # Sample Algerian companies (can be expanded)
    ALGERIAN_COMPANIES = [
        {
            'name': 'Yassir',
            'name_ar': 'ياسر',
            'description': 'Leading ride-hailing and delivery app in Algeria',
            'description_ar': 'تطبيق رائد للنقل والتوصيل في الجزائر',
            'company_type': 'startup',
            'industry': 'tech',
            'wilaya': 'alger',
            'website': 'https://yassir.com',
            'required_skills': ['python', 'react', 'mobile_development', 'devops'],
            'is_hiring': True,
            'remote_friendly': True,
        },
        {
            'name': 'Djezzy (Optimum Telecom)',
            'name_ar': 'جيزي',
            'description': 'Major telecommunications company in Algeria',
            'description_ar': 'شركة اتصالات رائدة في الجزائر',
            'company_type': 'enterprise',
            'industry': 'telecom',
            'wilaya': 'alger',
            'website': 'https://djezzy.dz',
            'required_skills': ['java', 'python', 'networking', 'sql'],
            'is_hiring': True,
            'remote_friendly': False,
        },
        {
            'name': 'Ooredoo Algeria',
            'name_ar': 'أوريدو الجزائر',
            'description': 'Telecommunications and internet services',
            'description_ar': 'خدمات الاتصالات والإنترنت',
            'company_type': 'multinational',
            'industry': 'telecom',
            'wilaya': 'alger',
            'website': 'https://ooredoo.dz',
            'required_skills': ['java', 'python', 'cloud', 'data_science'],
            'is_hiring': True,
            'remote_friendly': False,
        },
        {
            'name': 'Sonatrach',
            'name_ar': 'سوناطراك',
            'description': 'National oil and gas company with IT needs',
            'description_ar': 'الشركة الوطنية للنفط والغاز',
            'company_type': 'government',
            'industry': 'energy',
            'wilaya': 'alger',
            'website': 'https://sonatrach.com',
            'required_skills': ['python', 'data_science', 'erp', 'cybersecurity'],
            'is_hiring': True,
            'remote_friendly': False,
        },
        {
            'name': 'TemTem One',
            'name_ar': 'تمتم ون',
            'description': 'Delivery and logistics platform',
            'description_ar': 'منصة توصيل ولوجستيك',
            'company_type': 'startup',
            'industry': 'ecommerce',
            'wilaya': 'alger',
            'website': 'https://temtemone.com',
            'required_skills': ['react', 'nodejs', 'mobile_development'],
            'is_hiring': True,
            'remote_friendly': True,
        },
        {
            'name': 'Emploitic',
            'name_ar': 'إمبلويتيك',
            'description': 'Leading job search platform in Algeria',
            'description_ar': 'منصة البحث عن العمل الرائدة في الجزائر',
            'company_type': 'startup',
            'industry': 'tech',
            'wilaya': 'alger',
            'website': 'https://emploitic.com',
            'required_skills': ['php', 'javascript', 'mysql', 'react'],
            'is_hiring': True,
            'remote_friendly': True,
        },
        {
            'name': 'Jumia Algeria',
            'name_ar': 'جوميا الجزائر',
            'description': 'E-commerce platform',
            'description_ar': 'منصة التجارة الإلكترونية',
            'company_type': 'multinational',
            'industry': 'ecommerce',
            'wilaya': 'alger',
            'website': 'https://jumia.dz',
            'required_skills': ['python', 'java', 'data_science', 'devops'],
            'is_hiring': True,
            'remote_friendly': False,
        },
        {
            'name': 'KPMG Algeria',
            'name_ar': 'كي بي إم جي الجزائر',
            'description': 'Consulting and technology services',
            'description_ar': 'خدمات استشارية وتكنولوجية',
            'company_type': 'multinational',
            'industry': 'services',
            'wilaya': 'alger',
            'website': 'https://kpmg.com/dz',
            'required_skills': ['python', 'sql', 'data_science', 'erp'],
            'is_hiring': True,
            'remote_friendly': False,
        },
    ]
    
    def __init__(self, profile: Optional[LearnerProfile] = None):
        self.profile = profile
    
    def get_skill_demand(self, skill: str) -> Dict:
        """
        Get demand information for a specific skill.
        
        Args:
            skill: Skill name (normalized)
            
        Returns:
            dict: Skill demand data
        """
        skill_key = skill.lower().replace(' ', '_').replace('-', '_')
        
        if skill_key in self.SKILL_DEMAND_DATA:
            return self.SKILL_DEMAND_DATA[skill_key]
        
        # Try partial match
        for key, data in self.SKILL_DEMAND_DATA.items():
            if skill_key in key or key in skill_key:
                return data
        
        # Default for unknown skills
        return {
            'demand_score': 0.5,
            'growth_trend': 'stable',
            'average_salary': 'N/A',
            'related_skills': [],
            'job_count': 0,
            'category': 'unknown',
        }
    
    def get_market_insights(self, subject: str, language: str = 'ar') -> Dict:
        """
        Get market insights for a subject in the specified language.
        
        Args:
            subject: Learning subject
            language: User's preferred language
            
        Returns:
            dict: Market insights with multilingual content
        """
        skill_data = self.get_skill_demand(subject)
        
        # Generate insights in the user's language
        insights = {
            'subject': subject,
            'demand_score': skill_data['demand_score'],
            'demand_level': self._get_demand_level(skill_data['demand_score'], language),
            'growth_trend': skill_data['growth_trend'],
            'growth_text': self._get_growth_text(skill_data['growth_trend'], language),
            'average_salary': skill_data['average_salary'],
            'job_count': skill_data['job_count'],
            'related_skills': skill_data['related_skills'],
            'message': self._generate_insight_message(subject, skill_data, language),
        }
        
        return insights
    
    def _get_demand_level(self, score: float, language: str) -> str:
        """Get demand level text in user's language."""
        levels = {
            'high': {'ar': 'طلب مرتفع جداً', 'fr': 'Très forte demande', 'en': 'Very high demand'},
            'good': {'ar': 'طلب جيد', 'fr': 'Bonne demande', 'en': 'Good demand'},
            'moderate': {'ar': 'طلب متوسط', 'fr': 'Demande modérée', 'en': 'Moderate demand'},
            'low': {'ar': 'طلب منخفض', 'fr': 'Faible demande', 'en': 'Low demand'},
        }
        
        if score >= 0.8:
            level = 'high'
        elif score >= 0.6:
            level = 'good'
        elif score >= 0.4:
            level = 'moderate'
        else:
            level = 'low'
        
        lang = language if language in ['ar', 'fr', 'en'] else 'ar'
        return levels[level][lang]
    
    def _get_growth_text(self, trend: str, language: str) -> str:
        """Get growth trend text in user's language."""
        trends = {
            'rising': {'ar': '📈 في ارتفاع', 'fr': '📈 En hausse', 'en': '📈 Rising'},
            'stable': {'ar': '➡️ مستقر', 'fr': '➡️ Stable', 'en': '➡️ Stable'},
            'declining': {'ar': '📉 في انخفاض', 'fr': '📉 En baisse', 'en': '📉 Declining'},
        }
        
        lang = language if language in ['ar', 'fr', 'en'] else 'ar'
        return trends.get(trend, trends['stable'])[lang]
    
    def _generate_insight_message(self, subject: str, skill_data: Dict, language: str) -> str:
        """Generate a personalized insight message."""
        messages = {
            'ar': {
                'high': f"🌟 مهارة {subject} مطلوبة جداً في السوق الجزائرية! هناك حوالي {skill_data['job_count']} فرصة عمل متاحة حالياً.",
                'good': f"✅ {subject} لها طلب جيد في الجزائر. استمر في التعلم لتحسين فرصك!",
                'moderate': f"📊 {subject} لها طلب متوسط في الجزائر. قد تحتاج لتعلم مهارات إضافية مكملة.",
                'low': f"⚠️ {subject} لها طلب محدود حالياً في الجزائر. فكر في دمجها مع مهارات أخرى مطلوبة.",
            },
            'fr': {
                'high': f"🌟 La compétence {subject} est très demandée sur le marché algérien! Il y a environ {skill_data['job_count']} opportunités d'emploi disponibles.",
                'good': f"✅ {subject} a une bonne demande en Algérie. Continuez à apprendre pour améliorer vos chances!",
                'moderate': f"📊 {subject} a une demande modérée en Algérie. Vous pourriez avoir besoin de compétences complémentaires.",
                'low': f"⚠️ {subject} a une demande limitée actuellement en Algérie. Pensez à la combiner avec d'autres compétences demandées.",
            },
            'en': {
                'high': f"🌟 {subject} skill is in very high demand in the Algerian market! There are about {skill_data['job_count']} job opportunities currently available.",
                'good': f"✅ {subject} has good demand in Algeria. Keep learning to improve your chances!",
                'moderate': f"📊 {subject} has moderate demand in Algeria. You may need to learn complementary skills.",
                'low': f"⚠️ {subject} has limited demand currently in Algeria. Consider combining it with other in-demand skills.",
            },
        }
        
        score = skill_data['demand_score']
        if score >= 0.8:
            level = 'high'
        elif score >= 0.6:
            level = 'good'
        elif score >= 0.4:
            level = 'moderate'
        else:
            level = 'low'
        
        lang = language if language in ['ar', 'fr', 'en'] else 'ar'
        return messages[lang][level]
    
    def get_matching_companies(self, skills: List[str], wilaya: str = None) -> List[Dict]:
        """
        Get companies that hire for the given skills.
        
        Args:
            skills: List of skills
            wilaya: Optional wilaya filter
            
        Returns:
            list: Matching companies
        """
        matching = []
        skill_set = set(s.lower().replace(' ', '_') for s in skills)
        
        for company in self.ALGERIAN_COMPANIES:
            company_skills = set(s.lower().replace(' ', '_') for s in company['required_skills'])
            match_score = len(skill_set.intersection(company_skills)) / len(company_skills) if company_skills else 0
            
            if match_score > 0:
                if wilaya and company['wilaya'] != wilaya and company['wilaya'] != 'remote':
                    continue
                
                matching.append({
                    **company,
                    'match_score': match_score,
                })
        
        # Sort by match score
        matching.sort(key=lambda x: x['match_score'], reverse=True)
        return matching[:10]  # Return top 10
    
    def get_recommended_skills(self, current_skills: List[str], language: str = 'ar') -> List[Dict]:
        """
        Recommend additional skills based on current skills and market demand.
        
        Args:
            current_skills: Skills the user is learning/has
            language: User's preferred language
            
        Returns:
            list: Recommended skills with reasons
        """
        recommended = []
        current_set = set(s.lower().replace(' ', '_') for s in current_skills)
        
        # Find related skills that are in demand
        for skill in current_skills:
            skill_data = self.get_skill_demand(skill)
            for related in skill_data.get('related_skills', []):
                if related not in current_set:
                    related_data = self.get_skill_demand(related)
                    recommended.append({
                        'skill': related,
                        'demand_score': related_data['demand_score'],
                        'reason': self._get_recommendation_reason(skill, related, language),
                    })
        
        # Remove duplicates and sort by demand
        seen = set()
        unique_recommended = []
        for r in recommended:
            if r['skill'] not in seen:
                seen.add(r['skill'])
                unique_recommended.append(r)
        
        unique_recommended.sort(key=lambda x: x['demand_score'], reverse=True)
        return unique_recommended[:5]
    
    def _get_recommendation_reason(self, base_skill: str, related_skill: str, language: str) -> str:
        """Generate recommendation reason in user's language."""
        reasons = {
            'ar': f"مكمل ل {base_skill} ومطلوب في السوق",
            'fr': f"Complémentaire à {base_skill} et demandé sur le marché",
            'en': f"Complementary to {base_skill} and in demand",
        }
        lang = language if language in ['ar', 'fr', 'en'] else 'ar'
        return reasons[lang]
    
    def sync_to_database(self):
        """
        Sync skill demand and company data to the database.
        Call this to populate the database with initial data.
        """
        # Sync skill demands
        for skill_name, data in self.SKILL_DEMAND_DATA.items():
            SkillDemand.objects.update_or_create(
                skill_name=skill_name,
                defaults={
                    'demand_score': data['demand_score'],
                    'growth_trend': data['growth_trend'],
                    'average_salary': data['average_salary'],
                    'related_skills': data['related_skills'],
                    'job_count': data['job_count'],
                    'category': data['category'],
                }
            )
        
        # Sync companies
        for company_data in self.ALGERIAN_COMPANIES:
            AlgerianCompany.objects.update_or_create(
                name=company_data['name'],
                defaults={
                    'name_ar': company_data.get('name_ar', ''),
                    'description': company_data.get('description', ''),
                    'description_ar': company_data.get('description_ar', ''),
                    'company_type': company_data.get('company_type', 'sme'),
                    'industry': company_data.get('industry', 'tech'),
                    'wilaya': company_data.get('wilaya', 'alger'),
                    'website': company_data.get('website', ''),
                    'required_skills': company_data.get('required_skills', []),
                    'is_hiring': company_data.get('is_hiring', True),
                    'remote_friendly': company_data.get('remote_friendly', False),
                }
            )


def get_market_analysis(subject: str, language: str = 'ar') -> Dict:
    """
    Convenience function to get market analysis for a subject.
    
    Args:
        subject: Learning subject
        language: User's preferred language
        
    Returns:
        dict: Market insights
    """
    analyzer = AlgerianMarketAnalyzer()
    return analyzer.get_market_insights(subject, language)
