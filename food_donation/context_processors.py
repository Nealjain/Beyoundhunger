from .models import Notification, MarketplaceChat

def notifications_processor(request):
    """Add notification counts to context for all templates"""
    context = {}
    
    if request.user.is_authenticated:
        # Count unread notifications
        unread_notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        
        # Count unread messages
        unread_messages = MarketplaceChat.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        
        context['unread_notifications'] = unread_notifications
        context['unread_messages'] = unread_messages
    
    return context 