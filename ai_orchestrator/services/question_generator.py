"""
Question Generator Service
Generates personalized clarifying questions based on user's subject and language.
These questions help customize the roadmap for the Algerian market.
"""
from typing import List, Dict
from profiles.models import LearnerProfile, ClarifyingQuestion


class QuestionGenerator:
    """
    Generates clarifying questions to better understand the learner's needs.
    Questions are multilingual (Arabic, French, English) and focused on the Algerian market.
    """
    
    # Base questions for all subjects
    BASE_QUESTIONS = {
        'background': [
            {
                'key': 'education_background',
                'type': 'single_choice',
                'text_ar': 'ما هو مستواك التعليمي الحالي؟',
                'text_fr': 'Quel est votre niveau d\'éducation actuel ?',
                'text_en': 'What is your current education level?',
                'options': [
                    {'value': 'primary', 'ar': 'ابتدائي', 'fr': 'Primaire', 'en': 'Primary School'},
                    {'value': 'middle', 'ar': 'متوسط', 'fr': 'Collège', 'en': 'Middle School'},
                    {'value': 'secondary', 'ar': 'ثانوي', 'fr': 'Lycée', 'en': 'Secondary School'},
                    {'value': 'bac', 'ar': 'باكالوريا', 'fr': 'Baccalauréat', 'en': 'Baccalaureate'},
                    {'value': 'licence', 'ar': 'ليسانس', 'fr': 'Licence', 'en': 'Bachelor\'s'},
                    {'value': 'master', 'ar': 'ماستر', 'fr': 'Master', 'en': 'Master\'s'},
                    {'value': 'self_taught', 'ar': 'تعلم ذاتي', 'fr': 'Autodidacte', 'en': 'Self-taught'},
                ],
                'target_field': 'education_level',
            },
            {
                'key': 'prior_experience',
                'type': 'single_choice',
                'text_ar': 'هل لديك خبرة سابقة في هذا المجال؟',
                'text_fr': 'Avez-vous une expérience préalable dans ce domaine ?',
                'text_en': 'Do you have prior experience in this field?',
                'options': [
                    {'value': 'none', 'ar': 'لا، هذا جديد بالنسبة لي', 'fr': 'Non, c\'est nouveau pour moi', 'en': 'No, this is new to me'},
                    {'value': 'little', 'ar': 'قليل جداً', 'fr': 'Très peu', 'en': 'Very little'},
                    {'value': 'some', 'ar': 'بعض الخبرة', 'fr': 'Un peu', 'en': 'Some experience'},
                    {'value': 'moderate', 'ar': 'خبرة متوسطة', 'fr': 'Expérience moyenne', 'en': 'Moderate experience'},
                ],
                'target_field': 'level',
            },
        ],
        'goals': [
            {
                'key': 'main_goal',
                'type': 'single_choice',
                'text_ar': 'ما هو هدفك الرئيسي من هذا التعلم؟',
                'text_fr': 'Quel est votre objectif principal ?',
                'text_en': 'What is your main goal from this learning?',
                'options': [
                    {'value': 'job', 'ar': 'إيجاد وظيفة', 'fr': 'Trouver un emploi', 'en': 'Find a job'},
                    {'value': 'freelance', 'ar': 'العمل الحر', 'fr': 'Freelance', 'en': 'Freelance work'},
                    {'value': 'startup', 'ar': 'بدء مشروع خاص', 'fr': 'Créer ma startup', 'en': 'Start my own business'},
                    {'value': 'skill', 'ar': 'تطوير المهارات فقط', 'fr': 'Développer mes compétences', 'en': 'Just develop skills'},
                    {'value': 'career_change', 'ar': 'تغيير المسار المهني', 'fr': 'Changer de carrière', 'en': 'Career change'},
                ],
                'target_field': 'goals',
            },
            {
                'key': 'job_seeking',
                'type': 'yes_no',
                'text_ar': 'هل تبحث عن فرص عمل في الجزائر؟',
                'text_fr': 'Cherchez-vous des opportunités d\'emploi en Algérie ?',
                'text_en': 'Are you looking for job opportunities in Algeria?',
                'options': [
                    {'value': 'yes', 'ar': 'نعم', 'fr': 'Oui', 'en': 'Yes'},
                    {'value': 'no', 'ar': 'لا', 'fr': 'Non', 'en': 'No'},
                ],
                'target_field': 'seeking_job',
            },
        ],
        'preferences': [
            {
                'key': 'learning_style',
                'type': 'single_choice',
                'text_ar': 'كيف تفضل التعلم؟',
                'text_fr': 'Comment préférez-vous apprendre ?',
                'text_en': 'How do you prefer to learn?',
                'options': [
                    {'value': 'video', 'ar': 'مشاهدة فيديوهات', 'fr': 'Regarder des vidéos', 'en': 'Watch videos'},
                    {'value': 'reading', 'ar': 'قراءة كتب ومقالات', 'fr': 'Lire des livres et articles', 'en': 'Read books and articles'},
                    {'value': 'practice', 'ar': 'التطبيق العملي المباشر', 'fr': 'Pratique directe', 'en': 'Hands-on practice'},
                    {'value': 'mixed', 'ar': 'مزيج من كل شيء', 'fr': 'Un mélange de tout', 'en': 'Mix of everything'},
                ],
                'target_field': '',
            },
            {
                'key': 'content_language',
                'type': 'multiple_choice',
                'text_ar': 'بأي لغة تفضل المحتوى التعليمي؟',
                'text_fr': 'En quelle langue préférez-vous le contenu éducatif ?',
                'text_en': 'In which language do you prefer learning content?',
                'options': [
                    {'value': 'ar', 'ar': 'العربية', 'fr': 'Arabe', 'en': 'Arabic'},
                    {'value': 'fr', 'ar': 'الفرنسية', 'fr': 'Français', 'en': 'French'},
                    {'value': 'en', 'ar': 'الإنجليزية', 'fr': 'Anglais', 'en': 'English'},
                ],
                'target_field': '',
            },
        ],
        'availability': [
            {
                'key': 'hours_per_week',
                'type': 'single_choice',
                'text_ar': 'كم ساعة يمكنك تخصيصها للتعلم في الأسبوع؟',
                'text_fr': 'Combien d\'heures pouvez-vous consacrer à l\'apprentissage par semaine ?',
                'text_en': 'How many hours per week can you dedicate to learning?',
                'options': [
                    {'value': '2', 'ar': 'أقل من 3 ساعات', 'fr': 'Moins de 3 heures', 'en': 'Less than 3 hours'},
                    {'value': '5', 'ar': '3-5 ساعات', 'fr': '3-5 heures', 'en': '3-5 hours'},
                    {'value': '10', 'ar': '5-10 ساعات', 'fr': '5-10 heures', 'en': '5-10 hours'},
                    {'value': '15', 'ar': '10-15 ساعة', 'fr': '10-15 heures', 'en': '10-15 hours'},
                    {'value': '20', 'ar': 'أكثر من 15 ساعة', 'fr': 'Plus de 15 heures', 'en': 'More than 15 hours'},
                ],
                'target_field': 'weekly_hours',
            },
            {
                'key': 'urgency',
                'type': 'single_choice',
                'text_ar': 'ما مدى السرعة التي تريد بها إنهاء هذا المسار؟',
                'text_fr': 'À quelle vitesse voulez-vous terminer ce parcours ?',
                'text_en': 'How quickly do you want to finish this learning path?',
                'options': [
                    {'value': 'relaxed', 'ar': 'على مهلي، لا استعجال', 'fr': 'Pas pressé, à mon rythme', 'en': 'No rush, at my own pace'},
                    {'value': '6months', 'ar': 'خلال 6 أشهر', 'fr': 'Dans les 6 mois', 'en': 'Within 6 months'},
                    {'value': '3months', 'ar': 'خلال 3 أشهر', 'fr': 'Dans les 3 mois', 'en': 'Within 3 months'},
                    {'value': 'urgent', 'ar': 'في أسرع وقت ممكن', 'fr': 'Le plus vite possible', 'en': 'As soon as possible'},
                ],
                'target_field': '',
            },
        ],
        'job_market': [
            {
                'key': 'preferred_wilaya',
                'type': 'single_choice',
                'text_ar': 'في أي ولاية تبحث عن فرص عمل؟',
                'text_fr': 'Dans quelle wilaya cherchez-vous des opportunités ?',
                'text_en': 'In which wilaya are you looking for opportunities?',
                'options': [
                    {'value': 'alger', 'ar': 'الجزائر العاصمة', 'fr': 'Alger', 'en': 'Algiers'},
                    {'value': 'oran', 'ar': 'وهران', 'fr': 'Oran', 'en': 'Oran'},
                    {'value': 'constantine', 'ar': 'قسنطينة', 'fr': 'Constantine', 'en': 'Constantine'},
                    {'value': 'annaba', 'ar': 'عنابة', 'fr': 'Annaba', 'en': 'Annaba'},
                    {'value': 'setif', 'ar': 'سطيف', 'fr': 'Sétif', 'en': 'Sétif'},
                    {'value': 'remote', 'ar': 'عمل عن بعد', 'fr': 'Télétravail', 'en': 'Remote work'},
                    {'value': 'any', 'ar': 'أي ولاية', 'fr': 'Toute wilaya', 'en': 'Any wilaya'},
                ],
                'target_field': 'wilaya',
            },
            {
                'key': 'work_preference',
                'type': 'single_choice',
                'text_ar': 'ما نوع العمل الذي تفضله؟',
                'text_fr': 'Quel type de travail préférez-vous ?',
                'text_en': 'What type of work do you prefer?',
                'options': [
                    {'value': 'employee', 'ar': 'موظف في شركة', 'fr': 'Employé d\'entreprise', 'en': 'Company employee'},
                    {'value': 'freelance', 'ar': 'عمل حر (فريلانس)', 'fr': 'Freelance', 'en': 'Freelance'},
                    {'value': 'startup', 'ar': 'مؤسس شركة ناشئة', 'fr': 'Fondateur de startup', 'en': 'Startup founder'},
                    {'value': 'government', 'ar': 'قطاع حكومي', 'fr': 'Secteur public', 'en': 'Government sector'},
                    {'value': 'any', 'ar': 'أي نوع', 'fr': 'N\'importe quel type', 'en': 'Any type'},
                ],
                'target_field': '',
            },
        ],
    }
    
    # Subject-specific questions
    SUBJECT_QUESTIONS = {
        'python': [
            {
                'key': 'python_goal',
                'type': 'single_choice',
                'category': 'goals',
                'text_ar': 'ما الذي تريد استخدام بايثون فيه؟',
                'text_fr': 'Pour quoi voulez-vous utiliser Python ?',
                'text_en': 'What do you want to use Python for?',
                'options': [
                    {'value': 'web', 'ar': 'تطوير مواقع الويب (Django/Flask)', 'fr': 'Développement web (Django/Flask)', 'en': 'Web development (Django/Flask)'},
                    {'value': 'data', 'ar': 'علوم البيانات والذكاء الاصطناعي', 'fr': 'Data Science et IA', 'en': 'Data Science and AI'},
                    {'value': 'automation', 'ar': 'أتمتة المهام والسكريبتات', 'fr': 'Automatisation et scripts', 'en': 'Automation and scripting'},
                    {'value': 'general', 'ar': 'برمجة عامة', 'fr': 'Programmation générale', 'en': 'General programming'},
                ],
            },
        ],
        'javascript': [
            {
                'key': 'js_focus',
                'type': 'single_choice',
                'category': 'goals',
                'text_ar': 'ما هو تركيزك في JavaScript؟',
                'text_fr': 'Quel est votre focus en JavaScript ?',
                'text_en': 'What is your focus in JavaScript?',
                'options': [
                    {'value': 'frontend', 'ar': 'Frontend (React/Vue)', 'fr': 'Frontend (React/Vue)', 'en': 'Frontend (React/Vue)'},
                    {'value': 'backend', 'ar': 'Backend (Node.js)', 'fr': 'Backend (Node.js)', 'en': 'Backend (Node.js)'},
                    {'value': 'fullstack', 'ar': 'Full Stack', 'fr': 'Full Stack', 'en': 'Full Stack'},
                    {'value': 'mobile', 'ar': 'تطبيقات موبايل (React Native)', 'fr': 'Apps mobiles (React Native)', 'en': 'Mobile apps (React Native)'},
                ],
            },
        ],
        'data_science': [
            {
                'key': 'ds_interest',
                'type': 'single_choice',
                'category': 'goals',
                'text_ar': 'ما هو مجال اهتمامك في علوم البيانات؟',
                'text_fr': 'Quel est votre domaine d\'intérêt en Data Science ?',
                'text_en': 'What is your area of interest in Data Science?',
                'options': [
                    {'value': 'analysis', 'ar': 'تحليل البيانات', 'fr': 'Analyse de données', 'en': 'Data Analysis'},
                    {'value': 'ml', 'ar': 'تعلم الآلة', 'fr': 'Machine Learning', 'en': 'Machine Learning'},
                    {'value': 'dl', 'ar': 'التعلم العميق', 'fr': 'Deep Learning', 'en': 'Deep Learning'},
                    {'value': 'bi', 'ar': 'ذكاء الأعمال', 'fr': 'Business Intelligence', 'en': 'Business Intelligence'},
                ],
            },
        ],
        'web_development': [
            {
                'key': 'web_path',
                'type': 'single_choice',
                'category': 'goals',
                'text_ar': 'أي مسار في تطوير الويب تريد؟',
                'text_fr': 'Quel parcours de développement web voulez-vous ?',
                'text_en': 'Which web development path do you want?',
                'options': [
                    {'value': 'frontend', 'ar': 'Frontend فقط', 'fr': 'Frontend uniquement', 'en': 'Frontend only'},
                    {'value': 'backend', 'ar': 'Backend فقط', 'fr': 'Backend uniquement', 'en': 'Backend only'},
                    {'value': 'fullstack', 'ar': 'Full Stack (الكل)', 'fr': 'Full Stack (tout)', 'en': 'Full Stack (everything)'},
                ],
            },
        ],
    }
    
    def __init__(self, profile: LearnerProfile):
        self.profile = profile
        self.language = profile.language or 'ar'
    
    def generate_questions(self) -> List[ClarifyingQuestion]:
        """
        Generate all clarifying questions for the profile.
        Returns list of created ClarifyingQuestion instances.
        """
        questions = []
        order = 1
        
        # Generate base questions for all categories
        for category, category_questions in self.BASE_QUESTIONS.items():
            for q_data in category_questions:
                question = self._create_question(q_data, category, order)
                questions.append(question)
                order += 1
        
        # Add subject-specific questions
        subject = self.profile.subject.lower().replace(' ', '_')
        if subject in self.SUBJECT_QUESTIONS:
            for q_data in self.SUBJECT_QUESTIONS[subject]:
                category = q_data.get('category', 'goals')
                question = self._create_question(q_data, category, order)
                questions.append(question)
                order += 1
        
        return questions
    
    def _create_question(self, q_data: Dict, category: str, order: int) -> ClarifyingQuestion:
        """Create a ClarifyingQuestion instance from question data."""
        # Get text in user's preferred language
        text_key = f'text_{self.language}' if self.language != 'ar_dz' else 'text_ar'
        question_text = q_data.get(text_key, q_data.get('text_ar', ''))
        
        # Format options for the user's language
        formatted_options = []
        for opt in q_data.get('options', []):
            lang_key = self.language if self.language != 'ar_dz' else 'ar'
            formatted_options.append({
                'value': opt['value'],
                'label': opt.get(lang_key, opt.get('ar', '')),
                'label_ar': opt.get('ar', ''),
                'label_fr': opt.get('fr', ''),
                'label_en': opt.get('en', ''),
            })
        
        question = ClarifyingQuestion.objects.create(
            learner_profile=self.profile,
            question_text=question_text,
            question_text_ar=q_data.get('text_ar', ''),
            question_text_fr=q_data.get('text_fr', ''),
            question_text_en=q_data.get('text_en', ''),
            question_type=q_data.get('type', 'single_choice'),
            category=category,
            options=formatted_options,
            target_field=q_data.get('target_field') or '',
            order=order,
            is_required=True,
        )
        
        return question
    
    def get_question_text(self, question: ClarifyingQuestion) -> str:
        """Get question text in user's preferred language."""
        if self.language == 'fr' and question.question_text_fr:
            return question.question_text_fr
        elif self.language in ['en'] and question.question_text_en:
            return question.question_text_en
        return question.question_text_ar or question.question_text
    
    def get_option_label(self, option: Dict) -> str:
        """Get option label in user's preferred language."""
        lang_key = f'label_{self.language}' if self.language != 'ar_dz' else 'label_ar'
        return option.get(lang_key, option.get('label', ''))


def generate_questions_for_profile(profile: LearnerProfile) -> List[ClarifyingQuestion]:
    """
    Convenience function to generate questions for a profile.
    
    Args:
        profile: LearnerProfile instance
        
    Returns:
        list: List of ClarifyingQuestion instances
    """
    generator = QuestionGenerator(profile)
    return generator.generate_questions()
