# BeyondHunger PythonAnywhere Setup Guide

This guide will help you set up the BeyondHunger application on a new PythonAnywhere account.

## Step 1: Create a PythonAnywhere Account

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/) and sign up for a new account
2. Verify your email address and log in

## Step 2: Set Up Your Environment

1. From your dashboard, open a Bash console by clicking "Consoles" → "Bash"

2. Clone the repository:
```bash
cd ~
git clone https://github.com/Nealjain/Beyoundhunger.git beyoundhunger
cd beyoundhunger
```

3. Create and set up a virtual environment:
```bash
mkvirtualenv --python=python3.12 beyoundhunger_env
workon beyoundhunger_env
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the Python 3.13 compatibility fixes:
```bash
python fix_python313_compatibility.py
```

6. Run the test script to verify everything is working:
```bash
python test_app.py
```

7. Set up the database:
```bash
python manage.py migrate
```

8. Collect static files:
```bash
python manage.py collectstatic --noinput
```

9. Create a superuser for admin access:
```bash
python manage.py createsuperuser
```

## Step 3: Configure Web App

1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Select "Manual configuration"
4. Choose Python 3.12 as your Python version

5. Configure your app settings:
   - Source code: `/home/yourusername/beyoundhunger` (replace with your username)
   - Working directory: `/home/yourusername/beyoundhunger`
   - Virtual environment: `/home/yourusername/.virtualenvs/beyoundhunger_env`

6. Edit the WSGI file (click on the link provided):
   - Delete all the existing code
   - Add this code (update the username):

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/beyoundhunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'

# Activate your virtual environment
activate_this = '/home/yourusername/.virtualenvs/beyoundhunger_env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

7. Configure static files:
   - Add these in the "Static files" section:
     - URL: `/static/` → Directory: `/home/yourusername/beyoundhunger/static`
     - URL: `/media/` → Directory: `/home/yourusername/beyoundhunger/media`

8. Click "Reload" to start your web app

## Step 4: Verify Your Installation

1. Visit your site at `https://yourusername.pythonanywhere.com`
2. Check for any error messages in the error logs (available in the Web tab)
3. If you encounter any issues, run the compatibility fix script:
   ```bash
   python fix_python313_compatibility.py
   ```

## Step 5: Content Moderation

Your application now includes content moderation to prevent inappropriate language. This is implemented in:
- `food_donation/content_moderation.py`

To customize the list of filtered words:
1. Edit this file to add more words to the `INAPPROPRIATE_WORDS` list
2. Reload your web app after making changes

## Troubleshooting

If you encounter errors:

1. Check the error logs in the Web tab
2. Run the test script: `python test_app.py`
3. Make sure all the paths in your WSGI file match your username
4. Try fixing file permissions: `chmod -R u+rwX ~/beyoundhunger`
5. Verify your virtual environment is activated: `workon beyoundhunger_env`

For database errors, check your connection:
```python
python manage.py shell
from django.db import connection
connection.ensure_connection()
```

## Updating Your Site

When you need to update your site with new changes:

```bash
cd ~/beyoundhunger
git pull
workon beyoundhunger_env
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then go to the Web tab and click "Reload". 