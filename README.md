# RoadmapAI - Django Learning Platform

AI-powered personalized learning roadmap generator designed for the Algerian market, supporting Arabic, French, and English.

## Features

- 🤖 AI-powered roadmap generation using Groq LLM (Llama 3.3)
- 🌍 Multi-language support (Arabic, French, English)
- 📚 Personalized learning paths
- 🇩🇿 Algerian market insights
- 📊 Progress tracking
- 🎯 Goal-based customization
- 📱 Responsive design

## Tech Stack

- **Backend:** Django 6.0.1, Django REST Framework
- **Database:** SQLite (dev), PostgreSQL (production)
- **AI:** Groq API (Llama 3.3 70B)
- **Authentication:** JWT
- **Frontend:** Django Templates, Tailwind CSS

## Local Development

### Prerequisites

- Python 3.11+
- pip
- virtualenv

### Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd my_django_app
```

2. Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create .env file:

```bash
cp .env.example .env
```

5. Update .env with your keys:

```
SECRET_KEY=your-secret-key
DEBUG=True
GROQ_API_KEY=your-groq-api-key
```

6. Run migrations:

```bash
python manage.py migrate
```

7. Create superuser:

```bash
python manage.py createsuperuser
```

8. Run development server:

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Note:** This is a Django application and cannot be deployed to Netlify. Use Railway, Render, or Heroku instead.

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `GROQ_API_KEY` - Groq API key for AI features
- `DATABASE_URL` - Database connection string (production)
- `CORS_ALLOWED_ORIGINS` - Allowed CORS origins

## API Endpoints

- `/api/profiles/` - User profiles
- `/api/roadmaps/` - Learning roadmaps
- `/api/resources/` - Learning resources
- `/admin/` - Django admin panel

## Project Structure

```
my_django_app/
├── accounts/          # User authentication
├── ai_orchestrator/   # AI services (Groq integration)
├── assessments/       # User assessments
├── pages/            # Main pages and views
├── profiles/         # User profiles and onboarding
├── resources/        # Learning resources
├── roadmaps/         # Roadmap models and logic
├── telemetry/        # Usage tracking
├── templates/        # HTML templates
├── my_site/          # Project settings
└── manage.py         # Django management script
```

## Security

- ✅ Environment variables for secrets
- ✅ HTTPS enforced in production
- ✅ CORS configured
- ✅ CSRF protection enabled
- ✅ Secure cookie settings

## License

This project is for educational purposes.

## Support

For issues and questions, please open an issue on GitHub.
