# Django RoadmapAI - Deployment Guide

## ⚠️ Important: Netlify Cannot Host Django

**Netlify is for static sites only** (HTML, CSS, JavaScript, JAMstack apps). Django is a Python backend framework that requires a server environment.

## 🚀 Recommended Hosting Platforms

### 1. **Railway** (Recommended - Easiest)

- Free tier available
- Automatic deployments from Git
- Built-in PostgreSQL database
- Environment variables management

**Steps:**

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add PostgreSQL service
4. Set environment variables (see below)
5. Deploy automatically

### 2. **Render**

- Free tier available
- Easy setup
- Free PostgreSQL database

### 3. **Heroku**

- Popular choice
- Easy deployment
- Add-ons available

### 4. **PythonAnywhere**

- Python-specific hosting
- Free tier for learning projects

## 🔐 Environment Variables to Set

When deploying, set these environment variables on your hosting platform:

```bash
SECRET_KEY=your-production-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=your-production-database-url
GROQ_API_KEY=your-groq-api-key-here
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

## 📋 Pre-Deployment Checklist

- [x] Environment variables configured (.env)
- [x] requirements.txt created
- [x] Static files configured
- [x] Security settings added
- [x] Database migrations ready
- [x] .gitignore updated (no secrets committed)

## 🔧 Deployment Commands

The platform will automatically run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn my_site.wsgi
```

## 🗄️ Database

For production, switch from SQLite to PostgreSQL:

- Railway/Render provide free PostgreSQL
- Automatically configured via DATABASE_URL

## 📝 After Deployment

1. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

2. Access admin panel:

   ```
   https://your-domain.com/admin/
   ```

3. Test your API endpoints:
   ```
   https://your-domain.com/api/
   ```

## 🔒 Security Notes

- ✅ SECRET_KEY is stored in environment variables
- ✅ DEBUG is set to False in production
- ✅ GROQ_API_KEY is protected
- ✅ HTTPS enforced in production
- ✅ CORS configured for specific domains
- ❌ Never commit .env file to Git
- ❌ Never share your SECRET_KEY or API keys

## 📱 Frontend Deployment

If you have a separate frontend (React, Vue, etc.):

1. Deploy frontend to **Netlify** or **Vercel**
2. Deploy Django backend to **Railway** or **Render**
3. Update CORS_ALLOWED_ORIGINS with frontend URL
4. Update frontend API URL to backend domain

## 🆘 Troubleshooting

**Static files not loading:**

- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings

**Database errors:**

- Ensure DATABASE_URL is set correctly
- Run migrations: `python manage.py migrate`

**API errors:**

- Check ALLOWED_HOSTS includes your domain
- Verify CORS settings
- Check GROQ_API_KEY is set

## 📞 Support

For deployment issues, check:

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Django Deployment Checklist: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/
