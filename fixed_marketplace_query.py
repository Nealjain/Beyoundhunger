"""
Fixed query for marketplace items in views.py
Copy and paste this into your views.py file if the automated fix doesn't work.
"""

# Replace lines ~466-468 with this code
items = MarketplaceItem.objects.filter(status='available').select_related('seller').prefetch_related('images').order_by('-created_at')

# If you need to retain the line breaks for readability, use parentheses:
items = (
    MarketplaceItem.objects.filter(status='available')
    .select_related('seller')
    .prefetch_related('images')
    .order_by('-created_at')
) 