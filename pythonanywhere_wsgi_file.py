"""
This file contains the WSGI configuration for Python Anywhere.
It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/beyoundhunger12/beyoundhunger/Beyoundhunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'  # Replace with your actual secret key
os.environ['DJANGO_ALLOWED_HOSTS'] = 'beyoundhunger12.pythonanywhere.com'

# Setup Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 