from django import template
from food_donation.models import DeliveryAssignment

register = template.Library()

@register.filter
def filter_active_assignments(assignments, volunteer_id):
    """Filter active assignments for a specific volunteer."""
    return assignments.filter(
        volunteer_id=volunteer_id,
        status__in=['pending', 'in_progress']
    ).count() 