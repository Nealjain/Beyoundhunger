"""
Simplified WSGI file for PythonAnywhere
Use this if you're experiencing redirection issues or complex configuration problems.
"""
import os
import sys

# Add your project directory to the path
path = '/home/nealjain/beyondhunger'
if path not in sys.path:
    sys.path.append(path)

# Configure minimal environment settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_DEBUG'] = 'True'  # Enable debug temporarily to see detailed errors
os.environ['DJANGO_SECRET_KEY'] = 'LCK+yaE_(:V!C5B/xa&4`UK/v:+,R>&`:=APF+KN7sOik2bJ{i'
os.environ['DJANGO_ALLOWED_HOSTS'] = '*'  # Allow all hosts temporarily

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 