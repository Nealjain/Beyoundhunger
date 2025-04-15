#!/bin/bash
# setup_python313.sh - Deployment script for Python 3.13

# Exit on error
set -e

echo "================================================================="
echo "Setting up Beyond Hunger for Python 3.13 on PythonAnywhere"
echo "================================================================="

# Create necessary directories
echo "Creating required directories..."
mkdir -p staticfiles
mkdir -p media

# Set up Python 3.13 virtual environment
echo "Setting up Python 3.13 virtual environment..."
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (comment out if not needed)
echo "Do you want to create a superuser? (y/n)"
read CREATE_SUPERUSER
if [[ "$CREATE_SUPERUSER" == "y" ]]; then
    python manage.py createsuperuser
fi

# Fix user profiles
echo "Creating user profiles..."
python manage.py create_user_profile

echo "================================================================="
echo "Setup completed successfully!"
echo "================================================================="
echo ""
echo "Next steps:"
echo "1. Configure your WSGI file at /var/www/yourusername_pythonanywhere_com_wsgi.py"
echo "2. Set up static file mappings in the Web tab"
echo "3. Reload your web app"
echo "=================================================================" 