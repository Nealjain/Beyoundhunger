"""
PythonAnywhere WSGI file for Beyond Hunger
This is a simplified version with debug mode enabled for initial setup
"""
import os
import sys

# Add the project directory to the Python path
path = '/home/nealjain/beyondhunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'LCK+yaE_(:V!C5B/xa&4`UK/v:+,R>&`:=APF+KN7sOik2bJ{i'  # Replace with your generated key
os.environ['DJANGO_DEBUG'] = 'True'  # Enable debug for initial setup
os.environ['DJANGO_ALLOWED_HOSTS'] = 'nealjain.pythonanywhere.com,localhost,127.0.0.1'
os.environ['CORS_ALLOWED_ORIGINS'] = 'https://nealjain.pythonanywhere.com,http://nealjain.pythonanywhere.com,http://localhost:8000,http://127.0.0.1:8000'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://nealjain.pythonanywhere.com,http://nealjain.pythonanywhere.com,http://localhost:8000,http://127.0.0.1:8000'
os.environ['USE_DEBUG_MIDDLEWARE'] = 'True'  # Enable debug middleware

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# For troubleshooting
print("WSGI file loaded successfully!") 