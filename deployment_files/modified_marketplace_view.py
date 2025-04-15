"""
This file contains the fixed marketplace view function.
Copy this entire function to replace the one in your views.py file.
"""

def marketplace(request):
    """Marketplace view showing available items."""
    # Get all available marketplace items
    items = (
        MarketplaceItem.objects.filter(status='available')
        .select_related('seller')
        .prefetch_related('images')
        .order_by('-created_at')
    )
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(food_type__icontains=query)
        )
    
    # Process filters
    food_type = request.GET.get('food_type')
    if food_type:
        items = items.filter(food_type=food_type)
    
    # Pagination
    paginator = Paginator(items, 12)  # Show 12 items per page
    page = request.GET.get('page')
    items = paginator.get_page(page)
    
    context = {
        'items': items,
        'query': query,
        'food_type': food_type,
        'food_types': MarketplaceItem.FOOD_TYPE_CHOICES,
    }
    
    return render(request, 'food_donation/marketplace.html', context) 