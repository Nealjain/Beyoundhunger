# Beyond Hunger Deployment Guide - PythonAnywhere

This guide will walk you through deploying your Beyond Hunger application to PythonAnywhere's free tier.

## Step 1: Create a PythonAnywhere Account

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/) 
2. Sign up for a free "Beginner" account
3. Verify your email address

## Step 2: Set Up the Web App

1. Log in to your PythonAnywhere dashboard
2. Click on the **Web** tab
3. Click on **Add a new web app**
4. Select your domain name (it will be `yourusername.pythonanywhere.com`)
5. Select **Manual configuration** (not the Django option)
6. Choose **Python 3.10** as your Python version

## Step 3: Clone Your Repository

1. Go to the **Consoles** tab
2. Start a new **Bash console**
3. Clone your GitHub repository with this command:
   ```bash
   git clone https://github.com/Nealjain/Beyoundhunger.git
   ```
4. Rename the directory to match PythonAnywhere's expected format:
   ```bash
   mv Beyoundhunger beyond_hunger
   ```

## Step 4: Set Up a Virtual Environment

1. Navigate to your project directory:
   ```bash
   cd beyond_hunger
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 5: Configure the WSGI File

1. Go to the **Web** tab
2. Under the **Code** section, click on the link to the WSGI configuration file (it will be something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. Delete all the contents of this file
4. Copy and paste the following code (replace `yourusername` with your actual PythonAnywhere username):

```python
import os
import sys

# Add your project directory to the system path
path = '/home/yourusername/beyond_hunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'a-long-random-string-for-production'  # Generate a new secret key
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
os.environ['CORS_ALLOWED_ORIGINS'] = 'https://yourusername.pythonanywhere.com'

# Set up your application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Save the file

## Step 6: Configure Static Files

1. Still on the **Web** tab, scroll down to the **Static files** section
2. Add the following static file mappings:
   - URL: `/static/`  
     Directory: `/home/yourusername/beyond_hunger/staticfiles`
   - URL: `/media/`  
     Directory: `/home/yourusername/beyond_hunger/media`

## Step 7: Configure Virtual Environment Path

1. In the **Virtualenv** section, enter the path to your virtual environment:
   ```
   /home/yourusername/beyond_hunger/.venv
   ```

## Step 8: Set Up the Database

1. Go back to the **Consoles** tab
2. Start a new **Bash console** or use the existing one
3. Navigate to your project directory:
   ```bash
   cd ~/beyond_hunger
   ```
4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
5. Run database migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser (admin account):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your username, email, and password.

## Step 9: Collect Static Files

1. In the same console, run:
   ```bash
   python manage.py collectstatic --noinput
   ```

## Step 10: Reload Your Web App

1. Go back to the **Web** tab
2. Click the green **Reload** button for your web app

## Step 11: Access Your Application

Your app should now be live at `https://yourusername.pythonanywhere.com/`

If you encounter any issues, check the error logs in the **Web** tab under the **Logs** section.

## Updating Your Application

When you make changes to your code and want to update your deployed application:

1. Push your changes to GitHub
2. Log in to PythonAnywhere
3. Open a Bash console
4. Navigate to your project directory:
   ```bash
   cd ~/beyond_hunger
   ```
5. Pull the latest changes:
   ```bash
   git pull
   ```
6. Activate your virtual environment:
   ```bash
   source .venv/bin/activate
   ```
7. Update dependencies (if needed):
   ```bash
   pip install -r requirements.txt
   ```
8. Apply migrations (if needed):
   ```bash
   python manage.py migrate
   ```
9. Collect static files (if needed):
   ```bash
   python manage.py collectstatic --noinput
   ```
10. Go to the **Web** tab and click the **Reload** button

Now your application is updated with the latest changes! 