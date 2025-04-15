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

@register.filter
def count_unread_messages(messages, user):
    """Count unread messages for a specific user."""
    count = 0
    for message in messages:
        if not message.is_read and message.receiver == user:
            count += 1
    return count 