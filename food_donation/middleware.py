import re
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect
import json
import requests
from .models import VisitorLog

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


class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile list of paths to exclude from tracking
        self.exclude_paths = [
            r'^/static/',
            r'^/media/',
            r'^/__debug__/',
            r'^/admin/jsi18n/',
            r'^/favicon\.ico$',
            r'^/robots\.txt$',
        ]
        self.exclude_patterns = [re.compile(pattern) for pattern in self.exclude_paths]
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip tracking for excluded paths
        path = request.path
        for pattern in self.exclude_patterns:
            if pattern.match(path):
                return response
        
        # Skip AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return response
        
        # Get IP address with proxy handling
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')
        
        # Check if IP is internal/local to avoid tracking development visits
        if ip_address in ('127.0.0.1', 'localhost', '::1') and not settings.DEBUG:
            return response
            
        # Collect user agent info
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Try to get geolocation data (optional)
        geo_data = self.get_ip_info(ip_address)
        
        # Parse browser and device info from user agent
        browser, device, os = self.parse_user_agent(user_agent)
        
        # Create visitor log
        try:
            VisitorLog.objects.create(
                ip_address=ip_address,
                user_agent=user_agent,
                page_visited=path,
                referrer=referrer,
                user=user,
                country=geo_data.get('country'),
                city=geo_data.get('city'),
                region=geo_data.get('region'),
                browser=browser,
                device=device,
                os=os
            )
        except Exception as e:
            # Log error but don't prevent response
            if settings.DEBUG:
                print(f"Error tracking visitor: {str(e)}")
        
        return response
    
    def get_ip_info(self, ip):
        """Get geolocation information for an IP address"""
        if not ip or ip in ('127.0.0.1', 'localhost', '::1'):
            return {}
            
        try:
            # Use a free IP geolocation API
            response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=2)
            if response.status_code == 200:
                data = response.json()
                return {
                    'country': data.get('country_name'),
                    'city': data.get('city'),
                    'region': data.get('region')
                }
        except:
            pass
        
        return {}
    
    def parse_user_agent(self, user_agent):
        """Simple parsing of user agent string"""
        browser = 'Unknown'
        device = 'Desktop'
        os = 'Unknown'
        
        # Browser detection
        if 'Chrome' in user_agent and not 'Edge' in user_agent:
            browser = 'Chrome'
        elif 'Firefox' in user_agent:
            browser = 'Firefox'
        elif 'Safari' in user_agent and not 'Chrome' in user_agent:
            browser = 'Safari'
        elif 'Edge' in user_agent:
            browser = 'Edge'
        elif 'MSIE' in user_agent or 'Trident' in user_agent:
            browser = 'Internet Explorer'
        
        # Device detection
        if 'Mobile' in user_agent or 'Android' in user_agent:
            device = 'Mobile'
        elif 'iPad' in user_agent:
            device = 'Tablet'
        
        # OS detection
        if 'Windows' in user_agent:
            os = 'Windows'
        elif 'Mac OS' in user_agent:
            os = 'macOS'
        elif 'Linux' in user_agent:
            os = 'Linux'
        elif 'Android' in user_agent:
            os = 'Android'
        elif 'iOS' in user_agent:
            os = 'iOS'
            
        return browser, device, os 