# Manual Deployment Guide for PythonAnywhere (Free Account)

Since PythonAnywhere's free accounts don't have access to the webapp reload API, you'll need to deploy manually. This guide walks you through the process step by step.

## Step 1: Create a PythonAnywhere Account (First-time only)

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com/) and sign up for a free account
2. Verify your email and log in to your dashboard

## Step 2: Set Up Your Project on PythonAnywhere

1. **Open a Bash console**
   - From your dashboard, click on "Consoles" → "Bash"

2. **Clone your repository**
   ```bash
   cd ~
   git clone https://github.com/Nealjain/Beyoundhunger.git beyoundhunger
   cd beyoundhunger
   ```

3. **Create a virtual environment**
   ```bash
   mkvirtualenv --python=python3.12 beyoundhunger_env
   # If you see an error, you may need to install virtualenvwrapper first:
   # pip install virtualenvwrapper
   # export WORKON_HOME=$HOME/.virtualenvs
   # source /usr/local/bin/virtualenvwrapper.sh
   
   # Activate the environment
   workon beyoundhunger_env
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Set up your database**
   ```bash
   python manage.py migrate
   ```

5. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

## Step 3: Configure Your Web App

1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Select "Manual configuration"
4. Select "Python 3.12" as your Python version
5. Configure your app settings:
   - **Source code**: `/home/yourusername/beyoundhunger` (replace yourusername)
   - **Working directory**: `/home/yourusername/beyoundhunger`
   - **Virtual environment**: `/home/yourusername/.virtualenvs/beyoundhunger_env`

6. **Edit the WSGI file** (click on the WSGI file link in the Web tab)
   - Delete all existing content
   - Add this code (replace `yourusername` with your PythonAnywhere username):

   ```python
   import os
   import sys

   # Add your project directory to the Python path
   path = '/home/yourusername/beyoundhunger'
   if path not in sys.path:
       sys.path.append(path)

   # Set environment variables
   os.environ['DJANGO_SETTINGS_MODULE'] = 'beyoundhunger.settings'

   # Set up Django
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

7. **Configure static files**:
   - Add these in the "Static files" section:
     - URL: `/static/` → Directory: `/home/yourusername/beyoundhunger/static`
     - URL: `/media/` → Directory: `/home/yourusername/beyoundhunger/media`

8. **Click "Reload" to start your web app**

## Step 4: Set Up Environment Variables (if needed)

If your app requires environment variables (like secret keys, API keys, etc.):

1. Click on the "Web" tab
2. Scroll down to "Environment variables"
3. Add each required environment variable for your app 
4. Click "Reload" again to apply changes

## Step 5: Update and Redeploy (When you have new changes)

When you've pushed changes to GitHub and want to deploy them:

1. **Log in to PythonAnywhere** at [pythonanywhere.com](https://www.pythonanywhere.com/)

2. **Open a Bash console** (click "Consoles" → "Bash")

3. **Run these commands in sequence**:
   ```bash
   # Go to your project folder
   cd ~/beyoundhunger
   
   # Pull latest changes
   git pull
   
   # Activate virtual environment
   workon beyoundhunger_env
   
   # Install any new dependencies
   pip install -r requirements.txt
   
   # Apply database migrations
   python manage.py migrate
   
   # Update static files
   python manage.py collectstatic --noinput
   ```

4. **Go to the "Web" tab and click "Reload"** to restart your app with the changes

## Troubleshooting

- **Error logs**: Check the error logs in the Web tab if your app isn't working
- **File permissions**: Fix permissions with `chmod -R u+rwX ~/beyoundhunger`
- **Database issues**: Test your connection in the shell:
  ```bash
  python manage.py shell
  from django.db import connection
  connection.ensure_connection()  # Should not raise errors
  ```
- **WSGI file**: Make sure the path in the WSGI file exactly matches your username and directories

## Checking if Your Site is Live

After reloading, visit your site at:
`https://yourusername.pythonanywhere.com`

Your Bhandara detail page will be available at:
`https://yourusername.pythonanywhere.com/bhandara/1/` (change the number for different events)

## Automation Options

If you later upgrade to a paid PythonAnywhere account:
1. The GitHub Actions workflow will work automatically
2. You can use the `deploy_script.py` for API-based deployment 