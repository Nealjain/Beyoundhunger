"""
WSGI config for PythonAnywhere deployment.
This is a simplified version to make the process of deploying to PythonAnywhere easier.
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/jainneal/beyond_hunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = '&$2)$b)ll4&bhp#f1cqetl9=0s)p5^sli$oo4#3zldjvtyh)lf'  # Use the generated key
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'jainneal.pythonanywhere.com'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 