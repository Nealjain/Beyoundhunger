#!/usr/bin/env python3
"""
Direct fix for marketplace view in views.py

This script will directly modify the marketplace view function in your views.py file
to fix the backslash and indentation issues.
"""
import os
import re

def fix_marketplace_view():
    """Fix the marketplace view in views.py"""
    views_path = "food_donation/views.py"
    
    if not os.path.exists(views_path):
        print(f"Error: {views_path} not found!")
        return False
    
    # Read the file content
    with open(views_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Back up the original file
    with open(f"{views_path}.bak", 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fix the marketplace view function - using simpler regex pattern to avoid errors
    pattern = r'def marketplace\(request\):.*?\.select_related\(\'seller\'\).*?\.order_by\(\'-created_at\'\)'
    replacement = """def marketplace(request):
    \"\"\"View for the marketplace homepage with filtering\"\"\"
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    show_free = request.GET.get('free', '') == 'on'
    
    # Use select_related and prefetch_related for efficient loading
    items = (
        MarketplaceItem.objects.filter(status='available')
        .select_related('seller')
        .prefetch_related('bids')
        .order_by('-created_at')
    )"""
    
    # Use a simpler approach - find the problematic lines and replace them
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def marketplace(request):' in line:
            start_index = i
        if i > start_index and i < len(lines) - 1:
            if '.select_related' in line and '\\' in line:
                # Found the problematic line
                for j in range(start_index, i + 3):  # Replace a few lines around the issue
                    if 'items = MarketplaceItem.objects.filter' in lines[j]:
                        # Replace with fixed code
                        lines[j] = "    items = ("
                        lines[j+1] = "        MarketplaceItem.objects.filter(status='available')"
                        lines[j+2] = "        .select_related('seller')"
                        lines[j+3] = "        .prefetch_related('bids')"
                        if '.order_by' in lines[j+4]:
                            lines[j+4] = "        .order_by('-created_at')"
                            lines[j+5] = "    )"
                        else:
                            lines[j+4] = "        .order_by('-created_at')"
                            lines.insert(j+5, "    )")
                        break
                break
    
    # Write the fixed content back to the file
    fixed_content = '\n'.join(lines)
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed marketplace view in {views_path}")
    print(f"✅ Original file backed up to {views_path}.bak")
    return True

if __name__ == "__main__":
    fix_marketplace_view() 