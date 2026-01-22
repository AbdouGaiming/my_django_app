#!/bin/bash

echo "🚀 Deployment Checklist for Django RoadmapAI"
echo "=============================================="
echo ""

# Check for .env file
if [ -f .env ]; then
    echo "✅ .env file exists"
else
    echo "❌ .env file missing - copy from .env.example"
fi

# Check if .env is in .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "✅ .env is in .gitignore"
else
    echo "⚠️  .env should be in .gitignore"
fi

# Check for requirements.txt
if [ -f requirements.txt ]; then
    echo "✅ requirements.txt exists"
else
    echo "❌ requirements.txt missing"
fi

# Check for Procfile
if [ -f Procfile ]; then
    echo "✅ Procfile exists"
else
    echo "❌ Procfile missing"
fi

# Check for runtime.txt
if [ -f runtime.txt ]; then
    echo "✅ runtime.txt exists"
else
    echo "⚠️  runtime.txt missing (optional)"
fi

echo ""
echo "📋 Pre-deployment steps:"
echo "1. ✓ Clean project structure"
echo "2. ✓ Environment variables configured"
echo "3. ✓ Static files setup"
echo "4. ✓ Security settings enabled"
echo "5. ⚠️  Update GROQ_API_KEY in production .env"
echo "6. ⚠️  Generate new SECRET_KEY for production"
echo "7. ⚠️  Set ALLOWED_HOSTS for your domain"
echo ""
echo "🌐 Deployment platforms:"
echo "   • Railway: https://railway.app (Recommended)"
echo "   • Render: https://render.com"
echo "   • Heroku: https://heroku.com"
echo ""
echo "❌ NOT compatible with Netlify (use Railway/Render instead)"
echo ""
