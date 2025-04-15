# PythonAnywhere Quick Setup Guide

This guide will help you quickly set up your Beyond Hunger project on PythonAnywhere while avoiding timeout issues with package installation.

## Step 1: Clone Your Repository

Log in to PythonAnywhere and open a Bash console, then:

```bash
# Clone the repository
git clone https://github.com/Nealjain/Beyoundhunger.git beyond_hunger
cd beyond_hunger
```

## Step 2: Create a Virtual Environment

```bash
# Create a virtual environment (using Python 3.9)
mkvirtualenv --python=/usr/bin/python3.9 beyond_hunger
```

## Step 3: Install Packages One by One

Instead of running `pip install -r requirements.txt` which times out, use our helper script:

```bash
# Make the installer script executable
chmod +x pythonanywhere_installer.py

# Run the installer (this will install packages one at a time)
python pythonanywhere_installer.py
```

This script will install each package individually to avoid timeout issues.

## Step 4: Set Up Your Web App

1. Go to the Web tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.9
5. Enter your project path: `/home/jainneal/beyond_hunger`

## Step 5: Configure the WSGI File

1. In the Web tab, click on the link to your WSGI configuration file
2. Replace all content with the content from `pythonanywhere_wsgi_simple.py`
3. Update the path variable if your username is not `jainneal`
4. Save the file

## Step 6: Configure Static Files

In the Web tab:

- Add a static file mapping:
  - URL: `/static/`
  - Directory: `/home/jainneal/beyond_hunger/static/`

- Add a media file mapping:
  - URL: `/media/`
  - Directory: `/home/jainneal/beyond_hunger/media/`

## Step 7: Set Up the Database

```bash
# Apply migrations
python manage.py migrate

# Create a superuser (follow the prompts)
python manage.py createsuperuser
```

## Step 8: Reload Your Web App

Go to the Web tab and click the big green "Reload" button.

## Troubleshooting

1. If you get a "Bad Gateway" error:
   - Check the error logs in the Web tab
   - Make sure the paths in your WSGI file are correct

2. If you can't see static files:
   - Collect static files: `python manage.py collectstatic --noinput`
   - Double-check your static files configuration in the Web tab

3. For environment variables:
   - They are already set in the WSGI file
   - If you need to change them, edit the WSGI file directly 