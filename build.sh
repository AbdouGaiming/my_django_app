#!/bin/bash

# Build script for Render
python manage.py collectstatic --noinput
python manage.py migrate --noinput
