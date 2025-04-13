"""
WSGI Configuration for Beyond Hunger - Python 3.13 Version

This file contains settings optimized for Python 3.13 deployment on PythonAnywhere.
"""
import os
import sys

# Add project directory to the path - Replace 'yourusername' with your actual username
path = '/home/yourusername/beyondhunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'LCK+yaE_(:V!C5B/xa&4`UK/v:+,R>&`:=APF+KN7sOik2bJ{i'
os.environ['DJANGO_DEBUG'] = 'True'  # Set to True for initial setup, change to False later
os.environ['DJANGO_ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com,localhost,127.0.0.1'
os.environ['PYTHON_VERSION'] = '3.13'  # Indicate Python version

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Log successful loading for troubleshooting
import logging
logger = logging.getLogger("django")
logger.info("WSGI application loaded successfully with Python 3.13") 