import re
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)

class LoginRequiredMiddleware:
    """
    Middleware to control login redirects and help debug deployment issues.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration
        self.login_url = settings.LOGIN_URL
        self.exempt_urls = []
        
        # Compile exempt URLs if defined in settings
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            self.exempt_urls = [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]
            
        # Always exempt the login URL itself
        self.exempt_urls.append(re.compile(f'^{self.login_url}$'))
    
    def __call__(self, request):
        # Code to be executed for each request before the view
        path = request.path_info.lstrip('/')
        
        # Log request info for debugging
        logger.debug(f"Request path: {path}")
        logger.debug(f"User authenticated: {request.user.is_authenticated}")
        
        # Check if user is authenticated or URL is exempt
        if not request.user.is_authenticated:
            # Check if URL is exempt
            for exempt in self.exempt_urls:
                if exempt.match(path):
                    logger.debug(f"URL exempt from login: {path}")
                    break
            else:
                # Not exempt - redirect to login
                logger.debug(f"Redirecting to login: {path}")
                return HttpResponseRedirect(reverse('food_donation:login'))
        
        # Get response
        response = self.get_response(request)
        return response


class DeploymentDebugMiddleware:
    """
    Middleware to log helpful information for debugging deployment issues.
    Only active when DEBUG is True.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if settings.DEBUG:
            logger.debug(f"Request method: {request.method}")
            logger.debug(f"Request path: {request.path}")
            logger.debug(f"Request GET params: {request.GET}")
            logger.debug(f"Request META: Host={request.META.get('HTTP_HOST')}, Referer={request.META.get('HTTP_REFERER')}")
        
        response = self.get_response(request)
        
        if settings.DEBUG:
            logger.debug(f"Response status code: {response.status_code}")
            if response.status_code in (301, 302):
                logger.debug(f"Redirect location: {response.get('Location', 'Not found')}")
        
        return response 


class SocialAuthProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process request - check if user needs to complete profile
        if request.user.is_authenticated and request.session.get('needs_profile_completion', False):
            # Get the current path
            current_url = resolve(request.path_info).url_name
            
            # Define exempt paths that don't redirect (including the completion page itself)
            exempt_paths = ['complete_profile', 'logout', 'static', 'media', 'admin', 'api']
            
            # Check if current path is exempt
            is_exempt = any(path in request.path_info for path in exempt_paths)
            
            # If not exempt, redirect to complete profile
            if not is_exempt and current_url != 'complete_profile':
                return redirect('food_donation:complete_profile')
        
        response = self.get_response(request)
        return response 