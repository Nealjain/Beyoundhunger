#!/usr/bin/env python3

import os
import re
import sys

def fix_bhandara_urls():
    print("Checking for bhandara_detail issues...")
    urls_file = "food_donation/urls.py"
    
    with open(urls_file, 'r') as f:
        content = f.read()
    
    if "from . import bhandara_views" not in content:
        print("Adding import for bhandara_views...")
        content = content.replace(
            "from . import views_debug", 
            "from . import views_debug\nfrom . import bhandara_views  # Import the new bhandara_views module"
        )
    
    # Fix the URL pattern for bhandara_detail
    if "path('bhandara/<int:pk>/', views.bhandara_detail" in content:
        print("Updating bhandara_detail URL pattern...")
        content = content.replace(
            "path('bhandara/<int:pk>/', views.bhandara_detail",
            "path('bhandara/<int:pk>/', bhandara_views.bhandara_detail"
        )
    
    with open(urls_file, 'w') as f:
        f.write(content)
    
    print("Bhandara URLs fixed successfully!")

def main():
    print("Running Python 3.13 compatibility fixes...")
    
    # Check if bhandara_views.py exists, create it if not
    if not os.path.exists('food_donation/bhandara_views.py'):
        print("Creating bhandara_views.py...")
        with open('food_donation/bhandara_views.py', 'w') as f:
            f.write('''
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.conf import settings
from .models import Bhandara

def bhandara_detail(request, pk):
    """Display details of a specific Bhandara event."""
    # Get the specific Bhandara event
    event = get_object_or_404(Bhandara, pk=pk, is_approved=True, is_active=True)
    
    # Find similar events nearby (same city, future events)
    similar_events = Bhandara.objects.filter(
        is_approved=True,
        is_active=True,
        city=event.city,
        end_datetime__gte=timezone.now(),
    ).exclude(pk=event.pk).order_by('start_datetime')[:3]
    
    # Get Google Maps API key from settings
    google_maps_api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    
    # Current datetime for template
    current_datetime = timezone.now()
    
    context = {
        'event': event,
        'similar_events': similar_events,
        'google_maps_api_key': google_maps_api_key,
        'current_datetime': current_datetime,
    }
    
    return render(request, 'food_donation/bhandara_detail.html', context)
''')
    
    # Fix the URLs
    fix_bhandara_urls()
    
    print("All fixes completed!")

if __name__ == "__main__":
    main() 