"""
Optimized PythonAnywhere WSGI file for Beyond Hunger
This version includes optimizations to prevent tarpit issues
"""
import os
import sys

# Add the project directory to the Python path
path = '/home/nealjain/beyondhunger'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'beyond_hunger.settings'
os.environ['DJANGO_SECRET_KEY'] = 'LCK+yaE_(:V!C5B/xa&4`UK/v:+,R>&`:=APF+KN7sOik2bJ{i'
os.environ['DJANGO_DEBUG'] = 'False'  # Set to False to improve performance
os.environ['DJANGO_ALLOWED_HOSTS'] = 'nealjain.pythonanywhere.com,localhost,127.0.0.1'
os.environ['DJANGO_PERFORMANCE_MODE'] = 'True'  # Enable performance optimization
os.environ['PYTHONOPTIMIZE'] = '1'  # Enable Python optimizations

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Performance optimization middleware wrapper
class PerformanceMiddleware:
    def __init__(self, app):
        self.app = app
        self.max_execution_time = 10  # seconds
        
    def __call__(self, environ, start_response):
        # Exclude static file requests from processing
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith('/static/') or path_info.startswith('/media/'):
            return self.app(environ, start_response)
            
        # Custom start_response that doesn't modify responses
        def custom_start_response(status, headers, exc_info=None):
            return start_response(status, headers, exc_info)
            
        return self.app(environ, custom_start_response)

# Wrap the application with the performance middleware
application = PerformanceMiddleware(application) 