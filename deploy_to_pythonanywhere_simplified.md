# PythonAnywhere Simplified Deployment Guide (Python 3.13)

This guide provides simplified steps to deploy your Beyond Hunger project on PythonAnywhere with minimal errors using Python 3.13.

## Step 1: Get your PythonAnywhere account ready

1. Create a PythonAnywhere account if you haven't already
2. Log in to PythonAnywhere
3. Open a Bash console (click on "Consoles" > "Bash")

## Step 2: Clone the repository and set up

```bash
# Clone the repository
git clone https://github.com/Nealjain/Beyoundhunger.git beyoundhunger
cd beyoundhunger

# Make the scripts executable
chmod +x pythonanywhere_setup.sh
chmod +x fix_f_strings.py

# Create a virtual environment (with Python 3.13)
mkvirtualenv --python=/usr/bin/python3.13 beyoundhunger_env
workon beyoundhunger_env

# Run the complete setup script
./pythonanywhere_setup.sh

# Create a superuser account
python manage.py createsuperuser
```

## Step 3: Set up the web app

1. Go to the "Web" tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose your domain (e.g., yourusername.pythonanywhere.com)
4. Select "Manual configuration"
5. Choose Python 3.13

## Step 4: Configure the web app

In the Web tab:

1. Set up the paths:
   - Source code: `/home/yourusername/beyoundhunger` (replace 'yourusername' with your actual username)
   - Working directory: `/home/yourusername/beyoundhunger`

2. Set up the virtual environment:
   - Enter: `/home/yourusername/.virtualenvs/beyoundhunger_env`

3. Set up static files:
   - URL: `/static/` → Directory: `/home/yourusername/beyoundhunger/static`
   - URL: `/media/` → Directory: `/home/yourusername/beyoundhunger/media`

4. Edit the WSGI file:
   - Click on the WSGI file link
   - Delete all existing content
   - Copy the content from `pythonanywhere_wsgi.py` (make sure to replace 'yourusername' with your actual username)
   - Save the file

## Step 5: Start your web app

1. Click the big green "Reload" button on the Web tab
2. Visit your site at https://yourusername.pythonanywhere.com/

## Troubleshooting

If you encounter any issues:

1. Check the error logs in the Web tab
2. Ensure your WSGI file is configured correctly
3. Verify that all your static files are set up correctly
4. Make sure your virtualenv is active when running commands 