#!/bin/bash

# Exit on error
set -o errexit

echo "-------------------------------------"
echo "Setting up Beyond Hunger application"
echo "-------------------------------------"

# Create required directories
echo "Creating required directories..."
mkdir -p staticfiles
mkdir -p media

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Applying database migrations..."
python manage.py migrate

# Removing the create_user_profile command which might be causing the build failure
# If you need to run this, you can add it back or run it manually after deployment

echo "-------------------------------------"
echo "Build completed successfully"
echo "-------------------------------------" 