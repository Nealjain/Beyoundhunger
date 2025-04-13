# Deployment Guide for Beyond Hunger

This guide provides detailed instructions for deploying the Beyond Hunger application on PythonAnywhere, a free hosting platform ideal for Django applications.

## PythonAnywhere Deployment

### 1. Create a PythonAnywhere Account

1. Sign up for a free PythonAnywhere account at https://www.pythonanywhere.com/
2. Verify your email address and log in to your account

### 2. Set Up a Web App

1. In the PythonAnywhere dashboard, click on the **Web** tab
2. Click **Add a new web app**
3. Choose your domain name (it will be `yourusername.pythonanywhere.com`)
4. Select **Manual configuration**
5. Choose **Python 3.12** (or another compatible version)

### 3. Clone Your Repository

1. Go to the **Consoles** tab and start a new Bash console
2. Clone your GitHub repository:
   ```bash
   git clone https://github.com/yourusername/beyond-hunger.git
   ```

### 4. Create a Virtual Environment

1. In the Bash console, create a virtual environment:
   ```bash
   cd beyond-hunger
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 5. Configure Environment Variables

1. In the **Files** tab, navigate to `/var/www/yourusername_pythonanywhere_com_wsgi.py`
2. Edit this file to add environment variables and point to your Django application:
   ```python
   import os
   import sys

   # Add your project directory to the path
   path = '/home/yourusername/beyond-hunger'
   if path not in sys.path:
       sys.path.append(path)

   # Set environment variables
   os.environ['DJANGO_SECRET_KEY'] = 'your_secret_key_here'
   os.environ['DJANGO_DEBUG'] = 'False'
   os.environ['DJANGO_ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
   os.environ['CORS_ALLOWED_ORIGINS'] = 'https://yourusername.pythonanywhere.com'

   # Point to your Django application
   from beyond_hunger.wsgi import application
   ```

### 6. Configure Web App Settings

1. Go back to the **Web** tab
2. Scroll down to the **Code** section
3. Update the following settings:
   - **Source code**: `/home/yourusername/beyond-hunger`
   - **Working directory**: `/home/yourusername/beyond-hunger`
   - **WSGI configuration file**: `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   - **Python version**: 3.12 (or your chosen version)

4. Scroll to the **Virtualenv** section and enter: `/home/yourusername/beyond-hunger/.venv`

### 7. Set Up Static Files

1. In the **Static Files** section, add:
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/beyond-hunger/staticfiles`

2. Add another for media files:
   - **URL**: `/media/`
   - **Directory**: `/home/yourusername/beyond-hunger/media`

### 8. Set Up the Database

1. Go back to the Bash console
2. Navigate to your project directory:
   ```bash
   cd ~/beyond-hunger
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

### 9. Reload the Web App

1. Go back to the **Web** tab
2. Click the **Reload** button for your web app

### 10. Access Your Application

Your app should now be live at `https://yourusername.pythonanywhere.com/`

## Maintenance and Updates

To update your deployment after making changes to your code:

1. SSH into your PythonAnywhere account
2. Navigate to your project directory
3. Pull the latest changes:
   ```bash
   cd ~/beyond-hunger
   git pull
   ```

4. Apply any migrations:
   ```bash
   python manage.py migrate
   ```

5. Collect static files if needed:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Reload the web app from the **Web** tab

## Troubleshooting

If you encounter issues:

1. Check the error logs in the **Web** tab
2. Verify your environment variables are correctly set
3. Ensure your ALLOWED_HOSTS includes your PythonAnywhere domain
4. Confirm your static files are properly configured
5. Check that your database migrations have been applied

For more help, visit the [PythonAnywhere help page](https://help.pythonanywhere.com/) or the [Django deployment checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/). 