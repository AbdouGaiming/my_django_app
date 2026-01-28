#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Create Superuser logic (Corrected for Custom User Model)
if [ "$CREATE_SUPERUSER" = "True" ]; then
  python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# Check if user exists by EMAIL, not username
if not User.objects.filter(email=email).exists():
    # Create the superuser using email as the unique identifier
    User.objects.create_superuser(email=email, password=password)
    print(f"Superuser {email} created.")
else:
    print(f"Superuser {email} already exists.")
END
fi