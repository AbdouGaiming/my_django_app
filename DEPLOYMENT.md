# Django RoadmapAI - Render Deployment Guide

Your Django application is now **production-ready** for deployment on Render! 🚀

## ✅ What's Already Configured

### 1. Dependencies (requirements.txt)
- ✅ `gunicorn` - Production web server
- ✅ `psycopg2-binary` - PostgreSQL adapter
- ✅ `dj-database-url` - Database URL parser
- ✅ `whitenoise[brotli]` - Static files serving with compression

### 2. Settings (settings.py)
- ✅ Automatic Render environment detection
- ✅ Production database configuration with fallback
- ✅ Static files handling with WhiteNoise
- ✅ Security settings for production
- ✅ CORS and CSRF configuration

### 3. Build Script (build.sh)
- ✅ Executable permissions set
- ✅ Dependencies installation
- ✅ Static files collection
- ✅ Database migrations

### 4. Version Control (.gitignore)
- ✅ Environment variables (.env) excluded
- ✅ Static files directory excluded
- ✅ Database files excluded

## 🚀 Render Deployment Steps

### Step 1: Create Web Service on Render
1. Go to [render.com](https://render.com) and sign in
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `your-app-name`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn my_site.wsgi:application`

### Step 2: Set Environment Variables
In the Render Dashboard, go to **Environment** and add:

**Required Variables:**
```
SECRET_KEY=your-super-long-random-secret-key-here
RENDER_EXTERNAL_HOSTNAME=your-app-name.onrender.com
GROQ_API_KEY=your-groq-api-key
```

**Optional Variables:**
```
PYTHON_VERSION=3.10.0
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com
```

### Step 3: Create PostgreSQL Database (Recommended)
1. Click **"New"** → **"PostgreSQL"**
2. Choose a name and plan (free tier available)
3. Once created, Render automatically provides `DATABASE_URL`

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Render will automatically deploy your app
3. Monitor the build logs for any issues

## 🔧 Local Development Setup

1. **Create local environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your local values:**
   ```
   SECRET_KEY=your-dev-secret-key
   DEBUG=True
   GROQ_API_KEY=your-groq-api-key
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## 🛠 Troubleshooting

### Common Issues:

**1. Build fails with "Permission denied"**
- The build.sh file should already be executable, but if needed:
  ```bash
  chmod +x build.sh
  git add build.sh
  git commit -m "Make build.sh executable"
  git push
  ```

**2. Static files not loading**
- Check that WhiteNoise is properly configured (✅ already done)
- Ensure `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`

**3. Database connection issues**
- Verify PostgreSQL database is created and connected
- Check that `DATABASE_URL` environment variable is set

**4. CORS errors**
- Add your frontend domain to `CORS_ALLOWED_ORIGINS`
- Add your domain to `CSRF_TRUSTED_ORIGINS`

## 📝 Environment Variables Reference

### Production (Render Dashboard)
- `SECRET_KEY`: Django secret key (required)
- `RENDER_EXTERNAL_HOSTNAME`: your-app-name.onrender.com
- `DATABASE_URL`: Provided automatically by Render PostgreSQL
- `GROQ_API_KEY`: Your Groq API key
- `CORS_ALLOWED_ORIGINS`: Frontend domains (comma-separated)
- `CSRF_TRUSTED_ORIGINS`: Trusted domains (comma-separated)

### Development (.env file)
- `SECRET_KEY`: Different key for development
- `DEBUG=True`: Enable debug mode locally
- `GROQ_API_KEY`: Same as production or test key

## 🔒 Security Checklist
- ✅ Secret key is long and random
- ✅ DEBUG is False in production
- ✅ .env file is in .gitignore
- ✅ HTTPS is enforced in production
- ✅ Security headers are configured
- ✅ CORS is properly configured

## 📱 Frontend Integration
If you have a separate frontend:
1. Deploy frontend to Netlify/Vercel
2. Update `CORS_ALLOWED_ORIGINS` with frontend URL
3. Point frontend API calls to your Render backend URL

Your application is now production-ready! 🎉
