"""
Roadmap Planner Service
Generates learning steps from prerequisite graph with time constraints.
Focused on the Algerian market with multilingual support.
"""
from datetime import date, timedelta
from typing import List, Dict
from profiles.models import LearnerProfile
from roadmaps.models import Roadmap, RoadmapStep


class RoadmapPlanner:
    """
    Plans learning roadmaps based on profile and constraints.
    Tailored for the Algerian job market with Arabic, French, and English support.
    """
    
    # Prerequisite graph for common subjects - Updated with Algerian market focus
    PREREQUISITE_GRAPHS = {
        'python': [
            {
                'id': 1,
                'title': 'Python Basics',
                'title_ar': 'أساسيات بايثون',
                'title_fr': 'Les bases de Python',
                'topics': ['syntax', 'variables', 'data types'],
                'topics_ar': ['بناء الجملة', 'المتغيرات', 'أنواع البيانات'],
                'hours': 8,
                'prereqs': [],
                'market_relevance': 0.9,
                'algeria_jobs': 45,
            },
            {
                'id': 2,
                'title': 'Control Flow',
                'title_ar': 'التحكم في سير البرنامج',
                'title_fr': 'Contrôle de flux',
                'topics': ['if/else', 'loops', 'exceptions'],
                'topics_ar': ['الشروط', 'الحلقات', 'الاستثناءات'],
                'hours': 6,
                'prereqs': [1],
                'market_relevance': 0.9,
            },
            {
                'id': 3,
                'title': 'Functions & Modules',
                'title_ar': 'الدوال والوحدات',
                'title_fr': 'Fonctions et Modules',
                'topics': ['functions', 'modules', 'packages'],
                'topics_ar': ['الدوال', 'الوحدات', 'الحزم'],
                'hours': 8,
                'prereqs': [2],
                'market_relevance': 0.85,
            },
            {
                'id': 4,
                'title': 'Data Structures',
                'title_ar': 'هياكل البيانات',
                'title_fr': 'Structures de données',
                'topics': ['lists', 'dicts', 'sets', 'tuples'],
                'topics_ar': ['القوائم', 'القواميس', 'المجموعات'],
                'hours': 10,
                'prereqs': [3],
                'market_relevance': 0.9,
            },
            {
                'id': 5,
                'title': 'Object-Oriented Programming',
                'title_ar': 'البرمجة كائنية التوجه',
                'title_fr': 'Programmation Orientée Objet',
                'topics': ['classes', 'inheritance', 'polymorphism'],
                'topics_ar': ['الأصناف', 'الوراثة', 'تعدد الأشكال'],
                'hours': 12,
                'prereqs': [4],
                'market_relevance': 0.85,
            },
            {
                'id': 6,
                'title': 'File I/O & APIs',
                'title_ar': 'التعامل مع الملفات والـ APIs',
                'title_fr': 'Fichiers et APIs',
                'topics': ['file handling', 'JSON', 'REST APIs'],
                'topics_ar': ['معالجة الملفات', 'JSON', 'واجهات REST'],
                'hours': 8,
                'prereqs': [4],
                'market_relevance': 0.95,
                'algeria_jobs': 30,
            },
            {
                'id': 7,
                'title': 'Django Basics (High Demand in Algeria)',
                'title_ar': 'أساسيات Django (مطلوب جداً في الجزائر)',
                'title_fr': 'Bases de Django (Très demandé en Algérie)',
                'topics': ['django setup', 'models', 'views', 'templates'],
                'topics_ar': ['إعداد Django', 'النماذج', 'العروض', 'القوالب'],
                'hours': 15,
                'prereqs': [5, 6],
                'market_relevance': 0.95,
                'algeria_jobs': 20,
            },
            {
                'id': 8,
                'title': 'Project: Build a Real Application',
                'title_ar': 'مشروع: بناء تطبيق حقيقي',
                'title_fr': 'Projet: Construire une application réelle',
                'topics': ['portfolio project', 'deployment', 'github'],
                'topics_ar': ['مشروع للبورتفوليو', 'النشر', 'GitHub'],
                'hours': 20,
                'prereqs': [7],
                'market_relevance': 1.0,
            },
        ],
        'javascript': [
            {
                'id': 1,
                'title': 'JavaScript Fundamentals',
                'title_ar': 'أساسيات جافاسكريبت',
                'title_fr': 'Fondamentaux JavaScript',
                'topics': ['syntax', 'variables', 'types'],
                'topics_ar': ['بناء الجملة', 'المتغيرات', 'الأنواع'],
                'hours': 8,
                'prereqs': [],
                'market_relevance': 0.95,
                'algeria_jobs': 60,
            },
            {
                'id': 2,
                'title': 'DOM Manipulation',
                'title_ar': 'التعامل مع DOM',
                'title_fr': 'Manipulation du DOM',
                'topics': ['selectors', 'events', 'forms'],
                'topics_ar': ['المحددات', 'الأحداث', 'النماذج'],
                'hours': 8,
                'prereqs': [1],
                'market_relevance': 0.9,
            },
            {
                'id': 3,
                'title': 'Async JavaScript',
                'title_ar': 'جافاسكريبت غير المتزامنة',
                'title_fr': 'JavaScript Asynchrone',
                'topics': ['callbacks', 'promises', 'async/await'],
                'topics_ar': ['callbacks', 'الوعود', 'async/await'],
                'hours': 10,
                'prereqs': [2],
                'market_relevance': 0.9,
            },
            {
                'id': 4,
                'title': 'Modern ES6+',
                'title_ar': 'ES6+ الحديثة',
                'title_fr': 'ES6+ Moderne',
                'topics': ['arrow functions', 'modules', 'classes'],
                'topics_ar': ['الدوال السهمية', 'الوحدات', 'الأصناف'],
                'hours': 8,
                'prereqs': [3],
                'market_relevance': 0.85,
            },
            {
                'id': 5,
                'title': 'React.js (Most Demanded in Algeria)',
                'title_ar': 'React.js (الأكثر طلباً في الجزائر)',
                'title_fr': 'React.js (Le plus demandé en Algérie)',
                'topics': ['components', 'state', 'hooks', 'routing'],
                'topics_ar': ['المكونات', 'الحالة', 'Hooks', 'التوجيه'],
                'hours': 20,
                'prereqs': [4],
                'market_relevance': 0.95,
                'algeria_jobs': 35,
            },
            {
                'id': 6,
                'title': 'Node.js & Express',
                'title_ar': 'Node.js و Express',
                'title_fr': 'Node.js et Express',
                'topics': ['npm', 'routing', 'REST APIs'],
                'topics_ar': ['npm', 'التوجيه', 'واجهات REST'],
                'hours': 12,
                'prereqs': [4],
                'market_relevance': 0.85,
            },
            {
                'id': 7,
                'title': 'Full Stack Project',
                'title_ar': 'مشروع Full Stack',
                'title_fr': 'Projet Full Stack',
                'topics': ['frontend', 'backend', 'database', 'deployment'],
                'topics_ar': ['الواجهة الأمامية', 'الخلفية', 'قاعدة البيانات', 'النشر'],
                'hours': 25,
                'prereqs': [5, 6],
                'market_relevance': 1.0,
            },
        ],
        'web_development': [
            {
                'id': 1,
                'title': 'HTML Fundamentals',
                'title_ar': 'أساسيات HTML',
                'title_fr': 'Fondamentaux HTML',
                'topics': ['tags', 'forms', 'semantic HTML'],
                'topics_ar': ['العلامات', 'النماذج', 'HTML الدلالية'],
                'hours': 6,
                'prereqs': [],
                'market_relevance': 0.8,
            },
            {
                'id': 2,
                'title': 'CSS Basics',
                'title_ar': 'أساسيات CSS',
                'title_fr': 'Bases CSS',
                'topics': ['selectors', 'box model', 'flexbox'],
                'topics_ar': ['المحددات', 'نموذج الصندوق', 'Flexbox'],
                'hours': 8,
                'prereqs': [1],
                'market_relevance': 0.8,
            },
            {
                'id': 3,
                'title': 'Responsive Design',
                'title_ar': 'التصميم المتجاوب',
                'title_fr': 'Design Responsive',
                'topics': ['media queries', 'grid', 'mobile-first'],
                'topics_ar': ['استعلامات الوسائط', 'الشبكة', 'الجوال أولاً'],
                'hours': 6,
                'prereqs': [2],
                'market_relevance': 0.9,
            },
            {
                'id': 4,
                'title': 'JavaScript for Web',
                'title_ar': 'جافاسكريبت للويب',
                'title_fr': 'JavaScript pour le Web',
                'topics': ['DOM', 'events', 'fetch API'],
                'topics_ar': ['DOM', 'الأحداث', 'Fetch API'],
                'hours': 10,
                'prereqs': [3],
                'market_relevance': 0.9,
            },
            {
                'id': 5,
                'title': 'Frontend Framework (React/Vue)',
                'title_ar': 'إطار عمل Frontend (React/Vue)',
                'title_fr': 'Framework Frontend (React/Vue)',
                'topics': ['React/Vue basics', 'components', 'state'],
                'topics_ar': ['أساسيات React/Vue', 'المكونات', 'الحالة'],
                'hours': 15,
                'prereqs': [4],
                'market_relevance': 0.95,
                'algeria_jobs': 40,
            },
            {
                'id': 6,
                'title': 'Backend Basics (Node.js/Django)',
                'title_ar': 'أساسيات Backend (Node.js/Django)',
                'title_fr': 'Bases Backend (Node.js/Django)',
                'topics': ['servers', 'databases', 'APIs'],
                'topics_ar': ['الخوادم', 'قواعد البيانات', 'APIs'],
                'hours': 12,
                'prereqs': [4],
                'market_relevance': 0.9,
            },
            {
                'id': 7,
                'title': 'Portfolio Website Project',
                'title_ar': 'مشروع موقع البورتفوليو',
                'title_fr': 'Projet Site Portfolio',
                'topics': ['personal website', 'hosting', 'domain'],
                'topics_ar': ['موقع شخصي', 'الاستضافة', 'النطاق'],
                'hours': 15,
                'prereqs': [5, 6],
                'market_relevance': 1.0,
            },
        ],
        'data_science': [
            {
                'id': 1,
                'title': 'Python for Data Science',
                'title_ar': 'بايثون لعلوم البيانات',
                'title_fr': 'Python pour la Data Science',
                'topics': ['NumPy', 'Pandas basics'],
                'topics_ar': ['NumPy', 'أساسيات Pandas'],
                'hours': 12,
                'prereqs': [],
                'market_relevance': 0.9,
            },
            {
                'id': 2,
                'title': 'Data Visualization',
                'title_ar': 'تصور البيانات',
                'title_fr': 'Visualisation de données',
                'topics': ['Matplotlib', 'Seaborn', 'charts'],
                'topics_ar': ['Matplotlib', 'Seaborn', 'الرسوم البيانية'],
                'hours': 8,
                'prereqs': [1],
                'market_relevance': 0.85,
            },
            {
                'id': 3,
                'title': 'Statistics Fundamentals',
                'title_ar': 'أساسيات الإحصاء',
                'title_fr': 'Fondamentaux de Statistiques',
                'topics': ['descriptive stats', 'probability', 'distributions'],
                'topics_ar': ['الإحصاء الوصفي', 'الاحتمالات', 'التوزيعات'],
                'hours': 10,
                'prereqs': [1],
                'market_relevance': 0.85,
            },
            {
                'id': 4,
                'title': 'SQL & Databases',
                'title_ar': 'SQL وقواعد البيانات',
                'title_fr': 'SQL et Bases de données',
                'topics': ['SQL queries', 'PostgreSQL', 'data modeling'],
                'topics_ar': ['استعلامات SQL', 'PostgreSQL', 'نمذجة البيانات'],
                'hours': 10,
                'prereqs': [2, 3],
                'market_relevance': 0.95,
                'algeria_jobs': 50,
            },
            {
                'id': 5,
                'title': 'Machine Learning Intro',
                'title_ar': 'مقدمة في تعلم الآلة',
                'title_fr': 'Introduction au Machine Learning',
                'topics': ['sklearn', 'regression', 'classification'],
                'topics_ar': ['sklearn', 'الانحدار', 'التصنيف'],
                'hours': 15,
                'prereqs': [4],
                'market_relevance': 0.7,
            },
            {
                'id': 6,
                'title': 'Data Analysis Project',
                'title_ar': 'مشروع تحليل بيانات',
                'title_fr': 'Projet Analyse de données',
                'topics': ['real dataset', 'analysis', 'presentation'],
                'topics_ar': ['بيانات حقيقية', 'تحليل', 'عرض'],
                'hours': 20,
                'prereqs': [5],
                'market_relevance': 1.0,
            },
        ],
    }
    
    # Default graph for unknown subjects
    DEFAULT_GRAPH = [
        {
            'id': 1,
            'title': 'Fundamentals',
            'title_ar': 'الأساسيات',
            'title_fr': 'Fondamentaux',
            'topics': ['core concepts', 'basics'],
            'topics_ar': ['المفاهيم الأساسية', 'الأساسيات'],
            'hours': 10,
            'prereqs': [],
            'market_relevance': 0.7,
        },
        {
            'id': 2,
            'title': 'Intermediate Concepts',
            'title_ar': 'مفاهيم متوسطة',
            'title_fr': 'Concepts Intermédiaires',
            'topics': ['advanced basics', 'common patterns'],
            'topics_ar': ['الأساسيات المتقدمة', 'الأنماط الشائعة'],
            'hours': 12,
            'prereqs': [1],
            'market_relevance': 0.75,
        },
        {
            'id': 3,
            'title': 'Practical Applications',
            'title_ar': 'تطبيقات عملية',
            'title_fr': 'Applications Pratiques',
            'topics': ['hands-on practice', 'projects'],
            'topics_ar': ['ممارسة عملية', 'مشاريع'],
            'hours': 15,
            'prereqs': [2],
            'market_relevance': 0.9,
        },
        {
            'id': 4,
            'title': 'Portfolio Project',
            'title_ar': 'مشروع للبورتفوليو',
            'title_fr': 'Projet Portfolio',
            'topics': ['final project', 'portfolio'],
            'topics_ar': ['مشروع نهائي', 'بورتفوليو'],
            'hours': 20,
            'prereqs': [3],
            'market_relevance': 1.0,
        },
    ]
    
    def __init__(self, language: str = 'ar'):
        self.language = language
    
    def plan(self, profile: LearnerProfile, normalized_data: dict = None) -> List[Dict]:
        """
        Generate a learning plan based on profile.
        
        Returns:
            list: List of step dictionaries with sequence, titles, hours, etc.
        """
        if normalized_data is None:
            normalized_data = {}
        
        subject = normalized_data.get('subject_canonical', profile.subject.lower().replace(' ', '_'))
        level = normalized_data.get('level_canonical', profile.level or LearnerProfile.BEGINNER)
        self.language = profile.language or 'ar'
        
        # Get prerequisite graph
        graph = self.PREREQUISITE_GRAPHS.get(subject, self.DEFAULT_GRAPH)
        
        # Deep copy to avoid modifying original
        steps = [step.copy() for step in graph]
        
        # Filter based on level (skip beginner steps for advanced users)
        steps = self._filter_by_level(steps, level)

        # Adjust steps based on learner goals
        steps = self._augment_for_goals(steps, profile)
        
        # Adjust hours based on constraints
        steps = self._adjust_for_constraints(steps, profile)
        
        # Add localized content and metadata
        for i, step in enumerate(steps):
            step['sequence'] = i + 1
            
            # Set localized title based on language preference
            step['display_title'] = self._get_localized_text(step, 'title')
            step['display_topics'] = self._get_localized_text(step, 'topics')
            
            # Generate objectives in user's language
            step['objectives'] = self._generate_objectives(step)
            
            # Add market relevance info
            if 'market_relevance' in step:
                step['market_info'] = self._get_market_info(step)
        
        return steps

    def _augment_for_goals(self, steps: List[Dict], profile: LearnerProfile) -> List[Dict]:
        """Add or tweak steps based on learner goals for more personalization."""
        goals_text = (profile.goals or "").lower()
        subject_key = (profile.subject or "").lower().replace(' ', '_')

        if subject_key != 'python' or not goals_text:
            return steps

        extras = []

        if any(k in goals_text for k in ['web', 'django', 'api', 'backend']):
            extras.append({
                'id': 1001,
                'title': 'Django REST APIs',
                'title_ar': 'واجهات Django REST',
                'title_fr': 'APIs REST avec Django',
                'topics': ['django', 'rest framework', 'apis'],
                'topics_ar': ['Django', 'REST', 'واجهات برمجية'],
                'hours': 12,
                'prereqs': [],
                'market_relevance': 0.95,
                'algeria_jobs': 18,
            })

        if any(k in goals_text for k in ['data', 'analysis', 'pandas', 'ml', 'machine learning']):
            extras.append({
                'id': 1002,
                'title': 'Data Analysis with Pandas',
                'title_ar': 'تحليل البيانات باستخدام Pandas',
                'title_fr': 'Analyse de données avec Pandas',
                'topics': ['pandas', 'data analysis', 'data cleaning'],
                'topics_ar': ['Pandas', 'تحليل البيانات', 'تنظيف البيانات'],
                'hours': 10,
                'prereqs': [],
                'market_relevance': 0.8,
                'algeria_jobs': 12,
            })

        if any(k in goals_text for k in ['automation', 'script', 'scripting']):
            extras.append({
                'id': 1003,
                'title': 'Automation & Scripting',
                'title_ar': 'الأتمتة والسكريبتات',
                'title_fr': 'Automatisation et scripting',
                'topics': ['automation', 'scripts', 'cli tools'],
                'topics_ar': ['الأتمتة', 'سكريبتات', 'أدوات سطر الأوامر'],
                'hours': 8,
                'prereqs': [],
                'market_relevance': 0.7,
            })

        if not extras:
            return steps

        # Append extra steps before the final project step if present
        final_project_index = next((i for i, s in enumerate(steps) if 'Project' in s.get('title', '')), None)
        if final_project_index is None:
            steps.extend(extras)
        else:
            steps = steps[:final_project_index] + extras + steps[final_project_index:]

        # Reassign sequence-safe IDs to avoid collisions
        max_id = max((s.get('id', 0) for s in steps), default=0)
        for extra in steps:
            if extra.get('id', 0) >= 1000:
                max_id += 1
                extra['id'] = max_id

        return steps
    
    def _get_localized_text(self, step: Dict, field: str) -> any:
        """Get text in user's preferred language."""
        lang_field = f'{field}_{self.language}'
        if self.language == 'ar_dz':
            lang_field = f'{field}_ar'
        
        return step.get(lang_field) or step.get(f'{field}_ar') or step.get(field, '')
    
    def _generate_objectives(self, step: Dict) -> List[str]:
        """Generate learning objectives in user's language."""
        topics = self._get_localized_text(step, 'topics')
        
        if self.language in ['ar', 'ar_dz']:
            return [f"فهم {topic}" for topic in topics] if isinstance(topics, list) else [f"فهم {topics}"]
        elif self.language == 'fr':
            return [f"Comprendre {topic}" for topic in topics] if isinstance(topics, list) else [f"Comprendre {topics}"]
        else:
            return [f"Understand {topic}" for topic in topics] if isinstance(topics, list) else [f"Understand {topics}"]
    
    def _get_market_info(self, step: Dict) -> Dict:
        """Get market relevance info for a step."""
        relevance = step.get('market_relevance', 0.5)
        jobs = step.get('algeria_jobs', 0)
        
        if self.language in ['ar', 'ar_dz']:
            if relevance >= 0.9:
                demand = '🔥 مطلوب جداً في السوق الجزائرية'
            elif relevance >= 0.7:
                demand = '✅ مطلوب في السوق'
            else:
                demand = '📚 مهم للتأسيس'
        elif self.language == 'fr':
            if relevance >= 0.9:
                demand = '🔥 Très demandé sur le marché algérien'
            elif relevance >= 0.7:
                demand = '✅ Demandé sur le marché'
            else:
                demand = '📚 Important pour les fondamentaux'
        else:
            if relevance >= 0.9:
                demand = '🔥 High demand in Algerian market'
            elif relevance >= 0.7:
                demand = '✅ In demand'
            else:
                demand = '📚 Important foundation'
        
        return {
            'relevance_score': relevance,
            'demand_text': demand,
            'job_count': jobs,
        }
    
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
    
    def create_roadmap(self, user, profile: LearnerProfile, steps: List[Dict], normalized_data: dict = None) -> Roadmap:
        """
        Create a Roadmap instance with steps.
        
        Returns:
            Roadmap: Created roadmap with steps
        """
        if normalized_data is None:
            normalized_data = {}
        
        self.language = profile.language or 'ar'
        
        # Generate localized title and description
        if self.language in ['ar', 'ar_dz']:
            title = f"مسار تعلم: {profile.subject}"
            description = f"خطة تعلم مخصصة لتعلم {profile.subject} - مصممة للسوق الجزائرية"
        elif self.language == 'fr':
            title = f"Parcours d'apprentissage: {profile.subject}"
            description = f"Plan d'apprentissage personnalisé pour {profile.subject} - Conçu pour le marché algérien"
        else:
            title = f"Learning Path: {profile.subject}"
            description = f"Personalized roadmap for learning {profile.subject} - Designed for the Algerian market"
        
        # Create roadmap
        roadmap = Roadmap.objects.create(
            user=user,
            learner_profile=profile,
            title=title,
            description=description,
            total_estimated_hours=sum(step['hours'] for step in steps),
            input_profile_hash=normalized_data.get('profile_hash', ''),
            model_versions={'planner': '2.0', 'market': 'algeria_v1'},
        )
        
        # Create steps
        created_steps = {}
        for step_data in steps:
            # Use localized title
            step_title = step_data.get('display_title') or step_data.get('title', '')
            step_topics = step_data.get('display_topics') or step_data.get('topics', [])
            
            if isinstance(step_topics, list):
                topics_text = ', '.join(step_topics)
            else:
                topics_text = str(step_topics)

            objectives_text = ''
            if step_data.get('objectives'):
                objectives_text = ' '.join(step_data['objectives'])

            if objectives_text:
                step_description = f"Topics: {topics_text}. Objectives: {objectives_text}"
            else:
                step_description = f"Topics: {topics_text}."
            
            roadmap_step = RoadmapStep.objects.create(
                roadmap=roadmap,
                title=step_title,
                description=step_description,
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
