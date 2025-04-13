"""
Debug views for troubleshooting deployment issues.
These views don't require authentication and can be used to test basic functionality.
"""
import logging
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
def debug_home(request):
    """Simple home view for testing deployment without login requirements."""
    logger.debug("Entered debug_home view")
    
    try:
        context = {
            'title': 'Beyond Hunger - Debug Mode',
            'debug': settings.DEBUG,
            'user_count': User.objects.count(),
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'static_url': settings.STATIC_URL,
            'login_url': settings.LOGIN_URL,
        }
        
        return render(request, 'food_donation/debug.html', context)
    except Exception as e:
        logger.error(f"Error in debug_home view: {e}")
        return HttpResponse(f"""
            <h1>Beyond Hunger - Debug Mode</h1>
            <p>An error occurred: {e}</p>
            <hr>
            <h2>Server Information:</h2>
            <ul>
                <li>Debug: {settings.DEBUG}</li>
                <li>Allowed Hosts: {settings.ALLOWED_HOSTS}</li>
                <li>Static URL: {settings.STATIC_URL}</li>
                <li>Request path: {request.path}</li>
                <li>User authenticated: {request.user.is_authenticated}</li>
            </ul>
        """)

@csrf_exempt
def debug_info(request):
    """View to display system information for debugging."""
    try:
        # Check database connection
        from django.db import connection
        db_working = True
        try:
            connection.ensure_connection()
        except Exception as e:
            db_working = False
            db_error = str(e)
            
        # Check template rendering
        template_working = True
        try:
            loader.get_template('food_donation/base.html')
        except Exception as e:
            template_working = False
            template_error = str(e)
            
        # Check static files
        static_working = True
        import os
        static_root = settings.STATIC_ROOT
        if not os.path.exists(static_root):
            static_working = False
            static_error = f"Static root directory does not exist: {static_root}"
        
        # Build response
        response = f"""
        <h1>Beyond Hunger - System Info</h1>
        <h2>Database</h2>
        <p>Working: {db_working}</p>
        {f"<p>Error: {db_error}</p>" if not db_working else ""}
        
        <h2>Templates</h2>
        <p>Working: {template_working}</p>
        {f"<p>Error: {template_error}</p>" if not template_working else ""}
        
        <h2>Static Files</h2>
        <p>Working: {static_working}</p>
        {f"<p>Error: {static_error}</p>" if not static_working else ""}
        <p>STATIC_ROOT: {settings.STATIC_ROOT}</p>
        <p>STATIC_URL: {settings.STATIC_URL}</p>
        
        <h2>Environment</h2>
        <p>DEBUG: {settings.DEBUG}</p>
        <p>ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}</p>
        """
        
        return HttpResponse(response)
    except Exception as e:
        return HttpResponse(f"Error generating debug info: {e}") 