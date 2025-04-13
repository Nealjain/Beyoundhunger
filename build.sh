#!/bin/bash

# Exit on error
set -e

echo "-------------------------------------"
echo "Setting up Beyond Hunger application"
echo "-------------------------------------"

# Create required directories
echo "Creating required directories..."
mkdir -p staticfiles
mkdir -p media

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create user profiles if needed
echo "Creating user profiles if needed..."
python manage.py create_user_profile

echo "-------------------------------------"
echo "Build completed successfully"
echo "-------------------------------------" 