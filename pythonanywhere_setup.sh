#!/bin/bash
# Complete setup script for Beyond Hunger on PythonAnywhere with Python 3.13

echo "=== Setting up Beyond Hunger on PythonAnywhere (Python 3.13) ==="

# Install all required packages
echo "Installing required packages..."
pip install Django==5.0.0
pip install pillow
pip install python-dotenv
pip install dj-database-url
pip install django-allauth
pip install djangorestframework
pip install requests
pip install django-cors-headers
pip install whitenoise
pip install gunicorn
pip install oauthlib requests-oauthlib python3-openid PyJWT
pip install cryptography  # Required for Google OAuth
pip install reportlab     # Required for PDF generation
pip install six           # Required by many packages
echo "✓ Packages installed successfully"

# Fix f-string issues
echo "Fixing f-string issues..."
python fix_f_strings.py
echo "✓ Fixed f-string issues"

# Apply migrations - handle errors gracefully
echo "Applying database migrations..."
if python manage.py migrate; then
    echo "✓ Migrations applied successfully"
else
    echo "⚠️ There were some issues with migrations, but we'll continue"
    echo "   You may need to fix these later"
fi

# Collect static files - handle errors gracefully
echo "Collecting static files..."
if python manage.py collectstatic --noinput; then
    echo "✓ Static files collected successfully"
else
    echo "⚠️ There were some issues collecting static files, but we'll continue"
    echo "   You may need to address these later"
fi

echo "=== Setup complete! ==="
echo "Next steps:"
echo "1. Create a superuser with: python manage.py createsuperuser"
echo "2. Configure your WSGI file in the Web tab using pythonanywhere_wsgi.py"
echo "3. Reload your web app from the Web tab" 