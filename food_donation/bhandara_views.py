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