"""
Special WSGI file for fixing login redirect issues on PythonAnywhere.
Use this if your site keeps redirecting to login pages or has authentication issues.
"""
import os
import sys

# Add your project directory to the path
path = '/home/nealjain/beyondhunger'
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'

# Enable debug for troubleshooting
os.environ['DJANGO_DEBUG'] = 'True'

# Set secret key
os.environ['DJANGO_SECRET_KEY'] = 'LCK+yaE_(:V!C5B/xa&4`UK/v:+,R>&`:=APF+KN7sOik2bJ{i'

# Allow all hosts
os.environ['DJANGO_ALLOWED_HOSTS'] = '*'

# Disable built-in login redirect to troubleshoot
os.environ['DISABLE_LOGIN_REDIRECT'] = 'True'

# Disable CSRF temporarily for troubleshooting
os.environ['DISABLE_CSRF'] = 'True'

# Load the custom middleware and settings
os.environ['USE_DEBUG_MIDDLEWARE'] = 'True'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Custom middleware for handling login redirects
class WSGIMiddleware:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        # Log request details
        path_info = environ.get('PATH_INFO', '')
        with open('/tmp/wsgi_debug.log', 'a') as f:
            f.write(f"Request path: {path_info}\n")
            f.write(f"Request method: {environ.get('REQUEST_METHOD', '')}\n")
            
        # Process response
        response = self.app(environ, start_response)
        return response

# Wrap the application with our middleware
application = WSGIMiddleware(application) 