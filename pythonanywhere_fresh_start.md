# Fresh PythonAnywhere Deployment Guide

Follow these steps to deploy your Beyond Hunger application on PythonAnywhere from scratch:

## 1. Set Up Your PythonAnywhere Account

1. Log in to your PythonAnywhere account
2. Open a Bash console from your dashboard

## 2. Clone Your Repository

```bash
# Clone your repository
git clone https://github.com/Nealjain/Beyoundhunger.git ~/beyondhunger

# Navigate to the project directory
cd ~/beyondhunger
```

## 3. Set Up Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install any missing packages if needed
pip install whitenoise django-cors-headers gunicorn
```

## 4. Create Necessary Directories

```bash
# Create static and media directories
mkdir -p staticfiles
mkdir -p media
```

## 5. Configure Settings

```bash
# Generate a secure secret key
python generate_secret_key.py
# Copy the generated secret key for the next step
```

## 6. Configure WSGI File

1. Go to the Web tab in your PythonAnywhere dashboard
2. Click on your domain (e.g., nealjain.pythonanywhere.com)
3. Click on the WSGI configuration file link (e.g., /var/www/nealjain_pythonanywhere_com_wsgi.py)
4. Replace the entire content with this (replace YOUR_SECRET_KEY with the generated key):

```python
import os
import sys

# Add your project directory to the system path
path = '/home/nealjain/beyondhunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'YOUR_SECRET_KEY'  # Replace with your generated key
os.environ['DJANGO_DEBUG'] = 'False'  # Set to False for production
os.environ['DJANGO_ALLOWED_HOSTS'] = 'nealjain.pythonanywhere.com,localhost,127.0.0.1'
os.environ['CORS_ALLOWED_ORIGINS'] = 'https://nealjain.pythonanywhere.com,http://nealjain.pythonanywhere.com,http://localhost:8000,http://127.0.0.1:8000'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://nealjain.pythonanywhere.com,http://nealjain.pythonanywhere.com,http://localhost:8000,http://127.0.0.1:8000'

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Save the file

## 7. Configure Static Files in PythonAnywhere

1. In the Web tab, under "Static files":
2. Add these mappings:
   - URL: `/static/` → Directory: `/home/nealjain/beyondhunger/staticfiles`
   - URL: `/media/` → Directory: `/home/nealjain/beyondhunger/media`

## 8. Initialize the Database and Collect Static Files

Return to your Bash console:

```bash
# Make sure you're in the project directory
cd ~/beyondhunger

# Activate the virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create a superuser (follow the prompts)
python manage.py createsuperuser

# Fix user profiles if needed
python manage.py create_user_profile
```

## 9. Configure Web App Settings

1. In the Web tab:
   - Make sure your Python version is 3.8 or newer
   - Verify the path to your virtual environment: `/home/nealjain/beyondhunger/venv`
   - Source code: `/home/nealjain/beyondhunger`
   - Working directory: `/home/nealjain/beyondhunger`

## 10. Reload Your Web App

1. In the Web tab, click the "Reload" button for your web app

## 11. Test Your Deployment

1. Visit your site at: `https://nealjain.pythonanywhere.com/debug/`
2. This debug page should load without requiring login
3. If it works, try the main site: `https://nealjain.pythonanywhere.com/`

## Troubleshooting

If you encounter issues:

1. Check the error logs in the Web tab
2. Try enabling debug mode temporarily:
   - Edit the WSGI file and change `os.environ['DJANGO_DEBUG'] = 'True'`
   - Reload the web app
3. Visit the debug URLs to check for system information:
   - `/debug/` - Basic debug page
   - `/debug-info/` - System information

## Common Issues and Solutions

1. **Static files not working**:
   - Verify static file mappings in Web tab
   - Run `collectstatic` command again

2. **Database errors**:
   - Ensure migrations are applied correctly
   - Check database file permissions

3. **Import errors**:
   - Install any missing packages
   - Check Python version compatibility

4. **Login redirect loops**:
   - Try the debug URLs to bypass authentication
   - Verify authentication settings in `settings.py` 