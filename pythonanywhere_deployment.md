# PythonAnywhere Deployment Instructions

Follow these steps to deploy your updated Beyond Hunger project to PythonAnywhere:

## 1. Update Your Code

Log in to PythonAnywhere and open a Bash console, then:

```bash
# Navigate to your project directory
cd /home/nealjain/beyond_hunger

# Pull the latest changes (including the f-string fixes)
git fetch --all
git reset --hard origin/main

# If you haven't set up Git, you'll need to manually upload the files
# using the PythonAnywhere Files interface
```

> **Important**: We've fixed critical f-string issues in the code that were causing syntax errors. These fixes have been pushed to the GitHub repository.

## 2. Update Dependencies

```bash
# Activate your virtual environment (if you're using one)
source /home/jainneal/path/to/your/virtualenv/bin/activate

# Install or update dependencies
pip install -r requirements.txt
```

## 3. Apply Database Migrations

```bash
python manage.py migrate
```

## 4. Configure Environment Variables

In your WSGI configuration file (`/var/www/jainneal_pythonanywhere_com_wsgi.py`), make sure you have these environment variables:

```python
# Set environment variables
import os
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'  # Use a secure key
os.environ['DJANGO_DEBUG'] = 'False'  # Set to False in production
os.environ['DJANGO_ALLOWED_HOSTS'] = 'jainneal.pythonanywhere.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'your-email-app-password'  # For email functionality
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'  # For chatbot functionality
```

## 5. Update Google OAuth Settings

Make sure you've added your PythonAnywhere domain to the Google OAuth settings:

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Navigate to "APIs & Services" > "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add these to "Authorized JavaScript origins":
   ```
   https://jainneal.pythonanywhere.com
   ```
5. Add these to "Authorized redirect URIs":
   ```
   https://jainneal.pythonanywhere.com/accounts/google/login/callback/
   ```

## 6. Configure Static Files

Make sure your static files are properly configured in the PythonAnywhere Web tab:

- URL: `/static/`
- Directory: `/home/jainneal/beyond_hunger/static/`

And for media files:
- URL: `/media/`
- Directory: `/home/jainneal/beyond_hunger/media/`

## 7. Reload Your Web App

1. Go to the Web tab in PythonAnywhere
2. Click the big green "Reload" button for your web app

## 8. Verify Deployment

1. Visit your site at https://jainneal.pythonanywhere.com/
2. Test the money donation functionality
3. Test the Google OAuth login
4. Verify that emails are being sent correctly
5. Check that the admin can delete submissions

## Troubleshooting

If you encounter any issues:

1. Check the error logs in the PythonAnywhere Web tab
2. Verify that all required environment variables are set
3. Make sure your database migrations have been applied
4. Confirm that your Google OAuth settings are correct
5. Check that your email settings are properly configured

## Security Considerations

1. Never commit sensitive information to your repository
2. Always use environment variables for passwords, API keys, and secrets
3. Keep your SECRET_KEY secure and unique
4. Set DEBUG to False in production 