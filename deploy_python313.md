# Python 3.13 Compatibility Updates

This guide helps prepare your Beyond Hunger project for deployment on Python 3.13.

## 1. Update Requirements File

First, let's update the requirements.txt file to ensure all packages are compatible with Python 3.13:

```bash
# From your local project directory
pip install --upgrade pip
pip freeze > requirements.txt.new
```

Then review and edit requirements.txt.new to:
- Remove any unnecessary packages
- Ensure version specifications are appropriate
- Replace requirements.txt with the new file

## 2. Python 3.13 Compatibility Fixes

### Update settings.py

Some Django settings might need adjustment for Python 3.13:

- Ensure your middleware settings are up-to-date
- Update any deprecated features
- Add specific settings for Python 3.13 if needed

### Update Database Configuration

Ensure your database settings are compatible:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 30,  # Increased timeout for Python 3.13
        }
    }
}
```

## 3. Create a Python 3.13 Specific WSGI File

Create a new file called `wsgi_python313.py` in your project:

```python
import os
import sys

# Add project directory to the path
path = '/home/yourusername/beyondhunger'  # Replace with your actual username
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'LCK+yaE_(:V!C5B/xa&4`UK/v:+,R>&`:=APF+KN7sOik2bJ{i'
os.environ['DJANGO_DEBUG'] = 'True'  # Set to True for initial testing
os.environ['DJANGO_ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com,localhost,127.0.0.1'
os.environ['PYTHON_VERSION'] = '3.13'  # Indicate Python version

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 4. Update Deployment Scripts

Create a new PythonAnywhere setup script:

```bash
#!/bin/bash
# setup_python313.sh

# Exit on error
set -e

echo "Setting up Beyond Hunger for Python 3.13"

# Create directories
mkdir -p staticfiles
mkdir -p media

# Install dependencies
python3.13 -m pip install --upgrade pip
python3.13 -m pip install -r requirements.txt

# Apply migrations
python3.13 manage.py migrate

# Collect static files
python3.13 manage.py collectstatic --noinput

echo "Setup completed successfully!"
```

## 5. Commit Changes to GitHub

```bash
git add requirements.txt wsgi_python313.py setup_python313.sh
git commit -m "Update project for Python 3.13 compatibility"
git push origin main
```

## PythonAnywhere Deployment Notes

When deploying on PythonAnywhere with Python 3.13:

1. Make sure to select Python 3.13 when creating your web app
2. Use the correct path to the Python 3.13 interpreter in your virtual environment setup
3. Check for any specific PythonAnywhere requirements for Python 3.13
4. Monitor error logs carefully during initial deployment 