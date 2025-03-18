from django import template

register = template.Library()

@register.filter
def filter_active_assignments(assignments, volunteer_id):
    """
    Filter assignments that are active (assigned or picked_up) for a specific volunteer.
    
    Usage:
    {% with active_count=assignments|filter_active_assignments:volunteer.id %}
        {{ active_count }}
    {% endwith %}
    """
    active_count = 0
    for assignment in assignments:
        if assignment.volunteer.id == volunteer_id and assignment.status in ['assigned', 'picked_up']:
            active_count += 1
    return active_count 